#!/usr/bin/env python3
"""
Bani Schema Generator
Generates transliteration schemas using Ollama LLM

Usage:
    python scripts/generate.py --lang es --model gemma3:1b
"""

import json
import re
import argparse
from pathlib import Path
import ollama
from typing import Dict, Any


def load_jsonc(file_path: Path) -> Dict[str, Any]:
    """Load JSONC (JSON with comments) file by removing comments."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove single-line comments (// ...)
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

    # Remove multi-line comments (/* ... */)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    return json.loads(content)


def create_prompt(instructions: str, template: Dict[str, Any], target_lang: str) -> str:
    """Create the LLM prompt for schema generation."""

    # Extract language info from template
    lang_code = template['language']['code']
    lang_name = template['language']['name']

    # Replace [TARGET LANGUAGE] placeholder
    prompt = instructions.replace('[TARGET LANGUAGE]', lang_name)

    # Add specific context about what needs to be filled
    prompt += f"""

TARGET LANGUAGE: {lang_name} ({lang_code})

IMPORTANT: Only fill these specific fields in the JSON structure:
- style.name_native
- style.description
- rules.consonants (all 27 entries: 22 letters + 5 final forms)
- rules.vowels_nikud (all 9 nikud)
- rules.composite (optional, only if needed)
- examples.*.translit (for all 27 examples)
- examples.*.guide (translit with CAPITALS on stressed syllable)
- examples.*.guide_full.reference (simple, everyday words)
- examples.*.guide_full.stress_note ("stress on [SYLLABLE]")
- examples.*.guide_full.phonetic_notes (1-2 short notes)

DO NOT change any other fields, especially stress_syllable values.

Output ONLY valid JSON, no explanations, no markdown."""

    return prompt


def extract_json_from_response(response: str) -> Dict[str, Any]:
    """Extract JSON from LLM response, handling various formats."""
    # Try to find JSON in the response
    response = response.strip()

    # Remove markdown code blocks if present
    if response.startswith('```json'):
        response = response[7:]
    if response.startswith('```'):
        response = response[3:]
    if response.endswith('```'):
        response = response[:-3]

    response = response.strip()

    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Response was: {response[:500]}...")
        raise


def merge_llm_output(template: Dict[str, Any], llm_output: Dict[str, Any]) -> Dict[str, Any]:
    """Merge LLM-generated fields into the template."""

    # Deep merge the LLM output into template
    def deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                deep_merge(target[key], value)
            else:
                target[key] = value
        return target

    return deep_merge(template.copy(), llm_output)


def main():
    parser = argparse.ArgumentParser(description='Generate Bani transliteration schema using LLM')
    parser.add_argument('--lang', required=True, help='Target language code (es, en, pt, etc.)')
    parser.add_argument('--model', default='gemma3:1b', help='Ollama model to use')
    parser.add_argument('--output', help='Output file path (default: schemas/informal.{lang}.jsonc)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Setup paths
    project_root = Path(__file__).parent.parent
    schema_path = project_root / 'SCHEMA.jsonc'
    instructions_path = project_root / 'INSTRUCTIONS.md'
    output_path = Path(args.output) if args.output else project_root / 'schemas' / f'informal.{args.lang}.jsonc'

    # Ensure schemas directory exists
    output_path.parent.mkdir(exist_ok=True)

    print(f"Generating schema for language: {args.lang}")
    print(f"Using model: {args.model}")
    print(f"Output: {output_path}")

    # Load template and instructions
    try:
        template = load_jsonc(schema_path)
        with open(instructions_path, 'r', encoding='utf-8') as f:
            instructions = f.read()
    except FileNotFoundError as e:
        print(f"Error: Required file not found: {e}")
        return 1
    except Exception as e:
        print(f"Error loading files: {e}")
        return 1

    # Update template language
    template['language']['code'] = args.lang
    # You might want to add language name mapping here
    lang_names = {
        'es': 'Spanish',
        'en': 'English',
        'pt': 'Portuguese',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian'
    }
    template['language']['name'] = lang_names.get(args.lang, args.lang.title())
    template['style']['name'] = f"Informal {template['language']['name']} Transliteration"

    # Create prompt
    prompt = create_prompt(instructions, template, args.lang)

    if args.verbose:
        print(f"Prompt length: {len(prompt)} characters")
        print("Prompt preview:")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)

    # Generate with LLM
    try:
        print("Generating with Ollama...")
        response = ollama.generate(
            model=args.model,
            prompt=prompt,
            options={
                'temperature': 0.1,  # Low temperature for consistent results
                'top_p': 0.9,
                'num_predict': 2048  # Allow longer responses
            }
        )

        llm_output = extract_json_from_response(response['response'])

        if args.verbose:
            print("LLM output keys:", list(llm_output.keys()))

    except Exception as e:
        print(f"Error with Ollama: {e}")
        print("Make sure Ollama is running and the model is available:")
        print(f"  ollama serve")
        print(f"  ollama pull {args.model}")
        return 1

    # Merge results
    final_schema = merge_llm_output(template, llm_output)

    # Update validation status
    final_schema['validation']['status'] = 'pending_review'

    # Save result
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_schema, f, indent=2, ensure_ascii=False)
        print(f"Schema generated successfully: {output_path}")
        print("Next steps:")
        print(f"1. Review the generated schema: {output_path}")
        print("2. Validate with: python scripts/validate.py schemas/informal.{args.lang}.jsonc"
        print("3. Apply to dataset: python scripts/apply.py schemas/informal.{args.lang}.jsonc"
    except Exception as e:
        print(f"Error saving file: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())








