#!/usr/bin/env python3
"""
Debug script to see raw footnote content before processing
"""

import sys
import os
import re

try:
    import mammoth
except ImportError:
    print("Error: The 'mammoth' library is not installed.")
    sys.exit(1)

def main():
    input_file = "../tanaj.docx"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print("Converting tanaj.docx to see raw footnote content...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Look for footnote-related content
    footnote_patterns = [
        r'<a[^>]*footnote[^>]*>.*?</a>',
        r'\[\^\d+\]',
        r'\[\[\d+\]\]',
        r'#footnote-\d+',
        r'footnote-ref-\d+'
    ]

    found_patterns = {}
    for pattern in footnote_patterns:
        matches = []
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                matches.append(i)
        found_patterns[pattern] = matches
        print(f"Pattern '{pattern}': {len(matches)} matches")

    # Show some examples
    for pattern, line_nums in found_patterns.items():
        if line_nums:
            print(f"\nExamples for pattern '{pattern}':")
            for i in range(min(3, len(line_nums))):
                line_num = line_nums[i]
                print(f"Line {line_num}: {lines[line_num]}")

    # Look for Bereshit content and check for footnotes nearby
    bereshit_start = -1
    for i, line in enumerate(lines):
        if ('TORAH - BERESHIT' in line.upper() or 'בראשית' in line) and '__' in line and '](#' not in line:
            bereshit_start = i
            break

    if bereshit_start != -1:
        print(f"\nBereshit starts at line {bereshit_start}")
        # Check for footnote patterns in Bereshit area
        bereshit_lines = lines[bereshit_start:bereshit_start+100]  # First 100 lines of Bereshit
        footnote_refs = []
        for i, line in enumerate(bereshit_lines):
            if re.search(r'\[\^\d+\]', line):
                footnote_refs.append((bereshit_start + i, line))

        print(f"Footnote references in first 100 lines of Bereshit: {len(footnote_refs)}")
        for line_num, content in footnote_refs[:5]:
            print(f"Line {line_num}: {content}")

if __name__ == "__main__":
    main()













