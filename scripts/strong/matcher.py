"""
Core matching logic for Delitzsch Strong's Matcher
Identifies prefixes and matches stems to Strong's numbers
"""

import logging
from typing import Dict, List, Optional, Tuple

from dictionary_loader import get_dictionary_loader
from text_parser import get_text_parser
from hebrew_utils import normalize_for_matching, tokenize_verse, clean_word_for_processing, strip_nikud, strip_suffix

try:
    from debug_logger import debug_log
except ImportError:
    # Fallback if debug_logger not available
    def debug_log(*args, **kwargs):
        pass


class HebrewMatcher:
    """
    Matches Hebrew words to Strong's numbers with prefix identification.
    """

    # Common Hebrew prefix characters (without nikud)
    COMMON_PREFIX_CHARS = {
        'ב': 'Hb',  # in, at, with
        'ל': 'Hl',  # to, for
        'כ': 'Hk',  # like, as
        'מ': 'Hm',  # from
        'ו': 'Hc',  # and
        # REMOVED: 'ה': 'Hd',  # Causes false positives - ה is often part of verb morphology
        # REMOVED: 'ש': 'Ht',  # Causes false positives on 533 words
    }

    def __init__(self):
        self.loader = get_dictionary_loader()
        self.unmatched_log = []

    def process_verse_from_sqlite(self, verse_text: str) -> List[Dict]:
        """
        Process all words in a verse from SQLite text with embedded Strong's tags.

        Args:
            verse_text: Full Hebrew verse text with <S>NNNN</S> tags

        Returns:
            List of word dictionaries with text, strong, prefixes
        """
        parser = get_text_parser()
        parsed_words = parser.parse_verse_text(verse_text)
        processed_words = []

        for word_data in parsed_words:
            processed_word = self.process_word_with_strong(word_data)
            processed_words.append(processed_word)

        return processed_words

    def process_verse(self, verse_text: str) -> List[Dict]:
        """
        Process all words in a verse and return word analysis.
        LEGACY METHOD - kept for backward compatibility.

        Args:
            verse_text: Full Hebrew verse text with nikud

        Returns:
            List of word dictionaries with text, strong, prefixes
        """
        words = tokenize_verse(verse_text)
        processed_words = []

        for word in words:
            processed_word = self.process_word(word)
            processed_words.append(processed_word)

        return processed_words

    def process_word_with_strong(self, word_data: Dict) -> Dict:
        """
        Process a word that already has a Strong's number from SQLite.
        Performs prefix detection and formats the result.

        Args:
            word_data: Dictionary with 'text', 'text_no_nikud', 'strong' keys

        Returns:
            Processed word dictionary with prefixes and formatted strong number
        """
        original_word = word_data['text']  # Preserve original for output
        strong_number = word_data.get('strong')

        # #region agent log
        debug_log('matcher.py:process_word_with_strong', 'Processing word with pre-existing Strong number', {'word': original_word, 'strong': strong_number}, 'SQLITE')
        # #endregion

        # Clean word for prefix detection only
        cleaned_word = clean_word_for_processing(original_word)

        # Identify prefixes on the cleaned word
        # Use conservative mode for words without Strong's numbers (less reliable)
        has_strong = strong_number is not None
        prefixes, stem = self.identify_prefixes(cleaned_word, conservative=not has_strong)

        # #region agent log
        debug_log('matcher.py:process_word_with_strong', 'Prefix detection result', {'prefixes': prefixes, 'stem': stem}, 'SQLITE')
        # #endregion

        # Format the result using the ORIGINAL word text and provided Strong's number
        return self._format_result_with_strong(original_word, strong_number, prefixes, stem)

    def process_word(self, word: str) -> Dict:
        """
        Process Hebrew word with proper fallback chain:
        1. Try whole word lookup
        2. Try prefix stripping + whole word lookup
        3. Try prefix stripping + suffix stripping + lookup
        4. Return None if all fail
        """
        # #region agent log
        debug_log('matcher.py:process_word', 'Starting word processing', {'original_word': word}, 'A')
        # #endregion

        word = clean_word_for_processing(word)
        normalized_word = normalize_for_matching(word)

        # #region agent log
        debug_log('matcher.py:process_word', 'After cleaning and normalization', {'cleaned_word': word, 'normalized_word': normalized_word}, 'A')
        # #endregion

        # STEP 1: Try whole word first (EXPANDED)
        # Try multiple lookup strategies for compound words
        # #region agent log
        debug_log('matcher.py:process_word', 'STEP 1: Whole word lookup', {'normalized_word': normalized_word}, 'A')
        # #endregion

        strong_number = self.loader.get_strong_number(normalized_word)
        # #region agent log
        debug_log('matcher.py:process_word', 'STEP 1: Normalized lookup result', {'normalized_word': normalized_word, 'strong_number': strong_number}, 'A')
        # #endregion

        if not strong_number:
            # Try with common prefix prepended (for words like "למען" stored as "מען")
            for prefix_char in ['ל', 'ב', 'כ', 'מ']:
                if normalized_word.startswith(prefix_char):
                    # Try without first letter
                    without_prefix = normalized_word[1:]
                    strong_number = self.loader.get_strong_number(without_prefix)
                    if strong_number:
                        # Found it! Return with single prefix
                        # #region agent log
                        debug_log('matcher.py:process_word', 'STEP 1: Found with prefix stripped', {'without_prefix': without_prefix, 'strong_number': strong_number}, 'A')
                        # #endregion
                        return self._format_result(word, strong_number, [self.COMMON_PREFIX_CHARS[prefix_char]], None)

        if not strong_number:
            # Try preserving final forms (dictionary might have them)
            from hebrew_utils import strip_nikud
            preserved_finals = strip_nikud(word)  # strip nikud only, keep finals
            # #region agent log
            debug_log('matcher.py:process_word', 'STEP 1: Trying preserved finals', {'preserved_finals': preserved_finals}, 'A')
            # #endregion

            strong_number = self.loader.get_strong_number(preserved_finals)
            # #region agent log
            debug_log('matcher.py:process_word', 'STEP 1: Preserved finals lookup result', {'preserved_finals': preserved_finals, 'strong_number': strong_number}, 'A')
            # #endregion

        if strong_number:
            # #region agent log
            debug_log('matcher.py:process_word', 'STEP 1: Whole word match found', {'strong_number': strong_number}, 'A')
            # #endregion
            return self._format_result(word, strong_number, [], None)

        # STEP 2: Try prefix stripping
        # #region agent log
        debug_log('matcher.py:process_word', 'STEP 2: Starting prefix stripping', {}, 'B')
        # #endregion

        prefixes, stem = self.identify_prefixes(word)

        # #region agent log
        debug_log('matcher.py:process_word', 'STEP 2: Prefix stripping result', {'prefixes': prefixes, 'stem': stem}, 'B')
        # #endregion

        # STEP 4: Check for composite preposition (prefix + suffix only, no stem)
        # This must happen BEFORE stem validation
        if prefixes and stem:
            stem_clean = strip_nikud(stem)
            if stem_clean in ['ו', 'י', 'ה', 'ם', 'ן', 'נו', 'כם'] or stem_clean == '':
                # This is a composite preposition: prefix + suffix with no stem
                # For empty stem_clean, the suffix is the original stem (just nikud)
                suffix = stem_clean if stem_clean else stem
                # #region agent log
                debug_log('matcher.py:process_word', 'STEP 4: Composite preposition match found', {'prefixes': prefixes, 'suffix': suffix}, 'D')
                # #endregion
                return self._format_result(word, None, prefixes, suffix)

        # Validate stem after prefix removal
        stem_valid = self._is_valid_stem(stem)
        # #region agent log
        debug_log('matcher.py:process_word', 'STEP 2: Stem validation', {'stem': stem, 'stem_valid': stem_valid}, 'B')
        # #endregion

        if not stem_valid:
            # Prefix detection was likely wrong, log and return null
            # #region agent log
            debug_log('matcher.py:process_word', 'STEP 2: Invalid stem, returning null', {'stem': stem}, 'B')
            # #endregion
            self._log_unmatched(word, stem, "invalid stem after prefix removal")
            return self._format_result(word, None, [], None)

        normalized_stem = normalize_for_matching(stem)
        # #region agent log
        debug_log('matcher.py:process_word', 'STEP 2: Normalized stem for lookup', {'normalized_stem': normalized_stem}, 'B')
        # #endregion

        strong_number = self.loader.get_strong_number(normalized_stem)
        # #region agent log
        debug_log('matcher.py:process_word', 'STEP 2: Stem lookup result', {'normalized_stem': normalized_stem, 'strong_number': strong_number}, 'B')
        # #endregion

        if strong_number:
            # #region agent log
            debug_log('matcher.py:process_word', 'STEP 2: Prefix stripping match found', {'strong_number': strong_number, 'prefixes': prefixes}, 'B')
            # #endregion
            return self._format_result(word, strong_number, prefixes, None)

        # STEP 3: Try suffix stripping (BEFORE final form normalization)
        # #region agent log
        debug_log('matcher.py:process_word', 'STEP 3: Starting suffix stripping', {'normalized_stem': normalized_stem}, 'C')
        # #endregion

        # Strip suffix on text with nikud removed but finals preserved
        stem_with_finals = strip_nikud(stem)
        stem_no_suffix, suffix_id = strip_suffix(stem_with_finals)
        # #region agent log
        debug_log('matcher.py:process_word', 'STEP 3: Suffix stripping result', {'stem_with_finals': stem_with_finals, 'stem_no_suffix': stem_no_suffix, 'suffix_id': suffix_id}, 'C')
        # #endregion

        if suffix_id:
            # Now normalize the stem for lookup
            stem_normalized = normalize_for_matching(stem_no_suffix)
            strong_number = self.loader.get_strong_number(stem_normalized)
            # #region agent log
            debug_log('matcher.py:process_word', 'STEP 3: Normalized stem lookup result', {'stem_normalized': stem_normalized, 'strong_number': strong_number}, 'C')
            # #endregion
            if strong_number:
                # #region agent log
                debug_log('matcher.py:process_word', 'STEP 3: Suffix stripping match found', {'strong_number': strong_number, 'prefixes': prefixes, 'suffix_id': suffix_id}, 'C')
                # #endregion
                return self._format_result(word, strong_number, prefixes, suffix_id)


        # All strategies failed
        # #region agent log
        debug_log('matcher.py:process_word', 'All strategies failed', {'word': word, 'stem': stem, 'normalized_stem': normalized_stem, 'stem_no_suffix': stem_no_suffix}, 'E')
        # #endregion
        self._log_unmatched(word, stem, "no dictionary match")
        # FIX: Don't return prefixes if we couldn't verify the stem
        # If we can't match the stem to a dictionary entry, the prefix detection was likely wrong
        return self._format_result(word, None, [], None)

    def _is_valid_stem(self, stem: str) -> bool:
        """Validate stem is reasonable after prefix removal"""
        if not stem:
            return False
        # Strip nikud to check actual letter count
        clean_stem = strip_nikud(stem)
        return len(clean_stem) >= 2

    def _format_result_with_strong(self, word: str, strong_number: str, prefixes: List[str], stem: str = None) -> Dict:
        """Format the result dictionary when Strong's number is already known"""
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

    def _format_result(self, word: str, strong_number: str, prefixes: List[str], suffix_id: Optional[str]) -> Dict:
        """Format the result dictionary with prefixes and suffix"""
        if strong_number and prefixes:
            prefix_str = '/'.join(prefixes)
            strong_number = f"{prefix_str}/{strong_number}"

        result = {
            'text': word,
            'strong': strong_number,
            'prefixes': prefixes if prefixes else [],
            'suffix': suffix_id  # NEW: track suffixes
        }

        # Add possible_proper_name flag if the Strong's number is a proper name
        # This helps identify potential dictionary collisions
        if strong_number and self.loader.is_proper_name(strong_number):
            result['possible_proper_name'] = True

        return result

    def _log_unmatched(self, word: str, stem: str, reason: str):
        """Log unmatched words for debugging"""
        self.unmatched_log.append({
            'word': word,
            'stem': stem,
            'reason': reason
        })

    def identify_prefixes(self, word: str, conservative: bool = False) -> Tuple[List[str], str]:
        """
        Identify Hebrew prefixes in a word using sophisticated validation.

        Args:
            word: Hebrew word with nikud
            conservative: If True, be more conservative (for words without Strong's numbers)

        Returns:
            Tuple of (prefix_ids, remaining_stem)
        """
        if not word:
            return [], word

        # Try to detect prefixes with stem validation
        prefixes, stem = self._identify_prefixes_validated(word, conservative)
        return prefixes, stem

    def _identify_prefixes_validated(self, word: str, conservative: bool = False) -> Tuple[List[str], str]:
        """
        Identify prefixes with validation following Hebrew grammar rules.

        Hebrew prefix grammar (in order):
        1. Optionally: ו (conjunctive vav - "and")
        2. Optionally: ב, ל, כ, or מ (preposition)
        3. Optionally: ה (definite article)

        Rules:
        - For ו, ב, ל, כ prefixes: remaining stem must have >= 2 consonants
        - For מ (from): remaining stem must have >= 3 consonants (to reduce false positives)
        - For ה (definite article): remaining stem must have >= 3 consonants
        - Each prefix type can only appear once
        - In conservative mode: skip מ detection entirely (too many false positives)

        Args:
            word: Hebrew word with nikud
            conservative: If True, be more conservative with prefix detection

        Returns:
            Tuple of (prefix_ids, remaining_stem)
        """
        if not word:
            return [], word

        # Minimum stem lengths by prefix type
        MIN_STEM_FOR_HE = 3    # e.g., "היה" has stem "יה" = 2, so NOT a prefix
        MIN_STEM_FOR_MEM = 3   # מ needs longer stem validation
        MIN_STEM_DEFAULT = 2   # e.g., "להם" has stem "הם" = 2, IS a prefix

        # In conservative mode (words without Strong's), disable מ and be stricter with ה
        if conservative:
            MIN_STEM_FOR_HE = 4
            MIN_STEM_FOR_MEM = 99  # Effectively disable מ in conservative mode
            MIN_STEM_DEFAULT = 2

        # Prefix categories following Hebrew grammar order
        CONJUNCTIVE_VAV = {'ו': 'Hc'}
        SAFE_PREPOSITIONS = {'ב': 'Hb', 'ל': 'Hl', 'כ': 'Hk'}
        MEM_PREFIX = {'מ': 'Hm'}  # For Hiphil participles and preposition מן
        DEFINITE_ARTICLE = {'ה': 'Hd'}

        found_prefixes = []
        remaining = word

        # Step 1: Try to match conjunctive vav (ו)
        result = self._try_match_prefix(remaining, CONJUNCTIVE_VAV, MIN_STEM_DEFAULT)
        if result:
            prefix_id, new_remaining = result
            found_prefixes.append(prefix_id)
            remaining = new_remaining

        # Step 2a: Try to match safe prepositions (ב, ל, כ)
        result = self._try_match_prefix(remaining, SAFE_PREPOSITIONS, MIN_STEM_DEFAULT)
        if result:
            prefix_id, new_remaining = result
            found_prefixes.append(prefix_id)
            remaining = new_remaining
        else:
            # Step 2b: Try מ prefix - distinguish between:
            # - Preposition מִן (מִ/מֵ patterns) → HR
            # - Hiphil participle (מוֹ/מַ patterns) → Hm
            # Only enabled for words WITH Strong's numbers (not conservative mode)
            result = self._try_match_mem_prefix(remaining, MIN_STEM_FOR_MEM)
            if result:
                prefix_id, new_remaining = result
                found_prefixes.append(prefix_id)
                remaining = new_remaining

        # Step 3: Try to match definite article (ה)
        result = self._try_match_prefix(remaining, DEFINITE_ARTICLE, MIN_STEM_FOR_HE)
        if result:
            prefix_id, new_remaining = result
            found_prefixes.append(prefix_id)
            remaining = new_remaining

        return found_prefixes, remaining

    def _try_match_prefix(self, word: str, prefix_chars: Dict[str, str], min_stem: int) -> Optional[Tuple[str, str]]:
        """
        Try to match a prefix from the given set.

        Args:
            word: Word to check
            prefix_chars: Dict of {char: prefix_id}
            min_stem: Minimum consonants required in remaining stem

        Returns:
            Tuple of (prefix_id, remaining_word) if matched, None otherwise
        """
        if not word:
            return None

        # Get the first character without nikud
        first_char = strip_nikud(word[0])

        if first_char not in prefix_chars:
            return None

        prefix_id = prefix_chars[first_char]

        # Special check for definite article (ה)
        # Reject הִ (hiriq) - this is Hifil/Hitpael verbal pattern, not definite article
        if prefix_id == 'Hd' and len(word) > 1:
            second_char = word[1]
            if self._is_nikud(second_char):
                nikud_code = ord(second_char)
                # U+05B4 = hiriq (ִ) - indicates Hifil/Hitpael, not definite article
                if nikud_code == 0x05B4:
                    return None

        # Find where the first consonant ends (include its nikud)
        prefix_end = 1
        while prefix_end < len(word) and self._is_nikud(word[prefix_end]):
            prefix_end += 1

        potential_stem = word[prefix_end:]
        stem_consonants = strip_nikud(potential_stem)

        # Validate stem has enough consonants
        if len(stem_consonants) < min_stem:
            return None

        return (prefix_id, potential_stem)

    def _is_nikud(self, char: str) -> bool:
        """Check if a character is Hebrew nikud (vowel point or accent)"""
        code = ord(char)
        # Hebrew nikud range: U+0591 to U+05C7
        return 0x0591 <= code <= 0x05C7

    def _try_match_mem_prefix(self, word: str, min_stem: int) -> Optional[Tuple[str, str]]:
        """
        Try to match מ prefix, distinguishing between:
        - Preposition מִן (מִ/מֵ patterns) → HR (relational preposition)
        - Hiphil participle (מוֹ/מַ patterns) → Hm (morphological prefix)

        Args:
            word: Word to check
            min_stem: Minimum consonants required in remaining stem

        Returns:
            Tuple of (prefix_id, remaining_word) if matched, None otherwise
        """
        if not word:
            return None

        # Check if first character is מ
        first_char = strip_nikud(word[0])
        if first_char != 'מ':
            return None

        # Get the nikud pattern to determine type
        # Need to handle:
        # 1. מִ/מֵ (preposition) - nikud directly on מ
        # 2. מוֹ (Hiphil cholam male) - מ + ו + cholam
        # 3. מַ (Hiphil patach) - nikud directly on מ

        prefix_id = None
        prefix_end = 1

        # Skip any nikud directly after מ
        while prefix_end < len(word) and self._is_nikud(word[prefix_end]):
            nikud_code = ord(word[prefix_end])
            # Check nikud type
            if nikud_code == 0x05B4 or nikud_code == 0x05B5:
                # U+05B4 (hiriq ִ) or U+05B5 (tzere ֵ) = preposition מִן → HR
                prefix_id = 'HR'
            elif nikud_code == 0x05B7:
                # U+05B7 (patach ַ) = Hiphil pattern → Hm
                prefix_id = 'Hm'
            elif nikud_code == 0x05B9:
                # U+05B9 (cholam ֹ) = Hiphil pattern → Hm
                prefix_id = 'Hm'
            prefix_end += 1

        # Check for cholam male pattern: מ + ו + cholam (מוֹ)
        if prefix_id is None and prefix_end < len(word):
            next_char = word[prefix_end]
            if next_char == 'ו':
                # Check if followed by cholam
                if prefix_end + 1 < len(word) and ord(word[prefix_end + 1]) == 0x05B9:
                    # Cholam male pattern (מוֹ) = Hiphil → Hm
                    prefix_id = 'Hm'
                    prefix_end += 2  # Skip ו and cholam
                    # Skip any additional nikud
                    while prefix_end < len(word) and self._is_nikud(word[prefix_end]):
                        prefix_end += 1

        if prefix_id is None:
            return None

        potential_stem = word[prefix_end:]
        stem_consonants = strip_nikud(potential_stem)

        # Validate stem has enough consonants
        if len(stem_consonants) < min_stem:
            return None

        return (prefix_id, potential_stem)

    def _identify_prefixes_exact(self, word: str) -> Tuple[List[str], str]:
        """
        Try to identify prefixes using exact form matching from dictionary.

        Args:
            word: Hebrew word with nikud

        Returns:
            Tuple of (prefix_ids, remaining_stem)
        """
        # Try to find the word in prefix_forms
        prefix_forms = self.loader.prefix_forms

        # Check if the entire word is a known prefix form
        if word in prefix_forms:
            return prefix_forms[word], ""

        # Try to find prefixes by checking increasingly long substrings
        # This handles compound prefixes like "וּבִ" (Hc + Hb)
        remaining = word
        found_prefixes = []

        # Sort by length (longest first) to handle compound prefixes
        sorted_forms = sorted(prefix_forms.keys(), key=len, reverse=True)

        while remaining:
            found = False
            for form in sorted_forms:
                if remaining.startswith(form):
                    found_prefixes.extend(prefix_forms[form])
                    remaining = remaining[len(form):]
                    found = True
                    break

            if not found:
                break

        return found_prefixes, remaining

    def _identify_prefixes_common(self, word: str) -> Tuple[List[str], str]:
        """
        Fallback method using common prefix characters.

        Args:
            word: Hebrew word with nikud

        Returns:
            Tuple of (prefix_ids, remaining_stem)
        """
        if not word:
            return [], ""

        # Get first character without nikud
        first_char = strip_nikud(word[0])

        prefix_id = self.COMMON_PREFIX_CHARS.get(first_char)
        if prefix_id:
            return [prefix_id], word[1:]
        else:
            return [], word

    def get_unmatched_words(self) -> List[Dict]:
        """Get list of unmatched words for logging"""
        return self.unmatched_log.copy()

    def clear_unmatched_log(self):
        """Clear the unmatched words log"""
        self.unmatched_log.clear()


def process_delitzsch_book_from_sqlite(book_name: str) -> List[Dict]:
    """
    Process an entire Delitzsch book from SQLite database.

    Args:
        book_name: Name of the book

    Returns:
        List of chapter dictionaries ready for JSON output
    """
    from sqlite_loader import get_sqlite_loader

    loader = get_sqlite_loader()
    matcher = HebrewMatcher()
    chapters_output = []

    # Get book number from name
    book_number = loader.get_book_number(book_name)
    if not book_number:
        raise ValueError(f"Unknown book name: {book_name}")

    # Get all verses for this book
    book_verses = loader.get_book_verses(book_number)

    for chapter_num, verses in book_verses.items():
        verses_output = []

        for verse_data in verses:
            verse_num = verse_data['verse']
            verse_text_with_tags = verse_data['text']

            # Clean text for display (remove tags)
            from text_parser import get_text_parser
            parser = get_text_parser()
            clean_verse_text = parser.clean_verse_text_for_display(verse_text_with_tags)

            # Process the verse with SQLite data
            words = matcher.process_verse_from_sqlite(verse_text_with_tags)

            # Add "/" separators for prefixes in the Hebrew text
            hebrew_with_separators = _add_prefix_separators_to_hebrew(clean_verse_text, words)

            verse_output = {
                'chapter': chapter_num,
                'verse': verse_num,
                'hebrew': hebrew_with_separators,
                'words': words
            }
            verses_output.append(verse_output)

        # Group by chapter
        chapter_output = {
            'chapter': chapter_num,
            'verses': verses_output
        }
        chapters_output.append(chapter_output)

    return chapters_output


def _add_prefix_separators_to_hebrew(hebrew_text: str, words: List[Dict]) -> str:
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
                while char_pos < len(word_text) and _is_nikud_char(word_text[char_pos]):
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
                            while char_pos < len(word_text) and _is_nikud_char(word_text[char_pos]):
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


def _is_nikud_char(char: str) -> bool:
    """Check if a character is Hebrew nikud (vowel point or accent)"""
    code = ord(char)
    return 0x0591 <= code <= 0x05C7


def process_delitzsch_book(book_data: Dict, book_name: str) -> List[Dict]:
    """
    Process an entire Delitzsch book into chapter files.
    LEGACY METHOD - kept for backward compatibility.

    Args:
        book_data: Delitzsch book JSON data
        book_name: Name of the book

    Returns:
        List of chapter dictionaries ready for JSON output
    """
    matcher = HebrewMatcher()
    chapters_output = []

    for chapter_data in book_data.get('chapters', []):
        chapter_num = chapter_data.get('number')
        verses_output = []

        for verse_data in chapter_data.get('verses', []):
            verse_num = verse_data.get('number')
            verse_text = verse_data.get('text_nikud', '')

            # Process the verse
            words = matcher.process_verse(verse_text)

            verse_output = {
                'chapter': chapter_num,
                'verse': verse_num,
                'hebrew': verse_text,
                'words': words
            }
            verses_output.append(verse_output)

        # Group by chapter
        chapter_output = {
            'chapter': chapter_num,
            'hebrew_letter': chapter_data.get('hebrew_letter', ''),
            'verses': verses_output
        }
        chapters_output.append(chapter_output)

    return chapters_output