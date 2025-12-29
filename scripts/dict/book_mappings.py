"""
Book mappings and metadata for Hebrew Scripture processing.

Contains mappings between different book naming conventions, metadata,
and relationships between books across different sources (ISR, TS2009, TTH).
"""

from typing import Dict, Optional


class BookMapper:
    """Handles book name mappings and metadata."""

    # Complete book name mapping
    BOOK_MAPPING = {
        'genesis': {
            'normalized': 'gen',
            'book_id': 'genesis',
            'es': 'Génesis',
            'en': 'Genesis',
            'ts2009': 'bereshit_genesis',
            'tth': 'bereshit'
        },
        'exodus': {
            'normalized': 'exod',
            'book_id': 'exodus',
            'es': 'Éxodo',
            'en': 'Exodus',
            'ts2009': 'shemoth_exodus',
            'tth': 'shemot'
        },
        'leviticus': {
            'normalized': 'lev',
            'book_id': 'leviticus',
            'es': 'Levítico',
            'en': 'Leviticus',
            'ts2009': 'wayyiqra_leviticus',
            'tth': 'vaikra'
        },
        'numbers': {
            'normalized': 'num',
            'book_id': 'numbers',
            'es': 'Números',
            'en': 'Numbers',
            'ts2009': 'bemidbar_numbers',
            'tth': 'bamidbar'
        },
        'deuteronomy': {
            'normalized': 'deut',
            'book_id': 'deuteronomy',
            'es': 'Deuteronomio',
            'en': 'Deuteronomy',
            'ts2009': 'debarim_deuteronomy',
            'tth': 'devarim'
        },
        'joshua': {
            'normalized': 'josh',
            'book_id': 'joshua',
            'es': 'Josué',
            'en': 'Joshua',
            'ts2009': 'yehoshua_joshua',
            'tth': 'iehosua'
        },
        'judges': {
            'normalized': 'judg',
            'book_id': 'judges',
            'es': 'Jueces',
            'en': 'Judges',
            'ts2009': 'shophetim_judges',
            'tth': 'shoftim'
        },
        'ruth': {
            'normalized': 'ruth',
            'book_id': 'ruth',
            'es': 'Rut',
            'en': 'Ruth',
            'ts2009': 'ruth',
            'tth': None  # No disponible en TTH
        },
        'isamuel': {
            'normalized': '1sam',
            'book_id': 'samuel_1',
            'es': '1 Samuel',
            'en': '1 Samuel',
            'ts2009': 'shemuel_aleph_1_samuel',
            'tth': 'shemuel_alef'
        },
        'iisamuel': {
            'normalized': '2sam',
            'book_id': 'samuel_2',
            'es': '2 Samuel',
            'en': '2 Samuel',
            'ts2009': 'shemuel_bet_2_samuel',
            'tth': 'shemuel_bet'
        },
        'ikings': {
            'normalized': '1kgs',
            'book_id': 'kings_1',
            'es': '1 Reyes',
            'en': '1 Kings',
            'ts2009': 'melakim_aleph_1_kings',
            'tth': 'melajim_alef'
        },
        'iikings': {
            'normalized': '2kgs',
            'book_id': 'kings_2',
            'es': '2 Reyes',
            'en': '2 Kings',
            'ts2009': 'melakim_bet_2_kings',
            'tth': 'melajim_bet'
        },
        'ichronicles': {
            'normalized': '1chr',
            'book_id': 'chronicles_1',
            'es': '1 Crónicas',
            'en': '1 Chronicles',
            'ts2009': 'dibre_hayamim_aleph_1_chronicles',
            'tth': None
        },
        'iichronicles': {
            'normalized': '2chr',
            'book_id': 'chronicles_2',
            'es': '2 Crónicas',
            'en': '2 Chronicles',
            'ts2009': 'dibre_hayamim_bet_2_chronicles',
            'tth': None
        },
        'ezra': {
            'normalized': 'ezra',
            'book_id': 'ezra',
            'es': 'Esdras',
            'en': 'Ezra',
            'ts2009': 'ezra',
            'tth': None
        },
        'nehemiah': {
            'normalized': 'neh',
            'book_id': 'nehemiah',
            'es': 'Nehemías',
            'en': 'Nehemiah',
            'ts2009': 'nehemyah_nehemiah',
            'tth': None
        },
        'esther': {
            'normalized': 'esth',
            'book_id': 'esther',
            'es': 'Ester',
            'en': 'Esther',
            'ts2009': 'ester_esther',
            'tth': None
        },
        'job': {
            'normalized': 'job',
            'book_id': 'job',
            'es': 'Job',
            'en': 'Job',
            'ts2009': 'iyob_job',
            'tth': None
        },
        'psalms': {
            'normalized': 'ps',
            'book_id': 'psalms',
            'es': 'Salmos',
            'en': 'Psalms',
            'ts2009': 'tehillim_psalms',
            'tth': 'tehilim'
        },
        'proverbs': {
            'normalized': 'prov',
            'book_id': 'proverbs',
            'es': 'Proverbios',
            'en': 'Proverbs',
            'ts2009': 'mishle_proverbs',
            'tth': 'mishlei'
        },
        'ecclesiastes': {
            'normalized': 'eccl',
            'book_id': 'ecclesiastes',
            'es': 'Eclesiastés',
            'en': 'Ecclesiastes',
            'ts2009': 'qoheleth_ecclesiastes',
            'tth': None
        },
        'songofsolomon': {
            'normalized': 'song',
            'book_id': 'songofsolomon',
            'es': 'Cantares',
            'en': 'Song of Solomon',
            'ts2009': 'shir_hashirim_song_of_songs',
            'tth': None
        },
        'isaiah': {
            'normalized': 'isa',
            'book_id': 'isaiah',
            'es': 'Isaías',
            'en': 'Isaiah',
            'ts2009': 'yeshayahu_isaiah',
            'tth': 'ieshaiahu'
        },
        'jeremiah': {
            'normalized': 'jer',
            'book_id': 'jeremiah',
            'es': 'Jeremías',
            'en': 'Jeremiah',
            'ts2009': 'yirmeyahu_jeremiah',
            'tth': 'irmeiahu'
        },
        'lamentations': {
            'normalized': 'lam',
            'book_id': 'lamentations',
            'es': 'Lamentaciones',
            'en': 'Lamentations',
            'ts2009': 'ekah_lamentations',
            'tth': None
        },
        'ezekiel': {
            'normalized': 'ezek',
            'book_id': 'ezekiel',
            'es': 'Ezequiel',
            'en': 'Ezekiel',
            'ts2009': 'yehezqel_ezekiel',
            'tth': 'iejezkel'
        },
        'daniel': {
            'normalized': 'dan',
            'book_id': 'daniel',
            'es': 'Daniel',
            'en': 'Daniel',
            'ts2009': 'daniel_daniel',
            'tth': None
        },
        'hosea': {
            'normalized': 'hos',
            'book_id': 'hosea',
            'es': 'Oseas',
            'en': 'Hosea',
            'ts2009': 'hoshea_hosea',
            'tth': 'hoshea'
        },
        'joel': {
            'normalized': 'joel',
            'book_id': 'joel',
            'es': 'Joel',
            'en': 'Joel',
            'ts2009': 'yoel_joel',
            'tth': 'ioel'
        },
        'amos': {
            'normalized': 'amos',
            'book_id': 'amos',
            'es': 'Amós',
            'en': 'Amos',
            'ts2009': 'amos',
            'tth': 'amos'
        },
        'obadiah': {
            'normalized': 'obad',
            'book_id': 'obadiah',
            'es': 'Abdías',
            'en': 'Obadiah',
            'ts2009': 'obadyah_obadiah',
            'tth': None
        },
        'jonah': {
            'normalized': 'jonah',
            'book_id': 'jonah',
            'es': 'Jonás',
            'en': 'Jonah',
            'ts2009': 'yonah_jonah',
            'tth': 'ionah'
        },
        'micah': {
            'normalized': 'mic',
            'book_id': 'micah',
            'es': 'Miqueas',
            'en': 'Micah',
            'ts2009': 'mikah_micah',
            'tth': 'micah'
        },
        'nahum': {
            'normalized': 'nah',
            'book_id': 'nahum',
            'es': 'Nahúm',
            'en': 'Nahum',
            'ts2009': 'nahum_nahum',
            'tth': 'najum'
        },
        'habakkuk': {
            'normalized': 'hab',
            'book_id': 'habakkuk',
            'es': 'Habacuc',
            'en': 'Habakkuk',
            'ts2009': 'habaqqugq_habakkuk',
            'tth': 'jabakuk'
        },
        'zephaniah': {
            'normalized': 'zeph',
            'book_id': 'zephaniah',
            'es': 'Sofonías',
            'en': 'Zephaniah',
            'ts2009': 'tsephanyah_zephaniah',
            'tth': 'tzefaniah'
        },
        'haggai': {
            'normalized': 'hag',
            'book_id': 'haggai',
            'es': 'Hageo',
            'en': 'Haggai',
            'ts2009': 'haggai_haggai',
            'tth': 'jagai'
        },
        'zechariah': {
            'normalized': 'zech',
            'book_id': 'zechariah',
            'es': 'Zacarías',
            'en': 'Zechariah',
            'ts2009': 'zekaryah_zechariah',
            'tth': 'zejariah'
        },
        'malachi': {
            'normalized': 'mal',
            'book_id': 'malachi',
            'es': 'Malaquías',
            'en': 'Malachi',
            'ts2009': 'malaki_malachi',
            'tth': 'malaji'
        }
    }

    # Mapping of book names to morphus XML files
    MORPHUS_BOOK_MAP = {
        'genesis': 'Gen.xml',
        'exodus': 'Exod.xml',
        'leviticus': 'Lev.xml',
        'numbers': 'Num.xml',
        'deuteronomy': 'Deut.xml',
        'joshua': 'Josh.xml',
        'judges': 'Judg.xml',
        'ruth': 'Ruth.xml',
        'isamuel': '1Sam.xml',
        'iisamuel': '2Sam.xml',
        'ikings': '1Kgs.xml',
        'iikings': '2Kgs.xml',
        'ichronicles': '1Chr.xml',
        'iichronicles': '2Chr.xml',
        'ezra': 'Ezra.xml',
        'nehemiah': 'Neh.xml',
        'esther': 'Esth.xml',
        'job': 'Job.xml',
        'psalms': 'Ps.xml',
        'proverbs': 'Prov.xml',
        'ecclesiastes': 'Eccl.xml',
        'songofsolomon': 'Song.xml',
        'isaiah': 'Isa.xml',
        'jeremiah': 'Jer.xml',
        'lamentations': 'Lam.xml',
        'ezekiel': 'Ezek.xml',
        'daniel': 'Dan.xml',
        'hosea': 'Hos.xml',
        'joel': 'Joel.xml',
        'amos': 'Amos.xml',
        'obadiah': 'Obad.xml',
        'jonah': 'Jonah.xml',
        'micah': 'Mic.xml',
        'nahum': 'Nah.xml',
        'habakkuk': 'Hab.xml',
        'zephaniah': 'Zeph.xml',
        'haggai': 'Hag.xml',
        'zechariah': 'Zech.xml',
        'malachi': 'Mal.xml'
    }

    @classmethod
    def get_book_info(cls, book_key: str) -> Optional[Dict]:
        """Get book information by key."""
        return cls.BOOK_MAPPING.get(book_key.lower())

    @classmethod
    def get_book_id(cls, book_info: Dict) -> str:
        """Get the book_id from book_info."""
        if 'book_id' in book_info:
            return book_info['book_id']
        # Generate from English name
        en_name = book_info.get('en', '')
        book_id = en_name.lower().replace(' ', '_')
        return book_id

    @classmethod
    def get_hebrew_translit(cls, book_info: Dict) -> str:
        """Get Hebrew transliteration prioritizing TTH, then TS2009."""
        # If TTH exists, use its capitalized name
        if book_info.get('tth'):
            tth_name = book_info['tth']
            # Handle compound names like "shemuel_alef" -> "Shemuel Alef"
            if '_' in tth_name:
                parts = tth_name.split('_')
                return ' '.join(part.capitalize() for part in parts)
            return tth_name.capitalize()

        # If TS2009 exists, extract first part before underscore
        if book_info.get('ts2009'):
            ts2009_name = book_info['ts2009']
            parts = ts2009_name.split('_')
            if parts:
                translit = parts[0]
                return translit.capitalize()

        # Fallback: capitalized English name
        return book_info.get('en', '').capitalize()

    @classmethod
    def get_all_book_keys(cls) -> list:
        """Get all available book keys."""
        return list(cls.BOOK_MAPPING.keys())
