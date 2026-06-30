#!/usr/bin/env python3
"""Canonical Delitzsch CLI with subcommands."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    scripts_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(scripts_dir))
    from delitzsch.commands import audit, normalize, normalize_holem, review, run
else:
    from .commands import audit, normalize, normalize_holem, review, run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="delitzsch",
        description="Delitzsch parsing and maintenance CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run.register_subcommand(subparsers)
    audit.register_subcommand(subparsers)
    normalize_holem.register_subcommand(subparsers)
    normalize.register_subcommand(subparsers)
    review.register_subcommand(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 1

    return int(handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
