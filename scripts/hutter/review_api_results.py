from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.hutter.process_verses_api import DEFAULT_RESULTS_ROOT, HEBREW_MARKS
from scripts.hutter.verse_images import REPO_ROOT


LIKELY_CROP_ISSUE_TERMS = (
    "crop",
    "cropped",
    "cut off",
    "not visible",
    "only spanish",
    "spanish text",
    "non-hebrew",
    "neighboring",
    "previous crop",
    "next crop",
    "adjacent",
    "continues",
    "continuation",
    "incomplete",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review Hutter API OCR result JSONL files.")
    parser.add_argument("book", help="Book key, for example colossians.")
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON review report path. Defaults to data/hutter/api_results/<book>/review.json.",
    )
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"Missing results file: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def has_marks(text: str) -> bool:
    return any(character in HEBREW_MARKS for character in text)


def likely_crop_issue(row: dict[str, Any]) -> bool:
    note = str(row.get("notes", "")).lower()
    return any(term in note for term in LIKELY_CROP_ISSUE_TERMS)


def main() -> int:
    args = parse_args()
    results_dir = args.results_root.expanduser().resolve() / args.book
    results_path = results_dir / "results.jsonl"
    batches_path = results_dir / "batches.jsonl"
    output_path = args.output.expanduser().resolve() if args.output else results_dir / "review.json"

    rows = load_jsonl(results_path)
    batches = load_jsonl(batches_path) if batches_path.exists() else []

    status_counts: Counter[str] = Counter(str(row.get("status")) for row in rows)
    confidence_counts: Counter[str] = Counter(str(row.get("confidence")) for row in rows)
    no_marks = [row for row in rows if not has_marks(str(row.get("hebrew_text", "")))]
    empty = [row for row in rows if not str(row.get("hebrew_text", "")).strip()]
    needs_review = [
        row
        for row in rows
        if row.get("needs_review")
        or not has_marks(str(row.get("hebrew_text", "")))
        or not str(row.get("hebrew_text", "")).strip()
    ]
    likely_crop_issues = [row for row in needs_review if likely_crop_issue(row)]
    likely_ocr_issues = [row for row in needs_review if not likely_crop_issue(row)]
    usage = Counter()
    for batch in batches:
        batch_usage = batch.get("usage") or {}
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            usage[key] += int(batch_usage.get(key) or 0)

    report = {
        "book": args.book,
        "result_count": len(rows),
        "batch_count": len(batches),
        "status_counts": dict(sorted(status_counts.items())),
        "confidence_counts": dict(sorted(confidence_counts.items())),
        "needs_review_count": len(needs_review),
        "likely_crop_issue_count": len(likely_crop_issues),
        "likely_ocr_issue_count": len(likely_ocr_issues),
        "no_hebrew_marks_count": len(no_marks),
        "empty_text_count": len(empty),
        "usage": dict(usage),
        "needs_review": [
            {
                "id": row.get("id"),
                "confidence": row.get("confidence"),
                "has_hebrew_marks": has_marks(str(row.get("hebrew_text", ""))),
                "notes": row.get("notes"),
                "output_image": row.get("output_image"),
                "hebrew_text": row.get("hebrew_text"),
            }
            for row in needs_review
        ],
        "likely_crop_issues": [
            {
                "id": row.get("id"),
                "confidence": row.get("confidence"),
                "notes": row.get("notes"),
                "output_image": row.get("output_image"),
                "hebrew_text": row.get("hebrew_text"),
            }
            for row in likely_crop_issues
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Report: {output_path}")
    print(f"Rows: {len(rows)}")
    print(f"Batches: {len(batches)}")
    print(f"Needs review: {len(needs_review)}")
    print(f"Likely crop issues: {len(likely_crop_issues)}")
    print(f"Likely OCR issues: {len(likely_ocr_issues)}")
    print(f"No Hebrew marks: {len(no_marks)}")
    if usage:
        print(f"Usage: {dict(usage)}")
    for row in needs_review[:10]:
        rel_path = row.get("output_image")
        image_path = REPO_ROOT / str(rel_path) if rel_path else None
        print(f"- {row.get('id')} {row.get('confidence')} {image_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
