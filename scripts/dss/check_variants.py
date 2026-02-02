#!/usr/bin/env python3
"""
Check if all variants in dss.json are present in the books/ directory files.

This script compares the curated variants in dss.json with the comprehensive
data in the books/ directory to verify completeness.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple


def load_dss_json(file_path: Path) -> Dict:
    """Load the dss.json file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_book_json(file_path: Path) -> Dict:
    """Load a book JSON file from books/ directory."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_variants(dss_data: Dict, books_dir: Path) -> List[Dict]:
    """
    Check if variants from dss.json exist in books/ directory.
    
    Returns a list of results for each variant checked.
    """
    results = []
    
    # Map book names in dss.json to files in books/
    book_name_map = {
        'isaiah': 'isaiah.json',
        'samuel_1': '1samuel.json',  # assuming this is the name
        'samuel_2': '2samuel.json'
    }
    
    books = dss_data.get('books', {})
    
    for book_key, book_data in books.items():
        book_file = book_name_map.get(book_key)
        if not book_file:
            results.append({
                'book': book_key,
                'status': 'unmapped',
                'message': f'No file mapping for {book_key}'
            })
            continue
        
        book_path = books_dir / book_file
        if not book_path.exists():
            results.append({
                'book': book_key,
                'status': 'missing_file',
                'message': f'File not found: {book_file}'
            })
            continue
        
        # Load the book file
        book_json = load_book_json(book_path)
        book_chapters = book_json.get('chapters', {})
        
        # Check each chapter and verse in dss.json
        chapters = book_data.get('chapters', {})
        for chapter_num, chapter_data in chapters.items():
            verses = chapter_data.get('verses', {})
            
            for verse_nums, verse_data in verses.items():
                # Parse verse numbers (could be "8" or "26-11:3" or "22-23")
                verse_list = parse_verse_reference(verse_nums)
                
                for verse_num in verse_list:
                    # Check if chapter exists
                    if chapter_num not in book_chapters:
                        results.append({
                            'book': book_key,
                            'chapter': chapter_num,
                            'verse': verse_num,
                            'status': 'missing_chapter',
                            'message': f'Chapter {chapter_num} not found in {book_file}'
                        })
                        continue
                    
                    # Check if verse exists
                    chapter_verses = book_chapters[chapter_num].get('verses', {})
                    if verse_num not in chapter_verses:
                        results.append({
                            'book': book_key,
                            'chapter': chapter_num,
                            'verse': verse_num,
                            'status': 'missing_verse',
                            'message': f'{book_key} {chapter_num}:{verse_num} not found in {book_file}'
                        })
                    else:
                        # Verse exists - check if it has differences
                        verse_obj = chapter_verses[verse_num]
                        has_differences = bool(verse_obj.get('differences', []))
                        
                        results.append({
                            'book': book_key,
                            'chapter': chapter_num,
                            'verse': verse_num,
                            'status': 'found' if has_differences else 'found_no_diffs',
                            'message': f'{book_key} {chapter_num}:{verse_num} ✓',
                            'has_differences': has_differences,
                            'diff_count': len(verse_obj.get('differences', []))
                        })
    
    return results


def parse_verse_reference(verse_ref: str) -> List[str]:
    """
    Parse verse reference string into list of verse numbers.
    
    Examples:
        "8" -> ["8"]
        "22-23" -> ["22", "23"]
        "26-11:3" -> ["26"]  # Complex spanning reference
    """
    # Handle complex references like "26-11:3"
    if '-' in verse_ref and ':' in verse_ref:
        # Just take the first verse
        return [verse_ref.split('-')[0]]
    
    # Handle simple ranges like "22-23"
    if '-' in verse_ref:
        parts = verse_ref.split('-')
        start = int(parts[0])
        end = int(parts[1])
        return [str(v) for v in range(start, end + 1)]
    
    # Single verse
    return [verse_ref]


def print_summary(results: List[Dict]):
    """Print a summary of the results."""
    total = len(results)
    found = sum(1 for r in results if r['status'] == 'found')
    found_no_diffs = sum(1 for r in results if r['status'] == 'found_no_diffs')
    missing_verse = sum(1 for r in results if r['status'] == 'missing_verse')
    missing_chapter = sum(1 for r in results if r['status'] == 'missing_chapter')
    missing_file = sum(1 for r in results if r['status'] == 'missing_file')
    unmapped = sum(1 for r in results if r['status'] == 'unmapped')
    
    print("\n" + "="*70)
    print("DSS VARIANT VERIFICATION SUMMARY")
    print("="*70)
    print(f"\nTotal variants checked: {total}")
    print(f"  ✓ Found with differences: {found}")
    print(f"  ⚠ Found but no differences: {found_no_diffs}")
    print(f"  ✗ Missing verse: {missing_verse}")
    print(f"  ✗ Missing chapter: {missing_chapter}")
    print(f"  ✗ Missing book file: {missing_file}")
    print(f"  ? Unmapped: {unmapped}")
    
    # Print details of issues
    issues = [r for r in results if r['status'] not in ['found', 'found_no_diffs']]
    if issues:
        print("\n" + "="*70)
        print("ISSUES FOUND")
        print("="*70)
        for issue in issues:
            book = issue.get('book', '')
            chapter = issue.get('chapter', '')
            verse = issue.get('verse', '')
            status = issue['status']
            message = issue['message']
            
            if chapter and verse:
                print(f"  [{status}] {book} {chapter}:{verse}")
            else:
                print(f"  [{status}] {message}")
    
    # Print found verses with difference counts
    found_verses = [r for r in results if r['status'] == 'found']
    if found_verses:
        print("\n" + "="*70)
        print("VERIFIED VARIANTS")
        print("="*70)
        for item in found_verses:
            book = item['book']
            chapter = item['chapter']
            verse = item['verse']
            diff_count = item.get('diff_count', 0)
            print(f"  ✓ {book} {chapter}:{verse} ({diff_count} difference(s))")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    dss_json_path = project_root / 'data' / 'dss' / 'dss.json'
    books_dir = project_root / 'data' / 'dss' / 'books'
    
    if not dss_json_path.exists():
        print(f"Error: dss.json not found at {dss_json_path}")
        return 1
    
    if not books_dir.exists():
        print(f"Error: books directory not found at {books_dir}")
        return 1
    
    print("Loading dss.json...")
    dss_data = load_dss_json(dss_json_path)
    
    print("Checking variants against books/ directory...")
    results = check_variants(dss_data, books_dir)
    
    print_summary(results)
    
    return 0


if __name__ == '__main__':
    exit(main())
