#!/usr/bin/env python3
"""
Extract Shemot (Exodus) from tanaj.docx and create shemot.md
Based on the successful Bereshit extraction approach
"""

import sys
import os
import re

try:
    import mammoth
except ImportError:
    print("Error: The 'mammoth' library is not installed.")
    print("Install with: pip install mammoth")
    sys.exit(1)

def extract_verse_num(line: str) -> int:
    """Extract verse number from a line, return 0 if no verse marker found."""
    # Look for patterns like __1__, __2__, etc. at the beginning of the line
    verse_match = re.match(r'^__(\d+)__', line)
    if verse_match:
        return int(verse_match.group(1))
    return 0

def normalize_footnotes(text: str) -> str:
    """Normalize footnotes from HTML format to Markdown format."""
    # Convert footnote references: <a id="footnote-ref-244"></a>[^244] -> [^244]
    text = re.sub(r'<a id="footnote-ref-\d+"></a>\s*', '', text)
    # Convert other HTML anchor references: <a id="_Hlk..."></a> -> (remove)
    text = re.sub(r'<a id="_Hlk\d+"></a>\s*', '', text)
    # Convert footnote references: [\[1\]](#footnote-1) -> [^1]
    text = re.sub(r'\[\\\[(\d+)\\\]\]\(#footnote-\d+\)', r'[^\1]', text)

    # Convert footnote definitions: <a id="footnote-1"></a> content [↑](#footnote-ref-1) -> [^1]: content
    def replace_footnote_definition(match):
        num = match.group(1)
        content = match.group(2).strip()
        # Remove the back reference [↑](#footnote-ref-1)
        content = re.sub(r'\s*\[↑\]\s*\(#footnote-ref-\d+\)\s*$', '', content)
        # Clean up any remaining HTML
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\s+', ' ', content).strip()
        return f'\n[^{num}]: {content}\n'

    text = re.sub(
        r'<a id="footnote-(\d+)"[^>]*></a>\s*([^<\n]+)',
        replace_footnote_definition,
        text
    )
    return text

def extract_shemot_section(text: str) -> str:
    """Extract the Shemot section from the full text."""
    lines = text.split('\n')
    print(f"Processing {len(lines)} lines...")

    # Find Shemot start
    shemot_start = -1
    for i, line in enumerate(lines):
        if ('__SHEMOT' in line and 'ÉXODO' in line and 'שמות' in line and
            line.strip() == '__SHEMOT \\(ÉXODO\\)__ שמות'):
            shemot_start = i
            print(f"Found Shemot start at line {i}")
            break

    if shemot_start == -1:
        print("Error: Shemot title not found")
        return ""

    # Find Shemot end (next book: VAIKRÁ/LEVÍTICO)
    shemot_end = -1
    for i in range(shemot_start + 1, len(lines)):
        line = lines[i]
        line_upper = line.upper()
        # Skip empty lines and subtitles
        if not line or re.match(r'^\*([^*]+)\*$', line):
            continue

        # Stop at the main title of the next Torah book (Vaikrá/Leviticus)
        if line.strip() == '__VAIKRÁ \\(LEVÍTICO\\)__ ויקרא':
            shemot_end = i
            print(f"Found Shemot end at line {i}")
            break

    # If no next book found, take everything until footnotes start
    if shemot_end == -1:
        for i in range(shemot_start + 1, len(lines)):
            if re.match(r'\[\^\d+\]:', lines[i]):
                shemot_end = i
                print(f"Found footnotes start at line {i}")
                break

    if shemot_end == -1:
        print("Warning: Could not find clear end, taking rest of document")
        shemot_end = len(lines)

    # Extract Shemot lines
    shemot_lines = lines[shemot_start:shemot_end]

    # Find all footnote numbers used in Shemot
    footnote_nums = set()
    shemot_text = '\n'.join(shemot_lines)
    # Find footnote references like [^1]
    for match in re.finditer(r'\[\^(\d+)\]', shemot_text):
        footnote_nums.add(int(match.group(1)))

    print(f"Found {len(footnote_nums)} unique footnotes in Shemot")

    # Extract footnote definitions that belong to Shemot
    footnote_lines = []
    if footnote_nums:
        for i in range(shemot_end, len(lines)):
            line = lines[i]
            # Check for footnote definition patterns [^1]: content
            footnote_def_match = re.match(r'\[\^(\d+)\]:\s*(.+)', line)
            if footnote_def_match:
                footnote_num = int(footnote_def_match.group(1))
                if footnote_num in footnote_nums:
                    footnote_lines.append(line)

        # Add "## Footnotes" header
        if footnote_lines:
            footnote_lines.insert(0, "")
            footnote_lines.insert(0, "## Footnotes")

    return '\n'.join(shemot_lines + footnote_lines)

def format_to_target_structure(text: str) -> str:
    """Apply minimal formatting to the extracted text."""
    lines = text.split('\n')
    formatted_lines = []
    current_chapter = 0
    just_processed_chapter_marker = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip empty lines and subtitles
        if not line or re.match(r'^\*([^*]+)\*$', line):
            formatted_lines.append(line)
            i += 1
            continue

        # Check for book title keywords - only for the main book title at the beginning
        book_title_found = None
        line_length = len(line.strip())
        # Only consider as book title if line is short and contains specific patterns
        if (line_length < 150 and line_length > 0 and '__' in line and
            not line.startswith('#') and not re.match(r'\[\^\d+\]:', line)):
            # Check for Torah book titles (like Bereshit)
            if 'TORAH' in line.upper() and '__BERESHIT' in line:
                book_title_found = '__TORAH - BERESHIT (GÉNESIS)*__בראשית*'
            # Check for individual book titles (like Shemot)
            elif line.strip() == '__SHEMOT \\(ÉXODO\\)__ שמות':
                book_title_found = '__SHEMOT (ÉXODO)*__שמות*'

        if book_title_found:
            formatted_lines.append(f"# {book_title_found}")
            formatted_lines.append("")
            current_chapter = 1  # Reset chapter for new book
            i += 1  # Skip the original title line
            continue

        # Check if this is a chapter marker (like __29__)
        chapter_match = re.match(r'^__(\d+)__$', line)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            formatted_lines.append(line)
            formatted_lines.append("")
            current_chapter = chapter_num
            just_processed_chapter_marker = True
            i += 1
            continue

        # Check if this line has a verse marker
        verse_num = extract_verse_num(line)

        # If we just processed a chapter marker and this line has content
        if just_processed_chapter_marker and line.strip():
            # Check if it starts with __ __ (indicating malformed verse 1)
            if line.startswith('__ __'):
                # Replace __ __ with __1__
                line = line.replace('__ __', '__1__', 1)
            elif not re.match(r'^__\d+__', line) and verse_num == 0:
                # This is the first verse of the chapter, add __1__
                line = f"__1__ {line}"
            elif re.search(r'__\d+__', line) and not line.startswith('__1__'):
                # Line contains verse markers but doesn't start with __1__, add it
                line = f"__1__ {line}"
            just_processed_chapter_marker = False  # Reset flag

        # Default: keep the line exactly as is
        formatted_lines.append(line)
        i += 1

    # Minimal post-processing
    final_lines = []
    for line in formatted_lines:
        # Convert "*word *" to "*word*"
        line = re.sub(r'\*(\w+)\s+\*', r'*\1*', line)
        # Convert "* *word" to "*word*"
        line = re.sub(r'\*\s+\*(\w+)', r'*\1*', line)
        # Convert "word* *" to "*word*"
        line = re.sub(r'(\w+)\*\s+\*', r'*\1*', line)

        # Fix malformed verse markers: __2 __ -> __2__
        line = re.sub(r'__(\d+)\s+__', r'__\1__', line)

        # Remove unnecessary backslash escapes for punctuation
        line = re.sub(r'\\([.,:;])', r'\1', line)

        final_lines.append(line)

    return '\n'.join(final_lines)

def main():
    input_file = "../tanaj.docx"
    output_file = "shemot.md"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print(f"Converting '{input_file}' to extract Shemot section...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    if result.messages:
        print("Conversion warnings:")
        for message in result.messages:
            print(f"  - {message}")

    raw_markdown = result.value
    print("Normalizing footnotes...")
    normalized_text = normalize_footnotes(raw_markdown)

    print("Extracting Shemot section...")
    shemot_text = extract_shemot_section(normalized_text)

    if not shemot_text:
        print("Error: Could not extract Shemot section")
        sys.exit(1)

    print("Applying minimal formatting...")
    formatted_text = format_to_target_structure(shemot_text)

    print("Cleaning formatting...")
    # Final cleanup
    formatted_text = re.sub(r'\n{3,}', '\n\n', formatted_text)

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_text)

    # Count chapters and verses
    chapters = len(re.findall(r'^__\d+__$', formatted_text, re.MULTILINE))
    verses = len(re.findall(r'__\d+__', formatted_text))

    print("✓ Shemot extraction completed successfully!")
    print(f"  Generated file: {output_file}")
    print(f"  Size: {len(formatted_text)} characters")
    print(f"  Chapters detected: {chapters}")
    print(f"  Verse markers found: {verses}")

if __name__ == "__main__":
    main()
