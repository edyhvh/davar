"""
Error response schemas for consistent error handling
"""

from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """Standard error response format"""
    detail: str
    error_code: Optional[str] = None