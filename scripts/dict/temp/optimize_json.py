#!/usr/bin/env python3
"""
JSON Optimization Script

Minifies JSON files to reduce file size for production use while maintaining data integrity.
Creates both pretty-printed (.json) and minified (.min.json) versions.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
import argparse


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return {}


def optimize_json_file(input_file: Path, output_file: Path, minify: bool = True) -> bool:
    """
    Optimize a JSON file by either pretty-printing or minifying it.

    Args:
        input_file: Source JSON file
        output_file: Target optimized file
        minify: If True, create minified version; if False, create pretty-printed version

    Returns:
        True if successful, False otherwise
    """
    # Load the data
    data = load_json_file(input_file)
    if not data:
        return False

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            if minify:
                # Minified JSON (compact)
                json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            else:
                # Pretty-printed JSON
                json.dump(data, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(f"❌ Error optimizing {input_file}: {e}")
        return False


def get_file_sizes(file_path: Path) -> tuple[int, str]:
    """Get file size in bytes and human-readable format."""
    if not file_path.exists():
        return 0, "0 B"

    size_bytes = file_path.stat().st_size

    # Convert to human readable
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return size_bytes, f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0

    return int(size_bytes * 1024), f"{size_bytes:.1f} GB"


def main():
    parser = argparse.ArgumentParser(description='Optimize JSON files for production')
    parser.add_argument('--minify', action='store_true', help='Create minified versions')
    parser.add_argument('--pretty', action='store_true', help='Create pretty-printed versions')
    parser.add_argument('--file', help='Process only specific file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    if not args.minify and not args.pretty:
        print("❌ Must specify either --minify or --pretty")
        sys.exit(1)

    print("=" * 70)
    print("JSON OPTIMIZATION SCRIPT")
    print("=" * 70)

    # Define paths
    script_dir = Path(__file__).parent.parent.parent.parent  # scripts/dict/temp -> davar
    data_dir = script_dir / 'data' / 'dict'

    # Files to optimize
    files_to_optimize = [
        data_dir / 'lexicon' / 'roots.json',
        data_dir / 'lexicon' / 'words.json',
    ]

    # Add all book files
    books_dir = data_dir / 'books'
    if books_dir.exists():
        files_to_optimize.extend(books_dir.glob('*.json'))

    # Filter to specific file if requested
    if args.file:
        target_file = Path(args.file)
        if target_file.exists():
            files_to_optimize = [target_file]
        else:
            print(f"❌ File not found: {target_file}")
            sys.exit(1)

    print(f"📁 Data directory: {data_dir}")
    print(f"📄 Files to process: {len(files_to_optimize)}")
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()

    total_original_size = 0
    total_optimized_size = 0
    processed_count = 0

    for input_file in files_to_optimize:
        if not input_file.exists():
            print(f"⚠️  File not found, skipping: {input_file}")
            continue

        original_size, original_size_str = get_file_sizes(input_file)

        if args.minify:
            output_file = input_file.with_suffix('.min.json')
            operation = "minifying"
        else:
            output_file = input_file.with_suffix('.pretty.json')
            operation = "pretty-printing"

        print(f"🔄 {operation}: {input_file.name}")

        if args.dry_run:
            print(f"  📊 Original size: {original_size_str}")
            print(f"  🎯 Would create: {output_file.name}")
            continue

        # Perform optimization
        if optimize_json_file(input_file, output_file, minify=args.minify):
            optimized_size, optimized_size_str = get_file_sizes(output_file)

            # Calculate compression ratio
            if args.minify:
                ratio = ((original_size - optimized_size) / original_size) * 100 if original_size > 0 else 0
                print(f"  ✅ Minified: {original_size_str} → {optimized_size_str} ({ratio:.1f}% reduction)")
            else:
                ratio = ((optimized_size - original_size) / original_size) * 100 if original_size > 0 else 0
                print(f"  ✅ Pretty-printed: {original_size_str} → {optimized_size_str} ({ratio:.1f}% increase)")

            total_original_size += original_size
            total_optimized_size += optimized_size
            processed_count += 1
        else:
            print(f"  ❌ Failed to optimize {input_file.name}")

        print()

    if args.dry_run:
        print(f"🔍 Would process {len(files_to_optimize)} files")
        return

    # Summary
    print("=" * 70)
    print("OPTIMIZATION SUMMARY")
    print("=" * 70)

    if processed_count > 0:
        print(f"✅ Files processed: {processed_count}")

        orig_total_str = f"{total_original_size:,} bytes"
        opt_total_str = f"{total_optimized_size:,} bytes"

        if args.minify:
            savings = total_original_size - total_optimized_size
            savings_str = f"{savings:,} bytes"
            ratio = (savings / total_original_size) * 100 if total_original_size > 0 else 0
            print(f"💾 Space saved: {savings_str} ({ratio:.1f}%)")
            print(f"📊 Total: {orig_total_str} → {opt_total_str}")
        else:
            increase = total_optimized_size - total_original_size
            increase_str = f"{increase:,} bytes"
            ratio = (increase / total_original_size) * 100 if total_original_size > 0 else 0
            print(f"📊 Size increase: {increase_str} ({ratio:.1f}%)")
            print(f"📊 Total: {orig_total_str} → {opt_total_str}")

        print()
        print("📋 Next steps:")
        if args.minify:
            print("  1. Test minified files for data integrity")
            print("  2. Replace original files with .min.json versions if desired")
            print("  3. Consider using minified versions in production")
        else:
            print("  1. Test pretty-printed files")
            print("  2. Use for development/debugging")
    else:
        print("❌ No files were processed")


if __name__ == '__main__':
    main()

