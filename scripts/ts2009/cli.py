#!/usr/bin/env python3
"""
TS2009 Processing CLI
=====================

Command-line interface for TS2009 Bible processing system.

Usage:
    python cli.py all                    # Process all books
    python cli.py book <book_key>       # Process single book
    python cli.py book <book_key> --test # Test to temp directory
    python cli.py books                  # List available books
    python cli.py validate               # Validate output

Author: Davar Project
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import List, Optional

# Project paths - always relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "ts2009"
RAW_DIR = DATA_DIR / "raw"
TEMP_DIR = DATA_DIR / "temp"
OUTPUT_DIR = DATA_DIR

# Import TS2009 modules
try:
    # When run as module
    from .processor import TS2009Processor
    from .config import DEFAULT_DB_PATH, DEFAULT_OUTPUT_DIR, DEFAULT_TEMP_DIR
except ImportError:
    # When run as script
    from processor import TS2009Processor
    from config import DEFAULT_DB_PATH, DEFAULT_OUTPUT_DIR, DEFAULT_TEMP_DIR


class TS2009CLI:
    """Command-line interface for TS2009 processing."""

    def __init__(self):
        """Initialize CLI."""
        self.processor = TS2009Processor()

    def all_command(self, args: List[str]) -> int:
        """Handle all command to process all books."""
        test_mode = '--test' in args
        output_dir = str(TEMP_DIR) if test_mode else str(OUTPUT_DIR)

        if test_mode:
            args.remove('--test')

        print(f"Processing ALL books...")
        print(f"Results will go to: {output_dir}")
        print()

        try:
            processed = self.processor.process_all_books(Path(output_dir))
            print(f"\n✅ Completed: {len(processed)} books processed")
            return 0
        except Exception as e:
            print(f"❌ Error processing books: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def book_command(self, args: List[str]) -> int:
        """Handle book command for single book processing."""
        if not args:
            print("Usage: python cli.py book <book_key> [--test]")
            print("Example: python cli.py book amos")
            print("         python cli.py book amos --test")
            return 1

        book_key = args[0]
        test_mode = '--test' in args
        if test_mode:
            args.remove('--test')

        output_dir = TEMP_DIR if test_mode else OUTPUT_DIR

        print(f"Processing book: {book_key}")
        print(f"Results will go to: {output_dir}")
        print()

        # Get book number by name
        book_num = self.processor.get_book_number_by_name(book_key)
        if not book_num:
            print(f"❌ Book '{book_key}' not found")
            print(f"\nAvailable books:")
            self._print_available_books()
            return 1

        try:
            success = self.processor.process_single_book(book_num, output_dir)
            if success:
                print(f"\n✅ Book '{book_key}' processed successfully")
                return 0
            else:
                print(f"\n❌ Failed to process book '{book_key}'")
                return 1
        except Exception as e:
            print(f"❌ Error processing book: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def books_command(self, args: List[str]) -> int:
        """Handle books command to list available books."""
        print("Available books:")
        print()

        books = self.processor.get_available_books()
        
        # Group by section
        torah_books = []
        neviim_books = []
        ketuvim_books = []
        besorah_books = []

        # Get book info from BOOKS_MAPPING
        from config import BOOKS_MAPPING
        
        for book in books:
            for book_num, info in BOOKS_MAPPING.items():
                if info['name_anglicized'] == book:
                    section = info['section']
                    if section == 'torah':
                        torah_books.append(book)
                    elif section == 'neviim':
                        neviim_books.append(book)
                    elif section == 'ketuvim':
                        ketuvim_books.append(book)
                    elif section == 'besorah':
                        besorah_books.append(book)
                    break

        if torah_books:
            print("TORAH (Torah):")
            for book in sorted(torah_books):
                print(f"  {book}")
            print()

        if neviim_books:
            print("NEVI'IM (Prophets):")
            for book in sorted(neviim_books):
                print(f"  {book}")
            print()

        if ketuvim_books:
            print("KETUVIM (Writings):")
            for book in sorted(ketuvim_books):
                print(f"  {book}")
            print()

        if besorah_books:
            print("BESORAH (Gospel/Good News):")
            for book in sorted(besorah_books):
                print(f"  {book}")
            print()

        print(f"Total: {len(books)} books")
        return 0

    def validate_command(self, args: List[str]) -> int:
        """Handle validate command to validate output files."""
        output_dir = args[0] if args else str(OUTPUT_DIR)
        
        print(f"Validating TS2009 output in: {output_dir}")
        print()

        output_path = Path(output_dir)
        if not output_path.exists():
            print(f"❌ Output directory not found: {output_dir}")
            return 1

        # Get all JSON files
        json_files = list(output_path.glob("*.json"))
        if not json_files:
            print(f"❌ No JSON files found in: {output_dir}")
            return 1

        print(f"Found {len(json_files)} JSON files")
        print()

        valid_count = 0
        invalid_count = 0
        issues = []

        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate structure
                if 'metadata' not in data:
                    issues.append(f"{json_file.name}: Missing 'metadata'")
                    invalid_count += 1
                    continue
                
                if 'chapters' not in data:
                    issues.append(f"{json_file.name}: Missing 'chapters'")
                    invalid_count += 1
                    continue
                
                # Validate metadata
                metadata = data['metadata']
                required_metadata = ['book_id', 'book_name', 'section', 'total_chapters', 'total_verses']
                for field in required_metadata:
                    if field not in metadata:
                        issues.append(f"{json_file.name}: Missing metadata field '{field}'")
                        invalid_count += 1
                        break
                else:
                    # Validate chapters
                    chapters = data['chapters']
                    if not isinstance(chapters, list):
                        issues.append(f"{json_file.name}: 'chapters' is not a list")
                        invalid_count += 1
                        continue
                    
                    valid_count += 1
                    print(f"✓ {json_file.name}")
            
            except json.JSONDecodeError as e:
                issues.append(f"{json_file.name}: Invalid JSON - {e}")
                invalid_count += 1
            except Exception as e:
                issues.append(f"{json_file.name}: Error - {e}")
                invalid_count += 1

        print()
        print(f"Validation complete:")
        print(f"  Valid: {valid_count}")
        print(f"  Invalid: {invalid_count}")
        
        if issues:
            print()
            print("Issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return 1
        
        return 0

    def _print_available_books(self):
        """Print available books grouped by section."""
        books = self.processor.get_available_books()
        
        from config import BOOKS_MAPPING
        
        torah_books = []
        neviim_books = []
        ketuvim_books = []
        besorah_books = []

        for book in books:
            for book_num, info in BOOKS_MAPPING.items():
                if info['name_anglicized'] == book:
                    section = info['section']
                    if section == 'torah':
                        torah_books.append(book)
                    elif section == 'neviim':
                        neviim_books.append(book)
                    elif section == 'ketuvim':
                        ketuvim_books.append(book)
                    elif section == 'besorah':
                        besorah_books.append(book)
                    break

        if torah_books:
            print("  Torah:", ", ".join(sorted(torah_books)))
        if neviim_books:
            print("  Nevi'im:", ", ".join(sorted(neviim_books)))
        if ketuvim_books:
            print("  Ketuvim:", ", ".join(sorted(ketuvim_books)))
        if besorah_books:
            print("  Besorah:", ", ".join(sorted(besorah_books)))


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("TS2009 Bible Processor CLI")
        print("=" * 60)
        print()
        print("Usage:")
        print("  python cli.py all                    # Process all books")
        print("  python cli.py book <book_key>       # Process single book")
        print("  python cli.py book <book_key> --test # Test to temp directory")
        print("  python cli.py books                  # List available books")
        print("  python cli.py validate               # Validate output")
        print()
        print("Examples:")
        print("  python cli.py all")
        print("  python cli.py book amos")
        print("  python cli.py book amos --test")
        print("  python cli.py books")
        print("  python cli.py validate")
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    cli = TS2009CLI()

    if command == 'all':
        return cli.all_command(args)
    elif command == 'book':
        return cli.book_command(args)
    elif command == 'books':
        return cli.books_command(args)
    elif command == 'validate':
        return cli.validate_command(args)
    else:
        print(f"❌ Unknown command: {command}")
        print()
        print("Available commands:")
        print("  all      - Process all books")
        print("  book     - Process single book")
        print("  books    - List available books")
        print("  validate - Validate output")
        return 1


if __name__ == '__main__':
    exit(main())
