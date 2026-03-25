"""
Configuration for BES (Biblia en Español Sencillo) processing
Maps USFX 3-letter book codes to canonical English names and provides book metadata
"""

from typing import Dict, Any

# USFX 3-letter book codes to canonical English names
# Based on standard USFX format used by ebible.org
USFX_TO_ENGLISH = {
    # Torah (Pentateuch)
    "GEN": "Genesis",
    "EXO": "Exodus",
    "LEV": "Leviticus",
    "NUM": "Numbers",
    "DEU": "Deuteronomy",

    # Neviim (Former Prophets)
    "JOS": "Joshua",
    "JDG": "Judges",
    "1SA": "Samuel1",
    "2SA": "Samuel2",
    "1KI": "Kings1",
    "2KI": "Kings2",

    # Neviim (Latter Prophets)
    "ISA": "Isaiah",
    "JER": "Jeremiah",
    "EZK": "Ezekiel",  # USFX uses EZK

    # Neviim (The Twelve)
    "HOS": "Hosea",
    "JOL": "Joel",
    "AMO": "Amos",
    "OBA": "Obadiah",
    "JON": "Jonah",
    "MIC": "Micah",
    "NAM": "Nahum",
    "HAB": "Habakkuk",
    "ZEP": "Zephaniah",
    "HAG": "Haggai",
    "ZEC": "Zechariah",
    "MAL": "Malachi",

    # Ketuvim (Writings)
    "PSA": "Psalms",
    "PRO": "Proverbs",
    "JOB": "Job",
    "SNG": "SongOfSolomon",
    "RUT": "Ruth",
    "LAM": "Lamentations",
    "ECC": "Ecclesiastes",
    "EST": "Esther",
    "DAN": "Daniel",
    "EZR": "Ezra",
    "NEH": "Nehemiah",
    "1CH": "Chronicles1",
    "2CH": "Chronicles2",

    # Besorah (New Testament)
    "MAT": "Matthew",
    "MRK": "Mark",
    "LUK": "Luke",
    "JHN": "John",
    "ACT": "Acts",
    "ROM": "Romans",
    "1CO": "Corinthians1",
    "2CO": "Corinthians2",
    "GAL": "Galatians",
    "EPH": "Ephesians",
    "PHP": "Philippians",
    "COL": "Colossians",
    "1TH": "Thessalonians1",
    "2TH": "Thessalonians2",
    "1TI": "Timothy1",
    "2TI": "Timothy2",
    "TIT": "Titus",
    "PHM": "Philemon",
    "HEB": "Hebrews",
    "JAS": "James",
    "1PE": "Peter1",
    "2PE": "Peter2",
    "1JN": "John1",
    "2JN": "John2",
    "3JN": "John3",
    "JUD": "Jude",
    "REV": "Revelation",
}

# Book metadata (mirrored from backend/app/data_loaders/book_mapping.py)
# Used for generating book_info in JSON output
BOOK_METADATA = {
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
    "Revelation": {"section": "besorah", "order": 66, "chapters": 22, "hebrew_name": "סודות", "hebrew_transliteration": "Sodot", "spanish_name": "Apocalipsis"}
}

# Reverse mapping for convenience
ENGLISH_TO_USFX = {v: k for k, v in USFX_TO_ENGLISH.items()}

def get_book_metadata(book_name: str) -> Dict[str, Any]:
    """Get metadata for a canonical English book name"""
    return BOOK_METADATA.get(book_name)

def get_usfx_code(book_name: str) -> str:
    """Get USFX 3-letter code for a canonical English book name"""
    return ENGLISH_TO_USFX.get(book_name)

def get_english_name(usfx_code: str) -> str:
    """Get canonical English name for a USFX 3-letter code"""
    return USFX_TO_ENGLISH.get(usfx_code)