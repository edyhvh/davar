"""Consolidate verses into final JSON per book."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict

from .validate import validate_chapter_sequence, validate_verse_sequence
from .books import HEBREW_NUMERALS

logger = logging.getLogger(__name__)


def load_verses_from_checkpoint(checkpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Load all processed verses from checkpoint."""
    verses = []
    if 'images' not in checkpoint:
        return verses

    for image_name, image_data in checkpoint['images'].items():
        if image_data.get('status') == 'completed' and 'verses' in image_data:
            for verse_key, verse_data in image_data['verses'].items():
                if verse_data.get('status') == 'completed':
                    verses.append({
                        'chapter': verse_data.get('chapter'),
                        'verse': verse_data.get('verse'),
                        'text_nikud': verse_data.get('text_nikud'),
                        'source_files': verse_data.get('source_files', [image_name]),
                        'visual_uncertainty': verse_data.get('visual_uncertainty', [])
                    })
    return verses


def merge_duplicate_verses(verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Handle verses that appear in multiple images.

    Selects the best version based on text length and source file order.
    """
    verse_candidates: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}

    for verse in verses:
        chapter, verse_num = verse.get('chapter'), verse.get('verse')
        if chapter is None or verse_num is None:
            continue
        key = (chapter, verse_num)
        if key not in verse_candidates:
            verse_candidates[key] = []
        verse_candidates[key].append(verse)

    merged = []
    duplicates_found = 0

    for key, candidates in verse_candidates.items():
        chapter, verse_num = key

        if len(candidates) == 1:
            merged.append(candidates[0])
            continue

        duplicates_found += len(candidates) - 1

        all_sources = set()
        all_uncertainty = []
        for c in candidates:
            if isinstance(c.get('source_files'), list):
                all_sources.update(c['source_files'])
            if isinstance(c.get('visual_uncertainty'), list):
                all_uncertainty.extend(c['visual_uncertainty'])

        # Select best by text length
        best = max(candidates, key=lambda c: len(c.get('text_nikud', '')))

        if all_uncertainty:
            all_uncertainty = sorted(list(set(all_uncertainty)))

        merged_verse = {
            'chapter': chapter,
            'verse': verse_num,
            'text_nikud': best.get('text_nikud', ''),
            'source_files': sorted(list(all_sources)),
            'visual_uncertainty': all_uncertainty
        }

        if len(all_sources) > 1:
            merged_verse['multiple_sources'] = True

        merged.append(merged_verse)

    if duplicates_found > 0:
        logger.info(f"Resolved {duplicates_found} duplicate verse entries")

    return merged


def group_by_chapter(verses: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    """Group verses by chapter number."""
    chapters = defaultdict(list)
    for verse in verses:
        chapter_num = verse.get('chapter')
        if chapter_num is not None:
            chapters[chapter_num].append(verse)

    for chapter_num in chapters:
        chapters[chapter_num].sort(key=lambda v: v.get('verse', 0))

    return dict(chapters)


def build_book_json(book_name: str, chapters: Dict[int, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Build final JSON following schema."""
    chapters_list = []

    for chapter_num in sorted(chapters.keys()):
        chapter_verses = chapters[chapter_num]
        hebrew_letter = HEBREW_NUMERALS.get(chapter_num, str(chapter_num))

        verses_list = [{
            'number': verse.get('verse'),
            'text_nikud': verse.get('text_nikud', ''),
            'source_files': verse.get('source_files', []),
            'visual_uncertainty': verse.get('visual_uncertainty', [])
        } for verse in chapter_verses]

        chapters_list.append({
            'hebrew_letter': hebrew_letter,
            'number': chapter_num,
            'verses': verses_list
        })

    return {
        'book_name': book_name,
        'author': 'Elias Hutter',
        'publication_year': '1599–1602',
        'chapters': chapters_list
    }


def validate_complete_sequence(chapters: Dict[int, List[Dict[str, Any]]]) -> Tuple[bool, Optional[str]]:
    """Verify no gaps before finalizing."""
    if not chapters:
        return False, "No chapters found"

    chapter_list = [{'number': num} for num in chapters.keys()]
    is_valid, error, missing = validate_chapter_sequence(chapter_list)
    if not is_valid:
        return False, error

    for chapter_num, verses in chapters.items():
        verses_for_validation = [{'number': v.get('verse')} for v in verses]
        is_valid, error, missing = validate_verse_sequence(verses_for_validation)
        if not is_valid:
            return False, f"Chapter {chapter_num}: {error}"

    return True, None


def save_book_json(book_json: Dict[str, Any], output_path: Path) -> bool:
    """Save final JSON to output directory."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(book_json, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save book JSON: {e}")
        return False


def consolidate_book(checkpoint: Dict[str, Any], book_name: str, output_dir: Path) -> bool:
    """Consolidate verses from checkpoint into final book JSON."""
    verses = load_verses_from_checkpoint(checkpoint)
    if not verses:
        logger.warning(f"No verses found for {book_name}")
        return False

    logger.info(f"Consolidating {len(verses)} verses for {book_name}")

    verses = merge_duplicate_verses(verses)
    logger.info(f"After merging: {len(verses)} unique verses")

    chapters = group_by_chapter(verses)
    logger.info(f"Found {len(chapters)} chapters")

    is_valid, error = validate_complete_sequence(chapters)
    if not is_valid:
        logger.warning(f"Sequence validation failed: {error}")

    book_json = build_book_json(book_name, chapters)
    output_path = output_dir / f"{book_name}.json"

    return save_book_json(book_json, output_path)

