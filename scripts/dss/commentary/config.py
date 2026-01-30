"""
Configuration for DSS Commentary Enhancement.

Uses Claude API (Anthropic) for commentary generation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / '.env'

try:
    if ENV_FILE.exists() and ENV_FILE.is_file():
        load_dotenv(ENV_FILE, override=False)
except (PermissionError, IOError) as e:
    import warnings
    warnings.warn(f"Could not load .env file: {e}. Using environment variables if available.")

# Claude API Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
CLAUDE_MODEL = 'claude-haiku-4-5-20251001'  # Fast, intelligent, cost-effective
CLAUDE_API_VERSION = '2023-06-01'
CLAUDE_TIMEOUT = 120  # 2 minutes - Claude Haiku should respond within this time

# Paths
DSSI_DIR = PROJECT_ROOT / 'data' / 'dss' / 'dssi' / 'books'
METADATA_FILE = PROJECT_ROOT / 'data' / 'dss' / 'dssi' / 'metadata.json'

# Batch settings
# Note: Each difference generates ~400 tokens (Strong's + 3 commentaries)
# With 8K token limit, safe batch size is ~15 items to avoid truncation
MAX_BATCH_SIZE = 15  # Reduced for reliability
DEFAULT_BATCH_SIZE = 15

# Rate limiting and retry
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2.0
RATE_LIMIT_DELAY = 0.5  # seconds between calls

# Commentary version
COMMENTARY_VERSION = "v2_claude_2026"

# Temperature for generation
TEMPERATURE = 0.3  # Consistent, reproducible


def validate_anthropic_api_key() -> bool:
    """
    Validate that the Anthropic API key is set.
    
    Returns:
        True if API key is set, False otherwise
    """
    return ANTHROPIC_API_KEY is not None and len(ANTHROPIC_API_KEY.strip()) > 0
