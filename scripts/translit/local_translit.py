"""
Local rule-based transliteration (no API calls).
"""

from __future__ import annotations

import unicodedata
from typing import Dict, Iterable, List, Tuple

from .models import BatchResult, TransliterationResult, WordItem

DAGESH = "\u05BC"
SHIN_DOT = "\u05C1"
SIN_DOT = "\u05C2"
SHEVA = "\u05B0"
HATAF_SEGOL = "\u05B1"
HATAF_PATAH = "\u05B2"
HATAF_QAMATS = "\u05B3"
HIRIQ = "\u05B4"
TSERE = "\u05B5"
SEGOL = "\u05B6"
PATAH = "\u05B7"
QAMATS = "\u05B8"
HOLAM = "\u05B9"
QUBUTS = "\u05BB"
QAMATS_QATAN = "\u05C7"

VOWEL_MARKS = {
    SHEVA,
    HATAF_SEGOL,
    HATAF_PATAH,
    HATAF_QAMATS,
    HIRIQ,
    TSERE,
    SEGOL,
    PATAH,
    QAMATS,
    HOLAM,
    QUBUTS,
    QAMATS_QATAN,
}

FINAL_MAP = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ",
}

HEBREW_LETTERS = set(
    "אבגדהוזחטיכלמנסעפצקרשת" + "ךםןףץ"
)


def _is_hebrew_letter(ch: str) -> bool:
    return ch in HEBREW_LETTERS


def _is_hebrew_mark(ch: str) -> bool:
    return unicodedata.combining(ch) != 0 and "\u0590" <= ch <= "\u05C7"


def _normalize_word(text: str) -> str:
    return text.replace("/", "").replace("־", "")


def _tokenize(text: str) -> List[Tuple[str, List[str]]]:
    tokens: List[Tuple[str, List[str]]] = []
    for ch in _normalize_word(text):
        if _is_hebrew_letter(ch):
            tokens.append((ch, []))
        elif _is_hebrew_mark(ch) and tokens:
            letter, marks = tokens[-1]
            marks.append(ch)
            tokens[-1] = (letter, marks)
        else:
            continue
    return tokens


def _has_any_vowel(tokens: Iterable[Tuple[str, List[str]]]) -> bool:
    for _, marks in tokens:
        if any(mark in VOWEL_MARKS for mark in marks):
            return True
    return False


def _vowel_from_marks(letter: str, marks: List[str]) -> str:
    mark_set = set(marks)
    if HOLAM in mark_set:
        return "o"
    if QAMATS_QATAN in mark_set:
        return "o"
    if QUBUTS in mark_set:
        return "u"
    if letter == "ו" and DAGESH in mark_set and not (mark_set & (VOWEL_MARKS - {SHEVA})):
        return "u"
    if HIRIQ in mark_set:
        return "i"
    if TSERE in mark_set or SEGOL in mark_set or HATAF_SEGOL in mark_set:
        return "e"
    if PATAH in mark_set or QAMATS in mark_set or HATAF_PATAH in mark_set or HATAF_QAMATS in mark_set:
        return "a"
    if SHEVA in mark_set:
        return "e"
    return ""


def _consonant_for(letter: str, marks: List[str], lang: str, use_vowels: bool) -> str:
    base = FINAL_MAP.get(letter, letter)
    mark_set = set(marks)

    if base == "ש":
        if SHIN_DOT in mark_set:
            return "sh"
        if SIN_DOT in mark_set:
            return "s"
        return "sh"

    if base == "ב":
        return "b" if DAGESH in mark_set else "v"

    if base == "פ":
        return "p" if DAGESH in mark_set else "f"

    if base == "כ":
        if DAGESH in mark_set:
            return "k"
        return "ch" if lang == "en" else "j"

    if base == "ח":
        return "ch" if lang == "en" else "j"

    if base == "צ":
        return "tz"

    if base == "א" or base == "ע":
        return ""

    if base == "ה":
        return "h"

    if base == "ו":
        if use_vowels and (HOLAM in mark_set or (DAGESH in mark_set and not (mark_set & (VOWEL_MARKS - {SHEVA})))):
            return ""
        return "v"

    if base == "י":
        return "y"

    mapping = {
        "ג": "g",
        "ד": "d",
        "ז": "z",
        "ט": "t",
        "ל": "l",
        "מ": "m",
        "נ": "n",
        "ס": "s",
        "ק": "k",
        "ר": "r",
        "ת": "t",
    }
    return mapping.get(base, "")


def _transliterate_tokens(tokens: List[Tuple[str, List[str]]], lang: str, use_vowels: bool) -> str:
    parts: List[str] = []
    for letter, marks in tokens:
        consonant = _consonant_for(letter, marks, lang, use_vowels)
        vowel = _vowel_from_marks(letter, marks) if use_vowels else ""
        parts.append(f"{consonant}{vowel}")

    result = "".join(parts)
    if tokens:
        last_letter = FINAL_MAP.get(tokens[-1][0], tokens[-1][0])
        if last_letter == "ה" and not result.endswith("h"):
            result += "h"
    return result


class LocalTransliterator:
    """Rule-based transliterator (no external API calls)."""

    def transliterate_word(self, text: str) -> TransliterationResult:
        tokens = _tokenize(text)
        use_vowels = _has_any_vowel(tokens)
        translit_en = _transliterate_tokens(tokens, "en", use_vowels)
        translit_es = _transliterate_tokens(tokens, "es", use_vowels)
        return TransliterationResult(translit_en=translit_en, translit_es=translit_es)

    def translate_batch(self, items: List[WordItem]) -> BatchResult:
        results: Dict[str, TransliterationResult] = {}
        for item in items:
            results[item.word_id] = self.transliterate_word(item.text)
        return BatchResult(results=results, input_tokens=0, output_tokens=0)
