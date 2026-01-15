#!/usr/bin/env python3
"""
Particle Dictionary OE Forms Scanner

Scans OE JSON files to discover particle forms and calculate frequencies.
Updates particle dictionary entries with discovered forms.

Usage:
    python scripts/particles/scan_oe_forms.py [--test] [--dry-run] [--verbose] [--book BOOK]

Options:
    --test      Test mode: scan only Genesis 1
    --dry-run   Show what would change without writing files
    --verbose   Verbose output with progress details
    --book BOOK Scan specific book (e.g., 'genesis', 'exodus')
"""

import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

# Inseparable Hebrew prefixes (only these - no standalone particles)
HEBREW_PREFIXES = {'Hb', 'Hd', 'Hc', 'Hl', 'Hm', 'Hk', 'Ht'}

def extract_particle_ids(lemma):
    """Extract particle IDs from lemma field"""
    if not lemma:
        return []

    parts = lemma.split('/')
    particles = []

    for part in parts:
        if part.startswith('H') and len(part) == 2 and part in HEBREW_PREFIXES:
            particles.append(part)

    return particles

def extract_form_for_prefix(text, prefix_id, lemma_parts):
    """
    Extract the form for a specific Hebrew prefix from text.

    For text like "וְ/הָ/אָ֗רֶץ" with lemma "Hc/Hd/H776":
    - Hc maps to first part "וְ"
    - Hd maps to second part "הָ"
    """
    if not text or not lemma_parts:
        return ""

    text_parts = text.split('/')
    lemma_prefixes = lemma_parts

    # Find the position of our prefix in lemma
    try:
        pos = lemma_prefixes.index(prefix_id)
        if pos < len(text_parts):
            return text_parts[pos]
    except (ValueError, IndexError):
        pass

    return ""

def scan_oe_file(file_path, verbose=False):
    """Scan a single OE file and return form counts"""
    form_counts = defaultdict(lambda: defaultdict(int))

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            verses = json.load(f)

        if verbose:
            print(f"Scanning {file_path}: {len(verses)} verses")

        for verse in verses:
            for word in verse.get('words', []):
                lemma = word.get('lemma', '')
                text = word.get('text', '')

                if not lemma or not text:
                    continue

                lemma_parts = lemma.split('/')
                prefixes = extract_prefix_ids(lemma)

                for prefix_id in prefixes:
                    form = extract_form_for_prefix(text, prefix_id, lemma_parts)
                    if form:
                        form_counts[particle_id][form] += 1

    except Exception as e:
        print(f"Error scanning {file_path}: {e}")

    return form_counts

def merge_form_counts(counts_list):
    """Merge multiple form count dictionaries"""
    merged = defaultdict(lambda: defaultdict(int))

    for counts in counts_list:
        for particle_id, forms in counts.items():
            for form, count in forms.items():
                merged[particle_id][form] += count

    return merged

def update_prefix_entries(form_counts, entries_dir, dry_run=False, verbose=False):
    """Update prefix entries with discovered forms and frequencies"""
    updated_count = 0

    for particle_id, forms_dict in form_counts.items():
        entry_path = os.path.join(entries_dir, f"{particle_id}.json")

        if not os.path.exists(entry_path):
            if verbose:
                print(f"Warning: Entry not found: {entry_path}")
            continue

        try:
            with open(entry_path, 'r', encoding='utf-8') as f:
                entry = json.load(f)

            # Calculate total frequency
            total_freq = sum(forms_dict.values())

            # Get all discovered forms
            discovered_forms = list(forms_dict.keys())

            # Merge with existing forms
            existing_forms = entry.get('forms', [])
            all_forms = list(set(existing_forms + discovered_forms))

            if dry_run:
                print(f"Would update {particle_id}:")
                print(f"  Forms: {existing_forms} → {all_forms}")
                print(f"  Frequency: {entry.get('frequency', 0)} → {total_freq}")
                continue

            # Update entry
            entry['forms'] = all_forms
            entry['frequency'] = total_freq

            # Save updated entry
            with open(entry_path, 'w', encoding='utf-8') as f:
                json.dump(entry, f, indent=2, ensure_ascii=False)
                f.write('\n')

            updated_count += 1
            if verbose:
                print(f"Updated {prefix_id}: {len(discovered_forms)} forms, {total_freq} total")

        except Exception as e:
            print(f"Error updating {entry_path}: {e}")

    return updated_count

def create_forms_lookup(form_counts, entries_dir, output_path, dry_run=False):
    """Create forms_lookup.json with CSV baseline + discovered forms"""
    lookup = defaultdict(list)

    # 1. Add forms discovered from OE scan
    for prefix_id, forms_dict in form_counts.items():
        for form in forms_dict.keys():
            if prefix_id not in lookup[form]:
                lookup[form].append(prefix_id)

    # 2. Add baseline forms from CSV (prefix entries)
    if os.path.exists(entries_dir):
        for entry_file in Path(entries_dir).glob("*.json"):
            try:
                with open(entry_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                    prefix_id = entry.get('id')
                    for form in entry.get('forms', []):
                        if prefix_id not in lookup[form]:
                            lookup[form].append(prefix_id)
            except Exception as e:
                print(f"Warning: Could not read {entry_file}: {e}")

    # Convert to regular dict for JSON serialization
    lookup_dict = {form: ids for form, ids in lookup.items()}

    if dry_run:
        print(f"Would create forms lookup: {output_path}")
        print(f"Total forms: {len(lookup_dict)}")
        print(f"Sample entries: {dict(list(lookup_dict.items())[:5])}")
        return

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(lookup_dict, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"Created forms lookup: {output_path} ({len(lookup_dict)} forms)")

def get_oe_files(test_mode=False, book=None):
    """Get list of OE files to scan"""
    if test_mode:
        return [os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'oe', 'genesis', '1.json')]

    script_dir = os.path.dirname(__file__)
    if book:
        pattern = os.path.join(script_dir, '..', '..', 'data', 'oe', book.lower(), '*.json')
    else:
        pattern = os.path.join(script_dir, '..', '..', 'data', 'oe', '**', '*.json')

    files = glob.glob(pattern, recursive=True)
    # Exclude raw directory (different data structure)
    files = [f for f in files if '/raw/' not in f]
    return sorted(files)

def main():
    parser = argparse.ArgumentParser(description='Scan OE files for Hebrew prefix forms')
    parser.add_argument('--test', action='store_true', help='Test mode - scan only Genesis 1')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without writing files')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--book', help='Scan specific book (e.g., genesis, exodus)')
    args = parser.parse_args()

    # Get files to scan
    oe_files = get_oe_files(args.test, args.book)

    if not oe_files:
        print("No OE files found to scan")
        sys.exit(1)

    if args.verbose:
        print(f"Scanning {len(oe_files)} OE files...")

    # Scan files
    all_counts = []
    for i, file_path in enumerate(oe_files):
        if args.verbose and (i % 10 == 0 or i == len(oe_files) - 1):
            print(f"  [{i+1}/{len(oe_files)}] Scanning {file_path}")

        counts = scan_oe_file(file_path, args.verbose)
        all_counts.append(counts)

    # Merge all counts
    form_counts = merge_form_counts(all_counts)

    # Summary
    total_forms = sum(len(forms) for forms in form_counts.values())
    total_occurrences = sum(sum(forms.values()) for forms in form_counts.values())

    print("\nScan Summary:")
    print(f"  Files scanned: {len(oe_files)}")
    print(f"  Particle types: {len(form_counts)}")
    print(f"  Total forms found: {total_forms}")
    print(f"  Total occurrences: {total_occurrences}")

    if args.verbose:
        for particle_id, forms in sorted(form_counts.items()):
            print(f"  {particle_id}: {len(forms)} forms, {sum(forms.values())} total")

    # Update prefix entries
    script_dir = os.path.dirname(__file__)
    entries_dir = Path(os.path.join(script_dir, '..', '..', 'data', 'dict', 'prefixes', 'entries'))
    if entries_dir.exists():
        updated = update_prefix_entries(form_counts, entries_dir, args.dry_run, args.verbose)
        if not args.dry_run:
            print(f"Updated {updated} prefix entries")
    else:
        print(f"Warning: Entries directory not found: {entries_dir}")

    # Create forms lookup
    lookup_path = Path(os.path.join(script_dir, '..', '..', 'data', 'dict', 'prefixes', 'forms_lookup.json'))
    create_forms_lookup(form_counts, entries_dir, lookup_path, args.dry_run)

    if args.dry_run:
        print("\nDry run complete - no files modified")
    else:
        print("\nScan complete - particle entries updated")

if __name__ == '__main__':
    main()