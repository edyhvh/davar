#!/usr/bin/env python3
"""
Find Devárim title
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

    print("Finding Devárim title...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Search for Devárim patterns
    for i, line in enumerate(lines):
        if 'DEVÁRIM' in line.upper() or 'DEUTERONOMIO' in line.upper() or 'דברים' in line:
            print(f"Line {i}: '{line}'")
            if i > 1400 and i < 1600:  # Around where Bamidbar should end
                break

if __name__ == "__main__":
    main()




