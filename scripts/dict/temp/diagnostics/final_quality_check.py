#!/usr/bin/env python3
"""Final translation quality check."""

import json
from pathlib import Path


def main():
    print('🔍 Final Translation Quality Check\n')
    print('=' * 60)
    
    # Load files
    with open('data/dict/lexicon/roots.json') as f:
        roots = json.load(f)
    with open('data/dict/lexicon/words.json') as f:
        words = json.load(f)
    
    # Check H1254 (the original issue)
    print('\n1. ✅ H1254 (ברא - bara - "create"):')
    h1254 = roots['H1254']
    for i, d in enumerate(h1254['definitions']):
        print(f'   {i+1}. EN: "{d["text_en"]}"')
        print(f'      ES: "{d.get("text_es", "MISSING")}"')
    
    # Check some fixed entries
    print('\n2. ✅ Recently Fixed Entries:')
    test_cases = [
        ('H3667', words, 0),  # Canaan
        ('H450', words, 0),   # God knows  
        ('H6718', words, 0),  # hunting
    ]
    
    for strong, source, idx in test_cases:
        entry = source[strong]
        defn = entry['definitions'][idx]
        print(f'   {strong}: "{defn["text_en"]}" → "{defn.get("text_es", "MISSING")}"')
    
    # Count total translations
    print('\n3. ✅ Translation Coverage:')
    total_defs_roots = sum(len(e['definitions']) for e in roots.values())
    spanish_defs_roots = sum(
        sum(1 for d in e['definitions'] if d.get('text_es', '').strip())
        for e in roots.values()
    )
    
    total_defs_words = sum(len(e['definitions']) for e in words.values())
    spanish_defs_words = sum(
        sum(1 for d in e['definitions'] if d.get('text_es', '').strip())
        for e in words.values()
    )
    
    print(f'   Roots: {spanish_defs_roots}/{total_defs_roots} definitions')
    print(f'   Words: {spanish_defs_words}/{total_defs_words} definitions')
    print(f'   Total: {spanish_defs_roots + spanish_defs_words}/{total_defs_roots + total_defs_words} definitions')
    
    coverage_pct = (spanish_defs_roots + spanish_defs_words) / (total_defs_roots + total_defs_words) * 100
    print(f'   Coverage: {coverage_pct:.1f}%')
    
    print('\n' + '=' * 60)
    if coverage_pct == 100.0:
        print('✅ ALL TRANSLATIONS COMPLETE!')
    else:
        print(f'⚠️  {100 - coverage_pct:.1f}% of definitions still missing Spanish')


if __name__ == '__main__':
    main()
