"""
Lexicon-related schemas for API responses
"""

from pydantic import BaseModel
from typing import List, Optional


class DefinitionItem(BaseModel):
    """Response model for definition items"""
    text: str
    source: str  # 'custom', 'strong', 'bdb'
    language: str  # 'en', 'es'


class LexiconResponse(BaseModel):
    """Response model for lexicon entries"""
    strong_number: str
    hebrew: Optional[str] = None
    definitions: List[DefinitionItem]
    root: Optional[str] = None
    root_strong: Optional[str] = None
    root_translit_en: Optional[str] = None
    root_translit_es: Optional[str] = None
    root_definitions: Optional[List[DefinitionItem]] = None
    occurrences_count: int
    instances: List[str] = []
