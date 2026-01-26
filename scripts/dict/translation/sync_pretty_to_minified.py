#!/usr/bin/env python3
"""
Sync pretty-printed lexicon files to minified versions.

Copies the contents of roots.pretty.json -> roots.json and
words.pretty.json -> words.json with minified formatting.
"""

import json
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def _load_json(file_path: Path) -> Dict:
    """Load a JSON file."""
    with open(file_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_minified(data: Dict, file_path: Path) -> None:
    """Save JSON in minified format."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))


def sync_file(pretty_path: Path, minified_path: Path) -> None:
    """Sync a pretty JSON file to its minified counterpart."""
    logger.info("Loading %s", pretty_path)
    data = _load_json(pretty_path)

    logger.info("Saving %s", minified_path)
    _save_minified(data, minified_path)


def main() -> int:
    """Entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    project_root = Path(__file__).parent.parent.parent.parent
    lexicon_dir = project_root / "data" / "dict" / "lexicon"

    roots_pretty = lexicon_dir / "roots.pretty.json"
    roots_minified = lexicon_dir / "roots.json"
    words_pretty = lexicon_dir / "words.pretty.json"
    words_minified = lexicon_dir / "words.json"

    sync_file(roots_pretty, roots_minified)
    sync_file(words_pretty, words_minified)

    logger.info("Sync complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
