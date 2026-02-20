#!/usr/bin/env python3
"""
Script to merge Strong's numbers from v2 analysis files into the original verse data.

This script reads the v2 JSON files (which contain successful strong number assignments)
and updates the original verse data files with those strong numbers.

Usage:
    python scripts/delitzsch/strongs/v2/merge_strongs.py [--book BOOK_NAME] [--dry-run]
"""

import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths - use absolute path from the project root
# File: scripts/delitzsch/strongs/v2/merge_strongs.py
# parent chain: v2 -> strongs -> delitzsch -> scripts -> project_root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PARSED_DIR = DATA_DIR / "delitzsch_parsed"
V2_DIR = PARSED_DIR / "strongs" / "v2"

# All 27 NT books
ALL_BOOKS = [
    'matthew', 'mark', 'luke', 'john', 'acts',
    'romans', 'corinthians1', 'corinthians2', 'galatians',
    'ephesians', 'philippians', 'colossians', 'thessalonians1',
    'thessalonians2', 'timothy1', 'timothy2', 'titus',
    'philemon', 'hebrews', 'james', 'peter1', 'peter2',
    'john1', 'john2', 'john3', 'jude', 'revelation'
]


def load_v2_strongs(book_name: str) -> Optional[Dict[str, Any]]:
    """Load the v2 strongs file for a book."""
    v2_file = V2_DIR / f"{book_name}.json"
    if not v2_file.exists():
        logger.warning(f"V2 file not found: {v2_file}")
        return None
    
    with open(v2_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_assignment_map(v2_data: Dict[str, Any]) -> Dict[int, Dict[int, Dict[str, Any]]]:
    """
    Create a mapping from chapter -> word_index -> strong number assignment.
    
    Returns:
        {chapter_number: {word_index: {'strong': 'H1234', 'text': 'word', 'prefixes': [...]}}}
    """
    assignment_map: Dict[int, Dict[int, Dict[str, Any]]] = {}
    
    for chapter_data in v2_data.get('chapters', []):
        chapter_num = chapter_data['chapter']
        assignment_map[chapter_num] = {}
        
        for assignment in chapter_data.get('assignments', []):
            # Only process successful assignments (type: "strong")
            if assignment.get('type') == 'strong' and assignment.get('strong'):
                word_idx = assignment['word_index']
                assignment_map[chapter_num][word_idx] = {
                    'strong': assignment['strong'],
                    'text': assignment.get('text', ''),
                    'prefixes': assignment.get('prefixes', []),
                    'reason': assignment.get('reason', '')
                }
    
    return assignment_map


def merge_strongs_for_book(book_name: str, dry_run: bool = False) -> Dict[str, int]:
    """
    Merge strong numbers from v2 file into verse data for a single book.
    
    Returns:
        Statistics dict with counts of updated, skipped, failed
    """
    stats = {
        'updated': 0,
        'skipped': 0,
        'failed': 0,
        'chapters_processed': 0,
        'books_processed': 1
    }
    
    # Load v2 strongs
    v2_data = load_v2_strongs(book_name)
    if not v2_data:
        stats['failed'] = 1
        return stats
    
    logger.info(f"Processing book: {book_name}")
    logger.info(f"  Total assigned: {v2_data.get('total_assigned', 0)}")
    logger.info(f"  Total failed: {v2_data.get('total_failed', 0)}")
    
    # Create assignment map
    assignment_map = create_assignment_map(v2_data)
    logger.info(f"  Chapters with assignments: {len(assignment_map)}")
    
    # Process each chapter
    book_dir = PARSED_DIR / book_name
    if not book_dir.exists():
        logger.error(f"Book directory not found: {book_dir}")
        stats['failed'] = 1
        return stats
    
    for chapter_file in sorted(book_dir.glob("*.json")):
        chapter_num = int(chapter_file.stem)
        
        if chapter_num not in assignment_map:
            stats['skipped'] += 1
            continue
        
        # Load chapter data
        with open(chapter_file, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        # Get the verses (handle both list and dict formats)
        if isinstance(chapter_data, list) and len(chapter_data) > 0:
            verses = chapter_data[0].get('verses', [])
        else:
            verses = chapter_data.get('verses', [])
        
        # Get assignments for this chapter
        chapter_assignments = assignment_map[chapter_num]
        
        # Track which verses were modified
        verses_modified = 0
        words_updated = 0
        
        for verse_data in verses:
            verse_num = verse_data.get('verse', 0)
            words = verse_data.get('words', [])
            
            verse_updated = False
            for word_idx, word in enumerate(words):
                if word_idx in chapter_assignments:
                    assignment = chapter_assignments[word_idx]
                    
                    # Only update if current strong is null
                    if word.get('strong') is None:
                        word['strong'] = assignment['strong']
                        words_updated += 1
                        verse_updated = True
                        logger.debug(f"    Verse {verse_num}, word {word_idx}: '{assignment['text']}' -> {assignment['strong']}")
            
            if verse_updated:
                verses_modified += 1
        
        stats['chapters_processed'] += 1
        
        if not dry_run:
            # Save updated chapter data
            with open(chapter_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  Chapter {chapter_num}: {words_updated} words updated in {verses_modified} verses")
        stats['updated'] += words_updated
    
    logger.info(f"  Book complete: {stats['updated']} words updated, {stats['chapters_processed']} chapters processed")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Merge Strong's numbers from v2 analysis into verse data"
    )
    parser.add_argument(
        '--book', 
        type=str, 
        help='Specific book to process (e.g., colossians). If not provided, processes all books.'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be updated without making changes'
    )
    
    args = parser.parse_args()
    
    books_to_process = [args.book] if args.book else ALL_BOOKS
    
    total_stats = {
        'updated': 0,
        'skipped': 0,
        'failed': 0,
        'chapters_processed': 0,
        'books_processed': 0
    }
    
    for book in books_to_process:
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing: {book}")
        logger.info(f"{'='*50}")
        
        if args.dry_run:
            logger.info("  [DRY RUN - No changes will be made]")
        
        stats = merge_strongs_for_book(book, dry_run=args.dry_run)
        
        for key in total_stats:
            total_stats[key] += stats[key]
        
        if stats['failed'] > 0:
            logger.error(f"  Failed to process {book}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"  Books processed: {total_stats['books_processed']}")
    logger.info(f"  Chapters processed: {total_stats['chapters_processed']}")
    logger.info(f"  Words updated: {total_stats['updated']}")
    logger.info(f"  Skipped (no v2 data): {total_stats['skipped']}")
    logger.info(f"  Failed: {total_stats['failed']}")
    
    if args.dry_run:
        logger.info("\n  [DRY RUN COMPLETE - No files were modified]")
    else:
        logger.info("\n  Merge complete!")


if __name__ == '__main__':
    main()
