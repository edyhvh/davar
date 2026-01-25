#!/usr/bin/env python3
"""
CLI entry point for per-word transliteration.
"""

import argparse
import logging
import sys
from pathlib import Path

from .config import (
    BATCH_TOKEN_BUDGET,
    BESORAH_DIR,
    TANAKH_DIR,
    compute_cost,
)
from .local_processor import estimate_book_cost as estimate_book_cost_local
from .local_processor import transliterate_book_local

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


TANAKH_BOOKS = [
    "genesis", "exodus", "leviticus", "numbers", "deuteronomy",
    "joshua", "judges", "ruth", "isamuel", "iisamuel", "ikings", "iikings",
    "ichronicles", "iichronicles", "ezra", "nehemiah", "esther",
    "job", "psalms", "proverbs", "ecclesiastes", "songofsolomon",
    "isaiah", "jeremiah", "lamentations", "ezekiel", "daniel",
    "hosea", "joel", "amos", "obadiah", "jonah", "micah",
    "nahum", "habakkuk", "zephaniah", "haggai", "zechariah", "malachi",
]

BESORAH_BOOKS = [
    "matthew", "mark", "luke", "john", "acts",
    "romans", "corinthians1", "corinthians2", "galatians", "ephesians",
    "philippians", "colossians", "thessalonians1", "thessalonians2",
    "timothy1", "timothy2", "titus", "philemon",
    "hebrews", "james", "peter1", "peter2",
    "john1", "john2", "john3", "jude", "revelation",
]


def get_available_books(corpus: str) -> list:
    """Return list of available book directories for a corpus."""
    source_dir = TANAKH_DIR if corpus == "tanakh" else BESORAH_DIR
    return sorted([p.name for p in source_dir.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name != "raw"])


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate per-word transliterations using local rules",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--corpus",
        choices=["tanakh", "besorah"],
        required=True,
        help="Corpus to process"
    )
    parser.add_argument(
        "--book",
        default="all",
        help="Book id (directory name, e.g., genesis, john) or 'all' for entire corpus"
    )
    parser.add_argument(
        "--list-books",
        action="store_true",
        help="List available books for the corpus and exit"
    )
    parser.add_argument(
        "--token-budget",
        type=int,
        default=BATCH_TOKEN_BUDGET,
        help=f"Approx token budget per batch (default: {BATCH_TOKEN_BUDGET})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without writing output files"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # List books and exit if requested
    if args.list_books:
        books = get_available_books(args.corpus)
        print(f"Available books in {args.corpus} ({len(books)} total):")
        for book in books:
            print(f"  {book}")
        sys.exit(0)

    # Determine books to process
    if args.book == "all":
        books_to_process = get_available_books(args.corpus)
    else:
        books_to_process = [args.book]

    total_books = len(books_to_process)
    total_words = 0
    total_batches = 0
    total_input_tokens = 0
    total_output_tokens = 0
    failed_books = []

    logger.info("="*60)
    logger.info("Starting transliteration for %s (%s books)", args.corpus.upper(), total_books)
    logger.info("Token budget per batch: %s", args.token_budget)
    logger.info("Dry run: %s", args.dry_run)
    logger.info("="*60)

    for book_index, book_id in enumerate(books_to_process, start=1):
        logger.info("")
        logger.info("-"*60)
        logger.info("[%s/%s] Starting book: %s", book_index, total_books, book_id)
        logger.info("-"*60)

        try:
            stats = transliterate_book_local(
                book_id=book_id,
                corpus=args.corpus,
                token_budget=args.token_budget,
                dry_run=args.dry_run,
            )
            cost = estimate_book_cost_local(stats)

            total_words += stats.words
            total_batches += stats.batches
            total_input_tokens += stats.input_tokens
            total_output_tokens += stats.output_tokens

            logger.info("")
            logger.info(
                "[%s/%s] Book %s COMPLETED: %s words, %s batches, cost=$%.4f",
                book_index,
                total_books,
                stats.book_id,
                stats.words,
                stats.batches,
                cost,
            )

        except Exception as e:
            logger.error("[%s/%s] Book %s FAILED: %s", book_index, total_books, book_id, e)
            failed_books.append(book_id)
            continue

    # Final summary
    total_cost = compute_cost(total_input_tokens, total_output_tokens)

    logger.info("")
    logger.info("="*60)
    logger.info("TRANSLITERATION COMPLETE")
    logger.info("="*60)
    logger.info("Corpus: %s", args.corpus)
    logger.info("Books processed: %s/%s", total_books - len(failed_books), total_books)
    logger.info("Total words: %s", total_words)
    logger.info("Total batches: %s", total_batches)
    logger.info("Total input tokens: %s", total_input_tokens)
    logger.info("Total output tokens: %s", total_output_tokens)
    logger.info("Total estimated cost: $%.4f", total_cost)

    if failed_books:
        logger.warning("Failed books: %s", ", ".join(failed_books))

    if args.dry_run:
        logger.info("")
        logger.info("DRY RUN - No files were written")

    logger.info("="*60)

    if failed_books:
        sys.exit(1)


if __name__ == "__main__":
    main()
