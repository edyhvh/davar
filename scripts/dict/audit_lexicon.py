#!/usr/bin/env python3
"""
Audit script to identify mismatches between raw Strong definitions and lexicon definitions.
This helps find homograph issues where the wrong BDB entry was selected.
"""

import json
import sys
from pathlib import Path

# Add the scripts directory to the path so we can import config
sys.path.insert(0, str(Path(__file__).parent))

from config import Config

def load_raw_strongs():
    """Load raw Strong's dictionary data."""
    config = Config()
    raw_strongs_path = config.RAW_DIR / 'strongs_hebrew_dict_en.json'

    with open(raw_strongs_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_lexicon_words():
    """Load lexicon words data."""
    config = Config()
    lexicon_words_path = config.LEXICON_DIR / 'words.json'

    with open(lexicon_words_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_text(text):
    """Normalize text for comparison by removing extra whitespace and punctuation."""
    if not text:
        return ""
    # Remove extra whitespace, convert to lowercase
    return ' '.join(text.lower().split())

def audit_definitions():
    """Audit definitions for mismatches."""
    raw_strongs = load_raw_strongs()
    lexicon_words = load_lexicon_words()

    mismatches = []
    total_checked = 0

    for strong_num, lexicon_entry in lexicon_words.items():
        if strong_num not in raw_strongs:
            continue

        total_checked += 1
        raw_entry = raw_strongs[strong_num]

        # Get raw definitions
        raw_defs = []
        if 'strongs_def' in raw_entry:
            raw_defs.append(raw_entry['strongs_def'])
        if 'kjv_def' in raw_entry:
            raw_defs.append(raw_entry['kjv_def'])

        # Get lexicon BDB definitions
        lexicon_bdb_defs = []
        if 'definitions' in lexicon_entry:
            for def_item in lexicon_entry['definitions']:
                if def_item.get('source') == 'bdb' and 'text_en' in def_item:
                    lexicon_bdb_defs.append(def_item['text_en'])

        # Check if any raw definition matches any lexicon BDB definition
        raw_normalized = [normalize_text(d) for d in raw_defs]
        lexicon_normalized = [normalize_text(d) for d in lexicon_bdb_defs]

        has_match = False
        for raw_def in raw_normalized:
            for lex_def in lexicon_normalized:
                # Check for substring match (lexicon might be more detailed)
                if raw_def in lex_def or lex_def in raw_def:
                    has_match = True
                    break
            if has_match:
                break

        if not has_match:
            mismatches.append({
                'strong_number': strong_num,
                'lemma': lexicon_entry.get('lemma', ''),
                'raw_strongs_def': raw_entry.get('strongs_def', ''),
                'raw_kjv_def': raw_entry.get('kjv_def', ''),
                'lexicon_bdb_defs': lexicon_bdb_defs[:3],  # First 3 for brevity
                'lexicon_bdb_count': len(lexicon_bdb_defs)
            })

    print(f"Total entries checked: {total_checked}")
    print(f"Mismatches found: {len(mismatches)}")

    if mismatches:
        print("\nMismatches:")
        for mismatch in mismatches[:10]:  # Show first 10
            print(f"\n{strong_num}: {mismatch['lemma']}")
            print(f"  Raw Strong: {mismatch['raw_strongs_def']}")
            print(f"  Raw KJV: {mismatch['raw_kjv_def']}")
            print(f"  Lexicon BDB ({mismatch['lexicon_bdb_count']} defs): {', '.join(mismatch['lexicon_bdb_defs'])}")

        # Save full results to file
        output_path = Path(__file__).parent / 'lexicon_audit_results.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mismatches, f, indent=2, ensure_ascii=False)
        print(f"\nFull results saved to: {output_path}")

    return mismatches

if __name__ == '__main__':
    audit_definitions()