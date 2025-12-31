#!/usr/bin/env python3
"""
TTH Claude Processor - Main CLI
===============================

Command-line interface for processing TTH books.

Usage:
    python main.py <book_key>                    # Process single book to temp/
    python main.py <book_key> --output <dir>     # Process to specific directory
    python main.py <book_key> --chapters         # Split into chapter files
    python main.py --list                        # List available books
    python main.py --all                         # Process all books

Author: Davar Project
"""

import argparse
import sys
from pathlib import Path

from config import BOOKS_INFO, TEMP_PATH
from processor import process_book


def list_books():
    """List all available books."""
    print("\nAvailable books:")
    print("=" * 60)
    
    # Group by section
    sections = {}
    for key, info in BOOKS_INFO.items():
        section = info['section']
        if section not in sections:
            sections[section] = []
        sections[section].append((key, info))
    
    section_order = ['torah', 'neviim', 'ketuvim', 'besorah']
    
    for section in section_order:
        if section not in sections:
            continue
        
        # Get section display name
        first_book = sections[section][0][1]
        section_name = first_book.get('section_spanish', section.capitalize())
        section_hebrew = first_book.get('section_hebrew', '')
        
        print(f"\n{section_name} ({section_hebrew}):")
        print("-" * 40)
        
        for key, info in sections[section]:
            print(f"  {key:20} - {info['tth_name']:20} ({info['hebrew_name']})")
    
    print()


def process_all_books(output_dir: Path, split_chapters: bool = False):
    """Process all available books."""
    results = {'success': [], 'failed': []}
    
    for book_key in BOOKS_INFO:
        try:
            print(f"\n{'='*60}")
            print(f"Processing: {book_key}")
            print(f"{'='*60}")
            process_book(book_key, output_dir, split_chapters)
            results['success'].append(book_key)
        except Exception as e:
            print(f"ERROR processing {book_key}: {e}")
            results['failed'].append((book_key, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Success: {len(results['success'])} books")
    if results['failed']:
        print(f"Failed: {len(results['failed'])} books")
        for book, error in results['failed']:
            print(f"  - {book}: {error}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Process TTH books into structured JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py amos                     # Process Amos
  python main.py bereshit --chapters      # Process Genesis with chapter files
  python main.py --list                   # List all available books
  python main.py --all                    # Process all books
        """
    )
    
    parser.add_argument(
        'book',
        nargs='?',
        help='Book key to process (e.g., amos, bereshit)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=TEMP_PATH,
        help='Output directory (default: data/tth/temp)'
    )
    
    parser.add_argument(
        '-c', '--chapters',
        action='store_true',
        help='Split output into separate chapter files'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available books'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all available books'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_books()
        return 0
    
    if args.all:
        results = process_all_books(args.output, args.chapters)
        return 0 if not results['failed'] else 1
    
    if not args.book:
        parser.print_help()
        return 1
    
    if args.book not in BOOKS_INFO:
        print(f"Error: Unknown book '{args.book}'")
        print("Use --list to see available books")
        return 1
    
    try:
        result = process_book(args.book, args.output, args.chapters)
        
        # Print summary
        print("\n" + "=" * 60)
        print("PROCESSING COMPLETE")
        print("=" * 60)
        print(f"Book: {args.book}")
        print(f"Chapters: {result['book_info']['total_chapters']}")
        print(f"Verses: {result['book_info']['total_verses']}")
        print(f"Output: {args.output}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
