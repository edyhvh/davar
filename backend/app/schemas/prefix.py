"""
Prefix-related schemas for API responses
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class PrefixResponse(BaseModel):
    """Response model for prefix data"""
    id: str
    main_form: Optional[str] = None
    type: Optional[str] = None
    transliteration_en: Optional[str] = None
    transliteration_es: Optional[str] = None
    meanings: Dict[str, List[str]] = Field(default_factory=dict)
    forms: List[str] = Field(default_factory=list)
    notes: Optional[Dict[str, str]] = None
