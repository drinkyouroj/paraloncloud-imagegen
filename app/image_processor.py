import os
import httpx
import aiofiles
from PIL import Image
import numpy as np
from app.config import Config

class ImageProcessor:
    """Utility class for image processing operations"""
    
    @staticmethod
    async def download_image(url: str, save_path: str) -> str:
        """Download an image from a URL and save it locally"""
        try:
            # Ensure directory exists
            dir_path = os.path.dirname(save_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                async with aiofiles.open(save_path, 'wb') as f:
                    await f.write(response.content)
                
                return save_path
        except Exception as e:
            raise Exception(f"Failed to download image from {url}: {str(e)}")
    
    @staticmethod
    def apply_style_transfer(base_image_path: str, style_image_path: str, output_path: str, alpha: float = 0.5):
        """
        Apply a simple style transfer by blending images
        
        Args:
            base_image_path: Path to the base image
            style_image_path: Path to the style reference image
            output_path: Path to save the result
            alpha: Blending factor (0.0 to 1.0)
        """
        base_img = Image.open(base_image_path).convert("RGB")
        style_img = Image.open(style_image_path).convert("RGB")
        
        # Resize style image to match base image
        style_img = style_img.resize(base_img.size, Image.Resampling.LANCZOS)
        
        # Convert to numpy arrays
        base_array = np.array(base_img, dtype=np.float32)
        style_array = np.array(style_img, dtype=np.float32)
        
        # Blend images
        blended = (1 - alpha) * base_array + alpha * style_array
        blended = np.clip(blended, 0, 255).astype(np.uint8)
        
        # Save result
        result_img = Image.fromarray(blended)
        result_img.save(output_path)
        return output_path
    
    @staticmethod
    def resize_image(image_path: str, output_path: str, max_size: tuple = (1024, 1024)):
        """Resize an image while maintaining aspect ratio"""
        img = Image.open(image_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(output_path)
        return output_path
    
    @staticmethod
    def convert_format(image_path: str, output_path: str, format: str = "PNG"):
        """Convert image to a different format"""
        img = Image.open(image_path)
        img.save(output_path, format=format)
        return output_path
