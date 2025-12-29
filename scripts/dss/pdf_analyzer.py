#!/usr/bin/env python3
"""
PDF Analyzer for DSS Variants

Analyzes the specific PDF format containing DSS textual variants.
Extracts structured data from the "VARIANTES - TEXTO MASORÉTICO Y QUMRÁN.pdf" file.

Author: Davar Project Team
License: MIT
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dss_types import DSSVariant
from dss_processor import DSSProcessor

@dataclass
class DSSPDFVariant:
    """Represents a variant extracted from the PDF."""
    reference: str  # "Isaías 14:4" or "1 Samuel 1:22-23"
    tm_text: str    # Texto Masorético
    dss_text: str   # Texto de Qumrán
    description: str  # Description in Spanish
    hebrew_words: List[str] = None  # Hebrew words found

    def __post_init__(self):
        if self.hebrew_words is None:
            self.hebrew_words = []

class DSSPDFAnalyzer:
    """Analyzer for the specific DSS PDF format."""

    def __init__(self):
        self.variant_patterns = {
            # Isaiah patterns
            'isaiah_variant': re.compile(
                r'•\s*Isaías\s+(\d+):(\d+)\s+(.+?)(?=•\s*Isaías|\n\s*\n|$)',
                re.DOTALL
            ),

            # Samuel patterns
            'samuel_variant': re.compile(
                r'•\s*([12])\s*Samuel\s+(\d+):(\d+)(?:-(\d+))?\s+(.+?)(?=•\s*[12]\s*Samuel|\n\s*\n|$)',
                re.DOTALL
            ),

            # Samuel gaps (vacíos textuales)
            'samuel_gap': re.compile(
                r'•\s*([12])\s*Samuel\s+(\d+):(\d+)(?:-(\d+))?\s+(.+?)(?=•\s*[12]\s*Samuel|\n\s*\n|$)',
                re.DOTALL
            ),

            # Hebrew text extraction
            'hebrew_text': re.compile(r'[\u0590-\u05FF\u200f\u200e]{2,}[\s\u200f\u200e]*[\u0590-\u05FF\u200f\u200e]*'),

            # Qumrán vs TM comparison
            'qumran_vs_tm': re.compile(r'Qumrán:\s*([^\n]+?)\s*–\s*T\.M\.:\s*([^\n]+)', re.IGNORECASE),

            # TM vs Qumrán (alternative format)
            'tm_vs_qumran': re.compile(r'T\.M\.:\s*([^\n]+?)\s*–\s*Qumrán:\s*([^\n]+)', re.IGNORECASE)
        }

        self.book_mappings = {
            'Isaías': 'isaiah',
            '1 Samuel': 'samuel_1',
            '2 Samuel': 'samuel_2'
        }

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using pdftotext."""
        try:
            result = subprocess.run(
                ['pdftotext', '-layout', str(pdf_path), '-'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def parse_isaiah_section(self, text: str) -> List[DSSPDFVariant]:
        """Parse the Isaiah section of the PDF."""
        variants = []

        # Find Isaiah section
        isaiah_match = re.search(r'GRAN ROLLO DE ISAÍAS\s*\n(.+?)(?=\n\s*\n\s*FRAGMENTOS|\n\s*\n\s*$)', text, re.DOTALL)
        if not isaiah_match:
            return variants

        isaiah_text = isaiah_match.group(1)

        # Find individual variants
        for match in re.finditer(r'•\s*Isaías\s+(\d+):(\d+)\s+(.+?)(?=•\s*Isaías|\n\s*\n|$)', isaiah_text, re.DOTALL):
            chapter, verse = match.groups()[:2]
            description = match.group(3).strip()

            # Extract Qumrán vs TM comparison
            comparison_match = re.search(r'Qumrán:\s*([^\n]+?)\s*–\s*T\.M\.:\s*([^\n]+)', description, re.IGNORECASE)
            if comparison_match:
                dss_text, tm_text = comparison_match.groups()
            else:
                # Try alternative format
                comparison_match = re.search(r'T\.M\.:\s*([^\n]+?)\s*–\s*Qumrán:\s*([^\n]+)', description, re.IGNORECASE)
                if comparison_match:
                    tm_text, dss_text = comparison_match.groups()
                else:
                    tm_text, dss_text = "", ""

            # Extract Hebrew words
            hebrew_words = self.variant_patterns['hebrew_text'].findall(description)

            variant = DSSPDFVariant(
                reference=f"Isaías {chapter}:{verse}",
                tm_text=tm_text.strip(),
                dss_text=dss_text.strip(),
                description=description,
                hebrew_words=hebrew_words
            )
            variants.append(variant)

        return variants

    def parse_samuel_section(self, text: str) -> List[DSSPDFVariant]:
        """Parse the Samuel section of the PDF."""
        variants = []

        # Find Samuel variants section
        samuel_match = re.search(r'FRAGMENTOS DE SAMUEL - VARIANTES\s*\n(.+?)(?=\n\s*\n\s*FRAGMENTOS|\n\s*\n\s*$)', text, re.DOTALL)
        if samuel_match:
            samuel_text = samuel_match.group(1)
            variants.extend(self._parse_samuel_variants(samuel_text, "variants"))

        # Find Samuel gaps section
        gaps_match = re.search(r'FRAGMENTOS DE SAMUEL – VACÍOS TEXTUALES\s*\n(.+?)(?=\n\s*\n\s*$)', text, re.DOTALL)
        if gaps_match:
            gaps_text = gaps_match.group(1)
            variants.extend(self._parse_samuel_variants(gaps_text, "gaps"))

        return variants

    def _parse_samuel_variants(self, text: str, variant_type: str) -> List[DSSPDFVariant]:
        """Parse individual Samuel variants."""
        variants = []

        # Pattern for Samuel variants
        pattern = r'•\s*([12])\s*Samuel\s+(\d+):(\d+)(?:-(\d+))?\s+(.+?)(?=•\s*[12]\s*Samuel|\n\s*\n|$)'

        for match in re.finditer(pattern, text, re.DOTALL):
            book_num, chapter, verse_start = match.groups()[:3]
            verse_end = match.group(4)
            description = match.group(5).strip()

            # Handle verse ranges
            if verse_end:
                reference = f"{book_num} Samuel {chapter}:{verse_start}-{verse_end}"
            else:
                reference = f"{book_num} Samuel {chapter}:{verse_start}"

            # For Samuel, extract TM and DSS text from description
            tm_text, dss_text = self._extract_samuel_texts(description)

            # Extract Hebrew words
            hebrew_words = self.variant_patterns['hebrew_text'].findall(description)

            variant = DSSPDFVariant(
                reference=reference,
                tm_text=tm_text,
                dss_text=dss_text,
                description=description,
                hebrew_words=hebrew_words
            )
            variants.append(variant)

        return variants

    def _extract_samuel_texts(self, description: str) -> Tuple[str, str]:
        """Extract TM and DSS texts from Samuel description."""
        tm_text = ""
        dss_text = ""

        # Clean up the description first
        desc = re.sub(r'\s+', ' ', description)

        # Pattern 1: DSS with comma and quotes, TM with colon and quotes
        # "en los M.M.M. dice, "DSS text" ... el Texto Masorético dice: "TM text""
        dss_comma_match = re.search(
            r'en\s+los\s+M\.M\.M\.\s+dice,\s*["""]?([^""]+)["""]?.*?el\s+Texto\s+Masorético\s+dice:\s*["""]?([^""]+)["""]?',
            desc,
            re.IGNORECASE | re.DOTALL
        )
        if dss_comma_match:
            dss_text = dss_comma_match.group(1).strip()
            tm_text = dss_comma_match.group(2).strip()
            return tm_text, dss_text

        # Pattern 2: DSS first, then TM (most common)
        # "en los M.M.M. dice: [DSS text] ... el Texto Masorético dice: [TM text]"
        dss_first_match = re.search(
            r'en\s+los\s+M\.M\.M\.\s+dice:\s*["""]?([^""]+)["""]?.*?el\s+Texto\s+Masorético\s+dice:\s*["""]?([^""]+)["""]?',
            desc,
            re.IGNORECASE | re.DOTALL
        )
        if dss_first_match:
            dss_text = dss_first_match.group(1).strip()
            tm_text = dss_first_match.group(2).strip()
            return tm_text, dss_text

        # Pattern 3: TM first, then DSS
        # "en el Texto Masorético dice: [TM text] ... los M.M.M. dicen: [DSS text]"
        tm_first_match = re.search(
            r'en\s+el\s+Texto\s+Masorético\s+dice:\s*["""]?([^""]+)["""]?.*?los\s+M\.M\.M\.\s+(?:y\s+la\s+Septuaginta\s+)?dicen:\s*["""]?([^""]+)["""]?',
            desc,
            re.IGNORECASE | re.DOTALL
        )
        if tm_first_match:
            tm_text = tm_first_match.group(1).strip()
            dss_text = tm_first_match.group(2).strip()
            return tm_text, dss_text

        # Pattern 4: Simple DSS text extraction (with comma)
        dss_match = re.search(r'en\s+los\s+M\.M\.M\.\s+dice,\s*["""]?([^""]+)["""]?', desc, re.IGNORECASE)
        if dss_match:
            dss_text = dss_match.group(1).strip()

        # Pattern 5: Simple DSS text extraction (with colon)
        if not dss_text:
            dss_match = re.search(r'en\s+los\s+M\.M\.M\.\s+dice:\s*["""]?([^""]+)["""]?', desc, re.IGNORECASE)
            if dss_match:
                dss_text = dss_match.group(1).strip()

        # Pattern 6: Simple TM text extraction
        tm_match = re.search(r'el\s+Texto\s+Masorético\s+dice:\s*["""]?([^""]+)["""]?', desc, re.IGNORECASE)
        if tm_match:
            tm_text = tm_match.group(1).strip()

        # Pattern 7: Alternative TM extraction
        if not tm_text:
            tm_alt_match = re.search(r'Texto\s+Masorético\s+dice:\s*["""]?([^""]+)["""]?', desc, re.IGNORECASE)
            if tm_alt_match:
                tm_text = tm_alt_match.group(1).strip()

        # For gaps/additions, the TM text might be longer
        if not tm_text and not dss_text:
            # Look for addition patterns
            addition_match = re.search(r'los\s+M\.M\.M\.\s+(?:añaden|agregan)\s+(.+?)(?:\.\s*31|$)', desc, re.IGNORECASE | re.DOTALL)
            if addition_match:
                dss_text = addition_match.group(1).strip()
                # For additions, TM text is implied to be missing
                tm_text = "[texto ausente en TM]"

        return tm_text, dss_text

    def analyze_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Analyze the entire PDF and extract all variants."""
        print(f"Analyzing PDF: {pdf_path}")

        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return {"error": "Could not extract text from PDF"}

        print(f"Extracted {len(text)} characters of text")

        # Parse sections
        isaiah_variants = self.parse_isaiah_section(text)
        samuel_variants = self.parse_samuel_section(text)

        print(f"Found {len(isaiah_variants)} Isaiah variants")
        print(f"Found {len(samuel_variants)} Samuel variants")

        return {
            "isaiah_variants": isaiah_variants,
            "samuel_variants": samuel_variants,
            "total_variants": len(isaiah_variants) + len(samuel_variants),
            "text_sample": text[:500] + "..." if len(text) > 500 else text
        }

    def convert_to_dss_variants(self, pdf_variants: List[DSSPDFVariant]) -> List[DSSVariant]:
        """Convert PDF variants to DSSVariant objects."""
        dss_variants = []

        for pdf_variant in pdf_variants:
            # Parse reference
            book, chapter, verse = self._parse_reference(pdf_variant.reference)
            if not all([book, chapter, verse]):
                continue

            # Determine variant type
            variant_type = self._determine_variant_type(pdf_variant.description)

            # Create DSS variant
            variant = DSSVariant(
                book=book,
                chapter=chapter,
                verse=verse,
                masoretic_text=pdf_variant.tm_text,
                dss_text=pdf_variant.dss_text,
                variant_translation_es=self._extract_spanish_description(pdf_variant.description),
                comments_es=pdf_variant.description,
                dss_source="PDF_VARIANTS",
                variant_type=variant_type,
                significance=self._assess_significance(pdf_variant.description)
            )

            dss_variants.append(variant)

        return dss_variants

    def _parse_reference(self, reference: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
        """Parse biblical reference into book, chapter, verse."""
        # Isaiah pattern
        isaiah_match = re.match(r'Isaías\s+(\d+):(\d+)', reference)
        if isaiah_match:
            chapter, verse = map(int, isaiah_match.groups())
            return "isaiah", chapter, verse

        # Samuel pattern
        samuel_match = re.match(r'([12])\s*Samuel\s+(\d+):(\d+)', reference)
        if samuel_match:
            book_num, chapter, verse = samuel_match.groups()
            book = f"samuel_{book_num}"
            return book, int(chapter), int(verse)

        return None, None, None

    def _determine_variant_type(self, description: str) -> str:
        """Determine the type of variant from description."""
        desc_lower = description.lower()

        if any(word in desc_lower for word in ['adición', 'añade', 'agrega']):
            return 'addition'
        elif any(word in desc_lower for word in ['omisión', 'omite', 'falta']):
            return 'omission'
        elif any(word in desc_lower for word in ['sustitución', 'reemplaza', 'cambia']):
            return 'substitution'
        elif any(word in desc_lower for word in ['ortográfico', 'ortografía', 'deletrea']):
            return 'spelling'
        elif any(word in desc_lower for word in ['añaden', 'agregan', 'paréntesis']):
            return 'addition'
        else:
            return 'unknown'

    def _assess_significance(self, description: str) -> str:
        """Assess significance based on description."""
        desc_lower = description.lower()

        if any(word in desc_lower for word in ['error', 'corrección', 'significativo']):
            return 'high'
        elif any(word in desc_lower for word in ['menor', 'pequeño', 'ortográfico']):
            return 'low'
        else:
            return 'medium'

    def _extract_spanish_description(self, description: str) -> str:
        """Extract Spanish translation/description."""
        # Try to find the main descriptive part
        # Remove the technical parts and keep the meaning
        desc = re.sub(r'\s+', ' ', description)
        desc = re.sub(r'\([^)]*\)', '', desc)  # Remove parentheses
        desc = re.sub(r'Qumrán:\s*[^\s]*\s*–\s*T\.M\.:\s*[^\s]*', '', desc)
        desc = re.sub(r'T\.M\.:\s*[^\s]*\s*–\s*Qumrán:\s*[^\s]*', '', desc)

        return desc.strip()

def main():
    """Main function to analyze the PDF."""
    analyzer = DSSPDFAnalyzer()

    pdf_path = Path(__file__).parent.parent.parent / "data" / "dss" / "VARIANTES - TEXTO MASORÉTICO Y QUMRÁN.pdf"

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return 1

    # Analyze PDF
    result = analyzer.analyze_pdf(pdf_path)

    if "error" in result:
        print(f"Error: {result['error']}")
        return 1

    print("\n=== PDF Analysis Results ===")
    print(f"Total variants found: {result['total_variants']}")
    print(f"Isaiah variants: {len(result['isaiah_variants'])}")
    print(f"Samuel variants: {len(result['samuel_variants'])}")

    # Show sample variants
    print("\n=== Sample Isaiah Variants ===")
    for i, variant in enumerate(result['isaiah_variants'][:3]):
        print(f"{i+1}. {variant.reference}")
        print(f"   DSS: {variant.dss_text}")
        print(f"   TM: {variant.tm_text}")
        print()

    print("=== Sample Samuel Variants ===")
    for i, variant in enumerate(result['samuel_variants'][:3]):
        print(f"{i+1}. {variant.reference}")
        print(f"   DSS: {variant.dss_text}")
        print(f"   TM: {variant.tm_text}")
        print()

    # Convert and save to DSS processor
    all_pdf_variants = result['isaiah_variants'] + result['samuel_variants']
    dss_variants = analyzer.convert_to_dss_variants(all_pdf_variants)

    print(f"\nConverted {len(dss_variants)} variants to DSS format")

    # Save using processor
    processor = DSSProcessor()
    added_count = 0
    for variant in dss_variants:
        if processor.add_variant(variant):
            added_count += 1

    processor.save_data()
    print(f"Successfully added {added_count} variants to DSS database")

    return 0

if __name__ == "__main__":
    sys.exit(main())
