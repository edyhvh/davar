from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from scripts.hutter.verse_images import DEFAULT_MANIFEST_ROOT, REPO_ROOT, read_png_rgb

try:
    from PIL import Image
except ImportError:  # pragma: no cover - stdlib PNG fallback is covered by read_png_rgb use.
    Image = None


@dataclass(frozen=True)
class CropRisk:
    book: str
    chapter: int
    verse: int
    source_file: str
    output_image: str
    width: int
    height: int
    top_dark_density: float
    bottom_dark_density: float
    middle_dark_density: float
    risk_score: float
    crop_box: dict[str, int] | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit generated Hutter verse crop images.")
    parser.add_argument(
        "--manifest-root",
        type=Path,
        default=DEFAULT_MANIFEST_ROOT,
        help=f"Manifest root (default: {DEFAULT_MANIFEST_ROOT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "data" / "hutter" / "review_reports" / "nt_verse_image_audit.json",
        help="JSON report path.",
    )
    parser.add_argument("--top", type=int, default=250, help="Number of top crop risks to store.")
    return parser.parse_args()


def dark_density(image_path: Path) -> tuple[int, int, float, float, float]:
    if Image is not None:
        image = Image.open(image_path).convert("L")
        width, height = image.size

        def density_pil(y0: int, y1: int) -> float:
            x0 = int(width * 0.08)
            x1 = max(x0 + 1, int(width * 0.92))
            crop = image.crop((x0, max(0, y0), x1, min(height, y1)))
            histogram = crop.histogram()
            dark = sum(histogram[:150])
            total = sum(histogram)
            return dark / max(1, total)

        band = min(24, height)
        top = density_pil(0, band)
        bottom = density_pil(height - band, height)
        middle = density_pil(height // 2 - band // 2, height // 2 + band // 2)
        return width, height, top, bottom, middle

    image = read_png_rgb(image_path)
    stride = image.width * 3

    def density(y0: int, y1: int) -> float:
        x0 = int(image.width * 0.08)
        x1 = max(x0 + 1, int(image.width * 0.92))
        dark = 0
        total = 0
        for y in range(max(0, y0), min(image.height, y1)):
            row = y * stride
            for x in range(x0, x1):
                offset = row + x * 3
                luminance = (
                    image.pixels[offset]
                    + image.pixels[offset + 1]
                    + image.pixels[offset + 2]
                ) // 3
                if luminance < 150:
                    dark += 1
                total += 1
        return dark / max(1, total)

    band = min(24, image.height)
    top = density(0, band)
    bottom = density(image.height - band, image.height)
    middle = density(image.height // 2 - band // 2, image.height // 2 + band // 2)
    return image.width, image.height, top, bottom, middle


def score_risk(width: int, height: int, top: float, bottom: float, middle: float) -> float:
    score = max(top, bottom) * 100
    if height < 140:
        score += 18
    if top > 0.13:
        score += 12
    if bottom > 0.13:
        score += 12
    if middle > 0.50 and (top > 0.20 or bottom > 0.20):
        score += 8
    if width < 450:
        score += 10
    return round(score, 4)


def audit_manifest(manifest_path: Path) -> tuple[list[CropRisk], Counter[str], Counter[str]]:
    risks: list[CropRisk] = []
    status_counts: Counter[str] = Counter()
    book_status_counts: Counter[str] = Counter()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    book = payload["book"]

    for entry in payload["entries"]:
        status = str(entry["status"])
        status_counts[status] += 1
        book_status_counts[f"{book}:{status}"] += 1
        if status != "cropped" or not entry.get("output_image"):
            continue

        output_path = REPO_ROOT / entry["output_image"]
        if not output_path.exists():
            continue
        width, height, top, bottom, middle = dark_density(output_path)
        score = score_risk(width, height, top, bottom, middle)
        if score >= 35:
            risks.append(
                CropRisk(
                    book=book,
                    chapter=int(entry["chapter"]),
                    verse=int(entry["verse"]),
                    source_file=str(entry["source_file"]),
                    output_image=str(output_path.relative_to(REPO_ROOT)),
                    width=width,
                    height=height,
                    top_dark_density=round(top, 4),
                    bottom_dark_density=round(bottom, 4),
                    middle_dark_density=round(middle, 4),
                    risk_score=score,
                    crop_box=entry.get("crop_box"),
                )
            )

    return risks, status_counts, book_status_counts


def main() -> int:
    args = parse_args()
    manifest_root = args.manifest_root.expanduser().resolve()
    all_risks: list[CropRisk] = []
    statuses: Counter[str] = Counter()
    book_statuses: Counter[str] = Counter()

    for manifest_path in sorted(manifest_root.glob("*_verse_images.json")):
        risks, manifest_statuses, manifest_book_statuses = audit_manifest(manifest_path)
        all_risks.extend(risks)
        statuses.update(manifest_statuses)
        book_statuses.update(manifest_book_statuses)

    all_risks.sort(key=lambda risk: risk.risk_score, reverse=True)
    risks_by_book: dict[str, int] = defaultdict(int)
    for risk in all_risks:
        risks_by_book[risk.book] += 1

    report: dict[str, Any] = {
        "status_counts": dict(sorted(statuses.items())),
        "book_status_counts": dict(sorted(book_statuses.items())),
        "risk_threshold": 35,
        "risk_count": len(all_risks),
        "risk_count_by_book": dict(sorted(risks_by_book.items())),
        "top_risks": [asdict(risk) for risk in all_risks[: args.top]],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Report: {args.output}")
    print(f"Status counts: {report['status_counts']}")
    print(f"Risk count: {report['risk_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
