#!/usr/bin/env python3
"""
Find footnote definitions in the document
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

    print("Finding footnote definitions...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Look for footnote definitions
    footnote_defs = []
    for i, line in enumerate(lines):
        # Look for patterns like [^1]: or <a id="footnote-1"></a>
        if re.match(r'\[\^\d+\]:', line) or 'footnote-' in line:
            footnote_defs.append((i, line.strip()))

    print(f"Found {len(footnote_defs)} potential footnote definition lines")

    # Show first 10
    print("\nFirst 10 footnote definition lines:")
    for i, (line_num, content) in enumerate(footnote_defs[:10]):
        print(f"{i+1:2d}. Line {line_num:5d}: '{content}'")

    # Look specifically for footnote definition pattern
    footnote_def_pattern = r'\[\^\d+\]:'
    def_lines = [i for i, line in enumerate(lines) if re.match(footnote_def_pattern, line)]

    print(f"\nFound {len(def_lines)} lines matching footnote definition pattern {footnote_def_pattern}")

    if def_lines:
        print("Footnote definitions found at lines:", def_lines[:10])
        for line_num in def_lines[:5]:
            print(f"Line {line_num}: {lines[line_num]}")

if __name__ == "__main__":
    main()













