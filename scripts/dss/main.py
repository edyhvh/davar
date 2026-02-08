#!/usr/bin/env python3
"""
Main entry point for DSS differences parser
"""

import sys
from pathlib import Path

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from dss.config import BOOK_NAMES, NOTES_FILE
from dss.notes_parser import parse_notes_file
from dss.book_processor import BookProcessor
from dss.output_writer import OutputWriter


def main():
    """Main processing function."""
    print("Dead Sea Scrolls Differences Parser")
    print("=" * 60)
    
    # Parse notes first
    notes = parse_notes_file(NOTES_FILE)
    
    # Initialize processor and writer
    processor = BookProcessor(notes)
    writer = OutputWriter()
    
    # Process all books
    all_books = {}
    stats = {
        'total_books': 0,
        'total_differences': 0,
        'books_processed': []
    }
    
    for book_name in BOOK_NAMES.keys():
        book_data = processor.process_book(book_name)
        
        if book_data:
            # Use lowercase book name with underscores as key
            book_key = book_name.lower().replace(' ', '_')
            all_books[book_key] = book_data
            
            stats['books_processed'].append(BOOK_NAMES[book_name])
            stats['total_books'] += 1
            
            # Count differences
            for chapter in book_data['chapters'].values():
                for verse in chapter['verses'].values():
                    stats['total_differences'] += len(verse['differences'])
    
    # Write output files
    writer.write_differences(all_books)
    writer.write_metadata(stats)
    writer.print_summary(stats)


if __name__ == '__main__':
    main()
