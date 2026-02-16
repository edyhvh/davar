#!/usr/bin/env python3
"""Compatibility wrapper for the legacy run matcher entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    scripts_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(scripts_dir))
    from delitzsch.commands.run import main
    from delitzsch.matcher_runner import process_all_books, process_book, save_chapter_data, setup_logging, log_unmatched_words
else:
    from .commands.run import main
    from .matcher_runner import process_all_books, process_book, save_chapter_data, setup_logging, log_unmatched_words


if __name__ == "__main__":
    raise SystemExit(main())
