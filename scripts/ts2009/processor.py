"""
TS2009 Bible Processor - Main Processing Module

Processes TS2009 SQLite database into streamlined JSON format optimized for Davar app.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    # Try relative import for module usage
    from .config import (
        BOOKS_MAPPING, SECTIONS_MAPPING,
        DEFAULT_DB_PATH, DEFAULT_OUTPUT_DIR, DEFAULT_TEMP_DIR, PROCESSOR_VERSION, PROJECT_ROOT
    )
    from .text_processor import TextCleaner
except ImportError:
    # Fall back to absolute import for direct script execution
    from config import (
        BOOKS_MAPPING, SECTIONS_MAPPING,
        DEFAULT_DB_PATH, DEFAULT_OUTPUT_DIR, DEFAULT_TEMP_DIR, PROCESSOR_VERSION, PROJECT_ROOT
    )
    from text_processor import TextCleaner


@dataclass
class VerseData:
    """Represents a single verse with minimal required fields."""
    number: int
    text: str
    footnotes: List[str] = None

    def __post_init__(self):
        if self.footnotes is None:
            self.footnotes = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'number': self.number,
            'text': self.text
        }
        if self.footnotes:
            result['footnotes'] = self.footnotes
        return result


@dataclass
class ChapterData:
    """Represents a chapter with its verses."""
    number: int
    verses: List[VerseData]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'number': self.number,
            'verses': [verse.to_dict() for verse in self.verses]
        }


@dataclass
class BookMetadata:
    """Represents book metadata information."""
    book_id: str
    book_name: str
    book_hebrew: str
    book_anglicized: str
    section: str
    section_english: str
    section_hebrew: str
    expected_chapters: int
    total_chapters: int
    total_verses: int


@dataclass
class ProcessedBook:
    """Represents a complete processed book with metadata and chapters."""
    metadata: BookMetadata
    chapters: List[ChapterData]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'metadata': asdict(self.metadata),
            'chapters': [chapter.to_dict() for chapter in self.chapters]
        }


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

        # Group verses by chapter
        chapters_dict: Dict[int, List[Tuple[int, str]]] = {}
        for book, chapter, verse, scripture in raw_verses:
            if chapter not in chapters_dict:
                chapters_dict[chapter] = []
            chapters_dict[chapter].append((verse, scripture))

        # Process each chapter
        chapters = []
        for chapter_num in sorted(chapters_dict.keys()):
            verses_data = chapters_dict[chapter_num]
            verses = []
            
            for verse_num, scripture in verses_data:
                # Process text and extract footnotes
                processed = self.text_cleaner.process_verse_text(scripture)
                
                verse_data = VerseData(
                    number=verse_num,
                    text=processed.text,
                    footnotes=processed.footnotes
                )
                verses.append(verse_data)
            
            chapter_data = ChapterData(number=chapter_num, verses=verses)
            chapters.append(chapter_data)

        # Create metadata
        section_info = SECTIONS_MAPPING.get(book_info['section'], {})
        metadata = BookMetadata(
            book_id=book_info['name_english'].lower(),
            book_name=book_info['name_english'],
            book_hebrew=book_info['name_hebrew'],
            book_anglicized=book_info['name_anglicized'],
            section=book_info['section'],
            section_english=section_info.get('english', book_info['section']),
            section_hebrew=section_info.get('hebrew', ''),
            expected_chapters=book_info['expected_chapters'],
            total_chapters=len(chapters),
            total_verses=sum(len(ch.verses) for ch in chapters)
        )

        logging.info(f"  ✓ Processed {len(chapters)} chapters, {metadata.total_verses} verses")

        return ProcessedBook(metadata=metadata, chapters=chapters)


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

        # Use anglicized name for filename
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

    def get_available_books(self) -> List[str]:
        """Get list of available book anglicized names."""
        book_numbers = self.db_handler.get_book_numbers()
        books = []
        for book_num in book_numbers:
            book_info = self.book_processor.get_book_info(book_num)
            if book_info:
                books.append(book_info['name_anglicized'])
        return books

    def get_book_number_by_name(self, book_name: str) -> Optional[int]:
        """Get book number by anglicized name."""
        for book_num, book_info in BOOKS_MAPPING.items():
            if book_info['name_anglicized'] == book_name:
                return book_num
        return None
