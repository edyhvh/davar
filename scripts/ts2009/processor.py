"""
TS2009 Bible Processor - Main Processing Module

Processes TS2009 SQLite database into streamlined JSON format optimized for Davar app.
"""

import sqlite3
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    # Try relative import for module usage
    from .config import (
        BOOKS_MAPPING, SECTIONS_MAPPING, COMMON_HEBREW_TERMS,
        DEFAULT_DB_PATH, DEFAULT_OUTPUT_DIR, DEFAULT_TEMP_DIR, PROCESSOR_VERSION, PROJECT_ROOT
    )
except ImportError:
    # Fall back to absolute import for direct script execution
    from config import (
        BOOKS_MAPPING, SECTIONS_MAPPING, COMMON_HEBREW_TERMS,
        DEFAULT_DB_PATH, DEFAULT_OUTPUT_DIR, DEFAULT_TEMP_DIR, PROCESSOR_VERSION, PROJECT_ROOT
    )


@dataclass
class VerseData:
    """Represents a single verse with minimal required fields."""
    book: str
    book_id: str
    book_ts2009_name: str
    section: str
    chapter: int
    verse: int
    status: str = "present"
    text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class BookMetadata:
    """Represents book metadata information."""
    book_id: str
    expected_chapters: int
    section: str
    section_english: str
    total_chapters: int
    total_verses: int


@dataclass
class ProcessedBook:
    """Represents a complete processed book with metadata and verses."""
    metadata: BookMetadata
    verses: List[VerseData]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'metadata': asdict(self.metadata),
            'verses': [verse.to_dict() for verse in self.verses]
        }


class TextCleaner:
    """Handles cleaning and processing of TS2009 text content."""

    @staticmethod
    def clean_html_text(text: str) -> str:
        """
        Clean HTML text from TS2009, preserving Hebrew content and essential formatting.

        Args:
            text: Raw text from database

        Returns:
            Cleaned text ready for app consumption
        """
        if not text:
            return ""

        # Remove HTML tags but preserve content
        text = re.sub(r'<blu>(.*?)</blu>', r'\1', text)  # Remove blue styling
        text = re.sub(r'<red>(.*?)</red>', r'\1', text)  # Remove red styling
        text = re.sub(r'<b>(.*?)</b>', r'\1', text)     # Remove bold
        text = re.sub(r'<sup>([^<]*)</sup>', r'[\1]', text)  # Convert superscripts to brackets
        text = re.sub(r'<ref>([^<]*)</ref>', r'[\1]', text)  # Convert references to brackets
        text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', text)     # Remove links
        text = re.sub(r'<heb>(.*?)</heb>', r'\1', text)     # Preserve Hebrew content
        text = re.sub(r'<em>(.*?)</em>', r'\1', text)       # Remove emphasis
        text = re.sub(r'<u>(.*?)</u>', r'\1', text)         # Remove underline

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class DatabaseHandler:
    """Handles all database operations for TS2009 processing."""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")

    def get_book_numbers(self) -> List[int]:
        """Get all unique book numbers from the database."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT Book FROM Bible ORDER BY Book")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_verses_for_book(self, book_num: int) -> List[Tuple[int, int, int, str]]:
        """
        Get all verses for a specific book.

        Returns:
            List of tuples: (book, chapter, verse, scripture)
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            query = """
                SELECT Book, Chapter, Verse, Scripture
                FROM Bible
                WHERE Book = ?
                ORDER BY Chapter, Verse
            """
            cursor.execute(query, (book_num,))
            return cursor.fetchall()
        finally:
            conn.close()


class BookProcessor:
    """Processes individual books from TS2009 database."""

    def __init__(self, db_handler: DatabaseHandler):
        self.db_handler = db_handler
        self.text_cleaner = TextCleaner()

    def get_book_info(self, book_num: int) -> Optional[Dict[str, Any]]:
        """Get book metadata from configuration."""
        return BOOKS_MAPPING.get(book_num)

    def create_verse_data(self, book_info: Dict[str, Any], chapter: int, verse: int,
                         scripture: str) -> VerseData:
        """Create a VerseData object from raw database data."""
        cleaned_text = self.text_cleaner.clean_html_text(scripture)

        return VerseData(
            book=book_info['name_anglicized'],
            book_id=book_info['name_english'].lower(),
            book_ts2009_name=f"{book_info['name_hebrew']}/{book_info['name_english']}",
            section=book_info['section'],
            chapter=chapter,
            verse=verse,
            text=cleaned_text
        )

    def process_book(self, book_num: int) -> Optional[ProcessedBook]:
        """
        Process a complete book and return structured data.

        Args:
            book_num: TS2009 book number

        Returns:
            ProcessedBook object or None if processing failed
        """
        book_info = self.get_book_info(book_num)
        if not book_info:
            logging.warning(f"Book {book_num} not found in configuration")
            return None

        logging.info(f"Processing book {book_num}: {book_info['name_anglicized']}")

        # Get raw verses from database
        raw_verses = self.db_handler.get_verses_for_book(book_num)
        if not raw_verses:
            logging.warning(f"No verses found for book {book_num}")
            return None

        # Process verses
        verses = []
        chapters_seen = set()

        for book, chapter, verse, scripture in raw_verses:
            verse_data = self.create_verse_data(book_info, chapter, verse, scripture)
            verses.append(verse_data)
            chapters_seen.add(chapter)

        # Create metadata
        metadata = BookMetadata(
            book_id=book_info['name_english'].lower(),
            expected_chapters=book_info['expected_chapters'],
            section=book_info['section'],
            section_english=SECTIONS_MAPPING[book_info['section']]['english'],
            total_chapters=len(chapters_seen),
            total_verses=len(verses)
        )

        logging.info(f"  ✓ Processed {len(chapters_seen)} chapters, {len(verses)} verses")

        return ProcessedBook(metadata=metadata, verses=verses)


class TS2009Processor:
    """Main processor for TS2009 Bible conversion."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH, output_dir: str = DEFAULT_OUTPUT_DIR):
        self.db_path = db_path

        # Convert relative paths to absolute paths relative to project root
        output_path = Path(output_dir)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path

        self.output_dir = output_path
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.db_handler = DatabaseHandler(db_path)
        self.book_processor = BookProcessor(self.db_handler)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def save_book_to_json(self, processed_book: ProcessedBook, output_path: Path) -> None:
        """Save a processed book to JSON file."""
        data = processed_book.to_dict()
        data['processed_date'] = datetime.now().isoformat()
        data['processor_version'] = PROCESSOR_VERSION

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def process_single_book(self, book_num: int, output_dir: Optional[Path] = None) -> bool:
        """
        Process a single book and save to JSON.

        Args:
            book_num: TS2009 book number
            output_dir: Optional custom output directory

        Returns:
            True if successful, False otherwise
        """
        target_dir = output_dir or self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        book_info = self.book_processor.get_book_info(book_num)
        if not book_info:
            logging.warning(f"Book {book_num} not found in configuration")
            return False

        processed_book = self.book_processor.process_book(book_num)
        if not processed_book:
            return False

        # Use anglicized name for filename (lowercase), but English name for book_id field
        filename = book_info['name_anglicized']
        output_file = target_dir / f"{filename}.json"
        self.save_book_to_json(processed_book, output_file)

        logging.info(f"  → Saved to {output_file}")
        return True

    def process_all_books(self, output_dir: Optional[Path] = None) -> List[str]:
        """
        Process all books in the database.

        Args:
            output_dir: Optional custom output directory

        Returns:
            List of processed book IDs
        """
        target_dir = output_dir or self.output_dir

        logging.info(f"Processing TS2009 from {self.db_path}")
        logging.info(f"Output directory: {target_dir}")

        book_numbers = self.db_handler.get_book_numbers()
        logging.info(f"Found {len(book_numbers)} books to process")

        processed_books = []

        for book_num in book_numbers:
            try:
                if self.process_single_book(book_num, target_dir):
                    book_info = self.book_processor.get_book_info(book_num)
                    if book_info:
                        processed_books.append(book_info['name_anglicized'])
            except Exception as e:
                logging.error(f"Failed to process book {book_num}: {e}")

        logging.info(f"✓ Processing complete: {len(processed_books)} books processed")
        return processed_books

    def process_to_temp(self) -> List[str]:
        """Process all books to temporary directory for testing."""
        temp_dir = Path(DEFAULT_TEMP_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)
        return self.process_all_books(temp_dir)


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description='TS2009 Bible Processor')
    parser.add_argument('--db-path', default=DEFAULT_DB_PATH,
                       help='Path to TS2009 database file')
    parser.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR,
                       help='Output directory for JSON files')
    parser.add_argument('--temp', action='store_true',
                       help='Process to temporary directory for testing')

    args = parser.parse_args()

    try:
        processor = TS2009Processor(args.db_path, args.output_dir)

        if args.temp:
            logging.info("Processing to temporary directory for testing...")
            processed = processor.process_to_temp()
        else:
            processed = processor.process_all_books()

        logging.info(f"Successfully processed {len(processed)} books")

    except Exception as e:
        logging.error(f"Processing failed: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
