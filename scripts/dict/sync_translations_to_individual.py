#!/usr/bin/env python3
"""
Sync translations from consolidated roots.json/words.json back to individual files.

This ensures that individual files in lexicon/roots/ and lexicon/words/ have
the same Spanish translations (text_es) as the consolidated files.

Use this before running transliteration or other operations that modify individual files.
"""

import json
import sys
from pathlib import Path
from typing import Dict

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from config import config


def sync_translations_to_individual_files(file_type: str = "both") -> None:
    """
    Sync translations from consolidated files to individual files.
    
    Args:
        file_type: "roots", "words", or "both"
    """
    if file_type in ("roots", "both"):
        print("📥 Syncing roots translations...")
        sync_file_type("roots")
    
    if file_type in ("words", "both"):
        print("📥 Syncing words translations...")
        sync_file_type("words")


def sync_file_type(file_type: str) -> None:
    """Sync translations for a specific file type."""
    # Load consolidated file
    consolidated_file = config.LEXICON_DIR / f"{file_type}.json"
    individual_dir = config.LEXICON_ROOTS_DIR if file_type == "roots" else config.LEXICON_WORDS_DIR
    
    if not consolidated_file.exists():
        print(f"❌ Consolidated file not found: {consolidated_file}")
        return
    
    print(f"   Loading {consolidated_file}...")
    with consolidated_file.open("r", encoding="utf-8") as f:
        consolidated_data = json.load(f)
    
    updated = 0
    skipped = 0
    errors = 0
    
    # Update each individual file
    for strong_number, consolidated_entry in consolidated_data.items():
        individual_file = individual_dir / f"{strong_number}.json"
        
        if not individual_file.exists():
            skipped += 1
            continue
        
        try:
            # Load individual file
            with individual_file.open("r", encoding="utf-8") as f:
                individual_entry = json.load(f)
            
            # Check if definitions need updating
            needs_update = False
            if "definitions" in consolidated_entry:
                # Sync definitions (including text_es)
                individual_entry["definitions"] = consolidated_entry["definitions"]
                needs_update = True
            
            # Sync other translation-related fields if present
            for field in ["root", "root_strong", "root_definitions"]:
                if field in consolidated_entry:
                    individual_entry[field] = consolidated_entry[field]
                    needs_update = True
            
            if needs_update:
                # Save back to individual file
                with individual_file.open("w", encoding="utf-8") as f:
                    json.dump(individual_entry, f, ensure_ascii=False, indent=2)
                updated += 1
        
        except Exception as e:
            print(f"   ❌ Error processing {strong_number}: {e}")
            errors += 1
    
    print(f"   ✅ Updated: {updated}")
    print(f"   ⏭️  Skipped (not found): {skipped}")
    if errors > 0:
        print(f"   ❌ Errors: {errors}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sync translations from consolidated to individual lexicon files"
    )
    parser.add_argument(
        "--file",
        choices=["roots", "words", "both"],
        default="both",
        help="Which files to sync (default: both)"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("SYNCING TRANSLATIONS TO INDIVIDUAL FILES")
    print("="*60)
    
    sync_translations_to_individual_files(args.file)
    
    print("="*60)
    print("✅ Sync complete!")
    print("="*60)


if __name__ == "__main__":
    main()
