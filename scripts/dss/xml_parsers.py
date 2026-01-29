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
            dss_words = []
            variant_positions = []
            
            for i, word in enumerate(verse.findall('.//w')):
                word_text = word.text or ''
                is_variant = word.get('variant') == 'yes'
                variant_id = word.get('id', '')
                
                dss_words.append(word_text)
                
                if is_variant:
                    variant_positions.append({
                        'position': i + 1,
                        'word': word_text,
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
