"""
Writer for enhanced DSSI differences.

Updates book JSON files with enhanced commentaries and Strong's numbers.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .config import DSSI_DIR, METADATA_FILE, COMMENTARY_VERSION

logger = logging.getLogger(__name__)


def write_enhanced_differences(
    enhanced_differences: List[Dict],
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Write enhanced differences back to DSSI book files.
    
    Args:
        enhanced_differences: List of differences with added fields
        dry_run: If True, don't actually write files
        
    Returns:
        Statistics dict with counts per book
    """
    # Group by book file
    by_book = {}
    for diff in enhanced_differences:
        book_file = diff.get('book_file')
        if book_file:
            if book_file not in by_book:
                by_book[book_file] = []
            by_book[book_file].append(diff)
    
    stats = {'books_updated': 0, 'differences_updated': 0}
    
    for book_file, diffs in by_book.items():
        try:
            file_path = DSSI_DIR / book_file
            
            # Read original book data
            with open(file_path, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            # Update differences
            updated_count = 0
            for diff in diffs:
                chapter = diff.get('chapter')
                verse = diff.get('verse')
                position = diff.get('position')
                
                # Navigate to the difference in the nested structure
                if (chapter in book_data.get('chapters', {}) and
                    verse in book_data['chapters'][chapter].get('verses', {})):
                    
                    verse_data = book_data['chapters'][chapter]['verses'][verse]
                    differences = verse_data.get('differences', [])
                    
                    # Find matching difference by position
                    for i, existing_diff in enumerate(differences):
                        if existing_diff.get('position') == position:
                            # Preserve original commentary
                            if 'original_commentary' not in diff:
                                diff['original_commentary'] = existing_diff.get('commentary', '')
                            
                            # Update with enhanced fields
                            updated_diff = {
                                'position': position,
                                'masoretic_word': diff.get('masoretic_word'),
                                'dss_word': diff.get('dss_word'),
                                'masoretic_strong': diff.get('masoretic_strong', ''),
                                'dss_strong': diff.get('dss_strong', ''),
                                'original_commentary': diff.get('original_commentary', ''),
                                'commentary_en': diff.get('commentary_en', ''),
                                'commentary_es': diff.get('commentary_es', ''),
                                'commentary_he': diff.get('commentary_he', ''),
                                'commentary_version': COMMENTARY_VERSION,
                            }
                            
                            differences[i] = updated_diff
                            updated_count += 1
                            break
            
            # Write updated book data
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(book_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Updated {updated_count} differences in {book_file}")
            else:
                logger.info(f"[DRY RUN] Would update {updated_count} differences in {book_file}")
            
            stats['books_updated'] += 1
            stats['differences_updated'] += updated_count
            
        except Exception as e:
            logger.error(f"Error updating {book_file}: {e}")
            continue
    
    return stats


def update_metadata(
    total_processed: int,
    model_used: str,
    token_stats: Optional[Dict] = None,
    dry_run: bool = False
):
    """
    Update metadata.json with processing information.
    
    Args:
        total_processed: Total number of differences processed
        model_used: Model name used for generation
        token_stats: Optional token usage statistics
        dry_run: If True, don't actually write file
    """
    try:
        # Read existing metadata
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Add commentary generation section
        metadata['commentary_generation'] = {
            'timestamp': datetime.now().isoformat(),
            'model': model_used,
            'total_processed': total_processed,
            'commentary_version': COMMENTARY_VERSION,
        }
        
        if token_stats:
            metadata['commentary_generation']['token_stats'] = token_stats
        
        metadata['schema_version'] = '2.0'
        
        # Write updated metadata
        if not dry_run:
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            logger.info("Updated metadata.json with commentary generation info")
        else:
            logger.info("[DRY RUN] Would update metadata.json")
            
    except Exception as e:
        logger.error(f"Error updating metadata: {e}")


def write_sample_output(
    enhanced_differences: List[Dict],
    output_file: Path,
    count: int = 5
):
    """
    Write a sample of enhanced differences to a file for review.
    
    Args:
        enhanced_differences: List of enhanced differences
        output_file: Path to output file
        count: Number of samples to write
    """
    sample = enhanced_differences[:count]
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
        logger.info(f"Wrote {len(sample)} sample differences to {output_file}")
    except Exception as e:
        logger.error(f"Error writing sample output: {e}")
