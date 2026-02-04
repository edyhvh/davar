#!/usr/bin/env python3
"""
Translate only the fixed homonym words to avoid re-translating entire lexicon.

Uses the affected_words.json list to translate only the 254 words that were
fixed in the homonym correction process.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from translation.processor import LexiconProcessor

DATA_DIR = SCRIPT_DIR.parent.parent / "data" / "dict"
AFFECTED_WORDS_PATH = DATA_DIR / "affected_words.json"


def main():
    """Translate only the fixed homonym words."""
    print("🌍 Translating Fixed Homonym Words to Spanish\n")
    
    # Load affected words
    if not AFFECTED_WORDS_PATH.exists():
        print(f"❌ Error: {AFFECTED_WORDS_PATH} not found!")
        print("   Please run diagnose_homonyms.py first.")
        sys.exit(1)
    
    with open(AFFECTED_WORDS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    affected_words = data.get('affected_words', {})
    strong_numbers = list(affected_words.keys())
    
    print(f"📋 Found {len(strong_numbers)} words to translate\n")
    
    # Initialize translator
    try:
        processor = LexiconProcessor(target_lang='es', batch_size=50)
    except Exception as e:
        print(f"❌ Failed to initialize translator: {e}")
        sys.exit(1)
    
    # Translate each word
    total_translated = 0
    roots_count = 0
    words_count = 0
    
    for i, strong_number in enumerate(strong_numbers, 1):
        print(f"[{i}/{len(strong_numbers)}] Translating {strong_number}...", end=' ')
        
        try:
            # Try roots first
            stats_roots = processor.process_roots(strong_number, dry_run=False)
            if stats_roots['entries_processed'] > 0:
                roots_count += 1
                total_translated += stats_roots['definitions_translated']
                print(f"✅ ({stats_roots['definitions_translated']} definitions)")
                continue
            
            # Try words
            stats_words = processor.process_words(strong_number, dry_run=False)
            if stats_words['entries_processed'] > 0:
                words_count += 1
                total_translated += stats_words['definitions_translated']
                print(f"✅ ({stats_words['definitions_translated']} definitions)")
                continue
            
            print("⚠️  Not found")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("Translation Summary")
    print("="*60)
    print(f"Total words processed: {roots_count + words_count}")
    print(f"  Roots: {roots_count}")
    print(f"  Words: {words_count}")
    print(f"Total definitions translated: {total_translated}")
    print("="*60)
    
    # Rebuild consolidated files
    print("\n🔄 Rebuilding consolidated files...")
    from subprocess import run
    result = run(
        ['python3', str(SCRIPT_DIR / 'rebuild_lexicon_consolidated.py')],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Consolidated files updated")
        print(result.stdout)
    else:
        print("⚠️  Warning: Failed to rebuild consolidated files")
        print(result.stderr)
    
    print("\n✅ Translation complete!")
    print("\n💡 Next steps:")
    print("   1. Verify translations in data/dict/lexicon/roots/H1254.json")
    print("   2. Check consolidated files: roots.json and words.json")
    print("   3. Restart backend to load updated translations")


if __name__ == "__main__":
    main()
