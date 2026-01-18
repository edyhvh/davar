#!/usr/bin/env python3
"""
Markdown to JSON Converter Module
==================================

Converts individual book markdown files to simplified JSON format for TTH2.
Simplified version focused on the TTH2 workflow.

Features:
- Parses chapters and verses from markdown
- Extracts footnotes with superscript markers
- Detects Hebrew terms automatically
- Generates simplified JSON structure

Author: Davar Project
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

try:
    from .config import BOOKS_INFO, HEBREW_TERMS
    from .patterns import SECTION_HEADER_PATTERN
except ImportError:
    from config import BOOKS_INFO, HEBREW_TERMS
    from patterns import SECTION_HEADER_PATTERN

try:
    from .text_cleaner import get_cleaner
except ImportError:
    # Fallback for testing - try to import from parent directory
    try:
        from text_cleaner import get_cleaner
    except ImportError:
        # Final fallback
        def get_cleaner():
            return None


class TTH2MdToJson:
    """
    Converts individual book markdown files to simplified JSON format.
    """

    def __init__(self, book_key: str):
        """Initialize the converter for a specific book."""
        self.book_key = book_key
        self.book_info = BOOKS_INFO.get(book_key)
        self.hebrew_terms = HEBREW_TERMS
        self.footnote_definitions = {}
        self.text_cleaner = get_cleaner()

        if not self.book_info:
            raise ValueError(f"Book key '{book_key}' not found in books database")

    def read_markdown(self, file_path: str) -> str:
        """Read markdown file content."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_footnote_definitions(self, text: str):
        """Extract footnote definitions from document."""
        footnote_section_match = re.search(r'##\s*Footnotes\s*\n', text, re.IGNORECASE)
        if footnote_section_match:
            footnote_section = text[footnote_section_match.end():]
        else:
            footnote_section = text

        footnote_pattern = r'\[\^(\d+)\]:\s*(.+?)(?=\n\[|\n\n|$)'
        matches = re.finditer(footnote_pattern, footnote_section, re.MULTILINE | re.DOTALL)

        for match in matches:
            footnote_num = match.group(1)
            footnote_def = match.group(2).strip()
            footnote_def = re.sub(r'\*([^*]+)\*', r'\1', footnote_def)
            footnote_def = re.sub(r'\*\*([^*]+)\*\*', r'\1', footnote_def)
            footnote_def = re.sub(r'\s+', ' ', footnote_def).strip()
            self.footnote_definitions[footnote_num] = footnote_def

    def filter_section_headers(self, text: str) -> str:
        """
        Filter out section headers from the markdown text.

        Section headers appear as standalone italic lines like:
        *Anuncio del nacimiento de Iojanán*

        These should be removed before verse parsing to prevent them
        from being included in verse text.
        """
        lines = text.split('\n')
        filtered_lines = []

        # Section header indicators (Spanish keywords that indicate titles)
        title_indicators = [
            'anuncio', 'nacimiento', 'visita', 'profecía', 'crecimiento',
            'proclamación', 'inmersión', 'genealogía', 'tentación',
            'enseña', 'sanación', 'llamado', 'pregunta', 'advertencia',
            'parábola', 'emisión', 'regreso', 'reino', 'juicio',
            'bautismo', 'crucifixión', 'resurrección', 'ascensión',
            'introducción', 'saludo', 'justicia', 'venida', 'oración', 'despedida',
            'firmes', 'deber', 'trabajar', 'ansiedad',
            'siervos', 'vigilantes', 'fiel', 'infiel', 'división',
            'discuten', 'grande', 'humillado', 'humillación',
            'estregado', 'estrellas', 'proclamación', 'monte', 'sal',
            'luz', 'adulterio', 'juramento', 'venganza',
            'otros', 'leproso', 'ciegos', 'doce', 'discípulos', 'manda',
            'habla', 'parábolas', 'multitudes', 'sembrador', 'propósito',
            'cizaña', 'mostaza', 'levadura', 'tesoro', 'piedras',
            'preciosas', 'red', 'mar', 'hombre', 'sabio', 'natzrat',
            'muerte', 'oveja', 'perdida', 'deudores',
            'divorcio', 'obreros', 'viña', 'tercera', 'vez', 'jerijó',
            'boda', 'higuera', 'siervo', 'vírgenes', 'monedas', 'oro'
        ]

        for line in lines:
            stripped = line.strip()

            # Check if this is a standalone italic line that could be a section header
            section_match = SECTION_HEADER_PATTERN.match(stripped)
            if section_match:
                potential_header = section_match.group(1).strip()

                # Skip if it's too long (likely legitimate verse content)
                if len(potential_header.split()) > 10:
                    filtered_lines.append(line)
                    continue

                # Skip if it doesn't start with capital letter (likely not a title)
                if not potential_header[0].isupper():
                    filtered_lines.append(line)
                    continue

                # Check for section header indicators
                header_lower = potential_header.lower()
                if any(indicator in header_lower for indicator in title_indicators):
                    # This is a section header - skip it
                    continue

            # Keep the line
            filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    def extract_footnotes(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Extract footnotes from text and convert to superscript."""
        footnotes = []

        footnote_pattern = r'\[\^(\d+)\]'
        matches = list(re.finditer(footnote_pattern, text))

        def num_to_superscript(num_str):
            superscript_map = {
                '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
                '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
            }
            return ''.join(superscript_map.get(digit, digit) for digit in num_str)

        def extract_associated_word(text_before_marker: str) -> str:
            """Extract word associated with footnote."""
            text_before = text_before_marker.rstrip()

            compound_terms = [
                (r"Rúaj\s+Ha['']Kódesh", "Rúaj Ha'Kódesh"),
                (r"Ben\s+Ha['']Adam", "Ben Ha'Adam"),
                (r"Bet\s+Léjem", "Bet Léjem"),
                (r"Bet\s+Aniah", "Bet Aniah"),
            ]

            # Check for compound terms
            search_text = text_before[-50:] if len(text_before) > 50 else text_before
            for term_pattern, term_name in compound_terms:
                pattern = term_pattern + r'\s*$'
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    return term_name

            simple_word_pattern = r'([\w\'-]+)\s*$'
            match = re.search(simple_word_pattern, text_before)

            if match:
                word = match.group(1).strip()
                word = re.sub(r'[.,;:!?]+$', '', word)
                return word if word else ''

            return ''

        # Create mapping of footnote positions and associated words
        footnote_info = {}
        for match in matches:
            footnote_num = match.group(1)
            marker = num_to_superscript(footnote_num)
            definition = self.footnote_definitions.get(footnote_num, f'Nota al pie {footnote_num}')

            text_before = text[:match.start()]
            associated_word = extract_associated_word(text_before)

            footnote_info[footnote_num] = {
                'marker': marker,
                'definition': definition,
                'word': associated_word
            }

        # Replace all footnote markers with superscripts
        def replace_footnote(match):
            footnote_num = match.group(1)
            info = footnote_info[footnote_num]
            if not any(fn['number'] == footnote_num for fn in footnotes):
                footnotes.append({
                    'marker': info['marker'],
                    'number': footnote_num,
                    'word': info['word'],
                    'explanation': info['definition']
                })
            return info['marker']

        modified_text = re.sub(footnote_pattern, replace_footnote, text)

        footnotes.sort(key=lambda x: int(x['number']))
        return modified_text.strip(), footnotes

    def clean_text_preserve_comments(self, text: str) -> str:
        """
        Clean text while preserving comments, formatting, and italic emphasis.
        Simplified version to avoid regex hangs.
        """
        modified_text = text

        # Remove verse markers that may remain
        modified_text = re.sub(r'\*\*(\d+)\*\*', r'\1', modified_text)

        # Apply advanced text cleaning (this is the core functionality)
        modified_text = self.text_cleaner.clean_verse_text(modified_text)

        # Clean whitespace (simplified to avoid hangs)
        modified_text = ' '.join(modified_text.split()).strip()

        return modified_text


    def parse_chapters_and_verses(self, book_text: str, verbose: bool = False) -> List[Dict[str, Any]]:
        """Parse chapters and verses from the book text."""
        lines = book_text.split('\n')
        chapters = []

        current_chapter = None
        current_verses = []
        total_chapters_expected = self.book_info.get('chapters', 0)

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Stop parsing when we reach the footnotes section
            if line.startswith('## Footnotes') or line.startswith('# Footnotes'):
                break

            # Check for chapter markers
            chapter_match = re.match(r'^\*\*(\d+)\*\*\s*$', line)
            if chapter_match:
                # Save previous chapter if exists
                if current_chapter is not None and current_verses:
                    chapters.append({
                        'chapter': current_chapter,
                        'verses': current_verses
                    })

                current_chapter = int(chapter_match.group(1))
                current_verses = []
                i += 1
                continue

            # Process verses if we're in a chapter
            if current_chapter is not None:
                # Look for verse markers
                verse_match = re.match(r'^\*\*(\d+)\*\*\s*(.+)$', line)
                if verse_match:
                    verse_num = int(verse_match.group(1))
                    verse_text = verse_match.group(2).strip()

                    # Clean and process the verse
                    verse_text = self.clean_text_preserve_comments(verse_text)
                    verse_text, footnotes = self.extract_footnotes(verse_text)

                    verse_entry = {
                        'verse': verse_num,
                        'tth': verse_text,
                        'footnotes': footnotes,
                        'hebrew_terms': []
                    }

                    current_verses.append(verse_entry)
                    i += 1
                    continue

                # Continue accumulating verse text (multi-line verses)
                elif current_verses and line:
                    # Add to the last verse
                    last_verse = current_verses[-1]
                    last_verse['tth'] += ' ' + line.strip()

                    # Re-process the verse with the additional text
                    last_verse['tth'] = self.clean_text_preserve_comments(last_verse['tth'])
                    last_verse['tth'], last_verse['footnotes'] = self.extract_footnotes(last_verse['tth'])
                    last_verse['hebrew_terms'] = []

            i += 1

        # Save last chapter
        if current_chapter is not None and current_verses:
            chapters.append({
                'chapter': current_chapter,
                'verses': current_verses
            })

        return chapters

    def create_json_structure(self, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create the final JSON structure."""
        # Calculate statistics
        total_chapters = len(chapters)
        total_verses = sum(len(chapter['verses']) for chapter in chapters)

        # Create book info with proper structure
        book_info = {
            'book_id': self.book_key,
            'tth_name': self.book_info['tth_name'],
            'hebrew_name': self.book_info['hebrew_name'],
            'english_name': self.book_info['english_name'],
            'spanish_name': self.book_info['spanish_name'],
            'section': self.book_info['section'],
            'total_chapters': total_chapters,
            'total_verses': total_verses
        }

        # Create chapters structure
        chapters_structure = []
        for chapter_data in chapters:
            chapter_entry = {
                'chapter': chapter_data['chapter'],
                'verses': chapter_data['verses']
            }
            chapters_structure.append(chapter_entry)

        return {
            'book_info': book_info,
            'chapters': chapters_structure
        }

    def convert_markdown_to_json(self, input_file: str, output_file: Optional[str] = None, verbose: bool = False) -> str:
        """
        Convert a book markdown file to JSON.

        Args:
            input_file: Path to markdown file
            output_file: Path to output JSON file (auto-generated if None)
            verbose: If True, print detailed progress messages

        Returns:
            Path to the output JSON file
        """
        # Generate output filename if not provided
        if output_file is None:
            input_path = Path(input_file)
            output_file = str(input_path.with_suffix('.json'))

        # Read and process markdown
        markdown_text = self.read_markdown(input_file)

        # Filter out section headers before processing
        if verbose:
            print(f"    Filtering section headers...", end=' ', flush=True)
        markdown_text = self.filter_section_headers(markdown_text)
        if verbose:
            print(f"✓")

        # Extract footnote definitions
        if verbose:
            print(f"    Extracting footnotes...", end=' ', flush=True)
        self.extract_footnote_definitions(markdown_text)
        if verbose:
            print(f"✓ ({len(self.footnote_definitions)} found)")

        # Parse chapters and verses (show progress for large books)
        if verbose:
            print(f"    Parsing chapters and verses...", end=' ', flush=True)
        chapters = self.parse_chapters_and_verses(markdown_text, verbose=verbose)
        if verbose:
            print(f"✓")

        # Create JSON structure
        json_data = self.create_json_structure(chapters)

        # Write JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        if verbose:
            print(f"✓ Saved JSON to {output_file}")
            print(f"  Chapters: {json_data['book_info']['total_chapters']}")
            print(f"  Verses: {json_data['book_info']['total_verses']}")

        return output_file


def convert_book_markdown_to_json(book_key: str, input_file: str, output_file: Optional[str] = None, verbose: bool = False) -> str:
    """
    Convenience function to convert a book markdown file to JSON.

    Args:
        book_key: Book identifier
        input_file: Path to markdown file
        output_file: Path to output JSON file (optional)
        verbose: If True, print detailed progress messages

    Returns:
        Path to the output JSON file
    """
    converter = TTH2MdToJson(book_key)
    return converter.convert_markdown_to_json(input_file, output_file, verbose)