#!/usr/bin/env python3
"""
Targeted audit for homograph issues: Find Strong numbers where multiple BDB entries
share the same lemma, and check if the selected BDB entry matches the Strong definition.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Add the scripts directory to the path so we can import config
sys.path.insert(0, str(Path(__file__).parent))

from config import Config

def load_raw_strongs():
    """Load raw Strong's dictionary data."""
    config = Config()
    raw_strongs_path = config.RAW_DIR / 'strongs_hebrew_dict_en.json'

    with open(raw_strongs_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_lexical_index():
    """Load the lexical index mapping Strong to BDB IDs."""
    config = Config()
    lexical_index_path = config.LEXICAL_INDEX

    import xml.etree.ElementTree as ET
    tree = ET.parse(lexical_index_path)
    root = tree.getroot()

    mapping = {}
    for entry in root.findall('.//entry'):
        strong = entry.get('strongs')
        bdb_id = entry.get('id')
        if strong and bdb_id:
            mapping[strong] = bdb_id

    return mapping

def load_bdb_entries():
    """Load BDB entries grouped by lemma."""
    config = Config()
    bdb_path = config.BDB_XML

    import xml.etree.ElementTree as ET
    tree = ET.parse(bdb_path)
    root = tree.getroot()

    lemma_to_entries = defaultdict(list)
    for entry in root.findall('.//entry'):
        lemma = entry.get('n')
        if lemma:
            lemma_to_entries[lemma].append(entry)

    return lemma_to_entries

def normalize_text(text):
    """Normalize text for comparison."""
    if not text:
        return ""
    return ' '.join(text.lower().split())

def audit_homographs():
    """Audit for homograph issues."""
    raw_strongs = load_raw_strongs()
    lexical_index = load_lexical_index()
    bdb_entries = load_bdb_entries()

    config = Config()
    lexicon_words_path = config.LEXICON_DIR / 'words.json'

    with open(lexicon_words_path, 'r', encoding='utf-8') as f:
        lexicon_words = json.load(f)

    potential_issues = []

    for strong_num, lexicon_entry in lexicon_words.items():
        if strong_num not in raw_strongs or strong_num not in lexical_index:
            continue

        raw_entry = raw_strongs[strong_num]
        bdb_id = lexical_index[strong_num]
        lemma = lexicon_entry.get('lemma', '')

        # Check if this lemma has multiple BDB entries (homographs)
        if lemma not in bdb_entries or len(bdb_entries[lemma]) <= 1:
            continue

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

        # Check if raw definition matches any lexicon BDB definition
        raw_normalized = [normalize_text(d) for d in raw_defs]
        lexicon_normalized = [normalize_text(d) for d in lexicon_bdb_defs]

        has_match = False
        for raw_def in raw_normalized:
            for lex_def in lexicon_normalized:
                if raw_def in lex_def or lex_def in raw_def:
                    has_match = True
                    break
            if has_match:
                break

        if not has_match:
            # Get all BDB entries for this lemma
            all_bdb_defs = []
            for entry in bdb_entries[lemma]:
                defs = entry.findall('.//def')
                for d in defs:
                    if d.text:
                        all_bdb_defs.append(d.text.strip())

            potential_issues.append({
                'strong_number': strong_num,
                'lemma': lemma,
                'bdb_id_selected': bdb_id,
                'homograph_count': len(bdb_entries[lemma]),
                'raw_strongs_def': raw_entry.get('strongs_def', ''),
                'raw_kjv_def': raw_entry.get('kjv_def', ''),
                'selected_bdb_defs': lexicon_bdb_defs,
                'all_bdb_defs_for_lemma': list(set(all_bdb_defs))  # Unique defs
            })

    print(f"Potential homograph issues found: {len(potential_issues)}")

    if potential_issues:
        print("\nIssues:")
        for issue in potential_issues[:5]:  # Show first 5
            print(f"\n{issue['strong_number']}: {issue['lemma']} (BDB ID: {issue['bdb_id_selected']})")
            print(f"  Homographs with same lemma: {issue['homograph_count']}")
            print(f"  Raw Strong: {issue['raw_strongs_def']}")
            print(f"  Selected BDB defs: {', '.join(issue['selected_bdb_defs'][:2])}")
            print(f"  All possible BDB defs for lemma: {', '.join(issue['all_bdb_defs_for_lemma'][:3])}")

        # Save results
        output_path = Path(__file__).parent / 'homograph_audit_results.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(potential_issues, f, indent=2, ensure_ascii=False)
        print(f"\nFull results saved to: {output_path}")

    return potential_issues

if __name__ == '__main__':
    audit_homographs()