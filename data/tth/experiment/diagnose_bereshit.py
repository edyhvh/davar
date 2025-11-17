#!/usr/bin/env python3
"""
Diagnostic script to examine the Bereshit section in tanaj.docx
"""

import sys
import os
import re

try:
    import mammoth
except ImportError:
    print("Error: The 'mammoth' library is not installed.")
    print("Install it with: pip install mammoth")
    sys.exit(1)

def main():
    input_file = "../tanaj.docx"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print(f"Converting '{input_file}' for diagnosis...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    markdown_text = result.value
    lines = markdown_text.split('\n')

    # Find Bereshit start
    bereshit_start = -1
    for i, line in enumerate(lines):
        line_upper = line.upper()
        if ('TORAH - BERESHIT' in line_upper or 'BERESHIT' in line_upper) and len(line.strip()) < 100:
            bereshit_start = i
            print(f"Found Bereshit title at line {i}: {line.strip()}")
            break

    if bereshit_start == -1:
        print("Bereshit not found!")
        return

    # Show next 20 lines after Bereshit title
    print(f"\nNext 20 lines after Bereshit title:")
    for i in range(bereshit_start, min(bereshit_start + 20, len(lines))):
        print(f"{i:2d}: {lines[i]}")

    # Look for the next book
    print("\nLooking for next book...")
    book_keywords = [
        'TORAH - SHEMOT', 'SHEMOT', 'ÉXODO', 'שמות',
        'TORAH - VAIKRÁ', 'VAIKRÁ', 'LEVÍTICO', 'ויקרא',
        'TORAH - BAMIDBAR', 'BAMIDBAR', 'NÚMEROS', 'במדבר',
        'TORAH - DEVARIM', 'DEVARIM', 'DEUTERONOMIO', 'דברים'
    ]

    next_book_line = -1
    for i in range(bereshit_start + 1, len(lines)):
        line = lines[i].strip()
        line_upper = line.upper()

        if len(line) < 100 and line:
            for keyword in book_keywords:
                if keyword in line_upper:
                    next_book_line = i
                    print(f"Found next book at line {i}: {line}")
                    break
            if next_book_line != -1:
                break

    if next_book_line == -1:
        print("Next book not found within first 100 lines after Bereshit")

    # Show lines between Bereshit and next book (or first 50 lines)
    end_line = min(next_book_line if next_book_line != -1 else bereshit_start + 50, len(lines))
    print(f"\nContent between Bereshit and next book (lines {bereshit_start+1} to {end_line}):")
    for i in range(bereshit_start + 1, end_line):
        if lines[i].strip():
            print(f"{i:2d}: {lines[i]}")

if __name__ == "__main__":
    main()
