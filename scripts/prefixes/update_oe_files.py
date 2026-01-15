#!/usr/bin/env python3
"""
Particle Dictionary OE Files Updater

Adds particles array field to OE word objects based on lemma prefixes.

Usage:
    python scripts/particles/update_oe_files.py [--test] [--dry-run] [--verbose] [--book BOOK]

Options:
    --test      Test mode: update only Genesis 1
    --dry-run   Show what would change without writing files
    --verbose   Verbose output with progress details
    --book BOOK Update specific book (e.g., 'genesis', 'exodus')
"""

import argparse
import glob
import json
import os
import shutil
import sys
from pathlib import Path

# Inseparable Hebrew prefixes (only these - no standalone particles)
HEBREW_PREFIXES = {'Hb', 'Hd', 'Hc', 'Hl', 'Hm', 'Hk', 'Ht'}

def extract_prefix_ids(lemma):
    """Extract Hebrew prefix IDs from lemma field"""
    if not lemma:
        return []

    parts = lemma.split('/')
    prefixes = []

    for part in parts:
        if part.startswith('H') and len(part) == 2 and part in HEBREW_PREFIXES:
            prefixes.append(part)

    return prefixes

def update_oe_file(file_path, dry_run=False, verbose=False):
    """Update a single OE file with particles field"""
    modified = False
    stats = {
        'words_processed': 0,
        'particles_added': 0,
        'words_with_particles': 0
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            verses = json.load(f)

        if verbose:
            print(f"Processing {file_path}: {len(verses)} verses")

        for verse in verses:
            for word in verse.get('words', []):
                stats['words_processed'] += 1
                lemma = word.get('lemma', '')

                if not lemma:
                    continue

                particles = extract_prefix_ids(lemma)

                # Handle migration from 'particles' to 'prefixes' field
                if 'particles' in word and 'prefixes' not in word:
                    # Migrate old 'particles' field to 'prefixes'
                    word['prefixes'] = word.pop('particles')
                    modified = True
                    stats['particles_added'] += 1  # Count as migration

                if particles:
                    # Only add prefixes field if not already present
                    if 'prefixes' not in word:
                        word['prefixes'] = particles
                        modified = True
                        stats['particles_added'] += 1

                    stats['words_with_particles'] += 1

                # Also check for existing prefixes field consistency
                elif 'prefixes' in word:
                    if verbose:
                        print(f"Warning: Word has prefixes field but no prefix lemma: {word}")

        if modified and not dry_run:
            # Create backup
            backup_path = f"{file_path}.backup"
            shutil.copy2(file_path, backup_path)

            # Write updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(verses, f, indent=2, ensure_ascii=False)
                f.write('\n')

            if verbose:
                print(f"Updated {file_path} (backup: {backup_path})")

        return modified, stats

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, stats

def get_oe_files(test_mode=False, book=None):
    """Get list of OE files to update"""
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
    parser = argparse.ArgumentParser(description='Update OE files with prefixes field')
    parser.add_argument('--test', action='store_true', help='Test mode - update only Genesis 1')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without writing files')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--book', help='Update specific book (e.g., genesis, exodus)')
    args = parser.parse_args()

    # Get files to update
    oe_files = get_oe_files(args.test, args.book)

    if not oe_files:
        print("No OE files found to update")
        sys.exit(1)

    if args.verbose or args.dry_run:
        print(f"Processing {len(oe_files)} OE files...")

    # Process files
    total_stats = {
        'files_processed': 0,
        'files_modified': 0,
        'words_processed': 0,
        'particles_added': 0,
        'words_with_particles': 0
    }

    for i, file_path in enumerate(oe_files):
        if args.verbose and (i % 50 == 0 or i == len(oe_files) - 1):
            print(f"  [{i+1}/{len(oe_files)}] Processing {file_path}")

        modified, file_stats = update_oe_file(file_path, args.dry_run, args.verbose)

        total_stats['files_processed'] += 1
        if modified:
            total_stats['files_modified'] += 1

        for key in ['words_processed', 'particles_added', 'words_with_particles']:
            total_stats[key] += file_stats[key]

    # Print summary
    print("\nUpdate Summary:")
    print(f"  Files processed: {total_stats['files_processed']}")
    print(f"  Files modified: {total_stats['files_modified']}")
    print(f"  Words processed: {total_stats['words_processed']}")
    print(f"  Prefixes added: {total_stats['particles_added']}")
    print(f"  Words with prefixes: {total_stats['words_with_particles']}")

    if total_stats['words_processed'] > 0:
        coverage = (total_stats['words_with_particles'] / total_stats['words_processed']) * 100
        print(f"  Coverage: {coverage:.1f}%")
    if args.dry_run:
        print("\nDry run complete - no files modified")
    else:
        print(f"\nUpdate complete - {total_stats['files_modified']} files modified")

if __name__ == '__main__':
    main()