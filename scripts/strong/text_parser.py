"""
Text Parser for Delitzsch Strong's Matcher

Parses Hebrew text with embedded <S>NNNN</S> Strong's tags from SQLite database.
"""

import re
from typing import Dict, List, Optional, Tuple

from hebrew_utils import strip_nikud


class TextParser:
    """
    Parses Hebrew text with Strong's number tags from SQLite verses.
    """

    # Regex pattern to match word<S>number</S> pairs (including empty tags)
    # Captures: (word_without_tags, strong_number) or (word_without_tags, None)
    STRONG_TAG_PATTERN = re.compile(r'([^<\s]+)<S>(\d*)</S>')

    def __init__(self):
        pass

    def parse_verse_text(self, verse_text: str) -> List[Dict]:
        """
        Parse a verse text with Strong's tags into word dictionaries.
        Preserves the order of words as they appear in the verse.

        Args:
            verse_text: Hebrew text with <S>NNNN</S> tags

        Returns:
            List of word dictionaries with text, strong, prefixes
        """
        words = []
        remaining = verse_text

        # Process the verse text sequentially to maintain word order
        while remaining:
            # Try to match a word with Strong's tag
            match = self.STRONG_TAG_PATTERN.search(remaining)

            if match:
                # Check if there's untagged text before the match
                before_match = remaining[:match.start()].strip()
                if before_match:
                    # Process untagged words before this match
                    for word in before_match.split():
                        word = word.strip()
                        if word:
                            word_entry = self._create_word_entry(word, None)
                            words.append(word_entry)

                # Add the matched word with Strong's number
                hebrew_word = match.group(1)
                strong_num = match.group(2) if match.group(2) else None
                word_entry = self._create_word_entry(hebrew_word, strong_num)
                words.append(word_entry)

                # Move past this match
                remaining = remaining[match.end():].lstrip()
            else:
                # No more matches - process remaining untagged text
                for word in remaining.split():
                    word = word.strip()
                    if word:
                        word_entry = self._create_word_entry(word, None)
                        words.append(word_entry)
                break

        return words

    def _create_word_entry(self, hebrew_word: str, strong_num: Optional[str]) -> Dict:
        """
        Create a word entry dictionary.

        Args:
            hebrew_word: Hebrew word with nikud
            strong_num: Strong's number string or None

        Returns:
            Word entry dictionary
        """
        # Create text_no_nikud by stripping nikud
        text_no_nikud = strip_nikud(hebrew_word)

        # Format Strong's number
        formatted_strong = None
        if strong_num:
            formatted_strong = f"H{strong_num}"

        return {
            'text': hebrew_word,
            'strong': formatted_strong,
            'prefixes': []  # Will be filled by matcher logic
        }

    def extract_word_strong_pairs(self, verse_text: str) -> List[Tuple[str, Optional[str]]]:
        """
        Extract (word, strong_number) pairs from verse text.

        Args:
            verse_text: Hebrew text with <S>NNNN</S> tags

        Returns:
            List of (hebrew_word, strong_number) tuples
        """
        pairs = []

        # Find all word-Strong's pairs
        matches = self.STRONG_TAG_PATTERN.findall(verse_text)
        pairs.extend(matches)

        return pairs

    def clean_verse_text_for_display(self, verse_text: str) -> str:
        """
        Clean verse text by removing Strong's tags for display purposes.

        Args:
            verse_text: Hebrew text with <S>NNNN</S> tags

        Returns:
            Clean Hebrew text without tags
        """
        # Remove all <S>number</S> tags (including empty ones)
        clean_text = re.sub(r'<S>\d*</S>', '', verse_text)
        return clean_text.strip()


# Singleton instance
_parser_instance = None

def get_text_parser() -> TextParser:
    """Get singleton text parser instance"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = TextParser()
    return _parser_instance