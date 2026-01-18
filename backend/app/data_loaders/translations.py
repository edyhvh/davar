"""
Translation data loader
Loads TTH (Spanish) and TS2009 (English) translations
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from . import DataLoader


class TranslationLoader(DataLoader):
    """Loader for translation data (TTH Spanish, TS2009 English)"""

    def __init__(self, data_path: str = None):
        super().__init__(data_path)
        self.tth_path = self.data_path / "tth" / "draft"
        self.ts2009_path = self.data_path / "ts2009"

    def load_tth_verse(self, book_name: str, chapter: int, verse: int, language: str = "es") -> Optional[dict]:
        """Load TTH translation for a specific verse"""
        cache_key = f"tth_{book_name}_{chapter}_{verse}_{language}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # TTH uses Hebrew book names, so we need to map from English to Hebrew names
        hebrew_book_name = self._english_to_hebrew_book_name(book_name)
        if not hebrew_book_name:
            return None

        file_path = f"tth/draft/{hebrew_book_name}/{chapter:02d}.json"
        try:
            chapter_data = self.load_json(file_path)
            for verse_data in chapter_data:
                if (verse_data.get("chapter") == chapter and
                    verse_data.get("verse") == verse):
                    translation = verse_data.get("tth", "")
                    footnotes = verse_data.get("footnotes", [])
                    result = {
                        "translation": translation,
                        "footnotes": footnotes
                    }
                    self._cache[cache_key] = result
                    return result
        except (FileNotFoundError, KeyError):
            pass

        self._cache[cache_key] = None
        return None

    def load_ts2009_verse(self, book_name: str, chapter: int, verse: int) -> Optional[str]:
        """Load TS2009 English translation for a specific verse"""
        cache_key = f"ts2009_{book_name}_{chapter}_{verse}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # TS2009 uses Hebrew book names
        hebrew_book_name = self._english_to_hebrew_book_name(book_name)
        if not hebrew_book_name:
            return None

        try:
            book_data = self.load_json(f"ts2009/{hebrew_book_name}.json")
            # TS2009 data has a "verses" array with objects containing chapter, verse, text
            if "verses" in book_data:
                verses = book_data["verses"]
                for verse_data in verses:
                    if (verse_data.get("chapter") == chapter and
                        verse_data.get("verse") == verse):
                        translation = verse_data.get("text", "")
                        self._cache[cache_key] = translation
                        return translation
        except (FileNotFoundError, KeyError):
            pass

        self._cache[cache_key] = None
        return None

    def get_translation(self, book_name: str, chapter: int, verse: int, language: str) -> Optional[dict]:
        """Get translation for a verse in specified language"""
        if language.lower() == "es":
            return self.load_tth_verse(book_name, chapter, verse, language)
        elif language.lower() == "en":
            translation = self.load_ts2009_verse(book_name, chapter, verse)
            return {"translation": translation, "footnotes": None} if translation else None
        return None

    def _english_to_hebrew_book_name(self, english_name: str) -> Optional[str]:
        """Map English book names to Hebrew names used in translation files"""
        mapping = {
            "Genesis": "bereshit",
            "Exodus": "shemot",
            "Leviticus": "vaikra",
            "Numbers": "bamidbar",
            "Deuteronomy": "devarim",
            "Joshua": "iehosua",
            "Judges": "shoftim",
            "Samuel1": "shemuel_alef",
            "Samuel2": "shemuel_bet",
            "Kings1": "melajim_alef",
            "Kings2": "melajim_bet",
            "Isaiah": "ieshaiahu",
            "Jeremiah": "irmeiahu",
            "Ezekiel": "iejezkel",
            "Hosea": "hoshea",
            "Joel": "ioel",
            "Amos": "amos",
            "Obadiah": "ovadia",
            "Jonah": "ionah",
            "Micah": "micah",
            "Nahum": "najum",
            "Habakkuk": "jabakuk",
            "Zephaniah": "tzefaniah",
            "Haggai": "jagai",
            "Zechariah": "zejariah",
            "Malachi": "malaji",
            "Psalms": "tehilim",
            "Proverbs": "mishlei",
            "Job": "iyov",
            "SongOfSolomon": "shir_hashirim",
            "Ruth": "rut",
            "Lamentations": "eka",
            "Ecclesiastes": "kohelet",
            "Esther": "ester",
            "Daniel": "daniel",
            "Ezra": "ezra",
            "Nehemiah": "nehemya",
            "Chronicles1": "divrei_hayamim_alef",
            "Chronicles2": "divrei_hayamim_bet",
            # Besorah books
            "Matthew": "mattityahu",
            "Mark": "marqos",
            "Luke": "luqas",
            "John": "yohanan",
            "Acts": "maasei",
            "Romans": "romiyim",
            "Corinthians1": "qorintim_alef",
            "Corinthians2": "qorintim_bet",
            "Galatians": "galatiyim",
            "Ephesians": "efesiyim",
            "Philippians": "pilipiyim",
            "Colossians": "qolasim",
            "Thessalonians1": "tesalonikim_alef",
            "Thessalonians2": "tesalonikim_bet",
            "Timothy1": "timotiyos_alef",
            "Timothy2": "timotiyos_bet",
            "Titus": "titos",
            "Philemon": "filemon",
            "Hebrews": "ivrim",
            "James": "yaakov",
            "Peter1": "kefa_alef",
            "Peter2": "kefa_bet",
            "John1": "yohanan_alef",
            "John2": "yohanan_bet",
            "John3": "yohanan_gimel",
            "Jude": "yehudah",
            "Revelation": "hitgalut"
        }
        return mapping.get(english_name)


# Global instance
translation_loader = TranslationLoader()