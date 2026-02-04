#!/usr/bin/env python3
"""
Selective lexicon regeneration script to fix BDB homonym definition issues.

This script:
1. Reads affected_words.json for list of Strong's numbers to fix
2. Regenerates ONLY those affected entries using fixed extraction logic
3. Preserves existing translations (Spanish, etc.) in the JSON
4. Generates a detailed report of all changes

Author: Davar Project
Date: February 2026
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import from build_lexicon.py
from build_lexicon import (
    load_lexical_index,
    load_bdb_xml,
    load_strongs_data,
    load_strong_refs,
    build_lexicon_entry,
    NS
)
from config import config

# Paths
DATA_DIR = config.DICT_DIR
AFFECTED_WORDS_PATH = DATA_DIR / "affected_words.json"
REPORT_PATH = DATA_DIR / "homonym_fixes_report.md"

def load_affected_words() -> Dict:
    """Load the affected_words.json file from diagnostic."""
    print(f"📖 Loading affected words from {AFFECTED_WORDS_PATH}...")
    
    if not AFFECTED_WORDS_PATH.exists():
        print(f"❌ Error: {AFFECTED_WORDS_PATH} not found!")
        print("   Please run diagnose_homonyms.py first.")
        sys.exit(1)
    
    with open(AFFECTED_WORDS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    affected = data.get('affected_words', {})
    print(f"✅ Loaded {len(affected)} affected Strong's numbers")
    return affected

def load_existing_entry(strong_number: str) -> Optional[Dict]:
    """Load existing lexicon entry if it exists."""
    # Check roots directory first
    root_path = config.LEXICON_ROOTS_DIR / f"{strong_number}.json"
    if root_path.exists():
        with open(root_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Check words directory
    word_path = config.LEXICON_WORDS_DIR / f"{strong_number}.json"
    if word_path.exists():
        with open(word_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None

def regenerate_entry(
    strong_number: str,
    bdb_root: ET.Element
) -> Optional[Dict]:
    """Regenerate a single lexicon entry using fixed extraction logic."""
    
    # Get existing entry to preserve translations
    existing = load_existing_entry(strong_number)
    if not existing:
        print(f"   ⚠️  No existing entry found for {strong_number}, skipping...")
        return None
    
    # Use build_lexicon_entry to regenerate with FIXED logic
    new_entry = build_lexicon_entry(strong_number, bdb_root, update_existing=False, testing_mode=False)
    
    if not new_entry:
        print(f"   ⚠️  Failed to regenerate {strong_number}")
        return None
    
    # Preserve translations from existing entry
    for new_def in new_entry.get('definitions', []):
        # Find matching definition in existing entry
        for old_def in existing.get('definitions', []):
            if old_def.get('text_en') == new_def.get('text_en'):
                # Preserve Spanish and other translations
                if 'text_es' in old_def:
                    new_def['text_es'] = old_def['text_es']
                # Preserve any other language fields
                for key in old_def:
                    if key.startswith('text_') and key not in new_def:
                        new_def[key] = old_def[key]
                break
    
    return new_entry

def save_entry(strong_number: str, entry: Dict):
    """Save regenerated entry to appropriate directory."""
    is_root = entry.get('is_root', False)
    output_dir = config.LEXICON_ROOTS_DIR if is_root else config.LEXICON_WORDS_DIR
    output_path = output_dir / f"{strong_number}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
    
    return output_path

def compare_entries(old: Dict, new: Dict) -> Dict:
    """Compare old and new entries to generate change summary."""
    changes = {
        'added': [],
        'removed': [],
        'preserved': []
    }
    
    old_defs = {d['text_en'] for d in old.get('definitions', [])}
    new_defs = {d['text_en'] for d in new.get('definitions', [])}
    
    changes['added'] = list(new_defs - old_defs)
    changes['removed'] = list(old_defs - new_defs)
    changes['preserved'] = list(old_defs & new_defs)
    
    return changes

def generate_report(results: List[Dict]):
    """Generate detailed markdown report of all changes."""
    print(f"\n📝 Generating report at {REPORT_PATH}...")
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write("# BDB Homonym Definition Fixes - Report\n\n")
        f.write(f"**Generated**: February 2026\n\n")
        f.write(f"**Total Fixed**: {len(results)} words\n\n")
        f.write("---\n\n")
        
        # High-impact words section
        f.write("## High-Impact Words (Genesis 1-2, Key Passages)\n\n")
        priority_strongs = ['H1254', 'H352', 'H1481']  # bara, ayil, gur
        
        for result in results:
            if result['strong_number'] in priority_strongs:
                write_entry_report(f, result)
        
        f.write("\n---\n\n## All Fixed Words\n\n")
        
        # All words
        for result in results:
            if result['strong_number'] not in priority_strongs:
                write_entry_report(f, result)
    
    print(f"✅ Report saved to {REPORT_PATH}")

def write_entry_report(f, result: Dict):
    """Write a single entry's report."""
    strong = result['strong_number']
    lemma = result['lemma']
    changes = result['changes']
    occurrences = result.get('occurrences', 0)
    
    f.write(f"### {strong} - {lemma}\n\n")
    f.write(f"**Occurrences**: {occurrences}\n\n")
    
    if changes['removed']:
        f.write(f"**❌ Removed** (wrong homonym):\n")
        for def_text in changes['removed']:
            f.write(f"- {def_text}\n")
        f.write("\n")
    
    if changes['added']:
        f.write(f"**✅ Added** (correct primary sense):\n")
        for def_text in changes['added']:
            f.write(f"- {def_text}\n")
        f.write("\n")
    
    if changes['preserved']:
        f.write(f"**✓ Preserved**:\n")
        for def_text in changes['preserved']:
            f.write(f"- {def_text}\n")
        f.write("\n")
    
    f.write("---\n\n")

def main():
    """Main entry point for selective regeneration."""
    print("🔧 BDB Homonym Fixes - Selective Regeneration\n")
    
    # Load affected words
    affected_words = load_affected_words()
    
    # Load data sources
    print("\n📚 Loading data sources...")
    bdb_root = load_bdb_xml()
    if not bdb_root:
        print("❌ Error: Could not load BDB XML!")
        sys.exit(1)
    print("✅ Data sources loaded")
    
    # Process each affected word
    print(f"\n🔄 Regenerating {len(affected_words)} affected words...\n")
    results = []
    
    for i, (strong, details) in enumerate(affected_words.items(), 1):
        print(f"   [{i}/{len(affected_words)}] Processing {strong}...")
        
        # Load existing entry
        old_entry = load_existing_entry(strong)
        if not old_entry:
            print(f"      ⚠️  No existing entry found, skipping")
            continue
        
        # Regenerate with fixed logic
        new_entry = regenerate_entry(strong, bdb_root)
        if not new_entry:
            continue
        
        # Compare changes
        changes = compare_entries(old_entry, new_entry)
        
        # Save if there are actual changes
        if changes['added'] or changes['removed']:
            save_entry(strong, new_entry)
            print(f"      ✅ Saved (removed: {len(changes['removed'])}, added: {len(changes['added'])})")
            
            results.append({
                'strong_number': strong,
                'lemma': new_entry.get('lemma', ''),
                'changes': changes,
                'occurrences': new_entry.get('occurrences', {}).get('total', 0)
            })
        else:
            print(f"      ℹ️  No changes needed")
    
    # Generate report
    if results:
        generate_report(results)
    
    # Summary
    print(f"\n✅ Regeneration complete!")
    print(f"   Total processed: {len(affected_words)}")
    print(f"   Successfully fixed: {len(results)}")
    print(f"\n📊 Review the report at: {REPORT_PATH}")
    print(f"\n💡 Next steps:")
    print(f"   1. Review the report, especially high-impact words")
    print(f"   2. Check H1254 (ברא) in Genesis 1:1")
    print(f"   3. Run QA validation: python scripts/dict/qa.py")

if __name__ == "__main__":
    main()
