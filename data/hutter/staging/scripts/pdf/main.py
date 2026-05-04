#!/usr/bin/env python3
"""
Main entry point for the Hutter Polyglot Bible PDF downloader.

Usage:
    python -m scripts.pdf all                       # Download all books
    python -m scripts.pdf matthew                   # Download Matthew only
    python -m scripts.pdf matthew mark luke         # Download multiple books
    python -m scripts.pdf --list                    # List available books
    python -m scripts.pdf --test matthew            # Download to data/temp for testing
"""

import logging
import sys

from scripts.pdf.cli import list_books, parse_args, validate_books
from scripts.pdf.constants import TEST_OUTPUT_DIR
from scripts.pdf.downloader import download_books

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the PDF downloader."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle list command
    if args.list:
        list_books()
        return

    # Handle test mode
    output_dir = args.output
    if args.test:
        output_dir = TEST_OUTPUT_DIR
        logger.info(f"Test mode: downloading to {TEST_OUTPUT_DIR}")

    # Validate and get books to download
    book_names = validate_books(args.books)

    # Download books
    success = download_books(
        book_names=book_names,
        output_dir=output_dir,
        force_redownload=args.force,
        resume_existing=args.resume,
        connections_per_file=args.connections,
        max_concurrent=args.concurrent,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

