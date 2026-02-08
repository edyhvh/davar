"""
Book name normalization mappings
Maps various source naming conventions to Standard English canonical names
"""

from typing import Dict, Optional
from .translations import TTH_BOOK_MAPPING, TS2009_BOOK_MAPPING


class BookNameMapper:
    """Maps book names from various sources to canonical English names"""

    def __init__(self):
        # OE (Open English) mappings - mostly English already
        self.oe_to_english = {
            "genesis": "Genesis",
            "exodus": "Exodus",
            "leviticus": "Leviticus",
            "numbers": "Numbers",
            "deuteronomy": "Deuteronomy",
            "joshua": "Joshua",
            "judges": "Judges",
            "isamuel": "Samuel1",
            "samuel1": "Samuel1",
            "1sam": "Samuel1",
            "iisamuel": "Samuel2",
            "samuel2": "Samuel2",
            "2sam": "Samuel2",
            "ikings": "Kings1",
            "kings1": "Kings1",
            "1kgs": "Kings1",
            "iikings": "Kings2",
            "kings2": "Kings2",
            "2kgs": "Kings2",
            "isaiah": "Isaiah",
            "jeremiah": "Jeremiah",
            "ezekiel": "Ezekiel",
            "hosea": "Hosea",
            "joel": "Joel",
            "amos": "Amos",
            "obadiah": "Obadiah",
            "jonah": "Jonah",
            "micah": "Micah",
            "nahum": "Nahum",
            "habakkuk": "Habakkuk",
            "zephaniah": "Zephaniah",
            "haggai": "Haggai",
            "zechariah": "Zechariah",
            "malachi": "Malachi",
            "psalms": "Psalms",
            "proverbs": "Proverbs",
            "job": "Job",
            "songofsolomon": "SongOfSolomon",
            "ruth": "Ruth",
            "lamentations": "Lamentations",
            "ecclesiastes": "Ecclesiastes",
            "esther": "Esther",
            "daniel": "Daniel",
            "ezra": "Ezra",
            "nehemiah": "Nehemiah",
            "ichronicles": "Chronicles1",
            "chronicles1": "Chronicles1",
            "1chr": "Chronicles1",
            "iichronicles": "Chronicles2",
            "chronicles2": "Chronicles2",
            "2chr": "Chronicles2"
        }

        # Delitzsch mappings
        self.delitzsch_to_english = {
            "matthew": "Matthew",
            "mark": "Mark",
            "luke": "Luke",
            "john": "John",
            "acts": "Acts",
            "romans": "Romans",
            "corinthians1": "Corinthians1",
            "corinthians2": "Corinthians2",
            "galatians": "Galatians",
            "ephesians": "Ephesians",
            "philippians": "Philippians",
            "colossians": "Colossians",
            "thessalonians1": "Thessalonians1",
            "thessalonians2": "Thessalonians2",
            "timothy1": "Timothy1",
            "timothy2": "Timothy2",
            "titus": "Titus",
            "philemon": "Philemon",
            "hebrews": "Hebrews",
            "james": "James",
            "peter1": "Peter1",
            "peter2": "Peter2",
            "john1": "John1",
            "john2": "John2",
            "john3": "John3",
            "jude": "Jude",
            "revelation": "Revelation"
        }

        # TTH Hebrew transliterations to English
        self.tth_to_english = {value: key for key, value in TTH_BOOK_MAPPING.items()}

        # TS2009 Hebrew transliterations to English
        self.ts2009_to_english = {value: key for key, value in TS2009_BOOK_MAPPING.items()}

        # DSS mappings (book names in DSS data)
        self.dss_to_english = {
            "1samuel": "Samuel1",
            "2samuel": "Samuel2",
            "amos": "Amos",
            "deuteronomy": "Deuteronomy",
            "exodus": "Exodus",
            "ezekiel": "Ezekiel",
            "genesis": "Genesis",
            "habakkuk": "Habakkuk",
            "haggai": "Haggai",
            "hoseah": "Hosea",
            "isaiah": "Isaiah",
            "joel": "Joel",
            "jonah": "Jonah",
            "judges": "Judges",
            "jeremiah": "Jeremiah",
            "lamentations": "Lamentations",
            "leviticus": "Leviticus",
            "micah": "Micah",
            "nahum": "Nahum",
            "numbers": "Numbers",
            "obadiah": "Obadiah",
            "psalms": "Psalms",
            "job": "Job",
            "proverbs": "Proverbs",
            "ruth": "Ruth",
            "songs": "SongOfSolomon",
            "ecclesiastes": "Ecclesiastes",
            "esther": "Esther",
            "daniel": "Daniel",
            "ezra": "Ezra",
            "nehemiah": "Nehemiah",
            "chronicles1": "Chronicles1",
            "chronicles2": "Chronicles2",
            "zephaniah": "Zephaniah"
        }

        self.english_to_dss = {value: key for key, value in self.dss_to_english.items()}

        # Book metadata for canonical English names
        self.book_metadata = {
            "Genesis": {"section": "torah", "order": 1, "chapters": 50, "hebrew_name": "בראשית", "hebrew_transliteration": "Bereshit", "spanish_name": "Génesis"},
            "Exodus": {"section": "torah", "order": 2, "chapters": 40, "hebrew_name": "שמות", "hebrew_transliteration": "Shemot", "spanish_name": "Éxodo"},
            "Leviticus": {"section": "torah", "order": 3, "chapters": 27, "hebrew_name": "ויקרא", "hebrew_transliteration": "Vaikra", "spanish_name": "Levítico"},
            "Numbers": {"section": "torah", "order": 4, "chapters": 36, "hebrew_name": "במדבר", "hebrew_transliteration": "Bamidbar", "spanish_name": "Números"},
            "Deuteronomy": {"section": "torah", "order": 5, "chapters": 34, "hebrew_name": "דברים", "hebrew_transliteration": "Devarim", "spanish_name": "Deuteronomio"},
            "Joshua": {"section": "neviim", "order": 6, "chapters": 24, "hebrew_name": "יהושע", "hebrew_transliteration": "Yehoshua", "spanish_name": "Josué"},
            "Judges": {"section": "neviim", "order": 7, "chapters": 21, "hebrew_name": "שופטים", "hebrew_transliteration": "Shoftim", "spanish_name": "Jueces"},
            "Samuel1": {"section": "neviim", "order": 8, "chapters": 31, "hebrew_name": "שמואל א", "hebrew_transliteration": "Shemuel Alef", "spanish_name": "Samuel 1"},
            "Samuel2": {"section": "neviim", "order": 9, "chapters": 24, "hebrew_name": "שמואל ב", "hebrew_transliteration": "Shemuel Bet", "spanish_name": "Samuel 2"},
            "Kings1": {"section": "neviim", "order": 10, "chapters": 22, "hebrew_name": "מלכים א", "hebrew_transliteration": "Melajim Alef", "spanish_name": "Reyes 1"},
            "Kings2": {"section": "neviim", "order": 11, "chapters": 25, "hebrew_name": "מלכים ב", "hebrew_transliteration": "Melajim Bet", "spanish_name": "Reyes 2"},
            "Isaiah": {"section": "neviim", "order": 12, "chapters": 66, "hebrew_name": "ישעיהו", "hebrew_transliteration": "Yeshaiahu", "spanish_name": "Isaías"},
            "Jeremiah": {"section": "neviim", "order": 13, "chapters": 52, "hebrew_name": "ירמיהו", "hebrew_transliteration": "Yrmeiahu", "spanish_name": "Jeremías"},
            "Ezekiel": {"section": "neviim", "order": 14, "chapters": 48, "hebrew_name": "יחזקאל", "hebrew_transliteration": "Yejezkel", "spanish_name": "Ezequiel"},
            "Hosea": {"section": "neviim", "order": 15, "chapters": 14, "hebrew_name": "הושע", "hebrew_transliteration": "Hoshea", "spanish_name": "Oseas"},
            "Joel": {"section": "neviim", "order": 16, "chapters": 4, "hebrew_name": "יואל", "hebrew_transliteration": "Yoel", "spanish_name": "Joel"},
            "Amos": {"section": "neviim", "order": 17, "chapters": 9, "hebrew_name": "עמוס", "hebrew_transliteration": "Amos", "spanish_name": "Amós"},
            "Obadiah": {"section": "neviim", "order": 18, "chapters": 1, "hebrew_name": "עובדיה", "hebrew_transliteration": "Ovadiah", "spanish_name": "Abdías"},
            "Jonah": {"section": "neviim", "order": 19, "chapters": 4, "hebrew_name": "יונה", "hebrew_transliteration": "Yonah", "spanish_name": "Jonás"},
            "Micah": {"section": "neviim", "order": 20, "chapters": 7, "hebrew_name": "מיכה", "hebrew_transliteration": "Mijah", "spanish_name": "Miqueas"},
            "Nahum": {"section": "neviim", "order": 21, "chapters": 3, "hebrew_name": "נחום", "hebrew_transliteration": "Najum", "spanish_name": "Nahúm"},
            "Habakkuk": {"section": "neviim", "order": 22, "chapters": 3, "hebrew_name": "חבקוק", "hebrew_transliteration": "Jabaquq", "spanish_name": "Habacuc"},
            "Zephaniah": {"section": "neviim", "order": 23, "chapters": 3, "hebrew_name": "צפניה", "hebrew_transliteration": "Tzufaniah", "spanish_name": "Sofonías"},
            "Haggai": {"section": "neviim", "order": 24, "chapters": 2, "hebrew_name": "חגי", "hebrew_transliteration": "Jagai", "spanish_name": "Hageo"},
            "Zechariah": {"section": "neviim", "order": 25, "chapters": 14, "hebrew_name": "זכריה", "hebrew_transliteration": "Zejariah", "spanish_name": "Zacarías"},
            "Malachi": {"section": "neviim", "order": 26, "chapters": 3, "hebrew_name": "מלאכי", "hebrew_transliteration": "Malaji", "spanish_name": "Malaquías"},
            "Psalms": {"section": "ketuvim", "order": 27, "chapters": 150, "hebrew_name": "תהלים", "hebrew_transliteration": "Tehilim", "spanish_name": "Salmos"},
            "Proverbs": {"section": "ketuvim", "order": 28, "chapters": 31, "hebrew_name": "משלי", "hebrew_transliteration": "Mishlei", "spanish_name": "Proverbios"},
            "Job": {"section": "ketuvim", "order": 29, "chapters": 42, "hebrew_name": "איוב", "hebrew_transliteration": "Iyov", "spanish_name": "Job"},
            "SongOfSolomon": {"section": "ketuvim", "order": 30, "chapters": 8, "hebrew_name": "שיר השירים", "hebrew_transliteration": "Shir Hashirim", "spanish_name": "Cantares"},
            "Ruth": {"section": "ketuvim", "order": 31, "chapters": 4, "hebrew_name": "רות", "hebrew_transliteration": "Rut", "spanish_name": "Rut"},
            "Lamentations": {"section": "ketuvim", "order": 32, "chapters": 5, "hebrew_name": "איכה", "hebrew_transliteration": "Eijah", "spanish_name": "Lamentaciones"},
            "Ecclesiastes": {"section": "ketuvim", "order": 33, "chapters": 12, "hebrew_name": "קהלת", "hebrew_transliteration": "Kohelet", "spanish_name": "Eclesiastés"},
            "Esther": {"section": "ketuvim", "order": 34, "chapters": 10, "hebrew_name": "אסתר", "hebrew_transliteration": "Ester", "spanish_name": "Ester"},
            "Daniel": {"section": "ketuvim", "order": 35, "chapters": 12, "hebrew_name": "דניאל", "hebrew_transliteration": "Daniel", "spanish_name": "Daniel"},
            "Ezra": {"section": "ketuvim", "order": 36, "chapters": 10, "hebrew_name": "עזרא", "hebrew_transliteration": "Ezra", "spanish_name": "Esdras"},
            "Nehemiah": {"section": "ketuvim", "order": 37, "chapters": 13, "hebrew_name": "נחמיה", "hebrew_transliteration": "Nejemiyah", "spanish_name": "Nehemías"},
            "Chronicles1": {"section": "ketuvim", "order": 38, "chapters": 29, "hebrew_name": "דברי הימים א", "hebrew_transliteration": "Divrei Hayamim Alef", "spanish_name": "Crónicas 1"},
            "Chronicles2": {"section": "ketuvim", "order": 39, "chapters": 36, "hebrew_name": "דברי הימים ב", "hebrew_transliteration": "Divrei Hayamim Bet", "spanish_name": "Crónicas 2"},
            # Besorah
            "Matthew": {"section": "besorah", "order": 40, "chapters": 28, "hebrew_name": "מתתיהו", "hebrew_transliteration": "Mattityahu", "spanish_name": "Mateo"},
            "Mark": {"section": "besorah", "order": 41, "chapters": 16, "hebrew_name": "מרקוס", "hebrew_transliteration": "Markos", "spanish_name": "Marcos"},
            "Luke": {"section": "besorah", "order": 42, "chapters": 24, "hebrew_name": "לוקאס", "hebrew_transliteration": "Lukas", "spanish_name": "Lucas"},
            "John": {"section": "besorah", "order": 43, "chapters": 21, "hebrew_name": "יוחנן", "hebrew_transliteration": "Yojanan", "spanish_name": "Juan"},
            "Acts": {"section": "besorah", "order": 44, "chapters": 28, "hebrew_name": "מעשי השליחים", "hebrew_transliteration": "Maasei Hashlichim", "spanish_name": "Hechos"},
            "Romans": {"section": "besorah", "order": 45, "chapters": 16, "hebrew_name": "רומים", "hebrew_transliteration": "Romaim", "spanish_name": "Romanos"},
            "Corinthians1": {"section": "besorah", "order": 46, "chapters": 16, "hebrew_name": "קורינתים א", "hebrew_transliteration": "Korintiym Alef", "spanish_name": "Corintios 1"},
            "Corinthians2": {"section": "besorah", "order": 47, "chapters": 13, "hebrew_name": "קורינתים ב", "hebrew_transliteration": "Korintiym Bet", "spanish_name": "Corintios 2"},
            "Galatians": {"section": "besorah", "order": 48, "chapters": 6, "hebrew_name": "גלטים", "hebrew_transliteration": "Galatiym", "spanish_name": "Gálatas"},
            "Ephesians": {"section": "besorah", "order": 49, "chapters": 6, "hebrew_name": "אפסים", "hebrew_transliteration": "Efesiym", "spanish_name": "Efesios"},
            "Philippians": {"section": "besorah", "order": 50, "chapters": 4, "hebrew_name": "פיליפים", "hebrew_transliteration": "Filipiyim", "spanish_name": "Filipenses"},
            "Colossians": {"section": "besorah", "order": 51, "chapters": 4, "hebrew_name": "קלוסים", "hebrew_transliteration": "Kolosiym", "spanish_name": "Colosenses"},
            "Thessalonians1": {"section": "besorah", "order": 52, "chapters": 5, "hebrew_name": "תסלוניקים א", "hebrew_transliteration": "Tesalonikim Alef", "spanish_name": "Tesalonicenses 1"},
            "Thessalonians2": {"section": "besorah", "order": 53, "chapters": 3, "hebrew_name": "תסלוניקים ב", "hebrew_transliteration": "Tesalonikim Bet", "spanish_name": "Tesalonicenses 2"},
            "Timothy1": {"section": "besorah", "order": 54, "chapters": 6, "hebrew_name": "טימותי א", "hebrew_transliteration": "Timotiyos Alef", "spanish_name": "Timoteo 1"},
            "Timothy2": {"section": "besorah", "order": 55, "chapters": 4, "hebrew_name": "טימותי ב", "hebrew_transliteration": "Timotiyos Bet", "spanish_name": "Timoteo 2"},
            "Titus": {"section": "besorah", "order": 56, "chapters": 3, "hebrew_name": "טיטוס", "hebrew_transliteration": "Titos", "spanish_name": "Tito"},
            "Philemon": {"section": "besorah", "order": 57, "chapters": 1, "hebrew_name": "פילימון", "hebrew_transliteration": "Pilimon", "spanish_name": "Filemón"},
            "Hebrews": {"section": "besorah", "order": 58, "chapters": 13, "hebrew_name": "עברים", "hebrew_transliteration": "Ivrym", "spanish_name": "Hebreos"},
            "James": {"section": "besorah", "order": 59, "chapters": 5, "hebrew_name": "יעקב", "hebrew_transliteration": "Yaakov", "spanish_name": "Santiago"},
            "Peter1": {"section": "besorah", "order": 60, "chapters": 5, "hebrew_name": "כפא א", "hebrew_transliteration": "kefa Alef", "spanish_name": "Pedro 1"},
            "Peter2": {"section": "besorah", "order": 61, "chapters": 3, "hebrew_name": "כפא ב", "hebrew_transliteration": "Kefa Bet", "spanish_name": "Pedro 2"},
            "John1": {"section": "besorah", "order": 62, "chapters": 5, "hebrew_name": "יוחנן א", "hebrew_transliteration": "Yojanan Alef", "spanish_name": "Juan 1"},
            "John2": {"section": "besorah", "order": 63, "chapters": 1, "hebrew_name": "יוחנן ב", "hebrew_transliteration": "Yojanan Bet", "spanish_name": "Juan 2"},
            "John3": {"section": "besorah", "order": 64, "chapters": 1, "hebrew_name": "יוחנן ג", "hebrew_transliteration": "Yojanan Gimel", "spanish_name": "Juan 3"},
            "Jude": {"section": "besorah", "order": 65, "chapters": 1, "hebrew_name": "יהודה", "hebrew_transliteration": "Yehudah", "spanish_name": "Judas"},
            "Revelation": {"section": "besorah", "order": 66, "chapters": 22, "hebrew_name": "התגלות יוחנן", "hebrew_transliteration": "Sodot", "spanish_name": "Apocalipsis"}
        }

    def normalize_book_name(self, book_name: str, source: str = "auto") -> Optional[str]:
        """Normalize any book name to canonical English"""
        book_name = book_name.lower().strip()

        # Try different mapping sources based on the source parameter
        if source == "oe" or (source == "auto" and book_name in self.oe_to_english):
            return self.oe_to_english.get(book_name)
        elif source == "delitzsch" or (source == "auto" and book_name in self.delitzsch_to_english):
            return self.delitzsch_to_english.get(book_name)
        elif source == "tth" or (source == "auto" and book_name in self.tth_to_english):
            return self.tth_to_english.get(book_name)
        elif source == "ts2009" or (source == "auto" and book_name in self.ts2009_to_english):
            return self.ts2009_to_english.get(book_name)
        elif source == "dss" or (source == "auto" and book_name in self.dss_to_english):
            return self.dss_to_english.get(book_name)

        # If auto-detection fails, try all mappings
        if source == "auto":
            for mapping in [self.oe_to_english, self.delitzsch_to_english,
                            self.tth_to_english, self.ts2009_to_english, self.dss_to_english]:
                if book_name in mapping:
                    return mapping[book_name]

        return None

    def to_english(self, book_name: str, source: str = "auto") -> Optional[str]:
        """Alias for normalize_book_name for backward compatibility"""
        return self.normalize_book_name(book_name, source)

    def to_dss_key(self, book_name: str) -> Optional[str]:
        """Convert a book name to the DSS book key used in data/dss/books."""
        book_en = self.normalize_book_name(book_name, source="auto")
        if not book_en:
            return None
        return self.english_to_dss.get(book_en)

    def get_book_metadata(self, book_name: str) -> Optional[Dict[str, any]]:
        """Get metadata for a canonical English book name"""
        return self.book_metadata.get(book_name)

    def get_all_books(self, section: Optional[str] = None) -> list[str]:
        """Get all canonical book names, optionally filtered by section"""
        books = list(self.book_metadata.keys())
        if section:
            books = [b for b in books if self.book_metadata[b]
                     ["section"] == section]
        return sorted(books)

    def get_book_section(self, book_name: str) -> Optional[str]:
        """Get the section (torah, neviim, ketuvim, besorah) for a book"""
        metadata = self.get_book_metadata(book_name)
        return metadata["section"] if metadata else None

    def get_book_chapter_count(self, book_name: str) -> Optional[int]:
        """Get the number of chapters for a book"""
        metadata = self.get_book_metadata(book_name)
        return metadata["chapters"] if metadata else None


# Global instance
book_mapper = BookNameMapper()
