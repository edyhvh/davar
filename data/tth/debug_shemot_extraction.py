#!/usr/bin/env python3
"""
Debug Shemot extraction
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

    print("Debugging Shemot extraction...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Find Shemot start
    shemot_start = -1
    for i, line in enumerate(lines):
        if ('__SHEMOT' in line and 'ÉXODO' in line and 'שמות' in line and
            line.strip() == '__SHEMOT \\(ÉXODO\\)__ שמות'):
            shemot_start = i
            print(f"Found Shemot start at line {i}: '{line}'")
            break

    if shemot_start == -1:
        print("Shemot start not found")
        return

    # Look for Vaikrá (next book)
    print("\nLooking for Vaikrá...")
    vaikra_found = False
    for i in range(shemot_start + 1, min(shemot_start + 100, len(lines))):
        line = lines[i]
        if '__VAIKRÁ' in line or '__LEVÍTICO' in line or '__ויקרא' in line:
            print(f"Line {i}: '{line}'")
            if line.strip() == '__VAIKRÁ \\(LEVÍTICO\\)__ ויקרא':
                print(f"Found Vaikrá at line {i}")
                vaikra_found = True
                break

    if not vaikra_found:
        print("Vaikrá not found in first 100 lines after Shemot")

    # Check what comes after Shemot start
    print(f"\nContent after Shemot start (lines {shemot_start} to {min(shemot_start + 10, len(lines))}):")
    for i in range(shemot_start, min(shemot_start + 10, len(lines))):
        print(f"Line {i}: '{lines[i]}'")

    # Look for footnotes
    print("\nLooking for footnotes after line 650:")
    for i in range(650, min(670, len(lines))):
        line = lines[i]
        if re.match(r'\[\^\d+\]:', line) or '<a id="footnote-' in line:
            print(f"Line {i}: '{line}'")
            break

if __name__ == "__main__":
    main()
