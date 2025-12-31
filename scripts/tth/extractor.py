#!/usr/bin/env python3
"""
Book Extractor Module
=====================

Extracts individual book sections from complete TTH documents.

Features:
- Identifies book boundaries in complete documents
- Extracts book content with associated footnotes
- Handles Hebrew and Spanish text properly
- Maintains document structure and formatting

Author: Davar Project
"""

import re
from typing import Dict, List, Optional, Tuple, Set


class TTHBookExtractor:
    """
    Extracts individual book sections from complete TTH documents.
    """

    # Document sources
    DOCUMENT_SOURCES = {
        'tanaj': 'data/tth/raw/tanaj.docx',
        'besorah': 'data/tth/raw/besorah.docx',
        'sodot_iaacob_iehudah': 'data/tth/raw/sodot_iaacob_iehudah.docx',
        'tesaloniquim': 'data/tth/raw/tesaloniquim.docx'
    }

    # Book identification patterns - ordered by specificity (longest first)
    BOOK_PATTERNS = [
        # Besorah (Nuevo Testamento)
        ('matityahu', [
            r'Matityáhu.*?מתתיהו',
            r'Matityahu.*?מתתיהו',
            r'__MATITYÁHU.*?מתתיהו__',
            r'MATEO.*?מתתיהו',
            r'מתתיהו'
        ]),
        ('markos', [
            r'Markos.*?מרקוס',
            r'__MARKOS.*?מרקוס__',
            r'MARCOS.*?מרקוס',
            r'מרקוס'
        ]),
        ('lukas', [
            r'Lukas.*?לוקס',
            r'__LUKAS.*?לוקס__',
            r'LUCAS.*?לוקס',
            r'לוקס'
        ]),
        ('iojanan', [
            r'Iojanán.*?יוחנן',
            r'__IOJANÁN.*?יוחנן__',
            r'JUAN.*?יוחנן',
            r'יוחנן'
        ]),
        ('maasei_hashlijim', [
            r'Maasei\s+Hash\'lijim.*?מעשי\s+השליחים',
            r'__MAASEI.*?מעשי\s+השליחים__',
            r'HECHOS.*?מעשי\s+השליחים',
            r'מעשי\s+השליחים'
        ]),
        ('romaim', [
            r'Romaim.*?רומאים',
            r'__ROMAIM.*?רומאים__',
            r'ROMANOS.*?רומאים',
            r'רומאים'
        ]),
        ('iaacob', [
            r'\*\*IAACOB.*?\*\*',
            r'Iaacob.*?יעקב',
            r'__IAACOB.*?יעקב__',
            r'SANTIAGO.*?יעקב',
            r'\*\*IAACOB',
            r'SANTIAGO',
            r'יעקב'
        ]),
        ('iehudah', [
            r'\*\*IEHUDÁH.*?\*\*',
            r'Iehudáh.*?יהודה',
            r'__IEHUDÁH.*?יהודה__',
            r'JUDAS.*?יהודה',
            r'\*\*IEHUDÁH',
            r'JUDAS',
            r'יהודה'
        ]),
        ('sodot', [
            r'\*\*SODOT.*?\*\*',
            r'Sodot.*?סודות',
            r'__SODOT.*?סודות__',
            r'APOCALIPSIS.*?סודות',
            r'\*\*SODOT',
            r'APOCALIPSIS',
            r'סודות'
        ]),
        ('tesaloniquim_alef', [
            r'Tesaloniquim\s+Alef.*?תסלוניקים\s+א',
            r'Tesaloniquenses\s+1.*?תסלוניקים\s+א',
            r'__TESALONIKIM\s+ALEF.*?תסלוניקים\s+א__',
            r'תסלוניקים\s+א'
        ]),
        ('tesaloniquim_bet', [
            r'Tesaloniquim\s+Bet.*?תסלוניקים\s+ב',
            r'Tesaloniquenses\s+2.*?תסלוניקים\s+ב',
            r'__TESALONIKIM\s+BET.*?תסלוניקים\s+ב__',
            r'תסלוניקים\s+ב'
        ]),

        # Torah (Pentateuco)
        ('bereshit', [
            r'TORAH\s*-\s*BERESHIT.*?בראשית',
            r'__TORAH\s*-\s*BERESHIT.*?בראשית__',
            r'BERESHIT.*?בראשית',
            r'בראשית'
        ]),
        ('shemot', [
            r'SHEMOT.*?שמות',
            r'__SHEMOT.*?שמות__',
            r'שמות'
        ]),
        ('vaikra', [
            r'VAIKRÁ.*?ויקרא',
            r'__VAIKRÁ.*?ויקרא__',
            r'ויקרא'
        ]),
        ('bamidbar', [
            r'BAMIDBAR.*?במדבר',
            r'__BAMIDBAR.*?במדבר__',
            r'במדבר'
        ]),
        ('devarim', [
            r'DEVARIM.*?דברים',
            r'__DEVARIM.*?דברים__',
            r'דברים'
        ]),

        # Neviim (Profetas)
        ('iehosua', [
            r'IEHOSHÚA.*?יהושע',
            r'NEVIÍM\s*-\s*IEHOSHÚA.*?יהושע',
            r'__NEVIÍM\s*-\s*IEHOSHÚA.*?יהושע__',
            r'יהושע'
        ]),
        ('shoftim', [
            r'SHOFTÍM.*?שפטים',
            r'__SHOFTÍM.*?שפטים__',
            r'שפטים'
        ]),
        ('shemuel_alef', [
            r'SHEMUEL\s*ALEF.*?א\s*שמואל',
            r'__SHEMUEL\s*ALEF.*?א\s*שמואל__',
            r'א\s*שמואל'
        ]),
        ('shemuel_bet', [
            r'SHEMUEL\s*BET.*?ב\s*שמואל',
            r'__SHEMUEL\s*BET.*?ב\s*שמואל__',
            r'ב\s*שמואל'
        ]),
        ('melajim_alef', [
            r'MELAJIM\s*ALEF.*?א\s*מלכים',
            r'__MELAJIM\s*ALEF.*?א\s*מלכים__',
            r'א\s*מלכים'
        ]),
        ('melajim_bet', [
            r'MELAJIM\s*BET.*?ב\s*מלכים',
            r'__MELAJIM\s*BET.*?ב\s*מלכים__',
            r'ב\s*מלכים'
        ]),
        ('ieshaiahu', [
            r'IESHAIÁHU.*?ישעיהו',
            r'__IESHAIÁHU.*?ישעיהו__',
            r'ישעיהו'
        ]),
        ('irmeiahu', [
            r'IRMEIÁHU.*?ירמיהו',
            r'__IRMEIÁHU.*?ירמיהו__',
            r'ירמיהו'
        ]),
        ('iejezkel', [
            r'IEJEZKEL.*?יחזקאל',
            r'__IEJEZKEL.*?יחזקאל__',
            r'יחזקאל'
        ]),
        ('hoshea', [
            r'HOSHEA.*?הושע',
            r'__HOSHEA.*?הושע__',
            r'הושע'
        ]),
        ('ioel', [
            r'IOEL.*?יואל',
            r'__IOEL.*?יואל__',
            r'יואל'
        ]),
        ('amos', [
            r'AMÓS.*?עמוס',
            r'__AMÓS.*?עמוס__',
            r'עמוס'
        ]),
        ('ionah', [
            r'IONAH.*?יונה',
            r'__IONAH.*?יונה__',
            r'יונה'
        ]),
        ('micah', [
            r'MICAH.*?מיכה',
            r'__MICAH.*?מיכה__',
            r'מיכה'
        ]),
        ('najum', [
            r'NAJUM.*?נחום',
            r'__NAJUM.*?נחום__',
            r'נחום'
        ]),
        ('jabakuk', [
            r'JABAKUK.*?חבקוק',
            r'__JABAKUK.*?חבקוק__',
            r'חבקוק'
        ]),
        ('tzefaniah', [
            r'TZEFANIAH.*?צפניה',
            r'__TZEFANIAH.*?צפניה__',
            r'צפניה'
        ]),
        ('jagai', [
            r'JAGAI.*?חגי',
            r'__JAGAI.*?חגי__',
            r'חגי'
        ]),
        ('zejariah', [
            r'ZEJARIAH.*?זכריה',
            r'__ZEJARIAH.*?זכריה__',
            r'זכריה'
        ]),
        ('malaji', [
            r'MALAJI.*?מלאכי',
            r'__MALAJI.*?מלאכי__',
            r'מלאכי'
        ]),

        # Ketuvim (Escritos)
        ('tehilim', [
            r'KETUVIM\s*-\s*TEHILIM.*?תהלים',
            r'TEHILIM.*?תהלים',
            r'__KETUVIM\s*-\s*TEHILIM.*?תהלים__',
            r'__TEHILIM.*?תהלים__',
            r'תהלים'
        ]),
        ('mishlei', [
            r'MISHLEI.*?משלי',
            r'__MISHLEI.*?משלי__',
            r'משלי'
        ])
    ]

    def __init__(self):
        """Initialize the book extractor."""
        self.book_patterns = dict(self.BOOK_PATTERNS)
        # Map books to their source documents
        self.BOOK_SOURCES = {
            # Tanaj books
            'bereshit': 'tanaj', 'shemot': 'tanaj', 'vaikra': 'tanaj', 'bamidbar': 'tanaj', 'devarim': 'tanaj',
            'iehosua': 'tanaj', 'shoftim': 'tanaj', 'shemuel_alef': 'tanaj', 'shemuel_bet': 'tanaj',
            'melajim_alef': 'tanaj', 'melajim_bet': 'tanaj', 'ieshaiahu': 'tanaj', 'irmeiahu': 'tanaj',
            'iejezkel': 'tanaj', 'hoshea': 'tanaj', 'ioel': 'tanaj', 'amos': 'tanaj', 'ionah': 'tanaj',
            'micah': 'tanaj', 'najum': 'tanaj', 'jabakuk': 'tanaj', 'tzefaniah': 'tanaj', 'jagai': 'tanaj',
            'zejariah': 'tanaj', 'malaji': 'tanaj', 'tehilim': 'tanaj', 'mishlei': 'tanaj',

            # Besorah books
            'matityahu': 'besorah', 'markos': 'besorah', 'lukas': 'besorah', 'iojanan': 'besorah',
            'maasei_hashlijim': 'besorah', 'romaim': 'besorah', 'iaacob': 'sodot_iaacob_iehudah',
            'iehudah': 'sodot_iaacob_iehudah', 'sodot': 'sodot_iaacob_iehudah',
            'tesaloniquim_alef': 'tesaloniquim', 'tesaloniquim_bet': 'tesaloniquim'
        }

    def find_book_boundaries(self, text: str, book_key: str) -> Tuple[int, int]:
        """
        Find the start and end line numbers for a specific book.

        Args:
            text: Complete document text
            book_key: Book identifier (e.g., 'bereshit', 'shemot')

        Returns:
            Tuple of (start_line, end_line)
        """
        lines = text.split('\n')
        patterns = self.book_patterns.get(book_key, [])

        if not patterns:
            raise ValueError(f"Book '{book_key}' not found in pattern definitions")

        # Find book start
        book_start = -1
        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Skip empty lines
            if not line_stripped:
                continue

            # Check if line is too long (likely not a title)
            if len(line_stripped) > 200:
                continue

            # Check for TOC links (skip them)
            if '](#' in line_stripped:
                continue

            # Check for actual book header first (highest priority)
            if line_stripped.startswith('**') and re.search(r'\*\*IEHUDÁH.*?\*\*', line_stripped, re.IGNORECASE):
                book_start = i
                break

            # Try each pattern for this book
            for pattern in patterns:
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    # Additional validation: should contain Hebrew text
                    if re.search(r'[\u0590-\u05FF]', line_stripped):
                        # Skip TOC entries (lines with tab characters or page numbers)
                        if '\t' in line_stripped or re.search(r'\d{1,3}$', line_stripped.strip()):
                            continue
                        # For valid matches
                        elif book_start == -1:
                            book_start = i

            if book_start != -1:
                break

        if book_start == -1:
            raise ValueError(f"Could not find start of book '{book_key}'")

        # Find book end (next book or document end)
        book_end = len(lines)

        # Get all other book keys to find the next one
        other_books = [key for key in self.book_patterns.keys() if key != book_key]

        for i in range(book_start + 1, len(lines)):
            line = lines[i].strip()

            # Skip empty lines and subtitles (but not book headers)
            if not line or (re.match(r'^\*([^*]+)\*$', line) and not line.startswith('**')):
                continue

            # Check for book headers first (highest priority)
            if line.startswith('**') and ('(' in line or 'SODOT' in line or 'IAACOB' in line):
                # This is likely a book header, check if it's another book
                for other_book in other_books:
                    if other_book in line.upper() or any(keyword in line.upper() for keyword in ['SODOT', 'IAACOB', 'APOCALIPSIS', 'SANTIAGO']):
                        book_end = i
                        break
                if book_end != len(lines):
                    break
                continue

            # Check if this is the start of another book using patterns
            for other_book in other_books:
                other_patterns = self.book_patterns[other_book]
                for pattern in other_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Additional validation
                        if re.search(r'[\u0590-\u05FF]', line) or line.startswith('**'):
                            # Only end if it's an actual book header, not TOC
                            if line.strip().startswith('**') or '__' in line or ('\t' not in line and not re.search(r'\d{1,3}$', line.strip())):
                                book_end = i
                                break
                if book_end != len(lines):
                    break

            if book_end != len(lines):
                break

        return book_start, book_end

    def extract_footnotes_for_book(self, full_text: str, book_text: str) -> List[str]:
        """
        Extract footnote definitions that belong to this book.

        Args:
            full_text: Complete document text
            book_text: Text of the specific book

        Returns:
            List of footnote definition lines
        """
        # Find all footnote references in book text
        footnote_nums = set()
        for match in re.finditer(r'\[\^(\d+)\]', book_text):
            footnote_nums.add(int(match.group(1)))

        if not footnote_nums:
            return []

        # Extract footnote definitions from full text
        footnote_lines = []
        lines = full_text.split('\n')

        for line in lines:
            footnote_match = re.match(r'\[\^(\d+)\]:\s*(.+)', line)
            if footnote_match:
                footnote_num = int(footnote_match.group(1))
                if footnote_num in footnote_nums:
                    footnote_lines.append(line)

        return footnote_lines

    def extract_book_section(self, text: str, book_key: str) -> str:
        """
        Extract a specific book section from the complete document.

        Args:
            text: Complete document text
            book_key: Book identifier

        Returns:
            Extracted book text with footnotes
        """
        print(f"Extracting book: {book_key}")

        # Find book boundaries
        start_line, end_line = self.find_book_boundaries(text, book_key)
        lines = text.split('\n')

        # Extract book content
        book_lines = lines[start_line:end_line]
        book_text = '\n'.join(book_lines)

        # Extract associated footnotes
        footnote_lines = self.extract_footnotes_for_book(text, book_text)

        # Combine book content and footnotes
        result_lines = book_lines.copy()

        if footnote_lines:
            result_lines.extend(["", "## Footnotes"])
            result_lines.extend(footnote_lines)

        return '\n'.join(result_lines)

    def get_source_document_path(self, book_key: str) -> str:
        """
        Get the source document path for a book.

        Args:
            book_key: Book identifier

        Returns:
            Path to the source DOCX file
        """
        source = self.BOOK_SOURCES.get(book_key)
        if not source:
            raise ValueError(f"No source document found for book: {book_key}")

        docx_path = self.DOCUMENT_SOURCES.get(source)
        if not docx_path:
            raise ValueError(f"No path found for source: {source}")

        return docx_path

    def get_available_books(self) -> List[str]:
        """
        Get list of all available book keys.

        Returns:
            List of book identifiers
        """
        return list(self.book_patterns.keys())

    def validate_book_extraction(self, book_text: str, book_key: str) -> Dict[str, any]:
        """
        Validate that book extraction was successful.

        Args:
            book_text: Extracted book text
            book_key: Book identifier

        Returns:
            Validation results dictionary
        """
        validation = {
            'book_key': book_key,
            'has_content': len(book_text.strip()) > 0,
            'has_chapters': False,
            'chapter_count': 0,
            'has_verses': False,
            'verse_count': 0,
            'has_footnotes': False,
            'footnote_count': 0,
            'has_hebrew': False,
            'warnings': []
        }

        if not validation['has_content']:
            validation['warnings'].append("Book has no content")
            return validation

        # Check for chapters
        chapter_matches = re.findall(r'__\d+__', book_text)
        validation['chapter_count'] = len(set(chapter_matches))
        validation['has_chapters'] = validation['chapter_count'] > 0

        # Check for verses
        verse_matches = re.findall(r'\*\*\d+\*\*', book_text)
        validation['verse_count'] = len(verse_matches)
        validation['has_verses'] = validation['verse_count'] > 0

        # Check for footnotes
        footnote_matches = re.findall(r'\[\^\d+\]', book_text)
        validation['footnote_count'] = len(footnote_matches)
        validation['has_footnotes'] = validation['footnote_count'] > 0

        # Check for Hebrew text
        validation['has_hebrew'] = bool(re.search(r'[\u0590-\u05FF]', book_text))

        # Generate warnings
        if not validation['has_chapters']:
            validation['warnings'].append("No chapters found")

        if not validation['has_verses']:
            validation['warnings'].append("No verses found")

        if not validation['has_hebrew']:
            validation['warnings'].append("No Hebrew text found")

        return validation


def extract_book(text: str, book_key: str) -> str:
    """
    Convenience function to extract a single book.

    Args:
        text: Complete document text
        book_key: Book identifier

    Returns:
        Extracted book text
    """
    extractor = TTHBookExtractor()
    return extractor.extract_book_section(text, book_key)


def get_available_books() -> List[str]:
    """
    Get list of all available books.

    Returns:
        List of book identifiers
    """
    extractor = TTHBookExtractor()
    return extractor.get_available_books()
