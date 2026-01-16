"""
Prefix detection logic for Hebrew words
Identifies Hebrew prefixes (ו, ב, ל, כ, מ, ה) with grammar-based validation
"""

from typing import Dict, List, Optional, Tuple

from hebrew_utils import strip_nikud


class PrefixDetector:
    """
    Detects and identifies Hebrew prefixes in words using Hebrew grammar rules.
    
    Handles prefix detection for:
    - Conjunctive vav (ו) - "and"
    - Prepositions (ב, ל, כ) - "in/at/with", "to/for", "like/as"
    - Mem prefix (מ) - "from" or Hiphil participle
    - Definite article (ה) - "the"
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

    def __init__(self, dictionary_loader):
        """
        Initialize prefix detector.
        
        Args:
            dictionary_loader: Dictionary loader instance for accessing prefix forms
        """
        self.loader = dictionary_loader

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
        prefixes, stem = self._identify_validated(word, conservative)
        return prefixes, stem

    def _identify_validated(self, word: str, conservative: bool = False) -> Tuple[List[str], str]:
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
        result = self._try_match_standard(remaining, CONJUNCTIVE_VAV, MIN_STEM_DEFAULT)
        if result:
            prefix_id, new_remaining = result
            found_prefixes.append(prefix_id)
            remaining = new_remaining

        # Step 2a: Try to match safe prepositions (ב, ל, כ)
        result = self._try_match_standard(remaining, SAFE_PREPOSITIONS, MIN_STEM_DEFAULT)
        if result:
            prefix_id, new_remaining = result
            found_prefixes.append(prefix_id)
            remaining = new_remaining
        else:
            # Step 2b: Try מ prefix - distinguish between:
            # - Preposition מִן (מִ/מֵ patterns) → HR
            # - Hiphil participle (מוֹ/מַ patterns) → Hm
            # Only enabled for words WITH Strong's numbers (not conservative mode)
            result = self._try_match_mem(remaining, MIN_STEM_FOR_MEM)
            if result:
                prefix_id, new_remaining = result
                found_prefixes.append(prefix_id)
                remaining = new_remaining

        # Step 3: Try to match definite article (ה)
        result = self._try_match_standard(remaining, DEFINITE_ARTICLE, MIN_STEM_FOR_HE)
        if result:
            prefix_id, new_remaining = result
            found_prefixes.append(prefix_id)
            remaining = new_remaining

        return found_prefixes, remaining

    def _try_match_standard(self, word: str, prefix_chars: Dict[str, str], min_stem: int) -> Optional[Tuple[str, str]]:
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

    def _try_match_mem(self, word: str, min_stem: int) -> Optional[Tuple[str, str]]:
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

    def _is_nikud(self, char: str) -> bool:
        """Check if a character is Hebrew nikud (vowel point or accent)"""
        code = ord(char)
        # Hebrew nikud range: U+0591 to U+05C7
        return 0x0591 <= code <= 0x05C7

    def _identify_exact(self, word: str) -> Tuple[List[str], str]:
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

    def _identify_common(self, word: str) -> Tuple[List[str], str]:
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
