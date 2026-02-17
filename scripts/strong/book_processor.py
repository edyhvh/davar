"""Compatibility shim for migrated Delitzsch book processor."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "delitzsch"))

from scripts.delitzsch.book_processor import *  # noqa: F401,F403
