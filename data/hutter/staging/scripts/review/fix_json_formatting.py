#!/usr/bin/env python3
"""
Fix the formatting of nikud_review_verses_fixed.json by removing excessive whitespace.
"""

import json
from pathlib import Path


def fix_json_formatting():
    """Read the malformed JSON and write it back with proper formatting."""
    input_path = Path(__file__).parents[2] / 'data' / 'review' / 'nikud_review_verses_fixed.json'

    # Read the current file
    with open(input_path, 'r', encoding='utf-8') as f:
        # The file has extra whitespace, but json.load should still work
        data = json.load(f)

    # Write back with proper formatting
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Fixed formatting for {input_path}")
    print(f"File now contains {len(data)} verses")


if __name__ == '__main__':
    fix_json_formatting()