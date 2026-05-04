#!/usr/bin/env python3
"""
Create a JSON file listing all verses that need nikud review.

Extracts verses from Lena's corrections CSV that need manual nikud review.
"""

import csv
import json
from pathlib import Path


def create_nikud_review_list():
    """Create nikud_review_verses.json from Lena's corrections."""
    review_verses = []

    # Read Lena's corrections CSV
    lena_csv_path = Path(__file__).parents[2] / 'data' / 'review' / 'hutter_lena.csv'

    with open(lena_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            review_verses.append({
                'book': row['book'],
                'chapter': int(row['chapter']),
                'verse': int(row['verse']),
                'current_text': row['current_text'],
                'corrected_text': row['corrected_text'],
                'visual_uncertainty': row['uncertainties']
            })

    # Sort by book, chapter, verse for easier review
    review_verses.sort(key=lambda x: (x['book'], x['chapter'], x['verse']))

    # Write to JSON file
    output_path = Path(__file__).parents[2] / 'data' / 'review' / 'nikud_review_verses.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(review_verses, f, ensure_ascii=False, indent=2)

    print(f"Created {output_path} with {len(review_verses)} verses needing nikud review")

    # Print summary by book
    books = {}
    for verse in review_verses:
        book = verse['book']
        books[book] = books.get(book, 0) + 1

    print("\nVerses by book:")
    for book, count in books.items():
        print(f"  {book}: {count} verses")


if __name__ == '__main__':
    create_nikud_review_list()