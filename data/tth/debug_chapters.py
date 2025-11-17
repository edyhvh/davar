#!/usr/bin/env python3
"""
Debug script para entender por qué se están detectando capítulos falsos
"""

import re
from pathlib import Path


def debug_book_chapters(book_name: str):
    """Debug chapter detection for a specific book"""

    # Read the clean file
    with open('tanaj_clean.md', 'r', encoding='utf-8') as f:
        text = f.read()

    # Find book boundaries
    book_patterns = {
        'bereshit': r'# __TORAH - BERESHIT \(GÉNESIS\)\*\*בראשית\*',
        'tehilim': r'# __KETUVIM - TEHILIM \(SALMOS\)\*\*תהלים\*',
        'mishlei': r'# __MISHLEI \(PROVERBIOS\)\*\*משלי\*'
    }

    start_pattern = book_patterns[book_name]
    matches = list(re.finditer(start_pattern, text))

    if len(matches) < 2:
        print(f"No se encontraron suficientes ocurrencias de {book_name}")
        return

    # Use second occurrence (content)
    start_pos = matches[1].start()

    # Find end (next book)
    next_books = [b for b in book_patterns.keys() if b != book_name]
    end_pos = len(text)
    for next_book in next_books:
        next_pattern = book_patterns[next_book]
        next_matches = list(re.finditer(next_pattern, text[start_pos:]))
        if next_matches:
            end_pos = min(end_pos, start_pos + next_matches[0].start())

    book_content = text[start_pos:end_pos]
    lines = book_content.split('\n')

    print(f"📖 Analizando {book_name} - {len(lines)} líneas")
    print("=" * 60)

    chapter_starts = []
    verse_markers = []

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Check for chapter markers (exact match)
        chapter_match = re.match(r'^__(\d+)__$', line_stripped)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            chapter_starts.append((i, chapter_num, line_stripped))
            print(f"📄 Línea {i+1}: CAPÍTULO {chapter_num} encontrado")

        # Check for verse markers within text
        verse_matches = re.findall(r'__(\d+)__', line_stripped)
        if verse_matches and not chapter_match:  # Don't count if it's a chapter marker
            for verse_num in verse_matches:
                verse_markers.append((i, int(verse_num), line_stripped[:100]))
                print(f"📝 Línea {i+1}: Versículo {verse_num} en texto: {line_stripped[:80]}...")

    print(f"\n📊 RESUMEN:")
    print(f"  Marcadores de capítulo encontrados: {len(chapter_starts)}")
    print(f"  Marcadores de versículo en texto: {len(verse_markers)}")

    if chapter_starts:
        print(f"\n📄 Capítulos detectados: {[num for _, num, _ in chapter_starts]}")

    if len(chapter_starts) > 10:
        print(f"\n⚠️  ¡Demasiados capítulos detectados! Primeros 10:")
        for i, (line_num, chap_num, line_text) in enumerate(chapter_starts[:10]):
            print(f"  {i+1}. Línea {line_num}: Capítulo {chap_num}")


if __name__ == '__main__':
    print("🔍 DEBUG: Detección de capítulos en libros del Tanaj")
    print()

    for book in ['bereshit', 'tehilim', 'mishlei']:
        print(f"\n{'='*80}")
        print(f"ANALIZANDO: {book.upper()}")
        print('='*80)
        debug_book_chapters(book)













