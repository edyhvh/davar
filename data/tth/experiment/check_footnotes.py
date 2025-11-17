#!/usr/bin/env python3
"""
Script to check how footnotes are structured in the original tanaj.docx
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

    print("Converting tanaj.docx to check footnote structure...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    markdown_text = result.value
    lines = markdown_text.split('\n')

    print(f"Total lines: {len(lines)}")

    # Find where Bereshit content starts and ends
    bereshit_start = -1
    bereshit_end = -1

    for i, line in enumerate(lines):
        if ('TORAH - BERESHIT' in line.upper() or 'בראשית' in line) and '__' in line and '](#' not in line:
            bereshit_start = i
            break

    if bereshit_start == -1:
        print("Bereshit start not found")
        return

    print(f"Bereshit starts at line {bereshit_start}")

    # Find next book
    for i in range(bereshit_start + 1, len(lines)):
        line = lines[i].strip().upper()
        if 'TORAH - SHEMOT' in line or 'SHEMOT' in line and '__' in line and '](#' not in line:
            bereshit_end = i
            break

    if bereshit_end == -1:
        print("Next book not found, will search for footnotes after Bereshit content")
        # Look for footnotes after Bereshit
        for i in range(bereshit_start + 1000, min(bereshit_start + 2000, len(lines))):
            if re.match(r'\[\^\d+\]:', lines[i]):
                bereshit_end = i
                print(f"Footnotes start at line {i}")
                break

    print(f"Bereshit ends at line {bereshit_end}")

    # Find all footnotes in the document
    all_footnotes = []
    for i, line in enumerate(lines):
        if re.match(r'\[\^\d+\]:', line):
            all_footnotes.append(i)

    print(f"Total footnotes in document: {len(all_footnotes)}")

    if all_footnotes:
        print(f"First footnote at line {all_footnotes[0]}")
        print(f"Last footnote at line {all_footnotes[-1]}")

        # Check if footnotes are after Bereshit
        if all_footnotes[0] > bereshit_end:
            print("Footnotes are located AFTER the Bereshit section")
            print(f"Gap between Bereshit end and footnotes: {all_footnotes[0] - bereshit_end} lines")

            # Show what comes between Bereshit and footnotes
            print("Content between Bereshit and footnotes:")
            for i in range(bereshit_end, min(bereshit_end + 10, all_footnotes[0])):
                print(f"Line {i}: '{lines[i]}'")
        else:
            print("Footnotes are within or before Bereshit section")

        # Show sample footnotes
        print("\nSample footnotes:")
        for i in range(min(5, len(all_footnotes))):
            line_num = all_footnotes[i]
            print(f"Line {line_num}: {lines[line_num]}")
    else:
        print("No footnotes found in document")

if __name__ == "__main__":
    main()
