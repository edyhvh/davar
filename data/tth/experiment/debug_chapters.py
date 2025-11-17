#!/usr/bin/env python3
"""
Debug script to see why Bereshit stops at chapter 28
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

    print("Converting tanaj.docx to debug chapter detection...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Find Bereshit start
    bereshit_start = -1
    for i, line in enumerate(lines):
        line_upper = line.upper()
        if ('TORAH - BERESHIT' in line_upper or 'בראשית' in line) and '__' in line and '](#' not in line:
            bereshit_start = i
            print(f"Bereshit starts at line {i}: {line.strip()}")
            break

    if bereshit_start == -1:
        print("Bereshit not found")
        return

    # Look for the next book (Shemot/Exodus) - be more specific
    next_book_line = -1
    for i in range(bereshit_start + 1, len(lines)):
        line = lines[i].strip()
        line_upper = line.upper()

        if len(line) < 200 and line:
            # Check for Shemot/Exodus - look for the main title pattern like Bereshit
            if ('TORAH - SHEMOT' in line_upper and '__' in line) or \
               ('SHEMOT' in line_upper and 'ÉXODO' in line_upper and '__' in line) or \
               ('שמות' in line and '__' in line):
                # Make sure it's not a TOC link and not just a subtitle
                if '](#' not in line and not line.startswith('*'):
                    next_book_line = i
                    print(f"Next book (Shemot) found at line {i}: {line}")
                    break

    # Show what we found and check context
    if next_book_line != -1:
        print(f"\nChecking context around line {next_book_line}:")
        start = max(0, next_book_line - 5)
        end = min(len(lines), next_book_line + 10)
        for i in range(start, end):
            marker = " --> " if i == next_book_line else "     "
            print(f"     {marker}{i:4d}: {lines[i]}")
        print(f"Bereshit would end at line {next_book_line}")
        print(f"That's {next_book_line - bereshit_start} lines after start")
    else:
        print("Next book not found within reasonable range")
        # Look for chapter 29-50 content
        chapters_found = []
        for i in range(bereshit_start, min(bereshit_start + 2000, len(lines))):
            line = lines[i]
            # Look for chapter patterns
            if '__' in line and any(f'__{ch}__' in line for ch in range(29, 51)):
                chapters_found.append((i, line.strip()))
                if len(chapters_found) >= 5:  # Show first 5
                    break

        print(f"Chapters 29-50 found: {len(chapters_found)}")
        for line_num, content in chapters_found:
            print(f"Line {line_num}: {content}")

        # Check what comes after Bereshit content
        print("\nChecking content around where Bereshit should end...")
        check_start = bereshit_start + 1500  # Roughly where chapter 28 should be
        for i in range(check_start, min(check_start + 50, len(lines))):
            if lines[i].strip():
                print(f"Line {i}: {lines[i]}")
                if i - check_start >= 10:  # Show 10 lines
                    break

if __name__ == "__main__":
    main()
