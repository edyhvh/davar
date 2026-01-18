#!/usr/bin/env python3
"""
Check All Missing Verses in TTH Draft Files
===========================================

Comprehensive script to check all TTH books and chapters for missing last verses.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import sys


class TTHMissingVersesChecker:
    """Class to check for missing verses across all TTH books."""

    def __init__(self):
        self.project_root = Path.home() / "davar"
        self.raw_file = self.project_root / "data" / "tth" / "raw" / "tanaj.md"
        self.draft_dir = self.project_root / "data" / "tth" / "draft"

        # Book boundaries in tanaj.md
        self.book_boundaries = {
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

    def read_raw_file(self) -> str:
        """Read the raw tanaj.md file."""
        with open(self.raw_file, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_book_from_raw(self, book_key: str) -> str:
        """Extract a specific book from the raw tanaj.md file."""
        content = self.read_raw_file()

        if book_key not in self.book_boundaries:
            return ""

        start_marker, end_marker = self.book_boundaries[book_key]

        start_pos = content.find(start_marker)
        if start_pos == -1:
            # Try alternatives
            alternatives = ['TORAH - BERESHIT', '**1** TORAH', 'BERESHIT', '__SHEMOT', '__VAIKRA', '__BAMIDBAR', '__DEVARIM']
            for alt in alternatives:
                if alt in content:
                    start_pos = content.find(alt)
                    if start_pos != -1:
                        break

        if start_pos == -1:
            return ""

        end_pos = content.find(end_marker, start_pos)
        if end_pos == -1:
            end_pos = len(content)

        return content[start_pos:end_pos]

    def get_expected_last_verse(self, book_key: str, chapter_num: int) -> int:
        """Get the expected last verse number for a chapter."""
        book_text = self.extract_book_from_raw(book_key)
        if not book_text:
            return 0

        # Find the chapter
        chapter_pattern = f"\n\\*\\*{chapter_num}\\*\\*\n"
        match = re.search(chapter_pattern, book_text)
        if not match:
            return 0

        start_pos = match.start()

        # Find next chapter or end
        next_chapter_pattern = f"\n\\*\\*{chapter_num + 1}\\*\\*\n"
        next_match = re.search(next_chapter_pattern, book_text[start_pos + 1:])

        if next_match:
            end_pos = start_pos + 1 + next_match.start()
        else:
            end_pos = len(book_text)

        chapter_text = book_text[start_pos:end_pos]

        # Find all verse numbers in this chapter
        verse_nums = []
        lines = chapter_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            verse_match = re.match(r'^\*\*(\d+)\*\*\s+(.+)$', line)
            if verse_match:
                verse_nums.append(int(verse_match.group(1)))

        return max(verse_nums) if verse_nums else 0

    def get_actual_last_verse(self, book_key: str, chapter_num: int) -> int:
        """Get the actual last verse number in a draft chapter file."""
        chapter_file = self.draft_dir / book_key / f"{chapter_num:02d}.json"
        if not chapter_file.exists():
            return 0

        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                verses = json.load(f)

            if not verses:
                return 0

            return max(v['verse'] for v in verses)
        except:
            return 0

    def check_chapter(self, book_key: str, chapter_num: int) -> Tuple[bool, int, int]:
        """Check if a chapter has its last verse. Returns (is_missing, expected, actual)."""
        expected = self.get_expected_last_verse(book_key, chapter_num)
        actual = self.get_actual_last_verse(book_key, chapter_num)

        if expected == 0:
            return False, 0, actual  # Can't determine expected

        is_missing = actual < expected
        return is_missing, expected, actual

    def check_book(self, book_key: str) -> Dict[str, Any]:
        """Check all chapters in a book for missing last verses."""
        book_dir = self.draft_dir / book_key
        if not book_dir.exists():
            return {'book': book_key, 'exists': False, 'chapters': []}

        chapters = []
        missing_count = 0

        for chapter_file in sorted(book_dir.glob("*.json")):
            if chapter_file.stem == 'book_info':
                continue  # Skip book_info.json files

            try:
                chapter_num = int(chapter_file.stem)
            except ValueError:
                continue  # Skip files that don't have numeric names

            is_missing, expected, actual = self.check_chapter(book_key, chapter_num)

            if is_missing:
                missing_count += 1

            chapters.append({
                'chapter': chapter_num,
                'missing': is_missing,
                'expected': expected,
                'actual': actual
            })

        return {
            'book': book_key,
            'exists': True,
            'total_chapters': len(chapters),
            'missing_chapters': missing_count,
            'chapters': chapters
        }

    def check_all_books(self) -> Dict[str, Any]:
        """Check all TTH books for missing verses."""
        books = [
            # Torah
            'bereshit', 'shemot', 'vaikra', 'bamidbar', 'devarim',
            # Neviim
            'iehoshua', 'shoftim', 'shemuel_alef', 'shemuel_bet', 'melajim_alef', 'melajim_bet',
            'ieshaiahu', 'irmeiahu', 'iejezkel', 'hoshea', 'ioel', 'amos', 'ionah', 'micah',
            'najum', 'jabakuk', 'tzefaniah', 'jagai', 'zejariah', 'malaji',
            # Ketuvim
            'tehilim', 'mishlei'
        ]
        results = {}

        total_books = 0
        total_chapters = 0
        total_missing = 0

        for book_key in books:
            book_result = self.check_book(book_key)
            results[book_key] = book_result

            if book_result['exists']:
                total_books += 1
                total_chapters += book_result['total_chapters']
                total_missing += book_result['missing_chapters']

        results['summary'] = {
            'books_checked': total_books,
            'total_chapters': total_chapters,
            'total_missing': total_missing,
            'books_with_missing': sum(1 for r in results.values() if isinstance(r, dict) and r.get('missing_chapters', 0) > 0)
        }

        return results

    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print a formatted summary of missing verses."""
        summary = results['summary']

        print("=" * 70)
        print("TTH MISSING VERSES SUMMARY")
        print("=" * 70)
        print(f"Books checked: {summary['books_checked']}")
        print(f"Total chapters: {summary['total_chapters']}")
        print(f"Chapters with missing last verses: {summary['total_missing']}")
        print(f"Books with missing verses: {summary['books_with_missing']}")
        print()

        # Group books by category
        torah_books = ['bereshit', 'shemot', 'vaikra', 'bamidbar', 'devarim']
        neviim_books = ['iehoshua', 'shoftim', 'shemuel_alef', 'shemuel_bet', 'melajim_alef', 'melajim_bet',
                       'ieshaiahu', 'irmeiahu', 'iejezkel', 'hoshea', 'ioel', 'amos', 'ionah', 'micah',
                       'najum', 'jabakuk', 'tzefaniah', 'jagai', 'zejariah', 'malaji']
        ketuvim_books = ['tehilim', 'mishlei']

        all_books = torah_books + neviim_books + ketuvim_books

        for book_key in all_books:
            if book_key in results:
                book_result = results[book_key]
                if not book_result['exists']:
                    print(f"❌ {book_key}: Book directory not found")
                    continue

                missing = book_result['missing_chapters']
                total = book_result['total_chapters']

                if missing > 0:
                    print(f"⚠️  {book_key}: {missing}/{total} chapters missing last verses")
                else:
                    print(f"✅ {book_key}: All {total} chapters complete")

        print()
        print("DETAILED BREAKDOWN:")
        print("-" * 50)

        for book_key in all_books:
            if book_key in results:
                book_result = results[book_key]
                if book_result['exists'] and book_result['missing_chapters'] > 0:
                    print(f"\n{book_key.upper()}:")
                    for chapter in book_result['chapters']:
                        if chapter['missing']:
                            ch = chapter['chapter']
                            exp = chapter['expected']
                            act = chapter['actual']
                            print(f"  Chapter {ch}: missing verse {exp} (has {act})")


def main():
    checker = TTHMissingVersesChecker()
    results = checker.check_all_books()
    checker.print_summary(results)


if __name__ == '__main__':
    main()