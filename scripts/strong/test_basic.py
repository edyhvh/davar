#!/usr/bin/env python3
"""
Basic test script for Delitzsch Strong's Matcher
Tests the new modular architecture with separate components
"""

import sys
import os

# Add the scripts directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from hebrew_utils import strip_nikud, tokenize_verse, normalize_for_matching
from dictionary_loader import get_dictionary_loader
from prefix_detector import PrefixDetector
from result_formatter import ResultFormatter
from word_matcher import WordMatcher
from book_processor import BookProcessor


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


def test_prefix_detector():
    """Test prefix detection module"""
    print("Testing prefix detector...")

    loader = get_dictionary_loader()
    detector = PrefixDetector(loader)

    # Test conjunctive vav
    word = "וְאֵלֶּה"
    prefixes, stem = detector.identify_prefixes(word)
    print(f"Word: {word}")
    print(f"Prefixes: {prefixes}, Stem: {stem}")
    assert 'Hc' in prefixes  # Should detect ו

    # Test preposition ב
    word = "בְּמַּאֲמָר"
    prefixes, stem = detector.identify_prefixes(word)
    print(f"Word: {word}")
    print(f"Prefixes: {prefixes}, Stem: {stem}")
    assert 'Hb' in prefixes  # Should detect ב

    print("✓ Prefix detector tests passed\n")


def test_word_matcher():
    """Test word matching with new architecture"""
    print("Testing word matcher...")

    loader = get_dictionary_loader()
    detector = PrefixDetector(loader)
    formatter = ResultFormatter(loader)
    matcher = WordMatcher(loader, detector, formatter)

    # Test a simple word
    word = "בְּמַּאֲמָר"
    result = matcher.match_word(word)
    print(f"Word: {word}")
    print(f"Result: {result}")
    assert 'text' in result
    assert 'strong' in result
    assert 'prefixes' in result
    assert 'suffix' in result

    print("✓ Word matcher tests passed\n")


def test_result_formatter():
    """Test result formatting"""
    print("Testing result formatter...")

    loader = get_dictionary_loader()
    formatter = ResultFormatter(loader)

    # Test basic formatting
    result = formatter.format_word_result("בְּמַּאֲמָר", "H561", ["Hb"], None)
    print(f"Formatted result: {result}")
    assert result['text'] == "בְּמַּאֲמָר"
    assert result['strong'] == "Hb/H561"
    assert result['prefixes'] == ["Hb"]

    # Test separator addition
    hebrew = "בְּמַּאֲמָר הָרִאשׁוֹן"
    words = [
        {'text': 'בְּמַּאֲמָר', 'prefixes': ['Hb']},
        {'text': 'הָרִאשׁוֹן', 'prefixes': ['Hd']}
    ]
    result_text = formatter.add_prefix_separators(hebrew, words)
    print(f"Hebrew with separators: {result_text}")
    assert '/' in result_text  # Should have prefix separators

    print("✓ Result formatter tests passed\n")


def test_book_processor():
    """Test book processor integration"""
    print("Testing book processor...")

    loader = get_dictionary_loader()
    detector = PrefixDetector(loader)
    formatter = ResultFormatter(loader)
    matcher = WordMatcher(loader, detector, formatter)
    processor = BookProcessor(matcher, formatter)

    # Test that processor is properly initialized
    assert processor.matcher is not None
    assert processor.formatter is not None
    assert processor.sqlite_loader is not None
    assert processor.parser is not None

    print("✓ Book processor tests passed\n")


def main():
    """Run all tests"""
    print("Running Delitzsch Strong's Matcher tests...\n")
    print("Testing new modular architecture:\n")

    try:
        test_hebrew_utils()
        test_dictionary_loading()
        test_prefix_detector()
        test_result_formatter()
        test_word_matcher()
        test_book_processor()

        print("🎉 All tests passed!")
        print("✓ New modular architecture is working correctly")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())