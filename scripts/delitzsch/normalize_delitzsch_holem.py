#!/usr/bin/env python3
"""Normalize corrupted Delitzsch sin-dot-as-holem source text."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from .config import DELITZSCH_DIR
    from .hebrew_utils import normalize_delitzsch_holem
except ImportError:
    from config import DELITZSCH_DIR
    from hebrew_utils import normalize_delitzsch_holem


DEFAULT_BOOKS = tuple(path.stem for path in sorted(DELITZSCH_DIR.glob("*.json")))


@dataclass
class FileStats:
    changed: bool = False
    replacements: int = 0
    verses_changed: int = 0


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def iter_files(source_dir: Path, books: Iterable[str]) -> Iterable[Path]:
    for book in books:
        path = source_dir / f"{book}.json"
        if path.exists():
            yield path


def normalize_book_data(data: dict) -> FileStats:
    stats = FileStats()

    for chapter in data.get("chapters", []):
        for verse in chapter.get("verses", []):
            text = verse.get("text_nikud")
            if not isinstance(text, str):
                continue

            normalized = normalize_delitzsch_holem(text)
            if normalized == text:
                continue

            verse["text_nikud"] = normalized
            stats.changed = True
            stats.verses_changed += 1
            stats.replacements += sum(
                1 for before, after in zip(text, normalized) if before != after
            )

    return stats


def process_file(path: Path, dry_run: bool = False) -> FileStats:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = normalize_book_data(data)

    if stats.changed and not dry_run:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize corrupted sin dots to holem in Delitzsch source JSON",
    )
    parser.add_argument(
        "--books",
        nargs="+",
        default=DEFAULT_BOOKS,
        help="Book JSON names under data/delitzsch",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_dir = project_root() / "data" / "delitzsch"

    changed_files = 0
    changed_verses = 0
    replacements = 0

    for path in iter_files(source_dir, args.books):
        stats = process_file(path, dry_run=args.dry_run)
        if stats.changed:
            changed_files += 1
            changed_verses += stats.verses_changed
            replacements += stats.replacements
            print(
                f"updated: {path} "
                f"(verses: {stats.verses_changed}, replacements: {stats.replacements})"
            )

    mode = "DRY RUN" if args.dry_run else "WRITE"
    print(
        f"[{mode}] changed files: {changed_files}, "
        f"changed verses: {changed_verses}, replacements: {replacements}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
