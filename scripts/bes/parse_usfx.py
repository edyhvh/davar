#!/usr/bin/env python3
"""
Parse BES (Biblia en Español Sencillo) USFX XML into TTH2-compatible JSON format
"""

import xml.etree.ElementTree as ET
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from config import USFX_TO_ENGLISH, BOOK_METADATA, get_book_metadata

logger = logging.getLogger(__name__)

# Input/output paths
INPUT_XML = Path(__file__).parent.parent.parent / "data" / "bes" / "raw" / "spa-bes.usfx.xml"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "bes" / "json"

def clean_verse_text(text: str) -> str:
    """
    Clean verse text by removing USFX formatting tags and normalizing whitespace.

    USFX tags to remove: <f> (footnotes), <add> (additions), <wj> (words of Jesus),
    <nd> (name of deity), <w> (words with Strong's), <ve> (verse end), etc.
    """
    if not text:
        return ""

    # Remove common USFX tags that don't contribute to verse text
    tags_to_remove = ['f', 'fe', 'x', 'add', 'wj', 'nd', 'tl', 'bk', 'dc', 'qs', 'w', 've', 'v']

    # Simple tag removal - remove tags with attributes and self-closing tags
    cleaned = text
    for tag in tags_to_remove:
        # Remove self-closing tags
        cleaned = cleaned.replace(f'<{tag}/>', '')
        # Remove tags with attributes like <w s="H7225"> and </w>
        cleaned = re.sub(rf'<{tag}[^>]*>', '', cleaned)
        cleaned = re.sub(rf'</{tag}>', '', cleaned)

    # Clean up extra whitespace
    cleaned = ' '.join(cleaned.split())

    return cleaned.strip()

TEXT_BLOCK_TAGS = {
    "p", "q", "q1", "q2", "q3", "q4",
    "m", "mi",
    "li", "li1", "li2", "li3", "li4",
    "s", "s1", "s2", "s3",
    "sp", "d", "cl", "cls"
}

VERSE_SPLIT_RE = re.compile(r'<v[^>]*id="(\d+)"[^>]*\/?>')


def _strip_outer_tag(xml: str) -> str:
    xml = re.sub(r'^<[^>]+>', '', xml)
    xml = re.sub(r'</[^>]+>$', '', xml)
    return xml


def parse_usfx_book(book_element) -> Optional[Dict[str, Any]]:
    """
    Parse a single <book> element from USFX XML into TTH2-compatible JSON structure.

    Args:
        book_element: XML element for a book

    Returns:
        Dictionary with book_info and chapters, or None if parsing fails
    """
    book_id = book_element.get('id')
    if not book_id:
        logger.warning("Book element missing 'id' attribute")
        return None

    # Map USFX code to English name
    english_name = USFX_TO_ENGLISH.get(book_id)
    if not english_name:
        logger.warning(f"Unknown USFX book code: {book_id}")
        return None

    # Get book metadata
    metadata = get_book_metadata(english_name)
    if not metadata:
        logger.warning(f"No metadata found for book: {english_name}")
        return None

    logger.info(f"Parsing book: {english_name} (USFX: {book_id})")

    chapters = []
    current_chapter_num = None
    verses_in_chapter = []
    current_verse_num = None
    current_verse_parts: List[str] = []

    def flush_current_verse() -> None:
        nonlocal current_verse_num, current_verse_parts, verses_in_chapter
        if current_verse_num is None:
            return

        cleaned_text = clean_verse_text("".join(current_verse_parts))
        if cleaned_text:
            verses_in_chapter.append({
                "verse": current_verse_num,
                "bes": cleaned_text,
                "footnotes": []
            })

        current_verse_num = None
        current_verse_parts = []

    # Process all elements in the book (recursive search)
    for elem in book_element.iter():
        tag = elem.tag

        if tag == 'c':  # Chapter marker
            flush_current_verse()

            if current_chapter_num is not None and verses_in_chapter:
                chapters.append({
                    "chapter": current_chapter_num,
                    "verses": verses_in_chapter
                })

            chapter_num = elem.get('id')
            if chapter_num:
                try:
                    current_chapter_num = int(chapter_num)
                    verses_in_chapter = []
                except (ValueError, TypeError):
                    logger.warning(f"Invalid chapter number: {chapter_num} in {english_name}")
                    current_chapter_num = None
            else:
                current_chapter_num = None

        elif tag in TEXT_BLOCK_TAGS and current_chapter_num is not None:
            raw_xml = ET.tostring(elem, encoding='unicode', method='xml')
            inner_xml = _strip_outer_tag(raw_xml)

            if '<v' in inner_xml:
                parts = VERSE_SPLIT_RE.split(inner_xml)
                for idx in range(1, len(parts), 2):
                    verse_num = parts[idx]
                    verse_text = parts[idx + 1] if idx + 1 < len(parts) else ""

                    try:
                        verse_int = int(verse_num)
                    except (ValueError, TypeError):
                        logger.warning(
                            f"Invalid verse number: {verse_num} in {english_name} chapter {current_chapter_num}"
                        )
                        continue

                    flush_current_verse()
                    current_verse_num = verse_int
                    current_verse_parts = [verse_text]
            else:
                if current_verse_num is not None:
                    current_verse_parts.append(inner_xml)

    # Don't forget the last verse and chapter
    flush_current_verse()
    if current_chapter_num is not None and verses_in_chapter:
        chapters.append({
            "chapter": current_chapter_num,
            "verses": verses_in_chapter
        })

    # Count total verses
    total_verses = sum(len(chapter["verses"]) for chapter in chapters)

    # Build the final structure
    book_data = {
        "book_info": {
            "book_id": english_name.lower().replace('songofsolomon', 'songofsolomon'),  # Keep consistent with existing
            "tth_name": metadata["spanish_name"],  # Use Spanish name as display name
            "hebrew_name": metadata["hebrew_name"],
            "english_name": english_name,
            "spanish_name": metadata["spanish_name"],
            "section": metadata["section"],
            "total_chapters": len(chapters),  # Use actual chapters parsed
            "total_verses": total_verses
        },
        "chapters": chapters
    }

    return book_data

def parse_usfx_file() -> bool:
    """
    Parse the entire BES USFX XML file and generate JSON files for all books.

    Returns:
        True if successful, False otherwise
    """
    if not INPUT_XML.exists():
        logger.error(f"Input XML file not found: {INPUT_XML}")
        return False

    try:
        logger.info(f"Parsing USFX file: {INPUT_XML}")
        tree = ET.parse(INPUT_XML)
        root = tree.getroot()

        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        books_processed = 0

        # Find all book elements
        for book_elem in root.findall('.//book'):
            book_data = parse_usfx_book(book_elem)
            if book_data:
                book_id = book_data["book_info"]["book_id"]
                output_file = OUTPUT_DIR / f"{book_id}.json"

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(book_data, f, ensure_ascii=False, indent=2)

                books_processed += 1
                logger.info(f"Generated JSON for {book_id}")

        logger.info(f"Successfully processed {books_processed} books")
        return books_processed > 0

    except ET.ParseError as e:
        logger.error(f"XML parsing error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error parsing USFX: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = parse_usfx_file()
    exit(0 if success else 1)