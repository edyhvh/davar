"""CLI script to validate all JSON files in output directory."""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

from .validate import (
    validate_chapter_object,
    validate_chapter_sequence,
    validate_verse_sequence
)
from .books import BOOK_STRUCTURE

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def validate_json_file(json_path: Path) -> tuple[bool, list[str]]:
    """Validate a single JSON file."""
    errors = []

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {str(e)}"]
    except Exception as e:
        return False, [f"Error reading file: {str(e)}"]

    # Check required top-level fields
    required_fields = ['book_name', 'chapters']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    book_name = data['book_name']

    # Validate book structure
    if book_name not in BOOK_STRUCTURE:
        errors.append(f"Unknown book name: {book_name}")
        return False, errors

    chapters = data.get('chapters', [])
    if not chapters:
        errors.append("No chapters found")
        return False, errors

    # Validate chapter sequence
    is_valid, error, missing = validate_chapter_sequence(chapters)
    if not is_valid:
        errors.append(f"Chapter sequence error: {error}")
        if missing:
            errors.append(f"Missing chapters: {missing}")

    # Validate each chapter
    for chapter in chapters:
        is_valid, error = validate_chapter_object(chapter)
        if not is_valid:
            chapter_num = chapter.get('number', 'unknown')
            errors.append(f"Chapter {chapter_num}: {error}")
            continue

        # Validate verse sequence within chapter
        verses = chapter.get('verses', [])
        if verses:
            is_valid, error, missing_verses = validate_verse_sequence(verses)
            if not is_valid:
                chapter_num = chapter.get('number', 'unknown')
                errors.append(f"Chapter {chapter_num} verse sequence: {error}")
                if missing_verses:
                    errors.append(f"Chapter {chapter_num} missing verses: {missing_verses}")

    return len(errors) == 0, errors


def validate_all_json_files(output_dir: Path) -> bool:
    """Validate all JSON files in output directory."""
    if not output_dir.exists():
        logger.error(f"Output directory not found: {output_dir}")
        return False

    json_files = sorted(output_dir.glob("*.json"))
    if not json_files:
        logger.warning(f"No JSON files found in {output_dir}")
        return True

    logger.info(f"Validating {len(json_files)} JSON files...")

    all_valid = True
    for json_file in json_files:
        logger.info(f"Validating {json_file.name}...")
        is_valid, errors = validate_json_file(json_file)

        if is_valid:
            logger.info(f"✓ {json_file.name} is valid")
        else:
            all_valid = False
            logger.error(f"✗ {json_file.name} has errors:")
            for error in errors:
                logger.error(f"  - {error}")

    return all_valid


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate JSON files in output directory"
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory containing JSON files (default: output)'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Validate a single JSON file'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose logging'
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.file:
        # Validate single file
        json_path = Path(args.file)
        if not json_path.exists():
            logger.error(f"File not found: {json_path}")
            sys.exit(1)

        is_valid, errors = validate_json_file(json_path)
        if is_valid:
            logger.info(f"✓ {json_path.name} is valid")
            sys.exit(0)
        else:
            logger.error(f"✗ {json_path.name} has errors:")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(1)
    else:
        # Validate all files in output directory
        output_dir = Path(args.output_dir)
        success = validate_all_json_files(output_dir)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

