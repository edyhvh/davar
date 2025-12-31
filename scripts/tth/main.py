#!/usr/bin/env python3
"""
TTH Processing System - Main Entry Point
=========================================

Main entry point for the TTH (Traducción Textual del Hebreo) processing system.

This script provides a high-level interface for processing Hebrew Scriptures
from DOCX/Markdown to JSON format for the Davar app.

Usage:
    python main.py [command] [args...]

For detailed usage information, run:
    python main.py --help

Author: Davar Project
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from cli import TTHCLI


def main():
    """Main entry point."""
    # Show banner
    print("=" * 70)
    print("TTH Processing System - Davar Project")
    print("Traducción Textual del Hebreo")
    print("=" * 70)
    print()

    # If no arguments, show simplified help
    if len(sys.argv) == 1:
        print("USAGE:")
        print("  python main.py run <book_key>     # Process book to data/tth/")
        print("  python main.py test <book_key>    # Test book to data/tth/temp/")
        print("  python main.py all [--test]       # Process all books")
        print("  python main.py book <books>       # Process multiple books")
        print("  python main.py books              # List available books")
        print("  python main.py --help             # Show full help")
        print()
        print("EXAMPLES:")
        print("  python main.py run amos")
        print("  python main.py test amos")
        print("  python main.py book amos bereshit --test")
        print()
        sys.exit(0)

    # Run CLI
    cli = TTHCLI()
    exit_code = cli.run(sys.argv[1:])

    print()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
