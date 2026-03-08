#!/usr/bin/env python3
"""
Sync TS2009 translation files from Supabase Storage to local data directory.
This script runs at startup to ensure private TS2009 content is available.
"""

import os
import sys
from pathlib import Path

# Add backend to path for imports
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.config import settings

try:
    from supabase import create_client
except ImportError:
    print("ERROR: supabase package not installed. Run: pip install supabase")
    sys.exit(1)


TS2009_BUCKET = "ts2009"

def sync_ts2009():
    """Download all TS2009 JSON files from Supabase Storage bucket."""
    supabase_url = os.getenv('DAVAR_SUPABASE_URL')
    supabase_key = os.getenv('DAVAR_SUPABASE_SERVICE_KEY')

    if not supabase_url or not supabase_key:
        print("ERROR: DAVAR_SUPABASE_URL and DAVAR_SUPABASE_SERVICE_KEY must be set")
        sys.exit(1)

    # Initialize Supabase client
    supabase = create_client(supabase_url, supabase_key)

    # Target directory respects DAVAR_DATA_PATH
    data_path = Path(settings.data_path) / "ts2009"
    data_path.mkdir(parents=True, exist_ok=True)

    # Storage bucket for private TS2009 files
    bucket = supabase.storage.from_(TS2009_BUCKET)

    try:
        # List all files in bucket
        files = bucket.list()
        print(f"Found {len(files)} files in {TS2009_BUCKET} bucket")

        downloaded = 0
        for file_info in files:
            name = file_info["name"]
            if name.endswith(".json"):
                print(f"Downloading {name}...")
                content = bucket.download(name)
                file_path = data_path / name
                with open(file_path, "wb") as f:
                    f.write(content)
                downloaded += 1

        print(f"Successfully synced {downloaded} TS2009 files to {data_path}")

    except Exception as e:
        print(f"ERROR: Failed to sync TS2009 files: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_ts2009()