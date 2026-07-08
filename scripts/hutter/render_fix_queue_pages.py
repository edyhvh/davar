from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.hutter.verse_images import REPO_ROOT

try:
    from PIL import Image, ImageDraw
except ImportError as exc:  # pragma: no cover - operational script.
    raise SystemExit("Pillow is required for fix queue page rendering") from exc


DEFAULT_QUEUE = REPO_ROOT / "data" / "hutter" / "review_reports" / "api_fix_queue.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "hutter" / "review_reports" / "api_fix_pages"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render annotated source pages for Hutter OCR fix queue.")
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--categories",
        default="missing_response,empty_target_crop,crop_no_marks,ocr_no_marks",
        help="Comma-separated fix queue categories to render.",
    )
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def color_for(index: int, affected: bool) -> tuple[int, int, int]:
    if affected:
        return (220, 40, 40)
    palette = [
        (30, 100, 220),
        (20, 150, 80),
        (160, 80, 210),
        (220, 140, 20),
    ]
    return palette[index % len(palette)]


def draw_box(draw: ImageDraw.ImageDraw, box: dict[str, int], label: str, color: tuple[int, int, int]) -> None:
    left = int(box["left"])
    top = int(box["top"])
    right = int(box["right"])
    bottom = int(box["bottom"])
    for inset in range(3):
        draw.rectangle((left + inset, top + inset, right - inset, bottom - inset), outline=color)
    label_y = max(0, top - 18)
    draw.rectangle((left, label_y, min(right, left + 190), label_y + 16), fill=(255, 255, 255))
    draw.text((left + 3, label_y + 2), label, fill=color)


def main() -> int:
    args = parse_args()
    queue = load_json(args.queue.expanduser().resolve())
    output_dir = args.output_dir.expanduser().resolve()
    categories = {category.strip() for category in args.categories.split(",") if category.strip()}
    item_categories = {item["id"]: item["category"] for item in queue.get("items", [])}

    pages = [
        page
        for page in queue.get("pages", [])
        if any(item_categories.get(row_id) in categories for row_id in page.get("affected_ids", []))
    ]
    if args.limit is not None:
        pages = pages[: args.limit]

    rendered: list[dict[str, Any]] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for page in pages:
        source_image = page.get("source_image")
        if not source_image:
            continue
        source_path = REPO_ROOT / str(source_image)
        if not source_path.exists():
            continue
        image = Image.open(source_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        affected_ids = set(page.get("affected_ids", []))
        for index, verse in enumerate(page.get("verse_sequence", [])):
            box = verse.get("crop_box")
            if not box:
                continue
            verse_id = str(verse["id"])
            affected = verse_id in affected_ids
            label = f"{verse['chapter']}:{verse['verse']} {item_categories.get(verse_id, '')}"
            draw_box(draw, box, label, color_for(index, affected))

        output_path = output_dir / f"{page['book']}_{Path(page['source_file']).stem}.png"
        image.save(output_path)
        rendered.append(
            {
                "book": page["book"],
                "source_file": page["source_file"],
                "path": str(output_path.relative_to(REPO_ROOT)),
                "affected_ids": page.get("affected_ids", []),
            }
        )

    index_path = output_dir / "index.json"
    index_path.write_text(json.dumps(rendered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered pages: {len(rendered)}")
    print(f"Index: {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
