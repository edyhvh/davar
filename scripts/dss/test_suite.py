#!/usr/bin/env python3
"""
Basic Tests for DSS Processing Scripts

Simple tests to verify that the DSS processing system works correctly.

Author: Davar Project Team
License: MIT
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from dss_config import BOOKS_WITH_VARIANTS, get_book_file_path
        from processor import DSSProcessor
        from dss_types import DSSVariant
        from validator import DSSValidator
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_config():
    """Test configuration settings."""
    try:
        from dss_config import BOOKS_WITH_VARIANTS, BOOK_MAPPINGS

        assert 'isaiah' in BOOKS_WITH_VARIANTS
        assert 'samuel_1' in BOOKS_WITH_VARIANTS
        assert 'samuel_2' in BOOKS_WITH_VARIANTS

        assert BOOK_MAPPINGS['isaiah'] == 'Isaiah'

        print("✓ Configuration tests passed")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_variant_creation():
    """Test DSS variant creation and validation."""
    try:
        from dss_processor import DSSVariant

        # Create a valid variant
        variant = DSSVariant(
            book="isaiah",
            chapter=1,
            verse=1,
            masoretic_text="חָזוֹן יְשַׁעְיָהוּ",
            dss_text="חָזוֹן יְשַׁעְיָהוּ",
            variant_type="spelling",
            significance="low"
        )

        # Test validation
        errors = variant.validate()
        assert len(errors) == 0, f"Validation errors: {errors}"

        # Test serialization
        data = variant.to_dict()
        assert data['book'] == 'isaiah'
        assert data['chapter'] == 1

        # Test deserialization
        variant2 = DSSVariant.from_dict(data)
        assert variant2.book == variant.book

        print("✓ Variant creation and validation tests passed")
        return True
    except Exception as e:
        print(f"✗ Variant test failed: {e}")
        return False

def test_processor():
    """Test DSS processor functionality."""
    try:
        from dss_processor import DSSProcessor, DSSVariant

        processor = DSSProcessor()

        # Add a test variant
        variant = DSSVariant(
            book="isaiah",
            chapter=1,
            verse=1,
            masoretic_text="טֶקסט מָשׂוֹרֵתִי",
            dss_text="טֶקסט קוּמְרָאנִי",
            variant_type="substitution",
            significance="medium"
        )

        success = processor.add_variant(variant)
        assert success, "Failed to add variant"

        # Check retrieval
        variants = processor.get_variants("isaiah")
        assert len(variants) > 0, "No variants retrieved"

        # Check statistics
        stats = processor.generate_statistics()
        assert stats['total_variants'] > 0, "No variants in statistics"

        print("✓ Processor tests passed")
        return True
    except Exception as e:
        print(f"✗ Processor test failed: {e}")
        return False

def test_json_files():
    """Test that JSON files exist and are valid."""
    try:
        json_files = [
            Path(__file__).parent.parent.parent / "dss" / "isaiah_dss_variants.json",
            Path(__file__).parent.parent.parent / "dss" / "samuel_1_dss_variants.json",
            Path(__file__).parent.parent.parent / "dss" / "samuel_2_dss_variants.json"
        ]

        for json_file in json_files:
            assert json_file.exists(), f"JSON file not found: {json_file}"

            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            assert 'metadata' in data, f"No metadata in {json_file}"
            assert 'variants' in data, f"No variants array in {json_file}"
            assert isinstance(data['variants'], list), f"Variants not a list in {json_file}"

        print("✓ JSON file tests passed")
        return True
    except Exception as e:
        print(f"✗ JSON file test failed: {e}")
        return False

def run_tests():
    """Run all tests."""
    print("Running DSS Processing Tests")
    print("=" * 30)

    tests = [
        test_imports,
        test_config,
        test_variant_creation,
        test_processor,
        test_json_files
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 30)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())

