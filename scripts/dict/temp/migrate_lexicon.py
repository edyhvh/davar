#!/usr/bin/env python3
"""
Hebrew Scripture Lexicon Migration Script

Consolidates individual lexicon JSON files into consolidated roots.json and words.json files.
This script migrates from the old structure (one file per Strong's number) to the new
consolidated structure for better performance and maintainability.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
import argparse


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return {}


def consolidate_lexicon_files(source_dir: Path, output_file: Path, file_type: str) -> int:
    """
    Consolidate all JSON files in source_dir into a single consolidated JSON file.

    Args:
        source_dir: Directory containing individual JSON files
        output_file: Path where to save the consolidated file
        file_type: Type of files being consolidated ('roots' or 'words')

    Returns:
        Number of entries consolidated
    """
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return 0

    consolidated_data = {}
    files_processed = 0

    print(f"📂 Processing {file_type} from {source_dir}...")

    # Process each JSON file in the directory
    for json_file in sorted(source_dir.glob('*.json')):
        if json_file.name.startswith('.'):
            continue  # Skip hidden files

        # Load the individual file
        entry_data = load_json_file(json_file)
        if not entry_data:
            continue

        # Use strong_number as the key
        strong_number = entry_data.get('strong_number')
        if not strong_number:
            print(f"⚠️  Missing strong_number in {json_file}")
            continue

        consolidated_data[strong_number] = entry_data
        files_processed += 1

        if files_processed % 500 == 0:
            print(f"  📊 Processed {files_processed} {file_type}...")

    print(f"✅ Processed {files_processed} {file_type} files")

    # Sort by strong_number for consistency
    sorted_data = dict(sorted(consolidated_data.items()))

    # Save consolidated file
    print(f"💾 Saving consolidated {file_type} to {output_file}...")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Successfully saved {output_file} ({len(sorted_data)} entries)")
    except Exception as e:
        print(f"❌ Error saving {output_file}: {e}")
        return 0

    return len(sorted_data)


def validate_consolidated_file(file_path: Path, expected_entries: int) -> bool:
    """Validate that the consolidated file was created correctly."""
    if not file_path.exists():
        print(f"❌ Consolidated file not found: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        actual_entries = len(data)
        if actual_entries != expected_entries:
            print(f"⚠️  Entry count mismatch: expected {expected_entries}, got {actual_entries}")
            return False

        print(f"✅ Validation passed: {actual_entries} entries in {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error validating {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Consolidate lexicon files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    print("=" * 70)
    print("HEBREW SCRIPTURE LEXICON MIGRATION")
    print("=" * 70)

    # Define paths
    script_dir = Path(__file__).parent.parent.parent.parent  # scripts/dict/temp -> scripts -> davar
    data_dir = script_dir / 'data' / 'dict'
    lexicon_dir = data_dir / 'lexicon'

    roots_source = lexicon_dir / 'roots'
    words_source = lexicon_dir / 'words'

    roots_output = lexicon_dir / 'roots.json'
    words_output = lexicon_dir / 'words.json'

    print(f"📁 Data directory: {data_dir}")
    print(f"📁 Lexicon directory: {lexicon_dir}")
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()

    # Check if source directories exist
    if not roots_source.exists():
        print(f"❌ Roots source directory not found: {roots_source}")
        sys.exit(1)

    if not words_source.exists():
        print(f"❌ Words source directory not found: {words_source}")
        sys.exit(1)

    # Count expected files
    roots_files = list(roots_source.glob('*.json'))
    words_files = list(words_source.glob('*.json'))

    print(f"📊 Found {len(roots_files)} root files")
    print(f"📊 Found {len(words_files)} word files")
    print()

    if args.dry_run:
        print("🔍 Would consolidate:")
        print(f"  {len(roots_files)} root files → {roots_output}")
        print(f"  {len(words_files)} word files → {words_output}")
        return

    # Consolidate roots
    roots_count = consolidate_lexicon_files(roots_source, roots_output, 'roots')
    if roots_count == 0:
        print("❌ Failed to consolidate roots")
        sys.exit(1)

    # Consolidate words
    words_count = consolidate_lexicon_files(words_source, words_output, 'words')
    if words_count == 0:
        print("❌ Failed to consolidate words")
        sys.exit(1)

    print()
    print("🔍 Validating consolidated files...")

    # Validate results
    roots_valid = validate_consolidated_file(roots_output, roots_count)
    words_valid = validate_consolidated_file(words_output, words_count)

    if roots_valid and words_valid:
        print()
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print(f"  📄 {roots_output.name}: {roots_count} root entries")
        print(f"  📄 {words_output.name}: {words_count} word entries")
        print()
        print("📋 Next steps:")
        print("  1. Review the consolidated files")
        print("  2. Run tests to ensure data integrity")
        print("  3. Update any scripts that reference individual files")
        print("  4. Remove old individual files after verification")
    else:
        print("❌ MIGRATION FAILED - Validation errors found")
        sys.exit(1)


if __name__ == '__main__':
    main()
