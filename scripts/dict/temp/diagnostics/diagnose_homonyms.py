#!/usr/bin/env python3
"""
Diagnostic script to identify Strong's numbers affected by BDB homonym mixing issue.

This script:
1. Parses LexicalIndex.xml to find Strong's numbers with multiple BDB entries
2. Cross-references BrownDriverBriggs.xml to confirm mod="I", mod="II"+ homonyms exist
3. Outputs a list of affected Strong's numbers and their BDB entry details

Author: Davar Project
Date: February 2026
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data" / "dict"
RAW_DIR = DATA_DIR / "raw"
LEXICAL_INDEX_PATH = RAW_DIR / "LexicalIndex.xml"
BDB_XML_PATH = RAW_DIR / "BrownDriverBriggs.xml"
OUTPUT_PATH = DATA_DIR / "affected_words.json"

def parse_lexical_index() -> Dict[str, List[Dict[str, str]]]:
    """
    Parse LexicalIndex.xml to find Strong's numbers with multiple BDB entries.
    
    Returns:
        Dict mapping Strong's number (e.g., "H1254") to list of BDB entry info
    """
    print("📖 Parsing LexicalIndex.xml...")
    tree = ET.parse(LEXICAL_INDEX_PATH)
    root = tree.getroot()
    
    # Define namespace
    ns = {'ns': 'http://openscriptures.github.com/morphhb/namespace'}
    
    # Group by Strong's number
    strong_to_bdb = defaultdict(list)
    
    # Parse all entry elements that contain xref elements
    for entry in root.findall(".//ns:entry", ns):
        xref = entry.find("ns:xref", ns)
        if xref is not None:
            strong = xref.get("strong")
            bdb = xref.get("bdb")
            aug = xref.get("aug", "a")  # Default to "a" if not specified
            twot = xref.get("twot")
            
            # Get the Hebrew word and definition from parent entry
            w_elem = entry.find("ns:w", ns)
            def_elem = entry.find("ns:def", ns)
            hebrew = w_elem.text if w_elem is not None else ""
            definition = def_elem.text if def_elem is not None else ""
            
            if strong and bdb:
                # Add H prefix if not present
                if not strong.startswith("H"):
                    strong = f"H{strong}"
                
                strong_to_bdb[strong].append({
                    "bdb_id": bdb,
                    "aug": aug,
                    "twot": twot,
                    "hebrew": hebrew,
                    "definition": definition
                })
    
    # Filter to only Strong's numbers with multiple BDB entries
    multi_entry_strongs = {
        strong: entries 
        for strong, entries in strong_to_bdb.items() 
        if len(entries) > 1
    }
    
    print(f"✅ Found {len(multi_entry_strongs)} Strong's numbers with multiple BDB entries")
    return multi_entry_strongs

def parse_bdb_entries(bdb_ids: List[str]) -> Dict[str, Dict]:
    """
    Parse BrownDriverBriggs.xml to get entry details for given BDB IDs.
    
    Args:
        bdb_ids: List of BDB entry IDs (e.g., ["b.cx.aa", "b.cw.aa"])
    
    Returns:
        Dict mapping BDB ID to entry details (mod, first definition, etc.)
    """
    tree = ET.parse(BDB_XML_PATH)
    root = tree.getroot()
    
    # Define namespace for BDB XML
    ns = {'ns': 'http://openscriptures.github.com/morphhb/namespace'}
    
    bdb_details = {}
    
    for bdb_id in bdb_ids:
        # Find the entry with this ID (using namespace)
        entry = root.find(f".//ns:entry[@id='{bdb_id}']", ns)
        
        if entry is not None:
            mod = entry.get("mod", "I")  # Default to "I" if not specified
            entry_type = entry.get("type", "")
            
            # Try to extract first definition text (simplified)
            def_text = ""
            # Look for first text content
            for text in entry.itertext():
                clean = text.strip()
                if clean and len(clean) > 3:  # Skip very short fragments
                    def_text = clean[:100]  # First 100 chars
                    break
            
            bdb_details[bdb_id] = {
                "mod": mod,
                "type": entry_type,
                "preview": def_text
            }
    
    return bdb_details

def diagnose_affected_words() -> Dict:
    """
    Main diagnostic function to identify all affected Strong's numbers.
    
    Returns:
        Dict with diagnostic results and affected word details
    """
    print("🔍 Starting BDB Homonym Diagnostic...\n")
    
    # Step 1: Find Strong's numbers with multiple BDB entries
    multi_entry_strongs = parse_lexical_index()
    
    # Step 2: Analyze each to see if they have mod="I", mod="II"+ homonyms
    affected_words = {}
    homonym_count = defaultdict(int)
    
    print("\n🔬 Analyzing BDB entries for homonym markers...")
    
    debug_count = 0
    for strong, entries in multi_entry_strongs.items():
        bdb_ids = [e["bdb_id"] for e in entries]
        bdb_details = parse_bdb_entries(bdb_ids)
        
        # Debug: Show first 3 examples
        if debug_count < 3:
            print(f"   DEBUG {strong}: BDB IDs = {bdb_ids}, mods = {[d.get('mod') for d in bdb_details.values()]}")
            debug_count += 1
        
        # Check if there are different mod values (indicating true homonyms)
        mods = set(d.get("mod", "I") for d in bdb_details.values())
        
        # Only include if multiple mod values exist (true homonyms)
        if len(mods) > 1 or any(d.get("mod") in ["II", "III", "IV"] for d in bdb_details.values()):
            # Merge entry info with BDB details
            for entry in entries:
                bdb_id = entry["bdb_id"]
                if bdb_id in bdb_details:
                    entry.update(bdb_details[bdb_id])
            
            affected_words[strong] = {
                "strong_number": strong,
                "entries": entries,
                "homonym_count": len(entries)
            }
            
            homonym_count[len(entries)] += 1
    
    # Step 3: Compile statistics
    stats = {
        "total_affected": len(affected_words),
        "by_homonym_count": dict(homonym_count),
        "examples": {}
    }
    
    # Add some key examples
    if "H1254" in affected_words:
        stats["examples"]["H1254_bara_create"] = affected_words["H1254"]
    if "H352" in affected_words:
        stats["examples"]["H352_ayil_ram"] = affected_words["H352"]
    if "H1481" in affected_words:
        stats["examples"]["H1481_gur_sojourn"] = affected_words["H1481"]
    
    print(f"\n✅ Diagnostic complete!")
    print(f"   Total affected Strong's numbers: {stats['total_affected']}")
    print(f"   Distribution by homonym count: {stats['by_homonym_count']}")
    
    return {
        "stats": stats,
        "affected_words": affected_words
    }

def main():
    """Main entry point."""
    # Run diagnostic
    results = diagnose_affected_words()
    
    # Save to JSON file
    print(f"\n💾 Saving results to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Diagnostic complete! Results saved to {OUTPUT_PATH}")
    print(f"\n📊 Summary:")
    print(f"   Total affected words: {results['stats']['total_affected']}")
    print(f"   Distribution by homonym count:")
    for count, num_words in sorted(results['stats']['by_homonym_count'].items()):
        print(f"      {count} homonyms: {num_words} words")
    
    # Show a few examples
    if results['stats']['examples']:
        print(f"\n🔬 Key examples:")
        for key, example in list(results['stats']['examples'].items())[:3]:
            strong = example['strong_number']
            entries = example['entries']
            print(f"\n   {strong}:")
            for entry in entries:
                mod = entry.get('mod', '?')
                preview = entry.get('preview', '')[:50]
                print(f"      mod={mod} (aug={entry['aug']}): {preview}...")

if __name__ == "__main__":
    main()
