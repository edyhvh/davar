"""
Hebrew text transcription using Claude Vision API.

This package provides tools for transcribing Hebrew Bible images
using Anthropic's Claude Vision API.

Usage:
    python -m scripts.text --list                    # List available books
    python -m scripts.text --book matthew --dry-run  # Process 5 images
    python -m scripts.text --book matthew            # Process one book
    python -m scripts.text matthew mark luke         # Process multiple books
    python -m scripts.text --all                     # Process all books
    python -m scripts.text --book matthew --resume   # Resume from checkpoint
"""

# Core imports that don't require heavy dependencies
from .validate import (
    parse_json_response,
    validate_chapter_object,
    validate_verse_object,
    validate_hebrew_text,
    validate_verse_sequence,
    validate_chapter_sequence
)
from .books import get_book_info, get_chapter_context, validate_chapter_number
from .config import AVAILABLE_BOOKS

# Lazy imports for modules that require PIL and other heavy dependencies
# These are only imported when actually accessed to avoid import errors
# when only validation functions are needed
def __getattr__(name: str):
    """Lazy import handler for optional dependencies."""
    if name == 'ClaudeClient':
        from .api import ClaudeClient
        return ClaudeClient
    if name == 'CheckpointManager':
        from .checkpoint import CheckpointManager
        return CheckpointManager
    if name == 'consolidate_book':
        from .consolidate import consolidate_book
        return consolidate_book
    if name == 'load_yaml':
        from .prompt import load_yaml
        return load_yaml
    if name == 'build_prompt':
        from .prompt import build_prompt
        return build_prompt
    if name == 'get_yaml_version':
        from .prompt import get_yaml_version
        return get_yaml_version
    if name == 'calculate_yaml_hash':
        from .prompt import calculate_yaml_hash
        return calculate_yaml_hash
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # API
    'ClaudeClient',
    # Checkpoint
    'CheckpointManager',
    # Prompt
    'load_yaml',
    'build_prompt',
    'get_yaml_version',
    'calculate_yaml_hash',
    # Validation
    'parse_json_response',
    'validate_chapter_object',
    'validate_verse_object',
    'validate_hebrew_text',
    'validate_verse_sequence',
    'validate_chapter_sequence',
    # Consolidation
    'consolidate_book',
    # Books
    'get_book_info',
    'get_chapter_context',
    'validate_chapter_number',
    'AVAILABLE_BOOKS',
]

