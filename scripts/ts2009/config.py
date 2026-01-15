"""
TS2009 Processor Configuration

Contains all configuration constants, book mappings, and processing settings
for the TS2009 Bible processor.
"""

from typing import Dict, Any


import os
from pathlib import Path

# Get the project root directory (parent of scripts directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Database settings
DEFAULT_DB_PATH = PROJECT_ROOT / 'data/ts2009/raw/TS2009_Sent to DABAR.bbli'
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / 'data/ts2009'
DEFAULT_TEMP_DIR = PROJECT_ROOT / 'data/ts2009/temp'

# Processing settings
PROCESSOR_VERSION = "2.0.0"


# Book mappings - TS2009 book numbers to metadata
BOOKS_MAPPING: Dict[int, Dict[str, Any]] = {
    # TORAH (1-5)
    1: {
        'name_anglicized': 'bereshit',
        'name_hebrew': 'בראשית',
        'name_english': 'Genesis',
        'name_spanish': 'Génesis',
        'section': 'torah',
        'expected_chapters': 50
    },
    2: {
        'name_anglicized': 'shemoth',
        'name_hebrew': 'שמות',
        'name_english': 'Exodus',
        'name_spanish': 'Éxodo',
        'section': 'torah',
        'expected_chapters': 40
    },
    3: {
        'name_anglicized': 'wayyiqra',
        'name_hebrew': 'ויקרא',
        'name_english': 'Leviticus',
        'name_spanish': 'Levítico',
        'section': 'torah',
        'expected_chapters': 27
    },
    4: {
        'name_anglicized': 'bemidbar',
        'name_hebrew': 'במדבר',
        'name_english': 'Numbers',
        'name_spanish': 'Números',
        'section': 'torah',
        'expected_chapters': 36
    },
    5: {
        'name_anglicized': 'debarim',
        'name_hebrew': 'דברים',
        'name_english': 'Deuteronomy',
        'name_spanish': 'Deuteronomio',
        'section': 'torah',
        'expected_chapters': 34
    },

    # NEVI'IM - Former Prophets (6-11)
    6: {
        'name_anglicized': 'yehoshua',
        'name_hebrew': 'יהושע',
        'name_english': 'Joshua',
        'name_spanish': 'Josué',
        'section': 'neviim',
        'expected_chapters': 24
    },
    7: {
        'name_anglicized': 'shophetim',
        'name_hebrew': 'שופטים',
        'name_english': 'Judges',
        'name_spanish': 'Jueces',
        'section': 'neviim',
        'expected_chapters': 21
    },
    8: {
        'name_anglicized': 'ruth',
        'name_hebrew': 'רות',
        'name_english': 'Ruth',
        'name_spanish': 'Rut',
        'section': 'ketuvim',
        'expected_chapters': 4
    },
    9: {
        'name_anglicized': 'samuel_1',
        'name_hebrew': 'שמואל א',
        'name_english': 'samuel_1',
        'name_spanish': '1 Samuel',
        'section': 'neviim',
        'expected_chapters': 31
    },
    10: {
        'name_anglicized': 'samuel_2',
        'name_hebrew': 'שמואל ב',
        'name_english': 'samuel_2',
        'name_spanish': '2 Samuel',
        'section': 'neviim',
        'expected_chapters': 24
    },
    11: {
        'name_anglicized': 'kings_1',
        'name_hebrew': 'מלכים א',
        'name_english': 'kings_1',
        'name_spanish': '1 Reyes',
        'section': 'neviim',
        'expected_chapters': 22
    },
    12: {
        'name_anglicized': 'kings_2',
        'name_hebrew': 'מלכים ב',
        'name_english': 'kings_2',
        'name_spanish': '2 Reyes',
        'section': 'neviim',
        'expected_chapters': 25
    },
    13: {
        'name_anglicized': 'chronicles_1',
        'name_hebrew': 'דברי הימים א',
        'name_english': 'chronicles_1',
        'name_spanish': '1 Crónicas',
        'section': 'ketuvim',
        'expected_chapters': 29
    },
    14: {
        'name_anglicized': 'chronicles_2',
        'name_hebrew': 'דברי הימים ב',
        'name_english': 'chronicles_2',
        'name_spanish': '2 Crónicas',
        'section': 'ketuvim',
        'expected_chapters': 36
    },
    15: {
        'name_anglicized': 'ezra',
        'name_hebrew': 'עזרא',
        'name_english': 'Ezra',
        'name_spanish': 'Esdras',
        'section': 'ketuvim',
        'expected_chapters': 10
    },
    16: {
        'name_anglicized': 'nehemyah',
        'name_hebrew': 'נחמיה',
        'name_english': 'Nehemiah',
        'name_spanish': 'Nehemías',
        'section': 'ketuvim',
        'expected_chapters': 13
    },
    17: {
        'name_anglicized': 'ester',
        'name_hebrew': 'אסתר',
        'name_english': 'Esther',
        'name_spanish': 'Ester',
        'section': 'ketuvim',
        'expected_chapters': 10
    },
    18: {
        'name_anglicized': 'iyob',
        'name_hebrew': 'איוב',
        'name_english': 'Job',
        'name_spanish': 'Job',
        'section': 'ketuvim',
        'expected_chapters': 42
    },
    19: {
        'name_anglicized': 'tehillim',
        'name_hebrew': 'תהלים',
        'name_english': 'Psalms',
        'name_spanish': 'Salmos',
        'section': 'ketuvim',
        'expected_chapters': 150
    },
    20: {
        'name_anglicized': 'mishlei',
        'name_hebrew': 'משלי',
        'name_english': 'Proverbs',
        'name_spanish': 'Proverbios',
        'section': 'ketuvim',
        'expected_chapters': 31
    },
    21: {
        'name_anglicized': 'qoheleth',
        'name_hebrew': 'קהלת',
        'name_english': 'Ecclesiastes',
        'name_spanish': 'Eclesiastés',
        'section': 'ketuvim',
        'expected_chapters': 12
    },
    22: {
        'name_anglicized': 'shir_hashirim',
        'name_hebrew': 'שיר השירים',
        'name_english': 'Song of Songs',
        'name_spanish': 'Cantares',
        'section': 'ketuvim',
        'expected_chapters': 8
    },

    # NEVI'IM - Latter Prophets (23-27)
    23: {
        'name_anglicized': 'yeshayahu',
        'name_hebrew': 'ישעיהו',
        'name_english': 'Isaiah',
        'name_spanish': 'Isaías',
        'section': 'neviim',
        'expected_chapters': 66
    },
    24: {
        'name_anglicized': 'yirmeyahu',
        'name_hebrew': 'ירמיהו',
        'name_english': 'Jeremiah',
        'name_spanish': 'Jeremías',
        'section': 'neviim',
        'expected_chapters': 52
    },
    25: {
        'name_anglicized': 'ekah',
        'name_hebrew': 'איכה',
        'name_english': 'Lamentations',
        'name_spanish': 'Lamentaciones',
        'section': 'ketuvim',
        'expected_chapters': 5
    },
    26: {
        'name_anglicized': 'yehezqel',
        'name_hebrew': 'יחזקאל',
        'name_english': 'Ezekiel',
        'name_spanish': 'Ezequiel',
        'section': 'neviim',
        'expected_chapters': 48
    },
    27: {
        'name_anglicized': 'daniel',
        'name_hebrew': 'דניאל',
        'name_english': 'Daniel',
        'name_spanish': 'Daniel',
        'section': 'neviim',
        'expected_chapters': 12
    },

    # NEVI'IM - The Twelve (28-39)
    28: {
        'name_anglicized': 'hosea',
        'name_hebrew': 'הושע',
        'name_english': 'Hosea',
        'name_spanish': 'Oseas',
        'section': 'neviim',
        'expected_chapters': 14
    },
    29: {
        'name_anglicized': 'yoel',
        'name_hebrew': 'יואל',
        'name_english': 'Joel',
        'name_spanish': 'Joel',
        'section': 'neviim',
        'expected_chapters': 3
    },
    30: {
        'name_anglicized': 'amos',
        'name_hebrew': 'עמוס',
        'name_english': 'Amos',
        'name_spanish': 'Amós',
        'section': 'neviim',
        'expected_chapters': 9
    },
    31: {
        'name_anglicized': 'obadyah',
        'name_hebrew': 'עובדיה',
        'name_english': 'Obadiah',
        'name_spanish': 'Abdías',
        'section': 'neviim',
        'expected_chapters': 1
    },
    32: {
        'name_anglicized': 'yonah',
        'name_hebrew': 'יונה',
        'name_english': 'Jonah',
        'name_spanish': 'Jonás',
        'section': 'neviim',
        'expected_chapters': 4
    },
    33: {
        'name_anglicized': 'micah',
        'name_hebrew': 'מיכה',
        'name_english': 'Micah',
        'name_spanish': 'Miqueas',
        'section': 'neviim',
        'expected_chapters': 7
    },
    34: {
        'name_anglicized': 'nahum',
        'name_hebrew': 'נחום',
        'name_english': 'Nahum',
        'name_spanish': 'Nahúm',
        'section': 'neviim',
        'expected_chapters': 3
    },
    35: {
        'name_anglicized': 'habakkuk',
        'name_hebrew': 'חבקוק',
        'name_english': 'Habakkuk',
        'name_spanish': 'Habacuc',
        'section': 'neviim',
        'expected_chapters': 3
    },
    36: {
        'name_anglicized': 'zephaniah',
        'name_hebrew': 'צפניה',
        'name_english': 'Zephaniah',
        'name_spanish': 'Sofonías',
        'section': 'neviim',
        'expected_chapters': 3
    },
    37: {
        'name_anglicized': 'haggai',
        'name_hebrew': 'חגי',
        'name_english': 'Haggai',
        'name_spanish': 'Hageo',
        'section': 'neviim',
        'expected_chapters': 2
    },
    38: {
        'name_anglicized': 'zechariah',
        'name_hebrew': 'זכריה',
        'name_english': 'Zechariah',
        'name_spanish': 'Zacarías',
        'section': 'neviim',
        'expected_chapters': 14
    },
    39: {
        'name_anglicized': 'malachi',
        'name_hebrew': 'מלאכי',
        'name_english': 'Malachi',
        'name_spanish': 'Malaquías',
        'section': 'neviim',
        'expected_chapters': 4
    },

    # BESORAH (40-66)
    40: {
        'name_anglicized': 'mattithyahu',
        'name_hebrew': 'מתתיהו',
        'name_english': 'Matthew',
        'name_spanish': 'Mateo',
        'section': 'besorah',
        'expected_chapters': 28
    },
    41: {
        'name_anglicized': 'marqos',
        'name_hebrew': 'מרקוס',
        'name_english': 'Mark',
        'name_spanish': 'Marcos',
        'section': 'besorah',
        'expected_chapters': 16
    },
    42: {
        'name_anglicized': 'lugqas',
        'name_hebrew': 'לוקס',
        'name_english': 'Luke',
        'name_spanish': 'Lucas',
        'section': 'besorah',
        'expected_chapters': 24
    },
    43: {
        'name_anglicized': 'yohanan',
        'name_hebrew': 'יוחנן',
        'name_english': 'John',
        'name_spanish': 'Juan',
        'section': 'besorah',
        'expected_chapters': 21
    },
    44: {
        'name_anglicized': 'maasei',
        'name_hebrew': 'מעשי השליחים',
        'name_english': 'Acts',
        'name_spanish': 'Hechos',
        'section': 'besorah',
        'expected_chapters': 28
    },
    45: {
        'name_anglicized': 'romiyim',
        'name_hebrew': 'רומים',
        'name_english': 'Romans',
        'name_spanish': 'Romanos',
        'section': 'besorah',
        'expected_chapters': 16
    },
    46: {
        'name_anglicized': 'corinthians_1',
        'name_hebrew': 'קורינתיים א',
        'name_english': 'corinthians_1',
        'name_spanish': '1 Corintios',
        'section': 'besorah',
        'expected_chapters': 16
    },
    47: {
        'name_anglicized': 'corinthians_2',
        'name_hebrew': 'קורינתיים ב',
        'name_english': 'corinthians_2',
        'name_spanish': '2 Corintios',
        'section': 'besorah',
        'expected_chapters': 13
    },
    48: {
        'name_anglicized': 'galatiyim',
        'name_hebrew': 'גלטיים',
        'name_english': 'Galatians',
        'name_spanish': 'Gálatas',
        'section': 'besorah',
        'expected_chapters': 6
    },
    49: {
        'name_anglicized': 'ephsiyim',
        'name_hebrew': 'אפסיים',
        'name_english': 'Ephesians',
        'name_spanish': 'Efesios',
        'section': 'besorah',
        'expected_chapters': 6
    },
    50: {
        'name_anglicized': 'pilipiyim',
        'name_hebrew': 'פיליפיים',
        'name_english': 'Philippians',
        'name_spanish': 'Filipenses',
        'section': 'besorah',
        'expected_chapters': 4
    },
    51: {
        'name_anglicized': 'qolasim',
        'name_hebrew': 'קולסים',
        'name_english': 'Colossians',
        'name_spanish': 'Colosenses',
        'section': 'besorah',
        'expected_chapters': 4
    },
    52: {
        'name_anglicized': 'thessalonians_1',
        'name_hebrew': 'תסלוניקים א',
        'name_english': 'thessalonians_1',
        'name_spanish': '1 Tesalonicenses',
        'section': 'besorah',
        'expected_chapters': 5
    },
    53: {
        'name_anglicized': 'thessalonians_2',
        'name_hebrew': 'תסלוניקים ב',
        'name_english': 'thessalonians_2',
        'name_spanish': '2 Tesalonicenses',
        'section': 'besorah',
        'expected_chapters': 3
    },
    54: {
        'name_anglicized': 'timothy_1',
        'name_hebrew': 'טימותיוס א',
        'name_english': 'timothy_1',
        'name_spanish': '1 Timoteo',
        'section': 'besorah',
        'expected_chapters': 6
    },
    55: {
        'name_anglicized': 'timothy_2',
        'name_hebrew': 'טימותיוס ב',
        'name_english': 'timothy_2',
        'name_spanish': '2 Timoteo',
        'section': 'besorah',
        'expected_chapters': 4
    },
    56: {
        'name_anglicized': 'titos',
        'name_hebrew': 'טיטוס',
        'name_english': 'Titus',
        'name_spanish': 'Tito',
        'section': 'besorah',
        'expected_chapters': 3
    },
    57: {
        'name_anglicized': 'pileymon',
        'name_hebrew': 'פילמון',
        'name_english': 'Philemon',
        'name_spanish': 'Filemón',
        'section': 'besorah',
        'expected_chapters': 1
    },
    58: {
        'name_anglicized': 'ibrim',
        'name_hebrew': 'עברים',
        'name_english': 'Hebrews',
        'name_spanish': 'Hebreos',
        'section': 'besorah',
        'expected_chapters': 13
    },
    59: {
        'name_anglicized': 'yaaqob',
        'name_hebrew': 'יעקב',
        'name_english': 'James',
        'name_spanish': 'Santiago',
        'section': 'besorah',
        'expected_chapters': 5
    },
    60: {
        'name_anglicized': 'peter_1',
        'name_hebrew': 'כיפא א',
        'name_english': 'peter_1',
        'name_spanish': '1 Pedro',
        'section': 'besorah',
        'expected_chapters': 5
    },
    61: {
        'name_anglicized': 'peter_2',
        'name_hebrew': 'כיפא ב',
        'name_english': 'peter_2',
        'name_spanish': '2 Pedro',
        'section': 'besorah',
        'expected_chapters': 3
    },
    62: {
        'name_anglicized': 'john_1',
        'name_hebrew': 'יוחנן א',
        'name_english': 'john_1',
        'name_spanish': '1 Juan',
        'section': 'besorah',
        'expected_chapters': 5
    },
    63: {
        'name_anglicized': 'john_2',
        'name_hebrew': 'יוחנן ב',
        'name_english': 'john_2',
        'name_spanish': '2 Juan',
        'section': 'besorah',
        'expected_chapters': 1
    },
    64: {
        'name_anglicized': 'john_3',
        'name_hebrew': 'יוחנן ג',
        'name_english': 'john_3',
        'name_spanish': '3 Juan',
        'section': 'besorah',
        'expected_chapters': 1
    },
    65: {
        'name_anglicized': 'yehudah',
        'name_hebrew': 'יהודה',
        'name_english': 'Jude',
        'name_spanish': 'Judas',
        'section': 'besorah',
        'expected_chapters': 1
    },
    66: {
        'name_anglicized': 'hazon',
        'name_hebrew': 'חזון',
        'name_english': 'Revelation',
        'name_spanish': 'Apocalipsis',
        'section': 'besorah',
        'expected_chapters': 22
    },
}


# Section mappings
SECTIONS_MAPPING = {
    'torah': {
        'hebrew': 'תורה',
        'english': 'Torah',
        'spanish': 'Torá'
    },
    'neviim': {
        'hebrew': 'נביאים',
        'english': 'Prophets',
        'spanish': 'Profetas'
    },
    'ketuvim': {
        'hebrew': 'כתובים',
        'english': 'Writings',
        'spanish': 'Escritos'
    },
    'besorah': {
        'hebrew': 'בשורה',
        'english': 'Gospel/Good News',
        'spanish': 'Evangelio/Buena Noticia'
    }
}


# Common Hebrew terms for extraction (simplified for the streamlined version)
COMMON_HEBREW_TERMS = {
    'יהוה': 'Tetragrammaton - Name of Elohim',
    'אלהים': 'Elohim - Mighty One, God',
    'אל': 'El - God, mighty one',
    'יהושע': 'Yehoshua - Salvation of Yah',
    'משיח': 'Messiah - The Anointed One'
}
