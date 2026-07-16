from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from scripts.hutter.verse_images import DEFAULT_MANIFEST_ROOT, DEFAULT_OUTPUT_ROOT, DEFAULT_STAGING_ROOT, REPO_ROOT

try:
    from PIL import Image, ImageDraw
except ImportError as exc:  # pragma: no cover - this is an operational review script.
    raise SystemExit("Pillow is required for visual review sheets") from exc


NT_BOOKS = {
    "matthew",
    "mark",
    "luke",
    "john",
    "acts",
    "romans",
    "corinthians1",
    "corinthians2",
    "galatians",
    "ephesians",
    "philippians",
    "colossians",
    "thessalonians1",
    "thessalonians2",
    "timothy1",
    "timothy2",
    "titus",
    "philemon",
    "hebrews",
    "james",
    "peter1",
    "peter2",
    "john1",
    "john2",
    "john3",
    "jude",
    "revelation",
}


@dataclass(frozen=True)
class ReviewedCrop:
    book: str
    chapter: int
    verse: int
    source_file: str
    output_image: str
    width: int
    height: int
    dark_density: float
    top_dark_density: float
    bottom_dark_density: float
    middle_dark_density: float
    edge_density: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build repeatable local review reports and contact sheets for Hutter verse crops."
    )
    parser.add_argument("--staging-root", type=Path, default=DEFAULT_STAGING_ROOT)
    parser.add_argument("--manifest-root", type=Path, default=DEFAULT_MANIFEST_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT / "data" / "hutter" / "review_reports" / "verse_image_review.json",
    )
    parser.add_argument(
        "--sheets-dir",
        type=Path,
        default=REPO_ROOT / "data" / "hutter" / "review_reports" / "sheets",
    )
    parser.add_argument("--limit", type=int, default=48, help="Rows per review bucket.")
    return parser.parse_args()


def discover_source_availability(staging_root: Path) -> dict[str, Any]:
    output_root = staging_root / "output"
    images_root = staging_root / "data" / "images" / "hebrew_images"
    json_books = {path.stem for path in output_root.glob("*.json")}
    image_books = {
        path.name
        for path in images_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    } if images_root.exists() else set()

    processable = sorted(json_books & image_books)
    json_only = sorted(json_books - image_books)
    images_only = sorted(image_books - json_books)
    return {
        "json_book_count": len(json_books),
        "image_book_count": len(image_books),
        "processable_books": processable,
        "json_only_books": json_only,
        "images_only_books": images_only,
    }


def band_density(image: Image.Image, y0: int, y1: int) -> float:
    width, height = image.size
    x0 = int(width * 0.08)
    x1 = max(x0 + 1, int(width * 0.92))
    crop = image.crop((x0, max(0, y0), x1, min(height, y1)))
    histogram = crop.histogram()
    return sum(histogram[:160]) / max(1, sum(histogram))


def review_crop(entry: dict[str, Any]) -> ReviewedCrop | None:
    if entry.get("status") != "cropped" or not entry.get("output_image"):
        return None
    output_path = REPO_ROOT / str(entry["output_image"])
    if not output_path.exists():
        return None
    image = Image.open(output_path).convert("L")
    width, height = image.size
    band = min(24, height)
    top = band_density(image, 0, band)
    bottom = band_density(image, height - band, height)
    middle = band_density(image, height // 2 - band // 2, height // 2 + band // 2)
    full = band_density(image, int(height * 0.05), int(height * 0.95))
    return ReviewedCrop(
        book=str(entry["book"]),
        chapter=int(entry["chapter"]),
        verse=int(entry["verse"]),
        source_file=str(entry["source_file"]),
        output_image=str(entry["output_image"]),
        width=width,
        height=height,
        dark_density=round(full, 4),
        top_dark_density=round(top, 4),
        bottom_dark_density=round(bottom, 4),
        middle_dark_density=round(middle, 4),
        edge_density=round(max(top, bottom), 4),
    )


def load_reviewed_crops(manifest_root: Path) -> tuple[list[ReviewedCrop], Counter[str], Counter[str]]:
    reviewed: list[ReviewedCrop] = []
    statuses: Counter[str] = Counter()
    book_statuses: Counter[str] = Counter()
    for manifest_path in sorted(manifest_root.glob("*_verse_images.json")):
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        book = str(payload["book"])
        for entry in payload.get("entries", []):
            status = str(entry["status"])
            statuses[status] += 1
            book_statuses[f"{book}:{status}"] += 1
            crop = review_crop(entry)
            if crop is not None:
                reviewed.append(crop)
    return reviewed, statuses, book_statuses


def first_last_by_book(crops: list[ReviewedCrop]) -> list[ReviewedCrop]:
    by_book: dict[str, list[ReviewedCrop]] = defaultdict(list)
    for crop in crops:
        by_book[crop.book].append(crop)

    selected: list[ReviewedCrop] = []
    for book in sorted(by_book):
        rows = sorted(by_book[book], key=lambda item: (item.chapter, item.verse, item.source_file))
        selected.extend(rows[:2])
        selected.extend(rows[-2:])
    return dedupe_crops(selected)


def dedupe_crops(crops: list[ReviewedCrop]) -> list[ReviewedCrop]:
    seen: set[tuple[str, int, int, str]] = set()
    result: list[ReviewedCrop] = []
    for crop in crops:
        key = (crop.book, crop.chapter, crop.verse, crop.source_file)
        if key in seen:
            continue
        seen.add(key)
        result.append(crop)
    return result


def write_sheet(crops: list[ReviewedCrop], path: Path, columns: int = 4, thumb_width: int = 300) -> None:
    if not crops:
        return
    label_height = 34
    padding = 10
    cells: list[Image.Image] = []
    for crop in crops:
        image = Image.open(REPO_ROOT / crop.output_image).convert("RGB")
        thumb_height = max(1, int(image.height * thumb_width / image.width))
        image = image.resize((thumb_width, thumb_height))
        cell = Image.new("RGB", (thumb_width, thumb_height + label_height), "white")
        cell.paste(image, (0, label_height))
        label = f"{crop.book} {crop.chapter}:{crop.verse} h={crop.height} d={crop.dark_density:.2f}"
        ImageDraw.Draw(cell).text((5, 6), label, fill=(0, 0, 0))
        cells.append(cell)

    row_count = (len(cells) + columns - 1) // columns
    row_heights = [
        max(cell.height for cell in cells[row * columns : min((row + 1) * columns, len(cells))])
        for row in range(row_count)
    ]
    sheet = Image.new(
        "RGB",
        (
            columns * thumb_width + (columns + 1) * padding,
            sum(row_heights) + (row_count + 1) * padding,
        ),
        "white",
    )
    y = padding
    for row in range(row_count):
        x = padding
        for cell in cells[row * columns : min((row + 1) * columns, len(cells))]:
            sheet.paste(cell, (x, y))
            x += thumb_width + padding
        y += row_heights[row] + padding

    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)


def main() -> int:
    args = parse_args()
    staging_root = args.staging_root.expanduser().resolve()
    manifest_root = args.manifest_root.expanduser().resolve()
    report_path = args.report.expanduser().resolve()
    sheets_dir = args.sheets_dir.expanduser().resolve()

    availability = discover_source_availability(staging_root)
    crops, statuses, book_statuses = load_reviewed_crops(manifest_root)
    low_density = sorted(
        [crop for crop in crops if crop.dark_density < 0.035],
        key=lambda crop: crop.dark_density,
    )
    shortest = sorted(crops, key=lambda crop: (crop.height, crop.dark_density))[: args.limit]
    highest_edge = sorted(crops, key=lambda crop: crop.edge_density, reverse=True)[: args.limit]
    endings = first_last_by_book(crops)

    sheets = {
        "shortest": sheets_dir / "shortest_crops.png",
        "highest_edge": sheets_dir / "highest_edge_crops.png",
        "first_last": sheets_dir / "first_last_by_book.png",
    }
    write_sheet(shortest, sheets["shortest"])
    write_sheet(highest_edge, sheets["highest_edge"])
    write_sheet(endings, sheets["first_last"])
    if low_density:
        low_density_sheet = sheets_dir / "low_density_crops.png"
        write_sheet(low_density[: args.limit], low_density_sheet)
        sheets["low_density"] = low_density_sheet

    report = {
        "source_availability": availability,
        "status_counts": dict(sorted(statuses.items())),
        "book_status_counts": dict(sorted(book_statuses.items())),
        "reviewed_crop_count": len(crops),
        "low_density_threshold": 0.035,
        "low_density_count": len(low_density),
        "shortest_crops": [asdict(crop) for crop in shortest],
        "highest_edge_crops": [asdict(crop) for crop in highest_edge],
        "low_density_crops": [asdict(crop) for crop in low_density[: args.limit]],
        "sheets": {name: str(path.relative_to(REPO_ROOT)) for name, path in sheets.items()},
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Report: {report_path}")
    print(f"Reviewed crops: {len(crops)}")
    print(f"Status counts: {dict(sorted(statuses.items()))}")
    print(f"Low-density crops: {len(low_density)}")
    print(f"Sheets: {sheets_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
