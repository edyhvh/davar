#!/usr/bin/env python3
"""
Find Bamidbar title
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

    print("Finding Bamidbar title...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Search for Bamidbar patterns
    for i, line in enumerate(lines):
        if 'BAMIDBAR' in line.upper() or 'NÚMEROS' in line.upper() or 'במדבר' in line:
            print(f"Line {i}: '{line}'")
            if i > 1000 and i < 1500:  # Around where Vaikrá should end
                break

if __name__ == "__main__":
    main()




