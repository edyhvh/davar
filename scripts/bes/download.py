#!/usr/bin/env python3
"""
Download BES (Biblia en Español Sencillo) USFX XML source file
"""

import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Source URL for BES USFX XML
BES_USFX_URL = "https://github.com/seven1m/open-bibles/raw/master/spa-bes.usfx.xml"
OUTPUT_PATH = Path(__file__).parent.parent.parent / "data" / "bes" / "raw" / "spa-bes.usfx.xml"

def download_bes_usfx() -> bool:
    """Download BES USFX XML file to data/bes/raw/"""
    try:
        logger.info(f"Downloading BES USFX from {BES_USFX_URL}")

        # Ensure output directory exists
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Download the file
        response = requests.get(BES_USFX_URL, timeout=30)
        response.raise_for_status()

        # Write to file
        with open(OUTPUT_PATH, 'wb') as f:
            f.write(response.content)

        logger.info(f"Downloaded BES USFX to {OUTPUT_PATH} ({len(response.content)} bytes)")
        return True

    except requests.RequestException as e:
        logger.error(f"Failed to download BES USFX: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error downloading BES USFX: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = download_bes_usfx()
    exit(0 if success else 1)