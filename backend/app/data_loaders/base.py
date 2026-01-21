"""
Base data loader class with caching functionality
"""

from functools import lru_cache
import json
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import orjson  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - fallback for environments without orjson
    orjson = None

from app.config import settings


class DataLoader:
    """Base class for data loaders with caching"""

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path or settings.data_path)
        self._cache: Dict[str, Any] = {}

    @lru_cache(maxsize=100)
    def load_json(self, filepath: str) -> Dict[str, Any]:
        """Load JSON file with caching"""
        full_path = self.data_path / filepath
        if not full_path.exists():
            raise FileNotFoundError(f"Data file not found: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if orjson:
                return orjson.loads(content)
            return json.loads(content)

    def clear_cache(self):
        """Clear the LRU cache"""
        self.load_json.cache_clear()
        self._cache.clear()