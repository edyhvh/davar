#!/usr/bin/env python3
"""Test BDB XML parsing"""

import xml.etree.ElementTree as ET
from pathlib import Path

BDB_XML_PATH = Path(__file__).parent.parent.parent / "data" / "dict" / "raw" / "BrownDriverBriggs.xml"

tree = ET.parse(BDB_XML_PATH)
root = tree.getroot()

# Test finding H1254 entries
test_ids = ["b.cx.aa", "b.cw.aa"]

for bdb_id in test_ids:
    print(f"\n🔍 Searching for {bdb_id}...")
    
    # Try without namespace
    entry = root.find(f".//entry[@id='{bdb_id}']")
    print(f"   Without namespace: {entry is not None}")
    if entry is not None:
        print(f"   mod={entry.get('mod')}, type={entry.get('type')}")
    
    # Try with namespace
    ns = {'ns': 'http://openscriptures.github.com/morphhb/namespace'}
    entry_ns = root.find(f".//ns:entry[@id='{bdb_id}']", ns)
    print(f"   With namespace: {entry_ns is not None}")
    if entry_ns is not None:
        print(f"   mod={entry_ns.get('mod')}, type={entry_ns.get('type')}")
