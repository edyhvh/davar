#!/usr/bin/env python3
"""
Merge split Isaiah DSSI files into one isaiah.json file.

This script reads all isaiah_*.json files from data/dss/books/isaiah/ directory
and merges them into a single isaiah.json file in data/dss/books/ directory,
following the same format as other book files (removing file_number, total_files, etc.).
"""

import json
from pathlib import Path
from typing import Dict, Any


def merge_isaiah_files(
    input_dir: Path,
    output_file: Path
) -> int:
    """
    Merge all isaiah_*.json files into one unified book file.
    
    Args:
        input_dir: Directory containing isaiah_*.json files
        output_file: Path to output merged isaiah.json file
    
    Returns:
        Number of files merged
    """
    # Find all isaiah_*.json files and sort them numerically
    isaiah_files = sorted(
        input_dir.glob('isaiah_*.json'),
        key=lambda p: int(p.stem.split('_')[1])
    )
    
    if not isaiah_files:
        raise FileNotFoundError(f"No isaiah_*.json files found in {input_dir}")
    
    print(f"Found {len(isaiah_files)} Isaiah files to merge")
    
    # Initialize merged structure
    merged_data: Dict[str, Any] = {
        'name': 'Isaiah',
        'chapters': {}
    }
    
    total_differences = 0
    
    # Process each file
    for file_path in isaiah_files:
        print(f"  Processing {file_path.name}...", end=' ')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
        
        file_diff_count = file_data.get('difference_count', 0)
        total_differences += file_diff_count
        
        # Merge chapters
        chapters = file_data.get('chapters', {})
        for chapter_num, chapter_data in chapters.items():
            # Initialize chapter if not exists
            if chapter_num not in merged_data['chapters']:
                merged_data['chapters'][chapter_num] = {'verses': {}}
            
            # Merge verses
            verses = chapter_data.get('verses', {})
            for verse_num, verse_data in verses.items():
                # If verse already exists, merge differences
                if verse_num in merged_data['chapters'][chapter_num]['verses']:
                    existing_verse = merged_data['chapters'][chapter_num]['verses'][verse_num]
                    existing_verse['differences'].extend(verse_data.get('differences', []))
                else:
                    # Add new verse
                    merged_data['chapters'][chapter_num]['verses'][verse_num] = {
                        'masoretic_text': verse_data.get('masoretic_text', ''),
                        'dss_text': verse_data.get('dss_text', ''),
                        'differences': verse_data.get('differences', [])
                    }
        
        print(f"✓ ({file_diff_count} differences)")
    
    # Sort chapters and verses numerically
    sorted_chapters: Dict[str, Any] = {}
    for chapter_num in sorted(merged_data['chapters'].keys(), key=int):
        chapter_data = merged_data['chapters'][chapter_num]
        sorted_verses: Dict[str, Any] = {}
        
        for verse_num in sorted(chapter_data['verses'].keys(), key=int):
            sorted_verses[verse_num] = chapter_data['verses'][verse_num]
        
        sorted_chapters[chapter_num] = {'verses': sorted_verses}
    
    merged_data['chapters'] = sorted_chapters
    
    # Write merged file
    print(f"\nWriting merged file to {output_file}...")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Successfully merged {len(isaiah_files)} files")
    print(f"  Total chapters: {len(merged_data['chapters'])}")
    print(f"  Total differences: {total_differences}")
    
    return len(isaiah_files)


def main():
    """Main entry point."""
    # Define paths
    project_root = Path(__file__).parent.parent.parent
    input_dir = project_root / 'data' / 'dss' / 'books' / 'isaiah'
    output_file = project_root / 'data' / 'dss' / 'books' / 'isaiah.json'
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1
    
    try:
        num_files = merge_isaiah_files(
            input_dir=input_dir,
            output_file=output_file
        )
        print(f"\n✓ Isaiah files successfully merged into {output_file.name}")
        print(f"  Merged {num_files} files into one")
        return 0
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
