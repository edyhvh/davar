#!/usr/bin/env python3
"""
Hebrew Scripture Verses Migration Script

Consolidates individual verse JSON files into consolidated book JSON files.
This script migrates from the old structure (one file per verse) to the new
consolidated structure (one file per book) for better performance and maintainability.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple
import argparse


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return {}


def parse_verse_reference(reference: str) -> Tuple[str, str, str]:
    """
    Parse a verse reference like 'genesis.1.1' into book, chapter, verse.

    Returns:
        Tuple of (book, chapter, verse) as strings
    """
    parts = reference.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid reference format: {reference}")
    return parts[0], parts[1], parts[2]


def consolidate_book_verses(book_dir: Path, output_file: Path) -> Tuple[int, int]:
    """
    Consolidate all verse files for a single book into one consolidated JSON file.

    Args:
        book_dir: Directory containing verse files for this book (e.g., verses/genesis/)
        output_file: Path where to save the consolidated book file

    Returns:
        Tuple of (chapters_count, verses_count)
    """
    if not book_dir.exists():
        print(f"❌ Book directory not found: {book_dir}")
        return 0, 0

    book_name = book_dir.name
    book_data = {}
    verses_processed = 0

    print(f"📖 Processing book: {book_name}")

    # Process each verse file in the book directory
    for verse_file in sorted(book_dir.glob('*.json')):
        if verse_file.name.startswith('.'):
            continue  # Skip hidden files

        # Load the verse data
        verse_data = load_json_file(verse_file)
        if not verse_data:
            continue

        # Extract reference information
        reference = verse_data.get('reference')
        if not reference:
            print(f"⚠️  Missing reference in {verse_file}")
            continue

        try:
            parsed_book, chapter, verse = parse_verse_reference(reference)

            # Verify book name matches directory
            if parsed_book != book_name:
                print(f"⚠️  Book mismatch: expected {book_name}, got {parsed_book} in {verse_file}")
                continue

        except ValueError as e:
            print(f"⚠️  Invalid reference {reference} in {verse_file}: {e}")
            continue

        # Organize by chapter -> verse
        if chapter not in book_data:
            book_data[chapter] = {}

        book_data[chapter][verse] = verse_data
        verses_processed += 1

        if verses_processed % 1000 == 0:
            print(f"  📊 Processed {verses_processed} verses in {book_name}...")

    chapters_count = len(book_data)

    if verses_processed == 0:
        print(f"⚠️  No verses found for book {book_name}")
        return 0, 0

    print(f"✅ Processed {verses_processed} verses in {chapters_count} chapters for {book_name}")

    # Sort chapters and verses numerically
    sorted_book_data = {}
    for chapter in sorted(book_data.keys(), key=int):
        sorted_chapter_data = {}
        for verse in sorted(book_data[chapter].keys(), key=int):
            sorted_chapter_data[verse] = book_data[chapter][verse]
        sorted_book_data[chapter] = sorted_chapter_data

    # Save consolidated book file
    print(f"💾 Saving consolidated book to {output_file}...")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_book_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Successfully saved {output_file}")
    except Exception as e:
        print(f"❌ Error saving {output_file}: {e}")
        return 0, 0

    return chapters_count, verses_processed


def validate_consolidated_book(file_path: Path, expected_chapters: int, expected_verses: int) -> bool:
    """Validate that the consolidated book file was created correctly."""
    if not file_path.exists():
        print(f"❌ Consolidated book file not found: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        actual_chapters = len(data)
        actual_verses = sum(len(chapter_data) for chapter_data in data.values())

        if actual_chapters != expected_chapters:
            print(f"⚠️  Chapter count mismatch: expected {expected_chapters}, got {actual_chapters}")
            return False

        if actual_verses != expected_verses:
            print(f"⚠️  Verse count mismatch: expected {expected_verses}, got {actual_verses}")
            return False

        # Validate structure
        for chapter, chapter_data in data.items():
            if not isinstance(chapter_data, dict):
                print(f"⚠️  Invalid chapter structure for chapter {chapter}")
                return False

            for verse, verse_data in chapter_data.items():
                if not isinstance(verse_data, dict):
                    print(f"⚠️  Invalid verse structure for {chapter}.{verse}")
                    return False

                required_fields = ['reference', 'book_id', 'chapter', 'verse', 'hebrew_text', 'words']
                for field in required_fields:
                    if field not in verse_data:
                        print(f"⚠️  Missing field '{field}' in {chapter}.{verse}")
                        return False

        print(f"✅ Validation passed: {actual_chapters} chapters, {actual_verses} verses in {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error validating {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Consolidate verse files into books')
    parser.add_argument('--book', help='Process only specific book (e.g., genesis)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    print("=" * 70)
    print("HEBREW SCRIPTURE VERSES MIGRATION")
    print("=" * 70)

    # Define paths
    script_dir = Path(__file__).parent.parent.parent.parent  # scripts/dict/temp -> scripts -> davar
    data_dir = script_dir / 'data' / 'dict'
    verses_dir = data_dir / 'verses'
    books_dir = data_dir / 'books'

    print(f"📁 Data directory: {data_dir}")
    print(f"📁 Source verses directory: {verses_dir}")
    print(f"📁 Target books directory: {books_dir}")
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()

    # Check if source directory exists
    if not verses_dir.exists():
        print(f"❌ Verses source directory not found: {verses_dir}")
        sys.exit(1)

    # Create books directory if it doesn't exist
    if not args.dry_run:
        books_dir.mkdir(exist_ok=True)

    # Get list of books to process
    if args.book:
        book_dirs = [verses_dir / args.book]
        if not book_dirs[0].exists():
            print(f"❌ Book directory not found: {book_dirs[0]}")
            sys.exit(1)
    else:
        book_dirs = [d for d in sorted(verses_dir.iterdir()) if d.is_dir()]

    print(f"📚 Found {len(book_dirs)} book directories")
    if args.book:
        print(f"🎯 Processing only: {args.book}")
    print()

    total_books = 0
    total_chapters = 0
    total_verses = 0
    failed_books = []

    # Process each book
    for book_dir in book_dirs:
        book_name = book_dir.name
        output_file = books_dir / f"{book_name}.json"

        if args.dry_run:
            verse_files = list(book_dir.glob('*.json'))
            print(f"🔍 Would consolidate {len(verse_files)} verse files → {output_file}")
            continue

        print(f"📖 Processing {book_name}...")

        # Count files before processing
        verse_files = list(book_dir.glob('*.json'))
        expected_verses = len(verse_files)

        chapters_count, verses_count = consolidate_book_verses(book_dir, output_file)

        if chapters_count > 0 and verses_count > 0:
            # Validate the result
            if validate_consolidated_book(output_file, chapters_count, verses_count):
                total_books += 1
                total_chapters += chapters_count
                total_verses += verses_count
                print(f"✅ {book_name}: {chapters_count} chapters, {verses_count} verses")
            else:
                failed_books.append(book_name)
                print(f"❌ {book_name}: Validation failed")
        else:
            failed_books.append(book_name)
            print(f"❌ {book_name}: Processing failed")

        print()

    if args.dry_run:
        print(f"🔍 Would process {len(book_dirs)} books")
        return

    # Summary
    print("=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)

    if failed_books:
        print(f"❌ Failed books: {', '.join(failed_books)}")
        print("Please check the errors above and fix them before proceeding.")
        sys.exit(1)

    print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
    print(f"  📚 Books processed: {total_books}")
    print(f"  📖 Chapters total: {total_chapters}")
    print(f"  📝 Verses total: {total_verses}")
    print()
    print(f"📁 New structure created in: {books_dir}")
    print()
    print("📋 Next steps:")
    print("  1. Review the consolidated book files")
    print("  2. Run tests to ensure data integrity")
    print("  3. Update any scripts that reference individual verse files")
    print("  4. Remove old verses directory after verification")


if __name__ == '__main__':
    main()
