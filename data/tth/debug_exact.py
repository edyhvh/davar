#!/usr/bin/env python3
"""
Debug exact line matching
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

    print("Checking exact line matching...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Check line 653
    if 653 < len(lines):
        line = lines[653]
        print(f"Line 653: '{line}'")
        print(f"Line 653 stripped: '{line.strip()}'")
        print(f"'__SHEMOT' in line: {'__SHEMOT' in line}")
        print(f"'ÉXODO' in line: {'ÉXODO' in line}")
        print(f"'שמות' in line: {'שמות' in line}")
        print(f"line.strip() == '__SHEMOT (ÉXODO)__ שמות': {line.strip() == '__SHEMOT (ÉXODO)__ שמות'}")

    # Look for the exact pattern anywhere
    target = '__SHEMOT (ÉXODO)__ שמות'
    for i, line in enumerate(lines):
        if target in line:
            print(f"Found target at line {i}: '{line}'")

if __name__ == "__main__":
    main()




