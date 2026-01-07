"""
Lexicon translation module.

Provides translation functionality for Davar lexicon dictionaries using xAI Grok API.
"""

from .config import (
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
    DEFAULT_BATCH_SIZE,
    ROOTS_FILE,
    WORDS_FILE,
    validate_language,
    get_language_name,
    validate_grok_api_key,
    XAI_API_KEY,
    GROK_MODEL,
)
from .translator import GrokTranslator
from .processor import LexiconProcessor

__all__ = [
    'SUPPORTED_LANGUAGES',
    'DEFAULT_LANGUAGE',
    'DEFAULT_BATCH_SIZE',
    'ROOTS_FILE',
    'WORDS_FILE',
    'validate_language',
    'get_language_name',
    'validate_grok_api_key',
    'XAI_API_KEY',
    'GROK_MODEL',
    'GrokTranslator',
    'LexiconProcessor',
]

