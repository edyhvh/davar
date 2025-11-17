#!/usr/bin/env python3
"""
Extract Mishlei (Proverbs) from tanaj.docx and create mishlei.md
Based on the optimized workflow from previous books
Special handling for:
- Line-by-line sentence structure
- Sayings with titles from chapter 22 verse 22 onward
- Chapter/text titles
- Alphabetical divisions for "The Woman of Valor" (Proverbs 31:10-31)
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

def extract_mishlei_section(text: str) -> str:
    """Extract the Mishlei section from the full text."""
    lines = text.split('\n')
    print(f"Processing {len(lines)} lines...")

    # Find Mishlei start
    mishlei_start = -1
    for i, line in enumerate(lines):
        if line.strip() == '__MISHLEI \\(PROVERBIOS\\)__ משלי':
            mishlei_start = i
            print(f"Found Mishlei start at line {i}")
            break

    if mishlei_start == -1:
        print("Error: Mishlei title not found")
        return ""

    # Find Mishlei end (next book: Qohelet/Ecclesiastes or after last verse of chapter 31)
    mishlei_end = -1
    
    # First, try to find the next book
    for i in range(mishlei_start + 1, len(lines)):
        line = lines[i]
        line_upper = line.upper()
        # Skip empty lines and subtitles
        if not line or re.match(r'^\*([^*]+)\*$', line):
            continue

        # Stop at the next book (Qohelet/Ecclesiastes)
        if 'QOHELET' in line_upper or 'ECLESIASTÉS' in line_upper or 'קהלת' in line:
            mishlei_end = i
            print(f"Found Mishlei end at line {i}: {line[:50]}...")
            break

    # If no next book found, find the last verse of chapter 31 and cut after it
    if mishlei_end == -1:
        # Find the last occurrence of __31__ (the last verse of chapter 31)
        last_verse_31_line = -1
        for i in range(mishlei_start + 1, len(lines)):
            line = lines[i]
            # Look for verse 31 of chapter 31 (last verse)
            if re.match(r'^__31__', line) and not re.match(r'^__31__$', line):
                last_verse_31_line = i
        
        if last_verse_31_line > 0:
            # Find the end of that verse (next empty line or next numbered footnote)
            for i in range(last_verse_31_line + 1, min(len(lines), last_verse_31_line + 10)):
                line = lines[i]
                # Stop at numbered footnotes (like "1. O, *Por medio de.*")
                if re.match(r'^\d+\.\s+', line):
                    mishlei_end = i
                    print(f"Found Mishlei end at line {i} (after last verse of chapter 31, before footnotes)")
                    break
                # Stop at markdown footnotes
                if re.match(r'\[\^\d+\]:', line):
                    mishlei_end = i
                    print(f"Found Mishlei end at line {i} (after last verse of chapter 31, before markdown footnotes)")
                    break

    # If still not found, look for footnotes section
    if mishlei_end == -1:
        for i in range(mishlei_start + 1, len(lines)):
            # Look for numbered footnotes pattern (starts with "1. " after Mishlei content)
            if re.match(r'^\d+\.\s+', lines[i]):
                mishlei_end = i
                print(f"Found Mishlei end at line {i} (numbered footnotes start)")
                break
            if re.match(r'\[\^\d+\]:', lines[i]):
                mishlei_end = i
                print(f"Found Mishlei end at line {i} (markdown footnotes start)")
                break

    if mishlei_end == -1:
        print("Warning: Could not find clear end, taking rest of document")
        mishlei_end = len(lines)

    # Extract Mishlei lines
    mishlei_lines = lines[mishlei_start:mishlei_end]

    # Find all footnote numbers used in Mishlei
    footnote_nums = set()
    mishlei_text = '\n'.join(mishlei_lines)
    # Find footnote references like [^1]
    for match in re.finditer(r'\[\^(\d+)\]', mishlei_text):
        footnote_nums.add(int(match.group(1)))

    print(f"Found {len(footnote_nums)} unique footnotes in Mishlei")

    # Extract footnote definitions that belong to Mishlei
    footnote_lines = []
    if footnote_nums:
        for i in range(mishlei_end, len(lines)):
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

    return '\n'.join(mishlei_lines + footnote_lines)

def format_to_target_structure(text: str) -> str:
    """Apply minimal formatting to the extracted text."""
    lines = text.split('\n')
    formatted_lines = []
    just_processed_chapter_marker = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line:
            formatted_lines.append(line)
            i += 1
            continue

        # Check if it's an already formatted subtitle (*text*)
        if re.match(r'^\*([^*]+)\*$', line):
            formatted_lines.append(line)
            i += 1
            continue

        # Check for the main book title
        if line.strip() == '__MISHLEI \\(PROVERBIOS\\)__ משלי':
            formatted_lines.append("# __MISHLEI (PROVERBIOS)*__משלי*")
            formatted_lines.append("")
            i += 1
            continue

        # Check if this is a chapter marker (like __1__, __2__, etc. as standalone line)
        chapter_match = re.match(r'^__(\d+)__$', line)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            formatted_lines.append(line)
            formatted_lines.append("")
            just_processed_chapter_marker = True
            i += 1
            continue

        # Check if this is an unformatted subtitle
        # Only mark as subtitle if it's clearly before a chapter marker AND not part of a verse
        line_stripped = line.strip()
        line_length = len(line_stripped)

        is_subtitle = False
        if (line_length > 0 and line_length < 100 and
            not line.startswith('__') and not line.startswith('#') and
            not re.match(r'\[\^\d+\]:', line)):

            # Check if previous non-empty line was a verse (if so, this is likely part of the verse, not a subtitle)
            k = i - 1
            while k >= 0 and not lines[k].strip():
                k -= 1
            prev_is_verse = k >= 0 and re.search(r'__\d+__', lines[k]) and not re.match(r'^__\d+__$', lines[k])

            # Check if next non-empty line is a chapter marker (ONLY if next is chapter marker)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            next_is_chapter = j < len(lines) and re.match(r'^__\d+__$', lines[j])

            # Only mark as subtitle if:
            # 1. Next line is a chapter marker (definitive indicator)
            # 2. Previous line was NOT a verse (to avoid marking verse continuations as subtitles)
            # 3. It matches specific subtitle patterns (short, descriptive titles)
            if next_is_chapter and not prev_is_verse:
                # More restrictive subtitle patterns - only clear section titles
                title_patterns = [
                    r'^La \w+ \w+',  # "La Sabiduría llama", "La mujer de valor"
                    r'^Los \w+ \w+',  # "Los caminos de..."
                    r'^El \w+ \w+',   # "El camino de..."
                    r'^Palabras de \w+',  # "Palabras de Agur", "Palabras de Lemuel"
                    r'^Contraste entre',  # "Contraste entre..."
                    r'^La soberanía de',  # "La soberanía de..."
                ]
                # Also check if it's a very short descriptive phrase (2-4 words max)
                is_short_title = line_length < 50 and line_stripped.count(' ') < 4
                is_subtitle = (any(re.match(p, line_stripped, re.IGNORECASE) for p in title_patterns) or 
                               (is_short_title and not prev_is_verse))

            if is_subtitle:
                # Format as italic subtitle
                formatted_lines.append(f"*{line_stripped}*")
                formatted_lines.append("")
                i += 1
                continue

        # Check if this line has a verse marker
        verse_num = extract_verse_num(line)

        # If we just processed a chapter marker and this line has content, ensure it starts with __1__
        if just_processed_chapter_marker and line.strip():
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

        # Handle alphabetical divisions in Proverbs 31 (single Hebrew letters)
        if re.match(r'^[א-ת]$', line.strip()):
            formatted_lines.append(f"**{line.strip()}**")
            formatted_lines.append("")
            i += 1
            continue

        # Default: keep the line exactly as is
        formatted_lines.append(line)
        i += 1

    # Post-processing for Mishlei-specific formatting
    final_lines = []
    for line in formatted_lines:
        # Fix malformed verse markers: __2 __ -> __2__
        line = re.sub(r'__(\d+)\s+__', r'__\1__', line)
        
        # Fix verse markers with extra spaces: __19 __ -> __19__
        line = re.sub(r'__(\d+)\s+__', r'__\1__', line)
        
        # Ensure proper spacing after verse numbers: __8__Text -> __8__ Text
        line = re.sub(r'__(\d+)__([A-ZÁÉÍÓÚÑa-záéíóúñ\u0590-\u05FF])', r'__\1__ \2', line)

        # Fix hyphenated words
        line = re.sub(r'(\w+)\-(\w+)', r'\1\2', line)

        # Convert "*word *" to "*word*"
        line = re.sub(r'\*(\w+)\s+\*', r'*\1*', line)
        # Convert "* *word" to "*word*"
        line = re.sub(r'\*\s+\*(\w+)', r'*\1*', line)
        # Convert "word* *" to "*word*"
        line = re.sub(r'(\w+)\*\s+\*', r'*\1*', line)

        # Remove unnecessary backslash escapes for punctuation
        line = re.sub(r'\\([.,:;])', r'\1', line)

        final_lines.append(line)

    return '\n'.join(final_lines)

def main():
    input_file = "../tanaj.docx"
    output_file = "mishlei.md"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print(f"Converting '{input_file}' to extract Mishlei section...")

    with open(input_file, 'rb') as f:
        result = mammoth.convert_to_markdown(f)

    if result.messages:
        print("Conversion warnings:")
        for message in result.messages:
            print(f"  - {message}")

    raw_markdown = result.value
    print("Normalizing footnotes...")
    normalized_text = normalize_footnotes(raw_markdown)

    print("Extracting Mishlei section...")
    mishlei_text = extract_mishlei_section(normalized_text)

    if not mishlei_text:
        print("Error: Could not extract Mishlei section")
        sys.exit(1)

    print("Applying minimal formatting...")
    formatted_text = format_to_target_structure(mishlei_text)

    print("Cleaning formatting...")
    # Final cleanup
    formatted_text = re.sub(r'\n{3,}', '\n\n', formatted_text)

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_text)

    # Count chapters and verses
    chapters = len(re.findall(r'^__\d+__$', formatted_text, re.MULTILINE))
    verses = len(re.findall(r'__\d+__', formatted_text))

    print("✓ Mishlei extraction completed successfully!")
    print(f"  Generated file: {output_file}")
    print(f"  Size: {len(formatted_text)} characters")
    print(f"  Chapters detected: {chapters}")
    print(f"  Verse markers found: {verses}")

if __name__ == "__main__":
    main()
