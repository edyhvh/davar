"""
TTH Processing System - Temp (Modified) Version
================================================

Modified version of the TTH processing system that includes text cleaning
to fix common conversion issues:

1. Soft hyphens (word breaks like "Is\\-rael" -> "Israel")
2. Missing spaces after punctuation (":יהוה" -> ": יהוה")
3. Stuck connectors ("Ashdody" -> "Ashdod y")

Usage:
    from scripts.tth.temp import process_book_to_json
    process_book_to_json('amos', 'path/to/amos.md', 'output/')

Author: Davar Project
"""

from .text_cleaner import TTHTextCleaner, clean_text
from .processor import TTHProcessor, process_book_to_json

__all__ = [
    'TTHTextCleaner',
    'TTHProcessor',
    'clean_text',
    'process_book_to_json'
]

