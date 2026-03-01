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
        ('נות', 'abstract_nun'),   # -un (abstract noun with nun)
        
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
    
    # CRITICAL: Handle hiphil patterns on ORIGINAL stem (before suffix stripping corrupts them)
    # Hiphil perfect: הקטיל -> קטל (remove ה AND middle י)
    # e.g., השלימ -> שלם
    if stem.startswith('ה') and len(stem) >= 5:
        without_he = stem[1:]
        if len(without_he) >= 4 and without_he[2] == 'י':
            reduced = without_he[0] + without_he[1] + without_he[3:]
            candidates.append((reduced, 'hiphil_yod_original'))
    
    # Niphal on ORIGINAL stem: נקטיל -> קטל
    # e.g., נראים -> ראם (but we need ראה)
    if stem.startswith('נ') and len(stem) >= 5:
        without_nun = stem[1:]
        if len(without_nun) >= 4 and without_nun[2] == 'י':
            reduced = without_nun[0] + without_nun[1] + without_nun[3:]
            candidates.append((reduced, 'niphal_yod_original'))
    
    # Handle לה prefix (infinitive with ל + hiphil ה)
    # להעיד (to testify) -> עוד (remove לה, convert י to ו)
    if stem.startswith('לה') and len(stem) >= 5:
        without_lamed_he = stem[2:]  # Remove לה
        candidates.append((without_lamed_he, 'lamed_he_prefix'))
        # Convert י prefix to ו for roots like עוד, ידה
        if len(without_lamed_he) >= 3 and without_lamed_he[0] == 'י':
            converted = 'ו' + without_lamed_he[1:]
            candidates.append((converted, 'lamed_he_yod_to_vav'))
    
    # Handle ל prefix (infinitive)
    # לרמז -> רמז, לשלח -> שלח
    if stem.startswith('ל') and len(stem) >= 4:
        without_lamed = stem[1:]
        candidates.append((without_lamed, 'lamed_infinitive'))
    
    # Handle א prefix (1st person imperfect)
    # אשלח -> שלח
    if stem.startswith('א') and len(stem) >= 4:
        without_aleph = stem[1:]
        candidates.append((without_aleph, 'aleph_1st_person'))
        # Also try with suffix removal
        for suffix in ['הו', 'ו', 'ה', 'י', 'כם', 'כן', 'הם', 'הן']:
            if without_aleph.endswith(suffix) and len(without_aleph) > len(suffix) + 2:
                candidates.append((without_aleph[:-len(suffix)], f'aleph_1st_suffix_{suffix}'))
    
    # Handle ב prefix with ה (like בהיותי -> היה)
    # ב + ה + root + suffix
    if stem.startswith('בה') and len(stem) >= 5:
        without_bet_he = stem[2:]  # Remove בה
        candidates.append((without_bet_he, 'bet_he_prefix'))
        # Also try with suffix removal
        for suffix in ['תי', 'י', 'ו', 'ה', 'כם', 'כן']:
            if without_bet_he.endswith(suffix) and len(without_bet_he) > len(suffix) + 2:
                candidates.append((without_bet_he[:-len(suffix)], f'bet_he_suffix_{suffix}'))
        # Special: היות -> היה (convert ות to ה)
        if without_bet_he.endswith('ות'):
            candidates.append((without_bet_he[:-2] + 'ה', 'bet_he_convert_tav_to_he'))
        # Special: יות -> היה (for היה root)
        if without_bet_he.startswith('יות'):
            candidates.append(('היה', 'bet_he_hayah'))
    
    # Handle לה prefix with י (like להעיד -> עוד)
    # לה + י + root -> remove לה, convert י to ו
    if stem.startswith('לה') and len(stem) >= 5:
        without_lamed_he = stem[2:]  # Remove לה
        candidates.append((without_lamed_he, 'lamed_he_prefix'))
        # Convert י prefix to ו for roots like עוד
        if len(without_lamed_he) >= 3 and without_lamed_he[0] == 'י':
            converted = 'ו' + without_lamed_he[1:]
            candidates.append((converted, 'lamed_he_yod_to_vav'))
        # Hiphil pattern: middle י -> ו (like עיד -> עוד)
        # This handles roots where middle letter is ו in dictionary
        if len(without_lamed_he) >= 3:
            # Try converting middle י to ו
            for i in range(1, len(without_lamed_he) - 1):
                if without_lamed_he[i] == 'י':
                    converted = without_lamed_he[:i] + 'ו' + without_lamed_he[i+1:]
                    candidates.append((converted, f'lamed_he_middle_yod_to_vav_{i}'))
    
    # Handle וי prefix (vav consecutive + hiphil)
    # ויודה -> ידה (remove וי, keep root)
    if stem.startswith('וי') and len(stem) >= 4:
        without_vav_yod = stem[2:]  # Remove וי
        candidates.append((without_vav_yod, 'vav_yod_prefix'))
        # Also try reducing י -> (nothing) for roots like ידה
        if len(without_vav_yod) >= 3 and without_vav_yod[0] == 'י':
            reduced = without_vav_yod[1:]
            candidates.append((reduced, 'vav_yod_yod_reduced'))
        # Also convert ו -> י for roots like ידה
        if len(without_vav_yod) >= 3 and without_vav_yod[0] == 'ו':
            converted = 'י' + without_vav_yod[1:]
            candidates.append((converted, 'vav_yod_vav_to_yod'))
    
    # Handle ו prefix (vav consecutive) - when only ו is stripped
    # ודה -> ידה (convert ו to י for roots like ידה)
    if stem.startswith('ו') and len(stem) >= 3:
        without_vav = stem[1:]
        candidates.append((without_vav, 'vav_prefix'))
        # Convert ו to י for roots like ידה
        if len(without_vav) >= 3 and without_vav[0] == 'ו':
            converted = 'י' + without_vav[1:]
            candidates.append((converted, 'vav_vav_to_yod'))
        # Also try converting first ו to י directly (ודה -> ידה)
        converted_direct = 'י' + stem[1:]
        candidates.append((converted_direct, 'vav_to_yod_direct'))
    
    # Handle יו prefix (yod-vav pattern)
    # יודה -> ידה (remove middle ו)
    if stem.startswith('יו') and len(stem) >= 4:
        without_yod_vav = 'י' + stem[2:]  # Keep י, remove ו
        candidates.append((without_yod_vav, 'yod_vav_reduced'))
        # Also strip suffixes from the reduced form
        for suffix in ['יו', 'ו', 'י', 'ה', 'כם', 'כן', 'הם', 'הן']:
            if without_yod_vav.endswith(suffix) and len(without_yod_vav) > len(suffix) + 2:
                candidates.append((without_yod_vav[:-len(suffix)], f'yod_vav_reduced_suffix_{suffix}'))
    
    # Handle ה prefix followed by י (hiphil infinitive construct)
    # היותי -> היה (יות -> יה, the infinitive of היה)
    if stem.startswith('הי') and len(stem) >= 4:
        # Try היה pattern
        if stem.startswith('היות'):
            candidates.append(('היה', 'hayah_infinitive'))
        # Also try removing ה
        without_he = stem[1:]
        candidates.append((without_he, 'he_yod_prefix'))
    
    # Handle נתת pattern (נתן root with ת instead of ן)
    # נתתמ -> נתן (we gave) - but dictionary has נתנ (final ן normalized to נ)
    if stem.startswith('נתת') and len(stem) >= 4:
        # Replace final ת with נ (normalized form)
        candidates.append(('נתנ', 'natan_tav_to_nun'))
        # Also try stripping suffix first
        for suffix in ['מ', 'ם', 'ן', 'ה', 'ו', 'י', 'כם', 'כן', 'הם', 'הן']:
            if stem.endswith(suffix) and len(stem) > len(suffix) + 2:
                base = stem[:-len(suffix)]
                if base == 'נתת':
                    candidates.append(('נתנ', f'natan_suffix_{suffix}'))
    
    # Handle יולד pattern (ילד root with ו in middle)
    # יולדיו -> ילד (his parents)
    if stem.startswith('יו') and len(stem) >= 4:
        without_vav = 'י' + stem[2:]  # Remove ו after י
        candidates.append((without_vav, 'yod_vav_middle_removed'))
    
    # Handle איזה pattern (אי + זה compound)
    # איזה -> אי (which/what)
    if stem.startswith('אי') and len(stem) >= 3:
        candidates.append(('אי', 'ei_compound'))
        candidates.append(('איז', 'eiz_compound'))
    
    # Handle תחית pattern (ת + חיה - resurrection)
    # תחית -> חיה
    if stem.startswith('תחי'):
        candidates.append(('חיה', 'techiyat_chayah'))
    
    # Handle השד pattern (ה + שד - the demon)
    # השד -> שד
    if stem == 'השד':
        candidates.append(('שד', 'hashed_shed'))
    
    # Handle מתהלכים pattern (hitpael participle)
    # מתהלכים -> הלך (walking)
    if stem.startswith('מתהלכ'):
        candidates.append(('הלך', 'mithalech_halach'))
    
    # Handle המוכסים pattern (ה + מוכסים - tax collectors)
    # המוכסים -> מכס
    if stem.startswith('המוכס'):
        candidates.append(('מכס', 'hamochsim_meches'))
    
    # Handle יקל pattern (י + קל - will be light)
    # יקל -> קל
    if stem == 'יקל':
        candidates.append(('קל', 'yekal_kal'))
    
    # Handle הקיסם pattern (ה + קיסם - diviner)
    # הקיסם -> קסם (convert י to nothing)
    if stem.startswith('הקיס'):
        candidates.append(('קסם', 'hakosem_kesem'))
    
    # Handle אהבתכם pattern (אהבה + כם - your love)
    # אהבתכם -> אהב
    if stem.startswith('אהבת'):
        candidates.append(('אהב', 'ahavatcham_ahav'))
        # Strip suffix
        for suffix in ['כמ', 'כם', 'ה', 'ו', 'י']:
            if stem.endswith(suffix) and len(stem) > len(suffix) + 2:
                base = stem[:-len(suffix)]
                if base == 'אהבת':
                    candidates.append(('אהב', f'ahavat_suffix_{suffix}'))
                elif base == 'אהב':
                    candidates.append(('אהב', f'ahav_suffix_{suffix}'))
    
    # Handle תחי pattern (resurrection - תחיה)
    # תחי -> חיה
    if stem == 'תחי':
        candidates.append(('חיה', 'techi_chayah'))
    
    # Handle מוכס pattern (tax collector)
    # מוכס -> מכס
    if stem.startswith('מוכס'):
        candidates.append(('מכס', 'moches_meches'))
        # Strip suffixes
        for suffix in ['ימ', 'ים', 'י', 'ה', 'ו']:
            if stem.endswith(suffix) and len(stem) > len(suffix) + 2:
                base = stem[:-len(suffix)]
                if base == 'מוכס':
                    candidates.append(('מכס', f'moches_suffix_{suffix}'))
    
    # Handle הקיס pattern (diviner)
    # הקיס -> קסם
    if stem.startswith('הקיס'):
        candidates.append(('קסם', 'hakos_kesem'))
    
    # Handle קיסם pattern (diviner)
    # קיסם -> קסם
    if stem.startswith('קיסמ'):
        candidates.append(('קסם', 'kosam_kesem'))
    
    # Handle קיס pattern (diviner without suffix)
    # קיס -> קסם
    if stem == 'קיס':
        candidates.append(('קסם', 'kis_kesem'))
    
    # Handle יקל pattern (qal imperfect)
    # יקל -> קל
    if stem.startswith('יקל'):
        candidates.append(('קל', 'yekal_kal'))
        # Strip suffixes
        for suffix in ['ו', 'ה', 'י', 'נ', 'ת']:
            if stem.endswith(suffix) and len(stem) > len(suffix) + 1:
                base = stem[:-len(suffix)]
                if base == 'יקל':
                    candidates.append(('קל', f'yekal_suffix_{suffix}'))
    
    # Handle השד pattern (the demon)
    # השד -> שד
    if stem.startswith('השד'):
        candidates.append(('שד', 'hashed_shed'))
    
    # Handle שד pattern (demon)
    if stem == 'שד':
        candidates.append(('שד', 'shed_direct'))
    
    # Handle תהלכ pattern (hitpael of הלך)
    # תהלכ -> הלך
    if stem.startswith('תהלכ'):
        candidates.append(('הלך', 'tehalach_halach'))
    
    # Handle מתהלכ pattern (hitpael participle)
    # מתהלכ -> הלך
    if stem.startswith('מתהלכ'):
        candidates.append(('הלך', 'mithalech_halach'))
        # Strip suffixes
        for suffix in ['ימ', 'ים', 'י', 'ה', 'ו']:
            if stem.endswith(suffix) and len(stem) > len(suffix) + 4:
                base = stem[:-len(suffix)]
                if base == 'מתהלכ':
                    candidates.append(('הלך', f'mithalech_suffix_{suffix}'))
    
    # Handle תחית pattern (resurrection)
    # תחית -> חיה
    if stem.startswith('תחית'):
        candidates.append(('חיה', 'techiyat_chayah'))
    
    # Handle תחי pattern (resurrection)
    # תחי -> חיה
    if stem == 'תחי':
        candidates.append(('חיה', 'techi_chayah'))
    
    # Handle אהבת pattern (love construct)
    # אהבת -> אהב
    if stem.startswith('אהבת'):
        candidates.append(('אהב', 'ahavat_ahav'))
        # Strip suffixes
        for suffix in ['כמ', 'כם', 'הנ', 'ה', 'ו', 'י']:
            if stem.endswith(suffix) and len(stem) > len(suffix) + 2:
                base = stem[:-len(suffix)]
                if base == 'אהבת':
                    candidates.append(('אהב', f'ahavat_suffix_{suffix}'))
    
    # Handle אהב pattern (love)
    if stem == 'אהב':
        candidates.append(('אהב', 'ahav_direct'))
    
    # Handle מכס pattern (tax)
    if stem.startswith('מכס'):
        candidates.append(('מכס', 'meches_direct'))
    
    # Handle מוכס pattern (tax collector)
    # מוכס -> מכס
    if stem.startswith('מוכס'):
        candidates.append(('מכס', 'moches_meches'))
    
    # Handle קל pattern (light)
    if stem == 'קל':
        candidates.append(('קל', 'kal_direct'))
    
    # Handle קסם pattern (divination)
    if stem.startswith('קסמ'):
        candidates.append(('קסם', 'kesem_direct'))
    
    # Handle קיסם pattern (diviner)
    # קיסם -> קסם
    if stem.startswith('קיסמ'):
        candidates.append(('קסם', 'kosam_kesem'))
    
    # Handle הלך pattern (walk)
    if stem.startswith('הלכ'):
        candidates.append(('הלך', 'halach_direct'))
    
    # Handle חיה pattern (live)
    if stem.startswith('חיה'):
        candidates.append(('חיה', 'chayah_direct'))
    
    # Handle חי pattern (live)
    if stem == 'חי':
        candidates.append(('חיה', 'chi_chayah'))
    
    # Handle שד pattern (demon)
    if stem == 'שד':
        candidates.append(('שד', 'shed_direct'))
    
    # Handle תרגום pattern (תרגם root with ו in middle)
    # תרגומו -> תרגם (his translation)
    if 'תרגומ' in stem:
        candidates.append(('תרגם', 'targum_vav_removed'))
    
    # Handle תורת pattern (תורה root with ת instead of ה)
    # תורתכם -> תורה (your law)
    if 'תורת' in stem:
        candidates.append(('תורה', 'torah_tav_to_he'))
    
    # Handle שערות pattern (שער root with ות suffix)
    # שערותיה -> שער (her hairs)
    if 'שערות' in stem:
        candidates.append(('שער', 'searot_to_sear'))
    
    # Handle חזו pattern (חזה root with ו instead of ה)
    # תחזוני -> חזה (see me)
    if 'חזו' in stem:
        candidates.append(('חזה', 'chazah_vav_to_he'))
    
    # Handle מצאנ pattern (מצא root with נ suffix)
    # תמצאנני -> מצא (find me)
    if 'מצאנ' in stem:
        candidates.append(('מצא', 'matsa_n_suffix'))
    
    # Handle ה prefix (hiphil) with suffix removal
    # הושם -> שים (but שים not in dict), הצלב -> צלב (not in dict)
    if stem.startswith('ה') and len(stem) >= 4:
        without_he = stem[1:]
        candidates.append((without_he, 'he_hiphil'))
        # Also try with suffix removal
        for suffix in ['ו', 'ה', 'י', 'כם', 'כן', 'הם', 'הן', 'מ']:
            if without_he.endswith(suffix) and len(without_he) > len(suffix) + 2:
                candidates.append((without_he[:-len(suffix)], f'he_hiphil_suffix_{suffix}'))
        # Hiphil infinitive: העיד -> עוד (convert middle י to ו)
        # This handles hiphil forms where middle letter is ו in dictionary
        if len(without_he) >= 3:
            for i in range(1, len(without_he) - 1):
                if without_he[i] == 'י':
                    converted = without_he[:i] + 'ו' + without_he[i+1:]
                    candidates.append((converted, f'hiphil_middle_yod_to_vav_{i}'))
    
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
    
    # Handle hitpael forms with תצ prefix
    # תצטרכו (you need) -> טרכו -> טרך (but root is צרך!)
    # The ת in hitpael can be part of root - just remove תצ and try
    if stem.startswith('תצ') and len(stem) >= 5:
        base = stem[2:]  # Remove תצ
        candidates.append((base, 'hitpael_tzade_prefix'))
        # Also try converting ט -> צ for roots like צרך
        if base.startswith('ט') and len(base) >= 3:
            # Without suffix
            if len(base) >= 3:
                candidates.append(('צ' + base[1:-1], 'hitpael_tzade_tav_to_tsade_no_suffix'))
            # With suffix removed
            if base.endswith('ו'):
                tsade_form = 'צ' + base[1:-1]  # Remove last char (ו)
                candidates.append((tsade_form, 'hitpael_tzade_tav_to_tsade_suffix'))
    
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
    
    # Handle hitpael forms with תצ prefix (2nd person)
    # תצטרכו (you need) -> צרכ (remove תצ and suffix)
    if stem.startswith('תצ') and len(stem) >= 5:
        base = stem[2:]  # Remove תצ
        candidates.append((base, 'hitpael_tzade'))
        for suffix in ['נו', 'ו', 'ה', 'י', 'כם', 'כן', 'הם', 'הן', 'כמ']:
            if base.endswith(suffix) and len(base) > len(suffix) + 2:
                candidates.append((base[:-len(suffix)], f'hitpael_tzade_suffix_{suffix}'))
    
    # Handle ו prefix (vav consecutive - converted hiphil)
    # ויודה (and he thanked) -> יודה -> ידה
    if stem.startswith('וי') and len(stem) >= 4:
        without_vav_yod = stem[2:]  # Remove וי
        candidates.append((without_vav_yod, 'vav_hiphil_converted'))
        # Also try reducing י -> (nothing) for roots like ידה
        if len(without_vav_yod) >= 3 and without_vav_yod[0] == 'י':
            reduced = without_vav_yod[1:]
            candidates.append((reduced, 'vav_hiphil_yod_reduced'))
        # Also convert י prefix to ו for roots like עוד
        if len(without_vav_yod) >= 3 and without_vav_yod[0] == 'י':
            converted = 'ו' + without_vav_yod[1:]
            candidates.append((converted, 'vav_hiphil_yod_to_vav'))
    
    # Handle הו prefix (hophal)
    # הוציאו (they were caused to go out) -> יצא (remove הו, convert ציא to יצא)
    if stem.startswith('הו') and len(stem) >= 5:
        without_he_vav = stem[2:]  # Remove הו
        candidates.append((without_he_vav, 'hophal'))
        # Convert ציא -> יצא for roots like יצא
        if without_he_vav.startswith('ציא'):
            converted = 'יצא'
            candidates.append((converted, 'hophal_tzade_to_yod_tzade'))
    
    # Handle ונ prefix (vav + niphal)
    # ונרא (and we saw) -> נרא -> ראה
    if stem.startswith('ונ') and len(stem) >= 4:
        without_vavnun = stem[2:]  # Remove ונ
        candidates.append((without_vavnun, 'vav_niphal'))
        # Also try niphal transformation on result
        if without_vavnun.startswith('נ') and len(without_vavnun) > 3:
            candidates.append((without_vavnun[1:], 'vav_niphal_niphal'))
        # Also try adding ה for roots ending with ה (like ראה)
        candidates.append((without_vavnun + 'ה', 'vav_niphal_he_added'))
    
    # Handle ל prefix with ה (like להעיד -> to testify)
    # ל + ה + root -> remove ל, then hiphil
    if stem.startswith('לה') and len(stem) >= 5:
        without_lamed = stem[1:]  # Remove ל
        candidates.append((without_lamed, 'lamed_he_removed'))
        # Then try hiphil transformation on result
        if without_lamed.startswith('ה') and len(without_lamed) > 3:
            without_he = without_lamed[1:]
            candidates.append((without_he, 'lamed_he_removed_hiphil'))
    
    # Handle ל prefix with י followed by ו (like ליורש -> ירש)
    # This is ל + infinitive where י is actually י prefix
    if stem.startswith('לי') and len(stem) >= 5:
        without_lamed = stem[1:]  # Remove ל only
        candidates.append((without_lamed, 'lamed_removed'))
        # Then try reducing ו -> י
        if without_lamed[1] == 'ו':
            reduced = without_lamed[0] + without_lamed[2:]
            candidates.append((reduced, 'lamed_removed_yod_reduced'))
    
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
        
        # CRITICAL: Hiphil participle pattern מקטיל -> קטל (remove מ AND middle י)
        # e.g., מקריב -> קרב, מבטיח -> בטח
        # Pattern: מ + Q + R + י + L -> Q + R + L (remove מ and י)
        if base_stem.startswith('מ') and len(base_stem) >= 4:
            without_mem = base_stem[1:]
            # Check for י at position 2 (between 2nd and 3rd root letters)
            if len(without_mem) >= 3 and without_mem[2] == 'י':
                reduced = without_mem[0] + without_mem[1] + without_mem[3:]
                candidates.append((reduced, 'hiphil_participle_yod'))
        
        # CRITICAL: Niphal pattern נקטיל -> קטל (remove נ AND middle י)
        # e.g., נחזיק -> חזק, נקריב -> קרב
        if base_stem.startswith('נ') and len(base_stem) >= 4:
            without_nun = base_stem[1:]
            # Check for י at position 2
            if len(without_nun) >= 3 and without_nun[2] == 'י':
                reduced = without_nun[0] + without_nun[1] + without_nun[3:]
                candidates.append((reduced, 'niphal_yod'))
        
        # CRITICAL: Hiphil perfect pattern הקטיל -> קטל (remove ה AND middle י)
        # e.g., השלימ -> שלם, הרעיש -> רעש
        if base_stem.startswith('ה') and len(base_stem) >= 4:
            without_he = base_stem[1:]
            # Check for י at position 2
            if len(without_he) >= 3 and without_he[2] == 'י':
                reduced = without_he[0] + without_he[1] + without_he[3:]
                candidates.append((reduced, 'hiphil_yod'))
        
        # CRITICAL: Definite article + participle המקטיל -> קטל
        # e.g., המקריבים -> קרב (remove המ AND middle י)
        if base_stem.startswith('המ') and len(base_stem) >= 5:
            without_hem = base_stem[2:]
            # Check for י at position 2
            if len(without_hem) >= 3 and without_hem[2] == 'י':
                reduced = without_hem[0] + without_hem[1] + without_hem[3:]
                candidates.append((reduced, 'def_art_participle_yod'))
        
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
        
        # For stems starting with לי (like ליורש -> ירש)
        if base_stem.startswith('לי') and len(base_stem) >= 4:
            # ליורש -> ירש (remove ל and reduce ו)
            without_lamed_yod = base_stem[2:]
            candidates.append((without_lamed_yod, 'lamed_yod_removed'))
            # Also try with holem reduction: ליורש -> ירש (remove לי, then reduce ו)
            if len(without_lamed_yod) >= 3 and without_lamed_yod[1] == 'ו':
                reduced = without_lamed_yod[0] + without_lamed_yod[2:]
                candidates.append((reduced, 'lamed_yod_holem'))
        
        # For stems starting with ונו (like ונושא -> נשא)
        if base_stem.startswith('ונו') and len(base_stem) >= 5:
            candidates.append((base_stem[3:], 'vav_nun_vav_removed'))  # ונושא -> שא
            candidates.append(('נ' + base_stem[3:], 'vav_nun_vav_to_nun'))  # ונושא -> נשא
        
        # For niphal participle with ים suffix (like נראים -> ראה)
        if base_stem.startswith('נרא') and len(base_stem) >= 5:
            candidates.append(('ראה', 'niphal_participle_yod'))  # נראים -> ראה
        
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