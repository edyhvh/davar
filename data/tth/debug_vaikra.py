#!/usr/bin/env python3
"""
Find Vaikrá title
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

    print("Finding Vaikrá title...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Search for Vaikrá patterns
    for i, line in enumerate(lines):
        if 'VAIKRÁ' in line.upper() or 'LEVÍTICO' in line.upper() or 'ויקרא' in line:
            print(f"Line {i}: '{line}'")

if __name__ == "__main__":
    main()




