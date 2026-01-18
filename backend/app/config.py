"""
Configuration settings for Davar FastAPI backend
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Security
    api_key: str

    # CORS Settings
    allowed_origins: List[str] = ["http://localhost:2221"]

    # Rate Limiting
    rate_limit: str = "100/minute"

    # Environment
    env: str = "development"

    # Data Source Paths (relative to backend directory)
    data_path: str = "../data"

    class Config:
        env_file = ".env"
        env_prefix = "DAVAR_"
        case_sensitive = False


# Global settings instance
settings = Settings()