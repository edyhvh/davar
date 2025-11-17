#!/usr/bin/env python3
"""
Debug chapter processing in Shemot
"""

import sys
import os
import re

try:
    import mammoth
except ImportError:
    print("Error: The 'mammoth' library is not installed.")
    sys.exit(1)

def extract_verse_num(line: str) -> int:
    """Extract verse number from a line, return 0 if no verse marker found."""
    # Look for patterns like __1__, __2__, etc. at the beginning of the line
    verse_match = re.match(r'^__(\d+)__', line)
    if verse_match:
        return int(verse_match.group(1))
    return 0

def main():
    input_file = "../tanaj.docx"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print("Debugging chapter processing in Shemot...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    raw_markdown = result.value
    lines = raw_markdown.split('\n')

    print(f"Total lines: {len(lines)}")

    # Find Shemot start
    shemot_start = -1
    for i, line in enumerate(lines):
        if line.strip() == '__SHEMOT \\(ÉXODO\\)__ שמות':
            shemot_start = i
            break

    if shemot_start == -1:
        print("Shemot start not found")
        return

    # Simulate the processing logic
    current_chapter = 0
    formatted_lines = []

    # Process just the first few lines after Shemot start
    start_processing = False
    for i in range(shemot_start, min(shemot_start + 20, len(lines))):
        line = lines[i]

        # Skip empty lines and subtitles
        if not line or re.match(r'^\*([^*]+)\*$', line):
            formatted_lines.append(line)
            continue

        # Check if this is a chapter marker (like __29__)
        chapter_match = re.match(r'^__(\d+)__$', line)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            formatted_lines.append(line)
            formatted_lines.append("")
            current_chapter = chapter_num
            print(f"Processed chapter marker: {line}, current_chapter = {current_chapter}")
            print(f"formatted_lines length: {len(formatted_lines)}")
            print(f"formatted_lines[-5:] = {formatted_lines[-5:]}")
            start_processing = True
            continue

        if start_processing:
            # Check if this line has a verse marker
            verse_num = extract_verse_num(line)

            print(f"Processing line {i}: '{line[:50]}...'")
            print(f"  formatted_lines[-1] == '': {formatted_lines[-1] == ''}")
            print(f"  len(formatted_lines) >= 2: {len(formatted_lines) >= 2}")
            if len(formatted_lines) >= 2:
                print(f"  formatted_lines[-2] == '__{current_chapter}__': {formatted_lines[-2] == f'__{current_chapter}__'}")
                print(f"  formatted_lines[-2]: '{repr(formatted_lines[-2])}'")
                print(f"  f'__{current_chapter}__': '{repr(f'__{current_chapter}__')}'")
            print(f"  line.strip(): '{line.strip()[:30]}...'")
            print(f"  verse_num: {verse_num}")
            search_result = re.search(r'__\d+__', line)
            print(f"  re.search(r'__\d+__', line): {search_result is not None}")

            # If we just processed a chapter marker and this line has content
            if (formatted_lines and formatted_lines[-1] == "" and
                len(formatted_lines) >= 2 and formatted_lines[-2] == f"__{current_chapter}__" and
                line.strip()):
                print("  -> CONDITION MET: Should process verse 1 logic")

                # Check if it starts with __ __ (indicating malformed verse 1)
                if line.startswith('__ __'):
                    print("  -> Replacing '__ __' with '__1__'")
                    line = line.replace('__ __', '__1__', 1)
                elif not re.match(r'^__\d+__', line) and verse_num == 0:
                    print("  -> Adding '__1__' to start")
                    line = f"__1__ {line}"
                elif re.search(r'__\d+__', line) and not line.startswith('__1__'):
                    print("  -> Adding '__1__' to start (contains verse markers)")
                    line = f"__1__ {line}"
                else:
                    print("  -> No change needed")
            else:
                print("  -> CONDITION NOT MET")

            formatted_lines.append(line)
            break  # Just process first content line

if __name__ == "__main__":
    main()
