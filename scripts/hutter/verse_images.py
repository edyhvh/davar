from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STAGING_ROOT = REPO_ROOT / "data" / "hutter" / "staging"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "data" / "hutter" / "verse_images"
DEFAULT_MANIFEST_ROOT = REPO_ROOT / "data" / "hutter" / "manifests"
DEFAULT_OVERRIDES_PATH = REPO_ROOT / "data" / "hutter" / "crop_overrides.json"


@dataclass(frozen=True)
class VersePointer:
    book: str
    chapter: int
    verse: int
    source_file: str
    text_nikud: str
    visual_uncertainty: list[str]


@dataclass(frozen=True)
class CropBox:
    left: int
    top: int
    right: int
    bottom: int


@dataclass(frozen=True)
class VerseImageEntry:
    book: str
    chapter: int
    verse: int
    source_file: str
    source_image: str
    output_image: str | None
    crop_box: CropBox | None
    status: str
    notes: list[str]


@dataclass(frozen=True)
class PngImage:
    width: int
    height: int
    pixels: bytes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create verse-level image crops from existing Hutter page images and "
            "transcription JSON."
        ),
    )
    parser.add_argument("book", help="Book key, for example matthew, or all")
    parser.add_argument(
        "--staging-root",
        type=Path,
        default=DEFAULT_STAGING_ROOT,
        help=f"Hutter staging root (default: {DEFAULT_STAGING_ROOT})",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Verse crop output root (default: {DEFAULT_OUTPUT_ROOT})",
    )
    parser.add_argument(
        "--manifest-root",
        type=Path,
        default=DEFAULT_MANIFEST_ROOT,
        help=f"Manifest output root (default: {DEFAULT_MANIFEST_ROOT})",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=DEFAULT_OVERRIDES_PATH,
        help=f"Optional reviewed crop overrides JSON (default: {DEFAULT_OVERRIDES_PATH})",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Write assignments without reading or cropping image files.",
    )
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help=(
            "Write structural/source-existence notes without reading image pixels. "
            "Use this before broad crop planning."
        ),
    )
    parser.add_argument(
        "--crop-plan-only",
        action="store_true",
        help="Read images and compute crop boxes, but do not write cropped PNG files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned counts without writing files.",
    )
    parser.add_argument(
        "--source-files",
        help="Comma-separated source image file names to process, for example 000002.png.",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=18,
        help="Pixel padding around each estimated verse band.",
    )
    parser.add_argument(
        "--horizontal-padding",
        type=int,
        default=6,
        help="Pixel padding outside detected Hebrew column rules.",
    )
    parser.add_argument(
        "--analysis-left-ratio",
        type=float,
        default=0.10,
        help="Left edge ratio for Hebrew-row whitespace analysis.",
    )
    parser.add_argument(
        "--analysis-right-ratio",
        type=float,
        default=0.70,
        help="Right edge ratio for Hebrew-row whitespace analysis.",
    )
    parser.add_argument(
        "--dark-threshold",
        type=int,
        default=160,
        help="Pixel luminance below this value is treated as ink for segmentation.",
    )
    parser.add_argument(
        "--keep-duplicate-source-images",
        action="store_true",
        help=(
            "Do not suppress source files whose PNG bytes are identical to an "
            "earlier source page."
        ),
    )
    return parser.parse_args()


def load_book_json(book: str, staging_root: Path) -> dict[str, Any]:
    json_path = staging_root / "output" / f"{book}.json"
    if not json_path.exists():
        raise FileNotFoundError(f"Hutter JSON not found: {json_path}")
    return json.loads(json_path.read_text(encoding="utf-8"))


def load_crop_overrides(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def iter_verse_pointers(book: str, payload: dict[str, Any]) -> Iterable[VersePointer]:
    for chapter in payload.get("chapters", []):
        chapter_num = int(chapter["number"])
        for verse in chapter.get("verses", []):
            source_files = verse.get("source_files") or []
            for source_file in source_files:
                yield VersePointer(
                    book=book,
                    chapter=chapter_num,
                    verse=int(verse["number"]),
                    source_file=str(source_file),
                    text_nikud=str(verse.get("text_nikud", "")),
                    visual_uncertainty=list(verse.get("visual_uncertainty") or []),
                )


def group_by_source_file(pointers: Iterable[VersePointer]) -> dict[str, list[VersePointer]]:
    grouped: dict[str, list[VersePointer]] = {}
    for pointer in pointers:
        grouped.setdefault(pointer.source_file, []).append(pointer)

    for source_file in grouped:
        grouped[source_file].sort(key=lambda item: (item.chapter, item.verse))
    return dict(sorted(grouped.items()))


def read_png_rgb(path: Path) -> PngImage:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG file: {path}")

    pos = 8
    width = height = bit_depth = color_type = interlace = None
    idat: list[bytes] = []
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        pos += 4
        chunk_type = data[pos:pos + 4]
        pos += 4
        chunk = data[pos:pos + length]
        pos += length + 4
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(
                ">IIBBBBB", chunk
            )
        elif chunk_type == b"IDAT":
            idat.append(chunk)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None:
        raise ValueError(f"PNG missing IHDR: {path}")
    if bit_depth != 8 or color_type not in (0, 2, 6) or interlace != 0:
        raise ValueError(
            f"unsupported PNG format for {path}: bit_depth={bit_depth}, "
            f"color_type={color_type}, interlace={interlace}"
        )

    source_channels = {0: 1, 2: 3, 6: 4}[color_type]
    source_bpp = source_channels
    source_stride = width * source_bpp
    raw = zlib.decompress(b"".join(idat))
    rows: list[bytearray] = []
    out = bytearray(width * height * 3)
    index = 0
    previous = bytearray(source_stride)

    for y in range(height):
        filter_type = raw[index]
        index += 1
        current = bytearray(raw[index:index + source_stride])
        index += source_stride

        for i in range(source_stride):
            left = current[i - source_bpp] if i >= source_bpp else 0
            up = previous[i]
            up_left = previous[i - source_bpp] if i >= source_bpp else 0
            if filter_type == 1:
                current[i] = (current[i] + left) & 255
            elif filter_type == 2:
                current[i] = (current[i] + up) & 255
            elif filter_type == 3:
                current[i] = (current[i] + ((left + up) // 2)) & 255
            elif filter_type == 4:
                estimate = left + up - up_left
                left_distance = abs(estimate - left)
                up_distance = abs(estimate - up)
                up_left_distance = abs(estimate - up_left)
                predictor = (
                    left
                    if left_distance <= up_distance and left_distance <= up_left_distance
                    else up if up_distance <= up_left_distance else up_left
                )
                current[i] = (current[i] + predictor) & 255
            elif filter_type != 0:
                raise ValueError(f"unsupported PNG filter {filter_type} in {path}")

        row_offset = y * width * 3
        for x in range(width):
            source_offset = x * source_channels
            target_offset = row_offset + x * 3
            if color_type == 0:
                value = current[source_offset]
                out[target_offset:target_offset + 3] = bytes((value, value, value))
            else:
                out[target_offset:target_offset + 3] = current[source_offset:source_offset + 3]
        rows.append(current)
        previous = current

    return PngImage(width=width, height=height, pixels=bytes(out))


def write_png_rgb(path: Path, image: PngImage, box: CropBox) -> None:
    width = box.right - box.left
    height = box.bottom - box.top
    if width <= 0 or height <= 0:
        raise ValueError(f"invalid crop box: {box}")

    rows = bytearray()
    source_stride = image.width * 3
    for y in range(box.top, box.bottom):
        rows.append(0)
        row_start = y * source_stride + box.left * 3
        row_end = y * source_stride + box.right * 3
        rows.extend(image.pixels[row_start:row_end])

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(rows), level=6))
        + chunk(b"IEND", b"")
    )


def row_dark_counts(image: PngImage, x0: int, x1: int, threshold: int = 190) -> list[int]:
    x0 = max(0, min(image.width - 1, x0))
    x1 = max(x0 + 1, min(image.width, x1))
    counts: list[int] = []
    stride = image.width * 3
    for y in range(image.height):
        row_start = y * stride
        count = 0
        for x in range(x0, x1):
            offset = row_start + x * 3
            if (
                image.pixels[offset]
                + image.pixels[offset + 1]
                + image.pixels[offset + 2]
            ) // 3 < threshold:
                count += 1
        counts.append(count)
    return counts


def column_dark_counts(
    image: PngImage,
    y0: int,
    y1: int,
    threshold: int = 80,
) -> list[int]:
    y0 = max(0, min(image.height - 1, y0))
    y1 = max(y0 + 1, min(image.height, y1))
    counts: list[int] = []
    stride = image.width * 3
    for x in range(image.width):
        count = 0
        for y in range(y0, y1):
            offset = y * stride + x * 3
            if (
                image.pixels[offset]
                + image.pixels[offset + 1]
                + image.pixels[offset + 2]
            ) // 3 < threshold:
                count += 1
        counts.append(count)
    return counts


def column_dark_counts_by_threshold(
    image: PngImage,
    y0: int,
    y1: int,
    thresholds: tuple[int, ...],
) -> dict[int, list[int]]:
    y0 = max(0, min(image.height - 1, y0))
    y1 = max(y0 + 1, min(image.height, y1))
    if thresholds != (80, 100, 120, 140):
        raise ValueError("column_dark_counts_by_threshold expects thresholds 80,100,120,140")
    counts_by_threshold = {threshold: [0] * image.width for threshold in thresholds}
    counts_80 = counts_by_threshold[80]
    counts_100 = counts_by_threshold[100]
    counts_120 = counts_by_threshold[120]
    counts_140 = counts_by_threshold[140]
    stride = image.width * 3
    y_step = 2
    for y in range(y0, y1, y_step):
        row_start = y * stride
        for x in range(image.width):
            offset = row_start + x * 3
            luminance = (
                image.pixels[offset]
                + image.pixels[offset + 1]
                + image.pixels[offset + 2]
            ) // 3
            if luminance < 140:
                counts_140[x] += y_step
                if luminance < 120:
                    counts_120[x] += y_step
                    if luminance < 100:
                        counts_100[x] += y_step
                        if luminance < 80:
                            counts_80[x] += y_step
    return counts_by_threshold


def contiguous_ranges(values: list[int], predicate, min_length: int) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start: int | None = None
    for index, value in enumerate(values):
        matches = predicate(value)
        if matches and start is None:
            start = index
        if (not matches or index == len(values) - 1) and start is not None:
            end = index - 1 if not matches else index
            if end - start + 1 >= min_length:
                ranges.append((start, end))
            start = None
    return ranges


def find_hebrew_column_bounds(image: PngImage, padding: int) -> tuple[int, int, list[str]]:
    y0 = int(image.height * 0.12)
    y1 = int(image.height * 0.96)
    candidates: dict[int, int] = {}
    thresholds = (80, 100, 120, 140)
    counts_by_threshold = column_dark_counts_by_threshold(image, y0, y1, thresholds)

    for threshold in thresholds:
        counts = counts_by_threshold[threshold]
        line_threshold = max(80, int((y1 - y0) * 0.10))
        for start, end in contiguous_ranges(
            counts,
            predicate=lambda count: count >= line_threshold,
            min_length=1,
        ):
            if end - start + 1 > 30:
                continue
            center = (start + end) // 2
            candidates[center] = max(candidates.get(center, 0), max(counts[start:end + 1]))

    positions = sorted(candidates)
    best_pair = choose_strong_window_pair(
        positions,
        candidates,
        image.width,
        left_range=(0.06, 0.16),
        right_range=(0.62, 0.86),
    )
    if best_pair is None:
        best_pair = choose_column_rule_pair(
        positions,
        candidates,
        image.width,
        y1 - y0,
        left_range=(0.06, 0.18),
        right_range=(0.58, 0.88),
        center_range=(0.34, 0.52),
        target_center=0.43,
        target_width=0.58,
        )
    if best_pair is None:
        best_pair = choose_column_rule_pair(
            positions,
            candidates,
            image.width,
            y1 - y0,
            left_range=(0.18, 0.32),
            right_range=(0.56, 0.90),
            center_range=(0.44, 0.60),
            target_center=0.51,
            target_width=0.60,
        )

    if best_pair is None:
        return 0, image.width, ["hebrew_column:fallback_full_width"]

    left, right = best_pair
    expansion_notes: list[str] = []
    expanded = expand_narrow_column_bounds(left, right, image.width)
    if expanded != best_pair:
        expansion_notes.append(f"hebrew_column_expanded:{left}-{right}->{expanded[0]}-{expanded[1]}")
        left, right = expanded
    crop_left = max(0, left - padding)
    crop_right = min(image.width, right + padding)
    return crop_left, crop_right, [f"hebrew_column:{left}-{right}", *expansion_notes]


def expand_narrow_column_bounds(left: int, right: int, image_width: int) -> tuple[int, int]:
    width = right - left
    trigger_width = round(image_width * 0.56)
    if width > trigger_width:
        return left, right

    min_width = round(image_width * 0.68)
    if left <= image_width * 0.20:
        expanded_right = min(image_width, left + min_width)
        return left, max(right, expanded_right)
    if right >= image_width * 0.70:
        expanded_left = max(0, right - min_width)
        return min(left, expanded_left), right

    center = (left + right) // 2
    expanded_left = max(0, center - min_width // 2)
    expanded_right = min(image_width, expanded_left + min_width)
    expanded_left = max(0, expanded_right - min_width)
    return expanded_left, expanded_right


def choose_strong_window_pair(
    positions: list[int],
    candidates: dict[int, int],
    image_width: int,
    left_range: tuple[float, float],
    right_range: tuple[float, float],
) -> tuple[int, int] | None:
    left_positions = [
        position
        for position in positions
        if image_width * left_range[0] <= position <= image_width * left_range[1]
    ]
    right_positions = [
        position
        for position in positions
        if image_width * right_range[0] <= position <= image_width * right_range[1]
    ]
    if not left_positions or not right_positions:
        return None

    left = max(left_positions, key=lambda position: candidates[position])
    right = max(right_positions, key=lambda position: candidates[position])
    width_ratio = (right - left) / image_width
    if right > left and 0.45 <= width_ratio <= 0.80:
        return left, right
    return None


def choose_column_rule_pair(
    positions: list[int],
    candidates: dict[int, int],
    image_width: int,
    scan_height: int,
    left_range: tuple[float, float],
    right_range: tuple[float, float],
    center_range: tuple[float, float],
    target_center: float,
    target_width: float,
) -> tuple[int, int] | None:
    best_pair: tuple[int, int] | None = None
    best_score: float | None = None
    for left in positions:
        left_ratio = left / image_width
        if not left_range[0] <= left_ratio <= left_range[1]:
            continue
        for right in positions:
            if right <= left:
                continue
            right_ratio = right / image_width
            if not right_range[0] <= right_ratio <= right_range[1]:
                continue
            width_ratio = (right - left) / image_width
            center_ratio = ((left + right) / 2) / image_width
            if not 0.45 <= width_ratio <= 0.75:
                continue
            if not center_range[0] <= center_ratio <= center_range[1]:
                continue
            strength_bonus = min(candidates[left], candidates[right]) / max(1, scan_height)
            score = (
                abs(center_ratio - target_center) * 2
                + abs(width_ratio - target_width)
                - strength_bonus * 0.20
            )
            if best_score is None or score < best_score:
                best_pair = (left, right)
                best_score = score
    return best_pair


def estimate_content_bounds(
    row_counts: list[int],
    ink_threshold: int,
    start_ratio: float = 0.12,
) -> tuple[int, int]:
    start_scan = int(len(row_counts) * start_ratio)
    end_scan = int(len(row_counts) * 0.985)
    ink_rows = [
        row
        for row in range(start_scan, end_scan)
        if row_counts[row] >= ink_threshold
    ]
    if not ink_rows:
        return start_scan, end_scan
    return min(ink_rows), max(ink_rows)


def find_whitespace_gaps(
    row_counts: list[int],
    content_top: int,
    content_bottom: int,
    whitespace_threshold: int,
) -> list[tuple[int, int]]:
    scoped = row_counts[content_top:content_bottom + 1]
    raw_gaps = contiguous_ranges(
        scoped,
        predicate=lambda count: count <= whitespace_threshold,
        min_length=6,
    )
    return [(start + content_top, end + content_top) for start, end in raw_gaps]


def trim_content_bottom_for_trailing_blank(
    content_top: int,
    content_bottom: int,
    gaps: list[tuple[int, int]],
    image_height: int,
) -> tuple[int, str | None]:
    """Trim framed blank paper below the final book verse.

    Hutter's final book pages often leave most of the lower frame empty. The
    page frame or show-through text can still pull content_bottom near the
    physical page bottom, which creates a blank final verse crop.
    """

    span = max(1, content_bottom - content_top)
    min_gap = max(120, int(image_height * 0.12))
    earliest_trailing_start = content_top + int(span * 0.35)
    latest_required_end = content_bottom - int(image_height * 0.02)

    merged_tail_start: int | None = None
    max_gap_break = max(28, int(image_height * 0.025))
    min_tail_span = max(320, int(image_height * 0.18))
    for index, gap in enumerate(gaps):
        if gap[0] < earliest_trailing_start:
            continue

        merged_start, merged_end = gap
        whitespace_rows = gap[1] - gap[0] + 1
        for next_gap in gaps[index + 1 :]:
            if next_gap[0] - merged_end > max_gap_break:
                break
            merged_end = max(merged_end, next_gap[1])
            whitespace_rows += next_gap[1] - next_gap[0] + 1

        merged_span = max(1, merged_end - merged_start + 1)
        if (
            merged_span >= min_tail_span
            and whitespace_rows / merged_span >= 0.70
            and merged_end >= latest_required_end
        ):
            merged_tail_start = merged_start
            break

    if merged_tail_start is not None:
        trimmed_bottom = max(content_top + 1, merged_tail_start - 1)
        if trimmed_bottom < content_bottom:
            return trimmed_bottom, f"trimmed_trailing_blank:{content_bottom}->{trimmed_bottom}"

    trailing_gaps = [
        gap
        for gap in gaps
        if gap[0] >= earliest_trailing_start
        and gap[1] - gap[0] + 1 >= min_gap
        and gap[1] >= latest_required_end - min_gap
    ]
    if not trailing_gaps:
        return content_bottom, None

    gap = min(trailing_gaps, key=lambda item: item[0])
    trimmed_bottom = max(content_top + 1, gap[0] - 1)
    if trimmed_bottom >= content_bottom:
        return content_bottom, None
    return trimmed_bottom, f"trimmed_trailing_blank:{content_bottom}->{trimmed_bottom}"


def adjust_content_top_for_header(
    content_top: int,
    content_bottom: int,
    gaps: list[tuple[int, int]],
    image_height: int,
) -> int:
    header_limit = int(image_height * 0.24)
    header_gaps = [
        gap
        for gap in gaps
        if gap[0] >= content_top and gap[1] <= header_limit and gap[1] - gap[0] + 1 >= 10
    ]
    if not header_gaps:
        return content_top

    adjusted_top = max(gap[1] for gap in header_gaps) + 1
    if adjusted_top >= content_bottom:
        return content_top
    return adjusted_top


def choose_cut_lines(
    gaps: list[tuple[int, int]],
    content_top: int,
    content_bottom: int,
    verse_count: int,
) -> tuple[list[int], list[str]]:
    if verse_count <= 1:
        return [], []

    notes: list[str] = []
    cut_count = verse_count - 1
    span = max(1, content_bottom - content_top)
    target_spacing = span / verse_count
    candidates = sorted(
        {
            (gap[0] + gap[1]) // 2: gap
            for gap in gaps
            if content_top < (gap[0] + gap[1]) // 2 < content_bottom
        }.items()
    )
    min_segment = max(12.0, min(130.0, target_spacing * 0.55))

    if len(candidates) >= cut_count:
        cut_lines = choose_ordered_cut_lines(
            candidates,
            content_top,
            content_bottom,
            verse_count,
            target_spacing,
            min_segment,
        )
    else:
        cut_lines = []

    if len(cut_lines) != cut_count:
        notes.append("fallback_cut_sequence:ordered_gaps_unavailable")
        cut_lines = [
            content_top + round(index * span / verse_count)
            for index in range(1, verse_count)
        ]

    cut_lines = sorted(cut_lines)
    return cut_lines, notes


def choose_ordered_cut_lines(
    candidates: list[tuple[int, tuple[int, int]]],
    content_top: int,
    content_bottom: int,
    verse_count: int,
    target_spacing: float,
    min_segment: float,
) -> list[int]:
    cut_count = verse_count - 1
    # Dynamic selection keeps the full page sequence balanced. A greedy target
    # match can pick an internal Hebrew/gloss gap early and shift later verses.
    states: dict[tuple[int, int], tuple[float, int | None]] = {}
    for selected in range(1, cut_count + 1):
        target = content_top + round(selected * (content_bottom - content_top) / verse_count)
        for index, (center, gap) in enumerate(candidates):
            if selected == 1:
                segment_height = center - content_top
                if segment_height < min_segment:
                    continue
                cost = cut_sequence_cost(gap, center, target, segment_height, target_spacing)
                states[(selected, index)] = (cost, None)
                continue

            best: tuple[float, int] | None = None
            for previous_index in range(index):
                previous_state = states.get((selected - 1, previous_index))
                if previous_state is None:
                    continue
                previous_center = candidates[previous_index][0]
                segment_height = center - previous_center
                if segment_height < min_segment:
                    continue
                cost = previous_state[0] + cut_sequence_cost(
                    gap,
                    center,
                    target,
                    segment_height,
                    target_spacing,
                )
                if best is None or cost < best[0]:
                    best = (cost, previous_index)

            if best is not None:
                states[(selected, index)] = best

    best_final: tuple[float, int] | None = None
    for index, (center, _gap) in enumerate(candidates):
        state = states.get((cut_count, index))
        if state is None:
            continue
        final_segment = content_bottom - center
        if final_segment < min_segment:
            continue
        final_cost = state[0] + abs(final_segment - target_spacing) * 0.55
        if best_final is None or final_cost < best_final[0]:
            best_final = (final_cost, index)

    if best_final is None:
        return []

    selected_indices: list[int] = []
    selected = cut_count
    index: int | None = best_final[1]
    while selected > 0 and index is not None:
        selected_indices.append(index)
        _cost, previous = states[(selected, index)]
        index = previous
        selected -= 1
    if len(selected_indices) != cut_count:
        return []
    return [candidates[index][0] for index in reversed(selected_indices)]


def cut_sequence_cost(
    gap: tuple[int, int],
    center: int,
    target: int,
    segment_height: int,
    target_spacing: float,
) -> float:
    spacing_penalty = abs(segment_height - target_spacing) * 0.55
    return score_gap_for_cut(gap, target, target_spacing) + spacing_penalty


def score_gap_for_cut(gap: tuple[int, int], target: int, target_spacing: float) -> float:
    center = (gap[0] + gap[1]) / 2
    length = gap[1] - gap[0] + 1
    target_distance = abs(center - target)
    # Verse boundaries are usually the longer blank bands between gloss and the next
    # Hebrew verse. Shorter internal gaps between Hebrew lines can otherwise win just
    # because they are slightly closer to an equal-spacing target.
    length_bonus = min(target_spacing * 0.18, length * 3.0)
    short_gap_penalty = target_spacing * 0.14 if length < 12 else 0
    return target_distance - length_bonus + short_gap_penalty


def split_content_box(content_box: CropBox, count: int, padding: int, image_size: tuple[int, int]) -> list[CropBox]:
    if count <= 0:
        return []

    width, height = image_size
    content_height = max(1, content_box.bottom - content_box.top)
    bands: list[CropBox] = []
    for index in range(count):
        top = content_box.top + round(index * content_height / count)
        bottom = content_box.top + round((index + 1) * content_height / count)
        bands.append(
            CropBox(
                left=max(0, content_box.left - padding),
                top=max(0, top - padding),
                right=min(width, content_box.right + padding),
                bottom=min(height, bottom + padding),
            )
        )
    return bands


def boxes_from_cut_lines(
    crop_left: int,
    crop_right: int,
    content_top: int,
    content_bottom: int,
    cut_lines: list[int],
    padding: int,
    image_size: tuple[int, int],
) -> list[CropBox]:
    width, height = image_size
    boundaries = [content_top, *cut_lines, content_bottom]
    boxes: list[CropBox] = []
    for top, bottom in zip(boundaries, boundaries[1:]):
        boxes.append(
            CropBox(
                left=crop_left,
                top=max(0, top - padding),
                right=crop_right,
                bottom=min(height, bottom + padding),
            )
        )
    return boxes


def split_by_whitespace(
    image: PngImage,
    count: int,
    padding: int,
    analysis_left_ratio: float,
    analysis_right_ratio: float,
    skip_header: bool,
    trim_trailing_blank: bool = False,
    dark_threshold: int = 160,
    horizontal_padding: int = 6,
) -> tuple[list[CropBox], list[str]]:
    if count <= 0:
        return [], []

    crop_left, crop_right, column_notes = find_hebrew_column_bounds(image, horizontal_padding)
    column_width = max(1, crop_right - crop_left)
    inner_margin = max(24, min(80, int(column_width * 0.08)))
    x0 = max(crop_left + inner_margin, int(image.width * analysis_left_ratio))
    x1 = min(crop_right - inner_margin, int(image.width * analysis_right_ratio))
    if x1 <= x0 + 10:
        x0 = int(image.width * analysis_left_ratio)
        x1 = int(image.width * analysis_right_ratio)
    counts = row_dark_counts(image, x0, x1, threshold=dark_threshold)
    analysis_width = max(1, x1 - x0)
    ink_threshold = max(8, int(analysis_width * 0.020))
    content_top, content_bottom = estimate_content_bounds(
        counts,
        ink_threshold,
        start_ratio=0.12 if skip_header else 0.02,
    )
    scoped_counts = sorted(counts[content_top:content_bottom + 1])
    percentile_threshold = scoped_counts[int(len(scoped_counts) * 0.30)] if scoped_counts else 0
    whitespace_threshold = max(12, int(analysis_width * 0.025), percentile_threshold + 3)
    gaps = find_whitespace_gaps(counts, content_top, content_bottom, whitespace_threshold)
    if skip_header:
        content_top = adjust_content_top_for_header(content_top, content_bottom, gaps, image.height)
    gaps = [gap for gap in gaps if gap[0] > content_top]
    trim_note = None
    if trim_trailing_blank:
        content_bottom, trim_note = trim_content_bottom_for_trailing_blank(
            content_top,
            content_bottom,
            gaps,
            image.height,
        )
        gaps = [gap for gap in gaps if gap[0] > content_top and gap[1] < content_bottom]
    cut_lines, notes = choose_cut_lines(gaps, content_top, content_bottom, count)
    if trim_note is not None:
        notes.append(trim_note)

    boxes = boxes_from_cut_lines(
        crop_left,
        crop_right,
        content_top,
        content_bottom,
        cut_lines,
        padding,
        (image.width, image.height),
    )

    notes.extend(
        [
            *column_notes,
            f"analysis_x:{x0}-{x1}",
            f"dark_threshold:{dark_threshold}",
            f"whitespace_threshold:{whitespace_threshold}",
            f"content_y:{content_top}-{content_bottom}",
            f"cut_lines:{','.join(str(line) for line in cut_lines)}",
        ]
    )
    return boxes, notes


def chapter_last_verses(payload: dict[str, Any]) -> dict[int, int]:
    last_verses: dict[int, int] = {}
    for chapter in payload.get("chapters", []):
        chapter_num = int(chapter["number"])
        verse_numbers = [int(verse["number"]) for verse in chapter.get("verses", [])]
        if verse_numbers:
            last_verses[chapter_num] = max(verse_numbers)
    return last_verses


def book_last_verse(last_verses_by_chapter: dict[int, int]) -> tuple[int, int] | None:
    if not last_verses_by_chapter:
        return None
    chapter = max(last_verses_by_chapter)
    return chapter, last_verses_by_chapter[chapter]


def page_structure_notes(
    pointers: list[VersePointer],
    last_verses_by_chapter: dict[int, int],
) -> list[str]:
    notes: list[str] = []
    if not pointers:
        return notes

    chapters = [pointer.chapter for pointer in pointers]
    if len(set(chapters)) > 1:
        notes.append(
            "page_chapter_transition:"
            + ",".join(f"{pointer.chapter}:{pointer.verse}" for pointer in pointers)
        )
    if pointers[0].verse == 1:
        notes.append(f"page_starts_at_first_verse:{pointers[0].chapter}:1")

    for pointer in pointers:
        last_verse = last_verses_by_chapter.get(pointer.chapter)
        if pointer.verse == last_verse:
            notes.append(f"page_contains_last_verse:{pointer.chapter}:{pointer.verse}")
    return notes


def image_quality_notes(image: PngImage) -> list[str]:
    sample_step = 8
    luminance_total = 0
    red_total = 0
    blue_total = 0
    dark_count = 0
    sample_count = 0
    stride = image.width * 3
    for y in range(0, image.height, sample_step):
        row_start = y * stride
        for x in range(0, image.width, sample_step):
            offset = row_start + x * 3
            red = image.pixels[offset]
            green = image.pixels[offset + 1]
            blue = image.pixels[offset + 2]
            luminance = (red + green + blue) // 3
            luminance_total += luminance
            red_total += red
            blue_total += blue
            if luminance < 160:
                dark_count += 1
            sample_count += 1

    if sample_count == 0:
        return ["image_quality:empty_sample"]

    mean_luma = luminance_total / sample_count
    dark_ratio = dark_count / sample_count
    warmth = (red_total - blue_total) / sample_count
    notes = [
        f"image_size:{image.width}x{image.height}",
        f"image_luma_mean:{mean_luma:.1f}",
        f"image_dark_ratio:{dark_ratio:.4f}",
        f"image_warmth:{warmth:.1f}",
    ]
    if mean_luma < 180:
        notes.append("image_quality:dark_or_stained")
    if warmth > 28:
        notes.append("image_quality:yellowed_scan")
    if dark_ratio > 0.22:
        notes.append("image_quality:dense_ink_or_noise")
    return notes


def output_file_name(pointer: VersePointer) -> str:
    return f"{pointer.chapter:03d}_{pointer.verse:03d}_{Path(pointer.source_file).stem}.png"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def build_manifest(
    book: str,
    staging_root: Path,
    output_root: Path,
    manifest_only: bool = False,
    crop_plan_only: bool = False,
    audit_only: bool = False,
    padding: int = 18,
    analysis_left_ratio: float = 0.10,
    analysis_right_ratio: float = 0.70,
    source_files: set[str] | None = None,
    dark_threshold: int = 160,
    horizontal_padding: int = 6,
    dedupe_source_images: bool = True,
    crop_overrides: dict[str, Any] | None = None,
) -> list[VerseImageEntry]:
    payload = load_book_json(book, staging_root)
    last_verses_by_chapter = chapter_last_verses(payload)
    final_book_verse = book_last_verse(last_verses_by_chapter)
    grouped = group_by_source_file(iter_verse_pointers(book, payload))
    if source_files is not None:
        grouped = {
            source_file: pointers
            for source_file, pointers in grouped.items()
            if source_file in source_files
        }
    source_dir = staging_root / "data" / "images" / "hebrew_images" / book
    book_output_dir = output_root / book
    entries: list[VerseImageEntry] = []
    seen_source_hashes: dict[str, str] = {}
    book_overrides = (crop_overrides or {}).get(book, {})

    if not manifest_only and not crop_plan_only:
        book_output_dir.mkdir(parents=True, exist_ok=True)

    for source_file, pointers in grouped.items():
        source_image = source_dir / source_file
        notes: list[str] = page_structure_notes(pointers, last_verses_by_chapter)
        crop_boxes: list[CropBox | None] = [None] * len(pointers)

        if manifest_only:
            notes.append("manifest_only: crop not generated")
            status = "planned"
        elif audit_only:
            if source_image.exists():
                notes.append("audit_only: image pixels not read")
                status = "audited"
            else:
                notes.append(f"missing source image: {source_image}")
                status = "missing_source"
        elif not source_image.exists():
            notes.append(f"missing source image: {source_image}")
            status = "missing_source"
        else:
            try:
                if dedupe_source_images:
                    source_hash = hashlib.sha256(source_image.read_bytes()).hexdigest()
                    duplicate_source = seen_source_hashes.get(source_hash)
                    if duplicate_source is not None:
                        notes.append(
                            f"duplicate_source_image:{source_file} duplicates {duplicate_source}"
                        )
                        status = "duplicate_source_image"
                        raise DuplicateSourceImage
                    seen_source_hashes[source_hash] = source_file

                image = read_png_rgb(source_image)
                notes.extend(image_quality_notes(image))
                crop_boxes, cut_notes = split_by_whitespace(
                    image,
                    len(pointers),
                    padding,
                    analysis_left_ratio,
                    analysis_right_ratio,
                    skip_header=pointers[0].verse == 1,
                    trim_trailing_blank=(
                        final_book_verse is not None
                        and any(
                            (pointer.chapter, pointer.verse) == final_book_verse
                            for pointer in pointers
                        )
                    ),
                    dark_threshold=dark_threshold,
                    horizontal_padding=horizontal_padding,
                )
                notes.extend(cut_notes)
                override = book_overrides.get(source_file)
                if override is not None:
                    override_cut_lines = [int(line) for line in override.get("cut_lines", [])]
                    override_content_y = override.get("content_y")
                    if (
                        isinstance(override_content_y, list)
                        and len(override_content_y) == 2
                        and len(override_cut_lines) == max(0, len(pointers) - 1)
                    ):
                        crop_boxes = boxes_from_cut_lines(
                            crop_boxes[0].left,
                            crop_boxes[0].right,
                            int(override_content_y[0]),
                            int(override_content_y[1]),
                            override_cut_lines,
                            padding,
                            (image.width, image.height),
                        )
                        notes.append(
                            "manual_cut_override:"
                            + ",".join(str(line) for line in override_cut_lines)
                        )
                    else:
                        notes.append(f"manual_cut_override_invalid:{source_file}")
                if crop_plan_only:
                    status = "crop_planned"
                else:
                    for pointer, crop_box in zip(pointers, crop_boxes):
                        write_png_rgb(book_output_dir / output_file_name(pointer), image, crop_box)
                    status = "cropped"
            except Exception as exc:
                if isinstance(exc, DuplicateSourceImage):
                    pass
                else:
                    notes.append(f"crop_failed: {exc}")
                    status = "crop_failed"

        for pointer, crop_box in zip(pointers, crop_boxes):
            output_path = None
            if status == "cropped":
                output_path = display_path(book_output_dir / output_file_name(pointer))
            entries.append(
                VerseImageEntry(
                    book=book,
                    chapter=pointer.chapter,
                    verse=pointer.verse,
                    source_file=source_file,
                    source_image=display_path(source_image),
                    output_image=output_path,
                    crop_box=crop_box,
                    status=status,
                    notes=[*notes, *pointer.visual_uncertainty],
                )
            )

    return entries


class DuplicateSourceImage(Exception):
    pass


def write_manifest(book: str, manifest_root: Path, entries: list[VerseImageEntry]) -> Path:
    manifest_root.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_root / f"{book}_verse_images.json"
    payload = {
        "book": book,
        "entry_count": len(entries),
        "statuses": {
            status: sum(1 for entry in entries if entry.status == status)
            for status in sorted({entry.status for entry in entries})
        },
        "entries": [asdict(entry) for entry in entries],
    }
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest_path


def discover_books(staging_root: Path) -> list[str]:
    images_root = staging_root / "data" / "images" / "hebrew_images"
    output_root = staging_root / "output"
    if not images_root.exists():
        return []
    return sorted(
        path.name
        for path in images_root.iterdir()
        if path.is_dir() and (output_root / f"{path.name}.json").exists()
    )


def main() -> int:
    args = parse_args()
    book = args.book.lower()
    staging_root = args.staging_root.expanduser().resolve()
    output_root = args.output_root.expanduser().resolve()
    manifest_root = args.manifest_root.expanduser().resolve()
    overrides_path = args.overrides.expanduser().resolve()
    crop_overrides = load_crop_overrides(overrides_path)
    source_files = None
    if args.source_files:
        source_files = {
            source_file.strip()
            for source_file in args.source_files.split(",")
            if source_file.strip()
        }

    books = discover_books(staging_root) if book == "all" else [book]
    if not books:
        raise FileNotFoundError(f"No Hutter books found under {staging_root}")
    if book == "all" and source_files:
        raise ValueError("--source-files can only be used with a single book")

    total_entries = 0
    aggregate_statuses: dict[str, int] = {}
    for book_name in books:
        entries = build_manifest(
            book=book_name,
            staging_root=staging_root,
            output_root=output_root,
            manifest_only=args.manifest_only or args.dry_run,
            crop_plan_only=args.crop_plan_only,
            audit_only=args.audit_only,
            padding=args.padding,
            analysis_left_ratio=args.analysis_left_ratio,
            analysis_right_ratio=args.analysis_right_ratio,
            source_files=source_files,
            dark_threshold=args.dark_threshold,
            horizontal_padding=args.horizontal_padding,
            dedupe_source_images=not args.keep_duplicate_source_images,
            crop_overrides=crop_overrides,
        )

        statuses = {
            status: sum(1 for entry in entries if entry.status == status)
            for status in sorted({entry.status for entry in entries})
        }
        total_entries += len(entries)
        for status, count in statuses.items():
            aggregate_statuses[status] = aggregate_statuses.get(status, 0) + count

        print(f"Book: {book_name}")
        print(f"Verse image entries: {len(entries)}")
        print(f"Statuses: {statuses}")
        if not args.dry_run:
            manifest_path = write_manifest(book_name, manifest_root, entries)
            print(f"Manifest: {manifest_path}")
            if not args.manifest_only and not args.audit_only:
                print(f"Verse images: {output_root / book_name}")

    if len(books) > 1:
        print(f"Books processed: {len(books)}")
        print(f"Total verse image entries: {total_entries}")
        print(f"Aggregate statuses: {aggregate_statuses}")
    if args.dry_run:
        print("Dry run: manifests not written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
