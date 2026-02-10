"""
TS2009 Text Processor

Handles text cleaning and footnote extraction for TS2009 Bible data.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessedText:
    """Represents text after processing with footnotes extracted."""
    text: str
    footnotes: List[str]


class FootnoteExtractor:
    """Extracts footnotes from TS2009 verse text."""

    # Pattern to match footnote markers like [a], [b], [1], [2]
    FOOTNOTE_MARKER_PATTERN = re.compile(r'\[([a-z0-9]+)\]')
    
    # Pattern to match "Footnote: [a]..." text at the end
    FOOTNOTE_TEXT_PATTERN = re.compile(r'\s*Footnote:\s*(.+?)(?:\s*$|\s+Footnote:)', re.IGNORECASE)
    
    # Pattern to match multiple footnotes in "Footnote: [a]... [b]..." format
    MULTIPLE_FOOTNOTES_PATTERN = re.compile(r'Footnote:\s*\[([^\]]+)\]\s*([^\[]*)(?=\s*(?:Footnote:|$))', re.IGNORECASE)

    @classmethod
    def extract_footnotes(cls, text: str) -> ProcessedText:
        """
        Extract footnotes from verse text and return clean text with footnotes array.

        Args:
            text: Raw text from database that may contain footnotes

        Returns:
            ProcessedText with clean text and list of footnotes
        """
        if not text:
            return ProcessedText(text="", footnotes=[])

        # First, check if there's explicit "Footnote:" or "Footnotes:" text
        if re.search(r'footnote[s]?:', text, re.IGNORECASE):
            return cls._extract_explicit_footnotes(text)
        
        # Check for inline footnote markers like [a], [b]
        return cls._extract_inline_footnotes(text)

    @classmethod
    def _extract_explicit_footnotes(cls, text: str) -> ProcessedText:
        """
        Extract footnotes from text with explicit "Footnote:" or "Footnotes:" markers.

        Example: "And the earth came to be[a] formless... Footnote: [a]Or the earth became."
        """
        # Split on "Footnote:" or "Footnotes:" to separate verse text from footnotes
        # Use regex to split on either form (case-insensitive)
        parts = re.split(r'Footnote[s]?:', text, flags=re.IGNORECASE)
        
        if len(parts) == 1:
            # No footnotes found, return as-is
            return ProcessedText(text=text.strip(), footnotes=[])
        
        # First part is the verse text (keep footnote markers)
        verse_text = parts[0].strip()
        
        # Remaining parts are footnotes
        footnotes = []
        for part in parts[1:]:
            part = part.strip()
            if not part:
                continue
            
            # Extract all footnote markers and their text from this part
            # Pattern: [a]Or the earth became. [b]Another footnote.
            # Use finditer to get all matches with their positions
            for match in re.finditer(r'\[([^\]]+)\]\s*([^[]*)(?=\s*\[|$)', part):
                marker = match.group(1)
                footnote_text = match.group(2).strip()
                if footnote_text:
                    footnotes.append(f"[{marker}] {footnote_text}")
        
        # Clean up verse text - keep footnote markers but clean up whitespace
        verse_text = re.sub(r'\s+', ' ', verse_text).strip()
        
        return ProcessedText(text=verse_text, footnotes=footnotes)

    @classmethod
    def _extract_inline_footnotes(cls, text: str) -> ProcessedText:
        """
        Extract footnotes from text with inline markers only.

        Example: "And the earth came to be[a] formless..."
        """
        # Find all footnote markers
        markers = cls.FOOTNOTE_MARKER_PATTERN.findall(text)
        
        if not markers:
            return ProcessedText(text=text.strip(), footnotes=[])
        
        # Keep markers in text, just clean up whitespace
        clean_text = re.sub(r'\s+', ' ', text).strip()
        
        # Create footnotes list (we don't have the actual text, just markers)
        # This is a fallback - ideally footnotes should have explicit text
        footnotes = [f"[{marker}]" for marker in markers]
        
        return ProcessedText(text=clean_text, footnotes=footnotes)


class TextCleaner:
    """Handles cleaning and processing of TS2009 text content."""

    @staticmethod
    def clean_html_text(text: str) -> str:
        """
        Clean HTML text from TS2009, preserving Hebrew content and essential formatting.

        Args:
            text: Raw text from database

        Returns:
            Cleaned text ready for app consumption
        """
        if not text:
            return ""

        # Remove HTML tags but preserve content
        text = re.sub(r'<blu>(.*?)</blu>', r'\1', text)  # Remove blue styling
        text = re.sub(r'<red>(.*?)</red>', r'\1', text)  # Remove red styling
        text = re.sub(r'<b>(.*?)</b>', r'\1', text)     # Remove bold
        text = re.sub(r'<sup>([^<]*)</sup>', r'[\1]', text)  # Convert superscripts to brackets
        text = re.sub(r'<ref>([^<]*)</ref>', r'[\1]', text)  # Convert references to brackets
        text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', text)     # Remove links
        text = re.sub(r'<heb>(.*?)</heb>', r'\1', text)     # Preserve Hebrew content
        text = re.sub(r'<em>(.*?)</em>', r'\1', text)       # Remove emphasis
        text = re.sub(r'<u>(.*?)</u>', r'\1', text)         # Remove underline

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def process_verse_text(text: str) -> ProcessedText:
        """
        Process verse text: clean HTML and extract footnotes.

        Args:
            text: Raw text from database

        Returns:
            ProcessedText with clean text and footnotes
        """
        # First clean HTML
        cleaned = TextCleaner.clean_html_text(text)
        
        # Then extract footnotes
        return FootnoteExtractor.extract_footnotes(cleaned)
