#!/usr/bin/env python3
"""
TTH Thessalonikim Markdown Processor - Structures the content of the Traducción Textual del Hebreo
for 1 and 2 Thessalonians from Markdown format to JSON similar to TS2009.

Target format:
- Each chapter has a separate JSON file (01.json, 02.json, etc.)
- Structure compatible with the Davar app
- Includes Hebrew terms detection and footnotes
"""

import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple


class TTHMarkdownProcessor:
    def __init__(self, input_file: str = 'tesaloniquim.md'):
        self.input_file = input_file
        self.output_dir = 'draft'
        self.books_info = {
            'tesaloniquim_alef': {
                'tth_name': 'Tesaloniquim Álef',
                'hebrew_name': 'תסלוניקים א',
                'english_name': '1 Thessalonians',
                'spanish_name': '1 Tesalonicenses',
                'book_code': '1thess',
                'expected_chapters': 5
            },
            'tesaloniquim_bet': {
                'tth_name': 'Tesaloniquim Bet',
                'hebrew_name': 'תסלוניקים ב',
                'english_name': '2 Thessalonians',
                'spanish_name': '2 Tesalonicenses',
                'book_code': '2thess',
                'expected_chapters': 3
            }
        }

        # Common Hebrew terms to detect
        self.hebrew_terms = {
            'YEHOVAH': 'Tetragrámaton - Name of God',
            'Yehovah': 'Tetragrámaton - Name of God',
            'Yeshúa': 'Jesus in Hebrew',
            'Mesías': 'The Anointed One, Christ',
            'Elohim': 'God, Mighty One',
            'Eloha': 'Singular of Elohim',
            'Elohah': 'Singular of Elohim',
            'EL': 'Short version of Elohim',
            'Adón': 'Lord, Master',
            'Rúaj': 'Spirit, wind, breath',
            'Ha\'Kódesh': 'Holy',
            'Rúaj Ha\'Kódesh': 'Spirit of Holiness',
            'emunah': 'faith, faithfulness, constancy',
            'shalom': 'peace, complete wellbeing',
            'Ha\'satán': 'The adversary',
            'Kadosh': 'Set apart, Holy',
            'Teshuváh': 'Return, repentance',
            'Malajim': 'Messengers, angels',
            'Tzebaot': 'Hosts, Armies',
            'Hejal': 'Sanctuary, Palace',
            'Ierushaláim': 'Jerusalem',
            'Iehudáh': 'Judah',
            'Iehudí': 'Jewish',
            'Mitzráim': 'Egypt',
            'Shofar': 'Ram\'s horn',
            'Menorah': 'Golden candlestick',
            'Guei Hinom': 'Valley of Hinom, Gehenna',
            'Paúlus': 'Paul',
            'Iehudim': 'Jews',
            'Notzrí': 'Nazarene'
        }

        # Mapping of footnote numbers to superscript markers
        self.footnote_markers = {
            1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵',
            6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹', 10: '¹⁰',
            11: '¹¹', 12: '¹²', 13: '¹³', 14: '¹⁴', 15: '¹⁵',
            16: '¹⁶', 17: '¹⁷', 18: '¹⁸', 19: '¹⁹', 20: '²⁰',
            21: '²¹', 22: '²²', 23: '²³', 24: '²⁴', 25: '²⁵',
            26: '²⁶', 27: '²⁷', 28: '²⁸', 29: '²⁹', 30: '³⁰',
            31: '³¹', 32: '³²', 33: '³³', 34: '³⁴', 35: '³⁵',
            36: '³⁶', 37: '³⁷', 38: '³⁸', 39: '³⁹', 40: '⁴⁰',
            41: '⁴¹', 42: '⁴²', 43: '⁴³', 44: '⁴⁴', 45: '⁴⁵',
            46: '⁴⁶', 47: '⁴⁷', 48: '⁴⁸', 49: '⁴⁹', 50: '⁵⁰',
            51: '⁵¹', 52: '⁵²', 53: '⁵³', 54: '⁵⁴', 55: '⁵⁵',
            56: '⁵⁶', 57: '⁵⁷', 58: '⁵⁸', 59: '⁵⁹', 60: '⁶⁰',
            61: '⁶¹', 62: '⁶²', 63: '⁶³', 64: '⁶⁴', 65: '⁶⁵',
            66: '⁶⁶', 67: '⁶⁷', 68: '⁶⁸', 69: '⁶⁹', 70: '⁷⁰',
            71: '⁷¹', 72: '⁷²', 73: '⁷³', 74: '⁷⁴', 75: '⁷⁵'
        }

    def read_markdown(self) -> str:
        """Reads the markdown file"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_footnotes(self, text: str) -> Dict[int, str]:
        """Extracts footnote definitions from the markdown"""
        footnotes = {}
        # Search for patterns [^number]: text
        pattern = r'\[(\^?\d+)\]:\s*(.+?)(?=\n\[|\n\n|$)'
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)

        for num_str, explanation in matches:
            # Clean the number (may come with ^ or without it)
            num = int(num_str.replace('^', ''))
            # Clean the explanation
            explanation = explanation.strip()
            # Remove references to other verses like "Thus also in verse 3."
            explanation = re.sub(r'\s*Así también en vers?\.?\s*\d+.*?\.', '', explanation)
            explanation = re.sub(r'\s*Así también en los versículos.*?\.', '', explanation)
            explanation = re.sub(r'\s*Así también en cap\.\s*\d+.*?\.', '', explanation)
            explanation = re.sub(r'\s*Así también en los versículos.*?\.', '', explanation)
            # Remove markdown formatting (italic, bold)
            explanation = re.sub(r'\*([^*]+)\*', r'\1', explanation)  # Remove italic
            explanation = re.sub(r'\*\*([^*]+)\*\*', r'\1', explanation)  # Remove bold
            # Clean multiple spaces
            explanation = re.sub(r'\s+', ' ', explanation).strip()
            footnotes[num] = explanation

        return footnotes

    def split_into_books(self, text: str) -> Dict[str, str]:
        """Divides the text into the two Thessalonian letters"""
        books = {}

        # Find the boundaries of each book
        alef_match = re.search(r'\*\*TESALONIQUIM ÁLEF \(1 TESALONICENSES\)\*\*', text)
        bet_match = re.search(r'\*\*TESALONIQUIM BET \(2 TESALONICENSES\)\*\*', text)

        if alef_match and bet_match:
            # Extract 1 Thessalonians (without including footnotes at the end)
            alef_start = alef_match.start()
            # Search where the first book's footnotes end
            # Footnotes are before the second book's start
            books['tesaloniquim_alef'] = text[alef_start:bet_match.start()]

            # Extract 2 Thessalonians (from BET start to the end)
            books['tesaloniquim_bet'] = text[bet_match.start():]

        return books

    def extract_chapters(self, book_text: str, book_key: str, all_footnotes: Dict[int, str]) -> List[Dict[str, Any]]:
        """Extracts chapters from a book from the markdown"""
        chapters = []

        # Divide text into chapter sections
        lines = book_text.split('\n')
        current_chapter = None
        current_verses = []
        current_verse_num = None
        current_verse_text = []
        in_chapter_section = False

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Detect chapter start - **number** followed by empty line
            # This appears before verses
            chapter_match = re.match(r'^\*\*(\d+)\*\*\s*$', line)
            if chapter_match:
                # Save previous chapter if it exists
                if current_chapter is not None and current_verses:
                    chapters.append({
                        'chapter': current_chapter,
                        'verses': current_verses
                    })

                # Start new chapter
                current_chapter = int(chapter_match.group(1))
                current_verses = []
                current_verse_num = None
                current_verse_text = []
                in_chapter_section = True
                i += 1
                # Skip empty lines and italic titles after chapter number
                while i < len(lines) and (not lines[i].strip() or lines[i].strip().startswith('*')):
                    i += 1

                # Check if the next line is verse 1 without marker
                # (this occurs in some chapters where verse 1 has no **1**)
                if i < len(lines):
                    next_line = lines[i].strip()
                    # If next line is not a marked verse with **number**, it's verse 1
                    if not re.match(r'^\*\*\d+\*\*', next_line) and next_line:
                        current_verse_num = 1
                        current_verse_text = [next_line]
                        i += 1
                continue

            # Only process verses if we're in a chapter section
            if in_chapter_section:
                # Detect verse - pattern **number** followed by text on same line
                verse_match = re.match(r'^\*\*(\d+)\*\*\s+(.+)$', line)
                if verse_match:
                    # Save previous verse if it exists
                    if current_verse_num is not None:
                        verse_text = ' '.join(current_verse_text).strip()
                        if verse_text:
                            verse_text, verse_footnotes = self.process_footnotes_in_text(verse_text, all_footnotes)
                            current_verses.append({
                                'verse': current_verse_num,
                                'text': verse_text,
                                'footnotes': verse_footnotes,
                                'hebrew_terms': self.extract_hebrew_terms(verse_text)
                            })

                    # Start new verse
                    current_verse_num = int(verse_match.group(1))
                    current_verse_text = [verse_match.group(2)]
                    i += 1
                    continue

                # If we're in a verse, add line to text (verse continuation)
                if current_verse_num is not None:
                    # If next line is another verse or chapter, end this verse
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        # Check if next line is a new verse or chapter
                        if re.match(r'^\*\*\d+\*\*', next_line):
                            # Save current verse
                            verse_text = ' '.join(current_verse_text).strip()
                            if verse_text:
                                verse_text, verse_footnotes = self.process_footnotes_in_text(verse_text, all_footnotes)
                                current_verses.append({
                                    'verse': current_verse_num,
                                    'text': verse_text,
                                    'footnotes': verse_footnotes,
                                    'hebrew_terms': self.extract_hebrew_terms(verse_text)
                                })
                            current_verse_num = None
                            current_verse_text = []
                        elif line and not line.startswith('*'):  # Ignore italic titles
                            # Continue adding to current verse
                            current_verse_text.append(line)
                    elif line and not line.startswith('*'):  # Ignore italic titles
                        current_verse_text.append(line)

            i += 1

        # Save last verse and chapter
        if current_verse_num is not None:
            verse_text = ' '.join(current_verse_text).strip()
            if verse_text:
                verse_text, verse_footnotes = self.process_footnotes_in_text(verse_text, all_footnotes)
                current_verses.append({
                    'verse': current_verse_num,
                    'text': verse_text,
                    'footnotes': verse_footnotes,
                    'hebrew_terms': self.extract_hebrew_terms(verse_text)
                })

        if current_chapter is not None and current_verses:
            chapters.append({
                'chapter': current_chapter,
                'verses': current_verses
            })

        return chapters

    def process_footnotes_in_text(self, text: str, all_footnotes: Dict[int, str]) -> Tuple[str, List[Dict[str, str]]]:
        """Processes footnote references in the text and converts them to superscript format"""
        footnotes = []
        modified_text = text

        # Find all [^number] references in the text
        # They can come as [^1] or [1]
        footnote_pattern = r'\[(\^?\d+)\]'

        # Create position mapping to process from right to left
        footnote_positions = []
        for match in re.finditer(footnote_pattern, modified_text):
            ref = match.group(1)
            num = int(ref.replace('^', ''))
            if num in all_footnotes:
                footnote_positions.append((match.start(), match.end(), num))

        # Sort by position descending (right to left)
        footnote_positions.sort(key=lambda x: x[0], reverse=True)

        # Process each reference
        for start, end, num in footnote_positions:
            marker = self.footnote_markers.get(num, f'[{num}]')
            explanation = all_footnotes[num]

            # Find associated word before the note
            # Search backwards from note position
            text_before = modified_text[:start].rstrip()
            # Find last word before note (may include special characters like apostrophes)
            # Pattern to find word with possible Hebrew special characters
            word_match = re.search(r'([\w\'’-]+)\s*$', text_before)
            word = word_match.group(1) if word_match else ''

            # Replace [^number] or [number] with superscript marker
            modified_text = modified_text[:start] + marker + modified_text[end:]

            # Add to footnotes (reverse order so they appear in order)
            footnotes.insert(0, {
                'marker': marker,
                'word': word,
                'explanation': explanation
            })

        # Clean the text (remove italic titles and other markdown elements)
        # Preserve italic text but remove asterisks
        modified_text = re.sub(r'\*([^*]+)\*', r'\1', modified_text)
        # Clean multiple spaces but preserve single spaces
        modified_text = re.sub(r'\s+', ' ', modified_text).strip()

        return modified_text, footnotes

    def extract_hebrew_terms(self, text: str) -> List[Dict[str, str]]:
        """Extracts Hebrew terms from the text"""
        terms_found = []
        text_lower = text.lower()

        # Search terms in length order (longest first)
        sorted_terms = sorted(self.hebrew_terms.items(), key=lambda x: len(x[0]), reverse=True)

        found_terms = set()  # To avoid duplicates

        for term, explanation in sorted_terms:
            # Search for term considering capitalization variations
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            if pattern.search(text) and term not in found_terms:
                terms_found.append({
                    'term': term,
                    'explanation': explanation
                })
                found_terms.add(term)

        return terms_found

    def create_json_structure(self, book_key: str, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Creates the final JSON structure compatible with the app"""
        book_info = self.books_info[book_key]
        json_data = []

        for chapter_data in chapters:
            chapter_num = chapter_data['chapter']

            for verse_data in chapter_data['verses']:
                verse_entry = {
                    'book': book_key.replace('_', ''),
                    'book_tth_name': book_info['tth_name'],
                    'book_hebrew_name': book_info['hebrew_name'],
                    'book_english_name': book_info['english_name'],
                    'book_spanish_name': book_info['spanish_name'],
                    'chapter': chapter_num,
                    'verse': verse_data['verse'],
                    'status': 'present',
                    'tth': verse_data['text'],
                    'footnotes': verse_data.get('footnotes', []),
                    'hebrew_terms': verse_data.get('hebrew_terms', [])
                }
                json_data.append(verse_entry)

        return json_data

    def save_chapter_files(self, book_key: str, json_data: List[Dict[str, Any]]):
        """Saves JSON files per chapter"""
        book_info = self.books_info[book_key]

        # Create directory with Hebrew name (alef/bet)
        book_dir = f"{self.output_dir}/{book_key}"
        os.makedirs(book_dir, exist_ok=True)

        # Group by chapters
        chapters_data = {}
        for verse in json_data:
            chapter = verse['chapter']
            if chapter not in chapters_data:
                chapters_data[chapter] = []
            chapters_data[chapter].append(verse)

        # Save each chapter
        for chapter_num, verses in sorted(chapters_data.items()):
            filename = f"{chapter_num:02d}.json"
            filepath = f"{book_dir}/{filename}"

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(verses, f, ensure_ascii=False, indent=2)

            print(f"Saved: {filepath} ({len(verses)} verses)")

        # Save book information
        book_info_data = {
            **book_info,
            'total_chapters': len(chapters_data),
            'total_verses': len(json_data),
            'source_file': self.input_file,
            'processed_date': datetime.now().isoformat(),
            'processor_version': '2.0-markdown'
        }

        with open(f"{book_dir}/book_info.json", 'w', encoding='utf-8') as f:
            json.dump(book_info_data, f, ensure_ascii=False, indent=2)

        print(f"Saved: {book_dir}/book_info.json")

    def process(self):
        """Main process"""
        print("Starting TTH Thessalonians processing from Markdown...")

        # Read markdown
        markdown_text = self.read_markdown()
        print(f"Markdown read: {len(markdown_text)} characters")

        # Extract all footnotes first
        all_footnotes = self.extract_footnotes(markdown_text)
        print(f"Footnotes found: {len(all_footnotes)}")

        # Divide into books
        books = self.split_into_books(markdown_text)
        print(f"Books found: {list(books.keys())}")

        # Process each book
        for book_key, book_text in books.items():
            print(f"\nProcessing {book_key}...")

            # Extract chapters
            chapters = self.extract_chapters(book_text, book_key, all_footnotes)
            print(f"Chapters found: {len(chapters)}")

            # Create JSON structure
            json_data = self.create_json_structure(book_key, chapters)
            print(f"Total verses: {len(json_data)}")

            # Save files
            self.save_chapter_files(book_key, json_data)

        print("\nProcessing completed successfully!")


def main():
    processor = TTHMarkdownProcessor()
    processor.process()


if __name__ == '__main__':
    main()














