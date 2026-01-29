#!/usr/bin/env python3
"""
Parser for DSS variant notes with Hebrew word extraction
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple


def parse_notes_file(notes_file) -> Dict[str, Dict]:
    """
    Parse the DSS notes file to extract variant commentaries with Hebrew words.
    
    Args:
        notes_file: Path to DSS_TC_Notes.xml
        
    Returns:
        Dictionary mapping variant IDs to note data
    """
    print("Parsing notes file...")
    notes = {}
    
    try:
        tree = ET.parse(notes_file)
        root = tree.getroot()
        
        for var in root.findall('.//var'):
            var_id = var.get('id', '')
            note_text = ''.join(var.itertext()).strip()
            
            # Clean up the text
            note_text = note_text.replace('&lt;', '<').replace('&gt;', '>')
            
            # Get the raw XML to extract varheb tags
            raw_xml = ET.tostring(var, encoding='unicode')
            
            # Extract all Hebrew words from <varheb> tags
            hebrew_words = re.findall(r'<varheb>(.*?)</varheb>', raw_xml)
            
            notes[var_id] = {
                'commentary': note_text,
                'hebrew_words': hebrew_words,
                'raw_xml': raw_xml
            }
            
        print(f"Parsed {len(notes)} variant notes")
    except Exception as e:
        print(f"Error parsing notes file: {e}")
        raise
    
    return notes


def extract_masoretic_dss_words(
    note_data: Optional[Dict], 
    dss_word_fallback: str
) -> Tuple[Optional[str], str]:
    """
    Extract Masoretic and DSS Hebrew words from note data using XML patterns.
    
    Args:
        note_data: Dictionary containing commentary, hebrew_words, and raw_xml
        dss_word_fallback: Fallback DSS word if extraction fails
        
    Returns:
        Tuple of (masoretic_word, dss_word)
    """
    if not note_data:
        return None, dss_word_fallback
    
    raw_xml = note_data['raw_xml']
    hebrew_words = note_data['hebrew_words']
    
    masoretic_word = None
    dss_word = dss_word_fallback
    
    # Patterns to find Masoretic text (case insensitive)
    mas_patterns = [
        r'(?:the\s+)?Masoretic\s+reads?\s+<varheb>(.*?)</varheb>',
        r'(?:and\s+)?(?:the\s+)?Masoretic\s+(?:have?\s+)?(?:the\s+)?(?:defective|plene)?\s*(?:spelling\s+)?<varheb>(.*?)</varheb>',
        r'Mas[:\s][^<]*<varheb>(.*?)</varheb>',
        r',\s*Mas[^\<]*<varheb>(.*?)</varheb>',
    ]
    
    # Try to extract Masoretic word
    for pattern in mas_patterns:
        match = re.search(pattern, raw_xml, re.IGNORECASE)
        if match:
            masoretic_word = match.group(1).strip()
            break
    
    # Patterns to find DSS text (scroll references)
    dss_patterns = [
        r'(?:4Q|1Q|2Q|6Q|Mur|F\.)[^\s<]+\s+reads?\s+(?:the\s+)?(?:explicit\s+)?(?:either\s+the\s+plene\s+or\s+alternative\s+spelling\s+)?<varheb>(.*?)</varheb>',
        r'(?:4Q|1Q|2Q|6Q|Mur|F\.)[^\s<]+[^\<]*<varheb>(.*?)</varheb>',
    ]
    
    # Try to extract DSS word if we have multiple Hebrew words
    if len(hebrew_words) >= 2:
        for pattern in dss_patterns:
            match = re.search(pattern, raw_xml, re.IGNORECASE)
            if match:
                extracted_dss = match.group(1).strip()
                # Verify this is different from Masoretic
                if not masoretic_word or extracted_dss != masoretic_word:
                    dss_word = extracted_dss
                    break
    
    # If we still don't have a Masoretic word but have Hebrew words, try broader search
    if not masoretic_word and hebrew_words:
        # Look for any varheb after "Masoretic"
        broad_pattern = r'Masoretic[^<]{0,50}<varheb>(.*?)</varheb>'
        match = re.search(broad_pattern, raw_xml, re.IGNORECASE)
        if match:
            masoretic_word = match.group(1).strip()
    
    return masoretic_word, dss_word
