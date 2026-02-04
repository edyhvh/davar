#!/usr/bin/env python3
"""
Merge individual lexicon entry files into consolidated roots.json and words.json.

This script aggregates all individual JSON files into consolidated files,
while preserving text_es fields from existing consolidated files.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from config import config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge individual lexicon entries into consolidated JSON files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview counts without writing output files",
    )
    return parser.parse_args()


def load_existing_consolidated(file_path: Path) -> Dict[str, dict]:
    """Load existing consolidated file if it exists."""
    if not file_path.exists():
        return {}
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def preserve_text_es(new_definitions: List[dict], old_definitions: List[dict]) -> List[dict]:
    """
    Preserve text_es fields from old definitions into new definitions.
    Matches definitions by text_en and sense.
    """
    if not old_definitions:
        return new_definitions

    # Build lookup from old definitions by (text_en, sense) -> text_es
    old_lookup: Dict[Tuple[str, str], str] = {}
    for old_def in old_definitions:
        text_en = old_def.get("text_en", "")
        sense = old_def.get("sense", "0")
        text_es = old_def.get("text_es")
        if text_es:
            old_lookup[(text_en, sense)] = text_es

    if not old_lookup:
        return new_definitions

    # Apply text_es to new definitions
    for new_def in new_definitions:
        text_en = new_def.get("text_en", "")
        sense = new_def.get("sense", "0")
        key = (text_en, sense)
        if key in old_lookup and "text_es" not in new_def:
            new_def["text_es"] = old_lookup[key]

    return new_definitions


def merge_directory(entries_dir: Path, existing_consolidated: Dict[str, dict]) -> Tuple[Dict[str, dict], int, int]:
    """
    Merge all JSON files from a directory into a single dictionary,
    preserving text_es fields from existing consolidated data.
    """
    entries: Dict[str, dict] = {}
    skipped = 0
    preserved_count = 0

    for entry_path in sorted(entries_dir.glob("*.json")):
        try:
            with entry_path.open("r", encoding="utf-8") as f:
                entry = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"⚠️  Skipping {entry_path}: {exc}")
            skipped += 1
            continue

        strong_number = entry.get("strong_number") or entry_path.stem
        if not strong_number:
            skipped += 1
            continue

        # Preserve text_es from existing consolidated file
        if strong_number in existing_consolidated:
            old_entry = existing_consolidated[strong_number]
            old_definitions = old_entry.get("definitions", [])
            new_definitions = entry.get("definitions", [])

            # Check if any text_es will be preserved
            has_text_es_before = any("text_es" in d for d in new_definitions)
            entry["definitions"] = preserve_text_es(new_definitions, old_definitions)
            has_text_es_after = any("text_es" in d for d in entry.get("definitions", []))

            if not has_text_es_before and has_text_es_after:
                preserved_count += 1

        entries[strong_number] = entry

    return entries, skipped, preserved_count


def write_output(output_path: Path, entries: Dict[str, dict], dry_run: bool) -> None:
    """Write merged entries to consolidated JSON file."""
    if dry_run:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"✅ Wrote {len(entries)} entries to {output_path}")


def main() -> int:
    args = parse_args()

    lexicon_dir = config.LEXICON_DIR
    roots_dir = config.LEXICON_ROOTS_DIR
    words_dir = config.LEXICON_WORDS_DIR

    if not roots_dir.exists():
        print(f"❌ Roots directory not found: {roots_dir}")
        return 1
    if not words_dir.exists():
        print(f"❌ Words directory not found: {words_dir}")
        return 1

    # Load existing consolidated files to preserve text_es
    print("Loading existing consolidated files...")
    existing_roots = load_existing_consolidated(lexicon_dir / "roots.json")
    existing_words = load_existing_consolidated(lexicon_dir / "words.json")
    print(f"  Found {len(existing_roots)} existing roots, {len(existing_words)} existing words")

    print("Merging lexicon entries...")
    roots, roots_skipped, roots_preserved = merge_directory(roots_dir, existing_roots)
    words, words_skipped, words_preserved = merge_directory(words_dir, existing_words)

    print(f"📚 Roots: {len(roots)} entries ({roots_skipped} skipped, {roots_preserved} with text_es preserved)")
    print(f"📚 Words: {len(words)} entries ({words_skipped} skipped, {words_preserved} with text_es preserved)")

    if args.dry_run:
        print("🔍 Dry run - no files written")
        return 0

    write_output(lexicon_dir / "roots.json", roots, False)
    write_output(lexicon_dir / "words.json", words, False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
