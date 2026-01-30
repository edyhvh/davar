"""
Loader for DSSI book differences.

Reads all book JSON files and extracts differences into a flat list.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .config import DSSI_DIR

logger = logging.getLogger(__name__)


def load_all_differences() -> List[Dict]:
    """
    Load all DSS differences from DSSI book files.
    
    Each difference is enriched with book/chapter/verse context for
    later writing back to the source files.
    
    Returns:
        List of difference dictionaries with metadata:
        [
            {
                "book": "Genesis",
                "book_file": "genesis.json",
                "chapter": "1",
                "verse": "9",
                "position": 3,
                "masoretic_word": "יִקָּו֨וּ",
                "dss_word": "יקוו",
                "commentary": "4QGenb, Mas, LXX: be gathered...",
                "masoretic_text": "full verse Hebrew",
                "dss_text": "full verse DSS Hebrew"
            },
            ...
        ]
    """
    all_differences = []
    
    if not DSSI_DIR.exists():
        logger.error(f"DSSI directory not found: {DSSI_DIR}")
        return []
    
    book_files = sorted(DSSI_DIR.glob('*.json'))
    logger.info(f"Found {len(book_files)} book files in {DSSI_DIR}")
    
    for book_file in book_files:
        try:
            with open(book_file, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            book_name = book_data.get('name', book_file.stem)
            chapters = book_data.get('chapters', {})
            
            diff_count = 0
            for chapter_num, chapter_data in chapters.items():
                verses = chapter_data.get('verses', {})
                
                for verse_num, verse_data in verses.items():
                    differences = verse_data.get('differences', [])
                    
                    for diff in differences:
                        # Enrich with metadata
                        enriched_diff = {
                            'book': book_name,
                            'book_file': book_file.name,
                            'chapter': chapter_num,
                            'verse': verse_num,
                            'position': diff.get('position'),
                            'masoretic_word': diff.get('masoretic_word'),
                            'dss_word': diff.get('dss_word'),
                            'commentary': diff.get('commentary'),
                            'masoretic_text': verse_data.get('masoretic_text', ''),
                            'dss_text': verse_data.get('dss_text', ''),
                        }
                        all_differences.append(enriched_diff)
                        diff_count += 1
            
            logger.info(f"Loaded {diff_count} differences from {book_name}")
            
        except Exception as e:
            logger.error(f"Error loading {book_file.name}: {e}")
            continue
    
    logger.info(f"Total differences loaded: {len(all_differences)}")
    return all_differences


def load_differences_for_book(book: str) -> List[Dict]:
    """
    Load DSS differences for a single book.

    Args:
        book: Book identifier (file stem, file name, or book name in JSON)

    Returns:
        List of difference dictionaries for the requested book
    """
    if not DSSI_DIR.exists():
        logger.error(f"DSSI directory not found: {DSSI_DIR}")
        return []

    book_key = book.strip().lower()
    if not book_key:
        logger.error("Book identifier is empty")
        return []

    candidates = sorted(DSSI_DIR.glob('*.json'))
    matched_file: Optional[Path] = None

    for book_file in candidates:
        stem = book_file.stem.lower()
        if book_key == stem or book_key == book_file.name.lower():
            matched_file = book_file
            break

    if matched_file is None:
        for book_file in candidates:
            try:
                with open(book_file, 'r', encoding='utf-8') as f:
                    book_data = json.load(f)
                book_name = str(book_data.get('name', '')).strip().lower()
                if book_name and book_name == book_key:
                    matched_file = book_file
                    break
            except Exception as e:
                logger.debug(f"Skipping {book_file.name} while matching book name: {e}")

    if matched_file is None:
        logger.error(f"No book file found for '{book}'. Expected a file stem or book name.")
        return []

    try:
        with open(matched_file, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading {matched_file.name}: {e}")
        return []

    book_name = book_data.get('name', matched_file.stem)
    chapters = book_data.get('chapters', {})
    differences = []
    diff_count = 0

    for chapter_num, chapter_data in chapters.items():
        verses = chapter_data.get('verses', {})
        for verse_num, verse_data in verses.items():
            verse_differences = verse_data.get('differences', [])
            for diff in verse_differences:
                differences.append({
                    'book': book_name,
                    'book_file': matched_file.name,
                    'chapter': chapter_num,
                    'verse': verse_num,
                    'position': diff.get('position'),
                    'masoretic_word': diff.get('masoretic_word'),
                    'dss_word': diff.get('dss_word'),
                    'commentary': diff.get('commentary'),
                    'masoretic_text': verse_data.get('masoretic_text', ''),
                    'dss_text': verse_data.get('dss_text', ''),
                })
                diff_count += 1

    logger.info(f"Loaded {diff_count} differences from {book_name}")
    return differences


def load_sample_differences(count: int = 5) -> List[Dict]:
    """
    Load a sample of differences for testing.
    
    Args:
        count: Number of sample differences to load
        
    Returns:
        List of sample difference dictionaries
    """
    all_diffs = load_all_differences()
    return all_diffs[:count]
