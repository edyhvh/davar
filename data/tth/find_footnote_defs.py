#!/usr/bin/env python3
"""
Find footnote definitions at the end of the document
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

    print("Looking for footnote definitions at the end of the document...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Look at the last 1000 lines for footnote definitions
    last_1000 = lines[-1000:] if len(lines) > 1000 else lines

    footnote_defs = []
    for i, line in enumerate(last_1000):
        actual_line_num = len(lines) - len(last_1000) + i
        if re.search(r'footnote-\d+', line) or re.match(r'\[\^\d+\]:', line):
            footnote_defs.append((actual_line_num, line.strip()))

    print(f"Found {len(footnote_defs)} potential footnote definitions in last 1000 lines")

    if footnote_defs:
        print("\nFootnote definitions found:")
        for line_num, content in footnote_defs[:20]:  # Show first 20
            print(f"Line {line_num}: {content}")

        # Look for the pattern of footnote definitions
        # They might be in HTML format like <a id="footnote-1"></a> content
        footnote_def_pattern = r'<a id="footnote-\d+"></a>'
        def_matches = []
        for i, line in enumerate(last_1000):
            if re.search(footnote_def_pattern, line):
                actual_line_num = len(lines) - len(last_1000) + i
                def_matches.append((actual_line_num, line))

        print(f"\nFound {len(def_matches)} HTML footnote definition anchors")

        if def_matches:
            print("HTML footnote definitions:")
            for line_num, content in def_matches[:10]:
                print(f"Line {line_num}: {content}")

if __name__ == "__main__":
    main()













