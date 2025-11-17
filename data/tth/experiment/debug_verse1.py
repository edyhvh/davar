#!/usr/bin/env python3
"""
Debug verse 1 marking
"""

import sys
import os
import re

try:
    import mammoth
except ImportError:
    print("Error: The 'mammoth' library is not installed.")
    sys.exit(1)

def extract_verse_num(line: str) -> int:
    """Extract verse number from a line, return 0 if no verse marker found."""
    # Look for patterns like __1__, __2__, etc. at the beginning of the line
    verse_match = re.match(r'^__(\d+)__', line)
    if verse_match:
        return int(verse_match.group(1))
    return 0

def main():
    input_file = "../tanaj.docx"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print("Debugging verse 1 marking...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Find bereshit start
    bereshit_start = -1
    for i, line in enumerate(lines):
        if 'TORAH' in line.upper() and 'BERESHIT' in line.upper():
            bereshit_start = i
            break

    if bereshit_start == -1:
        print("Bereshit start not found")
        return

    # Find shemot (end of bereshit)
    bereshit_end = -1
    for i in range(bereshit_start + 1, len(lines)):
        line = lines[i]
        if line.strip() == '__SHEMOT \\(ÉXODO\\)__ שמות':
            bereshit_end = i
            break

    if bereshit_end == -1:
        print("Bereshit end not found")
        return

    print(f"Bereshit section: lines {bereshit_start} to {bereshit_end}")

    # Extract bereshit lines
    bereshit_lines = lines[bereshit_start:bereshit_end]

    # Find chapter 29 and what comes after
    for i, line in enumerate(bereshit_lines):
        if line.strip() == '__29__':
            print(f"Found __29__ at line {i} in bereshit section")
            print(f"Line {i}: '{line}'")
            if i + 1 < len(bereshit_lines):
                print(f"Line {i+1}: '{bereshit_lines[i+1]}'")
            if i + 2 < len(bereshit_lines):
                print(f"Line {i+2}: '{bereshit_lines[i+2]}'")
                verse_num = extract_verse_num(bereshit_lines[i+2])
                print(f"Verse num for line {i+2}: {verse_num}")
            break

if __name__ == "__main__":
    main()




