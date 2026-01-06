from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
import logging
import traceback
from typing import Optional
import aiofiles
import base64

from app.config import Config
from app.paralon_client import ParalonClient
from app.image_processor import ImageProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ParalonCloud Image Generation & Editing Tool")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/uploads", StaticFiles(directory=Config.UPLOAD_DIR), name="uploads")
app.mount("/generated", StaticFiles(directory=Config.GENERATED_DIR), name="generated")

# Initialize clients (with error handling)
try:
    paralon_client = ParalonClient()
    image_processor = ImageProcessor()
    logger.info("Clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize clients: {str(e)}")
    logger.error(traceback.format_exc())
    paralon_client = None
    image_processor = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "message": "ParalonCloud Image Generation & Editing Tool API",
        "client_initialized": paralon_client is not None,
        "api_base": Config.PARALONCLOUD_API_BASE if paralon_client else None
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    health = {
        "status": "ok",
        "client_initialized": paralon_client is not None,
        "api_key_set": bool(Config.PARALONCLOUD_API_KEY),
        "api_base": Config.PARALONCLOUD_API_BASE,
        "upload_dir_exists": os.path.exists(Config.UPLOAD_DIR),
        "generated_dir_exists": os.path.exists(Config.GENERATED_DIR)
    }
    
    if not health["api_key_set"]:
        health["error"] = "PARALONCLOUD_API_KEY not found in .env file"
    
    return health

@app.get("/api/test-endpoints")
async def test_endpoints():
    """Test which ParalonCloud endpoints are available"""
    import httpx
    
    if not paralon_client:
        raise HTTPException(status_code=500, detail="ParalonCloud client not initialized")
    
    base_url = Config.PARALONCLOUD_API_BASE.rstrip('/')
    api_key = Config.PARALONCLOUD_API_KEY
    
    test_endpoints = [
        "/images/generations",
        "/inference/images/generations",
        "/inference/generate",
        "/generate",
        "/chat/completions",  # This should work based on dashboard
    ]
    
    results = {}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint_path in test_endpoints:
            full_url = f"{base_url}{endpoint_path}"
            try:
                # Try a simple GET first
                response = await client.get(full_url, headers=headers)
                results[endpoint_path] = {
                    "status": response.status_code,
                    "method": "GET",
                    "exists": response.status_code != 404
                }
            except Exception as e:
                results[endpoint_path] = {
                    "status": "error",
                    "error": str(e),
                    "exists": False
                }
    
    return {
        "base_url": base_url,
        "tested_endpoints": results,
        "note": "This tests endpoint existence. Actual usage may require POST with proper payload."
    }

@app.post("/api/generate")
async def generate_image(
    prompt: str = Form(...),
    model: str = Form("dall-e-3"),
    size: str = Form("1024x1024"),
    quality: str = Form("standard"),
    n: int = Form(1)
):
    """
    Generate an image from a text prompt
    """
    if not paralon_client:
        raise HTTPException(status_code=500, detail="ParalonCloud client not initialized. Check your API key in .env file.")
    
    try:
        logger.info(f"Generating image with prompt: {prompt[:50]}...")
        image_data = await paralon_client.generate_image(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
            n=n
        )
        
        if not image_data:
            raise HTTPException(status_code=500, detail="No images returned from API")
        
        # Download and save images locally
        saved_paths = []
        for i, img_data in enumerate(image_data):
            filename = f"{uuid.uuid4()}.png"
            save_path = os.path.join(Config.GENERATED_DIR, filename)
            
            # Handle both URL strings and base64 encoded images
            if isinstance(img_data, str):
                if img_data.startswith('http://') or img_data.startswith('https://'):
                    # It's a URL
                    await image_processor.download_image(img_data, save_path)
                else:
                    # It's base64 encoded
                    try:
                        image_bytes = base64.b64decode(img_data)
                        async with aiofiles.open(save_path, 'wb') as f:
                            await f.write(image_bytes)
                    except Exception as e:
                        logger.error(f"Error decoding base64 image: {str(e)}")
                        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
            else:
                # Assume it's already bytes or a file-like object
                async with aiofiles.open(save_path, 'wb') as f:
                    if isinstance(img_data, bytes):
                        await f.write(img_data)
                    else:
                        await f.write(str(img_data).encode())
            
            saved_paths.append(f"/generated/{filename}")
        
        logger.info(f"Successfully generated {len(saved_paths)} image(s)")
        return {
            "success": True,
            "images": saved_paths,
            "data": image_data[:1] if image_data else []  # Return first item for debugging
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")

@app.post("/api/edit")
async def edit_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    mask: Optional[UploadFile] = File(None),
    model: str = Form("dall-e-2"),
    size: str = Form("1024x1024"),
    n: int = Form(1)
):
    """
    Edit an existing image using a prompt
    """
    try:
        # Save uploaded image
        image_filename = f"{uuid.uuid4()}_{image.filename}"
        image_path = os.path.join(Config.UPLOAD_DIR, image_filename)
        
        async with aiofiles.open(image_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        # Save mask if provided
        mask_path = None
        if mask:
            mask_filename = f"{uuid.uuid4()}_{mask.filename}"
            mask_path = os.path.join(Config.UPLOAD_DIR, mask_filename)
            async with aiofiles.open(mask_path, 'wb') as f:
                content = await mask.read()
                await f.write(content)
        
        # Edit image
        image_urls = await paralon_client.edit_image(
            image_path=image_path,
            prompt=prompt,
            mask_path=mask_path,
            model=model,
            size=size,
            n=n
        )
        
        # Download and save edited images
        saved_paths = []
        for i, url in enumerate(image_urls):
            filename = f"{uuid.uuid4()}.png"
            save_path = os.path.join(Config.GENERATED_DIR, filename)
            await image_processor.download_image(url, save_path)
            saved_paths.append(f"/generated/{filename}")
        
        return {
            "success": True,
            "images": saved_paths,
            "urls": image_urls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/variation")
async def create_variation(
    image: UploadFile = File(...),
    model: str = Form("dall-e-2"),
    size: str = Form("1024x1024"),
    n: int = Form(1)
):
    """
    Create variations of an existing image
    """
    try:
        # Save uploaded image
        image_filename = f"{uuid.uuid4()}_{image.filename}"
        image_path = os.path.join(Config.UPLOAD_DIR, image_filename)
        
        async with aiofiles.open(image_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        # Create variations
        image_urls = await paralon_client.create_variation(
            image_path=image_path,
            model=model,
            size=size,
            n=n
        )
        
        # Download and save variation images
        saved_paths = []
        for i, url in enumerate(image_urls):
            filename = f"{uuid.uuid4()}.png"
            save_path = os.path.join(Config.GENERATED_DIR, filename)
            await image_processor.download_image(url, save_path)
            saved_paths.append(f"/generated/{filename}")
        
        return {
            "success": True,
            "images": saved_paths,
            "urls": image_urls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/style-transfer")
async def style_transfer(
    base_image: UploadFile = File(...),
    style_image: UploadFile = File(...),
    alpha: float = Form(0.5)
):
    """
    Apply style transfer by blending two images
    """
    try:
        # Save uploaded images
        base_filename = f"{uuid.uuid4()}_{base_image.filename}"
        base_path = os.path.join(Config.UPLOAD_DIR, base_filename)
        
        style_filename = f"{uuid.uuid4()}_{style_image.filename}"
        style_path = os.path.join(Config.UPLOAD_DIR, style_filename)
        
        async with aiofiles.open(base_path, 'wb') as f:
            content = await base_image.read()
            await f.write(content)
        
        async with aiofiles.open(style_path, 'wb') as f:
            content = await style_image.read()
            await f.write(content)
        
        # Apply style transfer
        output_filename = f"{uuid.uuid4()}.png"
        output_path = os.path.join(Config.GENERATED_DIR, output_filename)
        image_processor.apply_style_transfer(base_path, style_path, output_path, alpha)
        
        return {
            "success": True,
            "image": f"/generated/{output_filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
