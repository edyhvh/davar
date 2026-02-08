#!/usr/bin/env python3
"""
XML parsing utilities for DSS and WLC files
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple


def parse_dss_book(book_file) -> List[Dict]:
    """
    Parse a DSS book file to extract variants.
    
    Args:
        book_file: Path to DSS XML file
        
    Returns:
        List of verse data with variants
    """
    print(f"Parsing DSS book: {book_file.name}")
    
    tree = ET.parse(book_file)
    root = tree.getroot()
    
    variants_data = []
    
    # Find all chapters
    for chapter in root.findall('.//cn'):
        chapter_num = chapter.get('n')
        
        # Skip non-numeric chapters (metadata, etc.)
        if not chapter_num:
            continue
        try:
            chapter_int = int(chapter_num)
        except (ValueError, TypeError):
            continue
        
        # Find all verses
        for verse in chapter.findall('.//vn'):
            verse_num = verse.get('n')
            
            # Skip non-numeric verses
            if not verse_num:
                continue
            try:
                verse_int = int(verse_num)
            except (ValueError, TypeError):
                continue
            
            # Collect all words including variants
            # DSS XML has 3 variant types: <w>, <group>, and <note>
            dss_words = []
            variant_positions = []
            
            # Build word list with position tracking
            all_words = verse.findall('.//w')
            for word_elem in all_words:
                word_text = word_elem.text or ''
                dss_words.append(word_text)
            
            # Now find variants - check different element types
            word_position = 0
            
            # 1. Find individual word variants
            for word_elem in all_words:
                word_position += 1
                if word_elem.get('variant') == 'yes':
                    variant_id = word_elem.get('id', '')
                    word_text = word_elem.text or ''
                    
                    # Check if this word is part of a group variant
                    parent = None
                    for group in verse.findall('.//group'):
                        if word_elem in group.findall('.//w'):
                            parent = group
                            break
                    
                    # Only add if not part of a group variant (will be handled separately)
                    if parent is None or parent.get('variant') != 'yes':
                        variant_positions.append({
                            'position': word_position,
                            'word': word_text,
                            'variant_id': variant_id
                        })
            
            # 2. Find group variants (multiple words with shared variant)
            for group_elem in verse.findall('.//group'):
                if group_elem.get('variant') == 'yes':
                    variant_id = group_elem.get('id', '')
                    group_words = []
                    group_position = None
                    
                    # Find position of first word in group
                    for idx, word_elem in enumerate(all_words, 1):
                        if word_elem in group_elem.findall('.//w'):
                            if group_position is None:
                                group_position = idx
                            group_words.append(word_elem.text or '')
                    
                    if group_words and group_position:
                        variant_positions.append({
                            'position': group_position,
                            'word': ' '.join(group_words),
                            'variant_id': variant_id
                        })
            
            # 3. Find note variants (structural differences like omissions)
            for note_elem in verse.findall('.//note'):
                if note_elem.get('variant') == 'yes':
                    variant_id = note_elem.get('id', '')
                    note_text = note_elem.text or 'note'
                    
                    # Use position 1 as default for structural notes
                    variant_positions.append({
                        'position': 1,
                        'word': note_text,
                        'variant_id': variant_id
                    })
            
            if variant_positions:
                variants_data.append({
                    'chapter': chapter_int,
                    'verse': verse_int,
                    'dss_text': ' '.join(dss_words),
                    'variants': variant_positions
                })
    
    return variants_data


def parse_wlc_book(book_file) -> Dict[Tuple[int, int], Dict]:
    """
    Parse a WLC (Masoretic) book file.
    
    Args:
        book_file: Path to WLC XML file
        
    Returns:
        Dictionary mapping (chapter, verse) to verse data
    """
    print(f"Parsing WLC book: {book_file.name}")
    
    tree = ET.parse(book_file)
    root = tree.getroot()
    
    masoretic_data = {}
    
    # Find all chapters
    for chapter in root.findall('.//{*}c'):
        chapter_num = chapter.get('n')
        
        # Skip non-numeric chapters
        if not chapter_num:
            continue
        try:
            chapter_int = int(chapter_num)
        except (ValueError, TypeError):
            continue
        
        # Find all verses
        for verse in chapter.findall('.//{*}v'):
            verse_num = verse.get('n')
            
            # Skip non-numeric verses
            if not verse_num:
                continue
            try:
                verse_int = int(verse_num)
            except (ValueError, TypeError):
                continue
            
            # Collect all words
            words = []
            for word in verse.findall('.//{*}w'):
                word_text = word.text or ''
                words.append(word_text)
            
            key = (chapter_int, verse_int)
            masoretic_data[key] = {
                'text': ' '.join(words),
                'words': words
            }
    
    return masoretic_data
