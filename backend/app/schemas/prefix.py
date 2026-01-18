"""
Prefix-related schemas for API responses
"""

from pydantic import BaseModel
from typing import List, Optional


class PrefixResponse(BaseModel):
    """Response model for prefix data"""
    id: str
    hebrew: Optional[str] = None
    meanings_en: List[str] = []
    meanings_es: List[str] = []
    examples: Optional[List[str]] = None