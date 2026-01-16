#!/usr/bin/env python3
"""
Delitzsch Strong's Matcher - Main CLI Entry Point

Processes Delitzsch Hebrew NT books and matches words to Strong's numbers
with prefix identification. Outputs data in book/chapter.json format.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    ensure_output_dirs, OUTPUT_DIR, UNMATCHED_WORDS_LOG
)
from dictionary_loader import get_dictionary_loader
from prefix_detector import PrefixDetector
from result_formatter import ResultFormatter
from word_matcher import WordMatcher
from book_processor import BookProcessor
from sqlite_loader import get_sqlite_loader


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def save_chapter_data(book_name: str, chapter_data: List[dict], dry_run: bool = False):
    """Save processed chapter data to JSON files"""
    book_dir = OUTPUT_DIR / book_name

    for chapter in chapter_data:
        chapter_num = chapter['chapter']
        output_file = book_dir / f"{chapter_num}.json"

        if dry_run:
            print(f"Would save: {output_file}")
            continue

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump([chapter], f, ensure_ascii=False, indent=2)
            print(f"Saved: {output_file}")
        except Exception as e:
            logging.error(f"Failed to save {output_file}: {e}")


def log_unmatched_words(word_matcher: WordMatcher):
    """Log unmatched words to file"""
    unmatched = word_matcher.get_unmatched_words()
    if not unmatched:
        return

    try:
        with open(UNMATCHED_WORDS_LOG, 'w', encoding='utf-8') as f:
            f.write("Unmatched words log\n")
            f.write("=" * 50 + "\n\n")
            for item in unmatched:
                f.write(f"Word: {item['word']}\n")
                f.write(f"Stem: {item['stem']}\n")
                f.write(f"Reason: {item['reason']}\n")
                f.write("-" * 30 + "\n")

        print(f"Unmatched words logged to: {UNMATCHED_WORDS_LOG}")
    except Exception as e:
        logging.error(f"Failed to write unmatched words log: {e}")


def process_book(book_name: str, dry_run: bool = False, verbose: bool = False) -> bool:
    """Process a single Delitzsch book from SQLite database"""
    if verbose:
        print(f"Processing book: {book_name}")

    try:
        # Initialize new modular architecture
        loader = get_dictionary_loader()
        prefix_detector = PrefixDetector(loader)
        result_formatter = ResultFormatter(loader)
        word_matcher = WordMatcher(loader, prefix_detector, result_formatter)
        book_processor = BookProcessor(word_matcher, result_formatter)

        # Process the book from SQLite
        chapters_output = book_processor.process_book_from_sqlite(book_name)

        # Save results
        save_chapter_data(book_name, chapters_output, dry_run)

        # Note: Unmatched words logging is not applicable for SQLite processing
        # since all words have Strong's numbers from the database

        if verbose:
            print(f"Successfully processed {book_name}")
        return True

    except Exception as e:
        logging.error(f"Failed to process book {book_name}: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def process_all_books(dry_run: bool = False, verbose: bool = False) -> int:
    """Process all Delitzsch books from SQLite database"""
    loader = get_sqlite_loader()
    available_books = loader.get_all_books()

    if not available_books:
        print("No books found in SQLite database!")
        return 1

    # Filter to NT books (470-730 range covers all NT books)
    nt_books = [(num, name) for num, name in available_books if 470 <= num <= 730]
    print(f"Found {len(nt_books)} NT books to process")

    if not dry_run:
        ensure_output_dirs()

    success_count = 0
    total_count = len(nt_books)

    for i, (book_number, book_name) in enumerate(nt_books, 1):
        print(f"[{i}/{total_count}] Processing {book_name}...")

        if process_book(book_name, dry_run, verbose):
            success_count += 1
        else:
            print(f"Failed to process {book_name}")

    print(f"\nProcessing complete: {success_count}/{total_count} books successful")
    return 0 if success_count == total_count else 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Delitzsch Strong's Matcher - Match Hebrew words to Strong's numbers"
    )

    parser.add_argument(
        '--book',
        type=str,
        help='Process specific book by name (e.g., acts, matthew, john1)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be done without writing files'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    if args.dry_run:
        print("DRY RUN MODE - No files will be written")

    # Process books
    if args.book:
        # Validate book name exists in SQLite database
        loader = get_sqlite_loader()
        available_books = loader.get_all_books()
        book_names = [name for num, name in available_books]

        if args.book not in book_names:
            print(f"Book '{args.book}' not found. Available books:")
            for name in sorted(book_names):
                print(f"  {name}")
            return 1

        # Create output directory for this book if not dry run
        if not args.dry_run:
            output_book_dir = OUTPUT_DIR / args.book
            output_book_dir.mkdir(parents=True, exist_ok=True)

        success = process_book(args.book, args.dry_run, args.verbose)
        return 0 if success else 1

    else:
        # Process all books
        return process_all_books(args.dry_run, args.verbose)


if __name__ == '__main__':
    sys.exit(main())