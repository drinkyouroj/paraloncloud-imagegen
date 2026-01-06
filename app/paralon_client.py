import os
import asyncio
import httpx
from openai import OpenAI
from app.config import Config

class ParalonClient:
    """Client for interacting with ParalonCloud's OpenAI-compatible API"""
    
    def __init__(self):
        Config.validate()
        self.api_key = Config.PARALONCLOUD_API_KEY
        self.base_url = Config.PARALONCLOUD_API_BASE.rstrip('/')
        
        # Try OpenAI client first, but we'll also support direct HTTP calls
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.use_openai_client = True
        except Exception:
            self.client = None
            self.use_openai_client = False
    
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
        # Try direct HTTP call first (more flexible for different API structures)
        try:
            return await self._generate_image_http(prompt, model, size, quality, n)
        except Exception as http_error:
            # Fall back to OpenAI client if HTTP fails
            if self.use_openai_client and self.client:
                try:
                    return await self._generate_image_openai(prompt, model, size, quality, n)
                except Exception as openai_error:
                    # If both fail, raise the more descriptive error
                    raise Exception(f"HTTP method failed: {str(http_error)}. OpenAI client also failed: {str(openai_error)}")
            else:
                raise http_error
    
    async def _generate_image_http(self, prompt: str, model: str, size: str, quality: str, n: int):
        """Generate image using direct HTTP calls"""
        # Try different endpoint variations
        endpoints = [
            f"{self.base_url}/images/generations",
            f"{self.base_url}/v1/images/generations",
            f"{self.base_url}/api/v1/images/generations",
            f"{self.base_url}/generate",
            f"{self.base_url}/v1/generate",
        ]
        
        payload = {
            "prompt": prompt,
            "model": model,
            "size": size,
            "n": n
        }
        
        # Add quality only for dall-e-3
        if model == "dall-e-3":
            payload["quality"] = quality
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        last_error = None
        async with httpx.AsyncClient(timeout=60.0) as client:
            for endpoint in endpoints:
                try:
                    response = await client.post(endpoint, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Handle different response formats
                        images = []
                        if "data" in data:
                            for img in data["data"]:
                                if "url" in img:
                                    images.append(img["url"])
                                elif "b64_json" in img:
                                    images.append(img["b64_json"])
                        elif "images" in data:
                            images = data["images"]
                        elif isinstance(data, list):
                            images = data
                        else:
                            # Try to extract any image URLs from the response
                            images = [str(data)]
                        
                        if images:
                            return images
                    
                    elif response.status_code == 404:
                        # Try next endpoint
                        continue
                    else:
                        error_text = response.text
                        raise Exception(f"API returned status {response.status_code}: {error_text}")
                        
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        last_error = f"Endpoint {endpoint} not found (404)"
                        continue
                    else:
                        raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
                except Exception as e:
                    last_error = str(e)
                    continue
        
        # If all endpoints failed
        raise Exception(f"All endpoint variations failed. Last error: {last_error}. Please check PARALONCLOUD_API_BASE in .env file. Current base URL: {self.base_url}")
    
    async def _generate_image_openai(self, prompt: str, model: str, size: str, quality: str, n: int):
        """Generate image using OpenAI client"""
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
        
        results = []
        for img in response.data:
            if hasattr(img, 'url') and img.url:
                results.append(img.url)
            elif hasattr(img, 'b64_json') and img.b64_json:
                results.append(img.b64_json)
            else:
                results.append(str(img))
        
        return results if results else []
    
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
