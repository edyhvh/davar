#!/usr/bin/env python3
"""
Debug Bamidbar footnotes
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

    print("Debugging Bamidbar footnotes...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Find Bamidbar start
    bamidbar_start = -1
    for i, line in enumerate(lines):
        if line.strip() == '__BAMIDBAR \\(NÚMEROS\\)__במדבר':
            bamidbar_start = i
            break

    if bamidbar_start == -1:
        print("Bamidbar start not found")
        return

    # Find Bamidbar end
    bamidbar_end = -1
    for i in range(bamidbar_start + 1, len(lines)):
        line = lines[i]
        if line.strip() == '__DEVARIM \\(DEUTERONOMIO\\)__ דברים':
            bamidbar_end = i
            break

    if bamidbar_end == -1:
        print("Bamidbar end not found")
        return

    print(f"Bamidbar section: lines {bamidbar_start} to {bamidbar_end}")

    # Check for footnote patterns in Bamidbar section
    footnote_refs = []
    footnote_defs = []

    for i in range(bamidbar_start, min(bamidbar_end, len(lines))):
        line = lines[i]
        # Check for footnote references
        if re.search(r'\[.*\]\(#footnote-\d+\)', line):
            footnote_refs.append((i, line[:100] + '...'))
        # Check for footnote definitions
        if re.search(r'\[.*\]:\s', line):
            footnote_defs.append((i, line[:100] + '...'))

    print(f"\nFound {len(footnote_refs)} footnote references in Bamidbar:")
    for i, (line_num, content) in enumerate(footnote_refs[:5]):  # Show first 5
        print(f"  Line {line_num}: {content}")

    print(f"\nFound {len(footnote_defs)} footnote definitions in Bamidbar:")
    for i, (line_num, content) in enumerate(footnote_defs[:5]):  # Show first 5
        print(f"  Line {line_num}: {content}")

    # Check if there are any footnotes after the end
    print(f"\nChecking for footnotes after Bamidbar end (around line {bamidbar_end}):")
    for i in range(bamidbar_end, min(bamidbar_end + 20, len(lines))):
        line = lines[i]
        if re.search(r'\[.*\]:\s', line):
            print(f"  Line {i}: {line[:100]}...")

if __name__ == "__main__":
    main()




