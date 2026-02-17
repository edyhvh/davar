#!/usr/bin/env python3
"""Entrypoint for `python -m scripts.delitzsch`."""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
