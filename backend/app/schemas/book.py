"""
Book-related schemas
"""

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class BookSection(str, Enum):
    """Book sections in Hebrew Scripture"""
    TORAH = "torah"      # Five Books of Moses
    NEVIIM = "neviim"    # Prophets
    KETUVIM = "ketuvim"  # Writings
    BESORAH = "besorah"  # Gospels/Acts


class BookResponse(BaseModel):
    """Book metadata response"""
    id: str           # Standard English name (e.g., "Genesis")
    name: str         # Standard English name (same as id)
    section: BookSection
    chapters: int     # Number of chapters
    order: str    # "tanaj" or "besorah"
    hebrew_name: str      # Hebrew characters (e.g., "בראשית")
    hebrew_transliteration: str  # Hebrew transliteration (e.g., "Bereshit")
    spanish_name: str    # Spanish name (e.g., "Génesis")