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
    text_no_nikud: Optional[str] = None
    strong: Optional[str] = None
    morph: Optional[str] = None
    prefixes: List[str] = []
    has_dss_variant: bool = False
    translit_en: Optional[str] = None
    translit_es: Optional[str] = None


class DssVariant(BaseModel):
    """Response model for DSS manuscript variants"""
    book: str
    chapter: int
    verse: int
    position: int
    dss_word: str
    masoretic_word: str
    dss_translit_en: Optional[str] = None
    dss_translit_es: Optional[str] = None
    comment_v2_en: Optional[str] = None
    comment_v2_es: Optional[str] = None
    comment_v2_he: Optional[str] = None
    masoretic_strong: Optional[str] = None
    dss_strong: Optional[str] = None


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