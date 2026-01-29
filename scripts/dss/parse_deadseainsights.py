#!/usr/bin/env python3
"""
Parse Dead Sea Scrolls differences from deadseainsights repository
Extract differences between DSS and Masoretic text into structured JSON

This script now uses the modular parser package for better maintainability.
For direct usage, see individual modules in the dss package.
"""

import sys
from pathlib import Path

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from dss.main import main

if __name__ == '__main__':
    main()
