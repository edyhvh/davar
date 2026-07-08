from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from scripts.hutter.verse_images import (
    DEFAULT_MANIFEST_ROOT,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_OVERRIDES_PATH,
    DEFAULT_STAGING_ROOT,
    VerseImageEntry,
    build_manifest,
    load_crop_overrides,
    write_manifest,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate crops for selected Hutter source pages and merge the "
            "new entries into the existing full verse-image manifest."
        )
    )
    parser.add_argument("book", help="Book key, for example galatians.")
    parser.add_argument(
        "--source-files",
        required=True,
        help="Comma-separated source image file names to regenerate, for example 000042.png.",
    )
    parser.add_argument("--staging-root", type=Path, default=DEFAULT_STAGING_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest-root", type=Path, default=DEFAULT_MANIFEST_ROOT)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES_PATH)
    parser.add_argument("--padding", type=int, default=18)
    parser.add_argument("--horizontal-padding", type=int, default=6)
    parser.add_argument("--analysis-left-ratio", type=float, default=0.10)
    parser.add_argument("--analysis-right-ratio", type=float, default=0.70)
    parser.add_argument("--dark-threshold", type=int, default=160)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def entry_key(entry: dict[str, Any] | VerseImageEntry) -> tuple[str, int, int, str]:
    if isinstance(entry, VerseImageEntry):
        return (entry.book, entry.chapter, entry.verse, entry.source_file)
    return (
        str(entry["book"]),
        int(entry["chapter"]),
        int(entry["verse"]),
        str(entry["source_file"]),
    )


def load_existing_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Existing full manifest is required before targeted regeneration: {path}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    book = args.book.lower()
    source_files = {
        source_file.strip()
        for source_file in args.source_files.split(",")
        if source_file.strip()
    }
    if not source_files:
        raise ValueError("--source-files must include at least one page file")

    manifest_root = args.manifest_root.expanduser().resolve()
    manifest_path = manifest_root / f"{book}_verse_images.json"
    existing = load_existing_manifest(manifest_path)
    existing_entries = existing.get("entries", [])

    regenerated = build_manifest(
        book=book,
        staging_root=args.staging_root.expanduser().resolve(),
        output_root=args.output_root.expanduser().resolve(),
        manifest_only=False,
        crop_plan_only=args.dry_run,
        padding=args.padding,
        analysis_left_ratio=args.analysis_left_ratio,
        analysis_right_ratio=args.analysis_right_ratio,
        source_files=source_files,
        dark_threshold=args.dark_threshold,
        horizontal_padding=args.horizontal_padding,
        crop_overrides=load_crop_overrides(args.overrides.expanduser().resolve()),
    )
    regenerated_payloads = [asdict(entry) for entry in regenerated]
    regenerated_by_key = {entry_key(entry): entry for entry in regenerated_payloads}

    merged_entries: list[dict[str, Any]] = []
    replaced_keys: set[tuple[str, int, int, str]] = set()
    for entry in existing_entries:
        key = entry_key(entry)
        replacement = regenerated_by_key.get(key)
        if replacement is None:
            merged_entries.append(entry)
            continue
        merged_entries.append(replacement)
        replaced_keys.add(key)

    missing_replacements = sorted(set(regenerated_by_key) - replaced_keys)
    if missing_replacements:
        merged_entries.extend(regenerated_by_key[key] for key in missing_replacements)

    if args.dry_run:
        output_images = [entry.output_image for entry in regenerated if entry.output_image]
        print(f"Dry run: would merge {len(regenerated)} entries into {manifest_path}")
        print(f"Regenerated source files: {sorted(source_files)}")
        for output_image in output_images:
            print(f"- {output_image}")
        return 0

    write_manifest(
        book,
        manifest_root,
        [
            VerseImageEntry(
                book=str(entry["book"]),
                chapter=int(entry["chapter"]),
                verse=int(entry["verse"]),
                source_file=str(entry["source_file"]),
                source_image=str(entry["source_image"]),
                output_image=entry.get("output_image"),
                crop_box=entry.get("crop_box"),
                status=str(entry["status"]),
                notes=list(entry.get("notes") or []),
            )
            for entry in merged_entries
        ],
    )

    print(f"Manifest: {manifest_path}")
    print(f"Merged regenerated entries: {len(regenerated)}")
    print(f"Regenerated source files: {sorted(source_files)}")
    for entry in regenerated:
        source_stem = Path(entry.source_file).stem
        print(f"- {entry.book}.{entry.chapter}.{entry.verse}.{source_stem} {entry.output_image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
