"""
Local processing pipeline for DSS variant transliteration (no API calls).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import DSS_BOOKS_DIR, DSS_TRANSLIT_DIR
from .local_translit import LocalTransliterator

logger = logging.getLogger(__name__)

MAQAF = "\u05BE"


@dataclass
class DssBookStats:
    book_id: str
    variants: int = 0
    failed: int = 0


def _load_dss_book(book_id: str) -> Dict:
    book_path = DSS_BOOKS_DIR / f"{book_id}.json"
    if not book_path.exists():
        raise FileNotFoundError(f"DSS book not found: {book_path}")

    with open(book_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _transliterate_phrase(
    transliterator: LocalTransliterator,
    text: str,
) -> Tuple[str, str]:
    if not text:
        return "", ""

    en_tokens: List[str] = []
    es_tokens: List[str] = []

    for token in text.split():
        if not token:
            continue
        parts = [p for p in token.split(MAQAF) if p]
        en_parts: List[str] = []
        es_parts: List[str] = []
        for part in parts:
            result = transliterator.transliterate_word(part)
            en_parts.append(result.translit_en)
            es_parts.append(result.translit_es)
        if en_parts:
            en_tokens.append("-".join(en_parts))
        if es_parts:
            es_tokens.append("-".join(es_parts))

    return " ".join(en_tokens), " ".join(es_tokens)


def transliterate_dss_book(
    book_id: str,
    dry_run: bool = False,
) -> DssBookStats:
    data = _load_dss_book(book_id)
    transliterator = LocalTransliterator()
    stats = DssBookStats(book_id=book_id)

    variants: List[Dict] = []
    chapters = data.get("chapters", {})
    for chapter_key, chapter_data in chapters.items():
        verses = chapter_data.get("verses", {})
        for verse_key, verse_data in verses.items():
            differences = verse_data.get("differences", []) or []
            for difference in differences:
                dss_word = difference.get("dss_word", "")
                try:
                    translit_en, translit_es = _transliterate_phrase(
                        transliterator, dss_word
                    )
                except Exception as exc:
                    logger.warning(
                        "Failed to transliterate DSS word '%s' in %s %s:%s: %s",
                        dss_word,
                        book_id,
                        chapter_key,
                        verse_key,
                        exc,
                    )
                    stats.failed += 1
                    translit_en, translit_es = "", ""

                variants.append(
                    {
                        "book": data.get("name", book_id),
                        "chapter": int(chapter_key),
                        "verse": int(verse_key),
                        "position": difference.get("position", 0),
                        "dss_word": dss_word,
                        "translit_en": translit_en,
                        "translit_es": translit_es,
                    }
                )
                stats.variants += 1

    output = {
        "book_id": book_id,
        "source": "dss",
        "language_targets": ["en", "es"],
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "variants": variants,
    }

    if not dry_run:
        DSS_TRANSLIT_DIR.mkdir(parents=True, exist_ok=True)
        out_file = DSS_TRANSLIT_DIR / f"{book_id}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, separators=(",", ":"))
        logger.info("Wrote DSS transliteration output to %s", out_file)
    else:
        logger.info("Dry run - skipping DSS transliteration file write")

    return stats


def get_available_dss_books() -> List[str]:
    if not DSS_BOOKS_DIR.exists():
        return []
    return sorted(
        path.stem
        for path in DSS_BOOKS_DIR.glob("*.json")
        if path.is_file()
    )
