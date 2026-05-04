"""Biblical book structure reference for validation and prompt enhancement."""

import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Book structure: book_name -> list of verse counts per chapter
BOOK_STRUCTURE = {
    # Gospels
    'matthew': [25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20],
    'mark': [45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20],
    'luke': [80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53],
    'john': [51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25],
    # Acts
    'acts': [26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31],
    # Pauline Epistles
    'romans': [32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27],
    'corinthians1': [31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24],
    'corinthians2': [24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14],
    'galatians': [24, 21, 29, 31, 26, 18],
    'ephesians': [23, 22, 21, 32, 33, 24],
    'philippians': [30, 30, 21, 23],
    'colossians': [29, 23, 25, 18],
    'thessalonians1': [10, 20, 13, 18, 28],
    'thessalonians2': [12, 17, 18],
    'timothy1': [20, 15, 16, 16, 25, 21],
    'timothy2': [18, 26, 17, 22],
    'titus': [16, 15, 15],
    'philemon': [25],
    # Hebrews
    'hebrews': [14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25],
    # General Epistles
    'james': [27, 26, 18, 17, 20],
    'peter1': [25, 25, 22, 19, 14],
    'peter2': [21, 22, 18],
    'john1': [10, 29, 24, 21, 21],
    'john2': [13],
    'john3': [15],
    'jude': [25],
    # Revelation
    'revelation': [20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21],
}

HEBREW_NUMERALS = {
    1: 'א', 2: 'ב', 3: 'ג', 4: 'ד', 5: 'ה', 6: 'ו', 7: 'ז', 8: 'ח', 9: 'ט',
    10: 'י', 11: 'יא', 12: 'יב', 13: 'יג', 14: 'יד', 15: 'טו', 16: 'טז',
    17: 'יז', 18: 'יח', 19: 'יט', 20: 'כ', 21: 'כא', 22: 'כב', 23: 'כג',
    24: 'כד', 25: 'כה', 26: 'כו', 27: 'כז', 28: 'כח', 29: 'כט', 30: 'ל',
    31: 'לא', 32: 'לב', 33: 'לג', 34: 'לד', 35: 'לה', 36: 'לו', 37: 'לז',
    38: 'לח', 39: 'לט', 40: 'מ', 41: 'מא', 42: 'מב', 43: 'מג', 44: 'מד',
    45: 'מה', 46: 'מו', 47: 'מז', 48: 'מח', 49: 'מט', 50: 'נ'
}


def get_book_info(book_name: str) -> Optional[Dict[str, Any]]:
    """Get structural information about a book."""
    book_name = book_name.lower()
    if book_name not in BOOK_STRUCTURE:
        return None

    verses_per_chapter = BOOK_STRUCTURE[book_name]
    return {
        'book_name': book_name,
        'total_chapters': len(verses_per_chapter),
        'total_verses': sum(verses_per_chapter),
        'verses_per_chapter': verses_per_chapter,
    }


def get_chapter_context(book_name: str) -> str:
    """Generate context string for the prompt about book structure."""
    info = get_book_info(book_name)
    if not info:
        return ""

    lines = [
        f"\n## CRITICAL: Book Structure for {book_name.upper()}",
        f"This book has exactly {info['total_chapters']} chapter(s) and {info['total_verses']} verses total.",
    ]

    if info['total_chapters'] == 1:
        lines.extend([
            f"⚠️ THIS BOOK HAS ONLY 1 CHAPTER. All verses belong to chapter 1.",
            f"Chapter 1 has {info['verses_per_chapter'][0]} verses (1-{info['verses_per_chapter'][0]}).",
            "DO NOT create multiple chapters. Any chapter number other than 1 is WRONG."
        ])
    else:
        lines.append("Chapter structure:")
        for i, verses in enumerate(info['verses_per_chapter'], 1):
            lines.append(f"  - Chapter {i}: {verses} verses")

    return "\n".join(lines)


def validate_chapter_number(book_name: str, chapter_num: int) -> bool:
    """Validate if a chapter number is valid for the book."""
    info = get_book_info(book_name)
    if not info:
        return True
    return 1 <= chapter_num <= info['total_chapters']


def validate_verse_number(book_name: str, chapter_num: int, verse_num: int) -> bool:
    """Validate if a verse number is valid for the chapter."""
    info = get_book_info(book_name)
    if not info or not validate_chapter_number(book_name, chapter_num):
        return True
    max_verses = info['verses_per_chapter'][chapter_num - 1]
    return 1 <= verse_num <= max_verses


def fix_chapter_assignment(book_name: str, chapters_data: list) -> list:
    """Fix chapter assignments based on book structure."""
    info = get_book_info(book_name)
    if not info:
        return chapters_data

    # Single chapter book - merge all verses into chapter 1
    if info['total_chapters'] == 1:
        all_verses = []
        for chapter in chapters_data:
            if 'verses' in chapter:
                all_verses.extend(chapter['verses'])

        seen = set()
        unique_verses = []
        for verse in sorted(all_verses, key=lambda v: v.get('number', 0)):
            verse_num = verse.get('number', 0)
            if verse_num not in seen and 1 <= verse_num <= info['verses_per_chapter'][0]:
                seen.add(verse_num)
                unique_verses.append(verse)

        return [{
            'hebrew_letter': 'א',
            'number': 1,
            'verses': unique_verses
        }]

    # Multi-chapter book - filter out invalid chapters
    valid_chapters = []
    for chapter in chapters_data:
        chapter_num = chapter.get('number', 0)
        if validate_chapter_number(book_name, chapter_num):
            valid_verses = [
                v for v in chapter.get('verses', [])
                if validate_verse_number(book_name, chapter_num, v.get('number', 0))
            ]
            if valid_verses:
                chapter['verses'] = valid_verses
                valid_chapters.append(chapter)

    return valid_chapters


def infer_chapter_from_sequence(
    book_name: str,
    previous_context: dict,
    current_chapters_data: list,
    image_name: str = ""
) -> Tuple[list, dict]:
    """
    Validate and correct chapter assignments based on sequential context.

    Returns:
        Tuple of (corrected_chapters_data, updated_context)
    """
    info = get_book_info(book_name)
    if not info:
        return current_chapters_data, previous_context

    prev_chapter = previous_context.get('last_chapter', 0)
    prev_verse = previous_context.get('last_verse', 0)

    if prev_chapter == 0:
        return current_chapters_data, _extract_last_verse_context(current_chapters_data)

    # Collect all verses
    all_verses = []
    for chapter in current_chapters_data:
        ch_num = chapter.get('number', 0)
        for verse in chapter.get('verses', []):
            all_verses.append({
                'original_chapter': ch_num,
                'verse_num': verse.get('number', 0),
                'verse_data': verse
            })

    if not all_verses:
        return current_chapters_data, previous_context

    # Calculate expected chapter
    expected_chapter = prev_chapter
    max_verse_prev = info['verses_per_chapter'][prev_chapter - 1]
    if prev_verse >= max_verse_prev and expected_chapter < info['total_chapters']:
        expected_chapter += 1

    # Check if model's chapters are plausible
    model_chapters = set(v['original_chapter'] for v in all_verses)
    corrections_needed = False
    chapter_offset = 0

    for model_ch in model_chapters:
        if model_ch < 1 or model_ch > info['total_chapters']:
            corrections_needed = True
            break

        diff = model_ch - expected_chapter

        if model_ch == info['total_chapters'] and expected_chapter < info['total_chapters'] - 3:
            corrections_needed = True
            chapter_offset = expected_chapter - model_ch
            break

        if abs(diff) > 3:
            corrections_needed = True
            chapter_offset = expected_chapter - model_ch
            break

    if not corrections_needed:
        result_chapters = []
        for chapter in current_chapters_data:
            ch_num = chapter.get('number', 0)
            if ch_num < 1 or ch_num > info['total_chapters']:
                continue
            max_v = info['verses_per_chapter'][ch_num - 1]
            valid_verses = [v for v in chapter.get('verses', []) if 1 <= v.get('number', 0) <= max_v]
            if valid_verses:
                result_chapters.append({
                    'number': ch_num,
                    'hebrew_letter': HEBREW_NUMERALS.get(ch_num, str(ch_num)),
                    'verses': valid_verses
                })
        return result_chapters, _extract_last_verse_context(result_chapters)

    # Apply sequential correction
    logger.info(f"{image_name}: Applying sequential correction (offset={chapter_offset})")

    current_chapter = expected_chapter
    max_verse_in_current = info['verses_per_chapter'][current_chapter - 1]
    corrected_chapters = {}
    last_processed = prev_verse if prev_verse < max_verse_prev else 0

    for v_info in all_verses:
        verse_num = v_info['verse_num']
        verse_data = v_info['verse_data']

        if verse_num < last_processed and last_processed - verse_num > 5:
            if current_chapter < info['total_chapters']:
                current_chapter += 1
                max_verse_in_current = info['verses_per_chapter'][current_chapter - 1]
                last_processed = 0

        while verse_num > max_verse_in_current and current_chapter < info['total_chapters']:
            current_chapter += 1
            max_verse_in_current = info['verses_per_chapter'][current_chapter - 1]

        if verse_num > max_verse_in_current:
            continue

        if current_chapter not in corrected_chapters:
            corrected_chapters[current_chapter] = []
        corrected_chapters[current_chapter].append(verse_data)
        last_processed = verse_num

    result = []
    for ch_num in sorted(corrected_chapters.keys()):
        result.append({
            'number': ch_num,
            'hebrew_letter': HEBREW_NUMERALS.get(ch_num, str(ch_num)),
            'verses': corrected_chapters[ch_num]
        })

    return result, _extract_last_verse_context(result)


def _extract_last_verse_context(chapters_data: list) -> dict:
    """Extract the last chapter and verse from chapters data."""
    last_chapter, last_verse = 0, 0
    for chapter in chapters_data:
        ch_num = chapter.get('number', 0)
        for verse in chapter.get('verses', []):
            v_num = verse.get('number', 0)
            if ch_num > last_chapter or (ch_num == last_chapter and v_num > last_verse):
                last_chapter, last_verse = ch_num, v_num
    return {'last_chapter': last_chapter, 'last_verse': last_verse}


def get_sequence_context_for_prompt(book_name: str, previous_context: dict) -> str:
    """Generate prompt context about expected chapter/verse based on sequence."""
    if not previous_context or previous_context.get('last_chapter', 0) == 0:
        return ""

    info = get_book_info(book_name)
    if not info:
        return ""

    prev_ch = previous_context['last_chapter']
    prev_v = previous_context['last_verse']
    max_v = info['verses_per_chapter'][prev_ch - 1]

    lines = [
        f"\n## SEQUENTIAL CONTEXT (from previous page)",
        f"The previous page ended at Chapter {prev_ch}, Verse {prev_v}.",
    ]

    if prev_v >= max_v:
        if prev_ch < info['total_chapters']:
            next_ch = prev_ch + 1
            lines.extend([
                f"⚠️ EXPECTED: This page should START with Chapter {next_ch}, Verse 1.",
                f"Chapter {next_ch} has {info['verses_per_chapter'][next_ch - 1]} verses."
            ])
    else:
        expected_next = prev_v + 1
        remaining = max_v - prev_v
        lines.extend([
            f"⚠️ EXPECTED: This page should CONTINUE with Chapter {prev_ch}, Verse {expected_next}.",
            f"Chapter {prev_ch} has {remaining} verses remaining ({expected_next}-{max_v})."
        ])
        if prev_ch < info['total_chapters']:
            next_ch = prev_ch + 1
            lines.append(
                f"If this page completes Chapter {prev_ch}, Chapter {next_ch} begins next "
                f"({info['verses_per_chapter'][next_ch - 1]} verses)."
            )

    return "\n".join(lines)


def diagnose_checkpoint(book_name: str, checkpoint_data: dict) -> dict:
    """Analyze a checkpoint to detect potential chapter assignment errors."""
    info = get_book_info(book_name)
    if not info:
        return {'error': f'Unknown book: {book_name}'}

    images = checkpoint_data.get('images', {})
    total_chapters = info['total_chapters']
    verse_sources = {}
    chapter_by_image = {}

    for img_name, img_data in sorted(images.items()):
        if img_data.get('status') not in ('success', 'completed'):
            continue
        chapters_seen = set()
        for verse_key, verse_data in img_data.get('verses', {}).items():
            ch, v = verse_data.get('chapter', 0), verse_data.get('verse', 0)
            if ch < 1 or v < 1:
                continue
            chapters_seen.add(ch)
            key = (ch, v)
            if key not in verse_sources:
                verse_sources[key] = []
            verse_sources[key].append(img_name)
        chapter_by_image[img_name] = chapters_seen

    problems = []

    # Check for duplicates
    duplicates = {k: v for k, v in verse_sources.items() if len(v) > 1}
    if len(duplicates) > 10:
        problems.append({
            'type': 'excessive_duplicates',
            'count': len(duplicates),
            'message': f'Found {len(duplicates)} duplicate verse entries'
        })

    # Check for invalid chapters
    invalid = [(k, v) for k, v in verse_sources.items() if k[0] > total_chapters]
    if invalid:
        problems.append({
            'type': 'invalid_chapters',
            'count': len(invalid),
            'message': f'Found {len(invalid)} verses in invalid chapters'
        })

    # Check for last-chapter concentration
    last_ch_verses = len([k for k in verse_sources.keys() if k[0] == total_chapters])
    expected_last = info['verses_per_chapter'][-1]
    if last_ch_verses > expected_last * 3:
        problems.append({
            'type': 'last_chapter_overload',
            'expected': expected_last,
            'found': last_ch_verses,
            'message': f'Last chapter has {last_ch_verses} entries (expected {expected_last})'
        })

    return {
        'book_name': book_name,
        'total_images': len(images),
        'total_verse_entries': len(verse_sources),
        'expected_verses': info['total_verses'],
        'duplicate_count': len(duplicates),
        'problems': problems,
        'health': 'OK' if not problems else 'ISSUES_DETECTED'
    }

