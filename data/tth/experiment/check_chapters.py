#!/usr/bin/env python3
"""
Check if chapters 29-50 exist in Bereshit
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

    print("Checking for chapters 29-50 in the document...")

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
            print(f"Bereshit starts at line {i}")
            break

    if bereshit_start == -1:
        print("Bereshit not found")
        return

    # Find the actual end of Bereshit (where Shemot starts)
    shemot_start = -1
    for i in range(bereshit_start + 1, len(lines)):
        line_upper = lines[i].upper()
        if ('TORAH - SHEMOT' in line_upper or 'SHEMOT' in line_upper or
            'ÉXODO' in line_upper or 'שמות' in line) and '__' in lines[i]:
            shemot_start = i
            print(f"Shemot starts at line {i}")
            break

    if shemot_start == -1:
        print("Shemot not found")
        shemot_start = len(lines)

    # Search for chapters 29-50 within Bereshit boundaries
    chapters_29_50 = {}
    for ch in range(29, 51):
        for i in range(bereshit_start, shemot_start):
            line = lines[i]
            if f'__{ch}__' in line:
                chapters_29_50[ch] = i
                break

    print(f"\nChapters 29-50 found in Bereshit section: {len(chapters_29_50)}")
    for ch, line_num in sorted(chapters_29_50.items()):
        print(f"Chapter {ch}: line {line_num}")

    # Check what happens at the end of Bereshit
    print("\nContent around the end of Bereshit:")
    start_check = max(bereshit_start, shemot_start - 20)
    for i in range(start_check, min(shemot_start + 5, len(lines))):
        if lines[i].strip():
            marker = " --> " if i == shemot_start else "     "
            print(f"     {marker}{i:4d}: {lines[i]}")

if __name__ == "__main__":
    main()
