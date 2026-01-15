"""
SQLite Database Loader for Delitzsch Strong's Matcher

Connects to SQLite3 database and queries verses with embedded Strong's numbers.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SQLiteLoader:
    """
    Loads Hebrew text with Strong's numbers from SQLite database.
    """

    # Book number to name mapping (based on database analysis)
    BOOK_MAPPINGS = {
        470: "matthew",
        480: "mark",
        490: "luke",
        500: "john",
        510: "acts",
        520: "romans",
        530: "corinthians1",
        540: "corinthians2",
        550: "galatians",
        560: "ephesians",
        570: "philippians",
        580: "colossians",
        590: "thessalonians1",
        600: "thessalonians2",
        610: "timothy1",
        620: "timothy2",
        630: "titus",
        640: "philemon",
        650: "hebrews",
        660: "james",
        670: "peter1",
        680: "peter2",
        690: "john1",
        700: "john2",
        710: "john3",
        720: "jude",
        730: "revelation"
    }

    def __init__(self, db_path: Path):
        """
        Initialize SQLite loader.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._connect()

    def _connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to connect to database {self.db_path}: {e}")

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_book_name(self, book_number: int) -> Optional[str]:
        """
        Get book name for a given book number.

        Args:
            book_number: Book number from database

        Returns:
            Book name or None if not found
        """
        return self.BOOK_MAPPINGS.get(book_number)

    def get_book_number(self, book_name: str) -> Optional[int]:
        """
        Get book number for a given book name.

        Args:
            book_name: Book name

        Returns:
            Book number or None if not found
        """
        for number, name in self.BOOK_MAPPINGS.items():
            if name == book_name:
                return number
        return None

    def get_verse_text(self, book_number: int, chapter: int, verse: int) -> Optional[str]:
        """
        Get Hebrew text for a specific verse.

        Args:
            book_number: Book number from database
            chapter: Chapter number
            verse: Verse number

        Returns:
            Hebrew text with Strong's tags or None if not found
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT text FROM verses WHERE book_number = ? AND chapter = ? AND verse = ?",
                (book_number, chapter, verse)
            )
            row = cursor.fetchone()
            return row['text'] if row else None
        except sqlite3.Error as e:
            print(f"Database error getting verse {book_number}:{chapter}:{verse}: {e}")
            return None

    def get_chapter_verses(self, book_number: int, chapter: int) -> List[Dict]:
        """
        Get all verses for a chapter.

        Args:
            book_number: Book number from database
            chapter: Chapter number

        Returns:
            List of verse dictionaries with verse_number and text
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT verse, text FROM verses WHERE book_number = ? AND chapter = ? ORDER BY verse",
                (book_number, chapter)
            )

            verses = []
            for row in cursor.fetchall():
                verses.append({
                    'verse': row['verse'],
                    'text': row['text']
                })
            return verses
        except sqlite3.Error as e:
            print(f"Database error getting chapter {book_number}:{chapter}: {e}")
            return []

    def get_book_verses(self, book_number: int) -> Dict[int, List[Dict]]:
        """
        Get all verses for a book, organized by chapter.

        Args:
            book_number: Book number from database

        Returns:
            Dictionary mapping chapter numbers to lists of verse dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT chapter, verse, text FROM verses WHERE book_number = ? ORDER BY chapter, verse",
                (book_number,)
            )

            chapters = {}
            for row in cursor.fetchall():
                chapter_num = row['chapter']
                if chapter_num not in chapters:
                    chapters[chapter_num] = []

                chapters[chapter_num].append({
                    'verse': row['verse'],
                    'text': row['text']
                })
            return chapters
        except sqlite3.Error as e:
            print(f"Database error getting book {book_number}: {e}")
            return {}

    def get_all_books(self) -> List[Tuple[int, str]]:
        """
        Get list of all available books.

        Returns:
            List of (book_number, book_name) tuples
        """
        return [(num, name) for num, name in self.BOOK_MAPPINGS.items()]

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Singleton instance
_loader_instance = None

def get_sqlite_loader(db_path: Optional[Path] = None) -> SQLiteLoader:
    """
    Get singleton SQLite loader instance.

    Args:
        db_path: Optional path to database file. If not provided, uses default from config.

    Returns:
        SQLiteLoader instance
    """
    global _loader_instance
    if _loader_instance is None:
        if db_path is None:
            # Import here to avoid circular imports
            from config import SQLITE_DB
            db_path = SQLITE_DB
        _loader_instance = SQLiteLoader(db_path)
    return _loader_instance