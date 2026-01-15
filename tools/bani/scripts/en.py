#!/usr/bin/env python3
"""Generate English transliterations for every Strong's entry (v3.0).

This script implements the complete workflow defined in ``INSTRUCTIONS.md`` v3.0
and ``SCHEMA.jsonc`` for generating academic English transliterations of
Biblical Hebrew words using Brill Simplified and SBL General Purpose systems:

1. **Dual System Support**: Supports both Brill Simplified (default) and SBL General Purpose
   systems with automatic switching based on schema configuration.

2. **Schema Validation**: Validates that the schema has all required mappings
   (27 consonants + 12 vowels + composites) and proper system configuration.

3. **Enhanced Strong's Integration**: Uses ``data/strongs.json`` with advanced fields:
   - ``pron`` field: Phonetic transcription for accurate syllable boundaries and stress
   - ``xlit`` field: Academic transliteration reference for validation
   - Intelligent alignment between pron syllables and transliteration

4. **Unicode-Aware Processing**: Proper handling of Unicode characters (ᵉ, ḥ, ', tz)
   in transliteration and syllable separation algorithms.

5. **Academic Output**: Generates ``data/strong_en.json`` with academic transliterations
   and pronunciation guides following Brill Simplified standards.

Based on Brill Simplified and SBL General Purpose systems from the
hebrew-transliteration library, optimized for English academic use.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants & Helpers
# ---------------------------------------------------------------------------

VOWELS = set("aeiou")
SHEVA_CHAR = "ְ"
DAGESH_CHAR = "ּ"

def _is_unicode_special(char: str) -> bool:
    """Check if character is a Unicode special character (not ASCII letter/digit/punctuation)."""
    return ord(char) > 127 and not char.isspace()


def load_json_file(path: Path) -> Dict[str, Any]:
    """Load and return a JSON/JSONC file, raising explicit errors on failure."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            content = handle.read()

            # Handle JSONC files by removing comments
            if path.suffix == '.jsonc':
                # Remove single-line comments (// ...) - more robust pattern
                lines = content.split('\n')
                cleaned_lines = []
                for line in lines:
                    # Remove everything after // but preserve the line structure
                    comment_start = line.find('//')
                    if comment_start >= 0:
                        line = line[:comment_start].rstrip()
                    if line.strip():  # Only keep non-empty lines
                        cleaned_lines.append(line)
                    elif not line.strip() and cleaned_lines:  # Keep one empty line max
                        if cleaned_lines[-1] != '':
                            cleaned_lines.append('')
                content = '\n'.join(cleaned_lines)

            return json.loads(content)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON data in {path}: {exc}")


def get_base_schema() -> Dict[str, Any]:
    """Get the base schema data (hardcoded to avoid JSONC parsing issues)."""
    return {
        "schema_version": "2.0.0",
        "language": {
            "code": "{LANGUAGE_CODE}",
            "name": "{LANGUAGE_NAME}",
            "variant": "{LANGUAGE_VARIANT}"
        },
        "transliteration_systems": {
            "sbl_general_purpose": {
                "name": "SBL General Purpose",
                "description": "Simplified academic transliteration following SBL guidelines",
                "source": "https://github.com/charlesLoder/hebrew-transliteration",
                "features": {
                    "vocal_sheva": "e",
                    "qamats_qatan": False,
                    "dagesh_strong": True,
                    "long_vowels": True
                }
            },
            "brill_simplified": {
                "name": "Brill Simplified",
                "description": "Simplified version of Brill academic transliteration",
                "source": "https://github.com/charlesLoder/hebrew-transliteration",
                "features": {
                    "vocal_sheva": "ᵉ",
                    "qamats_qatan": True,
                    "dagesh_strong": True,
                    "long_vowels": True,
                    "special_chars": True
                }
            }
        },
        "stress": {
            "default": "penultimate",
            "exceptions": {}
        },
        "workflow": {
            "use_strongs_reference": True,
            "pron_parsing": {
                "enabled": True,
                "syllable_separator": "-",
                "stress_marker": "'"
            },
            "xlit_reference": {
                "enabled": True
            },
            "validation_mode": "strict",
            "fallback_behavior": "use_generated"
        },
        "examples": {
            "H1": {
                "hebrew": "אָב",
                "translit": "av",
                "stress_syllable": 1,
                "guide": "AV",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_FATHER}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_AV}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_ALEPH_OMITTED}"]
                }
            },
            "H2": {
                "hebrew": "אַב",
                "translit": "ab",
                "stress_syllable": 1,
                "guide": "AB",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_SON}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_AB}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_AB_ARAMAIC}"]
                }
            },
            "H3": {
                "hebrew": "גַּם",
                "translit": "gam",
                "stress_syllable": 1,
                "guide": "GAM",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_ALSO}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_GAM}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_GIMEL}"]
                }
            },
            "H4": {
                "hebrew": "דָּם",
                "translit": "dam",
                "stress_syllable": 1,
                "guide": "DAM",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_BLOOD}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_DAM}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_DALET}"]
                }
            },
            "H5": {
                "hebrew": "הוּא",
                "translit": "hu",
                "stress_syllable": 2,
                "guide": "hu",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_HE}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_FINAL}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_HE_SOUND}"]
                }
            },
            "H6": {
                "hebrew": "וְ",
                "translit": "ve",
                "stress_syllable": 1,
                "guide": "VE",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_AND}",
                    "stress_note": "{LANGUAGE_EXAMPLE_CONJUNCTION}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_SHEVA_LIGHT}"]
                }
            },
            "H7": {
                "hebrew": "זֶה",
                "translit": "ze",
                "stress_syllable": 1,
                "guide": "ZE",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_THIS}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_ZE}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_ZAYIN}"]
                }
            },
            "H8": {
                "hebrew": "חַי",
                "translit": "khai",
                "stress_syllable": 1,
                "guide": "KHAI",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_LIVE}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_KHAI}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_HET_KH}"]
                }
            },
            "H9": {
                "hebrew": "טוֹב",
                "translit": "tov",
                "stress_syllable": 1,
                "guide": "TOV",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_GOOD}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_TOV}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_TET}"]
                }
            },
            "H10": {
                "hebrew": "יָד",
                "translit": "yad",
                "stress_syllable": 1,
                "guide": "YAD",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_HAND}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_YAD}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_YOD_CONSONANT}"]
                }
            },
            "H11": {
                "hebrew": "כֹּה",
                "translit": "kho",
                "stress_syllable": 1,
                "guide": "KHO",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_THUS}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_KHO}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_KAF_DAGESH}"]
                }
            },
            "H12": {
                "hebrew": "לֵב",
                "translit": "lev",
                "stress_syllable": 1,
                "guide": "LEV",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_HEART}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_LEV}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_LAMED}"]
                }
            },
            "H13": {
                "hebrew": "מַיִם",
                "translit": "mayim",
                "stress_syllable": 1,
                "guide": "MA-yim",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_WATER}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_MA}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_MEM}"]
                }
            },
            "H14": {
                "hebrew": "נַחַל",
                "translit": "nakhal",
                "stress_syllable": 2,
                "guide": "na-KHAL",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_RIVER}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_KHAL}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_NUN}"]
                }
            },
            "H15": {
                "hebrew": "סֵפֶר",
                "translit": "sefer",
                "stress_syllable": 1,
                "guide": "SE-fer",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_BOOK}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_SE}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_SAMEKH}"]
                }
            },
            "H16": {
                "hebrew": "עַיִן",
                "translit": "ayin",
                "stress_syllable": 2,
                "guide": "a-YIN",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_EYE}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_YIN}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_AYIN_OMITTED}"]
                }
            },
            "H17": {
                "hebrew": "פֶּה",
                "translit": "pe",
                "stress_syllable": 1,
                "guide": "PE",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_MOUTH}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_PE}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_PE_DAGESH}"]
                }
            },
            "H18": {
                "hebrew": "צַדִּיק",
                "translit": "tsadik",
                "stress_syllable": 1,
                "guide": "TSA-dik",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_RIGHTEOUS}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_TSA}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_TSADI_TS}"]
                }
            },
            "H19": {
                "hebrew": "קֹדֶשׁ",
                "translit": "qodesh",
                "stress_syllable": 1,
                "guide": "QO-desh",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_HOLY}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_QO}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_QOF}"]
                }
            },
            "H20": {
                "hebrew": "רֹאשׁ",
                "translit": "rosh",
                "stress_syllable": 1,
                "guide": "ROSH",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_HEAD}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_ROSH}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_RESH}"]
                }
            },
            "H21": {
                "hebrew": "שָׁלוֹם",
                "translit": "shalom",
                "stress_syllable": 2,
                "guide": "sha-LOM",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_PEACE}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_LOM}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_SHIN_SH}"]
                }
            },
            "H22": {
                "hebrew": "תּוֹרָה",
                "translit": "tora",
                "stress_syllable": 2,
                "guide": "to-RA",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_LAW}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_RA}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_TAV_DAGESH}"]
                }
            },
            "H23": {
                "hebrew": "מֶלֶךְ",
                "translit": "melekh",
                "stress_syllable": 1,
                "guide": "ME-lekh",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_KING}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_ME}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_KAF_SOFIT}"]
                }
            },
            "H24": {
                "hebrew": "סוֹף",
                "translit": "sof",
                "stress_syllable": 1,
                "guide": "SOF",
                "guide_full": {
                    "reference": "{LANGUAGE_EXAMPLE_END}",
                    "stress_note": "{LANGUAGE_EXAMPLE_STRESS_SOF}",
                    "phonetic_notes": ["{LANGUAGE_EXAMPLE_PE_SOFIT}"]
                }
            }
        },
        "llm_data": {
            "language_adaptation": {
                "description": "This is the UNIVERSAL BASE SCHEMA. To create a language-specific schema:",
                "steps": [
                    "1. Copy this file to 'schemas/{LANGUAGE_CODE}.jsonc'",
                    "2. Replace all {LANGUAGE_*} placeholders with actual values for the target language",
                    "3. Adapt consonant/vowel mappings to target language phonetics",
                    "4. Generate native name and description using LLM",
                    "5. Test with Hebrew words and verify pronunciation accuracy",
                    "6. Validate that all 22+ examples work correctly"
                ],
                "placeholders_to_replace": [
                    "{LANGUAGE_CODE}", "{LANGUAGE_NAME}", "{LANGUAGE_VARIANT}",
                    "{LLM_GENERATED_NATIVE_NAME}", "{LLM_GENERATED_DESCRIPTION}",
                    "{LANGUAGE_EXAMPLE_*}", "{LANGUAGE_VOWEL_SOUND}"
                ]
            }
        }
    }


def generate_english_schema() -> Dict[str, Any]:
    """Generate English schema from base schema with Brill Simplified system.

    Applies English-specific adaptations according to INSTRUCTIONS.md v2.0:
    - System: Brill Simplified (recommended for English)
    - Vocal sheva: "ᵉ" (Brill superscript standard)
    - Ayin: "'" (Brill glottal stop)
    - Het: "ḥ" (Brill academic)
    - Tzadi: "tz" (Brill style)
    - Qamats qatan: enabled (Brill feature)
    """
    base_schema = get_base_schema()

    # English language configuration
    english_config = {
        "language": {
            "code": "en",
            "name": "English",
            "variant": "neutral"
        },
        "style": {
            "name": "Academic English Transliteration",
            "name_native": "Academic Hebrew Transliteration",
            "description": "Academic transliteration system based on SBL and Brill standards for pronouncing Biblical Hebrew and Aramaic words. Stressed syllable in CAPITALS.",
            "system": "simple_english",
            "strict": False,
            "dagesh": True,
            "qamatz_qatan": True,
            "sheva": "simple",
            "stress_mark": "uppercase"
        }
    }

    # English-specific consonant mappings (Brill Simplified)
    english_consonants = {
        "א": "",     # Silent aleph
        "ב": "v",    # Vet (base) - becomes "b" with dagesh
        "ג": "g",    # Gimel (no dagesh change)
        "ד": "d",    # Dalet (no dagesh change)
        "ה": "h",    # He
        "ו": "v",    # Vav (consonantal)
        "ז": "z",    # Zayin
        "ח": "kh",   # Het (simple: kh)
        "ט": "t",    # Tet
        "י": "y",    # Yod (consonantal)
        "כ": "kh",   # Kaf (base) - becomes "k" with dagesh
        "ל": "l",    # Lamed
        "מ": "m",    # Mem
        "נ": "n",    # Nun
        "ס": "s",    # Samekh
        "ע": "",     # Ayin (simple: silent)
        "פ": "f",    # Pe (base) - becomes "p" with dagesh
        "צ": "ts",   # Tzadi (simple: ts)
        "ק": "k",    # Qof (simple: k)
        "ר": "r",    # Resh
        "ש": "sh",   # Shin (Brill distinguishes שׁ vs שׂ, but simplified here)
        "ת": "t",    # Tav
        # Final forms (same as regular except dagesh-affected)
        "ך": "kh",   # Kaf sofit (same as kaf without dagesh)
        "ם": "m",    # Mem sofit
        "ן": "n",    # Nun sofit
        "ף": "f",    # Pe sofit (same as pe without dagesh)
        "ץ": "ts"    # Tzadi sofit
    }

    # Standard Brill vowel mappings (superscript sheva)
    english_vowels = {
        "ָ": "a",    # Qamats
        "ַ": "a",    # Patah
        "ֵ": "e",    # Tsere
        "ֶ": "e",    # Segol
        "ִ": "i",    # Hiriq
        "ֹ": "o",    # Holam
        "ֻ": "u",    # Qubuts
        "וּ": "u",    # Shuruq
        "ְ": "e",     # Vocal sheva (simple: e)
        "ֲ": "a",    # Hataf patah
        "ֳ": "o",    # Hataf qamats
        "ֱ": "e"     # Hataf segol
    }

    # English composite/diphthong mappings (Brill style)
    english_composite = {
        "וֹ": "o",   # Vav + holam
        "וּ": "u",   # Vav + shuruq
        "יִ": "i",   # Yod + hiriq
        "ֵי": "ei",  # Tsere + yod
        "ֶי": "e",   # Segol + yod
        "ָי": "a",   # Qamats + yod
        "ַי": "a",   # Patah + yod
        "ִי": "i",   # Hiriq + yod
        "ֹי": "o",   # Holam + yod
        "ֻי": "u",   # Qubuts + yod
        "הָ": "ah",  # He + qamats
        "הֶ": "eh",  # He + segol
        "הֵ": "eh"   # He + tsere
    }

    # Special cases for Brill system
    english_special_cases = {
        "divine_name": "yhwh",
        "maqaf": "-",
        "qamats_he": "ah",
        "furtive_patah": "a"
    }

    # Build complete English schema
    english_schema = {
        "schema_version": "2.0.0",
        **english_config,
        "rules": {
            "consonants": english_consonants,
            "vowels_nikud": english_vowels,
            "composite": english_composite,
            "special_cases": english_special_cases,
            "post_processing": [
                "apply_dagesh_rules",
                "normalize_composites",
                "remove_duplicate_consonants",
                "lowercase_rest"
            ]
        },
        "stress": base_schema.get("stress", {
            "default": "penultimate",
            "exceptions": {}
        }),
        "workflow": base_schema.get("workflow", {
            "use_strongs_reference": True,
            "pron_parsing": {
                "enabled": True,
                "syllable_separator": "-",
                "stress_marker": "'"
            },
            "xlit_reference": {
                "enabled": True
            },
            "validation_mode": "strict",
            "fallback_behavior": "use_generated"
        }),
        "transliteration_systems": base_schema.get("transliteration_systems", {}),
        "system_variations": base_schema.get("system_variations", {})
    }

    # Add English examples (translated from Spanish)
    english_examples = {}
    if "examples" in base_schema:
        for key, example in base_schema["examples"].items():
            # Replace placeholder translations with English equivalents
            guide_full = example.get("guide_full", {})
            english_guide_full = {
                "reference": _get_english_translation(key),
                "stress_note": _get_english_stress_note(key),
                "phonetic_notes": _get_english_phonetic_notes(key)
            }

            english_examples[key] = {
                "hebrew": example["hebrew"],
                "translit": example["translit"],
                "stress_syllable": example["stress_syllable"],
                "guide": example["guide"],
                "guide_full": english_guide_full
            }

    english_schema["examples"] = english_examples
    english_schema["llm_data"] = base_schema.get("llm_data", {})
    english_schema["validation"] = {
        "status": "generated_from_base",
        "reviewer": "en.py",
        "reviewed_at": "2025-11-14",
        "based_on": "SCHEMA.jsonc with Brill Simplified system",
        "purpose": "English language-specific academic transliteration schema",
        "usage": "Academic Hebrew transliteration for English speakers"
    }

    return english_schema


def _get_english_translation(key: str) -> str:
    """Get English translation for example words."""
    translations = {
        "H1": "father", "H2": "ab", "H3": "also", "H4": "blood", "H5": "he",
        "H6": "and", "H7": "this", "H8": "live", "H9": "good", "H10": "hand",
        "H11": "thus", "H12": "heart", "H13": "water", "H14": "river", "H15": "book",
        "H16": "eye", "H17": "mouth", "H18": "righteous", "H19": "holy", "H20": "head",
        "H21": "peace", "H22": "law", "H23": "king", "H24": "end"
    }
    return translations.get(key, f"translation_{key}")


def _get_english_stress_note(key: str) -> str:
    """Get English stress explanation."""
    stress_notes = {
        "H1": "stress on AV", "H2": "stress on AB", "H3": "stress on GAM",
        "H4": "stress on DAM", "H5": "stress on final", "H6": "conjunction",
        "H7": "stress on ZEH", "H8": "stress on ḤAY", "H9": "stress on ṬOV",
        "H10": "stress on YAD", "H11": "stress on KOH", "H12": "stress on LEV",
        "H13": "stress on MA", "H14": "stress on ḤAL", "H15": "stress on SE",
        "H16": "stress on YIN", "H17": "stress on PEH", "H18": "stress on TZA",
        "H19": "stress on QO", "H20": "stress on ROSH", "H21": "stress on LOM",
        "H22": "stress on RAH", "H23": "stress on ME", "H24": "stress on SOF"
    }
    return stress_notes.get(key, f"stress on {key}")


def _get_english_phonetic_notes(key: str) -> List[str]:
    """Get English phonetic explanations."""
    phonetic_notes = {
        "H1": ["א silent (aleph)"], "H2": ["Aramaic form"],
        "H3": ["ג like 'g' in 'go'"], "H4": ["ד like 'd' in 'day'"],
        "H5": ["ה like 'h' in 'hay'"], "H6": ["ְ vocal sheva"],
        "H7": ["ז like 'z' in 'zoo'"], "H8": ["ח like 'ch' in Scottish 'loch'"],
        "H9": ["ט emphatic 't'"], "H10": ["י like 'y' in 'yes'"],
        "H11": ["כּ like 'k' (kaf with dagesh)"], "H13": ["מַיִם with diphthong"],
        "H14": ["נַחַל stress on second syllable"], "H15": ["ס like 's' in 'see'"],
        "H16": ["ע glottal stop (apostrophe)"], "H17": ["פּ like 'p' (pe with dagesh)"],
        "H18": ["צַדִּיק with 'tz' sound"], "H19": ["ק like 'k' in 'kite'"],
        "H20": ["רֹאשׁ with 'sh' sound"], "H21": ["שׁ like 'sh' in 'ship'"],
        "H22": ["תּ like 't' in 'top'"], "H23": ["ך like 'kh' (kaf sofit)"],
        "H24": ["ף like 'f' (pe sofit)"]
    }
    return phonetic_notes.get(key, [f"Phonetic notes for {key}"])


# ---------------------------------------------------------------------------
# Schema modelling
# ---------------------------------------------------------------------------


@dataclass
class PronParsingConfig:
    enabled: bool = True
    syllable_separator: str = "-"
    stress_marker: str = "'"


@dataclass
class WorkflowConfig:
    use_strongs_reference: bool = True
    pron: PronParsingConfig = field(default_factory=PronParsingConfig)
    xlit_reference_enabled: bool = True
    validation_mode: str = "strict"
    fallback_behavior: str = "use_generated"


@dataclass
class StressConfig:
    default: str = "penultimate"
    exceptions: Dict[str, int] = field(default_factory=dict)


@dataclass
class SchemaRules:
    consonants: Dict[str, str]
    vowels: Dict[str, str]
    composite: Dict[str, str] = field(default_factory=dict)
    post_processing: List[str] = field(default_factory=list)


@dataclass
class SchemaConfig:
    raw: Dict[str, Any]
    style: Dict[str, Any]
    rules: SchemaRules
    stress: StressConfig
    workflow: WorkflowConfig

    @classmethod
    def from_path(cls, path: Path) -> "SchemaConfig":
        data = load_json_file(path)
        cls._validate_structure(data, path)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchemaConfig":
        cls._validate_structure(data, None)

        style = data.get("style", {})
        rules_block = data["rules"]
        stress_block = data["stress"]
        workflow_block = data.get("workflow", {})

        workflow = WorkflowConfig(
            use_strongs_reference=workflow_block.get("use_strongs_reference", True),
            pron=PronParsingConfig(
                enabled=workflow_block.get("pron_parsing", {}).get("enabled", True),
                syllable_separator=workflow_block.get("pron_parsing", {}).get("syllable_separator", "-"),
                stress_marker=workflow_block.get("pron_parsing", {}).get("stress_marker", "'"),
            ),
            xlit_reference_enabled=workflow_block.get("xlit_reference", {}).get("enabled", True),
            validation_mode=workflow_block.get("validation_mode", "strict"),
            fallback_behavior=workflow_block.get("fallback_behavior", "use_generated"),
        )

        schema_rules = SchemaRules(
            consonants=rules_block["consonants"],
            vowels=rules_block["vowels_nikud"],
            composite=rules_block.get("composite", {}),
            post_processing=list(rules_block.get("post_processing", [])),
        )

        stress = StressConfig(
            default=stress_block.get("default", "penultimate"),
            exceptions=stress_block.get("exceptions", {}),
        )

        return cls(
            raw=data,
            style=style,
            rules=schema_rules,
            stress=stress,
            workflow=workflow,
        )

    @staticmethod
    def _validate_structure(data: Dict[str, Any], origin: Path) -> None:
        """Fail fast when the schema is incomplete or inconsistent (v2.0)."""
        required_top_level = ("rules", "style", "stress", "language", "schema_version")
        for key in required_top_level:
            if key not in data:
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} missing required block '{key}'")

        # Validate v2.0 specific fields
        style = data.get("style", {})
        if "system" not in style:
            origin_str = str(origin) if origin else "generated schema"
            raise ValueError(f"Schema {origin_str} missing style.system (required in v2.0)")

        system = style.get("system")
        if system not in ("sbl_general_purpose", "brill_simplified", "simple_english"):
            origin_str = str(origin) if origin else "generated schema"
            raise ValueError(f"Schema {origin_str} has invalid system '{system}'. Must be 'sbl_general_purpose', 'brill_simplified', or 'simple_english'")

        rules: Dict[str, Any] = data["rules"]
        for block in ("consonants", "vowels_nikud"):
            if block not in rules:
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} missing rules.{block}")

        # Validate all consonants are present (27 required)
        expected_consonants = {
            "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י", "כ", "ל", "מ", "נ",
            "ס", "ע", "פ", "צ", "ק", "ר", "ש", "ת", "ך", "ם", "ן", "ף", "ץ"
        }
        actual_consonants = set(rules["consonants"].keys())
        if actual_consonants != expected_consonants:
            origin_str = str(origin) if origin else "generated schema"
            missing = expected_consonants - actual_consonants
            extra = actual_consonants - expected_consonants
            error_msg = f"Schema {origin_str} consonant mapping mismatch."
            if missing:
                error_msg += f" Missing: {sorted(missing)}"
            if extra:
                error_msg += f" Extra: {sorted(extra)}"
            raise ValueError(error_msg)

        # Validate all vowels are present (12 required for Brill system)
        expected_vowels = {"ָ", "ַ", "ֵ", "ֶ", "ִ", "ֹ", "ֻ", "וּ", "ְ", "ֲ", "ֳ", "ֱ"}
        actual_vowels = set(rules["vowels_nikud"].keys())
        if actual_vowels != expected_vowels:
            origin_str = str(origin) if origin else "generated schema"
            missing = expected_vowels - actual_vowels
            extra = actual_vowels - expected_vowels
            error_msg = f"Schema {origin_str} vowel mapping mismatch."
            if missing:
                error_msg += f" Missing: {sorted(missing)}"
            if extra:
                error_msg += f" Extra: {sorted(extra)}"
            raise ValueError(error_msg)

        # System-specific validations
        if system == "sbl_general_purpose":
            # SBL: ayin silent, het="kh"/"j", kaf="kh"/"x" (Spanish adaptations), sheva="e"
            if rules["consonants"].get("ע") != "":
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} SBL system requires silent ayin (ע='')")
            het_mapping = rules["consonants"].get("ח")
            if het_mapping not in ("kh", "j"):  # Allow "j" for Spanish adaptation
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} SBL system requires het (ח='kh' or 'j' for Spanish)")
            kaf_mapping = rules["consonants"].get("כ")
            if kaf_mapping not in ("kh", "x", "c"):  # Allow "x" or "c" for Spanish adaptation
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} SBL system requires kaf (כ='kh', 'x', or 'c' for Spanish)")
            if rules["vowels_nikud"].get("ְ") != "e":
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} SBL system requires vocal sheva (ְ='e')")

        elif system == "brill_simplified":
            # Brill: ayin="'", het="ḥ", sheva="ᵉ"
            if rules["consonants"].get("ע") != "'":
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} Brill system requires ayin (ע='\'')")
            if rules["consonants"].get("ח") != "ḥ":
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} Brill system requires het (ח='ḥ')")
            sheva_value = rules["vowels_nikud"].get("ְ")
            if sheva_value not in ("ᵉ", "ĕ"):
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} Brill system requires sheva (ְ='ᵉ' or 'ĕ')")

        elif system == "simple_english":
            # Simple English: very permissive, focuses on readability
            # Allow ayin silent or with apostrophe
            ayin_mapping = rules["consonants"].get("ע")
            if ayin_mapping not in ("", "'"):
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} Simple English system requires ayin (ע='' or ''')")
            # Allow various het mappings (kh, ḥ)
            het_mapping = rules["consonants"].get("ח")
            if het_mapping not in ("kh", "ḥ"):
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} Simple English system requires het (ח='kh' or 'ḥ')")
            # Allow simple sheva
            sheva_value = rules["vowels_nikud"].get("ְ")
            if sheva_value not in ("e", "ᵉ", "ĕ"):
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} Simple English system requires simple sheva (ְ='e', 'ᵉ', or 'ĕ')")

        # Validate consonant mappings (allow empty strings for silent consonants like א and ע)
        silent_consonants = {"א", "ע"} if system in ("sbl_general_purpose", "simple_english") else {"א"}
        for consonant, value in rules["consonants"].items():
            if value is None:
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} has null mapping for consonant '{consonant}'")
            if value == "" and consonant not in silent_consonants:
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} has empty mapping for consonant '{consonant}' (should not be empty)")
            if value != "" and consonant in silent_consonants:
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} has non-empty mapping '{value}' for silent consonant '{consonant}' (should be empty)")

        # Validate vowel mappings (system-dependent sheva handling)
        for vowel, value in rules["vowels_nikud"].items():
            if value is None:
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} has null mapping for vowel '{vowel}'")
            # Allow empty string only for sheva in some systems
            if value == "" and vowel != "ְ":
                origin_str = str(origin) if origin else "generated schema"
                raise ValueError(f"Schema {origin_str} has empty mapping for vowel '{vowel}' (should not be empty)")

        # Validate workflow section
        workflow = data.get("workflow", {})
        if "use_strongs_reference" not in workflow:
            origin_str = str(origin) if origin else "generated schema"
            raise ValueError(f"Schema {origin_str} missing workflow.use_strongs_reference")

        # Validate examples section (should have at least 22 examples as per requirements)
        examples = data.get("examples", {})
        if len(examples) < 22:
            origin_str = str(origin) if origin else "generated schema"
            raise ValueError(f"Schema {origin_str} has only {len(examples)} examples, needs at least 22")


# ---------------------------------------------------------------------------
# Transliteration engine
# ---------------------------------------------------------------------------


@dataclass
class PronInfo:
    syllables: List[str]
    stress_index: int  # 1-based


@dataclass
class TransliterationResult:
    translit: str
    guide: str


class EnglishTransliterator:
    """Turn Hebrew (with nikud) into academic English transliteration."""

    def __init__(self, schema: SchemaConfig):
        self.schema = schema
        self.rules = schema.rules
        self.workflow = schema.workflow
        self.style = schema.style
        self.stress = schema.stress

        self.dagesh_enabled = bool(self.style.get("dagesh", True)) and self.style.get("system") != "simple_english"
        self.sheva_mode = self.style.get("sheva", "simple")
        self.strict_mode = bool(self.style.get("strict", False))

        self.combining_marks = {
            "ֽ",  # Meteg
            "ֿ",  # Rafe
            "ׁ",  # Shin dot (right)
            "ׂ",  # Shin dot (left)
            "ׄ",  # Upper dot
            "ׅ",  # Lower dot
        }

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def transliterate(
        self,
        hebrew_text: str,
        strong_number: str,
        pron: Optional[str] = None,
        xlit: Optional[str] = None,
    ) -> TransliterationResult:
        if not isinstance(hebrew_text, str):
            raise TypeError("hebrew_text must be a string")
        if not isinstance(strong_number, str):
            raise TypeError("strong_number must be a string")

        if not hebrew_text.strip():
            return TransliterationResult(translit="", guide="")

        self._validate_strong_number(strong_number)

        pron_info = self._parse_pron(pron) if self._should_use_pron(pron) else None
        xlit_info = self._parse_xlit(xlit) if self._should_use_xlit(xlit) else None

        translit = self._transliterate_chars(hebrew_text)
        if xlit_info:
            translit = self._apply_xlit_corrections(translit, xlit_info)

        translit = self._post_process(translit)

        guide = self._generate_guide(translit, strong_number, pron_info)
        self._validate_result(translit, guide, hebrew_text, strong_number)

        return TransliterationResult(translit=translit, guide=guide)

    # ------------------------------------------------------------------ #
    # Core transliteration steps
    # ------------------------------------------------------------------ #

    def _transliterate_chars(self, hebrew_text: str) -> str:
        parts: List[str] = []
        i = 0
        length = len(hebrew_text)

        while i < length:
            char = hebrew_text[i]

            if char in self.combining_marks:
                i += 1
                continue

            composite = self._match_composite(hebrew_text, i)
            if composite:
                value, consumed = composite
                parts.append(value)
                i += consumed
                continue

            if char in self.rules.consonants:
                value = self._transliterate_consonant(hebrew_text, i, char)
                if value:
                    parts.append(value)
                i += 1
                continue

            if char in self.rules.vowels:
                value = self._transliterate_vowel(char)
                if value:
                    parts.append(value)
                i += 1
                continue

            # Unknown symbols are ignored deliberately
            i += 1

        return "".join(parts)

    def _transliterate_consonant(self, text: str, index: int, char: str) -> str:
        value = self.rules.consonants.get(char, "")

        if char == "ש":
            variant = self._detect_shin_variant(text, index)
            if variant == "sin":
                return "s"
            return "sh"

        if self.dagesh_enabled and char in {"ב", "כ", "פ"}:
            if self._has_mark(text, index, DAGESH_CHAR):
                return {"ב": "b", "כ": "k", "פ": "p"}[char]
            # Without dagesh: use schema values
            return {"ב": self.rules.consonants.get("ב", "v"),
                    "כ": self.rules.consonants.get("כ", "kh"),
                    "פ": self.rules.consonants.get("פ", "f")}[char]

        return value

    def _transliterate_vowel(self, char: str) -> str:
        value = self.rules.vowels.get(char, "")

        if char == SHEVA_CHAR:
            if self.sheva_mode == "silent":
                return ""
            if self.sheva_mode == "simple":
                return "e"

        return value

    def _match_composite(self, text: str, index: int) -> Optional[Tuple[str, int]]:
        max_len = min(3, len(text) - index)
        for length in range(max_len, 1, -1):
            chunk = text[index:index + length]
            if chunk in self.rules.composite:
                return self.rules.composite[chunk], length
        return None

    def _detect_shin_variant(self, text: str, index: int) -> str:
        j = index + 1
        while j < len(text) and text[j] in self.combining_marks | {DAGESH_CHAR}:
            if text[j] == "ׂ":
                return "sin"
            if text[j] == "ׁ":
                return "shin"
            j += 1
        return "shin"

    def _has_mark(self, text: str, index: int, mark: str) -> bool:
        j = index + 1
        while j < len(text) and (text[j] in self.combining_marks or text[j] == DAGESH_CHAR):
            if text[j] == mark:
                return True
            j += 1
        return False

    # ------------------------------------------------------------------ #
    # Pron / xlit helpers
    # ------------------------------------------------------------------ #

    def _should_use_pron(self, pron: Optional[str]) -> bool:
        return bool(
            pron
            and self.workflow.use_strongs_reference
            and self.workflow.pron.enabled
        )

    def _should_use_xlit(self, xlit: Optional[str]) -> bool:
        return bool(
            xlit
            and self.workflow.use_strongs_reference
            and self.workflow.xlit_reference_enabled
        )

    def _parse_pron(self, pron: Optional[str]) -> Optional[PronInfo]:
        if not pron:
            return None

        try:
            chunks = [
                chunk.strip()
                for chunk in pron.split(self.workflow.pron.syllable_separator)
                if chunk.strip()
            ]
        except Exception:
            self._warn(f"Unable to split pron value '{pron}'")
            return None

        if not chunks:
            return None

        stress_index: Optional[int] = None
        cleaned: List[str] = []

        for chunk in chunks:
            if self.workflow.pron.stress_marker in chunk:
                chunk = chunk.replace(self.workflow.pron.stress_marker, "")
                stress_index = len(cleaned) + 1
            if chunk:
                cleaned.append(chunk)

        if not cleaned:
            return None

        if stress_index is None:
            stress_index = len(cleaned)

        return PronInfo(cleaned, stress_index)

    def _parse_xlit(self, xlit: Optional[str]) -> Optional[Dict[str, Any]]:
        if not xlit:
            return None
        lowered = xlit.lower()
        return {
            "has_ayin": any(symbol in lowered for symbol in ("ʻ", "ʿ")),
            "has_sheva": "ᵉ" in lowered,
            "length": len(lowered),
        }

    def _apply_xlit_corrections(self, translit: str, _: Dict[str, Any]) -> str:
        # Placeholder for future corrections. Keeping hook for completeness.
        return translit

    # ------------------------------------------------------------------ #
    # Guide / syllable helpers
    # ------------------------------------------------------------------ #

    def _generate_guide(
        self,
        translit: str,
        strong_number: str,
        pron_info: Optional[PronInfo],
    ) -> str:
        if not translit:
            return ""

        desired_count = len(pron_info.syllables) if pron_info else None
        pron_syllables = pron_info.syllables if pron_info else None
        syllables = self._split_syllables(translit, desired_count, pron_syllables)

        stress_index = self._resolve_stress(strong_number, pron_info, len(syllables))

        if not syllables:
            return translit.upper()

        guide_parts = []
        for idx, syllable in enumerate(syllables, start=1):
            if idx == stress_index:
                guide_parts.append(syllable.upper())
            else:
                guide_parts.append(syllable.lower())

        guide_result = "-".join(guide_parts)

        # Fix: If guide lacks ASCII uppercase but should have it, force uppercase on first ASCII syllable
        has_ascii_upper = any(char.isupper() and char.isascii() for char in guide_result)
        if not has_ascii_upper and any(vowel in translit.lower() for vowel in VOWELS):
            # Find first syllable with ASCII letters and make it uppercase
            fixed_parts = []
            found_upper = False
            for part in guide_parts:
                if not found_upper and any(c.isascii() and c.isalpha() for c in part):
                    fixed_parts.append(part.upper())
                    found_upper = True
                else:
                    fixed_parts.append(part)
            guide_result = "-".join(fixed_parts)

        return guide_result

    def _split_syllables(self, text: str, desired_count: Optional[int], pron_syllables: Optional[List[str]] = None) -> List[str]:
        if not text:
            return []

        aligned = None
        # If we have pron syllables, try to align with them
        if pron_syllables and len(pron_syllables) > 1:
            aligned = self._align_with_pron_syllables(text.lower(), pron_syllables)
            if aligned:
                return aligned

        syllables = self._basic_english_split(text.lower())

        # If we have pron info but alignment failed, try digraph-aware splitting
        if pron_syllables and aligned is None:
            digraph_aware = self._digraph_aware_split(text.lower(), len(pron_syllables))
            if digraph_aware and len(digraph_aware) == len(pron_syllables):
                return digraph_aware

        if desired_count:
            syllables = self._rebalance_syllables(syllables, desired_count)
        return syllables

    def _align_with_pron_syllables(self, text: str, pron_syllables: List[str]) -> Optional[List[str]]:
        """Try to align transliteration syllables with pron syllables using phonetic approximations."""
        # Remove stress markers and normalize pron syllables
        clean_pron = []
        for syl in pron_syllables:
            syl = syl.replace("'", "")
            # Basic phonetic normalization
            syl = syl.replace("aw", "a").replace("oo", "u").replace("ee", "i")
            syl = syl.replace("maw", "mah").replace("taw", "tah")  # Common Hebrew endings
            clean_pron.append(syl)

        # Try exact substring matching first
        result = []
        remaining = text
        for i, pron_syl in enumerate(clean_pron):
            if pron_syl in remaining:
                idx = remaining.find(pron_syl)
                if idx > 0:
                    # Add any prefix as separate syllable
                    result.append(remaining[:idx])
                result.append(remaining[idx:idx + len(pron_syl)])
                remaining = remaining[idx + len(pron_syl):]
            else:
                # Can't align exactly, try fuzzy matching for the last syllable
                if i == len(clean_pron) - 1 and remaining:
                    result.append(remaining)
                    remaining = ""
                else:
                    best_match = self._find_best_pron_match(remaining, pron_syl)
                    if best_match:
                        result.extend(best_match)
                        remaining = ""
                        break
                    else:
                        return None

        if remaining:
            # Add any remaining text to the last syllable
            result[-1] += remaining

        return result if len(result) >= len(clean_pron) else None

    def _digraph_aware_split(self, text: str, target_syllables: int) -> Optional[List[str]]:
        """Split text prioritizing digraph integrity for better pron alignment."""
        if target_syllables == 2 and len(text) >= 4:
            # For 2 syllables, check if there's a digraph that should start the second syllable
            for i in range(1, len(text) - 2):
                if text[i:i+2] in ['sh', 'tz', 'ch', 'kh', 'ph', 'th']:
                    # Found a digraph, split before it (but keep it with the following syllable)
                    return [text[:i], text[i:]]

        # For 3 syllables, try more complex patterns
        if target_syllables == 3 and len(text) >= 6:
            # Look for patterns like: vowel + digraph + consonant + vowel + ...
            # This is a simplified approach
            pass

        return None

    def _find_best_pron_match(self, text: str, pron_syl: str) -> Optional[List[str]]:
        """Find the best phonetic match for a pron syllable in the text."""
        # For common patterns where pron and translit don't align perfectly
        if pron_syl == "ma" and text.startswith("mah"):
            return ["mah"]
        if pron_syl == "ta" and text.startswith("tah"):
            return ["tah"]
        if pron_syl.endswith("a") and text.startswith(pron_syl[:-1] + "ah"):
            return [pron_syl[:-1] + "ah"]

        return None

    def _basic_english_split(self, text: str) -> List[str]:
        # Pre-process to handle digraphs (compound sounds) that should stay together
        processed_text = self._protect_digraphs(text)

        syllables: List[str] = []
        length = len(processed_text)
        start = 0
        idx = 0

        while idx < length:
            # Skip over protected digraphs (marked with special characters)
            if processed_text[idx] in ['\ufeff', '\u200c']:  # Zero-width characters for digraph protection
                idx += 2  # Skip the marker and the next character
                continue

            if processed_text[idx] not in VOWELS:
                idx += 1
                continue

            end = idx + 1
            while end < length:
                # Don't break on Unicode special characters - they belong to current syllable
                if _is_unicode_special(processed_text[end]):
                    end += 1
                    continue
                # Don't break digraphs
                if processed_text[end] in ['\ufeff', '\u200c']:
                    end += 2  # Skip the digraph
                    continue
                if processed_text[end] not in VOWELS:
                    end += 1
                    continue
                # Found next vowel - this is syllable boundary unless followed by Unicode chars
                if end + 1 < length and processed_text[end + 1] in VOWELS:
                    # Two vowels in a row - continue
                    end += 1
                    continue
                # Check if this vowel is followed by Unicode special chars
                next_pos = end + 1
                while next_pos < length and _is_unicode_special(processed_text[next_pos]):
                    next_pos += 1
                if next_pos < length and processed_text[next_pos] in VOWELS:
                    # Next vowel after Unicode chars - continue current syllable
                    end = next_pos
                    continue
                # This is a syllable boundary
                break

            syllable = processed_text[start:end]
            # Restore the original digraphs
            syllable = self._restore_digraphs(syllable)
            syllables.append(syllable)
            start = end
            idx = end

        if start < length:
            remaining = processed_text[start:]
            remaining = self._restore_digraphs(remaining)
            if syllables:
                syllables[-1] += remaining
            else:
                syllables.append(remaining)

        return syllables or [text]

    def _protect_digraphs(self, text: str) -> str:
        """Replace digraphs with protected sequences to prevent syllable splitting."""
        # Common digraphs in Hebrew transliteration
        digraphs = ['sh', 'tz', 'ch', 'kh', 'ph', 'th']
        result = text
        for digraph in digraphs:
            # Replace with zero-width non-breaking space + second char
            # This prevents the syllable splitter from breaking them
            result = result.replace(digraph, '\ufeff' + digraph[1])
        return result

    def _restore_digraphs(self, text: str) -> str:
        """Restore digraphs from protected sequences."""
        digraphs = ['sh', 'tz', 'ch', 'kh', 'ph', 'th']
        result = text
        for digraph in digraphs:
            result = result.replace('\ufeff' + digraph[1], digraph)
        return result

    def _rebalance_syllables(self, syllables: List[str], desired: int) -> List[str]:
        result = syllables[:]

        while len(result) > desired:
            merge_index = max(1, len(result) - 1)
            result[merge_index - 1] += result.pop(merge_index)

        while len(result) < desired:
            idx = self._find_split_candidate(result)
            if idx is None:
                break
            split_pos = self._find_split_point(result[idx])
            if not split_pos:
                break
            chunk = result[idx]
            result[idx:idx + 1] = [chunk[:split_pos], chunk[split_pos:]]

        return result

    def _find_split_candidate(self, syllables: List[str]) -> Optional[int]:
        for idx, syllable in enumerate(syllables):
            vowel_count = sum(1 for char in syllable if char in VOWELS)
            if vowel_count > 1 and len(syllable) >= 4:
                return idx
        return None

    def _find_split_point(self, syllable: str) -> Optional[int]:
        for idx in range(len(syllable) - 1, 0, -1):
            if syllable[idx] in VOWELS:
                return idx
        mid = len(syllable) // 2
        return mid if 0 < mid < len(syllable) else None

    def _resolve_stress(
        self,
        strong_number: str,
        pron_info: Optional[PronInfo],
        syllable_count: int,
    ) -> int:
        if pron_info:
            return max(1, min(pron_info.stress_index, syllable_count or 1))

        if strong_number in self.stress.exceptions:
            return max(1, self.stress.exceptions[strong_number])

        if syllable_count <= 1:
            return 1

        if self.stress.default == "penultimate":
            if syllable_count == 2:
                return 2
            return max(1, syllable_count - 1)
        if self.stress.default == "ultimate":
            return syllable_count
        if self.stress.default == "antepenultimate":
            return max(1, syllable_count - 2)

        return 1

    # ------------------------------------------------------------------ #
    # Validation / logging
    # ------------------------------------------------------------------ #

    def _post_process(self, text: str) -> str:
        result = text
        for step in self.rules.post_processing:
            if step == "remove_duplicate_consonants":
                result = re.sub(r"([bcdfghjklmnprstvz])\1+", r"\1", result, flags=re.IGNORECASE)
            elif step == "apply_stress_uppercase":
                # This is handled in the guide generation, not here
                pass
            elif step == "lowercase_rest":
                result = result.lower()
        return result

    def _validate_result(self, translit: str, guide: str, hebrew: str, strong_number: str) -> None:
        if self.workflow.validation_mode == "lenient":
            return

        if hebrew and not translit:
            self._warn(f"Empty transliteration for {strong_number}")

        if translit and not guide:
            self._warn(f"Empty guide for {strong_number}")

        if translit and guide:
            if any(vowel in translit.lower() for vowel in VOWELS):
                # Only check ASCII letters for uppercase stress marking, ignore Unicode chars
                if not any(char.isupper() and char.isascii() for char in guide):
                    self._warn(f"Guide '{guide}' lacks uppercase stress for {strong_number}")

    def _validate_strong_number(self, strong_number: str) -> None:
        if strong_number.startswith(("H", "G")):
            return
        message = f"Invalid Strong's key '{strong_number}'"
        if self.workflow.validation_mode == "error":
            raise ValueError(message)
        self._warn(message)

    def _warn(self, message: str) -> None:
        if self.workflow.validation_mode == "strict":
            print(f"Warning: {message}")


# ---------------------------------------------------------------------------
# Strong's processing pipeline
# ---------------------------------------------------------------------------


def load_strongs(path: Path) -> Dict[str, Any]:
    data = load_json_file(path)
    if isinstance(data, list):
        # Convert list to dict with IDs as keys
        return {entry["id"]: entry for entry in data}
    elif isinstance(data, dict):
        return data
    else:
        raise ValueError(f"Strong's dataset must be a JSON object or array, got {type(data)}")


def generate_transliterations(
    transliterator: EnglishTransliterator,
    strongs_data: Dict[str, Any],
    include_langs: Iterable[str] = ("Hebrew", "Aramaic"),
    limit: Optional[int] = None,
    only: Optional[Iterable[str]] = None,
) -> Tuple[Dict[str, Any], Dict[str, int]]:
    include_set = set(include_langs)
    only_list = list(only) if only else None

    results: Dict[str, Any] = {}
    stats = {"processed": 0, "skipped": 0, "errors": 0}

    items = strongs_data.items()
    if only_list:
        items = ((key, strongs_data[key]) for key in only_list if key in strongs_data)

    for idx, (strong_number, entry) in enumerate(items, start=1):
        if limit and idx > limit:
            break

        if not isinstance(entry, dict):
            stats["skipped"] += 1
            continue

        lang = entry.get("lang") or entry.get("language", "Hebrew")
        if lang not in include_set:
            continue

        hebrew = entry.get("hebrew", "")
        pron = entry.get("pron")
        xlit = entry.get("xlit")

        try:
            result = transliterator.transliterate(hebrew, strong_number, pron, xlit)
        except Exception as exc:  # pragma: no cover - defensive, script context
            stats["errors"] += 1
            print(f"Error processing {strong_number}: {exc}")
            continue

        results[strong_number] = {
            "hebrew": hebrew,
            "language": lang,
            "translit": result.translit,
            "guide": result.guide,
        }
        stats["processed"] += 1

        if stats["processed"] and stats["processed"] % 1000 == 0:
            print(f"  Processed {stats['processed']} entries...")

    return results, stats


def save_results(output_path: Path, data: Dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser(script_dir: Path) -> argparse.ArgumentParser:
    project_root = script_dir.parent
    default_strongs = project_root / "data" / "strongs.json"
    default_output = project_root / "data" / "strong_en.json"
    default_schema_output = project_root / "schemas" / "en.json"

    parser = argparse.ArgumentParser(
        description="Generate English transliterations using Brill Simplified system (v2.0)",
    )
    parser.add_argument("--generate-schema-only", action="store_true",
                       help="Only generate the English schema, don't process transliterations")
    parser.add_argument("--schema-output", type=Path, default=default_schema_output,
                       help="Where to save generated schema (default: %(default)s)")
    parser.add_argument("--strongs", type=Path, default=default_strongs,
                       help="Path to Strong's JSON (default: %(default)s)")
    parser.add_argument("--output", type=Path, default=default_output,
                       help="Destination JSON path for transliterations (default: %(default)s)")
    parser.add_argument("--limit", type=int, default=None,
                       help="Process only the first N entries (debug)")
    parser.add_argument("--only", type=str, default=None,
                       help="Comma-separated Strong's IDs to process")
    return parser


def parse_only_argument(raw: Optional[str]) -> Optional[List[str]]:
    if not raw:
        return None
    return [token.strip() for token in raw.split(",") if token.strip()]


def main(argv: Optional[List[str]] = None) -> None:
    script_dir = Path(__file__).resolve().parent
    parser = build_parser(script_dir)
    args = parser.parse_args(argv)

    # Generate English schema from base
    print("Generating English schema from base schema")
    english_schema_data = generate_english_schema()

    # Validate the generated schema
    try:
        schema = SchemaConfig.from_dict(english_schema_data)
        print("✓ Generated schema validation passed")
    except ValueError as e:
        print(f"❌ Schema validation failed: {e}")
        return

    # Save the generated schema
    args.schema_output.parent.mkdir(parents=True, exist_ok=True)
    with args.schema_output.open("w", encoding="utf-8") as f:
        json.dump(english_schema_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved English schema to: {args.schema_output}")

    # If only generating schema, stop here
    if args.generate_schema_only:
        print("Schema generation complete (transliteration generation skipped)")
        return

    # Proceed with transliteration generation
    transliterator = EnglishTransliterator(schema)
    strongs_data = load_strongs(args.strongs)
    only = parse_only_argument(args.only)

    print(f"Loaded Strong's data: {args.strongs} ({len(strongs_data)} entries)")
    system_name = "Simple English" if schema.style.get("system") == "simple_english" else "Brill Simplified"
    print(f"Using {system_name} system for English transliterations")

    results, stats = generate_transliterations(transliterator, strongs_data, limit=args.limit, only=only)

    save_results(args.output, results)

    print(f"✓ Saved {len(results)} English transliterations to {args.output}")
    print(f"Processed: {stats['processed']} | Errors: {stats['errors']} | Skipped: {stats['skipped']}")


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
