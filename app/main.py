from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
from typing import Optional
import aiofiles

from app.config import Config
from app.paralon_client import ParalonClient
from app.image_processor import ImageProcessor

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

# Initialize clients
paralon_client = ParalonClient()
image_processor = ImageProcessor()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "ParalonCloud Image Generation & Editing Tool API"}

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
    try:
        image_urls = await paralon_client.generate_image(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
            n=n
        )
        
        # Download and save images locally
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
