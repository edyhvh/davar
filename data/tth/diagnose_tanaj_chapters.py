#!/usr/bin/env python3
"""
Diagnóstico de problemas de capítulos en el Tanaj
"""

import re
from pathlib import Path


class TanajChapterDiagnostic:
    def __init__(self, tanaj_file: str = 'tanaj_clean.md'):
        self.tanaj_file = Path(tanaj_file)

    def read_file(self):
        """Read the markdown file"""
        with open(self.tanaj_file, 'r', encoding='utf-8') as f:
            return f.read()

    def analyze_book_chapters(self, book_name: str):
        """Analyze chapter structure for a specific book"""
        text = self.read_file()

        # Find book boundaries - use exact patterns from file
        book_patterns = {
            'bereshit': r'# __TORAH - BERESHIT \(GÉNESIS\)\*\*בראשית\*',
            'mishlei': r'# __MISHLEI \(PROVERBIOS\)\*\*משלי\*',
            'tehilim': r'# __KETUVIM - TEHILIM \(SALMOS\)\*\*תהלים\*',
            'bamidbar': r'# __BAMIDBAR \(NÚMEROS\)\*\*במדבר\*'
        }

        if book_name not in book_patterns:
            print(f"❌ Book {book_name} not in analysis list")
            return f"Book {book_name} not in analysis list"

        # Find book start using simple string search
        book_search_terms = {
            'bereshit': 'BERESHIT',
            'mishlei': 'MISHLEI',
            'tehilim': 'TEHILIM',
            'bamidbar': 'BAMIDBAR'
        }

        search_term = book_search_terms[book_name]
        print(f"🔍 Searching for: {search_term}")

        # Find the SECOND occurrence (content, not index)
        first_pos = text.find(search_term)
        if first_pos == -1:
            print(f"❌ Book {book_name} not found in text")
            return f"Book {book_name} not found"

        start_pos = text.find(search_term, first_pos + 1)
        if start_pos == -1:
            print(f"⚠️ Only one occurrence found for {book_name}, using first one")
            start_pos = first_pos

        # Find the actual start of the book header (go back to find # __)
        header_start = text.rfind('# __', 0, start_pos + len(search_term))
        if header_start == -1:
            print("❌ Could not find book header start")
            return "Could not find book header"

        print(f"✅ Book {book_name} content found at position {header_start}")

        # Find next book or end (use second occurrence if exists)
        next_terms = [term for key, term in book_search_terms.items() if key != book_name]
        end_pos = len(text)
        for term in next_terms:
            # Find first occurrence after our start position
            next_pos = text.find(term, start_pos + 1)
            if next_pos != -1:
                # Go back to find the header start
                header_pos = text.rfind('# __', start_pos, next_pos)
                if header_pos != -1:
                    end_pos = min(end_pos, header_pos)

        book_content = text[start_pos:end_pos]

        print(f"\n🔍 Analyzing {book_name} (length: {len(book_content)} chars)")
        print("=" * 60)

        # Find all chapter markers
        chapter_pattern = r'__(\d+)__'
        all_matches = list(re.finditer(chapter_pattern, book_content))

        print(f"Found {len(all_matches)} chapter markers")

        # Analyze each chapter marker
        chapters_found = {}
        for i, match in enumerate(all_matches):
            chapter_num = int(match.group(1))
            pos = match.start()

            # Get context around the marker
            start_context = max(0, pos - 50)
            end_context = min(len(book_content), pos + 100)
            context = book_content[start_context:end_context]

            # Check if it's a chapter start (at beginning of line or after whitespace)
            line_start = book_content.rfind('\n', 0, pos) + 1
            line_content = book_content[line_start:pos + len(match.group(0)) + 50].strip()

            is_chapter_start = (
                pos == line_start or  # At start of line
                book_content[pos-1] in '\n '  # After newline or space
            )

            chapters_found[chapter_num] = chapters_found.get(chapter_num, 0) + 1

            if i < 10:  # Show first 10
                print(f"Chapter {chapter_num} (x{chapters_found[chapter_num]}):")
                print(f"  Line: {repr(line_content[:80])}")
                print(f"  Is chapter start: {is_chapter_start}")
                print()

        # Summary
        unique_chapters = len(chapters_found)
        duplicates = {k: v for k, v in chapters_found.items() if v > 1}

        print("📊 SUMMARY:")
        print(f"  Unique chapter numbers: {unique_chapters}")
        print(f"  Chapters with duplicates: {len(duplicates)}")
        if duplicates:
            print(f"  Duplicates: {duplicates}")

        # Find missing chapters
        if book_name == 'bereshit':
            expected = 50
        elif book_name == 'mishlei':
            expected = 31
        elif book_name == 'tehilim':
            expected = 150
        elif book_name == 'bamidbar':
            expected = 36
        else:
            expected = 0

        if expected > 0:
            found_nums = set(chapters_found.keys())
            expected_nums = set(range(1, expected + 1))
            missing = expected_nums - found_nums
            extra = found_nums - expected_nums

            print(f"  Expected chapters: {expected}")
            print(f"  Missing chapters: {sorted(missing) if missing else 'None'}")
            print(f"  Extra chapters: {sorted(extra) if extra else 'None'}")

        return chapters_found

    def diagnose_marker_patterns(self, book_name: str):
        """Diagnose different marker patterns in a book"""
        text = self.read_file()

        # Find book boundaries (same as above)
        book_patterns = {
            'bereshit': r'# __TORAH - BERESHIT \(GÉNESIS\)\*\*בראשית\*',
            'mishlei': r'# __MISHLEI \(PROVERBIOS\)\*\*משלי\*',
            'tehilim': r'# __KETUVIM - TEHILIM \(SALMOS\)\*\*תהלים\*',
            'bamidbar': r'# __BAMIDBAR \(NÚMEROS\)\*\*במדבר\*'
        }

        start_pattern = book_patterns[book_name]
        start_match = re.search(start_pattern, text)
        if not start_match:
            return f"Book {book_name} not found"

        start_pos = start_match.start()

        # Find next book
        next_patterns = [p for k, p in book_patterns.items() if k != book_name]
        end_pos = len(text)
        for pattern in next_patterns:
            match = re.search(pattern, text[start_pos:])
            if match:
                end_pos = min(end_pos, start_pos + match.start())

        book_content = text[start_pos:end_pos]

        print(f"\n🔧 Diagnosing marker patterns in {book_name}")
        print("=" * 60)

        lines = book_content.split('\n')

        # Analyze patterns
        patterns_found = {}

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Check different patterns
            if re.match(r'^__\d+__$', line):
                pattern = "SOLO_NUMERO"
            elif re.match(r'^__\d+__\s+.+', line):
                pattern = "NUMERO_CON_TEXTO"
            elif '__' in line and re.search(r'__\d+__', line):
                pattern = "NUMERO_EN_LINEA"
            else:
                continue

            if pattern not in patterns_found:
                patterns_found[pattern] = []

            patterns_found[pattern].append((i, line[:100]))

        for pattern, examples in patterns_found.items():
            print(f"\n{pattern}: {len(examples)} ocurrencias")
            for i, (line_num, text) in enumerate(examples[:5]):  # Show first 5
                print(f"  Línea {line_num}: {repr(text)}")


def main():
    diagnostic = TanajChapterDiagnostic()

    # Analyze problematic books
    problematic_books = ['bereshit', 'mishlei', 'tehilim', 'bamidbar']

    for book in problematic_books:
        print(f"\n{'='*80}")
        print(f"ANALIZANDO LIBRO: {book.upper()}")
        print('='*80)

        # Chapter analysis
        chapters = diagnostic.analyze_book_chapters(book)

        # Pattern diagnosis
        diagnostic.diagnose_marker_patterns(book)


if __name__ == '__main__':
    main()
