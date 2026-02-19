"""
Deterministic lookup for pronominal suffix forms in Hebrew.

This module handles prepositions with pronominal suffixes that the AI
consistently misidentifies. The correct approach is to NOT assign any
Strong's number to these forms - they should be handled by the API
or left as null.

The Hebrew prepositions ב, ל, מ, כ do NOT have separate Strong's numbers
in the traditional Strong's concordance - they're handled as prefixes.
The pronominal suffixes (like כם = "you pl") also don't have separate
Strong's numbers.

So for forms like בָּכֶם ("in you"), we should:
- Keep the prefix in the "prefixes" array
- NOT assign any Strong's number (return None)
- Let the API or corpus handle it correctly
"""

import re
from typing import Optional, Tuple

# Hebrew letter codepoints
_HEBREW_LETTERS = set(range(0x05D0, 0x05EB))

def _normalize(text: str) -> str:
    """Extract consonant letters only."""
    return ''.join(c for c in text if ord(c) in _HEBREW_LETTERS)


# Prepositions - these don't have separate Strong's numbers in Hebrew!
# Return None to let the API handle them correctly
PREPOSITION_STRONGS = {
    'ב': None,   # בְּ - in, with, by - NO separate Strong's
    'ל': None,  # לְ - to, for, belonging to - NO separate Strong's
    'מ': None,  # מִן - from, out of - NO separate Strong's
    'כ': None,  # כְּ - as, like, according to - NO separate Strong's
}

# Pronominal suffix patterns and their person/number/gender
# These don't have separate Strong's numbers - they're suffixes on the preposition
PRONOMINAL_SUFFIXES = {
    # Singular
    'י': '1cs',    # me (1st person common singular)
    'ך': '2ms',    # you (2nd person masculine singular)
    'ךְ': '2fs',   # you (2nd person feminine singular)
    'ו': '3ms',    # him/it (3rd person masculine singular)
    'הּ': '3fs',   # her/it (3rd person feminine singular)
    
    # Plural
    'נוּ': '1cp',  # us (1st person common plural)
    'כֶם': '2mp',  # you (2nd person masculine plural)
    'כֶן': '2fp',  # you (2nd person feminine plural)
    'ם': '3mp',    # them (3rd person masculine plural)
    'ן': '3fp',    # them (3rd person feminine plural)
    
    # Variant forms with vowel letters
    'ךָ': '2ms',
    'הוּ': '3ms',
    'הָ': '3fs',
    'כָם': '2mp',
    'כָן': '2fp',
    'מוֹ': '3mp',
    'מוֹהֶם': '3mp',
    'מוֹהֶן': '3fp',
}


def is_pronominal_form(word: str, prefixes: list) -> bool:
    """
    Check if a word is a preposition with pronominal suffix.
    
    Args:
        word: Hebrew word text (with nikud)
        prefixes: List of prefix codes already identified
        
    Returns:
        True if this is a prepositional form with pronominal suffix
    """
    # Normalize to consonants only
    consonants = _normalize(word)
    
    # If it has a preposition prefix already identified, check the stem
    if prefixes:
        # Check if first prefix is a preposition
        first_prefix = prefixes[0] if prefixes else None
        if first_prefix in ('Hb', 'Hl', 'Hm', 'Hk'):
            # The stem after the preposition should be a pronominal suffix
            stem = consonants[1:] if len(consonants) > 1 else ''
            if stem in PRONOMINAL_SUFFIXES:
                return True
    
    # Check pattern: single letter preposition + suffix pattern
    if len(consonants) >= 2:
        first_letter = consonants[0]
        rest = consonants[1:]
        if first_letter in 'בלמכ' and rest in PRONOMINAL_SUFFIXES:
            return True
    
    return False


def lookup_pronominal(word: str, prefixes: list) -> Optional[str]:
    """
    Look up the Strong's number for a preposition with pronominal suffix.
    
    IMPORTANT: Hebrew prepositions and pronominal suffixes do NOT have
    separate Strong's numbers. We return None to let the API handle
    these forms correctly.
    
    Args:
        word: Hebrew word text (with nikud)
        prefixes: List of prefix codes already identified
        
    Returns:
        None - pronominal forms don't have separate Strong's numbers
        The API should handle these correctly.
    """
    consonants = _normalize(word)
    
    # Check if it's a pronominal form
    if not is_pronominal_form(word, prefixes):
        return None
    
    # Return None - these forms don't have separate Strong's numbers
    # Let the API handle them correctly
    return None


def get_pronominal_info(word: str, prefixes: list) -> Optional[Tuple[str, str]]:
    """
    Get information about the pronominal form.
    
    Args:
        word: Hebrew word text (with nikud)
        prefixes: List of prefix codes already identified
        
    Returns:
        Tuple of (description) or None - no Strong's number is assigned
    """
    if not is_pronominal_form(word, prefixes):
        return None
    
    consonants = _normalize(word)
    
    # Determine description
    if prefixes and prefixes[0] in ('Hb', 'Hl', 'Hm', 'Hk'):
        prefix_map = {'Hb': 'ב', 'Hl': 'ל', 'Hm': 'מ', 'Hk': 'כ'}
        prep = prefix_map.get(prefixes[0], '?')
        stem = consonants[1:] if len(consonants) > 1 else ''
        suffix_desc = PRONOMINAL_SUFFIXES.get(stem, 'unknown')
        description = f"{prep} + {suffix_desc} suffix (no Strong's number)"
    else:
        # Pattern match
        if len(consonants) >= 2:
            first_letter = consonants[0]
            rest = consonants[1:]
            prefix_map = {'ב': 'ב', 'ל': 'ל', 'מ': 'מ', 'כ': 'כ'}
            prep = prefix_map.get(first_letter, '?')
            suffix_desc = PRONOMINAL_SUFFIXES.get(rest, 'unknown')
            description = f"{prep} + {suffix_desc} suffix (no Strong's number)"
        else:
            description = f"preposition + suffix: {consonants} (no Strong's number)"
    
    return (description,)
# End of pronominal_lookup.py
