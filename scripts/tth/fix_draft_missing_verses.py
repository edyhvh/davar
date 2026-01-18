#!/usr/bin/env python3
"""
Fix Missing Last Verses in Draft Chapter Files
==============================================

Script to identify and fix missing last verses in draft/ chapter JSON files.
Compares draft chapter files with the raw tanaj.md source to find missing last verses.

Usage:
    python fix_draft_missing_verses.py [book_key] [chapter_num]
    python fix_draft_missing_verses.py --all
    python fix_draft_missing_verses.py --check [book_key]
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set, Optional
import sys
import shutil


class DraftMissingVersesFixer:
    """Class to identify and fix missing last verses in draft chapter JSON files."""

    def __init__(self):
        self.project_root = Path.home() / "davar"
        self.raw_file = self.project_root / "data" / "tth" / "raw" / "tanaj.md"
        self.draft_dir = self.project_root / "data" / "tth" / "draft"
        self.temp_dir = self.project_root / "data" / "tth" / "temp"

        # Book boundaries in tanaj.md
        self.book_boundaries = {
            'bereshit': ('**1** TORAH - BERESHIT', '__SHEMOT'),
            'shemot': ('__SHEMOT', '__VAIKRA'),
            'vaikra': ('__VAIKRA', '__BAMIDBAR'),
            'bamidbar': ('__BAMIDBAR', '__DEVARIM'),
            'devarim': ('__DEVARIM', '__IEHOSHUA'),
        }

    def read_raw_file(self) -> str:
        """Read the raw tanaj.md file."""
        with open(self.raw_file, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_book_from_raw(self, book_key: str) -> str:
        """Extract a specific book from the raw tanaj.md file."""
        content = self.read_raw_file()

        if book_key not in self.book_boundaries:
            raise ValueError(f"Unknown book: {book_key}")

        start_marker, end_marker = self.book_boundaries[book_key]

        # Find start position
        start_pos = content.find(start_marker)
        if start_pos == -1:
            # Try alternative start markers
            alt_markers = ['TORAH - BERESHIT', '**1** TORAH']
            for alt in alt_markers:
                start_pos = content.find(alt)
                if start_pos != -1:
                    break
            if start_pos == -1:
                raise ValueError(f"Could not find start marker for {book_key}: {start_marker}")

        # Find end position
        end_pos = content.find(end_marker, start_pos)
        if end_pos == -1:
            # If no end marker found, take everything to the end
            end_pos = len(content)

        return content[start_pos:end_pos]

    def extract_verses_from_raw_chapter(self, chapter_text: str, chapter_num: int) -> List[Tuple[int, str]]:
        """Extract all verses from a chapter text in the raw format."""
        verses = []

        lines = chapter_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Match verse pattern: **verse_number** verse text
            verse_match = re.match(r'^\*\*(\d+)\*\*\s+(.+)$', line)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2).strip()
                verses.append((verse_num, verse_text))

        return verses

    def get_chapter_text_from_raw(self, book_key: str, chapter_num: int) -> str:
        """Get the text of a specific chapter from the raw file."""
        book_text = self.extract_book_from_raw(book_key)

        # Find chapter markers that are alone on a line (chapter headers)
        # Pattern: \n**{chapter_num}**\n
        pattern = f"\n\\*\\*{chapter_num}\\*\\*\n"
        match = re.search(pattern, book_text)

        if not match:
            return ""

        start_pos = match.start()

        # Find next chapter marker (alone on a line) or end of book
        next_pattern = f"\n\\*\\*{chapter_num + 1}\\*\\*\n"
        next_match = re.search(next_pattern, book_text[start_pos + 1:])

        if next_match:
            end_pos = start_pos + 1 + next_match.start()
        else:
            # Look for next book marker
            end_pos = len(book_text)
            for end_marker in ['__SHEMOT', '__VAIKRA', '__BAMIDBAR', '__DEVARIM', '__IEHOSHUA']:
                marker_pos = book_text.find(end_marker, start_pos)
                if marker_pos != -1:
                    end_pos = min(end_pos, marker_pos)

        return book_text[start_pos:end_pos]

    def load_draft_chapter(self, book_key: str, chapter_num: int) -> List[Dict[str, Any]]:
        """Load a draft chapter JSON file."""
        chapter_file = self.draft_dir / book_key / f"{chapter_num:02d}.json"
        if not chapter_file.exists():
            raise FileNotFoundError(f"Draft chapter file not found: {chapter_file}")

        with open(chapter_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def find_missing_last_verse(self, book_key: str, chapter_num: int) -> Optional[Tuple[int, str]]:
        """Find if the last verse is missing from a draft chapter."""
        try:
            # Get raw chapter verses
            chapter_text = self.get_chapter_text_from_raw(book_key, chapter_num)
            raw_verses = self.extract_verses_from_raw_chapter(chapter_text, chapter_num)

            if not raw_verses:
                return None

            # Get max verse number from raw
            max_raw_verse = max(v[0] for v in raw_verses)

            # Get processed verses
            processed_verses = self.load_draft_chapter(book_key, chapter_num)
            processed_verse_nums = {v['verse'] for v in processed_verses}

            # Check if max verse is missing
            if max_raw_verse not in processed_verse_nums:
                # Find the verse text
                for verse_num, verse_text in raw_verses:
                    if verse_num == max_raw_verse:
                        return (max_raw_verse, verse_text)

        except Exception as e:
            print(f"Error checking {book_key} chapter {chapter_num}: {e}")

        return None

    def add_missing_verse_to_draft(self, book_key: str, chapter_num: int, verse_num: int, verse_text: str) -> bool:
        """Add a missing verse to a draft chapter file (working in temp/)."""
        try:
            # Load original chapter
            original_verses = self.load_draft_chapter(book_key, chapter_num)

            # Create temp directory structure
            temp_book_dir = self.temp_dir / book_key
            temp_book_dir.mkdir(parents=True, exist_ok=True)

            # Copy original file to temp
            original_file = self.draft_dir / book_key / f"{chapter_num:02d}.json"
            temp_file = temp_book_dir / f"{chapter_num:02d}.json"
            shutil.copy2(original_file, temp_file)

            # Add missing verse
            verse_entry = {
                'book': book_key,
                'book_id': 'genesis',  # TODO: get correct book_id
                'book_tth_name': book_key.title(),  # TODO: get correct name
                'book_hebrew_name': '',  # TODO: get correct name
                'book_english_name': book_key.title(),
                'book_spanish_name': book_key.title(),
                'section': 'torah',  # TODO: get correct section
                'section_hebrew': 'תורה',
                'section_english': 'Torah',
                'section_spanish': 'Torá',
                'chapter': chapter_num,
                'verse': verse_num,
                'status': 'present',
                'tth': verse_text,
                'footnotes': [],  # TODO: extract footnotes
                'hebrew_terms': [],  # TODO: extract hebrew terms
                'title': '',  # TODO: extract title if any
                'book_english_name_lower': book_key.lower()
            }

            original_verses.append(verse_entry)

            # Sort by verse number
            original_verses.sort(key=lambda x: x['verse'])

            # Save to temp
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(original_verses, f, ensure_ascii=False, indent=2)

            print(f"Added verse {verse_num} to {book_key}/{chapter_num:02d}.json in temp/")
            return True

        except Exception as e:
            print(f"Error adding verse to {book_key} chapter {chapter_num}: {e}")
            return False

    def check_book(self, book_key: str) -> None:
        """Check all chapters of a book for missing last verses."""
        print(f"Checking {book_key} chapters for missing last verses...")

        try:
            book_dir = self.draft_dir / book_key
            if not book_dir.exists():
                print(f"Book directory not found: {book_dir}")
                return

            missing_count = 0
            for chapter_file in sorted(book_dir.glob("*.json")):
                chapter_num = int(chapter_file.stem)
                missing = self.find_missing_last_verse(book_key, chapter_num)
                if missing:
                    verse_num, verse_text = missing
                    print(f"  Chapter {chapter_num}: missing verse {verse_num}")
                    missing_count += 1

            if missing_count == 0:
                print(f"No missing last verses found in {book_key}")
            else:
                print(f"Found {missing_count} chapters with missing last verses in {book_key}")

        except Exception as e:
            print(f"Error checking {book_key}: {e}")

    def fix_book(self, book_key: str) -> int:
        """Fix all missing last verses in a book."""
        print(f"Fixing {book_key}...")

        try:
            book_dir = self.draft_dir / book_key
            if not book_dir.exists():
                print(f"Book directory not found: {book_dir}")
                return 0

            fixed_count = 0
            for chapter_file in sorted(book_dir.glob("*.json")):
                chapter_num = int(chapter_file.stem)
                missing = self.find_missing_last_verse(book_key, chapter_num)
                if missing:
                    verse_num, verse_text = missing
                    if self.add_missing_verse_to_draft(book_key, chapter_num, verse_num, verse_text):
                        fixed_count += 1

            print(f"Fixed {fixed_count} chapters in {book_key}")
            return fixed_count

        except Exception as e:
            print(f"Error fixing {book_key}: {e}")
            return 0

    def check_chapter(self, book_key: str, chapter_num: int) -> None:
        """Check a specific chapter for missing last verse."""
        print(f"Checking {book_key} chapter {chapter_num}...")

        missing = self.find_missing_last_verse(book_key, chapter_num)
        if missing:
            verse_num, verse_text = missing
            print(f"Missing verse {verse_num}: {verse_text[:100]}...")
        else:
            print(f"No missing last verse found in {book_key} chapter {chapter_num}")

    def fix_chapter(self, book_key: str, chapter_num: int) -> bool:
        """Fix a specific chapter."""
        print(f"Fixing {book_key} chapter {chapter_num}...")

        missing = self.find_missing_last_verse(book_key, chapter_num)
        if missing:
            verse_num, verse_text = missing
            return self.add_missing_verse_to_draft(book_key, chapter_num, verse_num, verse_text)
        else:
            print(f"No missing last verse found in {book_key} chapter {chapter_num}")
            return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_draft_missing_verses.py [book_key [chapter_num] | --all | --check book_key]")
        sys.exit(1)

    fixer = DraftMissingVersesFixer()
    command = sys.argv[1]

    if command == '--all':
        # Fix all books
        books = ['bereshit', 'shemot', 'vaikra', 'bamidbar', 'devarim']
        total_fixed = 0
        for book in books:
            total_fixed += fixer.fix_book(book)
        print(f"Fixed {total_fixed} chapters total")

    elif command == '--check':
        if len(sys.argv) < 3:
            print("Usage: python fix_draft_missing_verses.py --check book_key")
            sys.exit(1)
        fixer.check_book(sys.argv[2])

    else:
        book_key = command
        if len(sys.argv) >= 3:
            # Fix specific chapter
            chapter_num = int(sys.argv[2])
            fixer.fix_chapter(book_key, chapter_num)
        else:
            # Fix entire book
            fixer.fix_book(book_key)


if __name__ == '__main__':
    main()