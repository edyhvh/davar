#!/usr/bin/env python3
"""
Find what comes after Devárim
"""

import sys
import os

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

    print("Finding what comes after Devárim...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Find Devárim start
    devarim_start = -1
    for i, line in enumerate(lines):
        if line.strip() == '__DEVARIM \\(DEUTERONOMIO\\)__ דברים':
            devarim_start = i
            print(f"Found Devárim start at line {i}")
            break

    if devarim_start == -1:
        print("Devárim start not found")
        return

    # Look for what comes after Devárim (around 500-700 lines after start, where Devárim should end)
    print(f"\nLooking for content after Devárim (lines {devarim_start + 500} to {devarim_start + 700}):")
    for i in range(devarim_start + 500, min(devarim_start + 700, len(lines))):
        line = lines[i]
        if '__' in line and ('IEHOSHÚA' in line.upper() or 'JOSUÉ' in line.upper() or
                            'SHOFTÍM' in line.upper() or 'JUECES' in line.upper() or
                            'TEHILIM' in line.upper() or 'SALMOS' in line.upper()):
            print(f"Line {i}: '{line}'")
            break
        elif (i - devarim_start) % 100 == 0:  # Print every 100 lines to see progress
            print(f"Line {i} (offset {i - devarim_start}): '{line[:50]}...'")

if __name__ == "__main__":
    main()
