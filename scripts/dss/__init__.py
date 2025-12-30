"""
DSS Variants Processing Package

A comprehensive system for processing Dead Sea Scrolls textual variants
for the Davar Bible study application.

This package provides tools for extracting, validating, and managing
textual variants between the Masoretic Text and DSS manuscripts.

Author: Davar Project Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Davar Project Team"
__license__ = "MIT"

# Import main classes for easy access
from .processor import DSSProcessor
from .dss_types import DSSVariant
from .validator import DSSValidator
from .dss_config import DSSConfig, BOOKS_WITH_VARIANTS, get_book_file_path
from .markdown_extractor import DSSMarkdownExtractor
from .etcbc_integrator import ETCBC_DSS_Integrator as ETCBCIntegrator

__all__ = [
    'DSSProcessor',
    'DSSVariant',
    'DSSValidator',
    'DSSConfig',
    'DSSMarkdownExtractor',
    'ETCBCIntegrator',
    'BOOKS_WITH_VARIANTS',
    'get_book_file_path'
]
