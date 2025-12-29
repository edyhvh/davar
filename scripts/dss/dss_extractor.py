#!/usr/bin/env python3
"""
DSS Variants Extractor

Extracts DSS variant information from PDF documents and other sources.
Handles text extraction, parsing, and structuring of variant data.

Author: Davar Project Team
License: MIT
"""

import re
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Pattern
from dataclasses import dataclass
# Optional PDF processing imports
try:
    import fitz  # PyMuPDF for PDF processing
    FITZ_AVAILABLE = True
except ImportError:
    fitz = None
    FITZ_AVAILABLE = False

try:
    from pdfplumber import open as open_pdf
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    open_pdf = None
    PDFPLUMBER_AVAILABLE = False

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dss_config import (
    DSS_DATA_DIR,
    BOOKS_WITH_VARIANTS,
    BOOK_MAPPINGS
)
from dss_processor import DSSVariant, DSSProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PDFExtractConfig:
    """Configuration for PDF extraction."""
    pdf_path: Path
    start_page: int = 0
    end_page: Optional[int] = None
    language_patterns: Dict[str, Pattern] = None

    def __post_init__(self):
        if self.language_patterns is None:
            self.language_patterns = {
                'spanish': re.compile(r'(?:traducción|variante|comentario)\s*:', re.IGNORECASE),
                'english': re.compile(r'(?:translation|variant|comment)\s*:', re.IGNORECASE),
                'hebrew': re.compile(r'[\u0590-\u05FF\u200f\u200e]+')  # Hebrew Unicode range
            }

class DSSExtractor:
    """Extractor for DSS variant data from various sources."""

    def __init__(self):
        self.processor = DSSProcessor()

        # Regex patterns for verse references
        self.verse_patterns = {
            'bible_ref': re.compile(r'(\d?\s*[A-Za-z]+)\s+(\d+):(\d+)', re.UNICODE),
            'chapter_verse': re.compile(r'(\d+):(\d+)'),
            'extended_ref': re.compile(r'([A-Za-z_]+)\s+(\d+):(\d+)(?:\s*-\s*(\d+):(\d+))?')
        }

        # Patterns for identifying variant types
        self.variant_type_patterns = {
            'addition': re.compile(r'(?:adición|addition|añade|adds)', re.IGNORECASE),
            'omission': re.compile(r'(?:omisión|omission|omite|omits)', re.IGNORECASE),
            'substitution': re.compile(r'(?:sustitución|substitution|reemplaza|replaces)', re.IGNORECASE),
            'transposition': re.compile(r'(?:transposición|transposition)', re.IGNORECASE),
            'spelling': re.compile(r'(?:ortografía|spelling|deletrea|spells)', re.IGNORECASE)
        }

    def extract_from_pdf(self, config: PDFExtractConfig) -> List[DSSVariant]:
        """Extract DSS variants from PDF document."""
        if not PDFPLUMBER_AVAILABLE and not FITZ_AVAILABLE:
            logger.error("PDF processing libraries not available. Install PyMuPDF or pdfplumber.")
            return []

        variants = []

        try:
            # Try with pdfplumber first (better for text extraction)
            if PDFPLUMBER_AVAILABLE:
                with open_pdf(config.pdf_path) as pdf:
                    pages = pdf.pages[config.start_page:config.end_page]

                for page_num, page in enumerate(pages):
                    text = page.extract_text()
                    if text:
                        page_variants = self._parse_pdf_page(text, page_num + config.start_page + 1)
                        variants.extend(page_variants)

        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyMuPDF: {e}")
            try:
                # Fallback to PyMuPDF
                if FITZ_AVAILABLE:
                    doc = fitz.open(config.pdf_path)
                    start_page = config.start_page
                    end_page = config.end_page or len(doc) - 1

                    for page_num in range(start_page, min(end_page + 1, len(doc))):
                        page = doc[page_num]
                        text = page.get_text()
                        page_variants = self._parse_pdf_page(text, page_num + 1)
                        variants.extend(page_variants)

                    doc.close()
                else:
                    logger.error("PyMuPDF not available")
                    return []

            except Exception as e2:
                logger.error(f"Both PDF extraction methods failed: {e2}")
                return []

        logger.info(f"Extracted {len(variants)} variants from PDF")
        return variants

    def _parse_pdf_page(self, text: str, page_num: int) -> List[DSSVariant]:
        """Parse a single page of PDF text for DSS variants."""
        variants = []

        # Split text into potential variant blocks
        # This is a heuristic approach - may need refinement based on actual PDF structure
        blocks = self._split_into_variant_blocks(text)

        for block in blocks:
            variant = self._parse_variant_block(block, page_num)
            if variant:
                variants.append(variant)

        return variants

    def _split_into_variant_blocks(self, text: str) -> List[str]:
        """Split PDF text into individual variant description blocks."""
        # Common separators in academic texts
        separators = [
            r'\n\s*(?=\d+\.\s)',  # Numbered lists
            r'\n\s*(?=Capítulo\s+\d+)',  # Chapter headers
            r'\n\s*(?=\d+:\d+)',  # Verse references
            r'\n\s*(?=TM\s*:)',  # Masoretic Text markers
            r'\n\s*(?=DSS\s*:)'  # DSS text markers
        ]

        blocks = [text]
        for separator in separators:
            new_blocks = []
            for block in blocks:
                new_blocks.extend(re.split(separator, block))
            blocks = new_blocks

        # Filter out empty blocks and clean up
        return [block.strip() for block in blocks if block.strip()]

    def _parse_variant_block(self, block: str, page_num: int) -> Optional[DSSVariant]:
        """Parse a single variant block into a DSSVariant object."""
        try:
            # Extract book, chapter, verse
            book, chapter, verse = self._extract_verse_reference(block)
            if not all([book, chapter, verse]):
                return None

            # Extract texts
            masoretic_text = self._extract_masoretic_text(block)
            dss_text = self._extract_dss_text(block)

            if not masoretic_text or not dss_text:
                return None

            # Extract translations and comments
            variant_translation_en = self._extract_translation(block, 'english')
            variant_translation_es = self._extract_translation(block, 'spanish')

            comments_he = self._extract_comments(block, 'hebrew')
            comments_en = self._extract_comments(block, 'english')
            comments_es = self._extract_comments(block, 'spanish')

            # Determine variant type
            variant_type = self._determine_variant_type(block)

            # Create variant object
            variant = DSSVariant(
                book=book,
                chapter=chapter,
                verse=verse,
                masoretic_text=masoretic_text,
                dss_text=dss_text,
                variant_translation_en=variant_translation_en,
                variant_translation_es=variant_translation_es,
                comments_he=comments_he,
                comments_en=comments_en,
                comments_es=comments_es,
                dss_source=f"PDF_page_{page_num}",
                variant_type=variant_type,
                significance=self._assess_significance(block)
            )

            return variant

        except Exception as e:
            logger.warning(f"Error parsing variant block: {e}")
            return None

    def _extract_verse_reference(self, block: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
        """Extract book, chapter, and verse from text block."""
        # Try different patterns
        for pattern_name, pattern in self.verse_patterns.items():
            match = pattern.search(block)
            if match:
                if pattern_name == 'bible_ref':
                    book_name = match.group(1).strip()
                    chapter = int(match.group(2))
                    verse = int(match.group(3))

                    # Map to our book naming convention
                    book = self._normalize_book_name(book_name)
                    return book, chapter, verse

                elif pattern_name == 'chapter_verse':
                    # Assume current book context (would need to be tracked)
                    chapter = int(match.group(1))
                    verse = int(match.group(2))
                    return "unknown", chapter, verse

        return None, None, None

    def _normalize_book_name(self, book_name: str) -> str:
        """Normalize book names to our standard format."""
        # Remove numbers and clean up
        book_name = re.sub(r'^\d+\s*', '', book_name).strip().lower()

        # Common mappings
        mappings = {
            'isaías': 'isaiah',
            'isaiah': 'isaiah',
            'is': 'isaiah',
            '1 samuel': 'samuel_1',
            'i samuel': 'samuel_1',
            '1sam': 'samuel_1',
            '2 samuel': 'samuel_2',
            'ii samuel': 'samuel_2',
            '2sam': 'samuel_2'
        }

        return mappings.get(book_name, book_name)

    def _extract_masoretic_text(self, block: str) -> str:
        """Extract Masoretic Text from block."""
        # Look for TM, MT, Masorético patterns
        patterns = [
            r'TM\s*:\s*([^D\n]+?)(?=DSS|$|\n)',
            r'MT\s*:\s*([^D\n]+?)(?=DSS|$|\n)',
            r'Masorético\s*:\s*([^D\n]+?)(?=DSS|$|\n)',
            r'Texto\s+Masorético\s*:\s*([^D\n]+?)(?=DSS|$|\n)'
        ]

        for pattern in patterns:
            match = re.search(pattern, block, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_dss_text(self, block: str) -> str:
        """Extract DSS Text from block."""
        # Look for DSS patterns
        patterns = [
            r'DSS\s*:\s*([^\n]+?)(?=\n|$|Traducción|Comentario)',
            r'Qumrán\s*:\s*([^\n]+?)(?=\n|$|Traducción|Comentario)',
            r'Dead Sea Scrolls\s*:\s*([^\n]+?)(?=\n|$|Traducción|Comentario)'
        ]

        for pattern in patterns:
            match = re.search(pattern, block, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_translation(self, block: str, language: str) -> str:
        """Extract translation for specific language."""
        if language == 'english':
            patterns = [
                r'Traducción\s+inglés\s*:\s*([^\n]+?)(?=\n|$)',
                r'English\s+translation\s*:\s*([^\n]+?)(?=\n|$)',
                r'Variant\s+in\s+English\s*:\s*([^\n]+?)(?=\n|$)'
            ]
        elif language == 'spanish':
            patterns = [
                r'Traducción\s+español\s*:\s*([^\n]+?)(?=\n|$)',
                r'Traducción\s+de\s+la\s+variante\s*:\s*([^\n]+?)(?=\n|$)',
                r'Variante\s+en\s+español\s*:\s*([^\n]+?)(?=\n|$)'
            ]
        else:
            return ""

        for pattern in patterns:
            match = re.search(pattern, block, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_comments(self, block: str, language: str) -> str:
        """Extract comments for specific language."""
        if language == 'hebrew':
            # Look for Hebrew text in comments
            hebrew_pattern = re.compile(r'[\u0590-\u05FF\u200f\u200e]{10,}')
            matches = hebrew_pattern.findall(block)
            return ' '.join(matches)

        elif language == 'english':
            patterns = [
                r'Comentario\s+inglés\s*:\s*([^\n]+?)(?=\n|$)',
                r'English\s+comment\s*:\s*([^\n]+?)(?=\n|$)',
                r'Nota\s+en\s+inglés\s*:\s*([^\n]+?)(?=\n|$)'
            ]
        elif language == 'spanish':
            patterns = [
                r'Comentario\s*:\s*([^\n]+?)(?=\n|$)',
                r'Nota\s*:\s*([^\n]+?)(?=\n|$)',
                r'Comentario\s+español\s*:\s*([^\n]+?)(?=\n|$)'
            ]
        else:
            return ""

        for pattern in patterns:
            match = re.search(pattern, block, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return ""

    def _determine_variant_type(self, block: str) -> str:
        """Determine the type of textual variant."""
        for variant_type, pattern in self.variant_type_patterns.items():
            if pattern.search(block):
                return variant_type

        return "unknown"

    def _assess_significance(self, block: str) -> str:
        """Assess the scholarly significance of the variant."""
        text = block.lower()

        if any(word in text for word in ['importante', 'significant', 'major', 'crucial']):
            return "high"
        elif any(word in text for word in ['menor', 'minor', 'pequeño', 'small']):
            return "low"
        else:
            return "medium"

    def process_pdf_and_save(self, pdf_path: Path) -> int:
        """Process PDF and save extracted variants."""
        config = PDFExtractConfig(pdf_path=pdf_path)

        logger.info(f"Processing PDF: {pdf_path}")
        variants = self.extract_from_pdf(config)

        # Add variants to processor
        added_count = 0
        for variant in variants:
            if self.processor.add_variant(variant):
                added_count += 1

        # Save data
        self.processor.save_data()

        logger.info(f"Successfully processed {added_count} variants from PDF")
        return added_count

def main():
    """Main entry point for DSS extraction."""
    if len(sys.argv) < 2:
        print("Usage: python dss_extractor.py <pdf_path>")
        return 1

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"PDF file not found: {pdf_path}")
        return 1

    extractor = DSSExtractor()
    success_count = extractor.process_pdf_and_save(pdf_path)

    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
