import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PARALONCLOUD_API_KEY = os.getenv("PARALONCLOUD_API_KEY")
    PARALONCLOUD_API_BASE = os.getenv("PARALONCLOUD_API_BASE", "https://paraloncloud.com/v1")
    
    # File paths
    UPLOAD_DIR = "uploads"
    GENERATED_DIR = "generated"
    
    # Create directories if they don't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(GENERATED_DIR, exist_ok=True)
    
    @classmethod
    def validate(cls):
        if not cls.PARALONCLOUD_API_KEY:
            raise ValueError("PARALONCLOUD_API_KEY not found in environment variables")
