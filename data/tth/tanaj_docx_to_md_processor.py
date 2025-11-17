#!/usr/bin/env python3
"""
Script to convert tanaj.docx to Markdown with chapter detection
- Detects book titles and formats with #
- Inserts ## Capítulo X when verse 1 is detected
- Keeps other content as-is
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
    text = re.sub(r'<a id="footnote-ref-(\d+)"[^>]*></a>\[\[\d+\]\]\(#footnote-\d+\)', r'[^\1]', text)
    text = re.sub(r'<a[^>]*id="footnote-ref-(\d+)"[^>]*></a>', r'[^\1]', text)
    text = re.sub(r'\[\^(\d+)\]\[\[\d+\]\]\(#footnote-\d+\)', r'[^\1]', text)
    text = re.sub(r'\[\^(\d+)\]\[\\?\[.*?\\?\]\]\(#footnote-\d+\)', r'[^\1]', text)
    text = re.sub(r'\[\^(\d+)\]\[\\?\[.*?\\?\]\]\s*\(#footnote-\d+\)', r'[^\1]', text)
    text = re.sub(r'\[\^(\d+)\]\s*\[\[\d+\]\]\(#footnote-\d+\)', r'[^\1]', text)

    def replace_footnote_definition(match):
        num = match.group(1)
        content = match.group(2).strip()
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\s+', ' ', content).strip()
        return f'\n[^{num}]: {content}\n'

    text = re.sub(
        r'<a id="footnote-(\d+)"[^>]*></a>\s*(.+?)(?=<a id="footnote-|\Z)',
        replace_footnote_definition,
        text,
        flags=re.DOTALL
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

        # Check for book title keywords - only if line is short, likely a title, and not already formatted
        book_title_found = None
        line_length = len(line.strip())
        # Only consider as book title if line is short (titles are short), doesn't contain verse markers, and not already a title
        if (line_length < 100 and line_length > 0 and not re.search(r'__\d+__', line) and
            not line.startswith('#') and not re.match(r'\[\^\d+\]:', line)):
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

        # Check if this line has a verse marker
        verse_num = extract_verse_num(line)
        if verse_num == 1 and current_chapter > 0:
            # Insert chapter number before verse 1
            formatted_lines.append(f"__{current_chapter}__")
            formatted_lines.append("")
            current_chapter += 1

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

        final_lines.append(line)

    return '\n'.join(final_lines)


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python tanaj_docx_to_md_processor.py <input.docx> [output.md]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) == 3 else "tanaj.md"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print(f"Converting '{input_file}' to '{output_file}'...")

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

        print("Applying minimal formatting...")
        markdown_text = format_to_target_structure(markdown_text)

        print("Cleaning formatting...")
        markdown_text = clean_markdown_text(markdown_text)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_text)

        size = len(markdown_text.encode('utf-8'))
        print("✓ Conversion completed successfully!")
        print(f"  Generated file: {output_file}")
        print(f"  Size: {size} characters")

    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
