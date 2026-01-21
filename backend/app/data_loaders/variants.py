"""
DSS variants data loader
Loads DSS (Dead Sea Scrolls) variant readings
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from .base import DataLoader


class VariantLoader(DataLoader):
    """Loader for DSS variant data from DSS JSON"""

    def __init__(self, data_path: Optional[str] = None):
        super().__init__(data_path)
        self.dss_path = self.data_path / "dss" / "dss.json"

    def load_dss_data(self) -> Dict[str, Any]:
        """Load the complete DSS data file"""
        cache_key = "dss_data"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            data = self.load_json("dss/dss.json")
            self._cache[cache_key] = data
            return data
        except FileNotFoundError:
            return {}

    def get_book_variants(self, book_name: str) -> Optional[Dict[str, Any]]:
        """Get all variants for a specific book"""
        dss_data = self.load_dss_data()
        books = dss_data.get("books", {})
        return books.get(book_name)

    def get_chapter_variants(self, book_name: str, chapter: int) -> Optional[Dict[str, Any]]:
        """Get all variants for a specific book chapter"""
        book_data = self.get_book_variants(book_name)
        if not book_data:
            return None

        chapters = book_data.get("chapters", {})
        return chapters.get(str(chapter))

    def get_verse_variants(self, book_name: str, chapter: int, verse: int) -> Optional[Dict[str, Any]]:
        """Get variants for a specific verse"""
        chapter_data = self.get_chapter_variants(book_name, chapter)
        if not chapter_data:
            return None

        verses = chapter_data.get("verses", {})
        return verses.get(str(verse))

    def get_variant_for_word(self, book_name: str, chapter: int, verse: int, word_position: int = 0) -> Optional[Dict[str, Any]]:
        """Get DSS variant for a specific word position in a verse"""
        verse_data = self.get_verse_variants(book_name, chapter, verse)
        if not verse_data:
            return None

        # For now, return the main variant data
        # In the future, this could be enhanced to match specific word positions
        return verse_data

    def get_dss_variants(self, book_name: str, chapter: int, verse: int) -> List[Dict[str, Any]]:
        """Get DSS variants for a specific verse"""
        verse_data = self.get_verse_variants(book_name, chapter, verse)
        if not verse_data:
            return []

        variants = []
        # DSS structure may contain multiple variants per verse
        # For now, extract variant information
        dss_variants = verse_data.get("variants", [])

        for variant in dss_variants:
            variant_data = {
                "word_position": variant.get("word_position", 0),
                "dss_text": variant.get("dss_text", ""),
                "manuscript": variant.get("manuscript", ""),
                "commentary": variant.get("commentary")
            }
            variants.append(variant_data)

        # If no structured variants, create a single variant from main verse data
        if not variants and verse_data:
            variant_data = {
                "word_position": verse_data.get("word_position", 0),
                "dss_text": verse_data.get("dss_text", ""),
                "manuscript": verse_data.get("manuscript", ""),
                "commentary": verse_data.get("commentary")
            }
            variants.append(variant_data)

        return variants

    def get_available_books(self) -> List[str]:
        """Get list of books that have DSS variants"""
        dss_data = self.load_dss_data()
        books = dss_data.get("books", {})
        return list(books.keys())


# Global instance
variant_loader = VariantLoader()
