"""
Security module for API key authentication
"""

from fastapi import HTTPException, status, Header
from typing import Optional
from app.config import settings


def require_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """
    Dependency function to require and validate API key.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: 401 if API key is missing or invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "API-Key"},
        )

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )

    return x_api_key