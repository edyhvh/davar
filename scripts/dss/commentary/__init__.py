"""
DSS Commentary Enhancement Module

Provides Claude-powered commentary rewriting for Dead Sea Scrolls variants
with Strong's number assignment and trilingual output.
"""

from .config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    DSSI_DIR,
    MAX_BATCH_SIZE,
    validate_anthropic_api_key,
)
from .loader import load_all_differences
from .writer import write_enhanced_differences, update_metadata

# Lazy import for rewriter to avoid requiring anthropic at import time


def get_rewriter():
    """Get the DSSCommentaryRewriter class (requires anthropic package)."""
    from .rewriter import DSSCommentaryRewriter
    return DSSCommentaryRewriter


__all__ = [
    'ANTHROPIC_API_KEY',
    'CLAUDE_MODEL',
    'DSSI_DIR',
    'MAX_BATCH_SIZE',
    'validate_anthropic_api_key',
    'load_all_differences',
    'get_rewriter',
    'write_enhanced_differences',
    'update_metadata',
]
