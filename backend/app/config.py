"""
Configuration settings for Davar FastAPI backend
"""

from pathlib import Path
import json
from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import field_validator


BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data"


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Security
    api_key: str = ""

    # CORS Settings
    allowed_origins: List[str] = [
        "http://localhost:2221",
        "http://localhost:3000",
        "http://localhost:3002",
        "https://davar.pages.dev",
    ]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse JSON array or comma-separated string into a list."""
        if isinstance(v, str):
            raw = v.strip()
            if not raw:
                return []
            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    parsed = raw
                else:
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed if str(origin).strip()]
            return [origin.strip() for origin in raw.split(",") if origin.strip()]
        return v

    # Rate Limiting
    rate_limit: str = "100/minute"

    # Environment
    env: str = "development"

    # Supabase (for TS2009 private content sync and future user data)
    supabase_url: Optional[str] = None
    supabase_service_key: Optional[str] = None

    # Data Source Paths (absolute to avoid cwd issues)
    data_path: str = str(DEFAULT_DATA_PATH)

    @field_validator("data_path", mode="before")
    @classmethod
    def resolve_data_path(cls, v):
        """Resolve relative paths against the project root."""
        if not v:
            return str(DEFAULT_DATA_PATH)
        path = Path(str(v))
        if not path.is_absolute():
            path = (BACKEND_ROOT / path).resolve()
        return str(path)

    class Config:
        env_file = str(BACKEND_ROOT / ".env")
        env_file_encoding = "utf-8"
        env_prefix = "DAVAR_"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()

# Bundle version numbers — bump when data changes to trigger re-download on clients
BUNDLE_VERSIONS: dict[str, int] = {
    "tanaj": 1,
    "besorah": 1,
    "dss": 1,
    "dictionary": 1,
    "tth": 1,
    "ts2009": 1,
}
