#!/usr/bin/env python3
"""
Basic test script for Delitzsch Strong's Matcher
"""

import sys
import os

# Add the scripts directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from hebrew_utils import strip_nikud, tokenize_verse, normalize_for_matching
from dictionary_loader import get_dictionary_loader
from matcher import HebrewMatcher


def test_hebrew_utils():
    """Test Hebrew utility functions"""
    print("Testing Hebrew utilities...")

    # Test nikud stripping
    text_with_nikud = "בְּמַּאֲמָר"
    stripped = strip_nikud(text_with_nikud)
    print(f"Original: {text_with_nikud}")
    print(f"Stripped: {stripped}")
    assert stripped == "במאמר"

    # Test tokenization
    verse = "בְּמַּאֲמָר הָרִאשׁוֹן כָּתַבְתִּי"
    tokens = tokenize_verse(verse)
    print(f"Verse: {verse}")
    print(f"Tokens: {tokens}")
    assert len(tokens) == 3

    # Test normalization
    normalized = normalize_for_matching(text_with_nikud)
    print(f"Normalized: {normalized}")

    print("✓ Hebrew utilities tests passed\n")


def test_dictionary_loading():
    """Test dictionary loading"""
    print("Testing dictionary loading...")

    loader = get_dictionary_loader()
    assert loader.is_loaded()

    # Test a known word
    strong = loader.get_strong_number("אמר")  # Should find H561 or similar
    print(f"Strong for 'אמר': {strong}")

    # Test prefixes
    prefixes = loader.get_prefixes_for_form("בְּ")
    print(f"Prefixes for 'בְּ': {prefixes}")

    print("✓ Dictionary loading tests passed\n")


def test_matcher():
    """Test word matching"""
    print("Testing matcher...")

    matcher = HebrewMatcher()

    # Test a simple word
    word = "בְּמַּאֲמָר"
    result = matcher.process_word(word)
    print(f"Word: {word}")
    print(f"Result: {result}")
    assert 'text' in result
    assert 'strong' in result
    assert 'prefixes' in result

    # Test a verse
    verse = "בְּמַּאֲמָר הָרִאשׁוֹן"
    words = matcher.process_verse(verse)
    print(f"Verse: {verse}")
    print(f"Words: {words}")
    assert len(words) == 2

    print("✓ Matcher tests passed\n")


def main():
    """Run all tests"""
    print("Running Delitzsch Strong's Matcher tests...\n")

    try:
        test_hebrew_utils()
        test_dictionary_loading()
        test_matcher()

        print("🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())