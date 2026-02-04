#!/usr/bin/env python3
"""
Rebuild consolidated lexicon files from per-entry JSON files.

Reads data/dict/lexicon/roots/*.json and words/*.json and writes
pretty-printed roots.json and words.json. Optionally deletes
roots.pretty.json and words.pretty.json after successful rebuild.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Tuple


# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild consolidated lexicon JSON files from per-entry files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview counts without writing output files",
    )
    parser.add_argument(
        "--keep-pretty",
        action="store_true",
        help="Do not delete legacy roots.pretty.json/words.pretty.json",
    )
    return parser.parse_args()


def load_entries(entries_dir: Path) -> Tuple[Dict[str, dict], int]:
    """Load all JSON entries from a directory without any modifications."""
    entries: Dict[str, dict] = {}
    skipped = 0

    for entry_path in sorted(entries_dir.glob("*.json")):
        try:
            with entry_path.open("r", encoding="utf-8") as handle:
                entry = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {entry_path}: {exc}") from exc

        strong_number = entry.get("strong_number") or entry_path.stem
        if not strong_number:
            skipped += 1
            continue

        if strong_number in entries:
            raise ValueError(f"Duplicate entry for {strong_number} in {entry_path}")

        # Store entry exactly as-is
        entries[strong_number] = entry

    return entries, skipped


def write_consolidated(output_path: Path, entries: Dict[str, dict], dry_run: bool) -> None:
    """Write consolidated JSON file without any modifications."""
    if dry_run:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(entries, handle, ensure_ascii=False, indent=2)


def delete_legacy_pretty(lexicon_dir: Path, dry_run: bool, keep_pretty: bool) -> None:
    if dry_run or keep_pretty:
        return

    for pretty_name in ("roots.pretty.json", "words.pretty.json"):
        pretty_path = lexicon_dir / pretty_name
        if pretty_path.exists():
            pretty_path.unlink()


def main() -> int:
    args = parse_args()

    lexicon_dir = config.LEXICON_DIR
    roots_dir = config.LEXICON_ROOTS_DIR
    words_dir = config.LEXICON_WORDS_DIR

    if not roots_dir.exists():
        raise FileNotFoundError(f"Roots directory not found: {roots_dir}")
    if not words_dir.exists():
        raise FileNotFoundError(f"Words directory not found: {words_dir}")

    roots, roots_skipped = load_entries(roots_dir)
    words, words_skipped = load_entries(words_dir)

    print(f"Loaded {len(roots)} roots ({roots_skipped} skipped)")
    print(f"Loaded {len(words)} words ({words_skipped} skipped)")

    write_consolidated(lexicon_dir / "roots.json", roots, args.dry_run)
    write_consolidated(lexicon_dir / "words.json", words, args.dry_run)

    delete_legacy_pretty(lexicon_dir, args.dry_run, args.keep_pretty)

    if args.dry_run:
        print("Dry run complete. No files were written.")
    else:
        print("Rebuild complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

