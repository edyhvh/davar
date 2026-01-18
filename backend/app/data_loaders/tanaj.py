"""
Tanaj (OE) data loader
Loads Hebrew text from Open English (OE) JSON files
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from . import DataLoader


class TanajLoader(DataLoader):
    """Loader for Tanaj Hebrew text from OE data"""

    def __init__(self, data_path: str = None):
        super().__init__(data_path)
        self.oe_path = self.data_path / "oe"

    def get_book_chapters(self, book_name: str) -> List[int]:
        """Get list of available chapters for a book"""
        book_path = self.oe_path / book_name
        if not book_path.exists():
            return []

        chapters = []
        for file_path in book_path.glob("*.json"):
            try:
                chapter_num = int(file_path.stem)
                chapters.append(chapter_num)
            except ValueError:
                continue
        return sorted(chapters)

    def load_chapter(self, book_name: str, chapter: int) -> List[Dict[str, Any]]:
        """Load all verses for a specific book chapter"""
        cache_key = f"oe_{book_name}_{chapter}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        file_path = f"oe/{book_name}/{chapter}.json"
        try:
            verses = self.load_json(file_path)
            self._cache[cache_key] = verses
            return verses
        except FileNotFoundError:
            return []

    def load_verse(self, book_name: str, chapter: int, verse: int) -> Optional[Dict[str, Any]]:
        """Load a specific verse"""
        verses = self.load_chapter(book_name, chapter)
        for v in verses:
            if v.get("verse") == verse:
                return v
        return None

    def get_available_books(self) -> List[str]:
        """Get list of all available OE books"""
        if not self.oe_path.exists():
            return []

        books = []
        for item in self.oe_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                books.append(item.name)
        return sorted(books)

    def get_books_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all available OE books"""
        books = []
        available_books = self.get_available_books()

        for book_name in available_books:
            book_path = self.oe_path / book_name
            chapter_count = len(self.get_book_chapters(book_name))

            # Map book names and sections
            section = self._get_book_section(book_name)

            book_metadata = {
                'name': book_name,
                'total_chapters': chapter_count,
                'section': section
            }
            books.append(book_metadata)

        return books

    def get_chapters(self, book_name: str) -> List[int]:
        """Get list of available chapters for a book"""
        return self.get_book_chapters(book_name)

    def get_verses(self, book_name: str, chapter: int) -> List[Dict[str, Any]]:
        """Load all verses for a specific book chapter"""
        return self.load_chapter(book_name, chapter)

    def _get_book_section(self, book_name: str) -> str:
        """Map book name to section (torah, neviim, ketuvim)"""
        torah_books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy']
        neviim_books = ['joshua', 'judges', 'samuel1', 'samuel2', 'kings1', 'kings2',
                       'isaiah', 'jeremiah', 'ezekiel', 'hosea', 'joel', 'amos',
                       'obadiah', 'jonah', 'micah', 'nahum', 'habakkuk', 'zephaniah',
                       'haggai', 'zechariah', 'malachi']
        ketuvim_books = ['psalms', 'proverbs', 'job', 'songofsolomon', 'ruth',
                        'lamentations', 'ecclesiastes', 'esther', 'daniel', 'ezra',
                        'nehemiah', 'chronicles1', 'chronicles2']

        if book_name in torah_books:
            return 'torah'
        elif book_name in neviim_books:
            return 'neviim'
        elif book_name in ketuvim_books:
            return 'ketuvim'
        else:
            return 'unknown'


# Global instance
tanaj_loader = TanajLoader()