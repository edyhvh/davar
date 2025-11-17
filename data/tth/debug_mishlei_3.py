#!/usr/bin/env python3
"""
Debug específico para el capítulo 3 de Mishlei
"""

import re
from pathlib import Path


def debug_mishlei_chapter_3():
    """Debug what happens with Mishlei chapter 3"""

    # Read the clean file
    with open('tanaj_clean.md', 'r', encoding='utf-8') as f:
        text = f.read()

    # Find Mishlei book boundaries
    book_patterns = {
        'mishlei': r'# __MISHLEI \(PROVERBIOS\)\*\*משלי\*'
    }

    start_pattern = book_patterns['mishlei']
    matches = list(re.finditer(start_pattern, text))

    if len(matches) < 2:
        print("No se encontraron suficientes ocurrencias de Mishlei")
        return

    # Use second occurrence (content)
    start_pos = matches[1].start()

    # Find end
    next_books = ['tehilim']
    end_pos = len(text)
    for next_book in next_books:
        next_pattern = r'# __' + next_book.upper() + r'.*\*\*.*\*'
        next_matches = list(re.finditer(next_pattern, text[start_pos:]))
        if next_matches:
            end_pos = min(end_pos, start_pos + next_matches[0].start())

    book_content = text[start_pos:end_pos]
    lines = book_content.split('\n')

    print(f"Mishlei content length: {len(book_content)} chars")
    print(f"Mishlei lines: {len(lines)}")

    # Find all chapter markers
    chapter_markers = []
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if re.match(r'^__(\d+)__$', line_stripped):
            chapter_num = int(re.match(r'^__(\d+)__$', line_stripped).group(1))
            chapter_markers.append((i, chapter_num))

    print(f"Found chapter markers: {len(chapter_markers)}")
    for line_num, chap_num in chapter_markers[:10]:  # First 10
        print(f"  Line {line_num}: Chapter {chap_num}")

    # Focus on chapter 3
    chapter_3_start = None
    chapter_4_start = None

    for line_num, chap_num in chapter_markers:
        if chap_num == 3:
            chapter_3_start = line_num
        elif chap_num == 4:
            chapter_4_start = line_num
            break

    if chapter_3_start is None:
        print("❌ Chapter 3 marker not found!")
        return

    print(f"✅ Chapter 3 starts at line {chapter_3_start}")

    # Extract chapter 3 content
    end_line = chapter_4_start if chapter_4_start else min(chapter_3_start + 100, len(lines))
    chapter_3_lines = lines[chapter_3_start:end_line]

    print(f"Chapter 3 has {len(chapter_3_lines)} lines")

    # Find verses in chapter 3
    verses_found = []
    for i, line in enumerate(chapter_3_lines):
        verse_markers = re.findall(r'__(\d+)__', line)
        if verse_markers:
            for verse_num in verse_markers:
                verses_found.append(int(verse_num))
                print(f"  Found verse {verse_num} in line: {line.strip()[:80]}...")

    print(f"Verses found in chapter 3: {sorted(set(verses_found))}")

    if verses_found:
        min_verse = min(verses_found)
        print(f"First verse in chapter 3: {min_verse}")

        # Check post-processing rules
        if min_verse > 20:
            print("❌ Chapter 3 would be rejected: starts with verse > 20")
        else:
            print("✅ Chapter 3 should pass verse number check")

        # Check verse consecutiveness
        unique_verses = sorted(set(verses_found))
        if len(unique_verses) > 1:
            gaps = [unique_verses[i+1] - unique_verses[i] for i in range(len(unique_verses)-1)]
            avg_gap = sum(gaps) / len(gaps) if gaps else 0
            print(f"Verse gaps: {gaps}")
            print(f"Average gap: {avg_gap:.2f}")
            if avg_gap > 10:
                print("❌ Chapter 3 would be rejected: too many gaps in verses")
            else:
                print("✅ Chapter 3 should pass gap check")
    else:
        print("❌ Chapter 3 has no verses - would be rejected")


if __name__ == '__main__':
    debug_mishlei_chapter_3()













