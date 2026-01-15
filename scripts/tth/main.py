#!/usr/bin/env python3
"""
TTH Processing System - Main Entry Point
=========================================

Main entry point for the TTH (Textual Translation of Hebrew) processing system.

Usage:
    python main.py <book_key>                # Process book to data/tth/temp (test mode)
    python main.py <book_key> --prod         # Process book to data/tth/ (production)
    python main.py run <book_key>            # Same as above (production)
    python main.py test <book_key>           # Test mode (data/tth/temp)
    python main.py books                     # List available books

Author: Davar Project
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Project paths
PROJECT_ROOT = Path.home() / "davar"
DATA_DIR = PROJECT_ROOT / "data" / "tth"
RAW_DIR = DATA_DIR / "raw"
TEMP_DIR = DATA_DIR / "temp"
OUTPUT_DIR = DATA_DIR


def show_banner():
    """Show application banner."""
    print("=" * 70)
    print("TTH Processing System - Davar Project")
    print("Textual Translation of Hebrew")
    print("=" * 70)
    print()


def show_help():
    """Show help information."""
    print("""
USAGE:
  python main.py <book_key>              Process book (test mode -> temp/)
  python main.py <book_key> --prod       Process book (production -> data/tth/)
  python main.py run <book_key>          Process book (production)
  python main.py test <book_key>         Process book (test mode)
  python main.py books                   List available books
  python main.py --help                  Show this help

EXAMPLES:
  python main.py amos                    # Test Amos to temp/
  python main.py shemot --prod           # Process Shemot to data/tth/
  python main.py run bereshit            # Process Bereshit to data/tth/
  python main.py test amos               # Test Amos to temp/

AVAILABLE BOOKS:
  Torah: bereshit, shemot, vaikra, bamidbar, devarim
  Prophets: amos, ionah, ieshaiahu, irmeiahu, etc.
  Writings: tehilim, mishlei
  Besorah: matityahu, markos, lukas, iojanan, iehudah, etc.
""")


def get_available_books():
    """Get list of available books."""
    try:
        from processor import TTHProcessor
        return list(TTHProcessor.BOOKS_INFO.keys())
    except ImportError:
        return []


def list_books():
    """List all available books."""
    try:
        from processor import TTHProcessor
        books = TTHProcessor.BOOKS_INFO
        
        print("AVAILABLE BOOKS:")
        print()
        
        # Group by section
        sections = {}
        for book_key, info in books.items():
            section = info.get('section', 'other')
            if section not in sections:
                sections[section] = []
            sections[section].append((book_key, info))
        
        section_names = {
            'torah': 'TORAH (Pentateuch)',
            'neviim': 'NEVIIM (Prophets)',
            'ketuvim': 'KETUVIM (Writings)',
            'besorah': 'BESORAH (New Testament)',
        }
        
        for section in ['torah', 'neviim', 'ketuvim', 'besorah']:
            if section in sections:
                print(f"{section_names.get(section, section.upper())}:")
                for book_key, info in sections[section]:
                    print(f"  {book_key:<20} - {info.get('spanish_name', '')} ({info.get('expected_chapters', '?')} chapters)")
                print()
        
        return 0
    except Exception as e:
        print(f"Error listing books: {e}")
        return 1


def process_book(book_key: str, output_dir: Path, test_mode: bool = True) -> int:
    """
    Process a single book.
    
    Args:
        book_key: Book identifier (e.g., 'amos', 'shemot')
        output_dir: Output directory path
        test_mode: If True, outputs to temp directory
    
    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        from converter import TTHDocxConverter, MAMMOTH_AVAILABLE
        from extractor import TTHBookExtractor
        from processor import TTHProcessor, process_book_to_json
        
        # Check if book exists
        if book_key not in TTHProcessor.BOOKS_INFO:
            print(f"❌ Unknown book: {book_key}")
            print(f"Use 'python main.py books' to see available books")
            return 1
        
        mode_str = "test" if test_mode else "production"
        print(f"Processing '{book_key}' ({mode_str} mode)")
        print(f"Output directory: {output_dir}")
        print()
        
        # Check for existing markdown file first
        markdown_file = RAW_DIR / f"{book_key}.md"
        
        if markdown_file.exists():
            # Process directly from markdown
            print(f"Using existing markdown: {markdown_file}")
            os.makedirs(output_dir, exist_ok=True)
            validation = process_book_to_json(book_key, str(markdown_file), str(output_dir))
            
            if validation.get('chapters_match', False):
                print(f"\n✓ {book_key} processed successfully")
                return 0
            else:
                print(f"\n⚠️ {book_key} processed with issues")
                return 1
        
        # Fall back to DOCX extraction
        if not MAMMOTH_AVAILABLE:
            print("❌ No markdown file found and mammoth library is not installed")
            print("Install with: pip install mammoth")
            return 1
        
        # Get source document
        extractor = TTHBookExtractor()
        docx_file = extractor.get_source_document_path(book_key)
        
        if not Path(docx_file).exists():
            print(f"❌ Source document not found: {docx_file}")
            return 1
        
        print(f"Source: {docx_file}")
        print()
        
        # Convert DOCX to markdown
        print("Converting DOCX to Markdown...")
        import mammoth
        with open(docx_file, 'rb') as f:
            result = mammoth.convert_to_markdown(f)
            markdown_text = result.value
        
        # Normalize markdown
        converter = TTHDocxConverter()
        markdown_text = converter.normalize_footnotes(markdown_text)
        markdown_text = converter.normalize_verse_markers(markdown_text)
        markdown_text = converter.add_missing_verse_1_markers(markdown_text)
        markdown_text = converter.separate_inline_verses(markdown_text)
        markdown_text = converter.clean_html_artifacts(markdown_text)
        
        # Extract book section
        print(f"Extracting book: {book_key}")
        book_text = extractor.extract_book_section(markdown_text, book_key)
        
        # Validate extraction
        validation_result = extractor.validate_book_extraction(book_text, book_key)
        if not validation_result['has_content']:
            print(f"❌ Could not extract content for {book_key}")
            return 1
        
        # Save temporary markdown
        temp_dir = output_dir / 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        temp_md_file = temp_dir / f"{book_key}.md"
        
        with open(temp_md_file, 'w', encoding='utf-8') as f:
            f.write(book_text)
        
        # Process to JSON
        print("Converting to JSON...")
        os.makedirs(output_dir, exist_ok=True)
        validation = process_book_to_json(book_key, str(temp_md_file), str(output_dir))
        
        if validation.get('chapters_match', False):
            print(f"\n✓ {book_key} processed successfully")
            return 0
        else:
            print(f"\n⚠️ {book_key} processed with issues")
            return 1
            
    except Exception as e:
        print(f"❌ Error processing {book_key}: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    show_banner()
    
    # No arguments - show help
    if len(sys.argv) == 1:
        show_help()
        sys.exit(0)
    
    args = sys.argv[1:]
    command = args[0].lower()
    
    # Help
    if command in ['--help', '-h', 'help']:
        show_help()
        sys.exit(0)
    
    # List books
    if command == 'books':
        sys.exit(list_books())
    
    # Commands with sub-arguments
    if command == 'run':
        if len(args) < 2:
            print("Usage: python main.py run <book_key>")
            sys.exit(1)
        book_key = args[1]
        exit_code = process_book(book_key, OUTPUT_DIR, test_mode=False)
        sys.exit(exit_code)
    
    if command == 'test':
        if len(args) < 2:
            print("Usage: python main.py test <book_key>")
            sys.exit(1)
        book_key = args[1]
        exit_code = process_book(book_key, TEMP_DIR, test_mode=True)
        sys.exit(exit_code)
    
    # Direct book name - default to test mode unless --prod flag
    book_key = command
    available_books = get_available_books()
    
    if book_key not in available_books:
        print(f"Unknown command or book: {book_key}")
        print()
        print("Use 'python main.py books' to see available books")
        print("Use 'python main.py --help' for usage information")
        sys.exit(1)
    
    # Check for --prod flag
    production_mode = '--prod' in args or '--production' in args
    
    if production_mode:
        exit_code = process_book(book_key, OUTPUT_DIR, test_mode=False)
    else:
        exit_code = process_book(book_key, TEMP_DIR, test_mode=True)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
