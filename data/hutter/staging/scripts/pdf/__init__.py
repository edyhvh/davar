"""
PDF Downloader Package for Hutter Polyglot Bible

This package provides functionality to download PDF files from the
Hutter Polyglot Bible archive using aria2 for optimal performance.
"""

from scripts.pdf.constants import BOOK_NAMES, OUTPUT_NAMES
from scripts.pdf.downloader import download_books, is_aria2_available

__all__ = [
    "BOOK_NAMES",
    "OUTPUT_NAMES",
    "download_books",
    "is_aria2_available",
]

