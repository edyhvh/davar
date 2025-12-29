#!/usr/bin/env python3
"""
Hebrew Scripture Verse Builder

A professional, modular script for generating lightweight verse JSON files
from Hebrew Scripture data sources.

This script processes data from:
- ISR Hebrew text (oe/ directory)
- Morphological analysis (morphus/ XML files)
- Lexical data (lexicon/ JSON files)

Output: Lightweight verse JSON files in verses/ directory
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration class for paths and settings."""

    def __init__(self):
        # Base project directory
        self.PROJECT_ROOT = Path(__file__).parent.parent.parent

        # Data directories
        self.DATA_DIR = self.PROJECT_ROOT / 'data'
        self.DICT_DIR = self.DATA_DIR / 'dict'
        self.OE_DIR = self.DATA_DIR / 'oe'

        # Raw data sources
        self.RAW_DIR = self.DICT_DIR / 'raw'
        self.MORPHUS_DIR = self.RAW_DIR / 'morphus'

        # Processed data
        self.LEXICON_DIR = self.DICT_DIR / 'lexicon'
        self.LEXICON_DRAFT_DIR = self.LEXICON_DIR / 'draft'
        self.LEXICON_ROOTS_DIR = self.LEXICON_DIR / 'roots'

        # Translations
        self.TS2009_DIR = self.DATA_DIR / 'ts2009'
        self.TTH_DIR = self.DATA_DIR / 'tth' / 'draft'

        # Output
        self.VERSES_DIR = self.DICT_DIR / 'verses'

        # Create output directory if it doesn't exist
        self.VERSES_DIR.mkdir(exist_ok=True)


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
        '1samuel': {
            'normalized': '1sam',
            'book_id': '1samuel',
            'es': '1 Samuel',
            'en': '1 Samuel',
            'ts2009': 'shemuel_aleph_1_samuel',
            'tth': 'shemuel_alef'
        },
        '2samuel': {
            'normalized': '2sam',
            'book_id': '2samuel',
            'es': '2 Samuel',
            'en': '2 Samuel',
            'ts2009': 'shemuel_bet_2_samuel',
            'tth': 'shemuel_bet'
        },
        '1kings': {
            'normalized': '1kgs',
            'book_id': '1kings',
            'es': '1 Reyes',
            'en': '1 Kings',
            'ts2009': 'melakim_aleph_1_kings',
            'tth': 'melajim_alef'
        },
        '2kings': {
            'normalized': '2kgs',
            'book_id': '2kings',
            'es': '2 Reyes',
            'en': '2 Kings',
            'ts2009': 'melakim_bet_2_kings',
            'tth': 'melajim_bet'
        },
        '1chronicles': {
            'normalized': '1chr',
            'book_id': '1chronicles',
            'es': '1 Crónicas',
            'en': '1 Chronicles',
            'ts2009': 'dibre_hayamim_aleph_1_chronicles',
            'tth': None
        },
        '2chronicles': {
            'normalized': '2chr',
            'book_id': '2chronicles',
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
        '1samuel': '1Sam.xml',
        '2samuel': '2Sam.xml',
        '1kings': '1Kgs.xml',
        '2kings': '2Kgs.xml',
        '1chronicles': '1Chr.xml',
        '2chronicles': '2Chr.xml',
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


class StrongProcessor:
    """Handles Strong's number processing and validation."""

    # Mapping of prefix codes to Strong's numbers for prepositions with pronominal suffixes
    PREFIX_TO_STRONG = {
        'Hb': 'H900',   # בְּ (be) - in, with
        'b': 'H900',    # בְּ (be) - in, with
        'Hl': 'H3808',  # לְ (le) - to, for
        'l': 'H3808',   # לְ (le) - to, for
        'Hc': 'H3605',  # כְּ (ke) - as, like
        'c': 'H3605',   # כְּ (ke) - as, like
        'Hm': 'H4480',  # מִן (min) - from
        'm': 'H4480',   # מִן (min) - from
    }

    def __init__(self, config: Config):
        self.config = config

    def extract_strong_number(self, lemma: str) -> Optional[str]:
        """
        Extract the Strong's number from a lemma.

        Examples:
            H1254 → H1254
            Hb/H7225 → H7225 (extracts H7225, ignoring prefix)
            Hc/H1961 → H1961
            Hc/Hd/H776 → H776
            Hb → H900 (preposition בְּ with pronominal suffix)
        """
        if not lemma:
            return None

        # Check if it's just a prefix code (like "Hb", "Hl") without a number
        # This happens with prepositions that have pronominal suffixes
        if lemma in self.PREFIX_TO_STRONG:
            return self.PREFIX_TO_STRONG[lemma]

        # Remove common prefixes (Hb/, Hc/, Hd/) to get to the actual number
        lemma_clean = re.sub(r'[Hh][bcdlm]/', '', lemma)

        # Extract Strong's number (format H followed by digits)
        match = re.search(r'[Hh](\d+)', lemma_clean)
        if match:
            return f"H{match.group(1)}"

        # If no number found but it's a known prefix, return the mapped Strong's
        if lemma in self.PREFIX_TO_STRONG:
            return self.PREFIX_TO_STRONG[lemma]

        return None

    def normalize_sense(self, sense: Optional[str]) -> Optional[str]:
        """
        Normalize the sense from morphus to simple format (without decimals).

        Examples:
            "1.0" -> "1"
            "1.1.1" -> "1"
            "0" -> "0"
            "0.0" -> "0"
            None -> None
        """
        if not sense:
            return None
        # Take only the first number before the dot
        parts = sense.split('.')
        return parts[0] if parts else None

    def get_lexicon_available_senses(self, strong_number: str) -> set:
        """
        Get all available senses from the lexicon for a Strong's number.

        Args:
            strong_number: Strong's number (e.g., "H1254")

        Returns:
            Set of available senses in the lexicon, or empty set if not found
        """
        if not strong_number:
            return set()

        available_senses = set()

        # Try draft/ directory first
        draft_file = self.config.LEXICON_DRAFT_DIR / f"{strong_number}.json"
        if draft_file.exists():
            try:
                with open(draft_file, 'r', encoding='utf-8') as f:
                    lexicon_data = json.load(f)
                    definitions = lexicon_data.get('definitions', [])
                    for defn in definitions:
                        sense = defn.get('sense')
                        if sense:
                            available_senses.add(sense)
            except Exception:
                pass

        # Try roots/ directory
        if not available_senses:
            roots_file = self.config.LEXICON_ROOTS_DIR / f"{strong_number}.json"
            if roots_file.exists():
                try:
                    with open(roots_file, 'r', encoding='utf-8') as f:
                        lexicon_data = json.load(f)
                        definitions = lexicon_data.get('definitions', [])
                        for defn in definitions:
                            sense = defn.get('sense')
                            if sense:
                                available_senses.add(sense)
                except Exception:
                    pass

        return available_senses

    def get_lexicon_sense(self, strong_number: str) -> Optional[str]:
        """
        Get the first available sense from the lexicon for a Strong's number.

        Args:
            strong_number: Strong's number (e.g., "H1254")

        Returns:
            First sense found in lexicon, or None if not found
        """
        if not strong_number:
            return None

        # Try draft/ directory first
        draft_file = self.config.LEXICON_DRAFT_DIR / f"{strong_number}.json"
        if draft_file.exists():
            try:
                with open(draft_file, 'r', encoding='utf-8') as f:
                    lexicon_data = json.load(f)
                    definitions = lexicon_data.get('definitions', [])
                    if definitions:
                        # Get the first sense from the first definition
                        first_sense = definitions[0].get('sense')
                        if first_sense:
                            return first_sense
            except Exception:
                pass

        # Try roots/ directory
        roots_file = self.config.LEXICON_ROOTS_DIR / f"{strong_number}.json"
        if roots_file.exists():
            try:
                with open(roots_file, 'r', encoding='utf-8') as f:
                    lexicon_data = json.load(f)
                    definitions = lexicon_data.get('definitions', [])
                    if definitions:
                        # Get the first sense from the first definition
                        first_sense = definitions[0].get('sense')
                        if first_sense:
                            return first_sense
            except Exception:
                pass

        return None

    def validate_sense(self, strong_number: str, sense: Optional[str]) -> Optional[str]:
        """
        Validate that a sense exists in the lexicon or has sub-senses.

        If morphus says "1" and lexicon has "1a", "1b", etc., then "1" is valid (parent category).
        Only returns None if the sense doesn't exist AND has no sub-senses.

        Args:
            strong_number: Strong's number (e.g., "H430")
            sense: Sense to validate (e.g., "1")

        Returns:
            Validated sense if it exists in lexicon or has sub-senses, None otherwise
        """
        if not sense or not strong_number:
            return None

        available_senses = self.get_lexicon_available_senses(strong_number)

        # If sense exists exactly in lexicon, return it
        if sense in available_senses:
            return sense

        # If sense doesn't exist, check if there are sub-senses
        # (e.g., sense="1" but lexicon has "1a", "1b")
        # If there are sub-senses, the parent sense "1" is valid
        has_sub_senses = any(s.startswith(sense) and len(s) > len(sense) for s in available_senses)

        if has_sub_senses:
            # The sense is a parent category (e.g., "1" is parent of "1a", "1b")
            return sense

        # Sense doesn't exist and no sub-senses found - invalid
        return None


class MorphusLoader:
    """Handles loading and processing of morphus XML data."""

    def __init__(self, config: Config, strong_processor: StrongProcessor):
        self.config = config
        self.strong_processor = strong_processor

    def load_morphus_senses(self, book_key: str) -> Optional[Dict[str, Dict[str, str]]]:
        """
        Load BDB senses from the morphus XML file.

        Returns:
            Dict with structure: {verse_ref: {position: sense}}
            Example: {"genesis.1.1": {"1": "1", "2": None, ...}}
            Senses are normalized to simple format (without decimals)
        """
        morphus_file = BookMapper.MORPHUS_BOOK_MAP.get(book_key)
        if not morphus_file:
            return None

        xml_path = self.config.MORPHUS_DIR / morphus_file
        if not xml_path.exists():
            return None

        try:
            import xml.etree.ElementTree as ET

            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Namespace
            ns = {'osis': 'http://www.bibletechnologies.net/2003/OSIS/namespace'}

            senses = {}

            # Get book name (full English book_id)
            book_info = BookMapper.get_book_info(book_key)
            if not book_info:
                return None
            book_id = BookMapper.get_book_id(book_info)

            # Iterate over all verses
            for verse in root.findall('.//osis:verse', ns):
                verse_id = verse.get('osisID', '')
                # Extract chapter and verse (e.g., "Gen.1.1" -> chapter=1, verse=1)
                parts = verse_id.split('.')
                if len(parts) >= 3:
                    chapter = parts[1]
                    verse_num = parts[2]
                    verse_ref = f"{book_id}.{chapter}.{verse_num}"

                    # Get all words in the verse
                    words = verse.findall('.//osis:w', ns)
                    verse_senses = {}

                    for pos, word in enumerate(words, start=1):
                        sense_raw = word.get('n')  # The 'n' attribute contains the BDB sense
                        # Normalize sense to simple format (without decimals)
                        sense = self.strong_processor.normalize_sense(sense_raw)
                        verse_senses[str(pos)] = sense

                    if verse_senses:
                        senses[verse_ref] = verse_senses

            return senses
        except Exception as e:
            logger.warning(f"Error loading morphus {xml_path}: {e}")
            return None


class VerseProcessor:
    """Handles verse processing and generation."""

    def __init__(self, config: Config, strong_processor: StrongProcessor, morphus_loader: MorphusLoader):
        self.config = config
        self.strong_processor = strong_processor
        self.morphus_loader = morphus_loader

    def process_word(self, word_data: Dict, position: int, sense: Optional[str] = None) -> Dict:
        """
        Process a word from the oe/ file and convert it to verse format

        Args:
            word_data: Word data from oe/
            position: Position of the word in the verse
            sense: BDB sense as string from morphus (already normalized without decimals)

        Returns:
            Dict with lightweight verse format
        """
        # Extract Strong's number
        strong = word_data.get('strong') or word_data.get('lemma', '')
        strong_number = self.strong_processor.extract_strong_number(strong)

        # Get Hebrew text of the word (without separators)
        hebrew_text = word_data.get('text', '').replace('/', '')

        # Validate sense against lexicon
        if sense and strong_number:
            sense = self.strong_processor.validate_sense(strong_number, sense)
            # If validation fails, use null - don't use lexicon fallback

        # If morphus didn't provide a sense, use null
        # The lexicon lists all possible senses, but we need morphus to tell us which one applies

        return {
            "position": position,
            "hebrew": hebrew_text,
            "strong_number": strong_number,
            "sense": sense  # String without decimals: "1", "0", etc., or None
        }

    def generate_verse(self, book_key: str, chapter: int, verse: int, verse_data: Dict, morphus_senses: Optional[Dict] = None) -> Dict:
        """
        Generate a lightweight verse from oe/ data

        Args:
            book_key: Book key in BOOK_MAPPING
            chapter: Chapter number
            verse: Verse number
            verse_data: Verse data from oe/
            morphus_senses: BDB senses dictionary from morphus

        Returns:
            Dict with lightweight verse format
        """
        book_info = BookMapper.get_book_info(book_key)
        if not book_info:
            raise ValueError(f"Book not found in BOOK_MAPPING: {book_key}")

        # Get book_id (full English name in lowercase)
        book_id = BookMapper.get_book_id(book_info)
        reference = f"{book_id}.{chapter}.{verse}"

        # Get sense for this verse from morphus
        verse_senses = None
        if morphus_senses:
            verse_senses = morphus_senses.get(reference)

        # Get complete Hebrew text of the verse
        hebrew_text = verse_data.get('hebrew', '').replace('/', ' ')
        # Clean multiple spaces
        hebrew_text = re.sub(r'\s+', ' ', hebrew_text).strip()

        # Process words
        words_data = verse_data.get('words', [])
        words = []
        for i, word_data in enumerate(words_data, start=1):
            # Get sense for this position (already normalized without decimals)
            sense = None
            if verse_senses:
                sense = verse_senses.get(str(i))

            word = self.process_word(word_data, i, sense)
            words.append(word)

        # Build verse
        verse_obj = {
            "reference": reference,
            "book_id": book_id,
            "chapter": chapter,
            "verse": verse,
            "hebrew_text": hebrew_text,
            "words": words
        }

        return verse_obj

    def process_oe_file(self, book_key: str, chapter_file: Path, morphus_senses: Optional[Dict] = None) -> List[Dict]:
        """
        Process a chapter file from oe/ and generate verses

        Args:
            book_key: Book key in BOOK_MAPPING
            chapter_file: Path to the chapter JSON file
            morphus_senses: Dict with BDB senses from morphus

        Returns:
            List of generated verses
        """
        with open(chapter_file, 'r', encoding='utf-8') as f:
            verses_data = json.load(f)

        # Extract chapter number from filename
        chapter_num = int(chapter_file.stem)

        verses = []
        for verse_data in verses_data:
            verse_num = verse_data.get('verse', 0)
            if verse_num == 0:
                continue

            try:
                verse_obj = self.generate_verse(book_key, chapter_num, verse_num, verse_data, morphus_senses)
                verses.append(verse_obj)
            except Exception as e:
                logger.warning(f"Error processing verse {chapter_num}:{verse_num}: {e}")

        return verses

    def process_book(self, book_key: str, book_dir: Path, chapter_num: Optional[int] = None) -> Tuple[int, int]:
        """
        Process chapters of a book

        Args:
            book_key: Book key in BOOK_MAPPING
            book_dir: Path to the book directory in oe/
            chapter_num: Optional chapter number to process only that chapter

        Returns:
            Tuple (processed verses, errors)
        """
        book_info = BookMapper.get_book_info(book_key)
        if not book_info:
            logger.error(f"Book not found: {book_key}")
            return 0, 0

        logger.info(f"📖 Processing: {book_info['en']} ({book_key})")
        if chapter_num:
            logger.info(f"  📄 Chapter: {chapter_num}")

        # Load BDB senses from morphus
        morphus_senses = self.morphus_loader.load_morphus_senses(book_key)
        if morphus_senses:
            logger.info("  ✅ BDB senses loaded from morphus")
        else:
            logger.warning("  ⚠️  No BDB senses found")

        total_verses = 0
        total_errors = 0

        # Get chapter files
        if chapter_num:
            # Process only the specified chapter
            chapter_file = book_dir / f"{chapter_num:02d}.json"
            if not chapter_file.exists():
                chapter_file = book_dir / f"{chapter_num}.json"
            chapter_files = [chapter_file] if chapter_file.exists() else []
        else:
            # Get all chapter files
            chapter_files = sorted(book_dir.glob("*.json"), key=lambda x: int(x.stem))

        # Create directory for the book if it doesn't exist
        book_id = BookMapper.get_book_id(book_info)
        output_book_dir = self.config.VERSES_DIR / book_id
        output_book_dir.mkdir(exist_ok=True)

        for chapter_file in chapter_files:
            if not chapter_file.exists():
                logger.warning(f"  ⚠️  Chapter file not found: {chapter_file}")
                continue

            try:
                verses = self.process_oe_file(book_key, chapter_file, morphus_senses)

                # Save each verse
                for verse in verses:
                    # Generate filename with full book_id
                    reference = f"{book_id}.{verse['chapter']}.{verse['verse']}"
                    output_file = output_book_dir / f"{reference}.json"

                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(verse, f, ensure_ascii=False, indent=2)

                    total_verses += 1

                if verses:
                    logger.info(f"  ✅ Chapter {chapter_file.stem}: {len(verses)} verses")

            except Exception as e:
                logger.error(f"  ❌ Error processing {chapter_file}: {e}")
                total_errors += 1

        return total_verses, total_errors


class VerseBuilder:
    """Main application class for building Hebrew Scripture verses."""

    def __init__(self):
        self.config = Config()
        self.strong_processor = StrongProcessor(self.config)
        self.morphus_loader = MorphusLoader(self.config, self.strong_processor)
        self.verse_processor = VerseProcessor(self.config, self.strong_processor, self.morphus_loader)

    def run(self, book_key: Optional[str] = None, chapter_num: Optional[int] = None) -> None:
        """
        Main execution method.

        Args:
            book_key: Specific book to process, or None for all books
            chapter_num: Specific chapter to process, or None for all chapters
        """
        logger.info("=" * 70)
        logger.info("HEBREW SCRIPTURE VERSE BUILDER")
        logger.info("=" * 70)
        logger.info(f"📁 Output directory: {self.config.VERSES_DIR}")
        logger.info(f"📁 OE directory: {self.config.OE_DIR}")
        logger.info(f"📁 Morphus directory: {self.config.MORPHUS_DIR}")
        logger.info("")

        if not self.config.OE_DIR.exists():
            logger.error(f"❌ OE directory not found: {self.config.OE_DIR}")
            return

        total_verses = 0
        total_errors = 0
        books_processed = 0

        if book_key:
            # Process only the specified book
            book_key = book_key.lower()
            if book_key not in BookMapper.BOOK_MAPPING:
                logger.error(f"❌ Book not found in mapping: {book_key}")
                logger.error(f"Available books: {', '.join(sorted(BookMapper.BOOK_MAPPING.keys()))}")
                return

            book_dir = self.config.OE_DIR / book_key
            if not book_dir.exists():
                logger.error(f"❌ Book directory not found: {book_dir}")
                return

            verses, errors = self.verse_processor.process_book(book_key, book_dir, chapter_num)
            total_verses += verses
            total_errors += errors
            books_processed = 1
        else:
            # Process each book available in oe/
            for book_dir in sorted(self.config.OE_DIR.iterdir()):
                if not book_dir.is_dir():
                    continue

                book_key_iter = book_dir.name.lower()

                # Check if the book is in our mapping
                if book_key_iter not in BookMapper.BOOK_MAPPING:
                    logger.warning(f"⚠️  Unmapped book: {book_key_iter} (skipping...)")
                    continue

                verses, errors = self.verse_processor.process_book(book_key_iter, book_dir)
                total_verses += verses
                total_errors += errors
                books_processed += 1

        logger.info("\n" + "=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)
        logger.info(f"📚 Books processed: {books_processed}")
        logger.info(f"✅ Verses generated: {total_verses}")
        logger.info(f"❌ Errors: {total_errors}")
        logger.info(f"📁 Files saved in: {self.config.VERSES_DIR}")
        logger.info("")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Generate lightweight verse JSON files from Hebrew Scripture data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all books
  python scripts/dict/verse_builder.py

  # Process only Genesis
  python scripts/dict/verse_builder.py --book genesis

  # Process only Genesis chapter 1
  python scripts/dict/verse_builder.py --book genesis --chapter 1
        """
    )
    parser.add_argument(
        '--book',
        type=str,
        help='Book key to process (e.g., genesis, exodus). If not specified, processes all books.'
    )
    parser.add_argument(
        '--chapter',
        type=int,
        help='Chapter number to process. If not specified, processes all chapters of the book.'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run the application
    builder = VerseBuilder()
    builder.run(args.book, args.chapter)


if __name__ == "__main__":
    main()
