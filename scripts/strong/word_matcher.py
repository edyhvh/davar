"""
Core word matching logic for Hebrew words to Strong's numbers
Handles fallback chain: whole word → prefix stripping → suffix stripping
"""

from typing import Dict, List, Optional

from hebrew_utils import (
    normalize_for_matching, 
    clean_word_for_processing, 
    strip_nikud, 
    strip_suffix
)
from prefix_detector import PrefixDetector
from result_formatter import ResultFormatter

try:
    from debug_logger import debug_log
except ImportError:
    # Fallback if debug_logger not available
    def debug_log(*args, **kwargs):
        pass


class MatchResult:
    """
    Result of a word matching operation.
    
    Attributes:
        strong_number: Strong's number (e.g., "H1234") or None
        prefixes: List of prefix IDs
        suffix_id: Suffix ID if detected
        stem: Remaining stem after prefix removal
    """
    def __init__(self, strong_number: Optional[str] = None, 
                 prefixes: List[str] = None, 
                 suffix_id: Optional[str] = None,
                 stem: Optional[str] = None):
        self.strong_number = strong_number
        self.prefixes = prefixes if prefixes else []
        self.suffix_id = suffix_id
        self.stem = stem


class WordMatcher:
    """
    Matches Hebrew words to Strong's numbers using a fallback chain.
    
    Matching strategy:
    1. Try whole word lookup
    2. Try prefix stripping + lookup
    3. Try prefix + suffix stripping + lookup
    4. Return None if all strategies fail
    """

    def __init__(self, dictionary_loader, prefix_detector: PrefixDetector, 
                 result_formatter: ResultFormatter):
        """
        Initialize word matcher.
        
        Args:
            dictionary_loader: Dictionary loader instance
            prefix_detector: Prefix detector instance
            result_formatter: Result formatter instance
        """
        self.loader = dictionary_loader
        self.prefix_detector = prefix_detector
        self.formatter = result_formatter
        self.unmatched_log = []

    def match_word(self, word: str) -> Dict:
        """
        Match Hebrew word using proper fallback chain:
        1. Try whole word lookup
        2. Try prefix stripping + whole word lookup
        3. Try prefix stripping + suffix stripping + lookup
        4. Return None if all fail
        
        Args:
            word: Hebrew word with nikud
            
        Returns:
            Formatted word dictionary with text, strong, prefixes, suffix
        """
        # #region agent log
        debug_log('word_matcher.py:match_word', 'Starting word processing', {'original_word': word}, 'A')
        # #endregion

        word = clean_word_for_processing(word)
        normalized_word = normalize_for_matching(word)

        # #region agent log
        debug_log('word_matcher.py:match_word', 'After cleaning and normalization', {'cleaned_word': word, 'normalized_word': normalized_word}, 'A')
        # #endregion

        # STEP 1: Try whole word first (EXPANDED)
        # Try multiple lookup strategies for compound words
        # #region agent log
        debug_log('word_matcher.py:match_word', 'STEP 1: Whole word lookup', {'normalized_word': normalized_word}, 'A')
        # #endregion

        strong_number = self.loader.get_strong_number(normalized_word)
        # #region agent log
        debug_log('word_matcher.py:match_word', 'STEP 1: Normalized lookup result', {'normalized_word': normalized_word, 'strong_number': strong_number}, 'A')
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
                        debug_log('word_matcher.py:match_word', 'STEP 1: Found with prefix stripped', {'without_prefix': without_prefix, 'strong_number': strong_number}, 'A')
                        # #endregion
                        prefix_id = self.prefix_detector.COMMON_PREFIX_CHARS[prefix_char]
                        return self.formatter.format_word_result(word, strong_number, [prefix_id], None)

        if not strong_number:
            # Try preserving final forms (dictionary might have them)
            preserved_finals = strip_nikud(word)  # strip nikud only, keep finals
            # #region agent log
            debug_log('word_matcher.py:match_word', 'STEP 1: Trying preserved finals', {'preserved_finals': preserved_finals}, 'A')
            # #endregion

            strong_number = self.loader.get_strong_number(preserved_finals)
            # #region agent log
            debug_log('word_matcher.py:match_word', 'STEP 1: Preserved finals lookup result', {'preserved_finals': preserved_finals, 'strong_number': strong_number}, 'A')
            # #endregion

        if strong_number:
            # #region agent log
            debug_log('word_matcher.py:match_word', 'STEP 1: Whole word match found', {'strong_number': strong_number}, 'A')
            # #endregion
            return self.formatter.format_word_result(word, strong_number, [], None)

        # STEP 2: Try prefix stripping
        # #region agent log
        debug_log('word_matcher.py:match_word', 'STEP 2: Starting prefix stripping', {}, 'B')
        # #endregion

        prefixes, stem = self.prefix_detector.identify_prefixes(word)

        # #region agent log
        debug_log('word_matcher.py:match_word', 'STEP 2: Prefix stripping result', {'prefixes': prefixes, 'stem': stem}, 'B')
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
                debug_log('word_matcher.py:match_word', 'STEP 4: Composite preposition match found', {'prefixes': prefixes, 'suffix': suffix}, 'D')
                # #endregion
                return self.formatter.format_word_result(word, None, prefixes, suffix)

        # Validate stem after prefix removal
        stem_valid = self._validate_stem(stem)
        # #region agent log
        debug_log('word_matcher.py:match_word', 'STEP 2: Stem validation', {'stem': stem, 'stem_valid': stem_valid}, 'B')
        # #endregion

        if not stem_valid:
            # Prefix detection was likely wrong, log and return null
            # #region agent log
            debug_log('word_matcher.py:match_word', 'STEP 2: Invalid stem, returning null', {'stem': stem}, 'B')
            # #endregion
            self._log_unmatched(word, stem, "invalid stem after prefix removal")
            return self.formatter.format_word_result(word, None, [], None)

        normalized_stem = normalize_for_matching(stem)
        # #region agent log
        debug_log('word_matcher.py:match_word', 'STEP 2: Normalized stem for lookup', {'normalized_stem': normalized_stem}, 'B')
        # #endregion

        strong_number = self.loader.get_strong_number(normalized_stem)
        # #region agent log
        debug_log('word_matcher.py:match_word', 'STEP 2: Stem lookup result', {'normalized_stem': normalized_stem, 'strong_number': strong_number}, 'B')
        # #endregion

        if strong_number:
            # #region agent log
            debug_log('word_matcher.py:match_word', 'STEP 2: Prefix stripping match found', {'strong_number': strong_number, 'prefixes': prefixes}, 'B')
            # #endregion
            return self.formatter.format_word_result(word, strong_number, prefixes, None)

        # STEP 3: Try suffix stripping (BEFORE final form normalization)
        # #region agent log
        debug_log('word_matcher.py:match_word', 'STEP 3: Starting suffix stripping', {'normalized_stem': normalized_stem}, 'C')
        # #endregion

        # Strip suffix on text with nikud removed but finals preserved
        stem_with_finals = strip_nikud(stem)
        stem_no_suffix, suffix_id = strip_suffix(stem_with_finals)
        # #region agent log
        debug_log('word_matcher.py:match_word', 'STEP 3: Suffix stripping result', {'stem_with_finals': stem_with_finals, 'stem_no_suffix': stem_no_suffix, 'suffix_id': suffix_id}, 'C')
        # #endregion

        if suffix_id:
            # Now normalize the stem for lookup
            stem_normalized = normalize_for_matching(stem_no_suffix)
            strong_number = self.loader.get_strong_number(stem_normalized)
            # #region agent log
            debug_log('word_matcher.py:match_word', 'STEP 3: Normalized stem lookup result', {'stem_normalized': stem_normalized, 'strong_number': strong_number}, 'C')
            # #endregion
            if strong_number:
                # #region agent log
                debug_log('word_matcher.py:match_word', 'STEP 3: Suffix stripping match found', {'strong_number': strong_number, 'prefixes': prefixes, 'suffix_id': suffix_id}, 'C')
                # #endregion
                return self.formatter.format_word_result(word, strong_number, prefixes, suffix_id)


        # All strategies failed
        # #region agent log
        debug_log('word_matcher.py:match_word', 'All strategies failed', {'word': word, 'stem': stem, 'normalized_stem': normalized_stem, 'stem_no_suffix': stem_no_suffix}, 'E')
        # #endregion
        self._log_unmatched(word, stem, "no dictionary match")
        # FIX: Don't return prefixes if we couldn't verify the stem
        # If we can't match the stem to a dictionary entry, the prefix detection was likely wrong
        return self.formatter.format_word_result(word, None, [], None)

    def match_word_with_strong(self, word_data: Dict) -> Dict:
        """
        Match a word that already has a Strong's number from SQLite.
        Performs prefix detection and formats the result.

        Args:
            word_data: Dictionary with 'text', 'text_no_nikud', 'strong' keys

        Returns:
            Formatted word dictionary with prefixes
        """
        original_word = word_data['text']  # Preserve original for output
        strong_number = word_data.get('strong')

        # #region agent log
        debug_log('word_matcher.py:match_word_with_strong', 'Processing word with pre-existing Strong number', {'word': original_word, 'strong': strong_number}, 'SQLITE')
        # #endregion

        # Clean word for prefix detection only
        cleaned_word = clean_word_for_processing(original_word)

        # Identify prefixes on the cleaned word
        # Use conservative mode for words without Strong's numbers (less reliable)
        has_strong = strong_number is not None
        prefixes, stem = self.prefix_detector.identify_prefixes(cleaned_word, conservative=not has_strong)

        # #region agent log
        debug_log('word_matcher.py:match_word_with_strong', 'Prefix detection result', {'prefixes': prefixes, 'stem': stem}, 'SQLITE')
        # #endregion

        # Format the result using the ORIGINAL word text and provided Strong's number
        return self.formatter.format_word_result_with_strong(original_word, strong_number, prefixes, stem)

    def _validate_stem(self, stem: str) -> bool:
        """
        Validate stem is reasonable after prefix removal.
        
        Args:
            stem: Stem after prefix removal
            
        Returns:
            True if stem is valid, False otherwise
        """
        if not stem:
            return False
        # Strip nikud to check actual letter count
        clean_stem = strip_nikud(stem)
        return len(clean_stem) >= 2

    def _log_unmatched(self, word: str, stem: str, reason: str):
        """Log unmatched words for debugging"""
        self.unmatched_log.append({
            'word': word,
            'stem': stem,
            'reason': reason
        })

    def get_unmatched_words(self) -> List[Dict]:
        """Get list of unmatched words for logging"""
        return self.unmatched_log.copy()

    def clear_unmatched_log(self):
        """Clear the unmatched words log"""
        self.unmatched_log.clear()
