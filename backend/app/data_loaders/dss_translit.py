"""
DSS transliteration data loader
Loads DSS variant transliterations from data/translit/dss JSON files
"""

from typing import Dict, Any, Optional
from .base import DataLoader
from .book_mapping import book_mapper


class DssTranslitLoader(DataLoader):
    """Loader for DSS variant transliteration data"""

    def __init__(self, data_path: Optional[str] = None):
        super().__init__(data_path)
        self.dss_translit_path = self.data_path / "translit" / "dss"

    def load_book(self, book_name: str) -> Optional[Dict[str, Any]]:
        book_key = book_mapper.to_dss_key(book_name)
        if not book_key:
            return None

        cache_key = f"dss_translit:{book_key}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            data = self.load_json(f"translit/dss/{book_key}.json")
        except FileNotFoundError:
            return None

        variants_index: Dict[int, Dict[int, Dict[int, Dict[str, Any]]]] = {}
        for variant in data.get("variants", []) or []:
            chapter = variant.get("chapter")
            verse = variant.get("verse")
            position = variant.get("position")
            if chapter is None or verse is None or position is None:
                continue
            variants_index.setdefault(int(chapter), {}).setdefault(
                int(verse), {}
            )[int(position)] = variant

        indexed = {
            "book_id": data.get("book_id"),
            "variants": variants_index,
        }
        self._cache[cache_key] = indexed
        return indexed

    def get_variant_translit(
        self,
        book_name: str,
        chapter: int,
        verse: int,
        position: int,
    ) -> Optional[Dict[str, Any]]:
        book_data = self.load_book(book_name)
        if not book_data:
            return None
        return (
            book_data.get("variants", {})
            .get(chapter, {})
            .get(verse, {})
            .get(position)
        )


# Global instance
dss_translit_loader = DssTranslitLoader()
