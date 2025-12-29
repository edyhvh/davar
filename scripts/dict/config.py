"""
Configuration module for Hebrew Scripture processing scripts.

Centralizes all path configurations, constants, and settings used across
the lexicon and verse building pipelines.
"""

from pathlib import Path


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
        self.LEXICON_WORDS_DIR = self.LEXICON_DIR / 'words'
        self.LEXICON_ROOTS_DIR = self.LEXICON_DIR / 'roots'
        self.LEXICON_TESTING_DIR = self.LEXICON_DIR / 'testing'
        self.LEXICON_TESTING_WORDS_DIR = self.LEXICON_TESTING_DIR / 'words'
        self.LEXICON_TESTING_ROOTS_DIR = self.LEXICON_TESTING_DIR / 'roots'

        # Backward compatibility aliases
        self.LEXICON_DRAFT_DIR = self.LEXICON_WORDS_DIR
        self.LEXICON_TESTING_DRAFT_DIR = self.LEXICON_TESTING_WORDS_DIR

        # Translations
        self.TS2009_DIR = self.DATA_DIR / 'ts2009'
        self.TTH_DIR = self.DATA_DIR / 'tth' / 'draft'

        # Output
        self.VERSES_DIR = self.DICT_DIR / 'verses'  # Legacy
        self.BOOKS_DIR = self.DICT_DIR / 'books'    # New consolidated format

        # Scripts directory (for lexicon list file)
        self.SCRIPTS_DIR = self.PROJECT_ROOT / 'scripts' / 'dict'

        # Source files
        self.STRONGS_FILE = self.RAW_DIR / 'strongs_hebrew_dict_en.json'
        self.STRONG_REFS_FILE = self.RAW_DIR / 'strong_refs.json'
        self.BDB_XML = self.RAW_DIR / 'BrownDriverBriggs.xml'
        self.LEXICON_LIST_FILE = self.SCRIPTS_DIR / 'lexicon_100_percent_list.json'

        # Create output directories if they don't exist
        # self.VERSES_DIR.mkdir(exist_ok=True)  # Legacy - removed to avoid creating unnecessary directories


# Global configuration instance
config = Config()
