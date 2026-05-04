"""
Command-line interface for the PDF to Images converter.
"""

import argparse
import sys
from typing import List

from scripts.images.constants import (
    AVAILABLE_BOOKS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_DPI,
    DEFAULT_IMAGE_FORMAT,
    DEFAULT_OUTPUT_DIR,
    PDF_SOURCE_DIR,
    SUPPORTED_FORMATS,
    TEST_OUTPUT_DIR,
)
from scripts.images.utils import check_pdf_integrity


def list_books() -> None:
    """List all available books."""
    print("Available books:")
    print("=" * 50)
    for i, book in enumerate(AVAILABLE_BOOKS, 1):
        print(f"{i:2d}. {book}")
    print("\nUsage examples:")
    print("  python -m scripts.images matthew")
    print("  python -m scripts.images matthew mark luke")
    print("  python -m scripts.images all")
    print("  python -m scripts.images --test matthew")


def check_all_pdfs_integrity() -> None:
    """Check integrity of all PDF files and report results."""
    import os

    print("PDF Integrity Check")
    print("=" * 60)
    print(f"{'Book':<20} {'Status':<15} {'Path'}")
    print("-" * 60)

    corrupted = []
    valid = []
    missing = []

    for book_name in AVAILABLE_BOOKS:
        pdf_path = os.path.join(PDF_SOURCE_DIR, f"{book_name}.pdf")

        if not os.path.exists(pdf_path):
            print(f"{book_name:<20} {'MISSING':<15} {pdf_path}")
            missing.append(book_name)
            continue

        if check_pdf_integrity(pdf_path):
            print(f"{book_name:<20} {'OK':<15} {pdf_path}")
            valid.append(book_name)
        else:
            print(f"{book_name:<20} {'CORRUPTED':<15} {pdf_path}")
            corrupted.append(book_name)

    print("-" * 60)
    print(f"Valid PDFs: {len(valid)}")
    print(f"Missing PDFs: {len(missing)}")
    print(f"Corrupted PDFs: {len(corrupted)}")

    if corrupted:
        print("\nCorrupted PDFs (need re-download):")
        for book in corrupted:
            print(f"  - {book}")
        print("\nTo re-download corrupted PDFs, run:")
        print(f"  python -m scripts.pdf {' '.join(corrupted)}")
    elif not missing:
        print("\nAll PDFs are valid! ✅")


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
        print("Example: python -m scripts.images matthew")
        sys.exit(1)

    invalid_books = []
    valid_books = []

    for book in book_names:
        if book.lower() == "all":
            return AVAILABLE_BOOKS.copy()
        elif book.lower() in AVAILABLE_BOOKS:
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
        description="Convert PDF pages to images using pdf2image",
        epilog="""
Examples:
  python -m scripts.images --list                     # List all books
  python -m scripts.images matthew                    # Convert Matthew
  python -m scripts.images matthew mark luke          # Convert multiple books
  python -m scripts.images all                        # Convert all books
  python -m scripts.images --test matthew             # Test mode (first 2 pages to data/temp)
  python -m scripts.images --pages 1-5 matthew        # Convert pages 1-5
  python -m scripts.images --dpi 150 matthew          # Custom DPI (150-200 for OCR)
  python -m scripts.images --format JPEG matthew      # JPEG format
  python -m scripts.images --batch-size 20 matthew    # Process 20 pages at once
  python -m scripts.images --check-integrity          # Check PDF integrity
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "books",
        nargs="*",
        help='Book names to convert (or "all" for all books)',
    )

    parser.add_argument(
        "--output",
        "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help=f"Test mode: convert first 2 pages to {TEST_OUTPUT_DIR}",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available books",
    )

    parser.add_argument(
        "--check-integrity",
        action="store_true",
        help="Check PDF integrity for all books and report corrupted files",
    )

    parser.add_argument(
        "--pages",
        type=str,
        help='Page range to convert (e.g., "1-5" or "3")',
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=SUPPORTED_FORMATS,
        default=DEFAULT_IMAGE_FORMAT,
        help=f"Image format (default: {DEFAULT_IMAGE_FORMAT})",
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=DEFAULT_DPI,
        help=f"DPI for image conversion (default: {DEFAULT_DPI}, recommended: 150-200 for OCR)",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Number of pages to process at once (default: {DEFAULT_BATCH_SIZE})",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-conversion of all pages (ignore existing images)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--pdf-path",
        type=str,
        help="Path to a specific PDF file to convert",
    )

    return parser


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = create_parser()
    return parser.parse_args()

