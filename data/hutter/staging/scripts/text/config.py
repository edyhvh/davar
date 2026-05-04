"""Configuration and constants for Hebrew text transcription."""

from pathlib import Path

# Available books in the Hebrew Bible corpus
AVAILABLE_BOOKS = [
    'matthew', 'mark', 'luke', 'john', 'acts', 'romans',
    'corinthians1', 'corinthians2', 'galatians', 'ephesians',
    'philippians', 'colossians', 'thessalonians1', 'thessalonians2',
    'timothy1', 'timothy2', 'titus', 'philemon', 'hebrews',
    'james', 'peter1', 'peter2', 'john1', 'john2', 'john3',
    'jude', 'revelation'
]

# Default paths
DEFAULT_IMAGES_DIR = Path('data/images/hebrew_images')
DEFAULT_OUTPUT_DIR = Path('output')
DEFAULT_YAML_PATH = Path('docs/hebrew.yaml')
DEFAULT_CHECKPOINT_DIR = Path('output/.checkpoints')

# Special book configurations
SPECIAL_BOOKS = {
    'colossians': {
        'exclude_pages': ['000026.png', '000028.png', '000030.png']
    },
    'john1': {
        'skip_pages': [6, 8],
        'odd_from': 9
    }
}

# Claude API pricing (per 1M tokens)
CLAUDE_PRICING = {
    'input': 3.00,
    'output': 15.00
}

# Image processing
MAX_DRY_RUN_IMAGES = 5
PARALLEL_DELAY_SECONDS = 0.5

