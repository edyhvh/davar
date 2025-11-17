#!/usr/bin/env python3
"""
Extract Tehilim (Psalms) from tanaj.docx and create tehilim.md
Based on the optimized workflow from previous books
Special handling for:
- Psalm titles
- Alphabetical divisions (alef-bet)
- Book divisions (1-41, 42-72, 73-89, 90-106, 107-150)
- Column-structured verses (Psalm 56-150)
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
    # Convert any other HTML anchor references: <a id="..."></a> -> (remove)
    text = re.sub(r'<a id="[^"]+"></a>\s*', '', text)
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

def extract_tehilim_section(text: str) -> str:
    """Extract the Tehilim section from the full text."""
    lines = text.split('\n')
    print(f"Processing {len(lines)} lines...")

    # Find Tehilim start
    tehilim_start = -1
    for i, line in enumerate(lines):
        if line.strip() == '__KETUVIM \\- TEHILIM \\(SALMOS\\)__תהלים':
            tehilim_start = i
            print(f"Found Tehilim start at line {i}")
            break

    if tehilim_start == -1:
        print("Error: Tehilim title not found")
        return ""

    # Find Tehilim end (next book: Mishlei/Proverbs)
    tehilim_end = -1
    for i in range(tehilim_start + 1, len(lines)):
        line = lines[i]
        line_upper = line.upper()
        # Skip empty lines and subtitles
        if not line or re.match(r'^\*([^*]+)\*$', line):
            continue

        # Stop at the next book (Mishlei/Proverbs)
        if 'MISHLEI' in line_upper or 'PROVERBIOS' in line_upper or 'משלי' in line:
            tehilim_end = i
            print(f"Found Tehilim end at line {i}: {line[:50]}...")
            break

    # If no next book found, take everything until footnotes start or reasonable end
    if tehilim_end == -1:
        # Tehilim is very long, look for a reasonable stopping point
        for i in range(tehilim_start + 1, min(len(lines), tehilim_start + 10000)):  # Look ahead up to 10k lines
            if re.match(r'\[\^\d+\]:', lines[i]):
                tehilim_end = i
                print(f"Found footnotes start at line {i}")
                break

    if tehilim_end == -1:
        print("Warning: Could not find clear end, taking large portion")
        # Take a reasonable chunk for Tehilim (should be around Psalm 150)
        tehilim_end = min(len(lines), tehilim_start + 8000)

    # Extract Tehilim lines
    tehilim_lines = lines[tehilim_start:tehilim_end]

    # Find all footnote numbers used in Tehilim
    footnote_nums = set()
    tehilim_text = '\n'.join(tehilim_lines)
    # Find footnote references like [^1]
    for match in re.finditer(r'\[\^(\d+)\]', tehilim_text):
        footnote_nums.add(int(match.group(1)))

    print(f"Found {len(footnote_nums)} unique footnotes in Tehilim")

    # Extract footnote definitions that belong to Tehilim
    footnote_lines = []
    if footnote_nums:
        for i in range(tehilim_end, min(len(lines), tehilim_end + 2000)):  # Look for footnotes in next 2000 lines
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

    return '\n'.join(tehilim_lines + footnote_lines)

def format_to_target_structure(text: str) -> str:
    """Apply special formatting for Tehilim (Psalms) with titles, book divisions, and column structures."""
    lines = text.split('\n')
    formatted_lines = []
    just_processed_psalm_marker = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line:
            formatted_lines.append(line)
            i += 1
            continue

        # Check for the main book title
        if line.strip() == '__KETUVIM \\- TEHILIM \\(SALMOS\\)__תהלים':
            formatted_lines.append("# __KETUVIM - TEHILIM (SALMOS)*__תהלים*")
            formatted_lines.append("")
            i += 1
            continue

        # Check for book division markers (like "LIBRO PRIMERO", "LIBRO SEGUNDO", etc.)
        if 'LIBRO' in line.upper() and ('PRIMERO' in line.upper() or 'SEGUNDO' in line.upper() or
                                       'TERCERO' in line.upper() or 'CUARTO' in line.upper() or
                                       'QUINTO' in line.upper()):
            formatted_lines.append(line)
            formatted_lines.append("")
            i += 1
            continue

        # Check for psalm titles (specific patterns for Tehilim titles)
        # Psalm titles contain specific keywords and are usually short
        if not line.startswith('__') and not line.startswith('#') and not re.match(r'\[\^\d+\]:', line):
            line_stripped = line.strip()
            line_length = len(line_stripped)

            # Check for specific psalm title patterns
            is_psalm_title = False

            # Look ahead to see if next non-empty line is a psalm marker
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            next_is_psalm = j < len(lines) and (re.match(r'^__\d+__$', lines[j].strip()) or re.match(r'^__\d+__', lines[j].strip()))

            if next_is_psalm and line_length > 0 and line_length < 150:
                # Check for specific title keywords
                title_keywords = [
                    'cántico', 'cántico de', 'para el supervisor', 'mizmor', 'shir',
                    'maskil', 'mikhtam', 'tehilah', 'shiggaion', 'lemaaseh',
                    'al shoshannim', 'al aley shoshannim', 'al hagittit',
                    'al mut labben', 'al tashheth', 'al ayyeleth hashachar',
                    'sobre la paloma', 'sobre no destruyas', 'sobre los lirios',
                    'de david', 'de asaf', 'de los hijos de koraj', 'de moises',
                    'de salomon', 'de etan', 'de heman'
                ]

                lower_line = line_stripped.lower()
                if any(keyword in lower_line for keyword in title_keywords):
                    is_psalm_title = True
                # Also check for lines that start with capital letters and are short
                elif line_length < 80 and line_stripped[0].isupper() and (
                    'de ' in lower_line or 'para ' in lower_line or 'sobre ' in lower_line or
                    'al ' in lower_line or 'con ' in lower_line
                ):
                    is_psalm_title = True

            if is_psalm_title:
                # Format as italic title
                formatted_lines.append(f"*{line_stripped}*")
                formatted_lines.append("")
                i += 1
                continue

        # Check for alphabetical divisions (alef-bet markers)
        # These are typically single Hebrew letters or short Hebrew words
        if re.match(r'^[א-ת]{1,2}$', line.strip()) or line.strip() in ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת']:
            # Keep Hebrew letter divisions as-is or format them
            formatted_lines.append(f"**{line.strip()}**")  # Make them bold
            formatted_lines.append("")
            i += 1
            continue

        # Check for psalm number markers (like __1__, __2__, etc. at start of line)
        psalm_match = re.match(r'^__(\d+)__$', line)
        if psalm_match:
            psalm_num = int(psalm_match.group(1))
            formatted_lines.append(line)
            formatted_lines.append("")
            just_processed_psalm_marker = True
            i += 1
            continue

        # Check if this line has verse markers
        verse_num = extract_verse_num(line)

        # If we just processed a psalm marker and this line has content, ensure it starts with __1__
        if just_processed_psalm_marker and line.strip():
            if line.startswith('__ __'):
                # Replace __ __ with __1__
                line = line.replace('__ __', '__1__', 1)
            elif not re.match(r'^__\d+__', line) and verse_num == 0:
                # This is the first verse of the psalm, add __1__
                line = f"__1__ {line}"
            elif re.search(r'__\d+__', line) and not line.startswith('__1__'):
                # Line contains verse markers but doesn't start with __1__, add it
                line = f"__1__ {line}"
            just_processed_psalm_marker = False  # Reset flag

        # Handle column-structured verses (for Psalms 56-150)
        # Look for lines that might be part of columnar structure
        if '__' in line and ('  ' in line or '\t' in line):  # Multiple spaces or tabs indicating columns
            # Keep the columnar structure as-is
            formatted_lines.append(line)
            i += 1
            continue

        # Default: keep the line exactly as is
        formatted_lines.append(line)
        i += 1

    # Post-processing for Tehilim-specific formatting
    final_lines = []
    for line in formatted_lines:
        # Fix malformed verse markers: __2 __ -> __2__
        line = re.sub(r'__(\d+)\s+__', r'__\1__', line)

        # Fix words split by hyphens: medi\-tación -> meditación, des\-piértate -> despiértate
        line = re.sub(r'(\w+)\-(\w+)', r'\1\2', line)

        # Remove unnecessary backslash escapes for punctuation
        line = re.sub(r'\\([.,:;])', r'\1', line)

        # Clean up multiple asterisks
        line = re.sub(r'\*\*\*+', '**', line)  # Multiple asterisks to double
        line = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', line)  # Ensure proper bold formatting

        # Fix incorrect italic formatting - remove italics from lines that are clearly verses
        # If a line starts with __1__ and is mostly in italics, remove the outer italics
        if line.startswith('__1__ *') and line.endswith('*'):
            # Check if this looks like a verse that shouldn't be entirely italic
            verse_content = line[7:-1]  # Remove __1__ * and final *
            # If it contains verse markers or looks like normal text, remove italics
            if '__' in verse_content or len(verse_content.split()) > 3:
                line = f"__1__ {verse_content}"

        final_lines.append(line)

    return '\n'.join(final_lines)

def main():
    input_file = "../tanaj.docx"
    output_file = "tehilim.md"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print(f"Converting '{input_file}' to extract Tehilim section...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    if result.messages:
        print("Conversion warnings:")
        for message in result.messages:
            print(f"  - {message}")

    raw_markdown = result.value
    print("Normalizing footnotes...")
    normalized_text = normalize_footnotes(raw_markdown)

    print("Extracting Tehilim section...")
    tehilim_text = extract_tehilim_section(normalized_text)

    if not tehilim_text:
        print("Error: Could not extract Tehilim section")
        sys.exit(1)

    print("Applying minimal formatting...")
    formatted_text = format_to_target_structure(tehilim_text)

    print("Cleaning formatting...")
    # Final cleanup
    formatted_text = re.sub(r'\n{3,}', '\n\n', formatted_text)

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_text)

    # Count chapters and verses
    chapters = len(re.findall(r'^__\d+__$', formatted_text, re.MULTILINE))
    verses = len(re.findall(r'__\d+__', formatted_text))

    print("✓ Tehilim extraction completed successfully!")
    print(f"  Generated file: {output_file}")
    print(f"  Size: {len(formatted_text)} characters")
    print(f"  Chapters detected: {chapters}")
    print(f"  Verse markers found: {verses}")

if __name__ == "__main__":
    main()


