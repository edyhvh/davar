"""
Configuration module for Grok translation system.

Loads API keys and configures Grok-specific translation settings.
"""

import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / '.env'

# Try to load .env file, but don't fail if it doesn't exist or can't be read
try:
    if ENV_FILE.exists() and ENV_FILE.is_file():
        load_dotenv(ENV_FILE, override=False)
except (PermissionError, IOError) as e:
    # If we can't read .env, continue - environment variables might be set elsewhere
    import warnings
    warnings.warn(f"Could not load .env file: {e}. Using environment variables if available.")

# Supported languages mapping: code -> full name
SUPPORTED_LANGUAGES: Dict[str, str] = {
    'es': 'Spanish',
    'pt': 'Portuguese',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'ar': 'Arabic',
    'fa': 'Farsi',
}

# Default language
DEFAULT_LANGUAGE = 'es'

# Grok API Configuration
XAI_API_KEY = os.getenv('XAI_API_KEY')
GROK_MODEL = 'grok-4'  # Fastest model: $0.10/1M input, $0.30/1M output

# Paths
LEXICON_DIR = PROJECT_ROOT / 'data' / 'dict' / 'lexicon'
ROOTS_FILE = LEXICON_DIR / 'roots.json'
WORDS_FILE = LEXICON_DIR / 'words.json'
ROOTS_PRETTY_FILE = LEXICON_DIR / 'roots.pretty.json'
WORDS_PRETTY_FILE = LEXICON_DIR / 'words.pretty.json'

# Translation settings (reuse from parent config)
DEFAULT_BATCH_SIZE = 50  # Number of definitions per API call
MAX_BATCH_SIZE = 100
MIN_BATCH_SIZE = 1

# Rate limiting and retry settings
# Grok has higher rate limits than Gemini free tier
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # Exponential backoff: 2^retry seconds
RATE_LIMIT_DELAY = 1.0  # Seconds to wait between API calls (Grok has higher limits)

# Batch API settings (Grok doesn't use batch API, but kept for compatibility)
USE_BATCH_API = False  # Grok doesn't support batch API
BATCH_INLINE_MAX_SIZE = 1000
BATCH_FILE_THRESHOLD = 1000
BATCH_POLL_INTERVAL = 60
BATCH_MAX_WAIT_HOURS = 24

# API Configuration
GROK_BASE_URL = "https://api.x.ai/v1"
GROK_TIMEOUT = 3600  # 1 hour timeout (recommended for reasoning models, though grok-4 is fast)


def validate_language(lang_code: str) -> bool:
    """
    Validate if a language code is supported.
    
    Args:
        lang_code: Language code (e.g., 'es', 'pt')
        
    Returns:
        True if supported, False otherwise
    """
    return lang_code.lower() in SUPPORTED_LANGUAGES


def get_language_name(lang_code: str) -> Optional[str]:
    """
    Get the full name of a language from its code.
    
    Args:
        lang_code: Language code (e.g., 'es', 'pt')
        
    Returns:
        Full language name or None if not found
    """
    return SUPPORTED_LANGUAGES.get(lang_code.lower())


def validate_grok_api_key() -> bool:
    """
    Validate that the xAI API key is set.
    
    Returns:
        True if API key is set, False otherwise
    """
    return XAI_API_KEY is not None and len(XAI_API_KEY.strip()) > 0

