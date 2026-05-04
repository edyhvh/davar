#!/usr/bin/env python3
"""
Apply corrections from Moriah and Lena to Hutter Hebrew text files.

This script reads correction data from CSV files and applies them to the
original book JSON files in output/, then writes updated versions to output/temp/.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any


def load_corrections() -> Tuple[Dict[str, List[Dict]], Dict[str, List[Dict]]]:
    """
    Load corrections from both Moriah and Lena CSV files.

    Returns:
        Tuple of (moriah_corrections, lena_corrections) where each is a dict
        mapping book_name to list of correction records.
    """
    moriah_corrections = {}
    lena_corrections = {}

    # Load Moriah corrections
    with open(Path(__file__).parents[2] / 'data' / 'review' / 'hutter_moriah.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            book = row['book']
            if book not in moriah_corrections:
                moriah_corrections[book] = []
            moriah_corrections[book].append({
                'chapter': int(row['chapter']),
                'verse': int(row['verse']),
                'corrected_text': row['corrected_text'],
                'reviewer': 'moriah'
            })

    # Load Lena corrections
    with open(Path(__file__).parents[2] / 'data' / 'review' / 'hutter_lena.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            book = row['book']
            if book not in lena_corrections:
                lena_corrections[book] = []
            lena_corrections[book].append({
                'chapter': int(row['chapter']),
                'verse': int(row['verse']),
                'corrected_text': row['corrected_text'],
                'reviewer': 'lena'
            })

    return moriah_corrections, lena_corrections


def load_book(book_name: str) -> Dict[str, Any]:
    """
    Load a book JSON file from the output directory.

    Args:
        book_name: Name of the book (without .json extension)

    Returns:
        The book data as a dictionary
    """
    book_path = Path(__file__).parents[2] / 'output' / f'{book_name}.json'
    with open(book_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def apply_corrections(book: Dict[str, Any], corrections: Dict[str, List[Dict]]) -> bool:
    """
    Apply corrections to a book's verses.

    Args:
        book: The book dictionary to modify
        corrections: Dictionary mapping book names to correction lists

    Returns:
        True if any corrections were applied, False otherwise
    """
    book_name = book['book_name']
    if book_name not in corrections:
        return False

    corrections_applied = False
    book_corrections = corrections[book_name]

    # Create a lookup map for faster access
    correction_map = {}
    for correction in book_corrections:
        key = (correction['chapter'], correction['verse'])
        correction_map[key] = correction

    # Apply corrections to chapters and verses
    for chapter in book['chapters']:
        for verse in chapter['verses']:
            key = (chapter['number'], verse['number'])
            if key in correction_map:
                correction = correction_map[key]
                verse['text_nikud'] = correction['corrected_text']
                verse['manually_corrected'] = True

                # For Lena corrections, also mark for nikud review
                if correction['reviewer'] == 'lena':
                    verse['needs_nikud_review'] = True

                corrections_applied = True

    return corrections_applied


def save_updated_book(book: Dict[str, Any], output_dir: Path) -> None:
    """
    Save the updated book to the output/temp directory.

    Args:
        book: The book dictionary to save
        output_dir: The output directory path
    """
    output_dir.mkdir(exist_ok=True)
    book_name = book['book_name']
    output_path = output_dir / f'{book_name}.json'

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(book, f, ensure_ascii=False, indent=2)


def main():
    """Main entry point for the script."""
    if len(sys.argv) != 1:
        print("Usage: python apply_corrections.py", file=sys.stderr)
        sys.exit(1)

    # Load corrections
    print("Loading corrections...")
    moriah_corrections, lena_corrections = load_corrections()

    # Combine corrections
    all_corrections = {}
    for book, corrections in moriah_corrections.items():
        all_corrections[book] = corrections
    for book, corrections in lena_corrections.items():
        if book in all_corrections:
            all_corrections[book].extend(corrections)
        else:
            all_corrections[book] = corrections

    print(f"Found corrections for {len(all_corrections)} books")

    # Get output directory
    output_dir = Path(__file__).parents[2] / 'output' / 'temp'

    # Process each book that has corrections
    books_processed = 0
    for book_name in all_corrections.keys():
        try:
            print(f"Processing {book_name}...")
            book = load_book(book_name)
            corrections_applied = apply_corrections(book, all_corrections)
            if corrections_applied:
                save_updated_book(book, output_dir)
                books_processed += 1
                print(f"  Applied corrections and saved to {output_dir}/{book_name}.json")
            else:
                print(f"  No corrections applied to {book_name}")
        except FileNotFoundError:
            print(f"  Warning: Book file {book_name}.json not found, skipping")
        except Exception as e:
            print(f"  Error processing {book_name}: {e}", file=sys.stderr)

    print(f"\nCompleted! Processed {books_processed} books with corrections.")


if __name__ == '__main__':
    main()