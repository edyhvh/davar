"""
JSON data loaders for Hebrew Scripture data sources
"""

from functools import lru_cache
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from app.config import settings


class DataLoader:
    """Base class for data loaders with caching"""

    def __init__(self, data_path: str = None):
        self.data_path = Path(data_path or settings.data_path)
        self._cache: Dict[str, Any] = {}

    @lru_cache(maxsize=100)
    def load_json(self, filepath: str) -> Dict[str, Any]:
        """Load JSON file with caching"""
        full_path = self.data_path / filepath
        if not full_path.exists():
            raise FileNotFoundError(f"Data file not found: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def clear_cache(self):
        """Clear the LRU cache"""
        self.load_json.cache_clear()
        self._cache.clear()


# Import all loaders
from .tanaj import tanaj_loader
from .besorah import besorah_loader
from .translations import translation_loader
from .variants import variant_loader
from .dictionary import dictionary_loader
from .book_mapping import book_mapper

__all__ = [
    "DataLoader",
    "tanaj_loader",
    "besorah_loader",
    "translation_loader",
    "variant_loader",
    "dictionary_loader",
    "book_mapper"
]