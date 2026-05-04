"""Prompt building from YAML configuration."""

import yaml
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML configuration file."""
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not data:
        raise ValueError(f"YAML file is empty: {path}")

    return data


def get_yaml_version(yaml_data: Dict[str, Any]) -> str:
    """Extract version from YAML metadata."""
    return yaml_data.get('metadata', {}).get('version', 'unknown')


def calculate_yaml_hash(yaml_content: str) -> str:
    """Generate SHA256 hash for versioning."""
    return hashlib.sha256(yaml_content.encode('utf-8')).hexdigest()


def build_prompt(yaml_data: Dict[str, Any]) -> str:
    """Construct full prompt from YAML rules."""
    vision_template = yaml_data.get('vision_prompt_template', {})
    role = vision_template.get('role', 'Expert Paleographer')
    task = vision_template.get('task', '')

    parts = [f"You are {role}.\n\n{task}\n"]

    # Critical rules header
    parts.append("## ⚠️ CRITICAL TRANSCRIPTION RULES - READ FIRST\n")
    parts.append("🔴 WORD SPACING: Every word MUST be separated by a space. NEVER concatenate words.")
    parts.append("🔴 CORRECT: 'וְנַצְרוּ אֶת־נַפְשׁוֹתֵיכֶם בְּאַהֲבַת אֱלֹהִים'")
    parts.append("🔴 WRONG: 'וְנַצְרוּאֶת־נַפְשׁוֹתֵיכֶםבְּאַהֲבַתאֱלֹהִים'")
    parts.append("🔴 NEVER include ׃ (Sof Pasuq) in 'text_nikud' - EXCLUDE COMPLETELY")
    parts.append("🔴 NEVER include \\n or line breaks in 'text_nikud' - ONE CONTINUOUS STRING ONLY")
    parts.append("🔴 COLUMN ISOLATION: ONLY transcribe the CENTRAL Hebrew column. Ignore Latin, Greek, German.")
    parts.append("🔴 If you violate these rules, the transcription is INVALID\n")

    # Text layout rules
    layout_rules = yaml_data.get('text_layout_rules', {})

    for rule_name in ['word_spacing', 'hutter_typography', 'column_isolation', 'character_confusion', 'paleographic_priority', 'lexical_fidelity']:
        rule = layout_rules.get(rule_name, {})
        if rule.get('rule'):
            parts.append(f"\n## {rule_name.replace('_', ' ').title()}\n{rule['rule']}")
            if rule.get('description'):
                parts.append(f"\n{rule['description']}")

    # Advanced vocalization
    advanced_voc = layout_rules.get('advanced_vocalization', {})
    if advanced_voc:
        parts.append("\n## Advanced Vocalization Rules")
        for sub_rule in ['hataf_vowels', 'vav_distinction', 'dagesh_verification', 'composite_marks']:
            r = advanced_voc.get(sub_rule, {})
            if r.get('rule'):
                parts.append(f"\n### {sub_rule.replace('_', ' ').title()}\n{r['rule']}")

    # Ornamented initials
    ornamented = layout_rules.get('ornamented_initials', {})
    if ornamented.get('rule'):
        parts.append(f"\n## Ornamented Initial Letters\n{ornamented['rule']}")

    # Auxiliary text to ignore
    auxiliary = layout_rules.get('auxiliary_hebrew_text_to_ignore', {})
    root_markers = auxiliary.get('root_markers', {})
    if root_markers.get('rule'):
        parts.append(f"\n## Auxiliary Hebrew Text to Ignore\n{root_markers['rule']}")

    # Normalization rules
    normalization = layout_rules.get('normalization_rules', {})
    if normalization:
        parts.append("\n## ⚠️ CRITICAL NORMALIZATION RULES")

        if normalization.get('makaf', {}).get('rule'):
            parts.append(f"\n### Makaf\n{normalization['makaf']['rule']}")

        sof_pasuq = normalization.get('sof_pasuq', {})
        if sof_pasuq.get('rule'):
            parts.extend([
                "\n### 🚫 SOF PASUQ (׃) - FORBIDDEN",
                sof_pasuq['rule'],
                "🔴 NEVER include ׃ in 'text_nikud'",
                "✅ CORRECT: 'דָּבָר' (without ׃)",
                "❌ WRONG: 'דָּבָר׃' (with ׃)"
            ])

        parts.extend([
            "\n### 🚫 LINE BREAKS - FORBIDDEN",
            "🔴 NEVER include \\n or line breaks in 'text_nikud'",
            "🔴 'text_nikud' MUST be one continuous string"
        ])

        if normalization.get('parentheses', {}).get('rule'):
            parts.append(f"\n### Parentheses\n{normalization['parentheses']['rule']}")

    # Special instructions
    parts.extend([
        "\n## Special Instructions",
        "- The first verse uses an ornamented letter - include it.",
        "- Verses are marked with Arabic numerals in the right margin.",
        "- Chapters are marked with large centered Hebrew letters."
    ])

    # Chapter/verse identification
    parts.extend([
        "\n## CHAPTER AND VERSE IDENTIFICATION",
        "- Chapters: LARGE CENTERED Hebrew letters (א=1, ב=2, etc.)",
        "- Verses: Arabic numerals in right margin",
        "- Report ACTUAL verse numbers you see, not starting from 1.",
        "- Extract ONLY text visible in THIS SPECIFIC IMAGE."
    ])

    # Output format
    if yaml_data.get('output_specification'):
        parts.extend([
            "\n## Output Format",
            "Return a JSON object:",
            """{
  "chapters": [{
    "hebrew_letter": "א",
    "number": 1,
    "verses": [{
      "number": 1,
      "text_nikud": "בְּרֵאשִׁית בָּרָא...",
      "source_files": ["000002.png"],
      "visual_uncertainty": []
    }]
  }]
}"""
        ])

    # User sovereignty
    user_rule = yaml_data.get('user_sovereignty_rule', {})
    if user_rule.get('description'):
        parts.append(f"\n## User Sovereignty Rule\n{user_rule['description']}")

    return "\n".join(parts)

