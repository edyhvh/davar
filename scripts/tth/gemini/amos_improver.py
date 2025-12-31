#!/usr/bin/env python3
"""
Script to improve the amos.json file by:
1. Removing duplicated book_info fields from verses
2. Adding missing section titles
3. Adding useful fields like book_english_name_lower
4. Adding input_file and source_file to book_info
"""

import json
import sys
from pathlib import Path

def improve_amos_json():
    # Load the current temp file
    temp_file = Path(__file__).parent.parent.parent / "data" / "tth" / "temp" / "amos.json"

    if not temp_file.exists():
        print(f"Error: {temp_file} not found")
        return False

    with open(temp_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data['verses'])} verses from {temp_file}")

    # Update book_info with additional metadata
    data['book_info'].update({
        'input_file': 'tanaj/amos.md',
        'source_file': 'tanaj/amos.md'
    })

    # Define section titles based on the draft and source file
    section_titles = {
        # Chapter 1
        (1, 1): "Juicio contra las naciones",
        # Chapters 2-3 (verses that have titles)
        (2, 4): "Juicio contra Iehudáh e Israel",
        (3, 1): "Castigo de los hijos de Israel",
        # Chapter 5
        (5, 1): "Llamado a regresar a יהוה",
        # Chapter 6
        (6, 1): "Profecía contra el orgullo de Israel",
        # Chapter 7
        (7, 1): "La langosta, el fuego y la plomada",
        (7, 10): "Amós es acusado por Amatziáh",
        # Chapter 8
        (8, 1): "Los juicios de Elohim",
        # Chapter 9
        (9, 11): "Restauración de Israel"
    }

    # Fields to remove from each verse (duplicated book info)
    fields_to_remove = [
        'book_tth_name', 'book_hebrew_name', 'book_english_name', 'book_spanish_name',
        'section', 'section_hebrew', 'section_english', 'section_spanish'
    ]

    # Process each verse
    for verse in data['verses']:
        # Remove duplicated fields
        for field in fields_to_remove:
            verse.pop(field, None)

        # Add book_english_name_lower
        verse['book_english_name_lower'] = 'amos'

        # Add title if it exists for this verse
        key = (verse['chapter'], verse['verse'])
        if key in section_titles:
            verse['title'] = section_titles[key]

    # Save the improved version
    output_file = temp_file.parent / "amos_improved.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved improved version to {output_file}")
    print(f"Removed duplicated fields: {fields_to_remove}")
    print(f"Added {len(section_titles)} section titles")
    print("Added book_english_name_lower to all verses")
    print("Added input_file and source_file to book_info")

    return True

if __name__ == "__main__":
    success = improve_amos_json()
    sys.exit(0 if success else 1)
