#!/usr/bin/env python3
"""
Dead Sea Scrolls differences parser package
"""

from .config import BOOK_NAMES, NOTES_FILE, OUTPUT_DIR
from .notes_parser import parse_notes_file, extract_masoretic_dss_words
from .xml_parsers import parse_dss_book, parse_wlc_book
from .book_processor import BookProcessor
from .output_writer import OutputWriter

__all__ = [
    'BOOK_NAMES',
    'NOTES_FILE',
    'OUTPUT_DIR',
    'parse_notes_file',
    'extract_masoretic_dss_words',
    'parse_dss_book',
    'parse_wlc_book',
    'BookProcessor',
    'OutputWriter',
]
