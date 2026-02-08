#!/usr/bin/env python3
"""
Audit: Find lexicon entries with fewer BDB senses than LexicalIndex provides.

Catches words like H4723 (miqveh) that have multiple BDB entries
(e.g. "hope" + "collection") but only one sense made it into our lexicon.

The root cause is the homonym prioritization in build_lexicon.py which
groups BDB entries by `mod` attribute and only keeps the first group,
discarding alternate senses from different etymological roots.

Usage:
    cd ~/davar && python -m scripts.dict.audit_missing_senses
    cd ~/davar && python -m scripts.dict.audit_missing_senses --fix
    cd ~/davar && python -m scripts.dict.audit_missing_senses --fix --dry-run
"""

from config import config
import json
import sys
from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).parent))

LI_NS = {'li': 'http://openscriptures.github.com/morphhb/namespace'}
BDB_NS = {'bdb': 'http://openscriptures.github.com/morphhb/namespace'}


def load_lexical_index_senses():
    """Load LexicalIndex and collect distinct BDB entries per Strong's number."""
    tree = ET.parse(config.LEXICAL_INDEX)
    root = tree.getroot()

    strong_bdb_map = defaultdict(list)

    for entry in root.findall('.//li:entry', LI_NS):
        xref = entry.find('li:xref', LI_NS)
        def_elem = entry.find('li:def', LI_NS)
        pos_elem = entry.find('li:pos', LI_NS)
        if xref is None:
            continue
        strong = xref.get('strong')
        aug = xref.get('aug', '')
        bdb_id = xref.get('bdb', '')
        gloss = def_elem.text.strip() if def_elem is not None and def_elem.text else ''
        pos = pos_elem.text.strip() if pos_elem is not None and pos_elem.text else ''

        if strong:
            strong_key = f"H{strong}"
            strong_bdb_map[strong_key].append({
                'bdb_id': bdb_id,
                'aug': aug,
                'gloss': gloss,
                'pos': pos,
            })

    return strong_bdb_map


def load_lexicon_definitions():
    """Load definitions per Strong's number from words/ and roots/."""
    result = {}
    for directory in [config.LEXICON_WORDS_DIR, config.LEXICON_ROOTS_DIR]:
        if not directory.exists():
            continue
        for f in directory.glob('H*.json'):
            try:
                data = json.load(open(f, 'r', encoding='utf-8'))
                strong = data.get('strong_number', f.stem)
                defs = data.get('definitions', [])
                main_glosses = [
                    d.get('text_en', '').lower().strip()
                    for d in defs
                    if d.get('sense', '') == '0'
                ]
                all_glosses = [
                    d.get('text_en', '').lower().strip()
                    for d in defs
                ]
                result[strong] = {
                    'total_defs': len(defs),
                    'main_glosses': main_glosses,
                    'all_glosses': all_glosses,
                    'lemma': data.get('lemma', ''),
                    'file': str(f),
                }
            except Exception:
                pass
    return result


def find_bdb_entry_by_id(bdb_root, bdb_id):
    """Find a BDB entry by its id attribute."""
    if bdb_root is None or not bdb_id:
        return None
    return bdb_root.find(f'.//bdb:entry[@id="{bdb_id}"]', BDB_NS)


def extract_definitions_from_bdb_entry(bdb_entry):
    """Extract definition texts from a BDB XML entry."""
    if bdb_entry is None:
        return []
    defs = []

    # Top-level definitions
    for d in bdb_entry.findall('./bdb:def', BDB_NS):
        if d.text and d.text.strip():
            defs.append(d.text.strip())

    # Definitions inside senses
    for sense in bdb_entry.findall('.//bdb:sense', BDB_NS):
        for d in sense.findall('./bdb:def', BDB_NS):
            if d.text and d.text.strip():
                defs.append(d.text.strip())

    return defs


def gloss_matches(needle, haystack_set):
    """Check if a gloss is already represented (exact or substring match)."""
    needle_lower = needle.lower().strip()
    for existing in haystack_set:
        if needle_lower == existing or needle_lower in existing or existing in needle_lower:
            return True
    return False


def fix_entry(strong, missing_glosses, bdb_root):
    """
    Add missing BDB definitions to the lexicon entry.

    Returns (updated_data, filepath) or (None, None) if nothing to do.
    """
    # Find the file
    filepath = config.LEXICON_WORDS_DIR / f"{strong}.json"
    if not filepath.exists():
        filepath = config.LEXICON_ROOTS_DIR / f"{strong}.json"
    if not filepath.exists():
        return None, None

    data = json.load(open(filepath, 'r', encoding='utf-8'))
    definitions = data.get('definitions', [])
    max_order = max((d.get('order', 0) for d in definitions), default=0)

    added = 0
    for entry in missing_glosses:
        bdb_id = entry['bdb_id']
        gloss = entry['gloss']

        # Try to get richer definitions from BDB XML
        bdb_entry = find_bdb_entry_by_id(
            bdb_root, bdb_id) if bdb_root else None
        bdb_defs = extract_definitions_from_bdb_entry(
            bdb_entry) if bdb_entry else []

        # Use BDB definitions if available, otherwise fall back to LI gloss
        defs_to_add = bdb_defs if bdb_defs else [gloss]

        existing_texts = {d.get('text_en', '').lower().strip()
                          for d in definitions}

        for def_text in defs_to_add:
            if not def_text or len(def_text.strip()) <= 1:
                continue
            if def_text.lower().strip() in existing_texts:
                continue
            if gloss_matches(def_text, existing_texts):
                continue
            # Skip preposition fragments
            if def_text.strip().lower() in {'in', 'on', 'at', 'to', 'of', 'by', 'as', 'with', 'from', 'for'}:
                continue

            max_order += 1
            definitions.append({
                'text_en': def_text.strip(),
                'source': 'bdb',
                'order': max_order,
                'sense': '0',
            })
            existing_texts.add(def_text.lower().strip())
            added += 1

    if added == 0:
        return None, None

    data['definitions'] = definitions
    data['sources'] = data.get('sources', {})
    data['sources']['bdb'] = True
    return data, filepath


def main():
    fix_mode = '--fix' in sys.argv
    dry_run = '--dry-run' in sys.argv

    print("=" * 80)
    print("AUDIT: MISSING BDB SENSES")
    if fix_mode:
        print(f"  MODE: {'DRY RUN' if dry_run else 'FIX (will write files)'}")
    print("=" * 80)

    print("\nLoading LexicalIndex...")
    li_senses = load_lexical_index_senses()
    print(f"  Strong's numbers in LexicalIndex: {len(li_senses)}")

    print("Loading lexicon entries...")
    lexicon = load_lexicon_definitions()
    print(f"  Lexicon entries: {len(lexicon)}")

    bdb_root = None
    if fix_mode:
        from utils import load_bdb_xml
        print("Loading BDB XML for fix mode...")
        bdb_root = load_bdb_xml()

    # Find entries where LexicalIndex has more distinct BDB senses than we have
    missing = []
    for strong, bdb_entries in li_senses.items():
        # Skip entries that only have proper-name senses (pos=Np with no other entries)
        non_propername = [e for e in bdb_entries if e['pos'] != 'Np']
        if len(non_propername) <= 1:
            # Either 0-1 non-proper-name senses — check if there are multiple with glosses
            meaningful = [e for e in bdb_entries if e['gloss']
                          and e['pos'] != 'Np']
            if len(meaningful) <= 1:
                continue

        if strong not in lexicon:
            continue

        lex = lexicon[strong]
        our_glosses = set(lex['all_glosses'])

        missing_glosses = []
        for entry in bdb_entries:
            g = entry['gloss'].lower().strip()
            if not g:
                continue
            if entry['pos'] == 'Np':
                continue
            if not gloss_matches(g, our_glosses):
                missing_glosses.append(entry)

        if missing_glosses:
            missing.append({
                'strong': strong,
                'lemma': lex['lemma'],
                'our_defs': lex['total_defs'],
                'our_glosses': list(our_glosses),
                'li_entries': len(bdb_entries),
                'missing': missing_glosses,
            })

    missing.sort(key=lambda x: int(x['strong'][1:])
                 if x['strong'][1:].isdigit() else 0)

    print(f"\n{'=' * 80}")
    print(
        f"RESULTS: {len(missing)} entries with potentially missing BDB senses")
    print(f"{'=' * 80}\n")

    fixed_count = 0
    for item in missing:
        mg = ', '.join(
            f'"{e["gloss"]}" (bdb={e["bdb_id"]})' for e in item['missing'])
        ours = ', '.join(f'"{g}"' for g in item['our_glosses'][:5]) or '(none)'
        print(f"  {item['strong']} {item['lemma']}")
        print(f"    Our glosses: {ours}  ({item['our_defs']} total defs)")
        print(f"    Missing from LI: {mg}")

        if fix_mode:
            updated_data, filepath = fix_entry(
                item['strong'], item['missing'], bdb_root)
            if updated_data and filepath:
                new_count = len(updated_data['definitions'])
                if dry_run:
                    print(
                        f"    [DRY RUN] Would update {filepath.name}: {item['our_defs']} -> {new_count} defs")
                else:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(updated_data, f,
                                  ensure_ascii=False, indent=2)
                    print(
                        f"    ✅ Updated {filepath.name}: {item['our_defs']} -> {new_count} defs")
                fixed_count += 1
            else:
                print(
                    f"    ⏭️  No new definitions to add (already covered or BDB empty)")

        print()

    print(f"{'=' * 80}")
    print(f"Total entries to review: {len(missing)}")
    if fix_mode:
        print(f"{'Fixed' if not dry_run else 'Would fix'}: {fixed_count}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
