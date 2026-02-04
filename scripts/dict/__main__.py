#!/usr/bin/env python3
"""
Entry point for the Hebrew Scripture Processing CLI.

Usage:
    python -m scripts.dict --help
    python -m scripts.dict lexicon build <args>
    python -m scripts.dict verses build <args>
    etc.
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())