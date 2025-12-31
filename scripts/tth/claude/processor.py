#!/usr/bin/env python3
"""
TTH Processor - Claude Version
==============================

Processes TTH docx files into structured JSON for the Davar app.
This version extracts directly from the .docx file to capture all verses correctly.

Key features:
- Extracts directly from tanaj.docx/besorah.docx using mammoth
- Correctly handles __número__ format for chapters and verses
- Detects verse 1 when it comes without a marker after chapter
- Preserves titles and section markers
- Extracts footnotes and Hebrew terms

Author: Davar Project
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

try:
    import mammoth
except ImportError:
    mammoth = None
    print("Warning: mammoth not installed. Install with: pip install mammoth")

from config import BOOKS_INFO, HEBREW_TERMS, DATA_PATH, RAW_PATH, TEMP_PATH


class TextCleaner:
    """Cleans verse text from conversion artifacts."""
    
    @staticmethod
    def fix_soft_hyphens(text: str) -> str:
        """Remove soft hyphens and fix broken words."""
        # Soft hyphen character
        text = text.replace('\xad', '')
        text = text.replace('­', '')  # HTML entity
        # Fix escaped hyphens from markdown
        text = text.replace('\\-', '')
        return text
    
    @staticmethod
    def fix_stuck_connectors(text: str) -> str:
        """Fix words stuck together with connectors."""
        # Common patterns: word,word -> word, word
        patterns = [
            (r'(\w+),(\w+)', r'\1, \2'),
            (r'(\w+);(\w+)', r'\1; \2'),
            (r'(\w+):(\w+)', r'\1: \2'),
        ]
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        return text
    
    @staticmethod
    def fix_punctuation_spacing(text: str) -> str:
        """Fix spacing around punctuation."""
        # Space before punctuation - remove
        text = re.sub(r'\s+([,;:.!?])', r'\1', text)
        # No space after punctuation - add (except at end)
        text = re.sub(r'([,;:])(\w)', r'\1 \2', text)
        return text
    
    @staticmethod
    def clean(text: str) -> str:
        """Apply all text cleaning operations."""
        if not text or not text.strip():
            return text
        
        result = text
        
        # Remove HTML anchor tags: <a id="..."></a>
        result = re.sub(r'<a\s+id="[^"]*"></a>\s*', '', result)
        
        # Convert markdown footnote links to [^number] format
        # Pattern: [\[1\]](#footnote-1) -> [^1]
        result = re.sub(r'\[\\\[(\d+)\\\]\]\(#footnote-\d+\)', r'[^\1]', result)
        
        # Remove italic markers around words: *word* -> word
        # But preserve asterisks that are part of content like *la* for emphasis
        result = re.sub(r'(?<!\w)\*([^*\s][^*]*[^*\s]|\w)\*(?!\w)', r'\1', result)
        
        # Clean up double asterisks leftover from malformed markdown
        result = re.sub(r'\*\s+\*', ' ', result)
        
        result = TextCleaner.fix_soft_hyphens(result)
        result = TextCleaner.fix_stuck_connectors(result)
        result = TextCleaner.fix_punctuation_spacing(result)
        result = re.sub(r'  +', ' ', result)  # Double spaces
        result = re.sub(r'\s+([.,;:!?])', r'\1', result)  # Space before punctuation
        
        # Convert escaped parentheses to normal
        result = result.replace('\\(', '(').replace('\\)', ')')
        
        # Remove remaining backslash escapes
        result = result.replace('\\.', '.')
        result = result.replace('\\-', '')
        
        return result.strip()


class TTHProcessor:
    """
    Processor for TTH (Textual Translation of Hebrew) texts.
    Extracts directly from docx files for accuracy.
    """
    
    def __init__(self, book_key: str):
        if book_key not in BOOKS_INFO:
            raise ValueError(f"Unknown book: {book_key}")
        
        self.book_key = book_key
        self.book_info = BOOKS_INFO[book_key]
        self.cleaner = TextCleaner()
        self.footnote_definitions: Dict[str, str] = {}
    
    def get_source_file(self) -> Path:
        """Get the source docx file path."""
        source = self.book_info.get('source', 'tanaj')
        if source == 'tanaj':
            return RAW_PATH / 'tanaj.docx'
        elif source == 'besorah':
            return RAW_PATH / 'besorah.docx'
        else:
            raise ValueError(f"Unknown source: {source}")
    
    def extract_from_docx(self) -> str:
        """Extract markdown text from docx file."""
        if mammoth is None:
            raise ImportError("mammoth library is required. Install with: pip install mammoth")
        
        source_file = self.get_source_file()
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        with open(source_file, 'rb') as f:
            result = mammoth.convert_to_markdown(f)
        
        if result.messages:
            print(f"  Conversion warnings: {len(result.messages)}")
        
        return result.value
    
    def extract_book_section(self, full_text: str) -> str:
        """Extract just the section for this book from the full document."""
        lines = full_text.split('\n')
        
        # Find book start using the pattern
        start_pattern = self.book_info.get('start_pattern', '')
        start_line = -1
        
        for i, line in enumerate(lines):
            if re.search(start_pattern, line, re.IGNORECASE):
                start_line = i
                print(f"  Found book start at line {i}: {line[:60]}...")
                break
        
        if start_line == -1:
            raise ValueError(f"Could not find start of book {self.book_key}")
        
        # Find book end using end patterns
        end_patterns = self.book_info.get('end_patterns', [])
        end_line = len(lines)
        
        for i in range(start_line + 10, len(lines)):
            line = lines[i]
            line_upper = line.upper()
            
            for pattern in end_patterns:
                pattern_upper = pattern.upper()
                if pattern_upper in line_upper:
                    # Verify it's a book title (starts with __ or is a header)
                    if line.strip().startswith('__') or line.strip().startswith('#'):
                        end_line = i
                        print(f"  Found book end at line {i}: {line[:60]}...")
                        break
            if end_line != len(lines):
                break
        
        # Extract book content
        book_lines = lines[start_line:end_line]
        book_text = '\n'.join(book_lines)
        
        # Also extract relevant footnotes
        footnote_nums = set()
        for match in re.finditer(r'\[\^(\d+)\]', book_text):
            footnote_nums.add(int(match.group(1)))
        
        if footnote_nums:
            footnote_lines = []
            for line in lines[end_line:]:
                match = re.match(r'\[\^(\d+)\]:\s*(.+)', line)
                if match:
                    if int(match.group(1)) in footnote_nums:
                        footnote_lines.append(line)
            
            if footnote_lines:
                book_text += '\n\n## Footnotes\n' + '\n'.join(footnote_lines)
        
        return book_text
    
    def extract_footnote_definitions(self, text: str):
        """Extract footnote definitions from the text."""
        self.footnote_definitions = {}
        
        # Look for footnote section
        footnote_section = text
        if '## Footnotes' in text:
            footnote_section = text.split('## Footnotes')[1]
        
        # Find all footnote definitions: [^número]: content
        for match in re.finditer(r'\[\^(\d+)\]:\s*(.+?)(?=\n\[|\n\n|$)', footnote_section, re.MULTILINE | re.DOTALL):
            num = match.group(1)
            definition = match.group(2).strip()
            # Clean up the definition
            definition = re.sub(r'\*([^*]+)\*', r'\1', definition)  # Remove italics
            definition = re.sub(r'\s+', ' ', definition).strip()
            self.footnote_definitions[num] = definition
    
    def parse_chapters_and_verses(self, book_text: str) -> List[Dict[str, Any]]:
        """
        Parse chapters and verses from the book text.
        
        In TTH docx format:
        - __número__ alone on a line = chapter marker
        - Text after chapter marker without verse number = verse 1
        - __número__ followed by text = verse (can have multiple verses per line)
        - __ __ or __  __ = malformed verse 1 marker
        """
        lines = book_text.split('\n')
        chapters: List[Dict[str, Any]] = []
        
        current_chapter = 0
        current_verses: List[Dict[str, Any]] = []
        current_title = None
        in_book_content = False
        pending_content: List[str] = []  # Accumulate content between chapter markers
        
        def flush_content():
            """Process accumulated content and extract verses."""
            nonlocal current_verses, current_title, pending_content
            
            if not pending_content:
                return
            
            # Join all accumulated content
            content = ' '.join(pending_content)
            pending_content = []
            
            # Remove malformed verse 1 markers: __ __ or __  __
            content = re.sub(r'__\s+__', '', content)
            
            # Find all verse markers
            verse_pattern = r'__(\d+)\s*__'
            verse_markers = list(re.finditer(verse_pattern, content))
            
            if not verse_markers:
                # No verse markers - this is verse 1 or continuation
                content = content.strip()
                if content:
                    if not current_verses:
                        # It's verse 1
                        verse_text = self.cleaner.clean(content)
                        entry = self._create_verse_entry(1, verse_text, current_title)
                        current_verses.append(entry)
                        current_title = None
                    else:
                        # Continuation of last verse
                        current_verses[-1]['text'] += ' ' + content
                return
            
            # Process text before first verse marker
            if verse_markers[0].start() > 0:
                prefix_text = content[:verse_markers[0].start()].strip()
                if prefix_text:
                    if not current_verses:
                        # It's verse 1
                        verse_text = self.cleaner.clean(prefix_text)
                        entry = self._create_verse_entry(1, verse_text, current_title)
                        current_verses.append(entry)
                        current_title = None
                    else:
                        # Append to last verse
                        current_verses[-1]['text'] += ' ' + prefix_text
            
            # Process each verse marker
            for idx, match in enumerate(verse_markers):
                verse_num = int(match.group(1))
                start_pos = match.end()
                
                # Find end position
                if idx + 1 < len(verse_markers):
                    end_pos = verse_markers[idx + 1].start()
                else:
                    end_pos = len(content)
                
                verse_text = content[start_pos:end_pos].strip()
                if verse_text:
                    verse_text = self.cleaner.clean(verse_text)
                    entry = self._create_verse_entry(verse_num, verse_text, current_title)
                    current_verses.append(entry)
                    current_title = None  # Only first verse gets the title
        
        i = 0
        while i < len(lines):
            line = lines[i]
            line_stripped = line.strip()
            
            # Skip empty lines
            if not line_stripped:
                i += 1
                continue
            
            # Stop at footnotes section
            if line_stripped == '## Footnotes' or re.match(r'^\[\^\d+\]:', line_stripped):
                break
            
            # Detect book title (marks start of content)
            # Book title format: __BOOK_NAME__ hebrew_name or __SECTION - BOOK_NAME__ hebrew_name
            # Must have the hebrew name AND be a short line (< 100 chars) AND not have verse markers
            if (line_stripped.startswith('__') and 
                self.book_info['hebrew_name'] in line_stripped and
                len(line_stripped) < 100 and
                not re.search(r'__\d+__', line_stripped[5:])):  # No verse markers after first __
                in_book_content = True
                i += 1
                continue
            
            # Skip lines before book content starts
            if not in_book_content:
                if re.match(r'^__\d+__\s*$', line_stripped):
                    in_book_content = True
                else:
                    i += 1
                    continue
            
            # Detect section titles: *Title text* (standalone, not in verse text)
            title_match = re.match(r'^\*([^*]+)\*$', line_stripped)
            if title_match:
                title_text = title_match.group(1).strip()
                if len(title_text) < 100 and not re.search(r'__\d+__', title_text):
                    # Flush content before updating title
                    flush_content()
                    current_title = title_text
                    i += 1
                    continue
            
            # Also detect unformatted titles (short lines without verse markers)
            if (not line_stripped.startswith('__') and 
                len(line_stripped) < 80 and
                not re.search(r'__\d+__', line_stripped)):
                # Check if next non-empty line is a chapter marker or verse
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    next_line = lines[j].strip()
                    if re.match(r'^__\d+__\s*$', next_line):
                        # It's a title before chapter marker
                        flush_content()
                        current_title = line_stripped
                        i += 1
                        continue
                    elif re.match(r'^__\d+__', next_line) or re.match(r'^__\s+__', next_line):
                        # Next line starts with verse marker, this might be a title
                        # Only treat as title if it looks like one (starts with uppercase, no punctuation mix)
                        if (line_stripped[0].isupper() and 
                            not re.search(r'[.,:;!?]', line_stripped[:20])):
                            flush_content()
                            current_title = line_stripped
                            i += 1
                            continue
            
            # CHAPTER MARKER: __número__ alone on line
            chapter_match = re.match(r'^__(\d+)__\s*$', line_stripped)
            if chapter_match:
                # Flush pending content for previous chapter
                flush_content()
                
                # Save previous chapter if any
                if current_chapter > 0 and current_verses:
                    chapters.append({
                        'chapter': current_chapter,
                        'verses': current_verses
                    })
                
                # Start new chapter
                current_chapter = int(chapter_match.group(1))
                current_verses = []
                pending_content = []
                
                i += 1
                continue
            
            # Accumulate content for later processing
            pending_content.append(line_stripped)
            i += 1
        
        # Flush remaining content
        flush_content()
        
        # Save final chapter
        if current_chapter > 0 and current_verses:
            chapters.append({
                'chapter': current_chapter,
                'verses': current_verses
            })
        
        return chapters
    
    def _create_verse_entry(self, verse_num: int, verse_text: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Create a verse entry dictionary."""
        # Extract footnotes
        verse_text, footnotes = self._extract_footnotes(verse_text)
        
        # Extract Hebrew terms
        hebrew_terms = self._extract_hebrew_terms(verse_text)
        
        entry = {
            'verse': verse_num,
            'text': verse_text,
            'footnotes': footnotes,
            'hebrew_terms': hebrew_terms,
        }
        
        if title:
            entry['title'] = title
        
        return entry
    
    def _extract_footnotes(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Extract footnotes from text and replace with superscripts."""
        footnotes = []
        
        # Find all [^número] patterns
        matches = list(re.finditer(r'\[\^(\d+)\]', text))
        
        # Superscript mapping
        superscripts = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', 
                       '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
        
        def to_superscript(num_str):
            return ''.join(superscripts.get(d, d) for d in num_str)
        
        # Process in reverse order
        for match in reversed(matches):
            num = match.group(1)
            marker = to_superscript(num)
            definition = self.footnote_definitions.get(num, f'Note {num}')
            
            # Find associated word (word before footnote marker)
            text_before = text[:match.start()].rstrip()
            word_match = re.search(r'([\w\'-]+)\s*$', text_before)
            associated_word = word_match.group(1) if word_match else ''
            
            # Replace marker
            text = text[:match.start()] + marker + text[match.end():]
            
            footnotes.append({
                'marker': marker,
                'number': num,
                'word': associated_word,
                'explanation': definition
            })
        
        # Sort by number
        footnotes.sort(key=lambda x: int(x['number']))
        
        return text, footnotes
    
    def _extract_hebrew_terms(self, text: str) -> List[Dict[str, str]]:
        """Extract Hebrew terms from the text."""
        terms_found = []
        found_normalized = set()
        
        # Sort terms by length (longer first) to avoid partial matches
        sorted_terms = sorted(HEBREW_TERMS.items(), key=lambda x: len(x[0]), reverse=True)
        
        for term, explanation in sorted_terms:
            normalized = term.upper()
            if normalized in found_normalized:
                continue
            
            # Create pattern for word boundary matching
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            
            if pattern.search(text):
                terms_found.append({
                    'term': term,
                    'explanation': explanation
                })
                found_normalized.add(normalized)
        
        return terms_found
    
    def create_json_structure(self, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create the final JSON structure."""
        book_info = self.book_info.copy()
        verses = []
        
        for chapter_data in chapters:
            chapter_num = chapter_data['chapter']
            
            for verse_data in chapter_data['verses']:
                verse_entry = {
                    'book': self.book_key,
                    'book_id': book_info.get('book_code', self.book_key),
                    'chapter': chapter_num,
                    'verse': verse_data['verse'],
                    'status': 'present',
                    'tth': verse_data['text'],
                    'footnotes': verse_data.get('footnotes', []),
                    'hebrew_terms': verse_data.get('hebrew_terms', []),
                }
                
                if 'title' in verse_data:
                    verse_entry['title'] = verse_data['title']
                
                verses.append(verse_entry)
        
        return {
            'book_info': {
                **book_info,
                'total_chapters': len(chapters),
                'total_verses': len(verses),
                'processed_date': datetime.now().isoformat(),
                'processor_version': '2.0.0',
            },
            'verses': verses
        }
    
    def process(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Main processing method.
        Returns the processed data and optionally saves to file.
        """
        print(f"Processing {self.book_key}...")
        
        # Extract from docx
        print("  Extracting from docx...")
        full_text = self.extract_from_docx()
        print(f"  Full text: {len(full_text)} characters")
        
        # Extract book section
        print("  Extracting book section...")
        book_text = self.extract_book_section(full_text)
        print(f"  Book section: {len(book_text)} characters")
        
        # Extract footnote definitions
        self.extract_footnote_definitions(book_text)
        print(f"  Footnote definitions: {len(self.footnote_definitions)}")
        
        # Parse chapters and verses
        print("  Parsing chapters and verses...")
        chapters = self.parse_chapters_and_verses(book_text)
        print(f"  Chapters: {len(chapters)}")
        
        # Create JSON structure
        result = self.create_json_structure(chapters)
        print(f"  Total verses: {len(result['verses'])}")
        
        # Save if output path provided
        if output_path:
            output_file = output_path / f"{self.book_key}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"  Saved to: {output_file}")
        
        return result


def process_book(book_key: str, output_dir: Optional[Path] = None, split_chapters: bool = False) -> Dict[str, Any]:
    """
    Process a single book.
    
    Args:
        book_key: The book key (e.g., 'amos', 'bereshit')
        output_dir: Directory to save output (defaults to temp/)
        split_chapters: If True, save each chapter as separate file
    
    Returns:
        The processed book data
    """
    if output_dir is None:
        output_dir = TEMP_PATH
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processor = TTHProcessor(book_key)
    result = processor.process(output_dir if not split_chapters else None)
    
    if split_chapters:
        # Save each chapter as separate file
        book_dir = output_dir / book_key
        book_dir.mkdir(parents=True, exist_ok=True)
        
        # Group verses by chapter
        chapters_data = {}
        for verse in result['verses']:
            ch = verse['chapter']
            if ch not in chapters_data:
                chapters_data[ch] = []
            chapters_data[ch].append(verse)
        
        # Save each chapter
        for ch_num, verses in sorted(chapters_data.items()):
            ch_file = book_dir / f"{ch_num:02d}.json"
            with open(ch_file, 'w', encoding='utf-8') as f:
                json.dump(verses, f, ensure_ascii=False, indent=2)
            print(f"  Saved chapter {ch_num} to {ch_file}")
        
        # Save book info
        info_file = book_dir / "book_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(result['book_info'], f, ensure_ascii=False, indent=2)
        print(f"  Saved book info to {info_file}")
    
    return result


if __name__ == '__main__':
    # Test with Amos
    result = process_book('amos')
    
    # Show first few verses
    print("\nFirst 3 verses:")
    for v in result['verses'][:3]:
        print(f"  {v['chapter']}:{v['verse']}: {v['tth'][:80]}...")
