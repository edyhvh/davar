#!/usr/bin/env python3
"""
Debug verse processing in Shemot
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

    print("Debugging verse processing in Shemot...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Find Shemot start
    shemot_start = -1
    for i, line in enumerate(lines):
        if line.strip() == '__SHEMOT \\(ÉXODO\\)__ שמות':
            shemot_start = i
            print(f"Found Shemot start at line {i}")
            break

    if shemot_start == -1:
        print("Shemot start not found")
        return

    # Find first few chapters in Shemot
    print("\nFirst 10 lines after Shemot start:")
    for i in range(shemot_start, min(shemot_start + 10, len(lines))):
        line = lines[i]
        print(f"Line {i}: '{line}'")

    # Look for chapter markers and what follows
    print("\nLooking for chapter markers in Shemot:")
    current_line = shemot_start
    while current_line < len(lines):
        line = lines[current_line]
        if re.match(r'^__\d+__$', line):
            chapter_num = int(re.match(r'^__(\d+)__$', line).group(1))
            print(f"\nFound chapter {chapter_num} at line {current_line}: '{line}'")

            # Check next few lines
            for j in range(1, 5):
                if current_line + j < len(lines):
                    next_line = lines[current_line + j]
                    verse_num = extract_verse_num(next_line)
                    print(f"  Line {current_line + j}: '{next_line[:100]}...' (verse_num: {verse_num})")
                    if next_line.strip() and verse_num == 0 and not re.match(r'^__\d+__$', next_line):
                        break
            break  # Just check first chapter for now
        current_line += 1

if __name__ == "__main__":
    main()




