#!/usr/bin/env python3
"""
Extract Ieshaiahu (Isaiah) from tanaj.docx and create ieshaiahu.md
Based on the optimized workflow from previous books
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

def extract_ieshaiahu_section(text: str) -> str:
    """Extract the Ieshaiahu section from the full text."""
    lines = text.split('\n')
    print(f"Processing {len(lines)} lines...")

    # Find Ieshaiahu start
    ieshaiahu_start = -1
    for i, line in enumerate(lines):
        if line.strip() == '__IESHAIÁHU \\(ISAÍAS\\)__ ישעיהו':
            ieshaiahu_start = i
            print(f"Found Ieshaiahu start at line {i}")
            break

    if ieshaiahu_start == -1:
        print("Error: Ieshaiahu title not found")
        return ""

    # Find Ieshaiahu end (next book: Yermeyahu/Jeremiah)
    ieshaiahu_end = -1
    for i in range(ieshaiahu_start + 1, len(lines)):
        line = lines[i]
        line_upper = line.upper()
        # Skip empty lines and subtitles
        if not line or re.match(r'^\*([^*]+)\*$', line):
            continue

        # Stop at the main title of the next book (Yermeyahu/Jeremiah)
        if 'YERMEYAHU' in line_upper or 'YERMIAHU' in line_upper or 'ירמיהו' in line:
            ieshaiahu_end = i
            print(f"Found Ieshaiahu end at line {i}: {line[:50]}...")
            break

    # If no next book found, take everything until footnotes start
    if ieshaiahu_end == -1:
        for i in range(ieshaiahu_start + 1, len(lines)):
            if re.match(r'\[\^\d+\]:', lines[i]):
                ieshaiahu_end = i
                print(f"Found footnotes start at line {i}")
                break

    if ieshaiahu_end == -1:
        print("Warning: Could not find clear end, taking rest of document")
        ieshaiahu_end = len(lines)

    # Extract Ieshaiahu lines
    ieshaiahu_lines = lines[ieshaiahu_start:ieshaiahu_end]

    # Find all footnote numbers used in Ieshaiahu
    footnote_nums = set()
    ieshaiahu_text = '\n'.join(ieshaiahu_lines)
    # Find footnote references like [^1]
    for match in re.finditer(r'\[\^(\d+)\]', ieshaiahu_text):
        footnote_nums.add(int(match.group(1)))

    print(f"Found {len(footnote_nums)} unique footnotes in Ieshaiahu")

    # Footnotes will be extracted and formatted by format_to_target_structure
    return '\n'.join(ieshaiahu_lines)

def format_to_target_structure(text: str) -> str:
    """Apply minimal formatting to the extracted text."""
    lines = text.split('\n')
    formatted_lines = []
    footnote_definitions = {}
    current_chapter = 0
    just_processed_chapter_marker = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip empty lines and already formatted subtitles
        if not line:
            formatted_lines.append(line)
            i += 1
            continue

        # Check if it's an already formatted subtitle (*text*)
        if re.match(r'^\*([^*]+)\*$', line):
            formatted_lines.append(line)
            i += 1
            continue


        # Continue with normal processing...

        # Check if this is an unformatted subtitle
        line_stripped = line.strip()
        line_length = len(line_stripped)

        # Look for subtitle patterns:
        # 1. Lines before chapter markers
        # 2. Lines that look like titles (short, contain Hebrew names, descriptive phrases)
        is_subtitle = False

        # Check if next non-empty line is a chapter marker
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1  # Skip empty lines
        next_is_chapter = j < len(lines) and re.match(r'^__\d+__$', lines[j])

        # Check if previous line was a verse ending or empty
        prev_had_content = False
        k = i - 1
        while k >= 0 and not lines[k].strip():
            k -= 1  # Skip empty lines backward
        if k >= 0 and (re.search(r'__\d+__', lines[k]) or re.match(r'^__\d+__$', lines[k])):
            prev_had_content = True

        # Subtitle detection criteria
        if (line_length > 0 and line_length < 100 and
            not line.startswith('__') and not line.startswith('#') and
            not re.match(r'\[\^\d+\]:', line) and
            not re.match(r'^__\d+__', line) and
            not re.match(r'^__\d+__', line_stripped)):

            # Check for title-like patterns
            has_title_patterns = (
                # Contains Hebrew names
                any(name in line_stripped for name in [
                    'Yeshayahu', 'Yeshua', 'David', 'Shelomoh', 'Abraham',
                    'Itzhak', 'Iaacob', 'Moshéh', 'Aharón', 'Yirmeyahu',
                    'Yechezquel', 'Daniél', 'Hoshea', 'Ioel', 'Amós',
                    'Ovadyah', 'Ionah', 'Mijah', 'Najum', 'Jabaquq',
                    'Tzefaniah', 'Jagai', 'Zejaryah', 'Malají'
                ]) or
                # Contains descriptive phrases
                any(phrase in line_stripped.lower() for phrase in [
                    'rey de', 'hijo de', 'muerte de', 'profeta',
                    'palacio', 'templo', 'altares', 'ídolos', 'pecados',
                    'reinado', 'guerra', 'paz', 'alianza', 'destrucción',
                    'cautiverio', 'exilio', 'liberación', 'restauración',
                    'visión', 'oráculo', 'profecía', 'mensaje', 'palabra'
                ]) or
                # Short phrases that look like section titles
                (line_length < 50 and (
                    line_stripped[0].isupper() or  # Starts with capital
                    'de' in line_stripped.lower() or  # Contains "de"
                    any(word in line_stripped.lower() for word in [
                        'rey', 'profeta', 'sacerdote', 'juez', 'príncipe',
                        'cautivo', 'exilio', 'destrucción', 'reconstrucción',
                        'visión', 'oráculo', 'mensaje'
                    ])
                ))
            )

            if has_title_patterns or next_is_chapter or prev_had_content:
                # Format as italic subtitle
                line = f"*{line_stripped}*"
                is_subtitle = True

        if is_subtitle:
            formatted_lines.append(line)
            i += 1
            continue

        # Check for book title keywords - only for the main book title at the beginning
        book_title_found = None
        line_length = len(line.strip())
        # Only consider as book title if line is short and contains specific patterns
        if (line_length < 150 and line_length > 0 and '__' in line and
            not line.startswith('#') and not re.match(r'\[\^\d+\]:', line)):
            # Check for individual book titles (like Ieshaiahu)
            if line.strip() == '__IESHAIÁHU \\(ISAÍAS\\)__ ישעיהו':
                book_title_found = '__IESHAIÁHU (ISAÍAS)*__ישעיהו*'

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

    # Add footnote definitions at the end
    if footnote_definitions:
        final_lines.append("")
        final_lines.append("## Footnotes")
        final_lines.append("")
        for num in sorted(footnote_definitions.keys(), key=int):
            final_lines.append(f"[^{num}]: {footnote_definitions[num]}")

    return '\n'.join(final_lines)

def main():
    input_file = "../tanaj.docx"
    output_file = "ieshaiahu.md"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print(f"Converting '{input_file}' to extract Ieshaiahu section...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    if result.messages:
        print("Conversion warnings:")
        for message in result.messages:
            print(f"  - {message}")

    raw_markdown = result.value
    print("Normalizing footnotes...")
    normalized_text = normalize_footnotes(raw_markdown)

    print("Extracting Ieshaiahu section...")
    ieshaiahu_text = extract_ieshaiahu_section(normalized_text)

    if not ieshaiahu_text:
        print("Error: Could not extract Ieshaiahu section")
        sys.exit(1)

    print("Applying minimal formatting...")
    formatted_text = format_to_target_structure(ieshaiahu_text)

    print("Cleaning formatting...")
    # Final cleanup
    formatted_text = re.sub(r'\n{3,}', '\n\n', formatted_text)

    # For Ieshaiahu, extract footnote definitions from the end of the document
    footnote_definitions = {}

    # First, extract footnote definitions from the end of the raw document
    raw_lines = raw_markdown.split('\n')
    for line in reversed(raw_lines):
        # Look for footnote definitions at the end: 555. <a id="footnote-555"></a> content [↑](#footnote-ref-555)
        footnote_match = re.search(r'(\d+)\.\s*<a id="footnote-\d+"></a>\s*([^<\n]+)', line)
        if footnote_match:
            num = footnote_match.group(1)
            content = footnote_match.group(2).strip()
            # Remove the back reference [↑](#footnote-ref-XXX)
            content = re.sub(r'\s*\[↑\]\s*\(#footnote-ref-\d+\)\s*$', '', content)
            footnote_definitions[num] = content

    # Now process the text to clean inline footnote content and keep only references
    lines = formatted_text.split('\n')
    processed_lines = []

    for line in lines:
        # Fix malformed verse markers that are attached to previous text
        # Pattern: any non-underscore character followed immediately by __number__
        line = re.sub(r'([^_])__(\d+)__', r'\1 __\2__', line)
        # Process inline footnotes: [^number].content -> [^number] (remove inline content)
        while '[^' in line and '].' in line:
            # Find footnote pattern
            start_idx = line.find('[^')
            dot_idx = line.find('].', start_idx)
            if start_idx == -1 or dot_idx == -1:
                break

            # Extract footnote reference
            footnote_ref = line[start_idx:dot_idx+1]  # [^555]

            # Find content end (next [^ or end of line)
            content_start = dot_idx + 2  # After ].
            next_ref = line.find('[^', content_start)
            if next_ref == -1:
                # Remove everything after the reference
                line = line[:start_idx] + footnote_ref
            else:
                # Keep everything after the inline content
                line = line[:start_idx] + footnote_ref + line[next_ref:]

        processed_lines.append(line)

    # Filter to only include footnotes that are referenced in Ieshaiahu text
    referenced_footnotes = set()
    ieshaiahu_text = '\n'.join(processed_lines)
    for match in re.finditer(r'\[\^(\d+)\]', ieshaiahu_text):
        referenced_footnotes.add(match.group(1))

    # Add footnote definitions at the end
    if referenced_footnotes:
        processed_lines.append("")
        processed_lines.append("## Footnotes")
        processed_lines.append("")
        for num in sorted(referenced_footnotes, key=int):
            if num in footnote_definitions:
                # Clean up unnecessary backslashes before punctuation
                content = footnote_definitions[num]
                content = re.sub(r'\\([.,;:])', r'\1', content)
                processed_lines.append(f"[^{num}]: {content}")

    formatted_text = '\n'.join(processed_lines)

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_text)

    # Count chapters and verses
    chapters = len(re.findall(r'^__\d+__$', formatted_text, re.MULTILINE))
    verses = len(re.findall(r'__\d+__', formatted_text))

    print("✓ Ieshaiahu extraction completed successfully!")
    print(f"  Generated file: {output_file}")
    print(f"  Size: {len(formatted_text)} characters")
    print(f"  Chapters detected: {chapters}")
    print(f"  Verse markers found: {verses}")

if __name__ == "__main__":
    main()
