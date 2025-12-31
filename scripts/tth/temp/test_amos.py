#!/usr/bin/env python3
"""
Test script to process amos.md with the modified processor.

This script tests the text cleaner integration by processing
the Amos book and comparing the output.

Usage:
    cd scripts/tth/temp
    python test_amos.py
"""

import os
import sys
import json

# Import from local (temp) processor, not the parent one
from processor import TTHProcessor, process_book_to_json


def test_amos_processing():
    """Test processing of Amos with modified processor."""
    print("=" * 70)
    print("TTH Processing Test - Amos with Text Cleaner")
    print("=" * 70)
    print()
    
    # Paths
    markdown_file = '../../../data/tth/tanaj/amos.md'
    output_dir = '../../../data/tth/temp/'
    
    # Check if markdown file exists
    if not os.path.exists(markdown_file):
        print(f"❌ Error: Markdown file not found: {markdown_file}")
        return 1
    
    print(f"Input:  {markdown_file}")
    print(f"Output: {output_dir}")
    print()
    
    # Process the book
    try:
        validation = process_book_to_json('amos', markdown_file, output_dir)
        
        # Check some specific verses for the fixes
        output_file = os.path.join(output_dir, 'amos.json')
        
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("\n" + "=" * 70)
            print("VERIFICATION OF SPECIFIC FIXES")
            print("=" * 70)
            
            verses = data.get('verses', [])
            
            # Check verse 1:1 for "Israel" (was "Is\-rael")
            verse_1_1 = next((v for v in verses if v['chapter'] == 1 and v['verse'] == 1), None)
            if verse_1_1:
                text = verse_1_1.get('tth', '')
                has_israel = 'Israel' in text
                has_bad_israel = 'Is\\-rael' in text or 'Is-rael' in text
                print(f"\n1. Soft hyphen fix (Is\\-rael -> Israel):")
                print(f"   Verse 1:1 contains 'Israel': {'✓' if has_israel else '✗'}")
                print(f"   Verse 1:1 has broken 'Is-rael': {'✗ (bad)' if has_bad_israel else '✓ (good)'}")
                
            # Check verse 1:2 for spacing after colon
            verse_1_2 = next((v for v in verses if v['chapter'] == 1 and v['verse'] == 2), None)
            if verse_1_2:
                text = verse_1_2.get('tth', '')
                # Check for "dijo: יהוה" (with space) vs "dijo:יהוה" (without)
                has_proper_spacing = ': יהוה' in text or ': ' in text
                has_bad_spacing = ':יהוה' in text
                print(f"\n2. Punctuation spacing fix (dijo:יהוה -> dijo: יהוה):")
                print(f"   Has proper spacing after colon: {'✓' if has_proper_spacing else '?'}")
                print(f"   Has stuck punctuation: {'✗ (bad)' if has_bad_spacing else '✓ (good)'}")
            
            # Check verse 1:8 for "Ashdod y" (was "Ashdody")
            verse_1_8 = next((v for v in verses if v['chapter'] == 1 and v['verse'] == 8), None)
            if verse_1_8:
                text = verse_1_8.get('tth', '')
                has_ashdod_y = 'Ashdod y' in text
                has_ashdody = 'Ashdody' in text
                print(f"\n3. Stuck connector fix (Ashdody -> Ashdod y):")
                print(f"   Has 'Ashdod y': {'✓' if has_ashdod_y else '✗'}")
                print(f"   Has stuck 'Ashdody': {'✗ (bad)' if has_ashdody else '✓ (good)'}")
            
            print("\n" + "=" * 70)
            print("Sample of first 3 verses:")
            print("=" * 70)
            for verse in verses[:3]:
                ch = verse['chapter']
                v = verse['verse']
                text = verse.get('tth', '')[:100] + '...' if len(verse.get('tth', '')) > 100 else verse.get('tth', '')
                print(f"\n{ch}:{v} - {text}")
            
        return 0 if validation.get('chapters_match') else 1
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = test_amos_processing()
    sys.exit(exit_code)

