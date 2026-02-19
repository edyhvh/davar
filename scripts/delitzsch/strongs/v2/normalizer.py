"""
Hebrew text normalization utilities.

Handles stripping of niqqud (vowel points), cantillation marks, and normalization
of Hebrew word forms for dictionary matching.
"""

import re
from typing import List, Tuple, Optional

from .config import HEBREW_LETTERS, PREFIX_MAP, PREPOSITION_LETTERS, PRONOMINAL_SUFFIXES


def strip_niqqud(text: str) -> str:
    """
    Remove all non-consonant characters from Hebrew text.
    Keeps only Hebrew letters (U+05D0 to U+05EA).
    """
    return ''.join(c for c in text if ord(c) in HEBREW_LETTERS)


def normalize_hebrew(text: str) -> str:
    """
    Normalize Hebrew text for dictionary matching.
    
    1. Strip niqqud and cantillation marks
    2. Normalize final forms (e.g., מ vs ם)
    
    Args:
        text: Hebrew text with or without niqqud
        
    Returns:
        Normalized consonant string
    """
    # First strip all non-consonants
    consonants = strip_niqqud(text)
    
    # Normalize final letter forms to regular forms
    # This is important because dictionary lemmas use regular forms
    final_to_regular = {
        'ך': 'כ',  # final kaf -> kaf
        'ם': 'מ',  # final mem -> mem
        'ן': 'נ',  # final nun -> nun
        'ף': 'פ',  # final pe -> pe
        'ץ': 'צ',  # final tsadi -> tsadi
    }
    
    result = []
    for char in consonants:
        result.append(final_to_regular.get(char, char))
    
    return ''.join(result)


def normalize_final_forms(text: str) -> str:
    """
    Specifically normalize final letter forms to regular forms.
    This is needed for suffix matching.
    """
    final_to_regular = {
        'ך': 'כ',
        'ם': 'מ', 
        'ן': 'נ',
        'ף': 'פ',
        'ץ': 'צ',
    }
    result = []
    for char in text:
        result.append(final_to_regular.get(char, char))
    return ''.join(result)


def strip_prefixes(consonants: str, prefixes: List[str]) -> str:
    """
    Remove prefix consonants from the word stem.
    
    Args:
        consonants: Normalized consonant string
        prefixes: List of prefix codes (e.g., ['Hb', 'Hd'])
        
    Returns:
        Stem with prefix consonants removed
    """
    if not prefixes:
        return consonants
    
    # Count how many prefix consonants to remove
    num_prefixes = len(prefixes)
    
    # Remove prefix consonants from the start
    if len(consonants) > num_prefixes:
        return consonants[num_prefixes:]
    
    return consonants


def detect_pronominal_suffix(consonants: str) -> Tuple[Optional[str], str]:
    """
    Detect if the word ends with a pronominal suffix.
    
    Args:
        consonants: Normalized consonant string
        
    Returns:
        Tuple of (suffix_type, stem_without_suffix) or (None, original)
    """
    # Check for longer suffixes first
    for suffix in sorted(PRONOMINAL_SUFFIXES.keys(), key=len, reverse=True):
        if consonants.endswith(suffix):
            stem = consonants[:-len(suffix)]
            if stem:  # Make sure there's something left
                return PRONOMINAL_SUFFIXES[suffix], stem
    
    return None, consonants


def is_pronominal_form(word: str, prefixes: List[str]) -> bool:
    """
    Check if a word is a preposition with pronominal suffix.
    
    Args:
        word: Hebrew word text (with niqqud)
        prefixes: List of prefix codes
        
    Returns:
        True if this is a prepositional form with pronominal suffix
    """
    consonants = normalize_hebrew(word)
    
    # If it has a preposition prefix already identified
    if prefixes:
        first_prefix = prefixes[0]
        if first_prefix in ('Hb', 'Hl', 'Hm', 'Hk'):
            # The stem after the preposition should be a pronominal suffix
            stem = consonants[1:] if len(consonants) > 1 else ''
            if stem in PRONOMINAL_SUFFIXES:
                return True
    
    # Check pattern: single letter preposition + suffix pattern
    if len(consonants) >= 2:
        first_letter = consonants[0]
        rest = consonants[1:]
        if first_letter in PREPOSITION_LETTERS and rest in PRONOMINAL_SUFFIXES:
            return True
    
    return False


def extract_stem(word: str, prefixes: List[str]) -> str:
    """
    Extract the core stem from a Hebrew word, removing prefixes and suffixes.
    
    Args:
        word: Hebrew word text (with niqqud)
        prefixes: List of prefix codes
        
    Returns:
        Normalized stem suitable for dictionary lookup
    """
    # Normalize first
    consonants = normalize_hebrew(word)
    
    # Strip prefixes
    stem = strip_prefixes(consonants, prefixes)
    
    # Detect and remove pronominal suffix
    suffix_type, stem_without_suffix = detect_pronominal_suffix(stem)
    
    return stem_without_suffix


def get_possible_stems(word: str, prefixes: List[str]) -> List[str]:
    """
    Get all possible stems for matching, ordered by likelihood.
    
    Args:
        word: Hebrew word text (with niqqud)
        prefixes: List of prefix codes
        
    Returns:
        List of possible stem variations
    """
    consonants = normalize_hebrew(word)
    stems = []
    
    # Primary stem: with prefixes stripped
    primary = strip_prefixes(consonants, prefixes)
    if primary:
        stems.append(primary)
    
    # Secondary: without suffix removal (for exact matches)
    if primary not in stems:
        stems.append(consonants)
    
    # Tertiary: try with only some prefixes removed
    if len(prefixes) > 1:
        partial = strip_prefixes(consonants, prefixes[:-1])
        if partial and partial not in stems:
            stems.append(partial)
    
    # CRITICAL FIX: When prefix includes "Hd" (definite article ה),
    # also try the FULL word WITH the prefix - many dictionary entries
    # include the definite article as part of the lemma
    if 'Hd' in prefixes:
        if consonants not in stems:
            stems.append(consonants)
        # Also try with just the definite article
        if consonants.startswith('ה') and consonants not in stems:
            stems.append(consonants)
    
    return stems


def strip_suffixes(stem: str) -> List[Tuple[str, str]]:
    """
    Strip common Hebrew suffixes and return possible base forms.
    
    Returns:
        List of tuples (base_form, suffix_type)
    """
    if len(stem) < 3:
        return [(stem, 'none')]
    
    results = []
    
    # Define suffix patterns from longest to shortest
    # Use regular forms (not final forms) for matching
    suffix_patterns = [
        # Complex pronominal suffixes (longest first)
        ('תיכם', 'suffix_2mp_fem'),  # -tikhem (you, masc pl, with fem noun ending)
        ('תיכן', 'suffix_2fp_fem'),  # -tikhen (you, fem pl, with fem noun ending)
        ('תיו', 'suffix_3ms_fem'),    # -tyo (his, with fem noun ending)
        ('תיה', 'suffix_3fs_fem'),    # -tyah (her, with fem noun ending)
        ('תינו', 'suffix_1cp_fem'),   # -tinu (our, with fem noun ending)
        ('תיך', 'suffix_2ms_fem'),    # -tikha (you masc, with fem noun ending)
        ('תיךְ', 'suffix_2ms_fem'),   # -tikha (with dagesh)
        
        # Full possessive chains (ת + י + suffix)
        ('תיכמ', 'suffix_2mp_fem_chain'),  # נפשתיכמ -> נפש
        
        # Plural/collective endings (most common)
        ('ים', 'plural_masc'),      # -im (masculine plural) - yod+regular mem
        ('ימ', 'plural_masc'),      # -ym (alternative form with final mem)
        ('ות', 'plural_fem'),       # -ot (feminine plural)
        
        # Pronominal suffixes (longer first)
        ('תמ', 'suffix_2mp'),       # -tem (you, masc pl) - for hiphil/hitpael forms
        ('תן', 'suffix_2fp'),       # -ten (you, fem pl)
        ('כם', 'suffix_2mp'),       # -khem (you, masc pl) - with regular mem
        ('כמ', 'suffix_2mp'),       # -khem with final mem
        ('כן', 'suffix_2fp'),       # -khen (you, fem pl)
        ('הם', 'suffix_3mp'),       # -hem (them, masc) - with regular mem
        ('המ', 'suffix_3mp'),       # -hem with final mem
        ('הן', 'suffix_3fp'),       # -hen (them, fem)
        ('נו', 'suffix_1cp'),       # -nu (us) - with regular vav
        ('רם', 'suffix_3mp'),       # -ram (them, masc) - for forms like שמרם
        ('רן', 'suffix_3fp'),       # -ren (them, fem)
        
        # Special: handle 3ms suffix on roots ending with ר (like שמר)
        # The רם/רן patterns above should catch these
        ('ך', 'suffix_2ms'),        # -kha (you, masc sg)
        ('ו', 'suffix_3ms'),        # -o (him/it) - with regular vav
        ('ה', 'suffix_3fs'),        # -ah (her/it)
        ('י', 'suffix_1cs'),        # -i (my/me)
        
        # Feminine singular endings
        ('ה', 'fem_sing'),          # -ah (feminine singular)
        ('ת', 'fem_sing_action'),   # -et (feminine action noun)
        
        # Abstract/quality endings
        ('ות', 'abstract'),         # -ut (abstract noun)
        
        # Participle/adjective endings
        ('י', 'adj_masc'),          # -i (adjective/participle form)
    ]
    
    # Try each suffix pattern
    for suffix, suffix_type in suffix_patterns:
        if stem.endswith(suffix):
            base = stem[:-len(suffix)]
            # Keep at least 2 letters for a valid root
            if len(base) >= 2:
                results.append((base, suffix_type))
    
    # If no suffixes found, return original
    if not results:
        results.append((stem, 'none'))
    
    return results


def extract_root_candidates(stem: str) -> List[Tuple[str, str]]:
    """
    Extract possible root candidates from a stem by removing various affixes.
    
    Returns:
        List of tuples (candidate, transformation_type)
    """
    candidates = [(stem, 'original')]
    
    # Get suffix-stripped forms
    suffix_forms = strip_suffixes(stem)
    candidates.extend(suffix_forms)
    
    # CRITICAL FIX: Also run binyan transformations on the ORIGINAL stem
    # before suffix stripping, because suffix stripping may remove important letters
    # e.g., מנסה -> suffix strip -> מנס (3 chars) fails len check
    # but מנסה (4 chars) should work with מנ->נ transformation
    
    # Handle מנ/ינ patterns on ORIGINAL stem
    if stem.startswith('מנ') and len(stem) >= 4:
        candidates.append((stem[1:], 'niphal_participle'))  # מנסה -> נסה
    if stem.startswith('ינ') and len(stem) >= 4:
        candidates.append((stem[1:], 'hiphil_participle'))  # ינסה -> נסה
    if stem.startswith('מי') and len(stem) >= 4:
        candidates.append((stem[1:], 'hiphil_participle_alt'))  # מיסה -> יסה
    
    # Handle יו patterns (like שנוי -> שנה)
    # שנוי (change) = שנה (root) + ו + י suffix
    if len(stem) >= 4 and stem.endswith('וי'):
        # שנוי -> שנה
        candidates.append((stem[:-2] + 'ה', 'yod_vav_reduced'))
    
    # CRITICAL: Handle hitpael forms with נת prefix (1st person)
    # נתחברנו (we joined) -> חברנו -> חבר (strip suffix)
    # נתודה (we will confess) -> ודה -> ידה (needs yod)
    if stem.startswith('נת') and len(stem) >= 5:
        base = stem[2:]  # Remove נת
        candidates.append((base, 'hitpael_1st'))
        # Also try stripping suffixes from the base
        for suffix in ['נו', 'ו', 'ה', 'י', 'כם', 'כן', 'הם', 'הן']:
            if base.endswith(suffix) and len(base) > len(suffix) + 2:
                candidates.append((base[:-len(suffix)], f'hitpael_1st_suffix_{suffix}'))
        # Special case: ודה -> ידה (vav -> yod conversion for hitpael)
        if base.startswith('ו'):
            candidates.append(('י' + base[1:], 'hitpael_1st_vav_to_yod'))  # ודה -> ידה
    
    # Handle hitpael forms with תת prefix (2nd person)
    # תתחברו (you will join) -> חברו -> חבר
    if stem.startswith('תת') and len(stem) >= 5:
        base = stem[2:]  # Remove תת
        candidates.append((base, 'hitpael_2nd'))
        for suffix in ['נו', 'ו', 'ה', 'י', 'כם', 'כן', 'הם', 'הן']:
            if base.endswith(suffix) and len(base) > len(suffix) + 2:
                candidates.append((base[:-len(suffix)], f'hitpael_2nd_suffix_{suffix}'))
    
    # Handle hitpael forms with ית prefix (3rd person masculine)
    # יתחבר (he will join) -> חבר
    if stem.startswith('ית') and len(stem) >= 4:
        base = stem[2:]  # Remove ית
        candidates.append((base, 'hitpael_3ms'))
        for suffix in ['נו', 'ו', 'ה', 'י', 'כם', 'כן', 'הם', 'הן']:
            if base.endswith(suffix) and len(base) > len(suffix) + 2:
                candidates.append((base[:-len(suffix)], f'hitpael_3ms_suffix_{suffix}'))
    
    # Handle hitpael forms with נת prefix followed by ה
    # נתהלך (we will walk) -> הלך
    if stem.startswith('נתה') and len(stem) >= 5:
        base = stem[3:]  # Remove נתה
        candidates.append((base, 'hitpael_with_he'))
        for suffix in ['נו', 'ו', 'ה', 'י', 'כם', 'כן', 'הם', 'הן']:
            if base.endswith(suffix) and len(base) > len(suffix) + 2:
                candidates.append((base[:-len(suffix)], f'hitpael_he_suffix_{suffix}'))
    
    # For each suffix-stripped form, also try binyan transformations
    for base_stem, suffix_type in suffix_forms:
        if suffix_type == 'none':
            base_stem = stem
        
        # Remove hitpael prefix (הת)
        if base_stem.startswith('הת') and len(base_stem) > 4:
            candidates.append((base_stem[2:], 'hitpael'))
        
        # Remove niphal prefix (נ)
        if base_stem.startswith('נ') and len(base_stem) > 3:
            candidates.append((base_stem[1:], 'niphal'))
        
        # Remove hiphil prefix (ה)
        if base_stem.startswith('ה') and len(base_stem) > 3:
            candidates.append((base_stem[1:], 'hiphil'))
        
        # Remove hophal prefix (הו)
        if base_stem.startswith('הו') and len(base_stem) > 4:
            candidates.append((base_stem[2:], 'hophal'))
        
        # Remove puul/pual prefix (מ)
        if base_stem.startswith('מ') and len(base_stem) > 3:
            candidates.append((base_stem[1:], 'puul'))
        
        # Remove participle prefix (מש) for participles like משמר
        if base_stem.startswith('מש') and len(base_stem) > 4:
            candidates.append((base_stem[2:], 'participle'))
        
        # Remove participle prefix (מ) for other participles
        if base_stem.startswith('מ') and len(base_stem) > 3:
            candidates.append((base_stem[1:], 'participle'))
        
        # Piel pattern: XYYZ -> XYZ (reduce doubled middle letter)
        if len(base_stem) >= 4:
            if base_stem[1] == base_stem[2]:
                reduced = base_stem[0] + base_stem[2:]
                candidates.append((reduced, 'piel_reduced'))
        
        # For 4-letter stems that might have prefixes, try removing first letter
        if len(base_stem) == 4:
            candidates.append((base_stem[1:], 'minus_first'))
        
        # For stems ending with ה (feminine), try removing it
        if base_stem.endswith('ה') and len(base_stem) > 3:
            candidates.append((base_stem[:-1], 'minus_final_he'))
        
        # For stems with ו between first and second letter (like אהוב -> אהב)
        if len(base_stem) >= 4 and base_stem[2] == 'ו':
            reduced = base_stem[:2] + base_stem[3:]
            candidates.append((reduced, 'holem_reduced'))
        
        # For stems with י between first and second letter
        if len(base_stem) >= 4 and base_stem[2] == 'י':
            reduced = base_stem[:2] + base_stem[3:]
            candidates.append((reduced, 'hiriq_reduced'))
        
        # CRITICAL: Handle מנ/ינ patterns (nifal/piel participles)
        # מנסה -> נסה (remove מ prefix, reduce נו to נ)
        # ינסה -> נסה (remove י prefix, reduce נו to נ)
        if base_stem.startswith('מנ') and len(base_stem) >= 4:
            # Remove מ and try נסה
            candidates.append((base_stem[1:], 'niphal_participle'))  # מנסה -> נסה
        if base_stem.startswith('ינ') and len(base_stem) >= 4:
            # Remove י and try נסה
            candidates.append((base_stem[1:], 'hiphil_participle'))  # ינסה -> נסה
        
        # For 2-letter stems after suffix removal, try adding vav (e.g., כב -> כוב)
        if len(base_stem) == 2:
            candidates.append((base_stem[0] + 'ו' + base_stem[1], 'added_vav'))
            candidates.append((base_stem[0] + 'י' + base_stem[1], 'added_yod'))
            candidates.append((base_stem + 'ה', 'added_he'))
            # Try adding first letter repeated (e.g., לבד -> בדד)
            candidates.append((base_stem[0] + base_stem, 'doubled_first'))
        
        # For 3-letter stems that might have lost a middle letter
        if len(base_stem) == 3:
            # Try adding vav between first and second
            candidates.append((base_stem[0] + 'ו' + base_stem[1:], 'inserted_vav'))
            # Try adding yod between first and second  
            candidates.append((base_stem[0] + 'י' + base_stem[1:], 'inserted_yod'))
            # For stems starting with ל (like לבד), try removing it
            if base_stem[0] == 'ל':
                candidates.append((base_stem[1:], 'minus_lamed'))
    
    # Deduplicate while preserving order
    seen = set()
    unique_candidates = []
    for candidate, transform in candidates:
        if candidate not in seen and len(candidate) >= 2:
            seen.add(candidate)
            unique_candidates.append((candidate, transform))
    
    return unique_candidates


def normalize_dictionary_lemma(lemma: str) -> str:
    """
    Normalize a dictionary lemma for indexing.
    
    Dictionary lemmas may contain spaces, hyphens, or other formatting.
    We extract just the Hebrew consonants.
    
    Args:
        lemma: Dictionary lemma (e.g., "אֲבִיגַיִל")
        
    Returns:
        Normalized consonant string
    """
    # Strip non-Hebrew characters
    hebrew_only = ''.join(c for c in lemma if ord(c) in HEBREW_LETTERS or c in 'ךםןףץ')
    
    # Normalize final forms
    return normalize_hebrew(hebrew_only)