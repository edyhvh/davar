#!/usr/bin/env python3
"""
DSS Processing Example Usage

Demonstrates how to use the DSS processing scripts to extract,
validate, and manage textual variants from Dead Sea Scrolls.

Author: Davar Project Team
License: MIT
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dss_processor import DSSProcessor, DSSVariant

def example_basic_usage():
    """Demonstrate basic DSS processor usage."""
    print("=== DSS Processor Basic Usage ===\n")

    # Initialize processor
    processor = DSSProcessor()

    # Create a sample variant
    sample_variant = DSSVariant(
        book="isaiah",
        chapter=1,
        verse=1,
        masoretic_text="מַשָּׂא יִשְׂרָאֵל",
        dss_text="מַשָּׂא יִשְׂרָאֵל",
        variant_translation_en="The burden of Israel",
        variant_translation_es="La carga de Israel",
        comments_en="Minor spelling variation in DSS manuscript 1QIsaa",
        comments_es="Variación menor de ortografía en el manuscrito 1QIsaa de Qumrán",
        dss_source="1QIsaa",
        variant_type="spelling",
        significance="low"
    )

    # Add variant
    if processor.add_variant(sample_variant):
        print("✓ Sample variant added successfully")
    else:
        print("✗ Failed to add sample variant")

    # Get variants
    isaiah_variants = processor.get_variants("isaiah")
    print(f"Total Isaiah variants: {len(isaiah_variants)}")

    # Generate statistics
    stats = processor.generate_statistics()
    print(f"\nStatistics: {stats['total_variants']} total variants across {stats['total_books']} books")

    # Save data
    processor.save_data()
    print("✓ Data saved to JSON files")

def example_pdf_processing():
    """Demonstrate PDF processing (requires actual PDF file)."""
    print("\n=== PDF Processing Example ===\n")

    # This would be used with the actual PDF file
    pdf_path = Path(__file__).parent.parent.parent / "data" / "dss" / "raw" / "VARIANTES - TEXTO MASORÉTICO Y QUMRÁN.pdf"

    if pdf_path.exists():
        print(f"PDF found at: {pdf_path}")
        print("To process PDF, run: python dss_extractor.py <pdf_path>")
    else:
        print("PDF file not found in expected location")
        print("To process a PDF, place it in data/dss/ and run:")
        print("python dss_extractor.py data/dss/your_file.pdf")

def example_validation():
    """Demonstrate validation usage."""
    print("\n=== Validation Example ===\n")

    from dss_validator import DSSValidator

    validator = DSSValidator()
    is_valid = validator.validate_all_books()

    if is_valid:
        print("✓ All DSS data passed validation")
    else:
        print("✗ Validation errors found")
        print("Run 'python dss_validator.py' for detailed report")

def example_data_structure():
    """Show the expected data structure."""
    print("\n=== DSS Variant Data Structure ===\n")

    structure = {
        "book": "isaiah",
        "chapter": 1,
        "verse": 1,
        "masoretic_text": "כָּל־הָאָרֶץ",
        "dss_text": "כָל־הָאָרֶץ",
        "variant_translation_en": "All the earth",
        "variant_translation_es": "Toda la tierra",
        "comments_he": "שינוי קל בכתיב",
        "comments_en": "Minor spelling change",
        "comments_es": "Cambio menor de ortografía",
        "dss_source": "1QIsaa",
        "variant_type": "spelling",
        "significance": "low"
    }

    import json
    print("Complete variant structure:")
    print(json.dumps(structure, ensure_ascii=False, indent=2))

def main():
    """Run all examples."""
    print("DSS Processing Scripts - Example Usage")
    print("=" * 40)

    try:
        example_basic_usage()
        example_pdf_processing()
        example_validation()
        example_data_structure()

        print("\n" + "=" * 40)
        print("Examples completed successfully!")
        print("\nNext steps:")
        print("1. Add your PDF file to data/dss/")
        print("2. Run: python dss_extractor.py data/dss/your_pdf.pdf")
        print("3. Run: python dss_validator.py")
        print("4. Check generated JSON files in dss/ directory")

    except Exception as e:
        print(f"Error running examples: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())

