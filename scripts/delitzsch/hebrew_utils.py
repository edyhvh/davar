"""
Hebrew text processing utilities for Delitzsch Strong's Matcher
"""

import re
from typing import Tuple, Optional


# Unicode ranges for Hebrew nikud (vowel points and accents)
NIKUD_PATTERN = re.compile(r'[\u0591-\u05BD\u05BF-\u05C7]')

# Hebrew final forms mapping for normalization
FINAL_FORMS = {
    '\u05da': '\u05db',  # ך -> כ
    '\u05dd': '\u05de',  # ם -> מ
    '\u05df': '\u05e0',  # ן -> נ
    '\u05e3': '\u05e4',  # ף -> פ
    '\u05e5': '\u05e6',  # ץ -> צ
}

# Maqaf (Hebrew hyphen) character
MAQAF = '\u05be'


def strip_nikud(text):
    """
    Remove Hebrew nikud (vowel points) from text using Unicode ranges.

    Args:
        text (str): Hebrew text with nikud

    Returns:
        str: Text without nikud
    """
    return NIKUD_PATTERN.sub('', text)


def normalize_final_forms(text):
    """
    Convert Hebrew final forms to regular forms for matching.

    Args:
        text (str): Hebrew text

    Returns:
        str: Text with final forms normalized
    """
    return ''.join(FINAL_FORMS.get(char, char) for char in text)


def tokenize_verse(verse_text):
    """
    Tokenize Hebrew verse text into individual words.
    Splits on whitespace and maqaf (־).

    Args:
        verse_text (str): Full verse text

    Returns:
        list[str]: List of individual words
    """
    # Split on whitespace
    words = verse_text.split()

    # Further split on maqaf and filter out empty strings
    tokenized = []
    for word in words:
        # Split on maqaf and add each part
        parts = word.split(MAQAF)
        tokenized.extend(part for part in parts if part.strip())

    return tokenized


def normalize_for_matching(text):
    """
    Normalize Hebrew text for dictionary matching.
    Strips nikud, converts final forms, and fixes corrupted Unicode.

    Args:
        text (str): Hebrew text with nikud

    Returns:
        str: Normalized text for matching
    """
    # First, fix corrupted Unicode (sin/shin dots in wrong positions)
    # U+05C2 (sin dot) and U+05C1 (shin dot) often appear incorrectly - strip them
    text = text.replace('\u05c2', '')  # Remove misplaced sin dots
    text = text.replace('\u05c1', '')  # Remove misplaced shin dots

    # Then do standard normalization
    text = strip_nikud(text)
    text = normalize_final_forms(text)
    return text


def is_hebrew_text(text):
    """
    Check if text contains Hebrew characters.

    Args:
        text (str): Text to check

    Returns:
        bool: True if contains Hebrew characters
    """
    # Hebrew Unicode range: U+0590-U+05FF
    return bool(re.search(r'[\u0590-\u05FF]', text))


def clean_word_for_processing(word):
    """
    Clean word for processing, removing punctuation and non-Hebrew characters
    that might interfere with matching.

    Args:
        word (str): Word to clean

    Returns:
        str: Cleaned word
    """
    # First, fix corrupted Unicode (sin/shin dots in wrong positions)
    # U+05C2 (sin dot) and U+05C1 (shin dot) often appear incorrectly - strip them
    word = word.replace('\u05c2', '')  # Remove misplaced sin dots
    word = word.replace('\u05c1', '')  # Remove misplaced shin dots

    # Strip common Hebrew punctuation marks
    word = word.rstrip('׃׀־׳״')  # sof pasuq, paseq, maqaf, geresh, gershayim
    return word.strip()


def strip_suffix(text: str) -> Tuple[str, Optional[str]]:
    """
    Strip Hebrew suffixes (pronominal and verb conjugation).
    Now operates on text WITH final forms, before normalization.
    Returns (stem, suffix_id) or (text, None) if no suffix found.

    Handles both:
    - Pronominal suffixes (on nouns/prepositions): נו, כם, ה, ו, ם, etc.
    - Verb conjugation suffixes: תי, תם, תן, נו, etc.
    """
    # Combined suffixes (longest first for greedy matching)
    # Now includes both final forms (ך, ם, ן) and normalized forms (כ, מ, נ)
    # Added compound suffixes like ים, ות, etc.
    SUFFIXES = {
        # Compound suffixes (plural + pronominal)
        'יהם': 'S3mp',  # their/them (3rd masculine plural)
        'יהן': 'S3fp',  # their/them (3rd feminine plural)
        'ינו': 'S1cp',  # our/us (1st person common plural)
        'יכם': 'S2mp',  # your (2nd masculine plural)
        'יכן': 'S2fp',  # your (2nd feminine plural)
        'ים': 'S3mp',   # them (masculine plural - י + ם)
        'ות': 'S3fp',   # them (feminine plural - ו + ת)
        'יך': 'S2',     # your (י + כ)
        'יו': 'S3ms',   # his (י + ו)

        # Pronominal suffixes (with final forms)
        'נו': 'S1cp',   # our/us (1st person common plural)
        'כם': 'S2mp',   # your (2nd masculine plural)
        'כן': 'S2fp',   # your (2nd feminine plural)
        'הם': 'S3mp',   # their/them (3rd masculine plural)
        'הן': 'S3fp',   # their/them (3rd feminine plural)
        'תי': 'S1cs',   # I (1st common singular - verb suffix)
        'תם': 'S2mp',   # you (2nd masculine plural - verb suffix)
        'תן': 'S2fp',   # you (2nd feminine plural - verb suffix)
        'ך': 'S2',      # your (WITH FINAL FORM - this is the key fix!)
        'כ': 'S2',      # your (normalized form)
        'ה': 'S3fs',    # her (3rd feminine singular)
        'ו': 'S3ms',    # his/him (3rd masculine singular)
        'ם': 'S3mp',    # them (WITH FINAL FORM - another key fix!)
        'מ': 'S3mp',    # them (normalized - alternate)
        'ן': 'S3fp',    # them (WITH FINAL FORM - another key fix!)
        'נ': 'S3fp',    # them (normalized - alternate)
        'ת': 'S2',      # you (2nd person - verb suffix)
    }

    # Try suffixes from longest to shortest
    for suffix, suffix_id in SUFFIXES.items():
        if text.endswith(suffix) and len(text) > len(suffix):
            stem = text[:-len(suffix)]
            # Validate stem is reasonable (at least 2 chars)
            if len(stem) >= 2:
                return stem, suffix_id

    return text, None