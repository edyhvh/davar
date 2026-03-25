#!/usr/bin/env python3
"""Manual TS2009 sync entrypoint."""

import sys
from pathlib import Path

# Add backend to path for imports
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.services.ts2009_sync import sync_ts2009_files

def sync_ts2009():
    """Sync TS2009 files from Supabase Storage."""
    try:
        result = sync_ts2009_files()
        print(
            "TS2009 sync complete: "
            f"listed={result.listed}, "
            f"downloaded={result.downloaded}, "
            f"skipped={result.skipped}, "
            f"manifest={result.manifest_path}"
        )
    except Exception as exc:
        print(f"ERROR: Failed to sync TS2009 files: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    sync_ts2009()