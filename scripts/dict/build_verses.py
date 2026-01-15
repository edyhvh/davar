#!/usr/bin/env python3
"""
Hebrew Scripture Verse Builder - Main Script

Builds lightweight verse JSON files for all books of the Hebrew Scriptures (Tanakh).
This is the main entry point for the verse generation pipeline.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from book_mappings import BookMapper
from strong_processor import StrongProcessor
from morphus_loader import MorphusLoader
from verse_processor import VerseProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VerseBuilder:
    """Main application class for building Hebrew Scripture verses."""

    def __init__(self):
        self.strong_processor = StrongProcessor()
        self.morphus_loader = MorphusLoader(self.strong_processor)
        self.verse_processor = VerseProcessor(self.strong_processor, self.morphus_loader)

    def run(self, book_key: Optional[str] = None, chapter_num: Optional[int] = None, verbose: bool = False) -> None:
        """
        Main execution method.

        Args:
            book_key: Specific book to process, or None for all books
            chapter_num: Specific chapter to process, or None for all chapters
            verbose: Enable verbose output
        """
        print("=" * 70)
        print("HEBREW SCRIPTURE VERSE BUILDER")
        print("=" * 70)
        print(f"📁 Output directory: {config.BOOKS_DIR}")
        print(f"📁 OE directory: {config.OE_DIR}")
        print(f"📁 Morphus directory: {config.MORPHUS_DIR}")
        print()

        if not config.OE_DIR.exists():
            logger.error(f"❌ OE directory not found: {config.OE_DIR}")
            return

        total_verses = 0
        total_errors = 0
        books_processed = 0

        if book_key:
            # Process only the specified book
            book_key = book_key.lower()
            if book_key not in BookMapper.BOOK_MAPPING:
                logger.error(f"❌ Book not found in mapping: {book_key}")
                logger.error(f"Available books: {', '.join(sorted(BookMapper.BOOK_MAPPING.keys()))}")
                return

            book_dir = config.OE_DIR / book_key
            if not book_dir.exists():
                logger.error(f"❌ Book directory not found: {book_dir}")
                return

            verses, errors, book_data = self.verse_processor.process_book(book_key, book_dir, chapter_num, verbose)
            total_verses += verses
            total_errors += errors

            # Save consolidated book file
            if book_data:
                book_id = BookMapper.get_book_id(BookMapper.get_book_info(book_key))
                output_file = config.BOOKS_DIR / f"{book_id}.json"

                # Sort chapters and verses
                sorted_book_data = {}
                for chapter in sorted(book_data.keys(), key=int):
                    sorted_chapter_data = {}
                    for verse in sorted(book_data[chapter].keys(), key=int):
                        sorted_chapter_data[verse] = book_data[chapter][verse]
                    sorted_book_data[chapter] = sorted_chapter_data

                # Save consolidated file
                config.BOOKS_DIR.mkdir(exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(sorted_book_data, f, ensure_ascii=False, separators=(',', ':'))

                if verbose:
                    print(f"💾 Saved consolidated book: {output_file}")

            books_processed = 1
        else:
            # Process each book available in oe/
            for book_dir in sorted(config.OE_DIR.iterdir()):
                if not book_dir.is_dir():
                    continue

                book_key_iter = book_dir.name.lower()

                # Check if the book is in our mapping
                if book_key_iter not in BookMapper.BOOK_MAPPING:
                    if verbose:
                        print(f"⚠️  Unmapped book: {book_key_iter} (skipping...)")
                    continue

                verses, errors, book_data = self.verse_processor.process_book(book_key_iter, book_dir, None, verbose)
                total_verses += verses
                total_errors += errors

                # Save consolidated book file
                if book_data:
                    book_id = BookMapper.get_book_id(BookMapper.get_book_info(book_key_iter))
                    output_file = config.BOOKS_DIR / f"{book_id}.json"

                    # Sort chapters and verses
                    sorted_book_data = {}
                    for chapter in sorted(book_data.keys(), key=int):
                        sorted_chapter_data = {}
                        for verse in sorted(book_data[chapter].keys(), key=int):
                            sorted_chapter_data[verse] = book_data[chapter][verse]
                        sorted_book_data[chapter] = sorted_chapter_data

                    # Save consolidated file
                    config.BOOKS_DIR.mkdir(exist_ok=True)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(sorted_book_data, f, ensure_ascii=False, separators=(',', ':'))

                    if verbose:
                        print(f"💾 Saved consolidated book: {output_file}")

                books_processed += 1

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"📚 Books processed: {books_processed}")
        print(f"✅ Verses generated: {total_verses}")
        print(f"❌ Errors: {total_errors}")
        print(f"📁 Files saved in: {config.BOOKS_DIR}")
        print()


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Generate lightweight verse JSON files from Hebrew Scripture data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all books
  python scripts/dict/build_verses.py

  # Process specific book
  python scripts/dict/build_verses.py --book genesis

  # Process specific chapter
  python scripts/dict/build_verses.py --book genesis --chapter 1

  # Verbose output
  python scripts/dict/build_verses.py --verbose
        """
    )
    parser.add_argument(
        '--book',
        type=str,
        help='Book key to process (e.g., genesis, exodus). If not specified, processes all books.'
    )
    parser.add_argument(
        '--chapter',
        type=int,
        help='Chapter number to process. If not specified, processes all chapters of the book.'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run the application
    builder = VerseBuilder()
    builder.run(args.book, args.chapter, args.verbose)


if __name__ == "__main__":
    main()
