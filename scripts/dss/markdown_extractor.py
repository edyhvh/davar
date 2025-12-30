#!/usr/bin/env python3
"""
DSS Markdown Extractor

Extracts DSS variant information from Markdown documents.
Parses structured Markdown format with DSS textual variants.
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from .dss_types import DSSVariant
from .dss_config import config, BOOK_MAPPINGS, get_book_file_path
from .utils import setup_logging, ensure_directories


@dataclass
class MarkdownExtractConfig:
    """Configuration for Markdown extraction."""
    variant_section_pattern: str = r'^##+\s*Variants?\s+(?:for\s+)?(.+)$'
    variant_pattern: str = r'^\s*\*\*(.+?)\*\*\s*-\s*(.+)$'
    reference_pattern: str = r'(\w+)\s+(\d+):(\d+)'
    significance_indicators: Dict[str, str] = None

    def __post_init__(self):
        if self.significance_indicators is None:
            self.significance_indicators = {
                'high': ['major', 'significant', 'important', 'critical'],
                'medium': ['moderate', 'notable', 'substantial'],
                'low': ['minor', 'small', 'spelling', 'trivial']
            }


class DSSMarkdownExtractor:
    """
    Extractor for DSS variants from Markdown documents.

    Parses structured Markdown files containing DSS textual variants
    and converts them to standardized DSSVariant objects.
    """

    def __init__(self, config_obj: MarkdownExtractConfig = None):
        self.config = config_obj or MarkdownExtractConfig()
        self.logger = setup_logging()

    def extract_from_markdown(self, markdown_path: Union[str, Path]) -> Dict[str, List[DSSVariant]]:
        """
        Extract DSS variants from a Markdown file.

        Args:
            markdown_path: Path to the Markdown file

        Returns:
            Dictionary mapping book names to lists of DSSVariant objects
        """
        path = Path(markdown_path)
        if not path.exists():
            raise FileNotFoundError(f"Markdown file not found: {path}")

        self.logger.info(f"Extracting DSS variants from: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        variants_by_book = self._parse_markdown_content(content)

        total_variants = sum(len(variants) for variants in variants_by_book.values())
        self.logger.info(f"Extracted {total_variants} variants from {len(variants_by_book)} books")

        return variants_by_book

    def _parse_markdown_content(self, content: str) -> Dict[str, List[DSSVariant]]:
        """
        Parse Markdown content and extract variants.

        Args:
            content: Raw Markdown content

        Returns:
            Dictionary of variants grouped by book
        """
        variants_by_book = {}

        # Split content into sections
        sections = self._split_into_sections(content)

        for section_title, section_content in sections.items():
            book_name = self._extract_book_from_section(section_title)
            if not book_name:
                continue

            self.logger.debug(f"Processing section for book: {book_name}")
            variants = self._extract_variants_from_section(section_content, book_name)

            if variants:
                variants_by_book[book_name] = variants
                self.logger.info(f"Found {len(variants)} variants for {book_name}")

        return variants_by_book

    def _split_into_sections(self, content: str) -> Dict[str, str]:
        """
        Split Markdown content into sections based on headers.

        Args:
            content: Markdown content

        Returns:
            Dictionary mapping section titles to content
        """
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            # Check if line is a header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if header_match:
                # Save previous section if exists
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                current_section = header_match.group(2).strip()
                current_content = []
            else:
                if current_section is not None:
                    current_content.append(line)

        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _extract_book_from_section(self, section_title: str) -> Optional[str]:
        """
        Extract book name from section title.

        Args:
            section_title: Section title

        Returns:
            Normalized book name or None
        """
        # Try to match variant section pattern
        match = re.search(self.config.variant_section_pattern, section_title, re.IGNORECASE)
        if match:
            book_name = match.group(1).strip()
            return self._normalize_book_name(book_name)

        # Try to match book name directly
        title_lower = section_title.lower()
        for standard_name, display_name in BOOK_MAPPINGS.items():
            # Check standard name
            if standard_name.lower() in title_lower:
                return standard_name
            # Check display name (with underscores replaced by spaces)
            if display_name.lower().replace('_', ' ') in title_lower:
                return standard_name
            # Check display name as-is
            if display_name.lower() in title_lower:
                return standard_name

        return None

    def _normalize_book_name(self, book_name: str) -> str:
        """
        Normalize book name to standard format.

        Args:
            book_name: Raw book name

        Returns:
            Normalized book name
        """
        # Convert to lowercase and remove extra spaces
        normalized = book_name.lower().strip()

        # Try to match against known books
        for standard_name in config.BOOKS_WITH_VARIANTS:
            if standard_name in normalized:
                return standard_name

        # Check display names
        for standard_name, display_name in BOOK_MAPPINGS.items():
            if display_name.lower() in normalized:
                return standard_name

        return normalized

    def _extract_variants_from_section(self, section_content: str, book: str) -> List[DSSVariant]:
        """
        Extract individual variants from section content.

        Args:
            section_content: Content of a section
            book: Book name for this section

        Returns:
            List of DSSVariant objects
        """
        variants = []
        lines = section_content.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            variant = self._parse_variant_line(line, book)
            if variant:
                variants.append(variant)

        return variants

    def _parse_variant_line(self, line: str, book: str) -> Optional[DSSVariant]:
        """
        Parse a single variant line from Markdown.

        Args:
            line: Markdown line containing variant information
            book: Book name

        Returns:
            DSSVariant object or None if parsing failed
        """
        # Try to match variant pattern
        match = re.search(self.config.variant_pattern, line, re.IGNORECASE)
        if not match:
            return None

        variant_text = match.group(1).strip()
        description = match.group(2).strip()

        # Try to extract reference from variant text
        reference_match = re.search(self.config.reference_pattern, variant_text)
        if not reference_match:
            self.logger.warning(f"Could not extract reference from: {variant_text}")
            return None

        book_ref, chapter_str, verse_str = reference_match.groups()
        try:
            chapter = int(chapter_str)
            verse = int(verse_str)
        except ValueError:
            self.logger.warning(f"Invalid chapter/verse numbers in: {variant_text}")
            return None

        # Extract MT and DSS text from description
        mt_text, dss_text, comments = self._parse_variant_description(description)

        # Determine significance
        significance = self._determine_significance(description)

        # Determine variant type
        variant_type = self._determine_variant_type(mt_text, dss_text, description)

        try:
            return DSSVariant(
                book=book,
                chapter=chapter,
                verse=verse,
                masoretic_text=mt_text,
                dss_text=dss_text,
                comments_en=comments,
                variant_type=variant_type,
                significance=significance
            )
        except Exception as e:
            self.logger.warning(f"Failed to create variant from line '{line}': {e}")
            return None

    def _parse_variant_description(self, description: str) -> Tuple[str, str, str]:
        """
        Parse variant description to extract MT text, DSS text, and comments.

        Args:
            description: Variant description text

        Returns:
            Tuple of (masoretic_text, dss_text, comments)
        """
        # Look for patterns like "MT: [text] vs DSS: [text]" or similar
        mt_pattern = r'MT:?\s*["""]?([^""]+)["""]?'
        dss_pattern = r'DSS:?\s*["""]?([^""]+)["""]?'

        mt_match = re.search(mt_pattern, description, re.IGNORECASE)
        dss_match = re.search(dss_pattern, description, re.IGNORECASE)

        mt_text = mt_match.group(1).strip() if mt_match else ""
        dss_text = dss_match.group(1).strip() if dss_match else ""

        # Remove the extracted parts from description to get comments
        comments = description
        if mt_match:
            comments = comments.replace(mt_match.group(0), "")
        if dss_match:
            comments = comments.replace(dss_match.group(0), "")

        # Clean up comments
        comments = re.sub(r'^\s*(vs\.?|versus|compared to)\s*', '', comments, flags=re.IGNORECASE)
        comments = re.sub(r'\s+', ' ', comments).strip()

        return mt_text, dss_text, comments

    def _determine_significance(self, description: str) -> str:
        """
        Determine significance level from description.

        Args:
            description: Variant description

        Returns:
            Significance level (high, medium, low)
        """
        desc_lower = description.lower()

        for level, indicators in self.config.significance_indicators.items():
            for indicator in indicators:
                if indicator in desc_lower:
                    return level

        return "low"  # Default to low significance

    def _determine_variant_type(self, mt_text: str, dss_text: str, description: str) -> str:
        """
        Determine variant type from texts and description.

        Args:
            mt_text: Masoretic Text
            dss_text: DSS Text
            description: Description text

        Returns:
            Variant type
        """
        desc_lower = description.lower()

        # Check for specific type indicators
        if any(word in desc_lower for word in ['addition', 'added', 'extra']):
            return 'addition'
        elif any(word in desc_lower for word in ['omission', 'omitted', 'missing']):
            return 'omission'
        elif any(word in desc_lower for word in ['substitution', 'replaced', 'changed']):
            return 'substitution'
        elif any(word in desc_lower for word in ['transposition', 'order', 'swapped']):
            return 'transposition'
        elif any(word in desc_lower for word in ['spelling', 'orthography']):
            return 'spelling'

        # Try to infer from text length differences
        if mt_text and dss_text:
            mt_words = len(mt_text.split())
            dss_words = len(dss_text.split())

            if abs(mt_words - dss_words) > 2:
                return 'addition' if dss_words > mt_words else 'omission'

        return 'unknown'

    def save_variants_to_json(self, variants_by_book: Dict[str, List[DSSVariant]], output_dir: Optional[Path] = None) -> None:
        """
        Save extracted variants to JSON files.

        Args:
            variants_by_book: Variants grouped by book
            output_dir: Output directory (defaults to config output dir)
        """
        output_dir = output_dir or config.paths.output_dir
        ensure_directories(output_dir)

        for book, variants in variants_by_book.items():
            file_path = get_book_file_path(book)

            # Convert variants to dictionaries
            variant_dicts = [variant.to_dict() for variant in variants]

            # Create metadata
            metadata = {
                "book": book,
                "total_variants": len(variants),
                "extraction_date": datetime.now().isoformat(),
                "source": "markdown",
                "variants": variant_dicts
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved {len(variants)} variants for {book} to {file_path}")

    def extract_and_save(self, markdown_path: Union[str, Path], output_dir: Optional[Path] = None) -> Dict[str, int]:
        """
        Extract variants from Markdown and save to JSON files.

        Args:
            markdown_path: Path to Markdown file
            output_dir: Output directory

        Returns:
            Dictionary with extraction statistics
        """
        variants_by_book = self.extract_from_markdown(markdown_path)
        self.save_variants_to_json(variants_by_book, output_dir)

        stats = {book: len(variants) for book, variants in variants_by_book.items()}
        stats["total_books"] = len(variants_by_book)
        stats["total_variants"] = sum(stats.values())

        return stats


# Convenience function for command line usage
def extract_dss_variants(markdown_file: str, output_dir: Optional[str] = None) -> Dict[str, int]:
    """
    Extract DSS variants from Markdown file (convenience function).

    Args:
        markdown_file: Path to Markdown file
        output_dir: Optional output directory

    Returns:
        Extraction statistics
    """
    extractor = DSSMarkdownExtractor()

    output_path = Path(output_dir) if output_dir else None

    return extractor.extract_and_save(markdown_file, output_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python markdown_extractor.py <markdown_file> [output_dir]")
        sys.exit(1)

    markdown_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        stats = extract_dss_variants(markdown_file, output_dir)
        print(f"Extraction completed successfully!")
        print(f"Books processed: {stats['total_books']}")
        print(f"Total variants: {stats['total_variants']}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
