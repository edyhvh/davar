#!/usr/bin/env python3
"""
Script to extract Bereshit (Genesis) from tanaj.docx and create bereshit.md
- Extracts only the Bereshit section from the full Tanaj document
- Applies the same processing as tanaj_docx_to_md_processor.py
- Creates a clean bereshit.md file
"""

import sys
import os
import re
from pathlib import Path

try:
    import mammoth
except ImportError:
    print("Error: The 'mammoth' library is not installed.")
    print("Install it with: pip install mammoth")
    sys.exit(1)


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


def clean_markdown_text(text: str) -> str:
    """Clean markdown text of HTML elements."""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.rstrip()
        # Skip very long lines that look like base64 images
        if len(line) > 10000 and ('/' in line or '+' in line or 'data:image' in line):
            continue
        cleaned_lines.append(line)
    lines = cleaned_lines
    text = '\n'.join(lines)
    text = text.lstrip('\n')

    # More careful handling of asterisks - don't collapse * * patterns
    # Only collapse multiple consecutive asterisks, but preserve separate italic markers
    text = re.sub(r'\*{3,}', '**', text)  # ***+ becomes **
    text = re.sub(r'\\([.;:,!?])', r'\1', text)

    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if re.match(r'\[\^\d+\]:', line):
            line = re.sub(r'\s*\[[^\]]+\]\(#footnote-ref-\d+\)\s*\d*\.?\s*$', '', line)
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)

    return text


def extract_verse_num(line: str) -> int:
    """Extract verse number from line. Returns 1 if __ __, else the number, or 0 if no verse."""
    match = re.search(r'__(\d+)__', line)
    if match:
        return int(match.group(1))
    elif re.search(r'__\s+__', line) or line.strip().startswith('__ '):
        return 1
    return 0


# Book title mapping - keyword-based, ordered by length descending to avoid substring matches
BOOK_TITLE_MAPPING = [
    ('DIVREI HAYAMIM ALEF', '__DIVREI HAYAMIM ALEF (1 CRÓNICAS)*__דברי הימים א*'),
    ('DIVREI HAYAMIM BET', '__DIVREI HAYAMIM BET (2 CRÓNICAS)*__דברי הימים ב*'),
    ('SHIR HASHIRIM', '__SHIR HASHIRIM (CANTAR DE LOS CANTARES)*__שיר השירים*'),
    ('SHEMUEL ALEF', '__SHEMUEL ALEF (1 SAMUEL)*__א שמואל*'),
    ('SHEMUEL BET', '__SHEMUEL BET (2 SAMUEL)*__ב שמואל*'),
    ('MELAJIM ALEF', '__MELAJIM ALEF (1 REYES)*__א מלכים*'),
    ('MELAJIM BET', '__MELAJIM BET (2 REYES)*__ב מלכים*'),
    ('NEVIÍM - IEHOSHÚA', '__NEVIÍM - IEHOSHÚA (JOSUÉ)*__יהושע*'),
    ('KETUVIM - TEHILIM', '__KETUVIM - TEHILIM (SALMOS)*__תהלים*'),
    ('TORAH - BERESHIT', '__TORAH - BERESHIT (GÉNESIS)*__בראשית*'),
    ('IESHAIÁHU', '__IESHAIÁHU (ISAÍAS)*__ישעיהו*'),
    ('IRMEIÁHU', '__IRMEIÁHU (JEREMÍAS)*__ירמיהו*'),
    ('IEJEZKEL', '__IEJEZKEL (EZEQUIEL)*__יחזקאל*'),
    ('TSEFANYAH', '__TSEFANYAH (SOFONÍAS)*__צפניה*'),
    ('ZEJARIÁH', '__ZEJARIÁH (ZACARÍAS)*__זכריה*'),
    ('MALAJÍ', '__MALAJÍ (MALAQUÍAS)*__מלאכי*'),
    ('MISHLEI', '__MISHLEI (PROVERBIOS)*__משלי*'),
    ('QOHELET', '__QOHELET (ECLESIASTÉS)*__קהלת*'),
    ('NEJEMIAH', '__NEJEMIAH (NEHEMÍAS)*__נחמיה*'),
    ('IEHOSHÚA', '__NEVIÍM - IEHOSHÚA (JOSUÉ)*__יהושע*'),
    ('JABAQUQ', '__JABAQUQ (HABACUC)*__חבקוק*'),
    ('BAMIDBAR', '__BAMIDBAR (NÚMEROS)*__במדבר*'),
    ('DEVARIM', '__DEVARIM (DEUTERONOMIO)*__דברים*'),
    ('SHOFTÍM', '__SHOFTÍM (JUECES)*__שפטים*'),
    ('OVADYAH', '__OVADYAH (ABDÍAS)*__עבדיה*'),
    ('MIJAH', '__MIJAH (MIQUEAS)*__מיכה*'),
    ('NAJUM', '__NAJUM (NAHÚM)*__נחום*'),
    ('JAGGAI', '__JAGGAI (AGEO)*__חגי*'),
    ('TEHILIM', '__KETUVIM - TEHILIM (SALMOS)*__תהלים*'),
    ('BERESHIT', '__TORAH - BERESHIT (GÉNESIS)*__בראשית*'),
    ('HOSHEA', '__HOSHEA (OSEAS)*__הושע*'),
    ('VAIKRÁ', '__VAIKRÁ (LEVÍTICO)*__ויקרא*'),
    ('SHEMOT', '__SHEMOT (ÉXODO)*__שמות*'),
    ('EZRAH', '__EZRAH (ESDRA)*__עזרא*'),
    ('YONAH', '__YONAH (JONÁS)*__יונה*'),
    ('ESTER', '__ESTER*__אסתר*'),
    ('DANIEL', '__DANIEL*__דניאל*'),
    ('QOHELET', '__QOHELET (ECLESIASTÉS)*__קהלת*'),
    ('RUT', '__RUT*__רות*'),
    ('AMÓS', '__AMÓS*__עמוס*'),
    ('IOEL', '__IOEL (JOEL)*__יואל*'),
    ('IYOV', '__IYOV (JOB)*__אִיּוֹב*'),
    ('EJA', '__EJA (LAMENTACIONES)*__איכה*')
]


def extract_bereshit_section(text: str) -> str:
    """
    Extract only the Bereshit section from the full Tanaj text.
    Returns the text from Bereshit start until the next book starts, including relevant footnotes.
    """
    lines = text.split('\n')
    bereshit_start = -1
    bereshit_end = -1

    # Find Bereshit start - look for the actual book title, not TOC links
    for i, line in enumerate(lines):
        line_upper = line.upper()
        # Look for the formatted book title pattern, not the TOC link
        if ('TORAH - BERESHIT' in line_upper or 'בראשית' in line) and '__' in line and len(line.strip()) < 200:
            # Make sure it's not a TOC link (which contains '](#')
            if '](#' not in line:
                bereshit_start = i
                break

    if bereshit_start == -1:
        raise ValueError("Bereshit section not found in the document")

    # Find where Bereshit ends (next book starts)
    for i in range(bereshit_start + 1, len(lines)):
        line = lines[i].strip()
        line_upper = line.upper()

        # Skip empty lines and subtitles
        if not line or re.match(r'^\*([^*]+)\*$', line):
            continue

        # Only stop at the main title of the next Torah book (Shemot/Exodus)
        # Look for the exact pattern with escaped parentheses
        if line.strip() == '__SHEMOT \\(ÉXODO\\)__ שמות':
            bereshit_end = i
            break

    # If no next book found, take everything until footnotes start or end
    if bereshit_end == -1:
        for i in range(bereshit_start + 1, len(lines)):
            if re.match(r'\[\^\d+\]:', lines[i]) or '<a id="footnote-' in lines[i]:
                bereshit_end = i
                break

    # If still no end found, take all remaining content
    if bereshit_end == -1:
        bereshit_end = len(lines)

    # Extract Bereshit section
    bereshit_lines = lines[bereshit_start:bereshit_end]

    # Find all footnote numbers used in Bereshit
    bereshit_text = '\n'.join(bereshit_lines)
    footnote_nums = set()
    # Find footnote references like [^1]
    for match in re.finditer(r'\[\^(\d+)\]', bereshit_text):
        footnote_nums.add(int(match.group(1)))

    # Extract footnote definitions that belong to Bereshit
    footnote_lines = []
    for i in range(len(lines)):
        line = lines[i]
        # Check for footnote definition patterns [^1]: content
        footnote_def_match = re.match(r'\[\^(\d+)\]:\s*(.+)', line)
        if footnote_def_match:
            footnote_num = int(footnote_def_match.group(1))
            if footnote_num in footnote_nums:
                footnote_lines.append(line)

    # Add "## Footnotes" header before footnote definitions
    if footnote_lines:
        footnote_lines.insert(0, "")
        footnote_lines.insert(0, "## Footnotes")

    return '\n'.join(bereshit_lines + footnote_lines)


def format_to_target_structure(text: str) -> str:
    """
    Format with book titles and chapter detection
    """
    lines = text.split('\n')
    formatted_lines = []
    current_chapter = 0  # Will be set to 1 when book starts

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Detect start of footnotes section
        if re.match(r'\[\^\d+\]:', line):
            formatted_lines.append(line)
            i += 1
            continue

        # Check for book title keywords - only for the main book title at the beginning
        book_title_found = None
        line_length = len(line.strip())
        # Only consider as book title if line is short, contains the Torah book pattern, and is at the beginning
        # Also check that it's likely a title by having specific formatting
        if (line_length < 150 and line_length > 0 and 'TORAH' in line.upper() and
            line.count('__') >= 2 and not line.startswith('#') and not re.match(r'\[\^\d+\]:', line)):
            for keyword, formatted in BOOK_TITLE_MAPPING:
                if keyword in line.upper():
                    book_title_found = formatted
                    break

        if book_title_found:
            formatted_lines.append(f"# {book_title_found}")
            formatted_lines.append("")
            current_chapter = 1  # Reset chapter for new book
            i += 1
            continue

        # DETECT SUBTITLES (keep as *subtitle*)
        subtitle_match = re.match(r'^\*([^*]+)\*$', line)
        if subtitle_match:
            formatted_lines.append(line)
            formatted_lines.append("")
            i += 1
            continue

        # Check if this is a chapter marker (like __29__)
        chapter_match = re.match(r'^__(\d+)__$', line)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            formatted_lines.append(line)
            formatted_lines.append("")
            current_chapter = chapter_num
            i += 1
            continue

        # Check if this line has a verse marker
        verse_num = extract_verse_num(line)

        # If we just processed a chapter marker and this line has content
        if (formatted_lines and formatted_lines[-1] == "" and
            len(formatted_lines) >= 2 and formatted_lines[-2] == f"__{current_chapter}__" and
            line.strip()):
            # Check if it starts with __ __ (indicating malformed verse 1)
            if line.startswith('__ __'):
                # Replace __ __ with __1__
                line = line.replace('__ __', '__1__', 1)
            elif not re.match(r'^__\d+__', line) and verse_num == 0:
                # This is the first verse of the chapter, add __1__
                line = f"__1__ {line}"

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
        # Convert "*word*" with missing spaces: "*al*hombre" -> "*al* hombre"
        line = re.sub(r'\*([a-záéíóúñA-ZÁÉÍÓÚÑ]+)\*([a-záéíóúñA-ZÁÉÍÓÚÑ])', r'*\1* \2', line)
        # But don't collapse ** patterns (bold) - only fix ***+
        line = re.sub(r'\*{3,}', '**', line)

        line = re.sub(r'(\S)\s+(\[\^\d+\])', r'\1\2', line)

        # Fix duplicate verse markers: __1__ __1__ -> __1__
        line = re.sub(r'__(\d+)__\s+__(\d+)__', r'__\1__', line)

        # Fix verse markers with extra spaces: __8 __ -> __8__
        line = re.sub(r'__(\d+)\s+__', r'__\1__', line)
        # Ensure proper spacing after verse numbers: __8__Text -> __8__ Text
        line = re.sub(r'__(\d+)__([A-ZÁÉÍÓÚÑa-záéíóúñ\u0590-\u05FF])', r'__\1__ \2', line)

        # Remove unnecessary backslash escapes for punctuation
        line = re.sub(r'\\([.,:;])', r'\1', line)

        final_lines.append(line)

    return '\n'.join(final_lines)


def main():
    # Path to the tanaj.docx file (assuming it's in the parent directory)
    input_file = "../tanaj.docx"  # Adjust path as needed
    output_file = "bereshit.md"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        print("Please ensure tanaj.docx is in the ../ directory")
        sys.exit(1)

    print(f"Converting '{input_file}' to extract Bereshit section...")

    try:
        with open(input_file, 'rb') as f:
            result = mammoth.convert_to_markdown(f)

        if result.messages:
            print("Conversion warnings:")
            for message in result.messages:
                print(f"  - {message}")

        markdown_text = result.value

        print("Normalizing footnotes...")
        markdown_text = normalize_footnotes(markdown_text)

        print("Extracting Bereshit section...")
        bereshit_text = extract_bereshit_section(markdown_text)

        print("Applying minimal formatting...")
        bereshit_text = format_to_target_structure(bereshit_text)

        print("Cleaning formatting...")
        bereshit_text = clean_markdown_text(bereshit_text)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(bereshit_text)

        size = len(bereshit_text.encode('utf-8'))
        print("✓ Bereshit extraction completed successfully!")
        print(f"  Generated file: {output_file}")
        print(f"  Size: {size} characters")

        # Count chapters and verses for QA
        chapters = len(re.findall(r'^__\d+__$', bereshit_text, re.MULTILINE))
        verses = len(re.findall(r'__\d+__', bereshit_text))
        print(f"  Chapters detected: {chapters}")
        print(f"  Verse markers found: {verses}")

    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
