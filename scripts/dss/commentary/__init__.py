"""
DSS Commentary Enhancement Module

Provides Grok-powered commentary rewriting for Dead Sea Scrolls variants
with Strong's number assignment and trilingual output.
"""

from .config import (
    XAI_API_KEY,
    GROK_MODEL,
    DSSI_DIR,
    MAX_BATCH_SIZE,
    validate_grok_api_key,
)
from .loader import load_all_differences
from .writer import write_enhanced_differences, update_metadata

# Lazy import for rewriter to avoid requiring xai-sdk at import time


def get_rewriter():
    """Get the DSSCommentaryRewriter class (requires xai-sdk package)."""
    from .rewriter import DSSCommentaryRewriter
    return DSSCommentaryRewriter


__all__ = [
    'XAI_API_KEY',
    'GROK_MODEL',
    'DSSI_DIR',
    'MAX_BATCH_SIZE',
    'validate_grok_api_key',
    'load_all_differences',
    'get_rewriter',
    'write_enhanced_differences',
    'update_metadata',
]
