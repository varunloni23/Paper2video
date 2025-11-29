import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

# Get the backend directory (where this file is located)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://neondb_owner:npg_Wp3OkPJ7EFxh@ep-fragrant-dust-ahntfjkd-pooler.c-3.us-east-1.aws.neon.tech/neondb?ssl=require"
    
    # Google Gemini API
    gemini_api_key: str = ""
    
    # OpenAI API Key
    openai_api_key: str = ""
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Storage paths - use absolute paths
    upload_dir: str = os.path.join(BACKEND_DIR, "uploads")
    output_dir: str = os.path.join(BACKEND_DIR, "outputs")
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    
    # Environment
    environment: str = "development"  # development, production
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        # Add frontend URL if set
        if self.frontend_url and self.frontend_url not in origins:
            origins.append(self.frontend_url)
        return origins
    
    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# Create directories if they don't exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)
