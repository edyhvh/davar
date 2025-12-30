#!/usr/bin/env python3
"""
ETCBC DSS Corpus Integrator

Integrates with the ETCBC Dead Sea Scrolls Text-Fabric corpus for enhanced
textual analysis and cross-referencing.

Author: Davar Project Team
License: MIT
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
import requests
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dss_config import config, ETCBC_DSS_CONFIG
from dss_types import DSSVariant

@dataclass
class ETCBC_DSS_Config:
    """Configuration for ETCBC DSS corpus integration."""
    corpus_url: str = "https://github.com/ETCBC/dss/releases/download/v0.1/tf.zip"
    local_path: Path = None
    features: List[str] = None
    sections: List[str] = None

    def __post_init__(self):
        if self.local_path is None:
            self.local_path = config.paths.corpus_dir
        if self.features is None:
            self.features = ETCBC_DSS_CONFIG.get("features", [])
        if self.sections is None:
            self.sections = ["scroll", "fragment", "line"]

class ETCBC_DSS_Integrator:
    """Integrator for ETCBC DSS Text-Fabric corpus."""

    def __init__(self, config: ETCBC_DSS_Config = None):
        self.config = config or ETCBC_DSS_Config()
        self.tf = None  # Text-Fabric API instance
        self.corpus_loaded = False
        self.available_features: Set[str] = set()

    def download_corpus(self) -> bool:
        """Download the ETCBC DSS corpus if not present."""
        try:
            # Check if corpus already exists
            if config.paths.corpus_dir.exists() and any(config.paths.corpus_dir.rglob("*.tf")):
                print(f"DSS corpus already exists at {config.paths.corpus_dir}")
                return True

            print(f"Downloading DSS corpus from {self.config.corpus_url}")

            # Use Text-Fabric to download the corpus
            from tf.fabric import Fabric

            # Create TF instance and download
            TF = Fabric(locations=str(config.paths.corpus_dir.parent), modules=['dss'], silent=False)

            # Download the corpus
            TF.download(self.config.corpus_url)

            print(f"DSS corpus downloaded successfully to {config.paths.corpus_dir}")
            return True

        except Exception as e:
            print(f"Error downloading DSS corpus: {e}")
            print("Falling back to mock functionality...")
            return self._create_mock_corpus()

    def load_corpus(self) -> bool:
        """Load the ETCBC DSS corpus into memory."""
        try:
            if not config.paths.corpus_dir.exists():
                if not self.download_corpus():
                    return False

            # Check if we have Text-Fabric available
            try:
                import tf
                from tf.app import use
            except ImportError:
                print("Text-Fabric not available. Install with: pip install text-fabric")
                print("For now, creating mock functionality...")
                return self._create_mock_corpus()

            # Load actual Text-Fabric corpus
            try:
                self.tf = use("ETCBC/dss", version="0.1", checkout="clone")
                self.corpus_loaded = True
                self.available_features = set(self.tf.api.Fall())
                print(f"ETCBC DSS corpus loaded successfully. Features: {len(self.available_features)}")
                return True

            except Exception as e:
                print(f"Error loading Text-Fabric corpus: {e}")
                print("Falling back to mock functionality...")
                return self._create_mock_corpus()

        except Exception as e:
            print(f"Error loading ETCBC DSS corpus: {e}")
            return False

    def _create_mock_corpus(self) -> bool:
        """Create mock corpus functionality for development."""
        print("Using mock ETCBC DSS corpus functionality")

        # Enhanced mock data structure with realistic DSS variants
        self.mock_data = {
            "isaiah": {
                # Isaiah 14:4 - from 1QIsa-a
                (14, 4): {
                    "glyphs": "מַדְהֵבָה",
                    "lexemes": ["מַדְהֵבָה"],
                    "morph": ["noun"],
                    "manuscript": "1QIsa-a",
                    "notes": "Spelling variant: מַדְהֵבָה vs MT מַדְהֵבָה"
                },
                # Isaiah 21:8 - from 1QIsa-a
                (21, 8): {
                    "glyphs": "הָרֹאֶה",
                    "lexemes": ["הָרֹאֶה"],
                    "morph": ["participle"],
                    "manuscript": "1QIsa-a",
                    "notes": "Aramaizing form: הָרֹאֶה vs MT הָרֹאֶה"
                },
                # Isaiah 36:5 - from 1QIsa-a
                (36, 5): {
                    "glyphs": "אָמַרְתָּה",
                    "lexemes": ["אָמַרְתָּה"],
                    "morph": ["verb"],
                    "manuscript": "1QIsa-a",
                    "notes": "Aramaizing ending: אָמַרְתָּה vs MT אָמַרְתָּ"
                },
                # Isaiah 38:13 - from 1QIsa-a
                (38, 13): {
                    "glyphs": "שִׁוִּיתִי",
                    "lexemes": ["שִׁוִּיתִי"],
                    "morph": ["verb"],
                    "manuscript": "1QIsa-a",
                    "notes": "Aramaizing form: שִׁוִּיתִי vs MT שִׁוִּיתִי"
                }
            },
            "samuel_1": {
                # 1 Samuel 1:22 - from 4QSama
                (1, 22): {
                    "glyphs": "וְחַנָּה לֹא תַעֲלֶה",
                    "lexemes": ["וְ", "חַנָּה", "לֹא", "תַעֲלֶה"],
                    "morph": ["conj", "proper_name", "neg", "verb"],
                    "manuscript": "4QSama",
                    "notes": "Different verbal form: תַעֲלֶה vs MT תָּעָלֶה"
                },
                # 1 Samuel 1:24 - from 4QSama
                (1, 24): {
                    "glyphs": "וְתַעֲלֵהוּ עִמָּהּ בִּפְרִים שְׁלֹשָׁה",
                    "lexemes": ["וְ", "תַעֲלֵהוּ", "עִמָּהּ", "בִּ", "פְרִים", "שְׁלֹשָׁה"],
                    "morph": ["conj", "verb", "prep", "prep", "noun", "adj"],
                    "manuscript": "4QSama",
                    "notes": "Shorter text: omits details about flour and wine"
                },
                # 1 Samuel 2:17 - from 4QSama
                (2, 17): {
                    "glyphs": "וַתְּהִי חַטַּאת הַנְּעָרִים גְּדֹלָה מְאֹד",
                    "lexemes": ["וַתְּהִי", "חַטַּאת", "הַ", "נְּעָרִים", "גְּדֹלָה", "מְאֹד"],
                    "morph": ["verb", "noun", "art", "noun", "adj", "adv"],
                    "manuscript": "4QSama",
                    "notes": "Different word order and morphology"
                },
                # 1 Samuel 2:20 - from 4QSama
                (2, 20): {
                    "glyphs": "וַיְבָרֶךְ עֵלִי אֶת אֶלְקָנָה וְאֶת אִשְׁתּוֹ",
                    "lexemes": ["וַ", "יְבָרֶךְ", "עֵלִי", "אֶת", "אֶלְקָנָה", "וְ", "אֶת", "אִשְׁתּוֹ"],
                    "morph": ["conj", "verb", "proper_name", "prep", "proper_name", "conj", "prep", "noun"],
                    "manuscript": "4QSama",
                    "notes": "Shorter blessing text"
                },
                # 1 Samuel 11:8 - from 4QSama
                (11, 8): {
                    "glyphs": "וַיִּפְקְדֵם בַּבָּזֶק וַיִּהְיוּ בְּנֵי יִשְׂרָאֵל שְׁלֹשׁ מֵאוֹת אָלֶף",
                    "lexemes": ["וַ", "יִּפְקְדֵם", "בַּ", "בָּזֶק", "וַ", "יִּהְיוּ", "בְּנֵי", "יִשְׂרָאֵל", "שְׁלֹשׁ", "מֵאוֹת", "אָלֶף"],
                    "morph": ["conj", "verb", "prep", "proper_name", "conj", "verb", "noun", "proper_name", "num", "num", "num"],
                    "manuscript": "4QSama",
                    "notes": "Different numbers: שְׁלֹשׁ מֵאוֹת אָלֶף vs MT שְׁלֹשִׁים אָלֶף"
                },
                # 1 Samuel 17:4 - from 4QSama
                (17, 4): {
                    "glyphs": "וַיֵּצֵא אִישׁ הַבֵּנַיִם מִמַּחֲנוֹת פְּלִשְׁתִּים גָּלְיָת שְׁמוֹ מִגַּת",
                    "lexemes": ["וַ", "יֵּצֵא", "אִישׁ", "הַ", "בֵּנַיִם", "מִ", "מַּחֲנוֹת", "פְּלִשְׁתִּים", "גָּלְיָת", "שְׁמוֹ", "מִ", "גַּת"],
                    "morph": ["conj", "verb", "noun", "art", "noun", "prep", "noun", "proper_name", "proper_name", "noun", "prep", "proper_name"],
                    "manuscript": "4QSama",
                    "notes": "Different height description: omits cubits measurement"
                }
            },
            "samuel_2": {
                # 2 Samuel 12:14 - from 4QSamb
                (12, 14): {
                    "glyphs": "אַךְ כִּי נִאַץ נִאַצְתָּ אֶת אוֹיְבֵי יְהוָה",
                    "lexemes": ["אַךְ", "כִּי", "נִאַץ", "נִאַצְתָּ", "אֶת", "אוֹיְבֵי", "יְהוָה"],
                    "morph": ["adv", "conj", "verb", "verb", "prep", "noun", "proper_name"],
                    "manuscript": "4QSamb",
                    "notes": "Additional phrase about despising enemies of YHWH"
                }
            }
        }

        self.corpus_loaded = True
        self.available_features = {"glyphs", "lexemes", "morph", "otype", "biblical"}
        print("Mock ETCBC DSS corpus created successfully")
        return True

    def get_text(self, book: str, chapter: int, verse: int,
                features: List[str] = None) -> Dict[str, Any]:
        """Get DSS text for a specific verse."""
        if not self.corpus_loaded:
            if not self.load_corpus():
                return {}

        if features is None:
            features = ["glyphs", "lexemes"]

        # Real Text-Fabric implementation
        if self.tf:
            try:
                # Import TF components
                from tf.fabric import Fabric

                # Load DSS corpus if not already loaded
                if not hasattr(self, '_dss_loaded'):
                    self._dss_loaded = False
                    try:
                        TF_LOCATION = config.paths.corpus_dir
                        DSS_MODULE = 'dss'

                        # Initialize Text-Fabric for DSS
                        TF = Fabric(locations=TF_LOCATION, modules=DSS_MODULE, silent=True)
                        self.api = TF.load('''
                            book chapter verse
                            glyph lex
                            otype
                        ''', silent=True)

                        if self.api:
                            self.F, self.L, self.T = self.api.F, self.api.L, self.api.T
                            self._dss_loaded = True
                            print("DSS Text-Fabric corpus loaded successfully")
                        else:
                            print("Failed to load DSS Text-Fabric API")
                            return {}

                    except Exception as e:
                        print(f"Error loading DSS corpus: {e}")
                        return {}

                if not self._dss_loaded:
                    return {}

                # Search for verses matching the criteria
                result = {}

                # Find all verses that match book, chapter, verse
                verses = []
                for v in self.F.otype.s('verse'):
                    if (self.F.book.v(v) == book and
                        self.F.chapter.v(v) == chapter and
                        self.F.verse.v(v) == verse):
                        verses.append(v)

                if not verses:
                    return {}  # No matching verses found

                # Collect text from all matching verses
                for feature in features:
                    if feature == "glyphs":
                        # Get all signs (glyphs) from the verse
                        verse_text = ""
                        for v in verses:
                            signs = self.L.d(v, otype='sign')
                            for sign in signs:
                                glyph = self.F.glyph.v(sign)
                                if glyph:  # Skip empty glyphs
                                    verse_text += glyph
                        result["glyphs"] = verse_text

                    elif feature == "lexemes":
                        # Get lexemes from words in the verse
                        verse_lexemes = []
                        for v in verses:
                            words = self.L.d(v, otype='word')
                            for word in words:
                                lex = self.F.lex.v(word)
                                if lex:
                                    verse_lexemes.append(lex)
                        result["lexemes"] = verse_lexemes

                    elif feature == "text":
                        # Full text reconstruction
                        verse_text = ""
                        for v in verses:
                            words = self.L.d(v, otype='word')
                            for word in words:
                                # Get the text representation
                                word_text = self.T.text(word, fmt='text-orig-full')
                                verse_text += word_text + " "
                        result["text"] = verse_text.strip()

                return result

            except Exception as e:
                print(f"Error retrieving DSS text from TF: {e}")
                return {}

        # Fallback to mock implementation
        if hasattr(self, 'mock_data') and book in self.mock_data:
            verse_data = self.mock_data[book].get((chapter, verse), {})
            return {feat: verse_data.get(feat, "") for feat in features}

        return {}

    def find_variant_matches(self, mt_text: str, book: str = None,
                           max_results: int = 10) -> List[Dict[str, Any]]:
        """Find DSS variants that match or differ from MT text."""
        if not self.corpus_loaded:
            return []

        matches = []

        # Mock implementation - in reality would search TF corpus
        if hasattr(self, 'mock_data'):
            for book_name, verses in self.mock_data.items():
                if book and book != book_name:
                    continue

                for (chapter, verse), data in verses.items():
                    dss_text = data.get("glyphs", "")
                    if dss_text and dss_text != mt_text:
                        matches.append({
                            "book": book_name,
                            "chapter": chapter,
                            "verse": verse,
                            "mt_text": mt_text,
                            "dss_text": dss_text,
                            "difference_type": "mock_variant",
                            "confidence": 0.8
                        })

                        if len(matches) >= max_results:
                            break

        return matches

    def get_manuscript_info(self, scroll_id: str = None) -> Dict[str, Any]:
        """Get information about DSS manuscripts."""
        # Mock manuscript information
        manuscripts = {
            "1QIsaa": {
                "name": "Great Isaiah Scroll",
                "book": "isaiah",
                "chapters": list(range(1, 67)),
                "completeness": "nearly_complete",
                "variant_count": 22
            },
            "4QSam": {
                "name": "Samuel manuscripts",
                "book": "samuel_1",
                "chapters": list(range(1, 32)),
                "completeness": "fragmentary",
                "variant_count": 15
            }
        }

        if scroll_id:
            return manuscripts.get(scroll_id, {})

        return manuscripts

    def cross_reference_with_mt(self, variants: List[DSSVariant]) -> List[Dict[str, Any]]:
        """Cross-reference DSS variants with MT text."""
        results = []

        for variant in variants:
            # Get DSS text from corpus
            dss_data = self.get_text(variant.book, variant.chapter, variant.verse)

            # Compare with our variant data
            corpus_dss_text = dss_data.get("glyphs", "")

            if corpus_dss_text:
                results.append({
                    "variant": variant,
                    "corpus_dss_text": corpus_dss_text,
                    "our_dss_text": variant.dss_text,
                    "match": corpus_dss_text == variant.dss_text,
                    "similarity_score": self._calculate_similarity(variant.dss_text, corpus_dss_text)
                })

        return results

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if not text1 or not text2:
            return 0.0

        # Simple character overlap (in practice use difflib or similar)
        set1 = set(text1.replace(" ", ""))
        set2 = set(text2.replace(" ", ""))

        if not set1 and not set2:
            return 1.0

        intersection = set1 & set2
        union = set1 | set2

        return len(intersection) / len(union) if union else 0.0

    def enhance_variant_data(self, variant: DSSVariant) -> DSSVariant:
        """Enhance variant data with corpus information."""
        if not self.corpus_loaded:
            return variant

        # Get additional data from corpus
        corpus_data = self.get_text(variant.book, variant.chapter, variant.verse,
                                   ["lexemes", "morph", "biblical"])

        # Enhance variant with corpus data
        enhanced_variant = DSSVariant(
            book=variant.book,
            chapter=variant.chapter,
            verse=variant.verse,
            masoretic_text=variant.masoretic_text,
            dss_text=variant.dss_text or corpus_data.get("glyphs", ""),
            variant_translation_en=variant.variant_translation_en,
            variant_translation_es=variant.variant_translation_es,
            comments_he=variant.comments_he,
            comments_en=variant.comments_en,
            comments_es=variant.comments_es,
            dss_source=variant.dss_source,
            variant_type=variant.variant_type,
            significance=variant.significance
        )

        return enhanced_variant

    def get_statistics(self) -> Dict[str, Any]:
        """Get corpus statistics."""
        stats = {
            "corpus_loaded": self.corpus_loaded,
            "available_features": list(self.available_features) if self.available_features else [],
            "books_available": [],
            "total_manuscripts": 0
        }

        if hasattr(self, 'mock_data'):
            stats["books_available"] = list(self.mock_data.keys())
            stats["total_manuscripts"] = len(self.get_manuscript_info())

        return stats

def main():
    """Test the ETCBC DSS integrator."""
    print("Testing ETCBC DSS Corpus Integration")
    print("=" * 40)

    integrator = ETCBC_DSS_Integrator()

    # Load corpus
    if integrator.load_corpus():
        print("✓ Corpus loaded successfully")

        # Get statistics
        stats = integrator.get_statistics()
        print(f"Statistics: {stats}")

        # Test text retrieval
        isaiah_text = integrator.get_text("isaiah", 1, 1)
        print(f"Isaiah 1:1 data: {isaiah_text}")

        # Test manuscript info
        manuscripts = integrator.get_manuscript_info()
        print(f"Available manuscripts: {list(manuscripts.keys())}")

        # Test variant matching
        matches = integrator.find_variant_matches("חָזוֹן יְשַׁעְיָהוּ", "isaiah")
        print(f"Found {len(matches)} variant matches")

    else:
        print("✗ Failed to load corpus")

if __name__ == "__main__":
    main()
