import os
import asyncio
from openai import OpenAI
from app.config import Config

class ParalonClient:
    """Client for interacting with ParalonCloud's OpenAI-compatible API"""
    
    def __init__(self):
        Config.validate()
        self.client = OpenAI(
            api_key=Config.PARALONCLOUD_API_KEY,
            base_url=Config.PARALONCLOUD_API_BASE
        )
    
    async def generate_image(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024", quality: str = "standard", n: int = 1):
        """
        Generate an image from a text prompt
        
        Args:
            prompt: Text description of the image to generate
            model: Model to use (e.g., "dall-e-3", "dall-e-2")
            size: Image size (e.g., "1024x1024", "1792x1024", "1024x1792")
            quality: Image quality ("standard" or "hd")
            n: Number of images to generate
        
        Returns:
            List of image URLs or base64 encoded images
        """
        try:
            # Run synchronous OpenAI call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=n
                )
            )
            
            if not response or not response.data:
                raise Exception("No data returned from API")
            
            # Extract image URLs or base64 data
            results = []
            for img in response.data:
                if hasattr(img, 'url') and img.url:
                    results.append(img.url)
                elif hasattr(img, 'b64_json') and img.b64_json:
                    results.append(img.b64_json)
                else:
                    # Try to get the image data directly
                    results.append(str(img))
            
            return results if results else []
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                raise Exception(f"Authentication failed. Check your PARALONCLOUD_API_KEY in .env file. Error: {error_msg}")
            elif "404" in error_msg or "Not Found" in error_msg:
                raise Exception(f"API endpoint not found. Check PARALONCLOUD_API_BASE in .env file. Error: {error_msg}")
            else:
                raise Exception(f"Error generating image: {error_msg}")
    
    async def edit_image(self, image_path: str, prompt: str, mask_path: str = None, model: str = "dall-e-2", size: str = "1024x1024", n: int = 1):
        """
        Edit an existing image using a prompt
        
        Args:
            image_path: Path to the image file to edit
            prompt: Description of the desired edit
            mask_path: Optional path to a mask image (transparent areas indicate where to edit)
            model: Model to use
            size: Output image size
            n: Number of variations to generate
        
        Returns:
            List of edited image URLs or base64 encoded images
        """
        try:
            with open(image_path, "rb") as image_file:
                image = image_file.read()
            
            mask = None
            if mask_path and os.path.exists(mask_path):
                with open(mask_path, "rb") as mask_file:
                    mask = mask_file.read()
            
            # Run synchronous OpenAI call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.images.edit(
                    model=model,
                    image=image,
                    prompt=prompt,
                    mask=mask,
                    size=size,
                    n=n
                )
            )
            
            return [img.url for img in response.data] if response.data and hasattr(response.data[0], 'url') else [img.b64_json for img in response.data] if response.data else []
        except Exception as e:
            raise Exception(f"Error editing image: {str(e)}")
    
    async def create_variation(self, image_path: str, model: str = "dall-e-2", size: str = "1024x1024", n: int = 1):
        """
        Create variations of an existing image
        
        Args:
            image_path: Path to the image file
            model: Model to use
            size: Output image size
            n: Number of variations to generate
        
        Returns:
            List of variation image URLs or base64 encoded images
        """
        try:
            with open(image_path, "rb") as image_file:
                image = image_file.read()
            
            # Run synchronous OpenAI call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.images.create_variation(
                    model=model,
                    image=image,
                    size=size,
                    n=n
                )
            )
            
            return [img.url for img in response.data] if response.data and hasattr(response.data[0], 'url') else [img.b64_json for img in response.data] if response.data else []
        except Exception as e:
            raise Exception(f"Error creating image variation: {str(e)}")
