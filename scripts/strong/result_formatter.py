"""
Result formatting logic for Hebrew word matching
Formats match results and adds prefix separators to Hebrew text
"""

from typing import Dict, List, Optional


class ResultFormatter:
    """
    Formats word matching results into output dictionaries.
    
    Handles:
    - Formatting word results with Strong's numbers and prefixes
    - Adding "/" separators for prefixes in Hebrew text
    - Proper name detection
    """

    def __init__(self, dictionary_loader):
        """
        Initialize result formatter.
        
        Args:
            dictionary_loader: Dictionary loader instance for accessing proper name data
        """
        self.loader = dictionary_loader

    def format_word_result(self, word: str, strong_number: Optional[str], 
                          prefixes: List[str], suffix_id: Optional[str] = None) -> Dict:
        """
        Format the result dictionary with prefixes and suffix.

        Args:
            word: Original Hebrew word text
            strong_number: Strong's number (e.g., "H1234") or None
            prefixes: List of prefix IDs (e.g., ["Hc", "Hb"])
            suffix_id: Suffix ID if detected (e.g., "ו", "ם")

        Returns:
            Formatted word dictionary with text, strong, prefixes, suffix
        """
        if strong_number and prefixes:
            prefix_str = '/'.join(prefixes)
            strong_number = f"{prefix_str}/{strong_number}"

        result = {
            'text': word,
            'strong': strong_number,
            'prefixes': prefixes if prefixes else [],
            'suffix': suffix_id  # Track suffixes
        }

        # Add possible_proper_name flag if the Strong's number is a proper name
        # This helps identify potential dictionary collisions
        if strong_number and self.loader.is_proper_name(strong_number):
            result['possible_proper_name'] = True

        return result

    def format_word_result_with_strong(self, word: str, strong_number: str, 
                                      prefixes: List[str], stem: str = None) -> Dict:
        """
        Format the result dictionary when Strong's number is already known.
        
        This is used when processing words from SQLite with pre-assigned Strong's numbers.

        Args:
            word: Original Hebrew word text
            strong_number: Strong's number (e.g., "H1234")
            prefixes: List of prefix IDs (e.g., ["Hc", "Hb"])
            stem: Remaining stem after prefix removal (optional)

        Returns:
            Formatted word dictionary with text, strong, prefixes
        """
        formatted_strong = strong_number

        if strong_number and prefixes:
            prefix_str = '/'.join(prefixes)
            formatted_strong = f"{prefix_str}/{strong_number}"

        result = {
            'text': word,
            'strong': formatted_strong,
            'prefixes': prefixes if prefixes else []
        }

        # Add possible_proper_name flag if the Strong's number is a proper name
        if strong_number and self.loader.is_proper_name(strong_number):
            result['possible_proper_name'] = True

        return result

    def add_prefix_separators(self, hebrew_text: str, words: List[Dict]) -> str:
        """
        Add "/" separators for prefixes in the Hebrew text based on word analysis.

        Args:
            hebrew_text: Clean Hebrew text without tags
            words: List of word dictionaries with prefix information

        Returns:
            Hebrew text with "/" separators for prefixes
        """
        result_parts = []
        remaining_text = hebrew_text

        for word_info in words:
            word_text = word_info['text']
            prefixes = word_info.get('prefixes', [])

            # Find the word in remaining text
            word_start = remaining_text.find(word_text)

            if word_start == -1:
                continue

            # Add any text before this word
            if word_start > 0:
                result_parts.append(remaining_text[:word_start])

            if prefixes:
                # Build the word with "/" after each prefix
                modified_word = ""
                char_pos = 0

                for prefix_code in prefixes:
                    if char_pos >= len(word_text):
                        break

                    # Add the consonant
                    modified_word += word_text[char_pos]
                    char_pos += 1

                    # Add any following nikud
                    while char_pos < len(word_text) and self._is_nikud_char(word_text[char_pos]):
                        modified_word += word_text[char_pos]
                        char_pos += 1

                    # Special handling for Hm (Hiphil) with cholam male (מוֹ)
                    # The vav is part of the prefix, not the stem
                    if prefix_code == 'Hm' and char_pos < len(word_text):
                        next_char = word_text[char_pos]
                        if next_char == 'ו':
                            # Check if followed by cholam
                            if char_pos + 1 < len(word_text) and ord(word_text[char_pos + 1]) == 0x05B9:
                                # Include vav + cholam in the prefix
                                modified_word += word_text[char_pos]  # vav
                                char_pos += 1
                                modified_word += word_text[char_pos]  # cholam
                                char_pos += 1
                                # Skip any additional nikud
                                while char_pos < len(word_text) and self._is_nikud_char(word_text[char_pos]):
                                    modified_word += word_text[char_pos]
                                    char_pos += 1

                    # Add "/" separator after this prefix
                    if char_pos < len(word_text):
                        modified_word += '/'

                # Add the remaining stem
                modified_word += word_text[char_pos:]
                result_parts.append(modified_word)
            else:
                result_parts.append(word_text)

            # Move past this word in remaining text
            remaining_text = remaining_text[word_start + len(word_text):]

        # Add any remaining text
        if remaining_text:
            result_parts.append(remaining_text)

        return ''.join(result_parts)

    def format_verse(self, verse_num: int, chapter_num: int, hebrew: str, words: List[Dict]) -> Dict:
        """
        Format complete verse output.

        Args:
            verse_num: Verse number
            chapter_num: Chapter number
            hebrew: Hebrew text (with or without separators)
            words: List of processed word dictionaries

        Returns:
            Complete verse dictionary ready for output
        """
        return {
            'chapter': chapter_num,
            'verse': verse_num,
            'hebrew': hebrew,
            'words': words
        }

    def _is_nikud_char(self, char: str) -> bool:
        """Check if a character is Hebrew nikud (vowel point or accent)"""
        code = ord(char)
        return 0x0591 <= code <= 0x05C7
