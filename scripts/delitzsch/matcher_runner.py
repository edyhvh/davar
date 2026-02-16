#!/usr/bin/env python3
"""Core run logic for Delitzsch matcher processing."""

from __future__ import annotations

import json
import logging
from typing import List

from .book_processor import BookProcessor
from .config import OUTPUT_DIR, UNMATCHED_WORDS_LOG, ensure_output_dirs
from .dictionary_loader import get_dictionary_loader
from .prefix_detector import PrefixDetector
from .result_formatter import ResultFormatter
from .sqlite_loader import get_sqlite_loader
from .word_matcher import WordMatcher


def setup_logging(verbose: bool = False):
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def save_chapter_data(book_name: str, chapter_data: List[dict], dry_run: bool = False):
    book_dir = OUTPUT_DIR / book_name

    for chapter in chapter_data:
        chapter_num = chapter["chapter"]
        output_file = book_dir / f"{chapter_num}.json"

        if dry_run:
            print(f"Would save: {output_file}")
            continue

        try:
            with open(output_file, "w", encoding="utf-8") as handle:
                json.dump([chapter], handle, ensure_ascii=False, indent=2)
            print(f"Saved: {output_file}")
        except Exception as error:
            logging.error(f"Failed to save {output_file}: {error}")


def log_unmatched_words(word_matcher: WordMatcher):
    unmatched = word_matcher.get_unmatched_words()
    if not unmatched:
        return

    try:
        with open(UNMATCHED_WORDS_LOG, "w", encoding="utf-8") as handle:
            handle.write("Unmatched words log\n")
            handle.write("=" * 50 + "\n\n")
            for item in unmatched:
                handle.write(f"Word: {item['word']}\n")
                handle.write(f"Stem: {item['stem']}\n")
                handle.write(f"Reason: {item['reason']}\n")
                handle.write("-" * 30 + "\n")

        print(f"Unmatched words logged to: {UNMATCHED_WORDS_LOG}")
    except Exception as error:
        logging.error(f"Failed to write unmatched words log: {error}")


def process_book(book_name: str, dry_run: bool = False, verbose: bool = False) -> bool:
    if verbose:
        print(f"Processing book: {book_name}")

    try:
        loader = get_dictionary_loader()
        prefix_detector = PrefixDetector(loader)
        result_formatter = ResultFormatter(loader)
        word_matcher = WordMatcher(loader, prefix_detector, result_formatter)
        book_processor = BookProcessor(word_matcher, result_formatter)

        chapters_output = book_processor.process_book_from_sqlite(book_name)
        save_chapter_data(book_name, chapters_output, dry_run)

        if verbose:
            print(f"Successfully processed {book_name}")
        return True

    except Exception as error:
        logging.error(f"Failed to process book {book_name}: {error}")
        if verbose:
            import traceback

            traceback.print_exc()
        return False


def process_all_books(dry_run: bool = False, verbose: bool = False) -> int:
    loader = get_sqlite_loader()
    available_books = loader.get_all_books()

    if not available_books:
        print("No books found in SQLite database!")
        return 1

    nt_books = [(num, name)
                for num, name in available_books if 470 <= num <= 730]
    print(f"Found {len(nt_books)} NT books to process")

    if not dry_run:
        ensure_output_dirs()

    success_count = 0
    total_count = len(nt_books)

    for index, (_, book_name) in enumerate(nt_books, 1):
        print(f"[{index}/{total_count}] Processing {book_name}...")

        if process_book(book_name, dry_run, verbose):
            success_count += 1
        else:
            print(f"Failed to process {book_name}")

    print(
        f"\nProcessing complete: {success_count}/{total_count} books successful")
    return 0 if success_count == total_count else 1
