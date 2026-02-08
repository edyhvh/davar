#!/usr/bin/env python3
"""
Configuration and constants for DSS parser
"""

from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
REPO_BASE = SCRIPT_DIR.parent.parent / "data/dss/deadseainsights/data"
DSS_DIR = REPO_BASE / "DSS_TC"
WLC_DIR = REPO_BASE / "tanach/Books"
NOTES_FILE = DSS_DIR / "DSS_TC_Notes.xml"
OUTPUT_DIR = SCRIPT_DIR.parent.parent / "data/dss/dssi"

# Book name mappings (XML name -> English display name)
BOOK_NAMES = {
    "1Kings": "1 Kings",
    "2Kings": "2 Kings",
    "1Samuel": "1 Samuel",
    "2Samuel": "2 Samuel",
    "2Chronicles": "2 Chronicles",
    "Amos": "Amos",
    "Canticles": "Song of Songs",
    "Daniel": "Daniel",
    "Deuteronomy": "Deuteronomy",
    "Ecclesiastes": "Ecclesiastes",
    "Exodus": "Exodus",
    "Ezekiel": "Ezekiel",
    "Ezra": "Ezra",
    "Genesis": "Genesis",
    "Habakkuk": "Habakkuk",
    "Haggai": "Haggai",
    "Hosea": "Hosea",
    "Isaiah": "Isaiah",
    "Jeremiah": "Jeremiah",
    "Job": "Job",
    "Joel": "Joel",
    "Jonah": "Jonah",
    "Joshua": "Joshua",
    "Judges": "Judges",
    "Lamentations": "Lamentations",
    "Leviticus": "Leviticus",
    "Malachi": "Malachi",
    "Micah": "Micah",
    "Nahum": "Nahum",
    "Numbers": "Numbers",
    "Obadiah": "Obadiah",
    "Proverbs": "Proverbs",
    "Psalms": "Psalms",
    "Ruth": "Ruth",
    "Zechariah": "Zechariah",
    "Zephaniah": "Zephaniah"
}

# Metadata
SOURCE_URL = 'https://codeberg.org/dandeto/deadseainsights'
LICENSE = 'CC BY-SA 4.0'
