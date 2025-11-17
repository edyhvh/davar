#!/usr/bin/env python3
"""
Simple debug script to see Bereshit content
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

    print(f"Converting '{input_file}'...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    markdown_text = result.value
    lines = markdown_text.split('\n')

    print(f"Total lines in document: {len(lines)}")

    # Find all Bereshit occurrences
    bereshit_lines = []
    for i, line in enumerate(lines):
        line_upper = line.upper()
        if 'BERESHIT' in line_upper or 'בראשית' in line:
            bereshit_lines.append((i, line.strip()))

    print(f"Found {len(bereshit_lines)} Bereshit occurrences:")
    for i, (line_num, content) in enumerate(bereshit_lines[:10]):  # Show first 10
        print(f"{i+1:2d}. Line {line_num:4d}: '{content}'")

        # Show context for each
        start = max(0, line_num - 2)
        end = min(len(lines), line_num + 3)
        print("     Context:")
        for j in range(start, end):
            marker = " --> " if j == line_num else "     "
            print(f"     {marker}{j:4d}: '{lines[j]}'")
        print()

    if not bereshit_lines:
        print("No Bereshit occurrences found!")

        # Show first 50 lines to see structure
        print("First 50 lines of document:")
        for i in range(min(50, len(lines))):
            if lines[i].strip():
                print(f"{i:2d}: '{lines[i]}'")

if __name__ == "__main__":
    main()
