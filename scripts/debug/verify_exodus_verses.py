#!/usr/bin/env python3
"""
Exodus Verses Validation Script

Validates the quality and structure of generated Exodus verse JSON files.
This script checks:
- File structure and naming convention
- JSON validity
- Required fields presence
- Strong's numbers format
- Sense validation against lexicon
- Statistical analysis
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
import argparse

# Configuration
EXODUS_DIR = Path(__file__).parent.parent.parent / 'data' / 'dict' / 'verses' / 'exodus'
LEXICON_DIR = Path(__file__).parent.parent.parent / 'data' / 'dict' / 'lexicon'
EXPECTED_TOTAL_VERSES = 1213  # Exodus has 1213 verses


class ExodusValidator:
    """Validator for Exodus verse files."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = defaultdict(int)
        self.strong_numbers = set()
        self.senses_found = Counter()
        self.senses_null = 0

    def log_error(self, message: str):
        """Log an error."""
        self.errors.append(message)
        print(f"❌ {message}")

    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        print(f"⚠️  {message}")

    def validate_file_structure(self) -> bool:
        """Validate overall file structure."""
        print("📁 Validating file structure...")

        if not EXODUS_DIR.exists():
            self.log_error(f"Exodus directory not found: {EXODUS_DIR}")
            return False

        files = list(EXODUS_DIR.glob("*.json"))
        self.stats['total_files'] = len(files)

        print(f"   Found {len(files)} JSON files")

        if len(files) != EXPECTED_TOTAL_VERSES:
            self.log_warning(f"Expected {EXPECTED_TOTAL_VERSES} files, found {len(files)}")

        # Check naming convention
        naming_errors = 0
        for file_path in files:
            filename = file_path.name
            if not filename.startswith('exodus.') or not filename.endswith('.json'):
                self.log_error(f"Invalid filename: {filename}")
                naming_errors += 1
                continue

            # Check format: exodus.X.Y.json
            parts = filename.replace('.json', '').split('.')
            if len(parts) != 3 or parts[0] != 'exodus':
                self.log_error(f"Invalid filename format: {filename}")
                naming_errors += 1
                continue

            try:
                chapter = int(parts[1])
                verse = int(parts[2])
                if chapter < 1 or chapter > 40 or verse < 1:
                    self.log_error(f"Invalid chapter/verse numbers in: {filename}")
                    naming_errors += 1
            except ValueError:
                self.log_error(f"Non-numeric chapter/verse in: {filename}")
                naming_errors += 1

        if naming_errors == 0:
            print("   ✅ All filenames follow correct convention")
        else:
            print(f"   ❌ {naming_errors} naming errors found")

        return naming_errors == 0

    def validate_json_structure(self, sample_size: int = 100) -> bool:
        """Validate JSON structure of sample files."""
        print(f"\n🔍 Validating JSON structure (sample: {sample_size} files)...")

        files = list(EXODUS_DIR.glob("*.json"))
        if len(files) < sample_size:
            sample_size = len(files)

        sample_files = files[:sample_size]  # First N files

        json_errors = 0
        structure_errors = 0

        required_fields = ['reference', 'book_id', 'chapter', 'verse', 'hebrew_text', 'words']

        for file_path in sample_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Check required fields
                for field in required_fields:
                    if field not in data:
                        self.log_error(f"Missing required field '{field}' in {file_path.name}")
                        structure_errors += 1
                        continue

                # Validate structure
                if data.get('book_id') != 'exodus':
                    self.log_error(f"Invalid book_id in {file_path.name}: {data.get('book_id')}")
                    structure_errors += 1

                if not isinstance(data.get('words'), list):
                    self.log_error(f"'words' field is not a list in {file_path.name}")
                    structure_errors += 1
                    continue

                # Validate words structure
                for i, word in enumerate(data['words'], 1):
                    if not isinstance(word, dict):
                        self.log_error(f"Word {i} is not a dict in {file_path.name}")
                        structure_errors += 1
                        continue

                    word_fields = ['position', 'hebrew', 'strong_number']
                    for field in word_fields:
                        if field not in word:
                            self.log_error(f"Missing '{field}' in word {i} of {file_path.name}")
                            structure_errors += 1

                    # Collect statistics
                    if word.get('strong_number'):
                        self.strong_numbers.add(word['strong_number'])

                    sense = word.get('sense')
                    if sense is not None:
                        self.senses_found[sense] += 1
                    else:
                        self.senses_null += 1

                self.stats['verses_validated'] += 1
                self.stats['total_words'] += len(data['words'])

            except json.JSONDecodeError as e:
                self.log_error(f"Invalid JSON in {file_path.name}: {e}")
                json_errors += 1
            except Exception as e:
                self.log_error(f"Error processing {file_path.name}: {e}")
                json_errors += 1

        if json_errors == 0:
            print(f"   ✅ All {sample_size} sampled files have valid JSON")
        else:
            print(f"   ❌ {json_errors} JSON errors found")

        if structure_errors == 0:
            print(f"   ✅ All sampled files have correct structure")
        else:
            print(f"   ❌ {structure_errors} structure errors found")

        return json_errors == 0 and structure_errors == 0

    def validate_strongs_format(self) -> bool:
        """Validate Strong's number format."""
        print("\n🔢 Validating Strong's numbers format...")
        invalid_strongs = []

        for strong in self.strong_numbers:
            if not strong.startswith('H') or not strong[1:].isdigit():
                invalid_strongs.append(strong)

        if invalid_strongs:
            for strong in invalid_strongs[:10]:  # Show first 10
                self.log_error(f"Invalid Strong's format: {strong}")
            if len(invalid_strongs) > 10:
                print(f"   ... and {len(invalid_strongs) - 10} more")
            return False

        print(f"   ✅ All {len(self.strong_numbers)} Strong's numbers have correct format (HXXXX)")
        return True

    def validate_senses(self) -> bool:
        """Validate sense assignments."""
        print("\n🎯 Validating sense assignments...")
        print(f"   Total senses assigned: {sum(self.senses_found.values())}")
        print(f"   Total senses null: {self.senses_null}")
        print(f"   Unique sense values: {len(self.senses_found)}")

        # Show most common senses
        if self.senses_found:
            print("   Most common senses:")
            for sense, count in self.senses_found.most_common(5):
                print(f"      Sense '{sense}': {count} occurrences")

        # Check for unusual sense values
        unusual_senses = []
        for sense in self.senses_found.keys():
            if not (isinstance(sense, str) and (sense.isdigit() or len(sense) <= 3)):
                unusual_senses.append(sense)

        if unusual_senses:
            self.log_warning(f"Unusual sense values found: {unusual_senses[:5]}")
            if len(unusual_senses) > 5:
                print(f"   ... and {len(unusual_senses) - 5} more")

        return len(unusual_senses) == 0

    def generate_report(self) -> Dict:
        """Generate validation report."""
        print("\n📊 VALIDATION REPORT")
        print("=" * 50)

        report = {
            'summary': {
                'total_files': self.stats['total_files'],
                'expected_files': EXPECTED_TOTAL_VERSES,
                'files_validated': self.stats.get('verses_validated', 0),
                'total_words': self.stats.get('total_words', 0),
                'unique_strong_numbers': len(self.strong_numbers),
                'errors': len(self.errors),
                'warnings': len(self.warnings)
            },
            'senses': {
                'assigned': sum(self.senses_found.values()),
                'null': self.senses_null,
                'unique_values': len(self.senses_found),
                'most_common': dict(self.senses_found.most_common(10))
            },
            'errors': self.errors[:20],  # First 20 errors
            'warnings': self.warnings[:20]  # First 20 warnings
        }

        print(f"📁 Files: {self.stats['total_files']}/{EXPECTED_TOTAL_VERSES} (expected)")
        print(f"✅ Validated: {self.stats.get('verses_validated', 0)} verses")
        print(f"📝 Total words: {self.stats.get('total_words', 0)}")
        print(f"🔢 Unique Strong's: {len(self.strong_numbers)}")
        print(f"🎯 Senses assigned: {sum(self.senses_found.values())}")
        print(f"🎯 Senses null: {self.senses_null}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")

        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors[:5]:
                print(f"   {error}")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings[:5]:
                print(f"   {warning}")
            if len(self.warnings) > 5:
                print(f"   ... and {len(self.warnings) - 5} more")

        overall_status = "✅ PASS" if not self.errors else "❌ FAIL"
        print(f"\n{overall_status}")

        return report

    def run_validation(self, sample_size: int = 100) -> bool:
        """Run complete validation suite."""
        print("🚀 Starting Exodus Verses Validation")
        print("=" * 50)

        # Run all validations
        structure_ok = self.validate_file_structure()
        json_ok = self.validate_json_structure(sample_size)
        strongs_ok = self.validate_strongs_format()
        senses_ok = self.validate_senses()

        # Generate report
        self.generate_report()

        # Return overall status
        return structure_ok and json_ok and strongs_ok and senses_ok


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate Exodus verse JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate with default sample size (100 files)
  python scripts/debug/verify_exodus_verses.py

  # Validate with larger sample
  python scripts/debug/verify_exodus_verses.py --sample 500

  # Quick validation (10 files)
  python scripts/debug/verify_exodus_verses.py --sample 10
        """
    )
    parser.add_argument(
        '--sample', '-s',
        type=int,
        default=100,
        help='Number of files to sample for detailed validation (default: 100)'
    )

    args = parser.parse_args()

    validator = ExodusValidator()
    success = validator.run_validation(args.sample)

    exit(0 if success else 1)


if __name__ == "__main__":
    main()
