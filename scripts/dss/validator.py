#!/usr/bin/env python3
"""
DSS Variants Validator

Validates DSS variant data for consistency, completeness, and correctness.
Performs cross-references with Masoretic Text and checks data integrity.

Author: Davar Project Team
License: MIT
"""

import json
import logging
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
import difflib
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dss_config import (
    BOOKS_WITH_VARIANTS,
    get_book_file_path
)
from dss_types import DSSVariant
from dss_types import DSSVariant

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DSSValidator:
    """Validator for DSS variant data."""

    def __init__(self):
        self.errors: Dict[str, List[str]] = defaultdict(list)
        self.warnings: Dict[str, List[str]] = defaultdict(list)
        self.stats: Dict[str, Any] = {}

        # Load reference data if available
        self.mt_data: Dict[str, Dict[Tuple[int, int], str]] = {}
        self._load_mt_reference_data()

    def _load_mt_reference_data(self) -> None:
        """Load Masoretic Text reference data for validation."""
        # This would load actual MT data from the project
        # For now, we'll use placeholder logic
        mt_data_path = Path(__file__).parent.parent / "data" / "ts2009"

        if mt_data_path.exists():
            logger.info("MT reference data directory found")
            # TODO: Implement MT data loading
        else:
            logger.warning("MT reference data not found - some validations will be skipped")

    def validate_all_books(self) -> bool:
        """Validate all DSS variant books."""
        all_valid = True

        for book in BOOKS_WITH_VARIANTS:
            if not self.validate_book(book):
                all_valid = False

        self._generate_validation_report()
        return all_valid

    def validate_book(self, book: str) -> bool:
        """Validate a specific book's DSS variants."""
        file_path = get_book_file_path(book)
        if not file_path.exists():
            self.errors[book].append(f"Variant file not found: {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors[book].append(f"Invalid JSON format: {e}")
            return False

        variants = data.get('variants', [])
        if not variants:
            self.warnings[book].append("No variants found in file")
            return True

        logger.info(f"Validating {len(variants)} variants for {book}")

        # Validate each variant
        for i, variant_data in enumerate(variants):
            self._validate_variant(book, i + 1, variant_data)

        # Cross-validation between variants
        self._validate_cross_references(book, variants)

        # Generate book statistics
        self._generate_book_stats(book, variants)

        has_errors = len(self.errors[book]) > 0
        return not has_errors

    def _validate_variant(self, book: str, index: int, variant_data: Dict[str, Any]) -> None:
        """Validate a single variant."""
        variant_id = f"{book}:{index}"

        # Required fields validation
        required_fields = ['book', 'chapter', 'verse', 'masoretic_text', 'dss_text']
        for field in required_fields:
            if field not in variant_data or not variant_data[field]:
                self.errors[book].append(f"Variant {index}: Missing or empty required field '{field}'")

        # Data type validation
        if 'chapter' in variant_data:
            if not isinstance(variant_data['chapter'], int) or variant_data['chapter'] < 1:
                self.errors[book].append(f"Variant {index}: Chapter must be a positive integer")

        if 'verse' in variant_data:
            if not isinstance(variant_data['verse'], int) or variant_data['verse'] < 1:
                self.errors[book].append(f"Variant {index}: Verse must be a positive integer")

        # Text validation
        if 'masoretic_text' in variant_data and variant_data['masoretic_text']:
            self._validate_hebrew_text(book, index, variant_data['masoretic_text'], 'masoretic_text')

        if 'dss_text' in variant_data and variant_data['dss_text']:
            self._validate_hebrew_text(book, index, variant_data['dss_text'], 'dss_text')

        # Cross-reference with MT if available
        if 'chapter' in variant_data and 'verse' in variant_data:
            self._validate_mt_reference(book, index, variant_data)

        # Variant type validation
        if 'variant_type' in variant_data:
            valid_types = ['addition', 'omission', 'substitution', 'transposition', 'spelling', 'unknown']
            if variant_data['variant_type'] not in valid_types:
                self.warnings[book].append(f"Variant {index}: Unknown variant type '{variant_data['variant_type']}'")

        # Significance validation
        if 'significance' in variant_data:
            valid_significance = ['high', 'medium', 'low']
            if variant_data['significance'] not in valid_significance:
                self.warnings[book].append(f"Variant {index}: Invalid significance level '{variant_data['significance']}'")

    def _validate_hebrew_text(self, book: str, index: int, text: str, field_name: str) -> None:
        """Validate Hebrew text content."""
        if not text.strip():
            return

        # Check for basic Hebrew characters
        hebrew_chars = re.findall(r'[\u0590-\u05FF\u200f\u200e]', text)
        if len(hebrew_chars) == 0:
            self.warnings[book].append(f"Variant {index}: {field_name} contains no Hebrew characters")

        # Check for suspicious characters
        suspicious_chars = re.findall(r'[a-zA-Z]{3,}', text)  # Latin words in Hebrew text
        if suspicious_chars:
            self.warnings[book].append(f"Variant {index}: {field_name} contains Latin words: {suspicious_chars}")

        # Check text length
        if len(text.strip()) < 2:
            self.warnings[book].append(f"Variant {index}: {field_name} is very short")

    def _validate_mt_reference(self, book: str, index: int, variant_data: Dict[str, Any]) -> None:
        """Validate variant against Masoretic Text reference."""
        chapter = variant_data.get('chapter')
        verse = variant_data.get('verse')
        mt_text = variant_data.get('masoretic_text', '').strip()

        if not all([chapter, verse, mt_text]):
            return

        # Check if we have MT reference data
        if book in self.mt_data and (chapter, verse) in self.mt_data[book]:
            reference_mt = self.mt_data[book][(chapter, verse)]

            # Simple text similarity check
            similarity = difflib.SequenceMatcher(None, mt_text, reference_mt).ratio()
            if similarity < 0.8:  # Less than 80% similarity
                self.warnings[book].append(
                    f"Variant {index}: MT text differs significantly from reference "
                    f"(similarity: {similarity:.2f})"
                )
        else:
            self.warnings[book].append(f"Variant {index}: No MT reference data available for validation")

    def _validate_cross_references(self, book: str, variants: List[Dict[str, Any]]) -> None:
        """Validate cross-references between variants in the same book."""
        verse_counts: Dict[Tuple[int, int], int] = defaultdict(int)

        for variant in variants:
            chapter = variant.get('chapter')
            verse = variant.get('verse')
            if chapter and verse:
                verse_counts[(chapter, verse)] += 1

        # Check for multiple variants per verse (usually expected)
        max_variants_per_verse = 5  # Reasonable limit
        for (chapter, verse), count in verse_counts.items():
            if count > max_variants_per_verse:
                self.warnings[book].append(
                    f"Verse {chapter}:{verse} has {count} variants (unusually high)"
                )

        # Check for verse gaps (non-contiguous verses)
        chapters = sorted(set(v['chapter'] for v in variants if 'chapter' in v))
        for chapter in chapters:
            chapter_verses = sorted(set(v['verse'] for v in variants
                                      if v.get('chapter') == chapter))
            if chapter_verses:
                expected_range = set(range(min(chapter_verses), max(chapter_verses) + 1))
                missing_verses = expected_range - set(chapter_verses)
                if missing_verses and len(missing_verses) < 10:  # Only warn for small gaps
                    self.warnings[book].append(
                        f"Chapter {chapter} has gaps in verses: {sorted(missing_verses)}"
                    )

    def _generate_book_stats(self, book: str, variants: List[Dict[str, Any]]) -> None:
        """Generate statistics for a book."""
        self.stats[book] = {
            'total_variants': len(variants),
            'chapters_covered': len(set(v.get('chapter', 0) for v in variants)),
            'verses_covered': len(set((v.get('chapter', 0), v.get('verse', 0)) for v in variants)),
            'variant_types': defaultdict(int),
            'significance_levels': defaultdict(int),
            'completion_percentage': {
                'masoretic_text': sum(1 for v in variants if v.get('masoretic_text', '').strip()),
                'dss_text': sum(1 for v in variants if v.get('dss_text', '').strip()),
                'translations': sum(1 for v in variants if v.get('variant_translation_en', '').strip() or v.get('variant_translation_es', '').strip()),
                'comments': sum(1 for v in variants if v.get('comments_en', '').strip() or v.get('comments_es', '').strip())
            }
        }

        # Count variant types and significance
        for variant in variants:
            vtype = variant.get('variant_type', 'unknown')
            sig = variant.get('significance', 'unknown')
            self.stats[book]['variant_types'][vtype] += 1
            self.stats[book]['significance_levels'][sig] += 1

        # Convert defaultdicts to regular dicts
        self.stats[book]['variant_types'] = dict(self.stats[book]['variant_types'])
        self.stats[book]['significance_levels'] = dict(self.stats[book]['significance_levels'])

    def _generate_validation_report(self) -> None:
        """Generate a comprehensive validation report."""
        report_path = Path(__file__).parent / "validation_report.json"

        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_books_validated': len(BOOKS_WITH_VARIANTS),
                'books_with_errors': len([b for b in self.errors if self.errors[b]]),
                'books_with_warnings': len([b for b in self.warnings if self.warnings[b]]),
                'total_errors': sum(len(errors) for errors in self.errors.values()),
                'total_warnings': sum(len(warnings) for warnings in self.warnings.values())
            },
            'errors': dict(self.errors),
            'warnings': dict(self.warnings),
            'statistics': self.stats
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"Validation report saved to {report_path}")

        # Print summary to console
        print("\n=== DSS Validation Report ===")
        print(f"Books validated: {report['summary']['total_books_validated']}")
        print(f"Books with errors: {report['summary']['books_with_errors']}")
        print(f"Books with warnings: {report['summary']['books_with_warnings']}")
        print(f"Total errors: {report['summary']['total_errors']}")
        print(f"Total warnings: {report['summary']['total_warnings']}")

        if self.errors:
            print("\nErrors found:")
            for book, errors in self.errors.items():
                print(f"  {book}: {len(errors)} errors")

        if self.warnings:
            print("\nWarnings found:")
            for book, warnings in self.warnings.items():
                print(f"  {book}: {len(warnings)} warnings")

def main():
    """Main entry point for DSS validation."""
    validator = DSSValidator()

    success = validator.validate_all_books()

    return 0 if success else 1

if __name__ == "__main__":
    import re
    from datetime import datetime
    sys.exit(main())
