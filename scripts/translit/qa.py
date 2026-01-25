"""
Quality checks for transliteration outputs.
"""

import json
from pathlib import Path
from typing import Dict


def _load_book(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_book(path: Path) -> Dict[str, int]:
    data = _load_book(path)
    stats = {
        "verses": 0,
        "words": 0,
        "missing_en": 0,
        "missing_es": 0,
        "missing_ids": 0,
    }

    for verse in data.get("verses", []):
        stats["verses"] += 1
        for word in verse.get("words", []):
            stats["words"] += 1
            if not word.get("id"):
                stats["missing_ids"] += 1
            if not word.get("translit_en"):
                stats["missing_en"] += 1
            if not word.get("translit_es"):
                stats["missing_es"] += 1

    return stats
