from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.translit.local_translit import LocalTransliterator


HUTTER_ROOT = REPO_ROOT / "data" / "hutter" / "staging" / "output"
DELITZSCH_ROOT = REPO_ROOT / "data" / "delitzsch_parsed"
TANAJ_ROOT = REPO_ROOT / "data" / "oe"
LEXICON_WORDS_ROOT = REPO_ROOT / "data" / "dict" / "lexicon" / "words"
LEXICON_ROOTS_ROOT = REPO_ROOT / "data" / "dict" / "lexicon" / "roots"
CUSTOM_DEFINITIONS_PATH = (
    REPO_ROOT / "data" / "dict" / "lexicon" / "custom_definitions.json"
)
MANUAL_OVERRIDES_PATH = REPO_ROOT / "data" / "hutter" / "strong_overrides.json"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "data" / "hutter" / "strong_mappings"
DEFAULT_REPORT_PATH = (
    REPO_ROOT / "data" / "hutter" / "review_reports" / "strong_mapping_report.json"
)

HEBREW_MARK_RE = re.compile(r"[\u0591-\u05C7]")
HEBREW_CANTILLATION_RE = re.compile(r"[\u0591-\u05AF\u05BD\u05BF\u05C0\u05C3-\u05C7]")
NON_HEBREW_RE = re.compile(r"[^א-ת]")
NON_POINTED_HEBREW_RE = re.compile(r"[^א-ת\u05B0-\u05BC\u05C1\u05C2]")
MAQAF = "\u05BE"
PREFIX_CODES = {
    "ו": "Hc",
    "ה": "Hd",
    "ב": "Hb",
    "כ": "Hk",
    "ל": "Hl",
    "מ": "Hm",
    "ש": "Hs",
}
FINAL_TO_MEDIAL = str.maketrans({"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"})


@dataclass(frozen=True)
class StrongCandidate:
    strong: str
    prefixes: tuple[str, ...]


@dataclass(frozen=True)
class MappingDecision:
    strong: str | None
    prefixes: tuple[str, ...]
    confidence: str
    method: str
    evidence: str
    score: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Map Strong numbers onto Hutter Hebrew words using reviewed "
            "Delitzsch/Tanakh forms, lexicon lemmas, and conservative verse alignment."
        )
    )
    parser.add_argument(
        "books",
        nargs="*",
        help="Optional Hutter book ids. Defaults to every New Testament Hutter book.",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write per-book mappings and the aggregate review report.",
    )
    parser.add_argument(
        "--include-low-confidence",
        action="store_true",
        help="Keep low-confidence fuzzy candidates as assigned mappings.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_hebrew(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    normalized = HEBREW_MARK_RE.sub("", normalized)
    normalized = normalized.translate(FINAL_TO_MEDIAL)
    return NON_HEBREW_RE.sub("", normalized)


def normalize_pointed_hebrew(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    normalized = HEBREW_CANTILLATION_RE.sub("", normalized)
    return NON_POINTED_HEBREW_RE.sub("", normalized)


def split_hutter_words(text: str) -> list[str]:
    words: list[str] = []
    for whitespace_token in text.split():
        parts = whitespace_token.split(MAQAF)
        for index, part in enumerate(parts):
            cleaned = part.strip()
            if not normalize_hebrew(cleaned):
                continue
            if index < len(parts) - 1:
                cleaned += MAQAF
            words.append(cleaned)
    return words


def base_strong(strong: str | None) -> str | None:
    if not strong:
        return None
    parts = [part for part in strong.split("/") if part]
    return parts[-1] if parts else None


def composite_strong(prefixes: Iterable[str], strong: str) -> str:
    prefix_list = list(prefixes)
    return "/".join([*prefix_list, strong]) if prefix_list else strong


def candidate_from_word(word: dict[str, Any]) -> StrongCandidate | None:
    strong = str(word.get("strong") or "").strip()
    if not strong:
        return None
    prefixes = tuple(str(item) for item in word.get("prefixes") or [])
    return StrongCandidate(strong=strong, prefixes=prefixes)


def strip_known_prefixes(surface: str, prefixes: Iterable[str]) -> str:
    normalized = normalize_hebrew(surface)
    remaining = normalized
    reverse_codes = {code: letter for letter, code in PREFIX_CODES.items()}
    for prefix in prefixes:
        letter = reverse_codes.get(prefix)
        if letter and remaining.startswith(letter) and len(remaining) > 1:
            remaining = remaining[1:]
    return remaining


def iter_source_words() -> Iterable[dict[str, Any]]:
    for book_dir in sorted(TANAJ_ROOT.iterdir()):
        if not book_dir.is_dir():
            continue
        for chapter_path in sorted(book_dir.glob("*.json")):
            data = load_json(chapter_path)
            if not isinstance(data, list):
                continue
            for verse in data:
                if not isinstance(verse, dict):
                    continue
                yield from verse.get("words") or []

    for book_dir in sorted(DELITZSCH_ROOT.iterdir()):
        if not book_dir.is_dir():
            continue
        for chapter_path in sorted(book_dir.glob("*.json")):
            data = load_json(chapter_path)
            if not isinstance(data, list) or not data:
                continue
            chapter = data[0] if isinstance(data[0], dict) else {}
            for verse in chapter.get("verses") or []:
                yield from verse.get("words") or []


def load_lexicon_lemmas() -> dict[str, Counter[str]]:
    index: dict[str, Counter[str]] = defaultdict(Counter)
    for root in (LEXICON_WORDS_ROOT, LEXICON_ROOTS_ROOT):
        for path in root.glob("*.json"):
            entry = load_json(path)
            strong = str(entry.get("strong_number") or path.stem)
            lemma = normalize_hebrew(str(entry.get("lemma") or ""))
            if lemma:
                index[lemma][strong] += 1

    custom = load_json(CUSTOM_DEFINITIONS_PATH)
    for strong, entry in custom.items():
        lemma = normalize_hebrew(str(entry.get("hebrew") or ""))
        if lemma:
            index[lemma][str(strong)] += 2
    return index


def load_manual_overrides() -> dict[str, dict[str, Any]]:
    if not MANUAL_OVERRIDES_PATH.exists():
        return {}
    entries = load_json(MANUAL_OVERRIDES_PATH)
    overrides: dict[str, dict[str, Any]] = {}
    for entry in entries:
        for form in entry.get("forms") or []:
            normalized = normalize_hebrew(str(form))
            if normalized:
                overrides[normalized] = entry
    return overrides


def load_custom_name_forms() -> dict[str, set[str]]:
    custom = load_json(CUSTOM_DEFINITIONS_PATH)
    forms: dict[str, set[str]] = defaultdict(set)
    for strong, entry in custom.items():
        transliteration = str(entry.get("transliteration_en") or "")
        if (
            not str(strong).startswith("D")
            or not transliteration
            or not transliteration[0].isupper()
            or not entry.get("nt_instances")
        ):
            continue
        raw_forms = [
            str(entry.get("hebrew") or ""),
            *[
                str(instance.get("text") or "")
                for instance in entry.get("nt_instances") or []
            ],
        ]
        for raw_form in raw_forms:
            for _, normalized in prefix_parses(raw_form):
                if len(normalized) >= 4:
                    forms[str(strong)].add(normalized)
    return forms


def build_indexes() -> tuple[
    dict[str, Counter[StrongCandidate]],
    dict[str, Counter[StrongCandidate]],
    dict[str, Counter[str]],
    dict[str, Counter[str]],
]:
    pointed_surface_index: dict[str, Counter[StrongCandidate]] = defaultdict(Counter)
    surface_index: dict[str, Counter[StrongCandidate]] = defaultdict(Counter)
    base_form_index: dict[str, Counter[str]] = defaultdict(Counter)

    for word in iter_source_words():
        candidate = candidate_from_word(word)
        surface = normalize_hebrew(str(word.get("text") or ""))
        if not candidate or not surface:
            continue
        pointed_surface = normalize_pointed_hebrew(str(word.get("text") or ""))
        if pointed_surface:
            pointed_surface_index[pointed_surface][candidate] += 1
        surface_index[surface][candidate] += 1
        base = base_strong(candidate.strong)
        root_surface = strip_known_prefixes(
            str(word.get("text") or ""), candidate.prefixes
        )
        if base and root_surface:
            base_form_index[root_surface][base] += 1

    return pointed_surface_index, surface_index, base_form_index, load_lexicon_lemmas()


def best_counter_value[T](counter: Counter[T]) -> tuple[T | None, int, float]:
    if not counter:
        return None, 0, 0.0
    (value, count), *rest = counter.most_common(2)
    total = sum(counter.values())
    runner_up = rest[0][1] if rest else 0
    dominance = count / max(total, 1)
    separation = (count - runner_up) / max(count, 1)
    return value, count, dominance * 0.7 + separation * 0.3


def prefix_parses(surface: str, max_prefixes: int = 3) -> Iterable[tuple[tuple[str, ...], str]]:
    normalized = normalize_hebrew(surface)
    yield (), normalized

    def walk(remaining: str, prefixes: tuple[str, ...]) -> Iterable[tuple[tuple[str, ...], str]]:
        if len(prefixes) >= max_prefixes or len(remaining) <= 2:
            return
        code = PREFIX_CODES.get(remaining[0])
        if not code or code in prefixes:
            return
        next_prefixes = (*prefixes, code)
        next_remaining = remaining[1:]
        yield next_prefixes, next_remaining
        yield from walk(next_remaining, next_prefixes)

    yield from walk(normalized, ())


def decide_from_indexes(
    text: str,
    manual_overrides: dict[str, dict[str, Any]],
    pointed_surface_index: dict[str, Counter[StrongCandidate]],
    surface_index: dict[str, Counter[StrongCandidate]],
    base_form_index: dict[str, Counter[str]],
    lemma_index: dict[str, Counter[str]],
) -> MappingDecision | None:
    surface = normalize_hebrew(text)
    override = manual_overrides.get(surface)
    if override:
        prefixes = tuple(str(item) for item in override.get("prefixes") or [])
        return MappingDecision(
            strong=str(override["strong"]),
            prefixes=prefixes,
            confidence="high",
            method="manual_override",
            evidence=str(override.get("reason") or "Reviewed Hutter lexical assignment"),
            score=1.0,
        )

    pointed_surface = normalize_pointed_hebrew(text)
    pointed_exact, pointed_count, pointed_quality = best_counter_value(
        pointed_surface_index.get(pointed_surface, Counter())
    )
    if pointed_exact and pointed_quality >= 0.65:
        return MappingDecision(
            strong=pointed_exact.strong,
            prefixes=pointed_exact.prefixes,
            confidence="high" if pointed_quality >= 0.86 else "medium",
            method="attested_pointed_surface",
            evidence=(
                f"pointed_surface={pointed_surface}; occurrences={pointed_count}; "
                f"quality={pointed_quality:.3f}"
            ),
            score=min(1.0, pointed_quality + 0.08),
        )

    exact, count, quality = best_counter_value(surface_index.get(surface, Counter()))
    if exact and quality >= 0.72:
        return MappingDecision(
            strong=exact.strong,
            prefixes=exact.prefixes,
            confidence="high" if quality >= 0.9 else "medium",
            method="attested_surface",
            evidence=f"surface={surface}; occurrences={count}; quality={quality:.3f}",
            score=quality,
        )

    best: MappingDecision | None = None
    for prefixes, root_surface in prefix_parses(text):
        if not root_surface:
            continue

        attested_candidate, attested_count, attested_quality = best_counter_value(
            base_form_index.get(root_surface, Counter())
        )
        lemma_candidate, lemma_count, lemma_quality = best_counter_value(
            lemma_index.get(root_surface, Counter())
        )

        candidate = attested_candidate
        candidate_count = attested_count
        candidate_quality = attested_quality
        method = "attested_prefixed_form"
        if lemma_candidate and (
            candidate is None or lemma_quality > candidate_quality + 0.08
        ):
            candidate = lemma_candidate
            candidate_count = lemma_count
            candidate_quality = lemma_quality
            method = "lexicon_lemma"
        if not candidate:
            continue

        prefix_penalty = 0.035 * len(prefixes)
        score = candidate_quality - prefix_penalty
        decision = MappingDecision(
            strong=composite_strong(prefixes, candidate),
            prefixes=prefixes,
            confidence="high" if score >= 0.88 else "medium",
            method=method,
            evidence=(
                f"root_surface={root_surface}; occurrences={candidate_count}; "
                f"quality={candidate_quality:.3f}"
            ),
            score=score,
        )
        if best is None or decision.score > best.score:
            best = decision

    return best if best and best.score >= 0.62 else None


def load_delitzsch_verses(book: str) -> dict[tuple[int, int], dict[str, Any]]:
    verses: dict[tuple[int, int], dict[str, Any]] = {}
    book_dir = DELITZSCH_ROOT / book
    if not book_dir.exists():
        return verses
    for chapter_path in sorted(book_dir.glob("*.json")):
        data = load_json(chapter_path)
        if not isinstance(data, list) or not data:
            continue
        chapter = data[0] if isinstance(data[0], dict) else {}
        for verse in chapter.get("verses") or []:
            key = (int(verse.get("chapter") or 0), int(verse.get("verse") or 0))
            verses[key] = verse
    return verses


def aligned_spelling_decision(
    hutter_word: str,
    delitzsch_word: dict[str, Any] | None,
) -> MappingDecision | None:
    if not delitzsch_word:
        return None
    hutter_surface = normalize_hebrew(hutter_word)
    delitzsch_surface = normalize_hebrew(str(delitzsch_word.get("text") or ""))
    if not hutter_surface or not delitzsch_surface:
        return None
    ratio = SequenceMatcher(None, hutter_surface, delitzsch_surface).ratio()
    if ratio < 0.78:
        return None
    candidate = candidate_from_word(delitzsch_word)
    if not candidate:
        return None
    return MappingDecision(
        strong=candidate.strong,
        prefixes=candidate.prefixes,
        confidence="medium" if ratio >= 0.86 else "low",
        method="aligned_spelling_variant",
        evidence=(
            f"hutter={hutter_surface}; delitzsch={delitzsch_surface}; "
            f"similarity={ratio:.3f}"
        ),
        score=ratio,
    )


def aligned_custom_name_decision(
    hutter_word: str,
    delitzsch_word: dict[str, Any] | None,
    custom_name_forms: dict[str, set[str]],
) -> MappingDecision | None:
    if not delitzsch_word:
        return None
    strong = base_strong(str(delitzsch_word.get("strong") or ""))
    if not strong or strong not in custom_name_forms:
        return None

    best_score = 0.0
    best_prefixes: tuple[str, ...] = ()
    best_surface = ""
    for prefixes, hutter_surface in prefix_parses(hutter_word):
        if len(hutter_surface) < 4:
            continue
        for custom_surface in custom_name_forms[strong]:
            score = SequenceMatcher(None, hutter_surface, custom_surface).ratio()
            if score > best_score:
                best_score = score
                best_prefixes = prefixes
                best_surface = custom_surface

    if best_score < 0.72:
        return None
    return MappingDecision(
        strong=composite_strong(best_prefixes, strong),
        prefixes=best_prefixes,
        confidence="high" if best_score >= 0.86 else "medium",
        method="aligned_custom_name",
        evidence=(
            f"hutter={normalize_hebrew(hutter_word)}; custom={best_surface}; "
            f"strong={strong}; similarity={best_score:.3f}"
        ),
        score=min(1.0, best_score + 0.08),
    )


def align_words(
    hutter_words: list[str],
    delitzsch_words: list[dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    hutter_surfaces = [normalize_hebrew(word) for word in hutter_words]
    delitzsch_surfaces = [
        normalize_hebrew(str(word.get("text") or "")) for word in delitzsch_words
    ]
    matcher = SequenceMatcher(None, hutter_surfaces, delitzsch_surfaces, autojunk=False)
    aligned: dict[int, dict[str, Any]] = {}
    for tag, h_start, h_end, d_start, d_end in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(h_end - h_start):
                aligned[h_start + offset] = delitzsch_words[d_start + offset]
            continue
        if tag == "replace" and h_end - h_start == d_end - d_start:
            for offset in range(h_end - h_start):
                aligned[h_start + offset] = delitzsch_words[d_start + offset]
    return aligned


def map_book(
    book: str,
    manual_overrides: dict[str, dict[str, Any]],
    custom_name_forms: dict[str, set[str]],
    pointed_surface_index: dict[str, Counter[StrongCandidate]],
    surface_index: dict[str, Counter[StrongCandidate]],
    base_form_index: dict[str, Counter[str]],
    lemma_index: dict[str, Counter[str]],
    include_low_confidence: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    hutter = load_json(HUTTER_ROOT / f"{book}.json")
    delitzsch = load_delitzsch_verses(book)
    transliterator = LocalTransliterator()
    chapters: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for chapter in hutter.get("chapters") or []:
        chapter_number = int(chapter.get("number") or 0)
        mapped_verses: list[dict[str, Any]] = []
        for verse in chapter.get("verses") or []:
            verse_number = int(verse.get("number") or 0)
            text = str(verse.get("text_nikud") or "").strip()
            hutter_words = split_hutter_words(text)
            delitzsch_verse = delitzsch.get((chapter_number, verse_number), {})
            delitzsch_words = delitzsch_verse.get("words") or []
            aligned = align_words(hutter_words, delitzsch_words)
            mapped_words: list[dict[str, Any]] = []

            for index, word_text in enumerate(hutter_words):
                transliteration = transliterator.transliterate_word(word_text)
                decision = decide_from_indexes(
                    word_text,
                    manual_overrides,
                    pointed_surface_index,
                    surface_index,
                    base_form_index,
                    lemma_index,
                )
                aligned_decision = aligned_spelling_decision(
                    word_text, aligned.get(index)
                )
                custom_name_decision = aligned_custom_name_decision(
                    word_text, aligned.get(index), custom_name_forms
                )
                if custom_name_decision and (
                    decision is None or custom_name_decision.score > decision.score
                ):
                    decision = custom_name_decision
                if aligned_decision and (
                    decision is None or aligned_decision.score > decision.score + 0.08
                ):
                    decision = aligned_decision

                if decision and (
                    decision.confidence != "low" or include_low_confidence
                ):
                    mapped_words.append(
                        {
                            "text": word_text,
                            "translit_en": transliteration.translit_en,
                            "translit_es": transliteration.translit_es,
                            "strong": decision.strong,
                            "prefixes": list(decision.prefixes),
                            "mapping_confidence": decision.confidence,
                            "mapping_method": decision.method,
                            "mapping_evidence": decision.evidence,
                        }
                    )
                    continue

                mapped_words.append(
                    {
                        "text": word_text,
                        "translit_en": transliteration.translit_en,
                        "translit_es": transliteration.translit_es,
                        "prefixes": [],
                        "mapping_confidence": "unresolved",
                        "mapping_method": "unresolved",
                    }
                )
                unresolved.append(
                    {
                        "book": book,
                        "chapter": chapter_number,
                        "verse": verse_number,
                        "position": index + 1,
                        "text": word_text,
                        "normalized": normalize_hebrew(word_text),
                        "aligned_delitzsch_word": aligned.get(index),
                    }
                )

            mapped_verses.append(
                {
                    "chapter": chapter_number,
                    "verse": verse_number,
                    "hebrew": text,
                    "words": mapped_words,
                }
            )

        chapters.append({"chapter": chapter_number, "verses": mapped_verses})

    return (
        {
            "book": book,
            "source": "Elias Hutter",
            "mapping_source": "Davar corpus and lexicon alignment",
            "chapters": chapters,
        },
        unresolved,
    )


def main() -> int:
    args = parse_args()
    available_books = sorted(
        path.stem
        for path in HUTTER_ROOT.glob("*.json")
        if (DELITZSCH_ROOT / path.stem).is_dir()
    )
    books = args.books or available_books
    missing = [book for book in books if book not in available_books]
    if missing:
        raise SystemExit(f"Unknown or non-New-Testament Hutter books: {', '.join(missing)}")

    pointed_surface_index, surface_index, base_form_index, lemma_index = build_indexes()
    manual_overrides = load_manual_overrides()
    custom_name_forms = load_custom_name_forms()
    output_root = args.output_root.expanduser().resolve()
    report_path = args.report.expanduser().resolve()
    all_unresolved: list[dict[str, Any]] = []
    book_summaries: list[dict[str, Any]] = []

    for book in books:
        payload, unresolved = map_book(
            book,
            manual_overrides,
            custom_name_forms,
            pointed_surface_index,
            surface_index,
            base_form_index,
            lemma_index,
            args.include_low_confidence,
        )
        words = [
            word
            for chapter in payload["chapters"]
            for verse in chapter["verses"]
            for word in verse["words"]
        ]
        confidence_counts = Counter(
            str(word.get("mapping_confidence") or "unresolved") for word in words
        )
        book_summaries.append(
            {
                "book": book,
                "verse_count": sum(
                    len(chapter["verses"]) for chapter in payload["chapters"]
                ),
                "word_count": len(words),
                "mapped_count": len(words) - len(unresolved),
                "unresolved_count": len(unresolved),
                "coverage": (
                    (len(words) - len(unresolved)) / len(words) if words else 0.0
                ),
                "confidence_counts": dict(sorted(confidence_counts.items())),
            }
        )
        all_unresolved.extend(unresolved)

        if args.write:
            output_root.mkdir(parents=True, exist_ok=True)
            (output_root / f"{book}.json").write_text(
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )

    total_words = sum(item["word_count"] for item in book_summaries)
    total_unresolved = len(all_unresolved)
    report = {
        "books": book_summaries,
        "totals": {
            "book_count": len(book_summaries),
            "word_count": total_words,
            "mapped_count": total_words - total_unresolved,
            "unresolved_count": total_unresolved,
            "coverage": (
                (total_words - total_unresolved) / total_words if total_words else 0.0
            ),
        },
        "unresolved": all_unresolved,
    }

    if args.write:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(json.dumps(report["totals"], ensure_ascii=False, indent=2))
    for summary in book_summaries:
        print(
            f"{summary['book']}: {summary['mapped_count']}/{summary['word_count']} "
            f"({summary['coverage']:.1%}) unresolved={summary['unresolved_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
