#!/usr/bin/env python3
"""
Main entry point for the PDF to Images converter.

Usage:
    python -m scripts.images all                    # Convert all books
    python -m scripts.images matthew                # Convert Matthew only
    python -m scripts.images matthew mark luke      # Convert multiple books
    python -m scripts.images --list                 # List available books
    python -m scripts.images --test matthew         # Convert to data/temp for testing
"""

import logging
import os
import sys

from scripts.images.cli import (
    check_all_pdfs_integrity,
    list_books,
    parse_args,
    validate_books,
)
from scripts.images.constants import TEST_OUTPUT_DIR
from scripts.images.converter import convert_pdf_to_images, process_books
from scripts.images.utils import parse_page_range

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the PDF to Images converter."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle list command
    if args.list:
        list_books()
        return

    # Handle integrity check command
    if args.check_integrity:
        check_all_pdfs_integrity()
        return

    # Determine output directory
    output_dir = args.output
    if args.test:
        output_dir = TEST_OUTPUT_DIR
        logger.info(f"Test mode: converting to {TEST_OUTPUT_DIR}")

    # Parse page range
    page_range = None
    if args.pages:
        try:
            page_range = parse_page_range(args.pages)
            logger.info(f"Converting page range: {args.pages}")
        except ValueError:
            logger.error(f"Invalid page range format: {args.pages}")
            logger.error("Use format like '1-5' or '3'")
            sys.exit(1)

    # Handle custom PDF path
    if args.pdf_path:
        if not os.path.exists(args.pdf_path):
            logger.error(f"PDF file not found: {args.pdf_path}")
            sys.exit(1)

        book_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
        logger.info(f"Processing custom PDF: {args.pdf_path}")

        success = convert_pdf_to_images(
            pdf_path=args.pdf_path,
            output_dir=output_dir,
            book_name=book_name,
            page_range=page_range,
            image_format=args.format,
            dpi=args.dpi,
            test_mode=args.test,
            batch_size=args.batch_size,
            force=args.force,
        )

        if not success:
            sys.exit(1)
        return

    # Validate and get books to process
    book_names = validate_books(args.books)

    # Process books
    success = process_books(
        book_names=book_names,
        output_dir=output_dir,
        page_range=page_range,
        image_format=args.format,
        dpi=args.dpi,
        test_mode=args.test,
        batch_size=args.batch_size,
        force=args.force,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

