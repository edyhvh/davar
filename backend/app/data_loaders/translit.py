"""
Transliteration data loader
Loads word-level transliteration data from data/translit JSON files
"""

from typing import Dict, List, Any, Optional
from .base import DataLoader


class TranslitLoader(DataLoader):
    """Loader for word-level transliteration data"""

    def __init__(self, data_path: Optional[str] = None):
        super().__init__(data_path)
        self.translit_path = self.data_path / "translit"
        self.oe_aliases = {
            "samuel1": "isamuel",
            "samuel2": "iisamuel",
            "kings1": "ikings",
            "kings2": "iikings",
            "chronicles1": "ichronicles",
            "chronicles2": "iichronicles",
        }

    def _resolve_book_name(self, book_name: str) -> str:
        normalized = book_name.lower()
        if (self.translit_path / f"{normalized}.json").exists():
            return normalized
        alias = self.oe_aliases.get(normalized)
        if alias and (self.translit_path / f"{alias}.json").exists():
            return alias
        return normalized

    def load_book(self, book_name: str) -> Optional[Dict[str, Any]]:
        """Load and index transliteration data for a book"""
        resolved_name = self._resolve_book_name(book_name)
        cache_key = f"translit_{resolved_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        file_path = f"translit/{resolved_name}.json"
        try:
            data = self.load_json(file_path)
        except FileNotFoundError:
            return None

        verses_index: Dict[int, Dict[int, List[Dict[str, Any]]]] = {}
        for verse in data.get("verses", []) or []:
            chapter = verse.get("chapter")
            verse_num = verse.get("verse")
            if not chapter or not verse_num:
                continue
            verses_index.setdefault(chapter, {})[verse_num] = verse.get(
                "words", []) or []

        indexed = {
            "book_id": data.get("book_id"),
            "verses": verses_index,
        }
        self._cache[cache_key] = indexed
        return indexed

    def get_verse_words(
        self,
        book_name: str,
        chapter: int,
        verse: int,
    ) -> List[Dict[str, Any]]:
        """Get transliteration word list for a verse"""
        book_data = self.load_book(book_name)
        if not book_data:
            return []
        return book_data.get("verses", {}).get(chapter, {}).get(verse, [])


# Global instance
translit_loader = TranslitLoader()
