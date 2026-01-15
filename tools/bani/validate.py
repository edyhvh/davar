#!/usr/bin/env python3
"""
Bani Schema Validator
Validates transliteration schemas for completeness and correctness

Usage:
    python scripts/validate.py schemas/informal.es.jsonc --level 3
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple


def load_jsonc(file_path: Path) -> Dict[str, Any]:
    """Load JSONC (JSON with comments) file by removing comments."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove single-line comments (// ...)
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

    # Remove multi-line comments (/* ... */)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    return json.loads(content)


class SchemaValidator:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_level_1(self) -> bool:
        """Level 1: Basic JSON structure and required fields."""
        required_fields = [
            'schema_version', 'language', 'style', 'rules',
            'stress', 'examples', 'validation'
        ]

        for field in required_fields:
            if field not in self.schema:
                self.errors.append(f"Missing required field: {field}")

        # Check language structure
        if 'language' in self.schema:
            lang = self.schema['language']
            required_lang_fields = ['code', 'name', 'variant']
            for field in required_lang_fields:
                if field not in lang:
                    self.errors.append(f"Missing language field: {field}")

        # Check style structure
        if 'style' in self.schema:
            style = self.schema['style']
            required_style_fields = ['name', 'name_native', 'description', 'strict', 'dagesh', 'qamatz_qatan', 'sheva', 'stress_mark']
            for field in required_style_fields:
                if field not in style:
                    self.errors.append(f"Missing style field: {field}")

        return len(self.errors) == 0

    def validate_level_2(self) -> bool:
        """Level 2: Rule completeness."""
        if 'rules' not in self.schema:
            return False

        rules = self.schema['rules']

        # Check consonants (22 letters + 5 final forms = 27)
        if 'consonants' in rules:
            consonants = rules['consonants']
            required_consonants = [
                'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י',
                'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',
                'ך', 'ם', 'ן', 'ף', 'ץ'  # final forms
            ]

            for cons in required_consonants:
                if cons not in consonants or not consonants[cons]:
                    self.errors.append(f"Missing consonant mapping: {cons}")
        else:
            self.errors.append("Missing consonants rules")

        # Check vowels (9 nikud)
        if 'vowels_nikud' in rules:
            vowels = rules['vowels_nikud']
            required_vowels = ['ָ', 'ַ', 'ֵ', 'ֶ', 'ִ', 'ֹ', 'ֻ', 'וּ', 'ְ']

            for vowel in required_vowels:
                if vowel not in vowels or not vowels[vowel]:
                    self.errors.append(f"Missing vowel mapping: {vowel}")
        else:
            self.errors.append("Missing vowels_nikud rules")

        return len(self.errors) == 0

    def validate_level_3(self) -> bool:
        """Level 3: Example validation and stress correctness."""
        if 'examples' not in self.schema:
            self.errors.append("Missing examples section")
            return False

        examples = self.schema['examples']

        # Check that we have examples for all required letters
        required_examples = [
            'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10',
            'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20',
            'H21', 'H22', 'H23', 'H24'  # 22 standard + 2 final forms
        ]

        for ex_id in required_examples:
            if ex_id not in examples:
                self.errors.append(f"Missing example: {ex_id}")
                continue

            example = examples[ex_id]
            required_ex_fields = ['hebrew', 'translit', 'stress_syllable', 'guide', 'guide_full']

            for field in required_ex_fields:
                if field not in example:
                    self.errors.append(f"Example {ex_id} missing field: {field}")
                    continue

            # Validate stress in guide
            if 'guide' in example and 'stress_syllable' in example:
                guide = example['guide']
                stress_syllable = example['stress_syllable']

                # Guide should have CAPITALS on stressed syllable
                syllables = guide.split()
                if stress_syllable <= len(syllables):
                    stressed_syllable = syllables[stress_syllable - 1]
                    if not any(c.isupper() for c in stressed_syllable):
                        self.warnings.append(f"Example {ex_id}: stressed syllable '{stressed_syllable}' should have CAPITALS")

            # Validate guide_full structure
            if 'guide_full' in example:
                gf = example['guide_full']
                required_gf_fields = ['reference', 'stress_note', 'phonetic_notes']

                for field in required_gf_fields:
                    if field not in gf:
                        self.errors.append(f"Example {ex_id} guide_full missing: {field}")

                # Validate phonetic_notes is array
                if 'phonetic_notes' in gf and not isinstance(gf['phonetic_notes'], list):
                    self.errors.append(f"Example {ex_id}: phonetic_notes should be an array")

        return len(self.errors) == 0

    def validate_level_4(self) -> bool:
        """Level 4: Human review validation (placeholder)."""
        # This would be for manual review
        # For now, just check that validation status is set
        if 'validation' in self.schema:
            validation = self.schema['validation']
            if 'status' not in validation:
                self.errors.append("Missing validation status")
            elif validation['status'] not in ['pending_review', 'approved', 'rejected']:
                self.warnings.append(f"Unexpected validation status: {validation['status']}")
        else:
            self.errors.append("Missing validation section")

        return len(self.errors) == 0

    def validate(self, level: int) -> Tuple[bool, List[str], List[str]]:
        """Run validation up to specified level."""
        self.errors = []
        self.warnings = []

        levels = [
            self.validate_level_1,
            self.validate_level_2,
            self.validate_level_3,
            self.validate_level_4
        ]

        for i in range(min(level, len(levels))):
            if not levels[i]():
                break

        return len(self.errors) == 0, self.errors, self.warnings


def main():
    parser = argparse.ArgumentParser(description='Validate Bani transliteration schema')
    parser.add_argument('schema_file', help='Path to schema file to validate')
    parser.add_argument('--level', type=int, choices=[1, 2, 3, 4], default=3,
                       help='Validation level (1-4, default: 3)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show errors')

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

    validator = SchemaValidator(schema)
    is_valid, errors, warnings = validator.validate(args.level)

    if not args.quiet:
        print(f"Validating schema: {schema_path}")
        print(f"Level: {args.level}")
        print(f"Schema version: {schema.get('schema_version', 'unknown')}")
        print(f"Language: {schema.get('language', {}).get('name', 'unknown')} ({schema.get('language', {}).get('code', 'unknown')})")
        print()

    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  ❌ {error}")
        print()

    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
        print()

    if is_valid:
        print("✅ Schema validation PASSED")
        return 0
    else:
        print("❌ Schema validation FAILED")
        return 1


if __name__ == '__main__':
    exit(main())








