from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.hutter.process_verses_api import DEFAULT_RESULTS_ROOT
from scripts.hutter.verse_images import DEFAULT_MANIFEST_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize Hutter API OCR review reports.")
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--manifest-root", type=Path, default=DEFAULT_MANIFEST_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON output path. Defaults to <results-root>/summary.json.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_ids(book: str, manifest_root: Path) -> list[str]:
    manifest_path = manifest_root / f"{book}_verse_images.json"
    if not manifest_path.exists():
        return []
    payload = load_json(manifest_path)
    ids: list[str] = []
    for entry in payload.get("entries", []):
        if entry.get("status") != "cropped" or not entry.get("output_image"):
            continue
        source_file = Path(str(entry["source_file"])).stem
        ids.append(f"{book}.{int(entry['chapter'])}.{int(entry['verse'])}.{source_file}")
    return ids


def completed_ids(results_path: Path) -> set[str]:
    if not results_path.exists():
        return set()
    completed: set[str] = set()
    for line in results_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("status") == "ok":
            completed.add(str(row.get("id")))
    return completed


def main() -> int:
    args = parse_args()
    results_root = args.results_root.expanduser().resolve()
    manifest_root = args.manifest_root.expanduser().resolve()
    output_path = args.output.expanduser().resolve() if args.output else results_root / "summary.json"

    books: list[dict[str, Any]] = []
    totals: Counter[str] = Counter()
    confidence_totals: Counter[str] = Counter()
    status_totals: Counter[str] = Counter()

    for review_path in sorted(results_root.glob("*/review.json")):
        book = review_path.parent.name
        review = load_json(review_path)
        usage = review.get("usage") or {}
        confidence_counts = review.get("confidence_counts") or {}
        status_counts = review.get("status_counts") or {}
        expected_ids = manifest_ids(book, manifest_root)
        done_ids = completed_ids(review_path.parent / "results.jsonl")
        pending_ids = [verse_id for verse_id in expected_ids if verse_id not in done_ids]
        row = {
            "book": book,
            "manifest_verse_count": len(expected_ids),
            "result_count": int(review.get("result_count") or 0),
            "raw_result_count": int(review.get("raw_result_count") or review.get("result_count") or 0),
            "retry_row_count": int(review.get("raw_result_count") or review.get("result_count") or 0)
            - int(review.get("result_count") or 0),
            "pending_count": len(pending_ids),
            "pending_ids": pending_ids,
            "batch_count": int(review.get("batch_count") or 0),
            "needs_review_count": int(review.get("needs_review_count") or 0),
            "likely_crop_issue_count": int(review.get("likely_crop_issue_count") or 0),
            "likely_ocr_issue_count": int(review.get("likely_ocr_issue_count") or 0),
            "no_hebrew_marks_count": int(review.get("no_hebrew_marks_count") or 0),
            "empty_text_count": int(review.get("empty_text_count") or 0),
            "total_tokens": int(usage.get("total_tokens") or 0),
            "input_tokens": int(usage.get("input_tokens") or 0),
            "output_tokens": int(usage.get("output_tokens") or 0),
            "status_counts": status_counts,
            "confidence_counts": confidence_counts,
        }
        books.append(row)
        for key in (
            "manifest_verse_count",
            "result_count",
            "raw_result_count",
            "retry_row_count",
            "pending_count",
            "batch_count",
            "needs_review_count",
            "likely_crop_issue_count",
            "likely_ocr_issue_count",
            "no_hebrew_marks_count",
            "empty_text_count",
            "total_tokens",
            "input_tokens",
            "output_tokens",
        ):
            totals[key] += row[key]
        status_totals.update({key: int(value) for key, value in status_counts.items()})
        confidence_totals.update({key: int(value) for key, value in confidence_counts.items()})

    summary = {
        "book_count": len(books),
        "totals": dict(totals),
        "status_counts": dict(sorted(status_totals.items())),
        "confidence_counts": dict(sorted(confidence_totals.items())),
        "books": books,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Report: {output_path}")
    print(f"Books: {summary['book_count']}")
    print(f"Verses: {totals['result_count']}")
    print(f"Pending: {totals['pending_count']}")
    print(f"Needs review: {totals['needs_review_count']}")
    print(f"Likely crop issues: {totals['likely_crop_issue_count']}")
    print(f"Likely OCR issues: {totals['likely_ocr_issue_count']}")
    print(f"Empty text: {totals['empty_text_count']}")
    print(f"No Hebrew marks: {totals['no_hebrew_marks_count']}")
    print(f"Total tokens: {totals['total_tokens']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
