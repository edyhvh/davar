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
DSS_CORPUS_DIR = DATA_DIR / "dss_corpus"  # For ETCBC DSS corpus data
DSS_CORPUS_BIBLICAL = DSS_CORPUS_DIR / "biblical"
DSS_CORPUS_NONBIBLICAL = DSS_CORPUS_DIR / "nonbiblical"

# Output directories
DSS_OUTPUT_DIR = PROJECT_ROOT / "dss"
DSS_BOOKS_DIR = DSS_OUTPUT_DIR / "books"

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
        DSS_OUTPUT_DIR,
        DSS_BOOKS_DIR,
        DSS_CORPUS_DIR,
        DSS_CORPUS_BIBLICAL,
        DSS_CORPUS_NONBIBLICAL
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_book_file_path(book: str) -> Path:
    """Get the file path for a specific book's DSS variants."""
    return DSS_BOOKS_DIR / f"{book}_dss_variants.json"

def get_available_books() -> List[str]:
    """Get list of books that have DSS variant files."""
    if not DSS_BOOKS_DIR.exists():
        return []

    return [f.stem.replace("_dss_variants", "")
            for f in DSS_BOOKS_DIR.glob("*_dss_variants.json")]

# Initialize directories on import
ensure_directories()
