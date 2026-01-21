"""
Configuration settings for Davar FastAPI backend
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Security
    api_key: str

    # CORS Settings
    allowed_origins: List[str] = ["http://localhost:2221"]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Rate Limiting
    rate_limit: str = "100/minute"

    # Environment
    env: str = "development"

    # Supabase (future user data)
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # Data Source Paths (relative to backend directory)
    data_path: str = "../data"

    class Config:
        env_file = "/Users/jhonny/davar/backend/.env"
        env_file_encoding = "utf-8"
        env_prefix = "DAVAR_"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()
