#!/usr/bin/env python3
"""
Particle Dictionary CSV Importer

Parses CSV data and creates JSON dictionary entries for Hebrew particles.
Processes data/not_strong/chart_en.csv and data/not_strong/chart_es.csv.

Usage:
    python scripts/particles/import_csv.py [--test] [--verbose]

Options:
    --test      Test mode: show what would be created without writing files
    --verbose   Verbose output with progress details
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

# Particle ID mapping based on main form (inseparable prefixes only)
PARTICLE_MAPPING = {
    'בְּ': 'Hb',   # be - in/with/by
    'הַ': 'Hd',   # ha - definite article
    'וְ': 'Hc',   # ve - conjunction
    'לְ': 'Hl',   # le - to/for
    'מִ': 'Hm',   # mi - from/than
    'כְּ': 'Hk',   # ke - as/like
    'אֵת': 'Ht',   # et - object marker (when used as prefix)
}

def normalize_form(form):
    """Normalize particle form by removing maqqef and stripping whitespace"""
    return form.replace('־', '').strip()

def parse_forms(forms_string):
    """Parse forms from CSV string (separated by ' · ')"""
    if not forms_string or forms_string.strip() == '':
        return []

    forms = [f.strip() for f in forms_string.split(' · ') if f.strip()]
    return [normalize_form(f) for f in forms]

def map_to_particle_id(main_form):
    """Map main form to particle ID"""
    normalized = normalize_form(main_form)
    if normalized in PARTICLE_MAPPING:
        return PARTICLE_MAPPING[normalized]

    # Fallback: try to find by partial match
    for form, pid in PARTICLE_MAPPING.items():
        if normalized in form:
            return pid

    raise ValueError(f"Could not map form '{main_form}' to particle ID")

def read_csv_data(csv_path):
    """Read CSV file and return list of dictionaries"""
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    return data

def create_particle_entry(en_row, es_row, verbose=False):
    """Create a particle entry from CSV rows"""
    try:
        particle_id = map_to_particle_id(en_row['Main Form'])

        if verbose:
            print(f"Processing {en_row['Main Form']} → {particle_id}")

        entry = {
            "id": particle_id,
            "main_form": en_row['Main Form'],
            "type": en_row['Type'],
            "meanings": {
                "en": [m.strip() for m in en_row['Main Meanings (expanded)'].split(' · ') if m.strip()],
                "es": [m.strip() for m in es_row['Significados principales (ampliados)'].split(' · ') if m.strip()]
            },
            "notes": {
                "en": en_row['Notes for Davar'],
                "es": es_row['Notas para Davar']
            },
            "forms": parse_forms(en_row['Most Common Forms']),
            "frequency": 0  # Will be populated by scan script
        }

        return particle_id, entry

    except Exception as e:
        print(f"Error processing row: {e}")
        print(f"EN row: {en_row}")
        print(f"ES row: {es_row}")
        raise

def save_particle_entry(particle_id, entry, output_dir, test_mode=False):
    """Save particle entry to JSON file"""
    output_path = os.path.join(output_dir, f"{particle_id}.json")

    if test_mode:
        print(f"Would create: {output_path}")
        print(f"Content: {json.dumps(entry, indent=2, ensure_ascii=False)}")
        return

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"Created: {output_path}")

def create_master_index(entries, output_path, test_mode=False):
    """Create master particles.json index"""
    index = {
        "version": "1.0",
        "description": "Master index of Hebrew particles for Davar",
        "particles": list(entries.keys()),
        "total_count": len(entries)
    }

    if test_mode:
        print(f"Would create master index: {output_path}")
        print(f"Content: {json.dumps(index, indent=2, ensure_ascii=False)}")
        return

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"Created master index: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Import particle dictionary from CSV')
    parser.add_argument('--test', action='store_true', help='Test mode - show what would be created without writing files')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    # Input files
    script_dir = os.path.dirname(__file__)
    en_csv = Path(os.path.join(script_dir, '..', '..', 'data', 'dict', 'prefixes', 'raw', 'chart_en.csv'))
    es_csv = Path(os.path.join(script_dir, '..', '..', 'data', 'dict', 'prefixes', 'raw', 'chart_es.csv'))

    # Output directories
    entries_dir = Path(os.path.join(script_dir, '..', '..', 'data', 'dict', 'prefixes', 'entries'))
    master_index = Path(os.path.join(script_dir, '..', '..', 'data', 'dict', 'prefixes', 'prefixes.json'))

    if args.verbose:
        print("Reading CSV files...")

    en_data = read_csv_data(en_csv)
    es_data = read_csv_data(es_csv)

    if len(en_data) != len(es_data):
        print(f"Error: EN and ES CSV files have different row counts ({len(en_data)} vs {len(es_data)})")
        sys.exit(1)

    if len(en_data) != 7:
        print(f"Warning: Expected 7 Hebrew prefix entries, found {len(en_data)}")
    
    if args.verbose:
        print(f"Found {len(en_data)} Hebrew prefix entries")

    entries = {}
    for i, (en_row, es_row) in enumerate(zip(en_data, es_data)):
        try:
            particle_id, entry = create_particle_entry(en_row, es_row, args.verbose)
            entries[particle_id] = entry

            if args.verbose:
                print(f"  [{i+1}/{len(en_data)}] {particle_id}: {entry['main_form']}")

        except Exception as e:
            print(f"Failed to process row {i+1}: {e}")
            continue

    # Save entries
    if args.verbose:
        print(f"\nSaving {len(entries)} entries...")

    for particle_id, entry in entries.items():
        save_particle_entry(particle_id, entry, entries_dir, args.test)

    # Create master index
    create_master_index(entries, master_index, args.test)

    if args.test:
        print(f"\nTest mode: Would create {len(entries)} Hebrew prefix entries")
        print("Run without --test to actually create the files")
    else:
        print(f"\nSuccessfully created {len(entries)} Hebrew prefix entries")
        if len(entries) != 7:
            print(f"Warning: Expected 7 entries, created {len(entries)}")

if __name__ == '__main__':
    main()