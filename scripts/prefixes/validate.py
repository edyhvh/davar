#!/usr/bin/env python3
"""
Particle Dictionary System Validator

Validates particle system integrity and generates coverage reports.

Usage:
    python scripts/particles/validate.py [--test] [--verbose] [--book BOOK]

Options:
    --test      Test mode: validate only Genesis
    --verbose   Verbose output with detailed issues
    --book BOOK Validate specific book (e.g., 'genesis', 'exodus')
"""

import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

# Valid Hebrew prefix IDs (inseparable prefixes only)
VALID_PREFIX_IDS = {
    'Hb', 'Hd', 'Hc', 'Hl', 'Hm', 'Hk', 'Ht'
}

def validate_prefix_entries(entries_dir):
    """Validate Hebrew prefix dictionary entries"""
    issues = []
    entries = {}

    if not os.path.exists(entries_dir):
        issues.append(f"Entries directory not found: {entries_dir}")
        return entries, issues

    entry_files = list(Path(entries_dir).glob("*.json"))

    if len(entry_files) != 7:
        issues.append(f"Expected 7 prefix entries, found {len(entry_files)}")

    for entry_file in entry_files:
        try:
            with open(entry_file, 'r', encoding='utf-8') as f:
                entry = json.load(f)

            prefix_id = entry.get('id')
            if not prefix_id:
                issues.append(f"Entry {entry_file.name} missing 'id' field")
                continue

            if prefix_id not in VALID_PREFIX_IDS:
                issues.append(f"Invalid prefix ID '{prefix_id}' in {entry_file.name}")

            entries[prefix_id] = entry

        except Exception as e:
            issues.append(f"Error reading {entry_file}: {e}")

    return entries, issues

def validate_oe_file(file_path, particle_entries, verbose=False):
    """Validate a single OE file"""
    issues = []
    stats = {
        'words_checked': 0,
        'words_with_particles': 0,
        'missing_particles': 0,
        'invalid_particle_ids': 0,
        'orphaned_particles': 0  # Words with particles but no particle lemma
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            verses = json.load(f)

        for verse in verses:
            for word in verse.get('words', []):
                stats['words_checked'] += 1
                lemma = word.get('lemma', '')
                particles = word.get('prefixes', [])

                # Check if lemma contains any of our tracked particles
                lemma_parts = lemma.split('/')
                has_prefix_lemma = any(
                    part in VALID_PREFIX_IDS
                    for part in lemma_parts
                )

                if particles:
                    stats['words_with_particles'] += 1

                    # Check if prefixes field is valid
                    if not isinstance(particles, list):
                        issues.append(f"Non-list prefixes field in {file_path}: {particles}")
                        continue

                    for pid in particles:
                        if pid not in VALID_PREFIX_IDS:
                            issues.append(f"Invalid prefix ID '{pid}' in {file_path}")
                            stats['invalid_particle_ids'] += 1

                    # Check for orphaned prefixes (prefixes but no prefix lemma)
                    if not has_prefix_lemma:
                        if verbose:
                            issues.append(f"Orphaned prefixes in {file_path}: {word}")
                        stats['orphaned_particles'] += 1

                # Check for missing prefixes (prefix lemma but no prefixes field)
                elif has_prefix_lemma:
                    issues.append(f"Missing prefixes field for lemma '{lemma}' in {file_path}")
                    stats['missing_particles'] += 1

    except Exception as e:
        issues.append(f"Error validating {file_path}: {e}")

    return stats, issues

def validate_forms_lookup(lookup_path, particle_entries):
    """Validate forms_lookup.json"""
    issues = []

    if not os.path.exists(lookup_path):
        issues.append(f"Forms lookup not found: {lookup_path}")
        return issues

    try:
        with open(lookup_path, 'r', encoding='utf-8') as f:
            lookup = json.load(f)

        # Check that all forms point to valid particle IDs
        for form, particle_ids in lookup.items():
            for pid in particle_ids:
                if pid not in VALID_PREFIX_IDS:
                    issues.append(f"Invalid particle ID '{pid}' for form '{form}' in lookup")

        # Check coverage: forms in entries should be in lookup
        for pid, entry in particle_entries.items():
            for form in entry.get('forms', []):
                if form not in lookup:
                    issues.append(f"Form '{form}' for {pid} not found in lookup")

    except Exception as e:
        issues.append(f"Error validating forms lookup: {e}")

    return issues

def generate_report(particle_issues, oe_stats, oe_issues, lookup_issues, test_mode=False):
    """Generate validation report"""
    print("=== Hebrew Prefix Dictionary Validation Report ===")

    # Prefix entries
    print("\n1. Hebrew Prefix Dictionary Entries:")
    if particle_issues:
        for issue in particle_issues:
            print(f"  ERROR: {issue}")
    else:
        print("  ✓ All entries valid")

    # OE validation
    print("\n2. OE Files Validation:")
    print(f"  Words checked: {oe_stats['words_checked']}")
    print(f"  Words with prefixes: {oe_stats['words_with_particles']}")
    print(f"  Missing prefixes: {oe_stats['missing_particles']}")
    print(f"  Invalid prefix IDs: {oe_stats['invalid_particle_ids']}")
    print(f"  Orphaned prefixes: {oe_stats['orphaned_particles']}")

    if oe_stats['words_checked'] > 0:
        coverage = (oe_stats['words_with_particles'] / oe_stats['words_checked']) * 100
        print(f"  Coverage: {coverage:.1f}%")
    if oe_issues:
        print(f"  Issues found: {len(oe_issues)}")
        if test_mode:
            # Show first few issues in test mode
            for issue in oe_issues[:5]:
                print(f"    {issue}")
            if len(oe_issues) > 5:
                print(f"    ... and {len(oe_issues) - 5} more")
    else:
        print("  ✓ No OE validation issues")

    # Forms lookup
    print("\n3. Forms Lookup Validation:")
    if lookup_issues:
        for issue in lookup_issues:
            print(f"  ERROR: {issue}")
    else:
        print("  ✓ Forms lookup valid")

    # Overall status
    all_issues = particle_issues + oe_issues + lookup_issues
    print("\n4. Overall Status:")
    if all_issues:
        print(f"  ⚠️  {len(all_issues)} issues found")
        return False
    else:
        print("  ✅ All validations passed")
        return True

def get_oe_files(test_mode=False, book=None):
    """Get list of OE files to validate"""
    if test_mode:
        script_dir = os.path.dirname(__file__)
        pattern = os.path.join(script_dir, '..', '..', 'data', 'oe', 'genesis', '*.json')
        files = glob.glob(pattern)
    elif book:
        pattern = f"data/oe/{book.lower()}/*.json"
        files = glob.glob(pattern, recursive=True)
    else:
        pattern = "data/oe/**/*.json"
        files = glob.glob(pattern, recursive=True)
    
    # Exclude raw directory (different data structure)
    files = [f for f in files if '/raw/' not in f]
    return sorted(files)

def main():
    parser = argparse.ArgumentParser(description='Validate Hebrew prefix dictionary system')
    parser.add_argument('--test', action='store_true', help='Test mode - validate only Genesis')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--book', help='Validate specific book (e.g., genesis, exodus)')
    args = parser.parse_args()

    # Validate particle entries
    script_dir = os.path.dirname(__file__)
    entries_dir = Path(os.path.join(script_dir, '..', '..', 'data', 'dict', 'prefixes', 'entries'))
    prefix_entries, particle_issues = validate_prefix_entries(entries_dir)

    # Validate forms lookup
    lookup_path = Path(os.path.join(script_dir, '..', '..', 'data', 'dict', 'prefixes', 'forms_lookup.json'))
    lookup_issues = validate_forms_lookup(lookup_path, prefix_entries)

    # Validate OE files
    oe_files = get_oe_files(args.test, args.book)
    total_oe_stats = {
        'words_checked': 0,
        'words_with_particles': 0,
        'missing_particles': 0,
        'invalid_particle_ids': 0,
        'orphaned_particles': 0
    }
    all_oe_issues = []

    if oe_files:
        print(f"Validating {len(oe_files)} OE files..." if not args.test else f"Validating {len(oe_files)} test files...")

        for i, file_path in enumerate(oe_files):
            if args.verbose and (i % 100 == 0 or i == len(oe_files) - 1):
                print(f"  [{i+1}/{len(oe_files)}] {file_path}")

            file_stats, file_issues = validate_oe_file(file_path, prefix_entries, args.verbose)
            all_oe_issues.extend(file_issues)

            for key in total_oe_stats:
                total_oe_stats[key] += file_stats[key]

    # Generate report
    success = generate_report(particle_issues, total_oe_stats, all_oe_issues, lookup_issues, args.test)

    if not success:
        print("\nValidation failed - check issues above")
        sys.exit(1)
    else:
        print("\nValidation successful!")

if __name__ == '__main__':
    main()