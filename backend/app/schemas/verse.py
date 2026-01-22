"""
Verse-related schemas for API responses
"""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class WordResponse(BaseModel):
    """Response model for individual Hebrew words"""
    position: int
    text: str
    strong: Optional[str] = None
    morph: Optional[str] = None
    prefixes: List[str] = []
    has_dss_variant: bool = False


class DssVariant(BaseModel):
    """Response model for DSS manuscript variants"""
    word_position: int
    dss_text: str
    manuscript: str
    commentary: Optional[str] = None


class TranslationFootnote(BaseModel):
    """Response model for translation footnotes"""
    marker: str
    number: str
    word: str
    explanation: str


class VerseResponse(BaseModel):
    """Response model for verse data"""
    chapter: int
    verse: int
    hebrew: str
    words: List[WordResponse]
    translation: Optional[str] = None
    translation_language: Optional[str] = None
    translation_footnotes: Optional[List[TranslationFootnote]] = None
    dss: Optional[List[DssVariant]] = None