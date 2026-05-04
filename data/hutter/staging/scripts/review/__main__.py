"""
Main entry point for the Hutter text corrections package.

This allows the package to be run as: python -m scripts.review
"""

from .apply_corrections import main

if __name__ == '__main__':
    main()