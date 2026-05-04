"""
Command-line interface for the Hutter Polyglot Bible PDF downloader.
"""

import argparse
import sys
from typing import List

from scripts.pdf.constants import (
    BOOK_NAMES,
    DEFAULT_CONNECTIONS_PER_FILE,
    DEFAULT_MAX_CONCURRENT,
    DEFAULT_OUTPUT_DIR,
    TEST_OUTPUT_DIR,
)


def list_books() -> None:
    """Display all available books with their simple names."""
    print("Available books:")
    print("=" * 50)
    for book_name in sorted(BOOK_NAMES.keys()):
        print(f"  {book_name}")
    print("\nUsage examples:")
    print("  python -m scripts.pdf matthew")
    print("  python -m scripts.pdf matthew mark luke john")
    print("  python -m scripts.pdf all")


def validate_books(book_names: List[str]) -> List[str]:
    """
    Validate that requested books exist.

    Args:
        book_names: List of book names to validate

    Returns:
        List of validated book names (lowercase)

    Raises:
        SystemExit: If any book name is invalid
    """
    if not book_names:
        print("Error: No books specified. Use --list to see available books.")
        print("Example: python -m scripts.pdf matthew")
        sys.exit(1)

    invalid_books = []
    valid_books = []

    for book in book_names:
        if book.lower() == "all":
            return list(BOOK_NAMES.keys())
        elif book.lower() in BOOK_NAMES:
            valid_books.append(book.lower())
        else:
            invalid_books.append(book)

    if invalid_books:
        print(f"Error: Unknown books: {', '.join(invalid_books)}")
        print("Use --list to see available books")
        sys.exit(1)

    return valid_books


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Download Hutter Polyglot Bible PDFs using aria2",
        epilog="""
Examples:
  python -m scripts.pdf --list                    # List all books
  python -m scripts.pdf matthew                   # Download Matthew
  python -m scripts.pdf matthew mark luke         # Download multiple books
  python -m scripts.pdf all                       # Download all books
  python -m scripts.pdf --test matthew mark       # Download to data/temp for testing
  python -m scripts.pdf --force matthew           # Force re-download
  python -m scripts.pdf --resume matthew          # Resume incomplete downloads
  python -m scripts.pdf -c 32 -j 10 matthew       # Custom aria2 settings
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "books",
        nargs="*",
        help='Book names to download (or "all" for all books)',
    )

    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help=f"Download to {TEST_OUTPUT_DIR} for testing",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available books",
    )

    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force re-download even if files exist",
    )

    parser.add_argument(
        "--resume", "-r",
        action="store_true",
        help="Resume downloads of existing files (treat as incomplete)",
    )

    parser.add_argument(
        "--connections", "-c",
        type=int,
        default=DEFAULT_CONNECTIONS_PER_FILE,
        help=f"Connections per file (default: {DEFAULT_CONNECTIONS_PER_FILE})",
    )

    parser.add_argument(
        "--concurrent", "-j",
        type=int,
        default=DEFAULT_MAX_CONCURRENT,
        help=f"Concurrent downloads (default: {DEFAULT_MAX_CONCURRENT})",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = create_parser()
    return parser.parse_args()

