#!/usr/bin/env python3
"""
Bani Schema Applier
Applies transliteration schema to Hebrew word dataset

Usage:
    python scripts/apply.py schemas/informal.es.jsonc --words 100
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import unicodedata


def load_jsonc(file_path: Path) -> Dict[str, Any]:
    """Load JSONC (JSON with comments) file by removing comments."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove single-line comments (// ...)
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

    # Remove multi-line comments (/* ... */)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    return json.loads(content)


class Transliterator:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.consonants = schema['rules']['consonants']
        self.vowels = schema['rules']['vowels_nikud']
        self.composite = schema.get('rules', {}).get('composite', {})
        self.post_processing = schema['rules'].get('post_processing', [])
        self.stress_default = schema['stress']['default']
        self.stress_exceptions = schema['stress']['exceptions']

    def normalize_hebrew(self, hebrew: str) -> str:
        """Normalize Hebrew text for processing."""
        # Decompose and recompose to normalize
        return unicodedata.normalize('NFD', hebrew)

    def split_into_syllables(self, translit: str) -> List[str]:
        """Simple syllable splitting based on vowels."""
        # This is a basic implementation - could be improved
        syllables = []
        current = ""

        for char in translit:
            current += char
            # Split on vowels (very basic)
            if char in 'aeiouAEIOU':
                syllables.append(current)
                current = ""

        if current:
            syllables.append(current)

        return syllables if syllables else [translit]

    def apply_stress(self, translit: str, strongs_num: str, stress_syllable: Optional[int] = None) -> str:
        """Apply stress marking to transliteration."""
        if stress_syllable is None:
            # Use exception or default
            if strongs_num in self.stress_exceptions:
                stress_syllable = self.stress_exceptions[strongs_num]
            else:
                # Calculate based on default rule
                syllables = self.split_into_syllables(translit)
                if self.stress_default == 'penultimate':
                    stress_syllable = max(1, len(syllables) - 1)
                elif self.stress_default == 'ultimate':
                    stress_syllable = len(syllables)
                elif self.stress_default == 'antepenultimate':
                    stress_syllable = max(1, len(syllables) - 2)
                else:
                    stress_syllable = len(syllables)

        syllables = self.split_into_syllables(translit)
        if stress_syllable > len(syllables):
            stress_syllable = len(syllables)

        # Apply uppercase stress marking
        if 1 <= stress_syllable <= len(syllables):
            syllables[stress_syllable - 1] = syllables[stress_syllable - 1].upper()

        return ''.join(syllables)

    def transliterate_word(self, hebrew: str, strongs_num: str = "") -> Dict[str, Any]:
        """Transliterate a single Hebrew word."""
        result = {
            'hebrew': hebrew,
            'translit': '',
            'stress_syllable': None,
            'guide': '',
            'guide_full': {
                'reference': '',
                'stress_note': '',
                'phonetic_notes': []
            }
        }

        try:
            # Normalize Hebrew
            normalized = self.normalize_hebrew(hebrew)

            # Basic character-by-character transliteration
            translit = ""
            i = 0
            while i < len(normalized):
                char = normalized[i]

                # Check for composite characters first (longer matches)
                found_composite = False
                for comp, replacement in self.composite.items():
                    if normalized.startswith(comp, i):
                        translit += replacement
                        i += len(comp)
                        found_composite = True
                        break

                if not found_composite:
                    # Single character mapping
                    if char in self.consonants:
                        translit += self.consonants[char]
                    elif char in self.vowels:
                        translit += self.vowels[char]
                    else:
                        # Keep unknown characters as-is or skip
                        translit += char
                    i += 1

            # Apply post-processing
            for rule in self.post_processing:
                if rule == 'remove_duplicate_consonants':
                    translit = re.sub(r'(.)\1+', r'\1', translit)
                elif rule == 'apply_stress_uppercase':
                    translit = self.apply_stress(translit, strongs_num)
                elif rule == 'lowercase_rest':
                    # Keep only the stressed syllable uppercase
                    pass  # Handled in apply_stress

            result['translit'] = translit.lower()

            # Generate guide (with stress)
            result['guide'] = self.apply_stress(translit.lower(), strongs_num)

            # Calculate stress syllable for guide_full
            syllables = self.split_into_syllables(translit.lower())
            stressed_idx = None
            for idx, syll in enumerate(syllables):
                if any(c.isupper() for c in syll):
                    stressed_idx = idx + 1
                    break

            result['stress_syllable'] = stressed_idx or len(syllables)

            # Generate stress note
            if stressed_idx:
                syllables_lower = [s.lower() for s in syllables]
                if stressed_idx <= len(syllables_lower):
                    stressed_syll = syllables_lower[stressed_idx - 1]
                    result['guide_full']['stress_note'] = f"stress on {stressed_syll.upper()}"

        except Exception as e:
            print(f"Warning: Error transliterating '{hebrew}': {e}")

        return result

    def apply_to_dataset(self, words: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply transliteration to a dataset of words."""
        result = {}

        for word_data in words:
            strongs_num = word_data.get('strongs', '')
            hebrew = word_data.get('hebrew', '')

            if not hebrew:
                continue

            transliterated = self.transliterate_word(hebrew, strongs_num)
            result[strongs_num] = transliterated

        return result


def load_sample_words(count: int = 100) -> List[Dict[str, Any]]:
    """Load sample Hebrew words for testing (mock data)."""
    # This is mock data - in real usage you'd load from a proper dataset
    sample_words = [
        {'strongs': 'H1', 'hebrew': 'אָב'},
        {'strongs': 'H2', 'hebrew': 'בֵּן'},
        {'strongs': 'H3', 'hebrew': 'גַּם'},
        {'strongs': 'H4', 'hebrew': 'דָּם'},
        {'strongs': 'H5', 'hebrew': 'הוּא'},
        {'strongs': 'H6', 'hebrew': 'וְ'},
        {'strongs': 'H7', 'hebrew': 'זֶה'},
        {'strongs': 'H8', 'hebrew': 'חַי'},
        {'strongs': 'H9', 'hebrew': 'טוֹב'},
        {'strongs': 'H10', 'hebrew': 'יָד'},
        {'strongs': 'H11', 'hebrew': 'כֹּה'},
        {'strongs': 'H12', 'hebrew': 'לֵב'},
        {'strongs': 'H13', 'hebrew': 'מַיִם'},
        {'strongs': 'H14', 'hebrew': 'נַחַל'},
        {'strongs': 'H15', 'hebrew': 'סֵפֶר'},
        {'strongs': 'H16', 'hebrew': 'עַיִן'},
        {'strongs': 'H17', 'hebrew': 'פֶּה'},
        {'strongs': 'H18', 'hebrew': 'צַדִּיק'},
        {'strongs': 'H19', 'hebrew': 'קֹדֶשׁ'},
        {'strongs': 'H20', 'hebrew': 'רֹאשׁ'},
        {'strongs': 'H21', 'hebrew': 'שָׁלוֹם'},
        {'strongs': 'H22', 'hebrew': 'תּוֹרָה'},
        {'strongs': 'H23', 'hebrew': 'מֶלֶךְ'},
        {'strongs': 'H24', 'hebrew': 'סוֹף'},
    ]

    return sample_words[:count]


def main():
    parser = argparse.ArgumentParser(description='Apply Bani transliteration schema to word dataset')
    parser.add_argument('schema_file', help='Path to schema file')
    parser.add_argument('--words', type=int, default=100, help='Number of words to process')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--sqlite', help='Output SQLite database path')
    parser.add_argument('--sample', action='store_true', help='Use sample data instead of real dataset')

    args = parser.parse_args()

    schema_path = Path(args.schema_file)

    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}")
        return 1

    try:
        schema = load_jsonc(schema_path)
    except Exception as e:
        print(f"Error loading schema: {e}")
        return 1

    # Validate schema first
    from validate import SchemaValidator
    validator = SchemaValidator(schema)
    is_valid, errors, warnings = validator.validate(3)

    if not is_valid:
        print("Schema validation failed. Please fix errors first:")
        for error in errors:
            print(f"  ❌ {error}")
        return 1

    if warnings:
        print("Schema has warnings:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")

    # Load words
    if args.sample:
        words = load_sample_words(args.words)
        print(f"Using {len(words)} sample words")
    else:
        print("Real dataset loading not implemented yet. Use --sample")
        return 1

    # Apply transliteration
    transliterator = Transliterator(schema)
    result = transliterator.apply_to_dataset(words)

    # Set default output path
    if not args.output:
        lang_code = schema['language']['code']
        args.output = f"data/json/bani-{lang_code}.json"

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save JSON
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Transliterations saved to: {output_path}")
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return 1

    # SQLite export (placeholder)
    if args.sqlite:
        print(f"SQLite export not implemented yet: {args.sqlite}")

    print(f"Successfully processed {len(result)} words")
    return 0


if __name__ == '__main__':
    exit(main())








