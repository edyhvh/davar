from __future__ import annotations

import argparse
import base64
import io
import json
import os
import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.hutter.verse_images import DEFAULT_MANIFEST_ROOT, REPO_ROOT

try:
    from openai import OpenAI
except ImportError as exc:  # pragma: no cover - operational dependency.
    raise SystemExit("OpenAI SDK is required. Run this with the project virtualenv.") from exc

try:
    from PIL import Image
    from PIL import ImageEnhance, ImageFilter, ImageOps
except ImportError as exc:  # pragma: no cover - operational dependency.
    raise SystemExit("Pillow is required to prepare verse images.") from exc


DEFAULT_RESULTS_ROOT = REPO_ROOT / "data" / "hutter" / "api_results"
DEFAULT_MODEL = "gpt-4.1-mini"
SYSTEM_PROMPT = """You are doing exact OCR transcription of verse-level image crops from Elias Hutter's Hebrew New Testament.

Extract only the Hebrew Bible verse text for the requested verse image.
Preserve Hebrew consonants, niqqud, cantillation-like marks if visible, maqaf, punctuation, and word order.
Copy the printed glyphs exactly. Hutter's wording and spelling may differ from familiar Hebrew Bible editions.
Do not translate, modernize, vocalize from memory, substitute familiar biblical wording, or repair uncertain text silently.
Do not replace printed words with synonyms. For example, if the crop prints חפץ, do not write רצון.
Ignore non-Hebrew material such as Latin, Spanish, Greek, notes, glosses, page titles, headers, catchwords, source labels, and verse numbers.
If the crop contains neighboring Hebrew from another verse, include only the target verse as best as the image allows.
If the image has Hebrew pointing marks but you cannot confidently preserve them, set confidence to low and needs_review to true.
If the target verse is cut off, partly missing, too blurry, or mixed with notes, flag it in needs_review and explain briefly.

Return only JSON with this shape:
{
  "verses": [
    {
      "id": "book.chapter.verse.source_file",
      "book": "book",
      "chapter": 1,
      "verse": 1,
      "hebrew_text": "transcribed Hebrew only",
      "confidence": "high|medium|low",
      "ignored_non_hebrew": true,
      "needs_review": false,
      "notes": "short note or empty string"
    }
  ]
}
"""
HEBREW_MARKS = set(chr(codepoint) for codepoint in range(0x0591, 0x05C8))


@dataclass(frozen=True)
class VerseImage:
    id: str
    book: str
    chapter: int
    verse: int
    source_file: str
    output_image: str


@dataclass(frozen=True)
class PreparedImage:
    data_url: str
    media_type: str
    original_width: int
    original_height: int
    prepared_width: int
    prepared_height: int
    byte_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a cost-conscious OpenAI OCR pilot over Hutter verse images."
    )
    parser.add_argument("book", help="Book key, for example colossians.")
    parser.add_argument("--manifest-root", type=Path, default=DEFAULT_MANIFEST_ROOT)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_HUTTER_MODEL", DEFAULT_MODEL),
        help=f"Vision-capable OpenAI model (default: {DEFAULT_MODEL}, overridable by OPENAI_HUTTER_MODEL).",
    )
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of unprocessed verse images.")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many manifest entries before processing.")
    parser.add_argument(
        "--ids",
        help="Comma-separated verse ids to process, for example romans.10.16.000084,romans.10.18.000086.",
    )
    parser.add_argument(
        "--ids-file",
        type=Path,
        default=None,
        help="Text file with one verse id per line. Blank lines and # comments are ignored.",
    )
    parser.add_argument("--batch-size", type=int, default=3, help="Images per API request.")
    parser.add_argument("--max-width", type=int, default=1400, help="Downscale wider crops to this width.")
    parser.add_argument("--jpeg-quality", type=int, default=88, help="JPEG quality for API upload images.")
    parser.add_argument(
        "--image-format",
        choices=["jpeg", "png"],
        default="jpeg",
        help="Prepared upload format. PNG is larger but may preserve small marks better.",
    )
    parser.add_argument("--scale", type=float, default=1.0, help="Upscale prepared image before upload.")
    parser.add_argument(
        "--ocr-preprocess",
        action="store_true",
        help="Apply grayscale autocontrast, sharpening, and contrast boost before upload.",
    )
    parser.add_argument(
        "--detail",
        choices=["auto", "low", "high"],
        default="high",
        help="OpenAI image detail. Hebrew niqqud generally needs high.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Optional temperature. Omitted by default because some models do not support it.",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=["none", "minimal", "low", "medium", "high", "xhigh"],
        default="low",
        help="Reasoning effort for GPT-5/o-series models. Use none or low for OCR cost control.",
    )
    parser.add_argument(
        "--text-verbosity",
        choices=["low", "medium", "high"],
        default="low",
        help="Response verbosity. Low keeps JSON concise.",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=None,
        help="Optional cap covering visible output and reasoning tokens.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Prepare images and report batches without API calls.")
    parser.add_argument("--force", action="store_true", help="Reprocess verses already present in results.jsonl.")
    parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between batches.")
    return parser.parse_args()


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in os.environ:
            continue
        value = value.strip().strip('"').strip("'")
        os.environ[key] = value


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def chunks(items: list[VerseImage], size: int) -> Iterable[list[VerseImage]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def verse_id(book: str, chapter: int, verse: int, source_file: str) -> str:
    return f"{book}.{chapter}.{verse}.{Path(source_file).stem}"


def load_manifest(book: str, manifest_root: Path) -> list[VerseImage]:
    manifest_path = manifest_root / f"{book}_verse_images.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing manifest: {manifest_path}")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    images: list[VerseImage] = []
    for entry in payload.get("entries", []):
        if entry.get("status") != "cropped" or not entry.get("output_image"):
            continue
        chapter = int(entry["chapter"])
        verse = int(entry["verse"])
        source_file = str(entry["source_file"])
        images.append(
            VerseImage(
                id=verse_id(book, chapter, verse, source_file),
                book=book,
                chapter=chapter,
                verse=verse,
                source_file=source_file,
                output_image=str(entry["output_image"]),
            )
        )
    return images


def load_requested_ids(ids: str | None, ids_file: Path | None) -> set[str] | None:
    requested: set[str] = set()
    if ids:
        requested.update(item.strip() for item in ids.split(",") if item.strip())
    if ids_file is not None:
        for line in ids_file.expanduser().read_text(encoding="utf-8").splitlines():
            clean = line.strip()
            if not clean or clean.startswith("#"):
                continue
            requested.add(clean)
    return requested or None


def completed_ids(results_path: Path) -> set[str]:
    if not results_path.exists():
        return set()
    completed: set[str] = set()
    for line in results_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("status") == "ok":
            completed.add(str(row.get("id")))
    return completed


def prepare_image(
    path: Path,
    max_width: int,
    jpeg_quality: int,
    image_format: str,
    scale: float,
    ocr_preprocess: bool,
) -> PreparedImage:
    image = Image.open(path).convert("RGB")
    original_width, original_height = image.size
    if original_width > max_width:
        prepared_height = max(1, round(original_height * max_width / original_width))
        image = image.resize((max_width, prepared_height), Image.Resampling.LANCZOS)
    if scale != 1.0:
        scaled_width = max(1, round(image.width * scale))
        scaled_height = max(1, round(image.height * scale))
        image = image.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
    if ocr_preprocess:
        image = ImageOps.grayscale(image)
        image = ImageOps.autocontrast(image, cutoff=1)
        image = ImageEnhance.Contrast(image).enhance(1.35)
        image = image.filter(ImageFilter.SHARPEN)
        image = image.convert("RGB")
    prepared_width, prepared_height = image.size

    buffer = io.BytesIO()
    if image_format == "png":
        media_type = "image/png"
        image.save(buffer, format="PNG", optimize=True)
    else:
        media_type = "image/jpeg"
        image.save(buffer, format="JPEG", quality=jpeg_quality, optimize=True)
    image_bytes = buffer.getvalue()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return PreparedImage(
        data_url=f"data:{media_type};base64,{encoded}",
        media_type=media_type,
        original_width=original_width,
        original_height=original_height,
        prepared_width=prepared_width,
        prepared_height=prepared_height,
        byte_count=len(image_bytes),
    )


def extract_output_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return str(text)
    payload = response.model_dump(mode="json") if hasattr(response, "model_dump") else response
    parts: list[str] = []
    for output in payload.get("output", []):
        for content in output.get("content", []):
            content_text = content.get("text")
            if content_text:
                parts.append(str(content_text))
    return "\n".join(parts)


def parse_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise
        parsed = json.loads(stripped[start : end + 1])
    if isinstance(parsed, list):
        return {"verses": parsed}
    if not isinstance(parsed, dict):
        raise ValueError("Model response JSON is not an object or array.")
    return parsed


def build_input(batch: list[VerseImage], prepared: dict[str, PreparedImage], detail: str) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = [{"type": "input_text", "text": SYSTEM_PROMPT}]
    for index, item in enumerate(batch, start=1):
        content.append(
            {
                "type": "input_text",
                "text": (
                    f"Image {index}: id={item.id}; book={item.book}; "
                    f"chapter={item.chapter}; verse={item.verse}; source_file={item.source_file}."
                ),
            }
        )
        content.append(
            {
                "type": "input_image",
                "image_url": prepared[item.id].data_url,
                "detail": detail,
            }
        )
    return [{"role": "user", "content": content}]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def normalize_rows(
    book: str,
    batch_id: str,
    batch: list[VerseImage],
    parsed: dict[str, Any],
) -> list[dict[str, Any]]:
    by_id = {str(item.get("id")): item for item in parsed.get("verses", []) if isinstance(item, dict)}
    rows: list[dict[str, Any]] = []
    for item in batch:
        result = by_id.get(item.id)
        if result is None:
            rows.append(
                {
                    **asdict(item),
                    "book": book,
                    "batch_id": batch_id,
                    "status": "missing_in_response",
                    "hebrew_text": "",
                    "confidence": "low",
                    "ignored_non_hebrew": None,
                    "needs_review": True,
                    "notes": "The model response did not include this verse id.",
                    "created_at": utc_now(),
                }
            )
            continue
        hebrew_text = str(result.get("hebrew_text", "")).strip()
        has_marks = any(character in HEBREW_MARKS for character in hebrew_text)
        model_needs_review = bool(result.get("needs_review", False))
        notes = str(result.get("notes", "")).strip()
        if not has_marks:
            model_needs_review = True
            notes = (
                f"{notes} No Hebrew pointing marks were returned; review against the image."
                if notes
                else "No Hebrew pointing marks were returned; review against the image."
            )
        rows.append(
            {
                **asdict(item),
                "book": book,
                "batch_id": batch_id,
                "status": "ok",
                "hebrew_text": hebrew_text,
                "has_hebrew_marks": has_marks,
                "confidence": str(result.get("confidence", "low")),
                "ignored_non_hebrew": result.get("ignored_non_hebrew"),
                "needs_review": model_needs_review,
                "notes": notes,
                "created_at": utc_now(),
            }
        )
    return rows


def usage_dict(response: Any) -> dict[str, Any] | None:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        return usage.model_dump(mode="json")
    return dict(usage)


def supports_reasoning(model: str) -> bool:
    normalized = model.lower()
    return normalized.startswith("gpt-5") or normalized.startswith("o")


def main() -> int:
    args = parse_args()
    if args.batch_size < 1:
        raise SystemExit("--batch-size must be at least 1")
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be positive when provided")

    load_dotenv(REPO_ROOT / ".env")
    manifest_root = args.manifest_root.expanduser().resolve()
    results_dir = args.results_root.expanduser().resolve() / args.book
    results_path = results_dir / "results.jsonl"
    batches_path = results_dir / "batches.jsonl"

    all_images = load_manifest(args.book, manifest_root)
    requested_ids = load_requested_ids(args.ids, args.ids_file)
    selected = all_images[args.offset :]
    if requested_ids is not None:
        known_ids = {item.id for item in all_images}
        unknown_ids = sorted(requested_ids - known_ids)
        if unknown_ids:
            raise SystemExit(f"Unknown ids for {args.book}: {', '.join(unknown_ids)}")
        selected = [item for item in selected if item.id in requested_ids]
    done = completed_ids(results_path) if not args.force else set()
    pending = [item for item in selected if item.id not in done]
    if args.limit is not None:
        pending = pending[: args.limit]

    prepared: dict[str, PreparedImage] = {}
    for item in pending:
        prepared[item.id] = prepare_image(
            REPO_ROOT / item.output_image,
            args.max_width,
            args.jpeg_quality,
            args.image_format,
            args.scale,
            args.ocr_preprocess,
        )

    total_upload_bytes = sum(image.byte_count for image in prepared.values())
    planned_batches = list(chunks(pending, args.batch_size))
    print(f"Book: {args.book}")
    print(f"Manifest verses: {len(all_images)}")
    print(f"Already completed: {len(done)}")
    print(f"Pending this run: {len(pending)}")
    print(f"Planned batches: {len(planned_batches)}")
    print(f"Prepared upload MB: {total_upload_bytes / 1024 / 1024:.2f}")
    print(f"Model: {args.model}")
    print(f"Results: {results_path}")

    if args.dry_run or not pending:
        return 0

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set. Add it to the environment or .env.")

    client = OpenAI(api_key=api_key)
    for batch_index, batch in enumerate(planned_batches, start=1):
        batch_id = f"{args.book}-{utc_now()}-{batch_index:04d}"
        print(f"Processing batch {batch_index}/{len(planned_batches)}: {', '.join(item.id for item in batch)}")
        started = time.time()
        request: dict[str, Any] = {
            "model": args.model,
            "input": build_input(batch, prepared, args.detail),
            "text": {"verbosity": args.text_verbosity},
        }
        if args.temperature is not None:
            request["temperature"] = args.temperature
        if args.max_output_tokens is not None:
            request["max_output_tokens"] = args.max_output_tokens
        if args.reasoning_effort and supports_reasoning(args.model):
            request["reasoning"] = {"effort": args.reasoning_effort}
        response = client.responses.create(**request)
        elapsed = round(time.time() - started, 3)
        response_text = extract_output_text(response)
        parsed = parse_json_object(response_text)
        raw_response = response.model_dump(mode="json") if hasattr(response, "model_dump") else None
        write_jsonl(
            batches_path,
            [
                {
                    "batch_id": batch_id,
                    "book": args.book,
                    "ids": [item.id for item in batch],
                    "status": "ok",
                    "model": args.model,
                    "elapsed_seconds": elapsed,
                    "usage": usage_dict(response),
                    "response_text": response_text,
                    "raw_response": raw_response,
                    "created_at": utc_now(),
                }
            ],
        )
        write_jsonl(results_path, normalize_rows(args.book, batch_id, batch, parsed))
        if args.sleep > 0 and batch_index < len(planned_batches):
            time.sleep(args.sleep)

    print(f"Wrote: {results_path}")
    print(f"Wrote: {batches_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
