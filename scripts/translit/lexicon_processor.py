"""
Process lexicon root entries for transliteration.

Adds translit_en and translit_es fields to individual root JSON files
using the same LocalTransliterator rules as verse-level transliteration.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from .config import LEXICON_ROOTS_DIR, OUTPUT_DIR
from .local_translit import LocalTransliterator
from .models import TransliterationStats

logger = logging.getLogger(__name__)


def transliterate_roots(
    dry_run: bool = False,
    strong_number: Optional[str] = None,
    verbose: bool = False
) -> TransliterationStats:
    """
    Add translit_en and translit_es to root entries.
    
    Args:
        dry_run: If True, don't write files
        strong_number: Process only this Strong's number (e.g., "H1")
        verbose: Enable verbose logging
        
    Returns:
        TransliterationStats with processing results
    """
    transliterator = LocalTransliterator()
    
    if not LEXICON_ROOTS_DIR.exists():
        raise FileNotFoundError(f"Roots directory not found: {LEXICON_ROOTS_DIR}")
    
    # Determine which files to process
    if strong_number:
        root_files = [LEXICON_ROOTS_DIR / f"{strong_number}.json"]
        if not root_files[0].exists():
            raise FileNotFoundError(f"Root file not found: {root_files[0]}")
    else:
        root_files = sorted(LEXICON_ROOTS_DIR.glob("H*.json"))
    
    logger.info(f"Processing {len(root_files)} root files...")
    
    stats = TransliterationStats(
        book_id="lexicon_roots",
        words=0,
        batches=1,
        input_tokens=0,
        output_tokens=0
    )
    
    processed = 0
    skipped_already_done = 0
    skipped_no_lemma = 0
    
    for root_file in root_files:
        try:
            # Load complete entry
            with open(root_file, 'r', encoding='utf-8') as f:
                entry = json.load(f)
            
            # Skip if already has transliteration
            if "translit_en" in entry and "translit_es" in entry:
                skipped_already_done += 1
                if verbose:
                    logger.debug(f"Skipping {root_file.stem}: already has transliteration")
                continue
            
            # Get lemma to transliterate
            lemma = entry.get("lemma")
            if not lemma:
                skipped_no_lemma += 1
                logger.warning(f"Skipping {root_file.stem}: no lemma field")
                continue
            
            # Transliterate
            result = transliterator.transliterate_word(lemma)
            
            # Add ONLY new fields (preserves all existing fields)
            entry["translit_en"] = result.translit_en
            entry["translit_es"] = result.translit_es
            
            # Save back
            if not dry_run:
                with open(root_file, 'w', encoding='utf-8') as f:
                    json.dump(entry, f, ensure_ascii=False, indent=2)
            
            processed += 1
            
            if verbose:
                logger.debug(
                    f"{root_file.stem}: {lemma} → "
                    f"EN: {result.translit_en}, ES: {result.translit_es}"
                )
        
        except Exception as e:
            logger.error(f"Error processing {root_file}: {e}")
            continue
    
    # Update stats
    stats.words = processed
    
    logger.info(f"✅ Processed: {processed}")
    logger.info(f"⏭️  Skipped (already done): {skipped_already_done}")
    if skipped_no_lemma > 0:
        logger.warning(f"⚠️  Skipped (no lemma): {skipped_no_lemma}")
    
    return stats


def estimate_roots_cost() -> float:
    """
    Estimate the cost of transliterating all roots.
    
    Since this uses local rules (not API), cost is always $0.00.
    
    Returns:
        Cost estimate (always 0.0)
    """
    return 0.0
