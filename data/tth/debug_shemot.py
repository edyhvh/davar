#!/usr/bin/env python3
"""
Debug script to see the exact Shemot title
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

    print("Finding Shemot title...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Find Shemot
    for i in range(650, 660):  # Around line 653
        if i < len(lines):
            line = lines[i].strip()
            if 'SHEMOT' in line.upper() or 'ÉXODO' in line.upper():
                print(f"Line {i}: '{line}'")
                print(f"Upper: '{line.upper()}'")
                print(f"Has '__': {'__' in line}")
                break

if __name__ == "__main__":
    main()





