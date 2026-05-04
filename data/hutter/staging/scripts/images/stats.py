"""
Performance statistics tracking for PDF conversion.
"""

import json
import logging
import os
import time
from typing import Dict, Optional, Tuple

from scripts.images.constants import PERF_STATS_FILE

logger = logging.getLogger(__name__)


def load_performance_stats() -> Dict:
    """Load performance statistics from file."""
    if os.path.exists(PERF_STATS_FILE):
        try:
            with open(PERF_STATS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_performance_stats(stats: Dict) -> None:
    """Save performance statistics to file."""
    os.makedirs(os.path.dirname(PERF_STATS_FILE), exist_ok=True)
    try:
        with open(PERF_STATS_FILE, "w") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save performance stats: {e}")


def estimate_conversion_time(
    book_name: str,
    total_pages: int,
    dpi: int = 300,
    batch_size: int = 10,
) -> Tuple[float, float]:
    """
    Estimate conversion time based on previous runs.

    Args:
        book_name: Name of the book
        total_pages: Total pages to convert
        dpi: DPI setting
        batch_size: Batch size setting

    Returns:
        Tuple of (estimated_seconds, pages_per_second)
    """
    stats = load_performance_stats()

    key = f"{book_name}_{dpi}_{batch_size}"
    if key in stats:
        pages_per_sec = stats[key].get("pages_per_sec", 1.0)
        estimated_seconds = total_pages / pages_per_sec
        return estimated_seconds, pages_per_sec

    # Fallback estimates based on DPI
    if dpi >= 300:
        pages_per_sec = 0.8  # Conservative estimate for high DPI
    elif dpi >= 200:
        pages_per_sec = 1.5
    else:
        pages_per_sec = 2.5  # Faster for lower DPI

    estimated_seconds = total_pages / pages_per_sec
    return estimated_seconds, pages_per_sec


def update_performance_stats(
    book_name: str,
    total_pages: int,
    dpi: int,
    batch_size: int,
    actual_time: float,
) -> None:
    """
    Update performance statistics after conversion.

    Args:
        book_name: Name of the book
        total_pages: Total pages converted
        dpi: DPI setting used
        batch_size: Batch size used
        actual_time: Actual time taken in seconds
    """
    stats = load_performance_stats()
    key = f"{book_name}_{dpi}_{batch_size}"

    pages_per_sec = total_pages / actual_time if actual_time > 0 else 1.0

    stats[key] = {
        "pages_per_sec": pages_per_sec,
        "total_pages": total_pages,
        "dpi": dpi,
        "batch_size": batch_size,
        "last_updated": time.time(),
    }

    save_performance_stats(stats)

