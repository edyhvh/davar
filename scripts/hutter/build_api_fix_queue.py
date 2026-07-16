from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from scripts.hutter.process_verses_api import DEFAULT_RESULTS_ROOT
from scripts.hutter.review_api_results import likely_crop_issue
from scripts.hutter.verse_images import DEFAULT_MANIFEST_ROOT, REPO_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a focused fix queue from Hutter API OCR reviews.")
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--manifest-root", type=Path, default=DEFAULT_MANIFEST_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "data" / "hutter" / "review_reports" / "api_fix_queue.json",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_rows(results_path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not results_path.exists():
        return rows
    for line in results_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row_id = str(row.get("id", ""))
        if row_id:
            rows[row_id] = row
    return rows


def manifest_context(book: str, manifest_root: Path) -> dict[str, Any]:
    manifest_path = manifest_root / f"{book}_verse_images.json"
    if not manifest_path.exists():
        return {}
    payload = load_json(manifest_path)
    by_id: dict[str, dict[str, Any]] = {}
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in payload.get("entries", []):
        if entry.get("status") != "cropped":
            continue
        source_stem = Path(str(entry["source_file"])).stem
        entry_id = f"{book}.{int(entry['chapter'])}.{int(entry['verse'])}.{source_stem}"
        by_id[entry_id] = entry
        by_source[str(entry["source_file"])].append(entry)
    for entries in by_source.values():
        entries.sort(key=lambda item: (int(item["chapter"]), int(item["verse"])))
    return {"by_id": by_id, "by_source": dict(by_source)}


def classify(row: dict[str, Any]) -> str:
    text = str(row.get("hebrew_text", "")).strip()
    has_marks = bool(row.get("has_hebrew_marks"))
    status = str(row.get("status", ""))
    if status != "ok":
        return "missing_response"
    if not text:
        return "empty_target_crop"
    if not has_marks and likely_crop_issue(row):
        return "crop_no_marks"
    if not has_marks:
        return "ocr_no_marks"
    if likely_crop_issue(row):
        return "crop_boundary"
    if row.get("needs_review"):
        return "ocr_uncertain"
    return "ok"


def queue_priority(category: str) -> int:
    return {
        "missing_response": 0,
        "empty_target_crop": 1,
        "crop_no_marks": 2,
        "ocr_no_marks": 3,
        "crop_boundary": 4,
        "ocr_uncertain": 5,
    }.get(category, 9)


def source_file_from_id(row_id: str) -> str:
    return f"{row_id.rsplit('.', 1)[-1]}.png"


def main() -> int:
    args = parse_args()
    results_root = args.results_root.expanduser().resolve()
    manifest_root = args.manifest_root.expanduser().resolve()
    output_path = args.output.expanduser().resolve()

    items: list[dict[str, Any]] = []
    page_groups: dict[str, dict[str, Any]] = {}
    counts: Counter[str] = Counter()

    for review_path in sorted(results_root.glob("*/review.json")):
        book = review_path.parent.name
        rows = latest_rows(review_path.parent / "results.jsonl")
        context = manifest_context(book, manifest_root)
        by_id = context.get("by_id", {})
        by_source = context.get("by_source", {})
        for row_id, row in sorted(rows.items()):
            category = classify(row)
            if category == "ok":
                continue
            counts[category] += 1
            manifest_entry = by_id.get(row_id, {})
            source_file = str(manifest_entry.get("source_file") or source_file_from_id(row_id))
            page_key = f"{book}/{source_file}"
            source_entries = by_source.get(source_file, [])
            page_group = page_groups.setdefault(
                page_key,
                {
                    "book": book,
                    "source_file": source_file,
                    "source_image": manifest_entry.get("source_image"),
                    "affected_ids": [],
                    "verse_sequence": [
                        {
                            "id": f"{book}.{int(entry['chapter'])}.{int(entry['verse'])}.{Path(str(entry['source_file'])).stem}",
                            "chapter": int(entry["chapter"]),
                            "verse": int(entry["verse"]),
                            "crop_box": entry.get("crop_box"),
                            "output_image": entry.get("output_image"),
                        }
                        for entry in source_entries
                    ],
                },
            )
            page_group["affected_ids"].append(row_id)
            items.append(
                {
                    "id": row_id,
                    "book": book,
                    "category": category,
                    "priority": queue_priority(category),
                    "source_file": source_file,
                    "output_image": row.get("output_image"),
                    "crop_box": manifest_entry.get("crop_box"),
                    "confidence": row.get("confidence"),
                    "has_hebrew_marks": bool(row.get("has_hebrew_marks")),
                    "empty_text": not bool(str(row.get("hebrew_text", "")).strip()),
                    "notes": row.get("notes"),
                    "hebrew_text": row.get("hebrew_text"),
                }
            )

    page_list = sorted(
        page_groups.values(),
        key=lambda item: (
            min(queue_priority(next(entry["category"] for entry in items if entry["id"] == affected_id)) for affected_id in item["affected_ids"]),
            item["book"],
            item["source_file"],
        ),
    )
    items.sort(key=lambda item: (item["priority"], item["book"], item["source_file"], item["id"]))
    report = {
        "item_count": len(items),
        "page_count": len(page_list),
        "category_counts": dict(sorted(counts.items())),
        "items": items,
        "pages": page_list,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Report: {output_path}")
    print(f"Items: {len(items)}")
    print(f"Pages: {len(page_list)}")
    print(f"Categories: {dict(sorted(counts.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
