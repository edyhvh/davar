"""
DSS (Dead Sea Scrolls) Configuration Module

This module contains configuration settings and constants for DSS variant processing.
"""

import os
from pathlib import Path
from typing import Dict, List, Set

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DSS_DATA_DIR = DATA_DIR / "dss"
SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "dss"

# DSS Corpus paths (if available)
DSS_CORPUS_DIR = DATA_DIR / "dss" / "raw" / "dss_corpus"  # Updated path
DSS_CORPUS_BIBLICAL = DSS_CORPUS_DIR / "biblical"
DSS_CORPUS_NONBIBLICAL = DSS_CORPUS_DIR / "nonbiblical"

# Output directories - JSON files go directly to data/dss/
DSS_OUTPUT_DIR = DATA_DIR / "dss"
DSS_BOOKS_DIR = DSS_OUTPUT_DIR  # No subfolder, files go directly here

# Books with DSS variants (initial set)
BOOKS_WITH_VARIANTS: Set[str] = {
    "isaiah",
    "samuel_1",
    "samuel_2"
}

# Book mapping (DSS naming convention to standard)
BOOK_MAPPINGS: Dict[str, str] = {
    "isaiah": "Isaiah",
    "samuel_1": "1_Samuel",
    "samuel_2": "2_Samuel"
}

# DSS variant data structure
DSS_VARIANT_SCHEMA = {
    "book": str,
    "chapter": int,
    "verse": int,
    "masoretic_text": str,  # MT text
    "dss_text": str,        # DSS text
    "variant_translation_en": str,  # English translation of the variation
    "variant_translation_es": str,  # Spanish translation of the variation
    "comments_he": str,     # Comments in Hebrew
    "comments_en": str,     # Comments in English
    "comments_es": str,     # Comments in Spanish (original)
    "dss_source": str,      # DSS manuscript reference
    "variant_type": str,    # Type of variant (addition, omission, substitution, etc.)
    "significance": str     # Scholarly significance level
}

# Text-Fabric DSS corpus configuration (if using ETCBC data)
TF_DSS_CONFIG = {
    "features": [
        "otype",      # Node types
        "sign",       # Individual signs/characters
        "word",       # Words
        "line",       # Lines
        "fragment",   # Fragments
        "scroll",     # Scrolls
        "book",       # Biblical books
        "chapter",    # Chapters
        "verse",      # Verses
        "glyph",      # Transcription
        "glyphs",     # Alternative transcription
        "lex",        # Lexeme
        "lexemes",    # Alternative lexeme
        "biblical"    # Biblical vs non-biblical flag
    ],
    "text_formats": [
        "text-orig-full",    # Original transcription
        "text-trans-full",   # ETCBC transcription
        "lex-orig-full",     # Lexeme in Hebrew
        "lex-trans-full"     # Lexeme in ETCBC
    ]
}

# ETCBC DSS Integration settings
ETCBC_DSS_CONFIG = {
    "enabled": True,
    "auto_enhance_variants": True,
    "cross_reference_mt": True,
    "download_on_demand": True,
    "cache_results": True
}

# Processing options
PROCESSING_CONFIG = {
    "extract_comments_from_pdf": True,
    "validate_verse_references": True,
    "cross_reference_with_mt": True,
    "generate_diff_analysis": True,
    "export_formats": ["json", "csv", "markdown"]
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": SCRIPTS_DIR / "dss_processor.log"
}

def ensure_directories() -> None:
    """Ensure all necessary directories exist."""
    directories = [
        DSS_OUTPUT_DIR,  # Main DSS output directory
        # DSS_CORPUS_* directories should already exist
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_book_file_path(book: str) -> Path:
    """Get the file path for a specific book's DSS variants."""
    return DSS_OUTPUT_DIR / f"{book}_dss.json"

def get_available_books() -> List[str]:
    """Get list of books that have DSS variant files."""
    if not DSS_OUTPUT_DIR.exists():
        return []

    return [f.stem.replace("_dss", "")
            for f in DSS_OUTPUT_DIR.glob("*_dss.json")]

# Create config instance for compatibility
class DSSConfig:
    """Configuration class for DSS processing."""

    def __init__(self):
        self.paths = self._create_paths()
        self.etcbc = self._create_etcbc_config()

    def _create_paths(self):
        class Paths:
            project_root = PROJECT_ROOT
            data_dir = DATA_DIR
            dss_data_dir = DSS_DATA_DIR
            scripts_dir = SCRIPTS_DIR
            corpus_dir = DSS_CORPUS_DIR
            corpus_biblical = DSS_CORPUS_BIBLICAL
            corpus_nonbiblical = DSS_CORPUS_NONBIBLICAL
            output_dir = DSS_OUTPUT_DIR

        return Paths()

    def _create_etcbc_config(self):
        class ETCBC:
            enabled = ETCBC_DSS_CONFIG["enabled"]
            auto_enhance_variants = ETCBC_DSS_CONFIG["auto_enhance_variants"]
            cross_reference_mt = ETCBC_DSS_CONFIG["cross_reference_mt"]
            download_on_demand = ETCBC_DSS_CONFIG["download_on_demand"]
            cache_results = ETCBC_DSS_CONFIG["cache_results"]

        return ETCBC()

# Create global config instance
config = DSSConfig()

# Initialize directories on import
ensure_directories()
