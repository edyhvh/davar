"""
Dictionary loading and indexing for Delitzsch Strong's Matcher
"""

import json
from typing import Dict, List, Tuple
from pathlib import Path

from config import WORDS_JSON, ROOTS_JSON, PREFIX_FORMS_JSON, PREFIX_ENTRIES_DIR


class DictionaryLoader:
    """
    Loads and indexes Hebrew dictionaries for fast lookups.
    """

    def __init__(self):
        self.words_by_normalized: Dict[str, str] = {}  # normalized -> H1234
        self.roots_by_normalized: Dict[str, str] = {}  # normalized -> H1234
        self.prefix_forms: Dict[str, List[str]] = {}   # form -> ["Hb"]
        self.prefix_patterns: List[Tuple[str, str]] = []  # [(pattern, id)]
        self.proper_names: set = set()  # Strong's numbers that are proper names

        self._loaded = False

    def load_all(self):
        """Load all dictionary data"""
        if self._loaded:
            return

        print("Loading words dictionary...")
        self._load_words()

        print("Loading roots dictionary...")
        self._load_roots()

        print("Loading prefix data...")
        self._load_prefixes()

        self._loaded = True
        print("Dictionary loading complete.")

    def _load_words(self):
        """Load words.json and build normalized lookup table"""
        if not WORDS_JSON.exists():
            raise FileNotFoundError(f"Words dictionary not found: {WORDS_JSON}")

        with open(WORDS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for strong_num, entry in data.items():
            if 'normalized' in entry:
                normalized = entry['normalized']
                self.words_by_normalized[normalized] = strong_num

            # Detect proper names by capitalized transliteration
            transliteration = entry.get('transliteration', '')
            if transliteration and transliteration[0].isupper():
                self.proper_names.add(strong_num)

        # Add known alternate forms
        ALTERNATE_FORMS = {
            'היא': 'H1931',  # She (alternate of הוא he)
            'יהי': 'H1961',  # Let it be (jussive form)
            'תהיה': 'H1961', # You will be
            'למען': 'H4616', # For the sake of (with prefix)
        }

        self.words_by_normalized.update(ALTERNATE_FORMS)

    def _load_roots(self):
        """Load roots.pretty.json and build normalized lookup table"""
        if not ROOTS_JSON.exists():
            raise FileNotFoundError(f"Roots dictionary not found: {ROOTS_JSON}")

        with open(ROOTS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for strong_num, entry in data.items():
            # Use normalized field if it exists, otherwise create from lemma
            if 'normalized' in entry:
                normalized = entry['normalized']
            elif 'lemma' in entry:
                # Create normalized form from lemma
                normalized = self._normalize_for_matching(entry['lemma'])
            else:
                continue

            self.roots_by_normalized[normalized] = strong_num

    def _normalize_for_matching(self, text):
        """Normalize Hebrew text for dictionary matching (copied from hebrew_utils)"""
        # Import here to avoid circular imports
        import re

        # Unicode ranges for Hebrew nikud (vowel points and accents)
        nikud_pattern = re.compile(r'[\u0591-\u05BD\u05BF-\u05C7]')

        # Hebrew final forms mapping for normalization
        final_forms = {
            '\u05da': '\u05db',  # ך -> כ
            '\u05dd': '\u05de',  # ם -> מ
            '\u05df': '\u05e0',  # ן -> נ
            '\u05e3': '\u05e4',  # ף -> פ
            '\u05e5': '\u05e6',  # ץ -> צ
        }

        # Strip nikud and normalize final forms
        text = nikud_pattern.sub('', text)
        text = ''.join(final_forms.get(char, char) for char in text)
        return text

    def _load_prefixes(self):
        """Load prefix forms and entries"""
        # Load forms_lookup.json
        if PREFIX_FORMS_JSON.exists():
            with open(PREFIX_FORMS_JSON, 'r', encoding='utf-8') as f:
                forms_data = json.load(f)

            # Convert the lookup format to our internal format
            for form, prefixes in forms_data.items():
                self.prefix_forms[form] = prefixes

        # Load prefix entries to understand available prefixes
        if PREFIX_ENTRIES_DIR.exists():
            prefix_files = list(PREFIX_ENTRIES_DIR.glob("*.json"))
            print(f"Found {len(prefix_files)} prefix entry files")

            # We could load the full definitions here if needed
            # For now, we'll just validate that we have the expected prefixes

    def get_strong_number(self, normalized_word: str) -> str:
        """
        Get Strong's number for a normalized Hebrew word.
        First tries words dictionary, then roots.

        Args:
            normalized_word: Normalized Hebrew word (no nikud, normalized finals)

        Returns:
            Strong's number (e.g., "H1234") or None if not found
        """
        # Try words first
        if normalized_word in self.words_by_normalized:
            return self.words_by_normalized[normalized_word]

        # Try roots as fallback
        if normalized_word in self.roots_by_normalized:
            return self.roots_by_normalized[normalized_word]

        return None

    def get_prefixes_for_form(self, form: str) -> List[str]:
        """
        Get prefix IDs for a given form.

        Args:
            form: The Hebrew form to check

        Returns:
            List of prefix IDs (e.g., ["Hb", "Hc"])
        """
        return self.prefix_forms.get(form, [])

    def is_loaded(self) -> bool:
        """Check if dictionaries have been loaded"""
        return self._loaded

    def is_proper_name(self, strong_number: str) -> bool:
        """
        Check if a Strong's number is a proper name.
        Proper names are detected by capitalized transliteration.

        Args:
            strong_number: Strong's number (e.g., "H1141")

        Returns:
            True if the word is a proper name
        """
        # Extract just the Strong's number without prefix codes
        if '/' in strong_number:
            strong_number = strong_number.split('/')[-1]
        return strong_number in self.proper_names


# Singleton instance
_loader_instance = None

def get_dictionary_loader() -> DictionaryLoader:
    """Get singleton dictionary loader instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = DictionaryLoader()
        _loader_instance.load_all()
    return _loader_instance