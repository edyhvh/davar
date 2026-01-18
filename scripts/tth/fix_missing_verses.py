#!/usr/bin/env python3
"""
Fix Missing Verses Script
========================

Script to identify and fix missing verses in TTH processed JSON files.
Compares processed JSON files with the raw tanaj.md source to find missing verses.

Usage:
    python fix_missing_verses.py [book_key]
    python fix_missing_verses.py --all
    python fix_missing_verses.py --check [book_key]
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import sys


class MissingVersesFixer:
    """Class to identify and fix missing verses in TTH JSON files."""

    def __init__(self):
        self.project_root = Path.home() / "davar"
        self.raw_file = self.project_root / "data" / "tth" / "raw" / "tanaj.md"
        self.processed_dir = self.project_root / "data" / "tth"

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

    def extract_verses_from_raw_book(self, book_text: str, book_key: str) -> Dict[Tuple[int, int], str]:
        """Extract all verses from a book text in the raw format."""
        verses = {}

        lines = book_text.split('\n')
        current_chapter = 1  # Start with chapter 1

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Check for chapter marker: **chapter_number**
            chapter_match = re.match(r'^\*\*(\d+)\*\*$', line)
            if chapter_match:
                current_chapter = int(chapter_match.group(1))
                i += 1
                continue

            # Check for verse: **verse_number** verse text
            verse_match = re.match(r'^\*\*(\d+)\*\*\s+(.+)$', line)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2).strip()
                verses[(current_chapter, verse_num)] = verse_text

            i += 1

        return verses

    def load_processed_json(self, book_key: str) -> Dict[str, Any]:
        """Load the processed JSON file for a book."""
        json_file = self.processed_dir / f"{book_key}.json"
        if not json_file.exists():
            raise FileNotFoundError(f"Processed JSON file not found: {json_file}")

        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def find_missing_verses(self, book_key: str) -> List[Tuple[int, int, str]]:
        """Find verses that are in raw but missing from processed JSON."""
        try:
            # Get raw verses
            raw_book_text = self.extract_book_from_raw(book_key)
            raw_verses = self.extract_verses_from_raw_book(raw_book_text, book_key)

            # Get processed verses
            processed_data = self.load_processed_json(book_key)
            processed_verses = set()

            for chapter in processed_data['chapters']:
                chapter_num = chapter['chapter']
                for verse in chapter['verses']:
                    processed_verses.add((chapter_num, verse['verse']))

            # Find missing verses
            missing = []
            for (chap, verse), text in raw_verses.items():
                if (chap, verse) not in processed_verses:
                    missing.append((chap, verse, text))

            return missing

        except Exception as e:
            print(f"Error finding missing verses for {book_key}: {e}")
            return []

    def add_missing_verses_to_json(self, book_key: str, missing_verses: List[Tuple[int, int, str]]) -> bool:
        """Add missing verses to the processed JSON file."""
        if not missing_verses:
            return True

        try:
            # Load current JSON
            json_file = self.processed_dir / f"{book_key}.json"
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Group missing verses by chapter
            missing_by_chapter = {}
            for chap, verse, text in missing_verses:
                if chap not in missing_by_chapter:
                    missing_by_chapter[chap] = []
                missing_by_chapter[chap].append((verse, text))

            # Add missing verses to appropriate chapters
            for chapter in data['chapters']:
                chapter_num = chapter['chapter']
                if chapter_num in missing_by_chapter:
                    existing_verses = {v['verse'] for v in chapter['verses']}

                    for verse_num, verse_text in missing_by_chapter[chapter_num]:
                        if verse_num not in existing_verses:
                            # Create verse entry
                            verse_entry = {
                                'verse': verse_num,
                                'status': 'present',
                                'tth': verse_text,
                                'footnotes': [],  # TODO: extract footnotes if needed
                                'hebrew_terms': []  # TODO: extract hebrew terms if needed
                            }
                            chapter['verses'].append(verse_entry)

                    # Sort verses by verse number
                    chapter['verses'].sort(key=lambda x: x['verse'])

                    # Remove from missing list
                    del missing_by_chapter[chapter_num]

            # Update total verses count
            total_verses = sum(len(chapter['verses']) for chapter in data['chapters'])
            data['book_info']['total_verses'] = total_verses

            # Save updated JSON
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"Added {len(missing_verses)} missing verses to {book_key}")
            return True

        except Exception as e:
            print(f"Error adding missing verses to {book_key}: {e}")
            return False

    def check_book(self, book_key: str) -> None:
        """Check a specific book for missing verses."""
        print(f"Checking {book_key} for missing verses...")

        try:
            missing = self.find_missing_verses(book_key)
            if missing:
                print(f"Found {len(missing)} missing verses in {book_key}:")
                for chap, verse, text in missing:
                    print(f"  Chapter {chap}, Verse {verse}: {text[:100]}...")
            else:
                print(f"No missing verses found in {book_key}")
        except Exception as e:
            print(f"Error checking {book_key}: {e}")

    def fix_book(self, book_key: str) -> bool:
        """Fix missing verses for a specific book."""
        print(f"Fixing {book_key}...")

        try:
            missing = self.find_missing_verses(book_key)
            if missing:
                success = self.add_missing_verses_to_json(book_key, missing)
                if success:
                    print(f"Successfully fixed {book_key}")
                    return True
                else:
                    print(f"Failed to fix {book_key}")
                    return False
            else:
                print(f"No missing verses found in {book_key}")
                return True
        except Exception as e:
            print(f"Error fixing {book_key}: {e}")
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_missing_verses.py [book_key | --all | --check book_key]")
        sys.exit(1)

    fixer = MissingVersesFixer()
    command = sys.argv[1]

    if command == '--all':
        # Fix all books
        books = ['bereshit', 'shemot', 'vaikra', 'bamidbar', 'devarim']
        success_count = 0
        for book in books:
            if fixer.fix_book(book):
                success_count += 1
        print(f"Fixed {success_count}/{len(books)} books")

    elif command == '--check':
        if len(sys.argv) < 3:
            print("Usage: python fix_missing_verses.py --check book_key")
            sys.exit(1)
        fixer.check_book(sys.argv[2])

    else:
        # Fix specific book
        fixer.fix_book(command)


if __name__ == '__main__':
    main()