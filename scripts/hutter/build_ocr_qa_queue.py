from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.hutter.build_api_fix_queue import DEFAULT_RESULTS_ROOT, latest_rows, manifest_context
from scripts.hutter.review_api_results import likely_crop_issue
from scripts.hutter.verse_images import DEFAULT_MANIFEST_ROOT, REPO_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a QA queue for Hutter OCR rows that need text validation, not crop repair."
    )
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--manifest-root", type=Path, default=DEFAULT_MANIFEST_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "data" / "hutter" / "review_reports" / "api_ocr_qa_queue.json",
    )
    return parser.parse_args()


def confidence_rank(value: Any) -> int:
    return {"low": 0, "medium": 1, "high": 2}.get(str(value).lower(), 3)


def source_file_from_id(row_id: str) -> str:
    return f"{row_id.rsplit('.', 1)[-1]}.png"


def main() -> int:
    args = parse_args()
    results_root = args.results_root.expanduser().resolve()
    manifest_root = args.manifest_root.expanduser().resolve()
    output_path = args.output.expanduser().resolve()

    items: list[dict[str, Any]] = []
    for review_path in sorted(results_root.glob("*/review.json")):
        book = review_path.parent.name
        context = manifest_context(book, manifest_root)
        by_id = context.get("by_id", {})
        rows = latest_rows(review_path.parent / "results.jsonl")
        for row_id, row in sorted(rows.items()):
            if row.get("status") != "ok":
                continue
            if not row.get("needs_review"):
                continue
            text = str(row.get("hebrew_text", "")).strip()
            has_marks = bool(row.get("has_hebrew_marks"))
            if not text or not has_marks:
                continue
            if likely_crop_issue(row):
                continue
            manifest_entry = by_id.get(row_id, {})
            source_file = str(manifest_entry.get("source_file") or source_file_from_id(row_id))
            items.append(
                {
                    "id": row_id,
                    "book": book,
                    "source_file": source_file,
                    "confidence": row.get("confidence"),
                    "needs_review": bool(row.get("needs_review")),
                    "notes": row.get("notes"),
                    "hebrew_text": row.get("hebrew_text"),
                    "output_image": row.get("output_image"),
                    "source_image": manifest_entry.get("source_image"),
                    "crop_box": manifest_entry.get("crop_box"),
                }
            )

    items.sort(
        key=lambda item: (
            confidence_rank(item.get("confidence")),
            item["book"],
            item["source_file"],
            item["id"],
        )
    )
    report = {
        "item_count": len(items),
        "purpose": (
            "Rows here have Hebrew text and marks but were flagged by the model "
            "as uncertain. Review these after crop repairs so we avoid paid reruns "
            "for cases that only need text validation."
        ),
        "items": items,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Report: {output_path}")
    print(f"Items: {len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
