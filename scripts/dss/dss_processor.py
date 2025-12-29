#!/usr/bin/env python3
"""
DSS Variants Processor

Main processor for Dead Sea Scrolls textual variants extraction and management.
Handles the processing of DSS manuscripts, comparison with Masoretic Text,
and generation of structured variant data.

Author: Davar Project Team
License: MIT
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dss_config import (
    DSS_VARIANT_SCHEMA,
    BOOKS_WITH_VARIANTS,
    get_book_file_path,
    LOGGING_CONFIG,
    PROCESSING_CONFIG,
    ETCBC_DSS_CONFIG
)
from dss_types import DSSVariant
from etcbc_dss_integrator import ETCBC_DSS_Integrator, ETCBC_DSS_Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG["file"]),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# DSSVariant is now imported from dss_types

class DSSProcessor:
    """Main processor for DSS variants."""

    def __init__(self):
        self.variants: Dict[str, List[DSSVariant]] = {}
        self.etcbc_integrator = None
        self._load_existing_data()
        self._initialize_etcbc_integration()

    def _initialize_etcbc_integration(self) -> None:
        """Initialize ETCBC DSS integration if enabled."""
        if ETCBC_DSS_CONFIG.get("enabled", False):
            try:
                self.etcbc_integrator = ETCBC_DSS_Integrator()
                logger.info("ETCBC DSS integration initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize ETCBC DSS integration: {e}")
                self.etcbc_integrator = None
        else:
            logger.info("ETCBC DSS integration disabled")

    def _load_existing_data(self) -> None:
        """Load existing DSS variant data from JSON files."""
        for book in BOOKS_WITH_VARIANTS:
            file_path = get_book_file_path(book)
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.variants[book] = [
                            DSSVariant.from_dict(variant) for variant in data.get('variants', [])
                        ]
                    logger.info(f"Loaded {len(self.variants[book])} variants for {book}")
                except Exception as e:
                    logger.error(f"Error loading {book} data: {e}")
                    self.variants[book] = []
            else:
                self.variants[book] = []
                logger.info(f"Initialized empty variant list for {book}")

    def add_variant(self, variant: DSSVariant, enhance_with_etcbc: bool = None) -> bool:
        """Add a new variant to the collection."""
        errors = variant.validate()
        if errors:
            logger.error(f"Validation errors for variant {variant.book} {variant.chapter}:{variant.verse}: {errors}")
            return False

        if variant.book not in self.variants:
            self.variants[variant.book] = []

        # Check for duplicates
        for existing in self.variants[variant.book]:
            if (existing.chapter == variant.chapter and
                existing.verse == variant.verse and
                existing.dss_text == variant.dss_text):
                logger.warning(f"Duplicate variant found for {variant.book} {variant.chapter}:{variant.verse}")
                return False

        # Enhance with ETCBC data if available and enabled
        if enhance_with_etcbc is None:
            enhance_with_etcbc = ETCBC_DSS_CONFIG.get("auto_enhance_variants", True)

        if enhance_with_etcbc and self.etcbc_integrator and not variant.dss_text.strip():
            try:
                enhanced_variant = self.etcbc_integrator.enhance_variant_data(variant)
                if enhanced_variant.dss_text and enhanced_variant.dss_text != variant.dss_text:
                    logger.info(f"Enhanced variant {variant.book} {variant.chapter}:{variant.verse} with ETCBC data")
                    variant = enhanced_variant
            except Exception as e:
                logger.warning(f"Failed to enhance variant with ETCBC data: {e}")

        self.variants[variant.book].append(variant)
        logger.info(f"Added variant for {variant.book} {variant.chapter}:{variant.verse}")
        return True

    def get_variants(self, book: str, chapter: Optional[int] = None,
                    verse: Optional[int] = None) -> List[DSSVariant]:
        """Get variants for a specific book/chapter/verse."""
        if book not in self.variants:
            return []

        variants = self.variants[book]

        if chapter is not None:
            variants = [v for v in variants if v.chapter == chapter]

        if verse is not None:
            variants = [v for v in variants if v.verse == verse]

        return variants

    def save_data(self) -> None:
        """Save all variant data to JSON files."""
        for book, variants in self.variants.items():
            file_path = get_book_file_path(book)
            data = {
                "metadata": {
                    "book": book,
                    "total_variants": len(variants),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "variants": [variant.to_dict() for variant in variants]
            }

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved {len(variants)} variants for {book}")
            except Exception as e:
                logger.error(f"Error saving {book} data: {e}")

    def validate_all_data(self) -> Dict[str, List[str]]:
        """Validate all variant data and return errors by book."""
        errors = {}
        for book, variants in self.variants.items():
            book_errors = []
            for i, variant in enumerate(variants):
                variant_errors = variant.validate()
                if variant_errors:
                    book_errors.extend([f"Variant {i+1}: {error}" for error in variant_errors])
            if book_errors:
                errors[book] = book_errors
        return errors

    def generate_statistics(self) -> Dict[str, Any]:
        """Generate statistics about the DSS variants."""
        stats = {
            "total_books": len(self.variants),
            "total_variants": sum(len(variants) for variants in self.variants.values()),
            "books_breakdown": {},
            "etcbc_integration": {
                "enabled": self.etcbc_integrator is not None,
                "corpus_loaded": self.etcbc_integrator.corpus_loaded if self.etcbc_integrator else False
            }
        }

        for book, variants in self.variants.items():
            stats["books_breakdown"][book] = {
                "total_variants": len(variants),
                "chapters_covered": len(set(v.chapter for v in variants)),
                "verses_covered": len(set((v.chapter, v.verse) for v in variants)),
                "variant_types": {},
                "significance_levels": {}
            }

            # Count variant types and significance
            for variant in variants:
                vtype = variant.variant_type or "unknown"
                sig = variant.significance or "unknown"
                stats["books_breakdown"][book]["variant_types"][vtype] = \
                    stats["books_breakdown"][book]["variant_types"].get(vtype, 0) + 1
                stats["books_breakdown"][book]["significance_levels"][sig] = \
                    stats["books_breakdown"][book]["significance_levels"].get(sig, 0) + 1

        return stats

    def cross_validate_with_mt(self, book: str = None) -> Dict[str, Any]:
        """Cross-validate DSS variants with Masoretic Text using ETCBC."""
        if not self.etcbc_integrator:
            return {"error": "ETCBC DSS integration not available"}

        results = {
            "total_validated": 0,
            "matches_found": 0,
            "differences_found": 0,
            "enhancements_made": 0,
            "details": []
        }

        books_to_check = [book] if book else list(self.variants.keys())

        for book_name in books_to_check:
            if book_name not in self.variants:
                continue

            logger.info(f"Cross-validating {book_name} with ETCBC DSS corpus")

            for variant in self.variants[book_name]:
                results["total_validated"] += 1

                # Get corpus data for this verse
                corpus_data = self.etcbc_integrator.get_text(
                    variant.book, variant.chapter, variant.verse,
                    ["glyphs", "lexemes"]
                )

                corpus_text = corpus_data.get("glyphs", "")

                detail = {
                    "book": variant.book,
                    "chapter": variant.chapter,
                    "verse": variant.verse,
                    "our_mt_text": variant.masoretic_text,
                    "our_dss_text": variant.dss_text,
                    "corpus_dss_text": corpus_text,
                    "mt_match": False,
                    "dss_match": False,
                    "enhanced": False
                }

                # Check if corpus has data for this verse
                if corpus_text:
                    results["matches_found"] += 1

                    # Compare DSS texts
                    if variant.dss_text and corpus_text:
                        similarity = self.etcbc_integrator._calculate_similarity(variant.dss_text, corpus_text)
                        detail["dss_similarity"] = similarity
                        detail["dss_match"] = similarity > 0.8  # 80% similarity threshold

                    # If we don't have DSS text but corpus does, enhance
                    if not variant.dss_text.strip() and corpus_text:
                        variant.dss_text = corpus_text
                        detail["enhanced"] = True
                        results["enhancements_made"] += 1

                results["details"].append(detail)

        # Save updated data if enhancements were made
        if results["enhancements_made"] > 0:
            self.save_data()
            logger.info(f"Saved {results['enhancements_made']} enhanced variants")

        return results

    def get_etcbc_statistics(self) -> Dict[str, Any]:
        """Get ETCBC DSS corpus statistics."""
        if not self.etcbc_integrator:
            return {"error": "ETCBC DSS integration not available"}

        return self.etcbc_integrator.get_statistics()

    def export_to_csv(self, output_path: Path) -> None:
        """Export all variants to CSV format."""
        import csv

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['book', 'chapter', 'verse', 'masoretic_text', 'dss_text',
                         'variant_translation_en', 'variant_translation_es',
                         'comments_he', 'comments_en', 'comments_es',
                         'dss_source', 'variant_type', 'significance']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for book_variants in self.variants.values():
                for variant in book_variants:
                    writer.writerow(variant.to_dict())

        logger.info(f"Exported data to {output_path}")

def main():
    """Main entry point for DSS processing."""
    processor = DSSProcessor()

    # Validate data
    errors = processor.validate_all_data()
    if errors:
        logger.error("Validation errors found:")
        for book, book_errors in errors.items():
            logger.error(f"{book}:")
            for error in book_errors:
                logger.error(f"  - {error}")
        return 1

    # Generate and log statistics
    stats = processor.generate_statistics()
    logger.info("DSS Variants Statistics:")
    logger.info(f"Total books: {stats['total_books']}")
    logger.info(f"Total variants: {stats['total_variants']}")

    for book, book_stats in stats['books_breakdown'].items():
        logger.info(f"{book}: {book_stats['total_variants']} variants")

    # Save data
    processor.save_data()

    # Export to CSV if requested
    if PROCESSING_CONFIG.get("export_formats", []).count("csv"):
        csv_path = Path(__file__).parent / "dss_variants_export.csv"
        processor.export_to_csv(csv_path)

    logger.info("DSS processing completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
