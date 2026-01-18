"""
Dictionary data loader
Loads lexicon (custom definitions, BDB/Strong's) and prefix data
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from . import DataLoader


class DictionaryLoader(DataLoader):
    """Loader for dictionary data (lexicon and prefixes)"""

    def __init__(self, data_path: str = None):
        super().__init__(data_path)
        self.lexicon_path = self.data_path / "dict" / "lexicon"
        self.prefixes_path = self.data_path / "dict" / "prefixes"

    def load_custom_definitions(self) -> Dict[str, Any]:
        """Load custom definitions dictionary"""
        cache_key = "custom_definitions"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            data = self.load_json("dict/lexicon/custom_definitions.json")
            self._cache[cache_key] = data
            return data
        except FileNotFoundError:
            return {}

    def load_roots_lexicon(self) -> Dict[str, Any]:
        """Load full roots lexicon (BDB/Strong's)"""
        cache_key = "roots_lexicon"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            data = self.load_json("dict/lexicon/roots.pretty.json")
            self._cache[cache_key] = data
            return data
        except FileNotFoundError:
            return {}

    def get_custom_definition(self, strong_number: str) -> Optional[Dict[str, Any]]:
        """Get custom definition for a Strong's number"""
        custom_defs = self.load_custom_definitions()
        return custom_defs.get(strong_number)

    def get_lexicon_entry(self, strong_number: str) -> Optional[Dict[str, Any]]:
        """Get lexicon entry for a Strong's number, preferring custom definitions"""
        # First try custom definitions
        custom_defs = self.load_custom_definitions()
        if strong_number in custom_defs:
            return custom_defs[strong_number]

        # Fall back to BDB/Strong's
        roots_lexicon = self.load_roots_lexicon()
        if strong_number in roots_lexicon:
            return roots_lexicon[strong_number]

        return None

    def load_prefix_data(self, prefix_id: str) -> Optional[Dict[str, Any]]:
        """Load prefix definition data"""
        cache_key = f"prefix_{prefix_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            data = self.load_json(f"dict/prefixes/entries/{prefix_id}.json")
            self._cache[cache_key] = data
            return data
        except FileNotFoundError:
            return None

    def get_prefix(self, prefix_id: str) -> Optional[Dict[str, Any]]:
        """Get prefix definition data"""
        return self.load_prefix_data(prefix_id)

    def get_available_prefixes(self) -> List[str]:
        """Get list of available prefix IDs"""
        entries_path = self.prefixes_path / "entries"
        if not entries_path.exists():
            return []

        prefixes = []
        for file_path in entries_path.glob("*.json"):
            prefix_id = file_path.stem
            prefixes.append(prefix_id)
        return sorted(prefixes)

    def search_lexicon(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search lexicon entries (basic implementation)"""
        # This is a basic search - could be enhanced with proper indexing
        custom_defs = self.load_custom_definitions()
        results = []

        for strong_num, entry in custom_defs.items():
            hebrew = entry.get("hebrew", "").lower()
            translit_en = entry.get("transliteration_en", "").lower()
            translit_es = entry.get("transliteration_es", "").lower()

            if (query.lower() in hebrew or
                query.lower() in translit_en or
                query.lower() in translit_es):
                results.append(entry)
                if len(results) >= limit:
                    break

        return results


# Global instance
dictionary_loader = DictionaryLoader()