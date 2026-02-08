#!/usr/bin/env python3
"""
Split Isaiah DSSI file into multiple smaller JSON files.

This script takes the large isaiah.json file and splits it into ~20 smaller
files for easier processing, maintaining proper JSON structure and order.
"""

import json
import math
from pathlib import Path


def split_isaiah_by_differences(
    input_file: Path,
    output_dir: Path,
    target_files: int = 40
):
    """
    Split Isaiah JSON file into multiple files based on verse differences.
    
    Args:
        input_file: Path to the input isaiah.json file
        output_dir: Directory to save the split files
        target_files: Target number of output files (default: 40)
    """
    # Read the input file
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    book_name = data.get('name', 'Isaiah')
    chapters = data.get('chapters', {})
    
    # Count total differences
    all_differences = []
    for chapter_num, chapter_data in chapters.items():
        verses = chapter_data.get('verses', {})
        for verse_num, verse_data in verses.items():
            differences = verse_data.get('differences', [])
            for diff in differences:
                all_differences.append({
                    'chapter': chapter_num,
                    'verse': verse_num,
                    'verse_data': verse_data,
                    'difference': diff
                })
    
    total_differences = len(all_differences)
    print(f"Found {total_differences} total differences across {len(chapters)} chapters")
    
    # Calculate differences per file
    diffs_per_file = math.ceil(total_differences / target_files)
    print(f"Splitting into ~{target_files} files with ~{diffs_per_file} differences each")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Split into files
    file_num = 1
    current_batch = []
    current_structure = {}
    
    for i, item in enumerate(all_differences):
        chapter = item['chapter']
        verse = item['verse']
        
        # Initialize structure if needed
        if chapter not in current_structure:
            current_structure[chapter] = {}
        if verse not in current_structure[chapter]:
            current_structure[chapter][verse] = {
                'masoretic_text': item['verse_data'].get('masoretic_text', ''),
                'dss_text': item['verse_data'].get('dss_text', ''),
                'differences': []
            }
        
        # Add difference to current batch
        current_structure[chapter][verse]['differences'].append(item['difference'])
        current_batch.append(item)
        
        # Check if we should write this batch
        should_write = (
            len(current_batch) >= diffs_per_file and 
            file_num < target_files
        ) or (i == total_differences - 1)
        
        if should_write:
            # Create output file structure
            output_data = {
                'name': book_name,
                'file_number': file_num,
                'total_files': target_files,
                'difference_count': len(current_batch),
                'chapters': {}
            }
            
            # Build chapters structure
            for ch_num in sorted(current_structure.keys(), key=lambda x: int(x)):
                output_data['chapters'][ch_num] = {
                    'verses': {}
                }
                for v_num in sorted(current_structure[ch_num].keys(), key=lambda x: int(x)):
                    output_data['chapters'][ch_num]['verses'][v_num] = current_structure[ch_num][v_num]
            
            # Write to file
            output_file = output_dir / f'isaiah_{file_num:03d}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ Created {output_file.name}: {len(current_batch)} differences "
                  f"(chapters {min(current_structure.keys(), key=lambda x: int(x))}-"
                  f"{max(current_structure.keys(), key=lambda x: int(x))})")
            
            # Reset for next batch
            file_num += 1
            current_batch = []
            current_structure = {}
    
    print(f"\n✓ Successfully split into {file_num - 1} files in {output_dir}")
    return file_num - 1


def main():
    """Main entry point."""
    # Define paths
    project_root = Path(__file__).parent.parent.parent
    input_file = project_root / 'data' / 'dss' / 'dssi' / 'books' / 'isaiah.json'
    output_dir = project_root / 'data' / 'dss' / 'dssi' / 'books' / 'isaiah'
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return 1
    
    try:
        num_files = split_isaiah_by_differences(
            input_file=input_file,
            output_dir=output_dir,
            target_files=40
        )
        print(f"\n✓ Isaiah file successfully split into {num_files} parts")
        return 0
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
