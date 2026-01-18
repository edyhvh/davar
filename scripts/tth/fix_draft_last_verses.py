#!/usr/bin/env python3
"""
Fix Missing Last Verses in Draft Chapter Files
==============================================

Simple script to add missing last verses to draft/ chapter JSON files.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
import sys


class DraftLastVersesFixer:
    """Class to fix missing last verses in draft chapter JSON files."""

    def __init__(self, use_temp=False):
        self.project_root = Path.home() / "davar"
        self.raw_file = self.project_root / "data" / "tth" / "raw" / "tanaj.md"
        self.draft_dir = self.project_root / "data" / "tth" / "draft"
        self.temp_dir = self.project_root / "data" / "tth" / "temp"
        self.use_temp = use_temp
        self.target_dir = self.temp_dir if use_temp else self.draft_dir

    def read_raw_file(self) -> str:
        """Read the raw tanaj.md file."""
        with open(self.raw_file, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_book_from_raw(self, book_key: str) -> str:
        """Extract a specific book from the raw tanaj.md file."""
        content = self.read_raw_file()

        # List of all supported books
        supported_books = [
            # Torah
            'bereshit', 'shemot', 'vaikra', 'bamidbar', 'devarim',
            # Neviim
            'iehoshua', 'shoftim', 'shemuel_alef', 'shemuel_bet', 'melajim_alef', 'melajim_bet',
            'ieshaiahu', 'irmeiahu', 'iejezkel', 'hoshea', 'ioel', 'amos', 'ionah', 'micah',
            'najum', 'jabakuk', 'tzefaniah', 'jagai', 'zejariah', 'malaji',
            # Ketuvim
            'tehilim', 'mishlei'
        ]

        if book_key not in supported_books:
            raise ValueError(f"Unknown book: {book_key}")

        # Book boundaries in tanaj.md
        boundaries = {
            # Torah
            'bereshit': ('**1** TORAH - BERESHIT', '__SHEMOT'),
            'shemot': ('__SHEMOT', '__VAIKRA'),
            'vaikra': ('__VAIKRA', '__BAMIDBAR'),
            'bamidbar': ('__BAMIDBAR', '__DEVARIM'),
            'devarim': ('__DEVARIM', '__IEHOSHUA'),

            # Neviim (Prophets)
            'iehoshua': ('__IEHOSHUA', '__SHOFTIM'),
            'shoftim': ('__SHOFTIM', '__SHEMUEL_ALEF'),
            'shemuel_alef': ('__SHEMUEL_ALEF', '__SHEMUEL_BET'),
            'shemuel_bet': ('__SHEMUEL_BET', '__MELAJIM_ALEF'),
            'melajim_alef': ('__MELAJIM_ALEF', '__MELAJIM_BET'),
            'melajim_bet': ('__MELAJIM_BET', '__IESHAIAHU'),
            'ieshaiahu': ('__IESHAIAHU', '__IRMEIAHU'),
            'irmeiahu': ('__IRMEIAHU', '__IEJEZKEL'),
            'iejezkel': ('__IEJEZKEL', '__HOSHEA'),
            'hoshea': ('__HOSHEA', '__IOEL'),
            'ioel': ('__IOEL', '__AMOS'),
            'amos': ('__AMOS', '__IONAH'),
            'ionah': ('__IONAH', '__MICAH'),
            'micah': ('__MICAH', '__NAJUM'),
            'najum': ('__NAJUM', '__JABAKUK'),
            'jabakuk': ('__JABAKUK', '__TZEFANIAH'),
            'tzefaniah': ('__TZEFANIAH', '__JAGAI'),
            'jagai': ('__JAGAI', '__ZEJARIAH'),
            'zejariah': ('__ZEJARIAH', '__MALAJI'),
            'malaji': ('__MALAJI', '__TEHILIM'),

            # Ketuvim (Writings)
            'tehilim': ('__TEHILIM', '__MISHLEI'),
            'mishlei': ('__MISHLEI', '__End'),
        }

        start_marker, end_marker = boundaries[book_key]

        start_pos = content.find(start_marker)
        if start_pos == -1:
            # Try alternatives
            alternatives = ['TORAH - BERESHIT', '**1** TORAH', 'BERESHIT']
            for alt in alternatives:
                start_pos = content.find(alt)
                if start_pos != -1:
                    break

        if start_pos == -1:
            raise ValueError(f"Could not find start marker for {book_key}")

        end_pos = content.find(end_marker, start_pos)
        if end_pos == -1:
            end_pos = len(content)

        return content[start_pos:end_pos]

    def get_last_verse_for_chapter(self, book_key: str, chapter_num: int) -> tuple[int, str] | None:
        """Get the last verse number and text for a chapter from raw file."""
        book_text = self.extract_book_from_raw(book_key)

        # Find the chapter
        chapter_pattern = f"\n\\*\\*{chapter_num}\\*\\*\n"
        match = re.search(chapter_pattern, book_text)
        if not match:
            return None

        start_pos = match.start()

        # Find next chapter or end
        next_chapter_pattern = f"\n\\*\\*{chapter_num + 1}\\*\\*\n"
        next_match = re.search(next_chapter_pattern, book_text[start_pos + 1:])

        if next_match:
            end_pos = start_pos + 1 + next_match.start()
        else:
            end_pos = len(book_text)

        chapter_text = book_text[start_pos:end_pos]

        # Extract all verses from this chapter
        verses = []
        lines = chapter_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            verse_match = re.match(r'^\*\*(\d+)\*\*\s+(.+)$', line)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2).strip()
                verses.append((verse_num, verse_text))

        if verses:
            return max(verses, key=lambda x: x[0])  # Return verse with highest number

        return None

    def load_draft_chapter(self, book_key: str, chapter_num: int) -> List[Dict[str, Any]]:
        """Load a draft chapter JSON file."""
        chapter_file = self.target_dir / book_key / f"{chapter_num:02d}.json"
        if not chapter_file.exists():
            raise FileNotFoundError(f"Chapter file not found: {chapter_file}")

        with open(chapter_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_max_verse_in_draft(self, verses: List[Dict[str, Any]]) -> int:
        """Get the maximum verse number in a draft chapter."""
        if not verses:
            return 0
        return max(v['verse'] for v in verses)

    def fix_chapter_last_verse(self, book_key: str, chapter_num: int) -> bool:
        """Fix missing last verse in a draft chapter."""
        try:
            # Get what should be the last verse from raw
            expected_last = self.get_last_verse_for_chapter(book_key, chapter_num)
            if not expected_last:
                print(f"Could not find expected last verse for {book_key} chapter {chapter_num}")
                return False

            expected_verse_num, expected_verse_text = expected_last

            # Get current verses in draft
            current_verses = self.load_draft_chapter(book_key, chapter_num)
            max_current_verse = self.get_max_verse_in_draft(current_verses)

            if max_current_verse >= expected_verse_num:
                print(f"{book_key}/{chapter_num:02d}.json already has verse {expected_verse_num}")
                return True

            # Add missing verse directly to the draft file
            verse_entry = {
                'book': book_key,
                'book_id': 'genesis',  # TODO: get correct book_id
                'book_tth_name': book_key.title(),
                'book_hebrew_name': '',
                'book_english_name': book_key.title(),
                'book_spanish_name': book_key.title(),
                'section': 'torah',  # TODO: get correct section
                'section_hebrew': 'תורה',
                'section_english': 'Torah',
                'section_spanish': 'Torá',
                'chapter': chapter_num,
                'verse': expected_verse_num,
                'status': 'present',
                'tth': expected_verse_text,
                'footnotes': [],  # TODO: extract footnotes
                'hebrew_terms': [],  # TODO: extract hebrew terms
                'title': '',  # TODO: extract title if any
                'book_english_name_lower': book_key.lower()
            }

            current_verses.append(verse_entry)
            current_verses.sort(key=lambda x: x['verse'])

            # Save to the target directory (draft or temp)
            target_file = self.target_dir / book_key / f"{chapter_num:02d}.json"
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(current_verses, f, ensure_ascii=False, indent=2)

            target_name = "temp" if self.use_temp else "draft"
            print(f"Added verse {expected_verse_num} to {book_key}/{chapter_num:02d}.json in {target_name}/")
            return True

        except Exception as e:
            print(f"Error fixing {book_key} chapter {chapter_num}: {e}")
            return False

    def fix_all_books(self) -> int:
        """Fix all books with missing verses."""
        target_name = "temp" if self.use_temp else "draft"

        # List of all books that have draft directories
        all_books = [
            # Torah
            'bereshit', 'shemot', 'vaikra', 'bamidbar', 'devarim',
            # Neviim
            'iehoshua', 'shoftim', 'shemuel_alef', 'shemuel_bet', 'melajim_alef', 'melajim_bet',
            'ieshaiahu', 'irmeiahu', 'iejezkel', 'hoshea', 'ioel', 'amos', 'ionah', 'micah',
            'najum', 'jabakuk', 'tzefaniah', 'jagai', 'zejariah', 'malaji',
            # Ketuvim
            'tehilim', 'mishlei'
        ]

        total_fixed = 0
        print(f"Fixing missing last verses for ALL books (using {target_name}/)...")
        print("=" * 60)

        for book_key in all_books:
            fixed = self.fix_book(book_key)
            total_fixed += fixed

        print("=" * 60)
        print(f"Total verses added across all books: {total_fixed}")
        return total_fixed

    def fix_book(self, book_key: str) -> int:
        """Fix all chapters in a book."""
        target_name = "temp" if self.use_temp else "draft"
        print(f"Fixing missing last verses in {book_key} (using {target_name}/)...")

        try:
            book_dir = self.target_dir / book_key
            if not book_dir.exists():
                # If using temp, copy from draft first
                if self.use_temp:
                    draft_book_dir = self.draft_dir / book_key
                    if draft_book_dir.exists():
                        import shutil
                        shutil.copytree(draft_book_dir, book_dir)
                        print(f"Copied {book_key} from draft/ to temp/")
                    else:
                        print(f"Book directory not found in draft/: {draft_book_dir}")
                        return 0
                else:
                    print(f"Book directory not found: {book_dir}")
                    return 0

            fixed_count = 0
            for chapter_file in sorted(book_dir.glob("*.json")):
                if chapter_file.stem == 'book_info':
                    continue  # Skip book_info.json and other non-chapter files

                try:
                    chapter_num = int(chapter_file.stem)
                except ValueError:
                    continue  # Skip files that don't have numeric names

                if self.fix_chapter_last_verse(book_key, chapter_num):
                    fixed_count += 1

            print(f"Processed {fixed_count} chapters in {book_key}")
            return fixed_count

        except Exception as e:
            print(f"Error fixing {book_key}: {e}")
            return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_draft_last_verses.py [book_key [chapter_num] | --all | --all-temp]")
        print("  book_key: Fix specific book")
        print("  --all: Fix all books in draft/ directory")
        print("  --all-temp: Test fix all books in temp/ directory first")
        sys.exit(1)

    command = sys.argv[1]

    if command == '--all':
        fixer = DraftLastVersesFixer(use_temp=False)
        fixer.fix_all_books()
    elif command == '--all-temp':
        fixer = DraftLastVersesFixer(use_temp=True)
        fixer.fix_all_books()
    else:
        fixer = DraftLastVersesFixer(use_temp=False)
        book_key = command

        if len(sys.argv) >= 3:
            chapter_num = int(sys.argv[2])
            fixer.fix_chapter_last_verse(book_key, chapter_num)
        else:
            fixer.fix_book(book_key)


if __name__ == '__main__':
    main()