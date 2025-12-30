"""
DSS Utility Functions

Common utility functions and helpers for DSS processing operations.
Includes file operations, text processing, and data manipulation utilities.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from functools import wraps
import time


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger:
    """
    Setup logging configuration for DSS operations.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console: Whether to also log to console

    Returns:
        Configured logger instance
    """
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger('dss')
    logger.setLevel(numeric_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def ensure_directories(*paths: Path) -> None:
    """
    Ensure that all specified directories exist, creating them if necessary.

    Args:
        *paths: Directory paths to ensure exist
    """
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def load_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    path = Path(file_path)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file {path}: {e}")


def save_json_file(
    data: Dict[str, Any],
    file_path: Union[str, Path],
    indent: int = 2,
    ensure_ascii: bool = False
) -> None:
    """
    Save data to a JSON file.

    Args:
        data: Data to save
        file_path: Path where to save the JSON file
        indent: JSON indentation level
        ensure_ascii: Whether to escape non-ASCII characters
    """
    path = Path(file_path)
    ensure_directories(path.parent)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)


def normalize_hebrew_text(text: str) -> str:
    """
    Normalize Hebrew text for consistent processing.

    Args:
        text: Hebrew text to normalize

    Returns:
        Normalized Hebrew text
    """
    if not text:
        return text

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())

    # Normalize Hebrew-specific characters if needed
    # (Add more normalization rules as required)

    return text


def validate_biblical_reference(reference: str) -> Optional[tuple]:
    """
    Validate and parse a biblical reference.

    Args:
        reference: Biblical reference string (e.g., "Genesis 1:1")

    Returns:
        Tuple of (book, chapter, verse) or None if invalid
    """
    # Basic pattern for book chapter:verse
    pattern = r'^([^0-9]+)\s+(\d+):(\d+)$'
    match = re.match(pattern, reference.strip())

    if match:
        book, chapter, verse = match.groups()
        try:
            return book.strip(), int(chapter), int(verse)
        except ValueError:
            pass

    return None


def time_execution(func):
    """
    Decorator to time function execution.

    Args:
        func: Function to time

    Returns:
        Wrapped function that logs execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger('dss')

        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {e}")
            raise

    return wrapper


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Safe filename
    """
    # Replace invalid characters with underscores
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove leading/trailing dots and spaces
    safe_name = safe_name.strip('. ')

    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed"

    return safe_name


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity based on word overlap.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not text1 or not text2:
        return 0.0

    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 and not words2:
        return 1.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def group_variants_by_chapter(variants: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    """
    Group DSS variants by chapter.

    Args:
        variants: List of variant dictionaries

    Returns:
        Dictionary mapping chapter numbers to lists of variants
    """
    grouped = {}

    for variant in variants:
        chapter = variant.get('chapter', 0)
        if chapter not in grouped:
            grouped[chapter] = []
        grouped[chapter].append(variant)

    return grouped


def count_variant_types(variants: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count variants by type.

    Args:
        variants: List of variant dictionaries

    Returns:
        Dictionary mapping variant types to counts
    """
    counts = {}

    for variant in variants:
        variant_type = variant.get('variant_type', 'unknown')
        counts[variant_type] = counts.get(variant_type, 0) + 1

    return counts


def generate_statistics_report(variants: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate comprehensive statistics report for variants.

    Args:
        variants: List of variant dictionaries

    Returns:
        Statistics dictionary
    """
    if not variants:
        return {"total_variants": 0, "message": "No variants to analyze"}

    total_variants = len(variants)
    books = set(v.get('book') for v in variants if v.get('book'))
    chapters = set(v.get('chapter') for v in variants if v.get('chapter'))

    variant_types = count_variant_types(variants)
    significance_levels = {}

    for variant in variants:
        sig = variant.get('significance', 'unknown')
        significance_levels[sig] = significance_levels.get(sig, 0) + 1

    variants_with_comments = sum(1 for v in variants if v.get('comments_en') or v.get('comments_es'))
    variants_with_translations = sum(1 for v in variants if v.get('variant_translation_en') or v.get('variant_translation_es'))

    return {
        "total_variants": total_variants,
        "unique_books": len(books),
        "unique_chapters": len(chapters),
        "variant_types": variant_types,
        "significance_levels": significance_levels,
        "variants_with_comments": variants_with_comments,
        "variants_with_translations": variants_with_translations,
        "comment_coverage": variants_with_comments / total_variants if total_variants > 0 else 0,
        "translation_coverage": variants_with_translations / total_variants if total_variants > 0 else 0,
    }


class ProgressTracker:
    """Simple progress tracking utility."""

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.logger = logging.getLogger('dss')

    def update(self, increment: int = 1) -> None:
        """Update progress by increment."""
        self.current += increment
        self._log_progress()

    def set_current(self, current: int) -> None:
        """Set current progress value."""
        self.current = current
        self._log_progress()

    def _log_progress(self) -> None:
        """Log current progress."""
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            elapsed = time.time() - self.start_time
            rate = self.current / elapsed if elapsed > 0 else 0

            self.logger.info(
                f"{self.description}: {self.current}/{self.total} "
                f"({percentage:.1f}%) - {rate:.1f} items/sec"
            )

    def finish(self) -> None:
        """Mark progress as complete."""
        elapsed = time.time() - self.start_time
        self.logger.info(
            f"{self.description} completed: {self.current} items in {elapsed:.2f} seconds"
        )
