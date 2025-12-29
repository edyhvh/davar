"""
DSS Variants Processing Package

This package provides tools for extracting, processing, and validating
Dead Sea Scrolls textual variants for the Davar Bible study app.

Modules:
- dss_config: Configuration and constants
- dss_processor: Main processing logic
- dss_extractor: PDF extraction and parsing
- dss_validator: Data validation and QA
- example_usage: Usage examples and demonstrations

Author: Davar Project Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Davar Project Team"

# Import main classes for easy access
from .dss_types import DSSVariant
from .dss_processor import DSSProcessor
from .dss_extractor import DSSExtractor
from .dss_validator import DSSValidator
from .dss_config import BOOKS_WITH_VARIANTS, get_book_file_path
from .etcbc_dss_integrator import ETCBC_DSS_Integrator, ETCBC_DSS_Config
from .pdf_analyzer import DSSPDFAnalyzer

__all__ = [
    'DSSProcessor',
    'DSSVariant',
    'DSSExtractor',
    'DSSValidator',
    'BOOKS_WITH_VARIANTS',
    'get_book_file_path'
]
