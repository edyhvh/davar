#!/usr/bin/env python3
"""
Parser for DSS variant notes with Hebrew word extraction
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple


def is_fragment_to_fragment_difference(commentary: str) -> bool:
    """
    Determine if commentary describes a meaningful textual difference
    (not just automatic spelling/orthographic variations).
    
    INCLUDES:
    - Fragment-to-fragment (2+ DSS manuscripts)
    - Scholarly single-DSS notes (omissions, word changes, semantic differences)
    
    EXCLUDES:
    - Automatic spelling differences (plene/defective)
    - Simple orthographic variations
    - Vowel-pointing differences
    
    Args:
        commentary: The commentary text
        
    Returns:
        True if commentary describes a meaningful difference
    """
    if not commentary:
        return False
    
    # First check: Is this an automatic spelling difference? → EXCLUDE
    spelling_exclude_patterns = [
        r'\bplene\s+spelling\b',
        r'\bdefective\s+spelling\b',
        r'\balternative\s+spelling\b',
        r'\borthographic(?:\s+alternative)?\b',
        r'\bparagogic\s+nun\b',
        r'\bvowel\s*point(?:ing|ed)?\b',
        r'\bpronoun-(?:medial|final)\s+spelling\b',
        r'\bMasoretes?\s+(?:vowel\s+)?point',
        r'\b(?:just|only|merely)\s+(?:a\s+)?spelling',
        r'\bvar(?:iant)?\.\s+spelling\b',
    ]
    
    for pattern in spelling_exclude_patterns:
        if re.search(pattern, commentary, re.IGNORECASE):
            # Double-check: substantive changes override spelling exclusion
            substantive_overrides = [
                r'\b(?:omit|add|include)s?\b',
                r'\bchange\s+of\s+(?:tense|subject|meaning)\b',
                r'\bdifferent\s+(?:word|verb|noun|preposition)',
            ]
            
            has_override = any(re.search(p, commentary, re.IGNORECASE) 
                             for p in substantive_overrides)
            
            if not has_override:
                return False  # Pure spelling difference
    
    # Second check: Does this have substantive content? → INCLUDE
    substantive_include_patterns = [
        r'\b(?:omit|add|include|repeat)s?\b',
        r'\b(?:LXX|SP|Samaritan)',
        r'\bchange\s+of\s+(?:tense|subject|meaning)',
        r'\b(?:homoeoteleuton|parablepsis)',
        r'\breads?\s+\w+\s+meaning\s+(?!the\s+same)',
        r'\bdifferent\s+(?:word|verb|noun|form)',
        r'\bscribal\s+(?:mistake|error)(?!.*spelling)',
        r'\bcorruption\b',
        r'\bgenuine\s+reading\b',
        r'\boriginal\s+reading\b',
        r'\bno\s+change\s+of\s+meaning\s+to\s+the\s+(?:text|verse)',  # Scholarly phrase
    ]
    
    for pattern in substantive_include_patterns:
        if re.search(pattern, commentary, re.IGNORECASE):
            return True  # Substantive difference
    
    # Third check: Pattern to match DSS scroll sigla
    dss_pattern = r'\b([1-9]Q[A-Za-z]+[a-z]?|Mur[A-Z]+[a-z]?|pap\w+)\b'
    dss_refs = set(re.findall(dss_pattern, commentary, re.IGNORECASE))
    
    # If 2+ DSS manuscripts mentioned → fragment-to-fragment difference
    if len(dss_refs) >= 2:
        return True
    
    # If only 1 DSS but has longer, detailed commentary (not just spelling) → INCLUDE
    if len(dss_refs) == 1 and len(commentary) > 100:
        # Longer commentary usually indicates scholarly analysis
        # But exclude if it's primarily about spelling
        spelling_ratio = sum(1 for p in spelling_exclude_patterns 
                           if re.search(p, commentary, re.IGNORECASE))
        if spelling_ratio == 0:
            return True
    
    return False


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
