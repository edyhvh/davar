#!/usr/bin/env python3
"""
Validate root_ref integrity between words.json and roots.json.
"""

import json
from pathlib import Path


def main() -> None:
    words_path = Path(__file__).parent.parent.parent / 'data' / 'dict' / 'lexicon' / 'words.json'
    roots_path = Path(__file__).parent.parent.parent / 'data' / 'dict' / 'lexicon' / 'roots.json'

    words = json.loads(words_path.read_text(encoding='utf-8'))
    roots = json.loads(roots_path.read_text(encoding='utf-8'))

    root_ref_to_word = []
    missing_roots = []

    for sn, entry in words.items():
        root_ref = entry.get('root_ref')
        if not root_ref:
            continue

        if root_ref not in roots:
            if root_ref in words:
                root_ref_to_word.append({
                    'word': sn,
                    'root_ref': root_ref,
                    'ref_is_root': words[root_ref].get('is_root', False)
                })
            else:
                missing_roots.append({'word': sn, 'root_ref': root_ref})

    print(f"Words with root_ref pointing to other words (not in roots.json): {len(root_ref_to_word)}")
    print(f"Words with root_ref missing entirely: {len(missing_roots)}")

    if root_ref_to_word:
        print("\nSample root_ref to words:")
        for item in root_ref_to_word[:10]:
            print(f"  {item['word']} -> {item['root_ref']} (is_root={item['ref_is_root']})")

    if missing_roots:
        print("\nSample missing roots:")
        for item in missing_roots[:10]:
            print(f"  {item['word']} -> {item['root_ref']} (not found)")


if __name__ == '__main__':
    main()
