"""
Utility functions for PDF to Images conversion.
"""

import os
from typing import List, Optional, Set, Tuple


def check_pdf_integrity(pdf_path: str) -> bool:
    """
    Check if a PDF file is complete and valid.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        True if PDF appears to be complete, False otherwise
    """
    try:
        with open(pdf_path, "rb") as f:
            # Check header
            f.seek(0)
            header = f.read(20)
            if not header.startswith(b"%PDF-"):
                return False

            # Check EOF marker at the end
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 100))
            end_content = f.read(100)
            if b"%%EOF" not in end_content:
                return False

            return True
    except Exception:
        return False


def get_converted_pages(book_dir: str, expected_pages: Set[int]) -> Set[int]:
    """
    Check which pages are already converted.

    Args:
        book_dir: Directory containing converted images
        expected_pages: Set of expected page numbers

    Returns:
        Set of page numbers that are already converted
    """
    converted_pages = set()

    if not os.path.exists(book_dir):
        return converted_pages

    for filename in os.listdir(book_dir):
        if filename.endswith(".png") and filename[0].isdigit():
            try:
                page_num = int(filename.split(".")[0])
                converted_pages.add(page_num)
            except ValueError:
                continue

    return converted_pages


def get_missing_page_ranges(
    expected_pages: Set[int],
    converted_pages: Set[int],
) -> List[Tuple[int, int]]:
    """
    Get ranges of missing pages for efficient batch processing.

    Args:
        expected_pages: Set of expected page numbers
        converted_pages: Set of already converted page numbers

    Returns:
        List of (start, end) tuples representing missing page ranges
    """
    if not expected_pages:
        return []

    missing_pages = sorted(set(expected_pages) - converted_pages)
    if not missing_pages:
        return []

    # Convert to ranges
    ranges = []
    start = missing_pages[0]
    prev = missing_pages[0]

    for page in missing_pages[1:]:
        if page != prev + 1:
            ranges.append((start, prev))
            start = page
        prev = page

    ranges.append((start, prev))
    return ranges


def parse_page_range(page_range_str: str) -> Optional[Tuple[int, int]]:
    """
    Parse page range string like '1-5' or '3'.

    Args:
        page_range_str: Page range string

    Returns:
        Tuple of (start_page, end_page) or None
    """
    if not page_range_str:
        return None

    if "-" in page_range_str:
        start, end = page_range_str.split("-")
        return int(start), int(end)
    else:
        page = int(page_range_str)
        return page, page


def format_time(seconds: float) -> str:
    """Format seconds into human-readable string."""
    if seconds > 60:
        return f"{seconds/60:.1f}min"
    return f"{seconds:.1f}s"

