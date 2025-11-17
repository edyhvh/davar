#!/usr/bin/env python3
"""
Test regex patterns for footnotes
"""

import re

# Test string from the output
test_string = 'y abrirás brecha[\\[125\\]](#footnote-125) hacia el mar, hacia el este, y el norte, y el sur,'

print("Test string:")
print(repr(test_string))

# Test different regex patterns
patterns = [
    r'\[\[(\d+)\]\]\(#footnote-\d+\)',
    r'\[\\\[(\d+)\\\]\]\(#footnote-\d+\)',
    r'\[\[(\d+)\]\]',
    r'\[.*?\]\(.*?\)',
]

for pattern in patterns:
    matches = re.findall(pattern, test_string)
    print(f"Pattern '{pattern}': {matches}")













