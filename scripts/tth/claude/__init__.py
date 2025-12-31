"""
TTH Claude Processor
====================

A clean, accurate processor for TTH (Textual Translation of Hebrew) texts.
"""

from .config import BOOKS_INFO, HEBREW_TERMS, get_book_info, get_available_books
from .processor import TTHProcessor, process_book, TextCleaner

__version__ = '1.0.0'
__all__ = [
    'TTHProcessor',
    'process_book',
    'TextCleaner',
    'BOOKS_INFO',
    'HEBREW_TERMS',
    'get_book_info',
    'get_available_books',
]

