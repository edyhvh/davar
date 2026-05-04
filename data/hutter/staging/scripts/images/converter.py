"""
PDF to Image conversion functionality.
"""

import logging
import os
import time
from pathlib import Path
from typing import List, Optional, Set, Tuple

from pdf2image import convert_from_path, pdfinfo_from_path
from tqdm import tqdm

from scripts.images.constants import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_DPI,
    DEFAULT_IMAGE_FORMAT,
    PDF_SOURCE_DIR,
)
from scripts.images.stats import (
    estimate_conversion_time,
    update_performance_stats,
)
from scripts.images.utils import (
    check_pdf_integrity,
    format_time,
    get_converted_pages,
    get_missing_page_ranges,
)

logger = logging.getLogger(__name__)


def convert_pdf_to_images(
    pdf_path: str,
    output_dir: str,
    book_name: str,
    page_range: Optional[Tuple[int, int]] = None,
    image_format: str = DEFAULT_IMAGE_FORMAT,
    dpi: int = DEFAULT_DPI,
    test_mode: bool = False,
    batch_size: int = DEFAULT_BATCH_SIZE,
    force: bool = False,
) -> bool:
    """
    Convert PDF pages to images with batch processing for better performance.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Output directory for images
        book_name: Name of the book (for directory naming)
        page_range: Tuple of (start_page, end_page) or None for all pages
        image_format: Image format ('PNG', 'JPEG', etc.)
        dpi: DPI for image conversion
        test_mode: If True, only convert first 2 pages
        batch_size: Number of pages to process at once
        force: Force re-conversion of existing pages

    Returns:
        True if conversion succeeded, False otherwise
    """
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return False

    # Check PDF integrity before attempting conversion
    if not check_pdf_integrity(pdf_path):
        logger.error(f"PDF file appears to be corrupted or incomplete: {pdf_path}")
        logger.error("This PDF is missing the EOF marker or has an invalid header.")
        logger.error("The file may have been downloaded incompletely.")
        return False

    # Create output directory
    book_dir = os.path.join(output_dir, book_name)
    Path(book_dir).mkdir(parents=True, exist_ok=True)

    try:
        # Determine total pages to process
        expected_pages = _get_expected_pages(pdf_path, page_range, test_mode)

        if test_mode:
            logger.info("Test mode: converting only first 2 pages")

        # Check which pages are already converted
        converted_pages = get_converted_pages(book_dir, expected_pages) if not force else set()
        missing_pages = expected_pages - converted_pages

        if not missing_pages and not force:
            logger.info(f"All {len(expected_pages)} pages for {book_name} are already converted!")
            return True

        total_pages_to_convert = len(missing_pages)
        logger.info(
            f"Converting {pdf_path} to images "
            f"({total_pages_to_convert}/{len(expected_pages)} pages missing at {dpi} DPI)..."
        )

        # Estimate time before starting
        estimated_time, est_pages_per_sec = estimate_conversion_time(
            book_name, total_pages_to_convert, dpi, batch_size
        )
        logger.info(
            f"Estimated time: {format_time(estimated_time)} "
            f"({est_pages_per_sec:.2f} pages/sec)"
        )

        start_time = time.time()

        # Get ranges of missing pages for efficient processing
        missing_ranges = get_missing_page_ranges(expected_pages, converted_pages)

        # Process missing page ranges
        pages_processed = _process_page_ranges(
            pdf_path=pdf_path,
            book_dir=book_dir,
            book_name=book_name,
            missing_ranges=missing_ranges,
            total_pages_to_convert=total_pages_to_convert,
            image_format=image_format,
            dpi=dpi,
            batch_size=batch_size,
            start_time=start_time,
        )

        total_time = time.time() - start_time
        actual_pages_per_sec = pages_processed / total_time if total_time > 0 else 0

        logger.info(
            f"Successfully converted {pages_processed} pages for {book_name} "
            f"in {total_time:.1f}s ({actual_pages_per_sec:.2f} pages/sec)"
        )
        logger.info(
            f"Total converted: {len(expected_pages)} pages "
            f"({len(converted_pages)} already existed)"
        )

        # Update performance statistics
        update_performance_stats(book_name, pages_processed, dpi, batch_size, total_time)

        return True

    except Exception as e:
        logger.error(f"Error converting {pdf_path}: {str(e)}")
        return False


def _get_expected_pages(
    pdf_path: str,
    page_range: Optional[Tuple[int, int]],
    test_mode: bool,
) -> Set[int]:
    """Get the set of expected page numbers to convert."""
    if page_range:
        start_page, end_page = page_range
        expected_pages = set(range(start_page, end_page + 1))
    else:
        info = pdfinfo_from_path(pdf_path)
        total_pages = info["Pages"]
        expected_pages = set(range(1, total_pages + 1))

    if test_mode:
        expected_pages = set(range(1, min(3, max(expected_pages) + 1)))

    return expected_pages


def _process_page_ranges(
    pdf_path: str,
    book_dir: str,
    book_name: str,
    missing_ranges: List[Tuple[int, int]],
    total_pages_to_convert: int,
    image_format: str,
    dpi: int,
    batch_size: int,
    start_time: float,
) -> int:
    """Process missing page ranges and return number of pages processed."""
    pages_processed = 0

    with tqdm(total=total_pages_to_convert, desc=f"Converting {book_name}", unit="pages") as pbar:
        for range_start, range_end in missing_ranges:
            range_pages = list(range(range_start, range_end + 1))

            # Process this range in batches
            for i in range(0, len(range_pages), batch_size):
                batch_start_time = time.time()
                batch_pages = range_pages[i : i + batch_size]

                # Convert batch
                pages = convert_from_path(
                    pdf_path,
                    dpi=dpi,
                    first_page=min(batch_pages),
                    last_page=max(batch_pages),
                    fmt=image_format.lower(),
                )

                # Save batch pages
                for j, page in enumerate(pages):
                    page_num = batch_pages[j]
                    filename = f"{page_num:06d}.png"
                    filepath = os.path.join(book_dir, filename)
                    page.save(filepath, image_format)
                    logger.debug(f"Saved page {page_num}: {filename}")

                batch_count = len(pages)
                pages_processed += batch_count
                pbar.update(batch_count)

                # Update progress bar with ETA
                _update_progress_bar(
                    pbar=pbar,
                    pages_processed=pages_processed,
                    total_pages_to_convert=total_pages_to_convert,
                    batch_count=batch_count,
                    batch_time=time.time() - batch_start_time,
                    elapsed=time.time() - start_time,
                )

    return pages_processed


def _update_progress_bar(
    pbar: tqdm,
    pages_processed: int,
    total_pages_to_convert: int,
    batch_count: int,
    batch_time: float,
    elapsed: float,
) -> None:
    """Update progress bar with ETA information."""
    if pages_processed > 0:
        current_pages_per_sec = batch_count / batch_time if batch_time > 0 else 0
        avg_pages_per_sec = pages_processed / elapsed

        remaining_pages = total_pages_to_convert - pages_processed
        eta_seconds = remaining_pages / avg_pages_per_sec if avg_pages_per_sec > 0 else 0

        pbar.set_postfix(
            {
                "ETA": format_time(eta_seconds),
                "avg pages/sec": f"{avg_pages_per_sec:.2f}",
                "current": f"{current_pages_per_sec:.2f}",
            }
        )


def process_books(
    book_names: List[str],
    output_dir: str,
    page_range: Optional[Tuple[int, int]] = None,
    image_format: str = DEFAULT_IMAGE_FORMAT,
    dpi: int = DEFAULT_DPI,
    test_mode: bool = False,
    batch_size: int = DEFAULT_BATCH_SIZE,
    force: bool = False,
) -> bool:
    """
    Process multiple books for image conversion.

    Args:
        book_names: List of book names to process
        output_dir: Base output directory
        page_range: Page range to convert (None for all pages)
        image_format: Image format
        dpi: DPI for conversion
        test_mode: Test mode (first 2 pages only)
        batch_size: Number of pages to process at once
        force: Force re-conversion

    Returns:
        True if all books converted successfully, False otherwise
    """
    success_count = 0
    corrupted_count = 0
    total_books = len(book_names)

    logger.info(f"Processing {total_books} books...")

    for book_name in book_names:
        pdf_path = os.path.join(PDF_SOURCE_DIR, f"{book_name}.pdf")

        logger.info(f"Processing {book_name}...")

        if convert_pdf_to_images(
            pdf_path=pdf_path,
            output_dir=output_dir,
            book_name=book_name,
            page_range=page_range,
            image_format=image_format,
            dpi=dpi,
            test_mode=test_mode,
            batch_size=batch_size,
            force=force,
        ):
            success_count += 1
        else:
            # Check if it was due to corruption
            if not check_pdf_integrity(pdf_path):
                corrupted_count += 1
                logger.error(f"PDF is corrupted: {book_name}")
            else:
                logger.error(f"Conversion failed for unknown reason: {book_name}")

    logger.info(f"Completed: {success_count}/{total_books} books processed successfully")
    if corrupted_count > 0:
        logger.warning(f"{corrupted_count} PDFs were corrupted and need re-download")
        logger.info("Run: python -m scripts.pdf <book_names> to re-download")

    return success_count == total_books

