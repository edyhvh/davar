"""Validation functions for schema and content."""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple

import jsonschema

logger = logging.getLogger(__name__)


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate JSON against schema."""
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Schema validation error: {str(e)}"


def validate_hebrew_text(text: str) -> Tuple[bool, Optional[str]]:
    """Verify Hebrew characters (Unicode U+0590-U+05FF)."""
    if not text:
        return False, "Text is empty"

    has_hebrew = bool(re.search(r'[\u0590-\u05FF]', text))
    if not has_hebrew:
        return False, "Text contains no Hebrew characters"

    invalid_chars = re.findall(r'[^\u0590-\u05FF\s\-\.,;:()\[\]{}"\']', text)
    if invalid_chars:
        return False, f"Text contains invalid characters: {set(invalid_chars)}"

    return True, None


def validate_verse_sequence(verses: List[Dict[str, Any]]) -> Tuple[bool, Optional[str], List[int]]:
    """Check verse numbers are sequential."""
    if not verses:
        return True, None, []

    verse_numbers = sorted([v.get('number') for v in verses if v.get('number') is not None])
    if not verse_numbers:
        return False, "No verse numbers found", []

    expected_set = set(range(verse_numbers[0], verse_numbers[-1] + 1))
    missing = sorted(list(expected_set - set(verse_numbers)))

    if missing:
        return False, f"Missing verses: {missing}", missing
    return True, None, []


def validate_chapter_sequence(chapters: List[Dict[str, Any]]) -> Tuple[bool, Optional[str], List[int]]:
    """Check chapter numbers are sequential."""
    if not chapters:
        return True, None, []

    chapter_numbers = sorted([c.get('number') for c in chapters if c.get('number') is not None])
    if not chapter_numbers:
        return False, "No chapter numbers found", []

    expected_set = set(range(chapter_numbers[0], chapter_numbers[-1] + 1))
    missing = sorted(list(expected_set - set(chapter_numbers)))

    if missing:
        return False, f"Missing chapters: {missing}", missing
    return True, None, []


def validate_verse_object(verse: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate a single verse object."""
    required_fields = ['text_nikud', 'source_files', 'number']
    for field in required_fields:
        if field not in verse:
            return False, f"Missing required field: {field}"

    if not isinstance(verse['number'], int):
        return False, f"Verse number must be int, got {type(verse['number'])}"
    if not isinstance(verse['text_nikud'], str):
        return False, f"text_nikud must be string, got {type(verse['text_nikud'])}"
    if not isinstance(verse['source_files'], list):
        return False, f"source_files must be list, got {type(verse['source_files'])}"
    if not verse['text_nikud'].strip():
        return False, "text_nikud is empty"

    is_valid, error = validate_hebrew_text(verse['text_nikud'])
    if not is_valid:
        return False, f"Invalid Hebrew text: {error}"

    if not verse['source_files']:
        return False, "source_files is empty"

    if 'visual_uncertainty' in verse and not isinstance(verse['visual_uncertainty'], list):
        return False, f"visual_uncertainty must be list, got {type(verse['visual_uncertainty'])}"

    return True, None


def validate_chapter_object(chapter: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate a single chapter object."""
    required_fields = ['hebrew_letter', 'number', 'verses']
    for field in required_fields:
        if field not in chapter:
            return False, f"Missing required field: {field}"

    if not isinstance(chapter['number'], int):
        return False, f"Chapter number must be int, got {type(chapter['number'])}"
    if not isinstance(chapter['hebrew_letter'], str):
        return False, f"hebrew_letter must be string, got {type(chapter['hebrew_letter'])}"
    if not isinstance(chapter['verses'], list):
        return False, f"verses must be list, got {type(chapter['verses'])}"

    hebrew_letter = chapter['hebrew_letter']
    if len(hebrew_letter) < 1 or len(hebrew_letter) > 3:
        return False, f"hebrew_letter must be 1-3 characters, got '{hebrew_letter}'"
    if not re.match(r'^[\u0590-\u05FF]+$', hebrew_letter):
        return False, f"hebrew_letter must contain only Hebrew characters"

    if not chapter['verses']:
        return False, "Chapter has no verses"

    for verse in chapter['verses']:
        is_valid, error = validate_verse_object(verse)
        if not is_valid:
            return False, f"Invalid verse: {error}"

    return True, None


def parse_json_response(response_text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Parse JSON response from API."""
    if not response_text:
        return None, "Empty response"

    # Try markdown code blocks first
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            return None, "No JSON found in response"

    try:
        return json.loads(json_str), None
    except json.JSONDecodeError as e:
        return None, f"Failed to parse JSON: {str(e)}"

