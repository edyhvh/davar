#!/usr/bin/env python3
"""Check for empty Spanish translations after API mismatches."""

import json
from pathlib import Path

def check_empty_translations():
    print('🔍 Checking for empty Spanish translations...\n')
    
    # Check roots.json
    roots_path = Path('data/dict/lexicon/roots.json')
    with open(roots_path) as f:
        roots = json.load(f)
    
    empty_es_roots = []
    for strong, entry in roots.items():
        for i, defn in enumerate(entry.get('definitions', [])):
            text_es = defn.get('text_es', '').strip()
            if not text_es:
                empty_es_roots.append((strong, i, defn.get('text_en', 'N/A')))
    
    print(f'📦 roots.json: {len(empty_es_roots)} empty Spanish translations')
    if empty_es_roots:
        print('   First 5 examples:')
        for strong, idx, text_en in empty_es_roots[:5]:
            preview = text_en[:60] if len(text_en) > 60 else text_en
            print(f'   - {strong} def[{idx}]: "{preview}"')
    
    # Check words.json
    words_path = Path('data/dict/lexicon/words.json')
    with open(words_path) as f:
        words = json.load(f)
    
    empty_es_words = []
    for strong, entry in words.items():
        for i, defn in enumerate(entry.get('definitions', [])):
            text_es = defn.get('text_es', '').strip()
            if not text_es:
                empty_es_words.append((strong, i, defn.get('text_en', 'N/A')))
    
    print(f'\n📦 words.json: {len(empty_es_words)} empty Spanish translations')
    if empty_es_words:
        print('   First 10 examples:')
        for strong, idx, text_en in empty_es_words[:10]:
            preview = text_en[:60] if len(text_en) > 60 else text_en
            print(f'   - {strong} def[{idx}]: "{preview}"')
    
    total_empty = len(empty_es_roots) + len(empty_es_words)
    print(f'\n📊 Total empty translations: {total_empty}')
    
    if total_empty == 0:
        print('✅ No empty translations found!')
        return 0
    else:
        print(f'⚠️  Found {total_empty} definitions without Spanish translations')
        
        # Save list for potential re-translation
        if empty_es_words:
            save_path = Path('data/dict/empty_translations.json')
            with open(save_path, 'w') as f:
                json.dump({
                    'roots': empty_es_roots,
                    'words': empty_es_words
                }, f, indent=2)
            print(f'\n💾 Saved list to: {save_path}')
        
        return total_empty

if __name__ == '__main__':
    check_empty_translations()
