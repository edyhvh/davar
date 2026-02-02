"""
DSS variants data loader
Loads DSS (Dead Sea Scrolls) variant readings
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from .base import DataLoader
from .book_mapping import book_mapper


class VariantLoader(DataLoader):
    """Loader for DSS variant data from DSS JSON"""

    def __init__(self, data_path: Optional[str] = None):
        super().__init__(data_path)
        self.dss_books_path = self.data_path / "dss" / "books"

    def load_dss_book(self, book_key: str) -> Optional[Dict[str, Any]]:
        """Load a DSS book file by its DSS key."""
        cache_key = f"dss_book:{book_key}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            data = self.load_json(f"dss/books/{book_key}.json")
            self._cache[cache_key] = data
            return data
        except FileNotFoundError:
            return None

    def get_book_variants(self, book_name: str) -> Optional[Dict[str, Any]]:
        """Get all variants for a specific book"""
        book_key = book_mapper.to_dss_key(book_name)
        if not book_key:
            return None

        return self.load_dss_book(book_key)

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

        differences = verse_data.get("differences", [])
        variants = []
        for difference in differences:
            variants.append({
                "book": book_name,
                "chapter": chapter,
                "verse": verse,
                "position": difference.get("position", 0),
                "masoretic_word": difference.get("masoretic_word", ""),
                "dss_word": difference.get("dss_word", ""),
                "comment_v2_en": difference.get("comment_v2_en"),
                "comment_v2_es": difference.get("comment_v2_es"),
                "comment_v2_he": difference.get("comment_v2_he"),
                "masoretic_strong": difference.get("masoretic_strong"),
                "dss_strong": difference.get("dss_strong")
            })

        return variants

    def get_available_books(self) -> List[str]:
        """Get list of books that have DSS variants"""
        if not self.dss_books_path.exists():
            return []

        return sorted(
            path.stem
            for path in self.dss_books_path.glob("*.json")
            if path.is_file()
        )


# Global instance
variant_loader = VariantLoader()
