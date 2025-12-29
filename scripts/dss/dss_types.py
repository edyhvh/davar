"""
DSS Data Types

Common data types and classes for DSS processing.

Author: Davar Project Team
License: MIT
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class DSSVariant:
    """Data class representing a DSS textual variant."""
    book: str
    chapter: int
    verse: int
    masoretic_text: str
    dss_text: str
    variant_translation_en: str = ""
    variant_translation_es: str = ""
    comments_he: str = ""
    comments_en: str = ""
    comments_es: str = ""
    dss_source: str = ""
    variant_type: str = ""
    significance: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "book": self.book,
            "chapter": self.chapter,
            "verse": self.verse,
            "masoretic_text": self.masoretic_text,
            "dss_text": self.dss_text,
            "variant_translation_en": self.variant_translation_en,
            "variant_translation_es": self.variant_translation_es,
            "comments_he": self.comments_he,
            "comments_en": self.comments_en,
            "comments_es": self.comments_es,
            "dss_source": self.dss_source,
            "variant_type": self.variant_type,
            "significance": self.significance
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DSSVariant':
        """Create instance from dictionary."""
        return cls(**data)

    def validate(self) -> list:
        """Validate the variant data and return list of errors."""
        errors = []

        if not self.book:
            errors.append("Book is required")
        if not isinstance(self.chapter, int) or self.chapter < 1:
            errors.append("Chapter must be a positive integer")
        if not isinstance(self.verse, int) or self.verse < 1:
            errors.append("Verse must be a positive integer")
        if not self.masoretic_text.strip():
            errors.append("Masoretic text is required")
        if not self.dss_text.strip():
            errors.append("DSS text is required")

        return errors

