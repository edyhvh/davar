"""
PDF to Images Converter Package

This package provides functionality to convert PDF pages to images
for OCR processing using pdf2image library.
"""

from scripts.images.constants import AVAILABLE_BOOKS, DEFAULT_DPI, DEFAULT_OUTPUT_DIR
from scripts.images.converter import convert_pdf_to_images, process_books

__all__ = [
    "AVAILABLE_BOOKS",
    "DEFAULT_DPI",
    "DEFAULT_OUTPUT_DIR",
    "convert_pdf_to_images",
    "process_books",
]

