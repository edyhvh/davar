#!/usr/bin/env python3
"""
Convenience entry point for running the DSS parser
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
