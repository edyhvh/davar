"""
Configuration for DSS Commentary Enhancement.

Uses Grok API (xAI) for commentary generation.
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

# Grok API Configuration (xAI)
XAI_API_KEY = os.getenv('XAI_API_KEY')
GROK_MODEL = 'grok-4-1-fast-non-reasoning'  # Fast, cost-effective: $0.20/1M input, $0.50/1M output
GROK_TIMEOUT = 3600  # 1 hour timeout for longer batches

# Paths
DSSI_DIR = PROJECT_ROOT / 'data' / 'dss' / 'dssi' / 'books'
METADATA_FILE = PROJECT_ROOT / 'data' / 'dss' / 'dssi' / 'metadata.json'

# Batch settings
# Note: Grok 4.1 Fast has 2M context window but response limits require smaller batches
# Each difference generates ~300 tokens input + ~400 tokens output (Strong's + 3 commentaries)
# Conservative batch size ensures complete JSON responses without truncation
MAX_BATCH_SIZE = 50  # Conservative size to avoid response truncation
DEFAULT_BATCH_SIZE = 50

# Rate limiting and retry
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2.0
RATE_LIMIT_DELAY = 1.0  # seconds between calls (Grok has generous limits)

# Commentary version
COMMENTARY_VERSION = "v2_grok_2026"

# Temperature for generation
TEMPERATURE = 0.3  # Consistent, reproducible


def validate_grok_api_key() -> bool:
    """
    Validate that the xAI API key is set.
    
    Returns:
        True if API key is set, False otherwise
    """
    return XAI_API_KEY is not None and len(XAI_API_KEY.strip()) > 0
