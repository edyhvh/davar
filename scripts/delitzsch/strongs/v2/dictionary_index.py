"""
Dictionary indexing and loading module.

Builds an efficient index from the Strong's Hebrew dictionary for fast lookup
by normalized Hebrew forms.
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass

from .config import DICTIONARY_PATH, MIN_STEM_LENGTH
from .normalizer import normalize_dictionary_lemma, normalize_hebrew

logger = logging.getLogger(__name__)


@dataclass
class DictionaryEntry:
    """Represents a single Strong's dictionary entry."""
    strong: str
    lemma: str
    normalized_lemma: str
    xlit: str
    derivation: str
    strongs_def: str
    kjv_def: str
    is_root: bool
    root_strong: Optional[str]  # If derived, the parent root
    is_proper_name: bool
    

class DictionaryIndex:
    """
    Indexed Strong's Hebrew dictionary for fast lookup.
    
    Creates multiple indexes:
    1. By normalized lemma (primary lookup)
    2. By Strong's number (for root tracing)
    3. By root relationship (for derived forms)
    """
    
    def __init__(self):
        self.entries: Dict[str, DictionaryEntry] = {}  # strong -> entry
        self.lemma_index: Dict[str, List[str]] = {}  # normalized_lemma -> [strongs]
        self.root_entries: Set[str] = set()  # Set of root Strong's numbers
        self.proper_names: Set[str] = set()  # Set of proper name Strong's numbers
        self._loaded = False
        
    def load(self, dictionary_path: Optional[Path] = None) -> None:
        """
        Load and index the Strong's dictionary.
        
        Args:
            dictionary_path: Path to dictionary JSON file
        """
        path = dictionary_path or DICTIONARY_PATH
        
        if not path.exists():
            raise FileNotFoundError(f"Dictionary not found: {path}")
        
        logger.info(f"Loading dictionary from {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for strong, entry_data in data.items():
            self._process_entry(strong, entry_data)
        
        self._loaded = True
        logger.info(f"Indexed {len(self.entries)} entries, {len(self.root_entries)} roots, {len(self.proper_names)} proper names")
    
    def _process_entry(self, strong: str, data: Dict[str, Any]) -> None:
        """Process a single dictionary entry and add to indexes."""
        lemma = data.get('lemma', '')
        normalized = normalize_dictionary_lemma(lemma)
        
        if not normalized or len(normalized) < MIN_STEM_LENGTH:
            return
        
        derivation = data.get('derivation', '')
        is_root, root_strong = self._analyze_derivation(derivation, strong)
        
        # Detect proper names from various indicators
        is_proper_name = self._detect_proper_name(data, lemma, derivation)
        
        entry = DictionaryEntry(
            strong=strong,
            lemma=lemma,
            normalized_lemma=normalized,
            xlit=data.get('xlit', ''),
            derivation=derivation,
            strongs_def=data.get('strongs_def', ''),
            kjv_def=data.get('kjv_def', ''),
            is_root=is_root,
            root_strong=root_strong,
            is_proper_name=is_proper_name
        )
        
        self.entries[strong] = entry
        
        # Index by normalized lemma
        if normalized not in self.lemma_index:
            self.lemma_index[normalized] = []
        self.lemma_index[normalized].append(strong)
        
        # Track roots
        if is_root:
            self.root_entries.add(strong)
        
        # Track proper names
        if is_proper_name:
            self.proper_names.add(strong)
    
    def _analyze_derivation(self, derivation: str, strong: str) -> Tuple[bool, Optional[str]]:
        """
        Analyze the derivation field to determine if this is a root or derived form.
        
        Returns:
            Tuple of (is_root, parent_root_strong)
        """
        if not derivation:
            return True, None  # Assume root if no derivation info
        
        # Patterns indicating derived forms
        derived_patterns = [
            r'from\s+H(\d+)',  # "from H1234"
            r'from\s+the\s+same\s+as\s+H(\d+)',  # "from the same as H1234"
            r'corresponding\s+to\s+H(\d+)',  # Aramaic correspondence
            r'intensive\s+from\s+H(\d+)',  # Intensive forms
            r'passive\s+participle\s+of\s+H(\d+)',  # Participles
            r'active\s+participle\s+of\s+H(\d+)',  # Active participles
            r'feminine\s+of\s+H(\d+)',  # Feminine forms
            r'feminine\s+passive\s+participle\s+of\s+H(\d+)',  # Fem pass participle
            r'dual\s+of\s+H(\d+)',  # Dual forms
            r'plural\s+of\s+H(\d+)',  # Plural forms
            r'prolongation\s+for\s+H(\d+)',  # Prolongations
            r'contracted\s+from\s+H(\d+)',  # Contracted forms
            r'another\s+form\s+for\s+H(\d+)',  # Alternative forms
            r'or\s+[^;]+\s+from\s+H(\d+)',  # "or X from H####"
            r'by\s+reduplication\s+from\s+H(\d+)',  # Reduplicated forms
            r' denominative\s+from\s+H(\d+)',  # Denominative verbs
        ]
        
        for pattern in derived_patterns:
            match = re.search(pattern, derivation, re.IGNORECASE)
            if match:
                parent = f"H{match.group(1)}"
                return False, parent
        
        # Primitive roots are marked explicitly
        if 'primitive root' in derivation.lower():
            return True, None
        
        # If no clear derivation pattern, assume it's a root
        return True, None
    
    def _detect_proper_name(self, data: Dict[str, Any], lemma: str, derivation: str) -> bool:
        """
        Detect if this entry is a proper name.
        
        Uses multiple heuristics:
        1. Capitalized transliteration
        2. Definition mentions "name of"
        3. Known proper name patterns
        """
        xlit = data.get('xlit', '')
        strongs_def = data.get('strongs_def', '')
        kjv_def = data.get('kjv_def', '')
        
        # Check if transliteration starts with uppercase
        if xlit and xlit[0].isupper():
            return True
        
        # Check definitions for proper name indicators
        name_indicators = [
            r'name\s+of\s+(a\s+)?(man|woman|place|son|daughter)',
            r'patronymic',
            r'patrial',
            r'[A-Z][a-z]+,\s+(the\s+)?name\s+of',
            r'[A-Z][a-z]+,\s+a\s+(son|daughter|place)',
        ]
        
        for indicator in name_indicators:
            if re.search(indicator, strongs_def, re.IGNORECASE):
                return True
            if re.search(indicator, kjv_def, re.IGNORECASE):
                return True
        
        return False
    
    def lookup_by_lemma(self, normalized_lemma: str) -> List[DictionaryEntry]:
        """
        Look up dictionary entries by normalized lemma.
        
        Args:
            normalized_lemma: Normalized Hebrew lemma
            
        Returns:
            List of matching entries
        """
        if not self._loaded:
            raise RuntimeError("Dictionary not loaded. Call load() first.")
        
        strongs = self.lemma_index.get(normalized_lemma, [])
        return [self.entries[s] for s in strongs]
    
    def lookup_by_strong(self, strong: str) -> Optional[DictionaryEntry]:
        """
        Look up a dictionary entry by Strong's number.
        
        Args:
            strong: Strong's number (e.g., "H1234")
            
        Returns:
            Dictionary entry or None
        """
        if not self._loaded:
            raise RuntimeError("Dictionary not loaded. Call load() first.")
        
        return self.entries.get(strong)
    
    def get_root_strong(self, strong: str) -> Optional[str]:
        """
        Get the root Strong's number for a derived form.
        
        Args:
            strong: Strong's number of potentially derived form
            
        Returns:
            Root Strong's number or None if already root
        """
        entry = self.entries.get(strong)
        if entry and entry.root_strong:
            return entry.root_strong
        return None
    
    def is_proper_name(self, strong: str) -> bool:
        """Check if a Strong's number represents a proper name."""
        return strong in self.proper_names
    
    def is_root(self, strong: str) -> bool:
        """Check if a Strong's number represents a root word."""
        return strong in self.root_entries
    
    def find_best_match(self, normalized_stem: str, is_proper: bool = False) -> Optional[Tuple[str, float]]:
        """
        Find the best matching Strong's number for a normalized stem.
        
        Args:
            normalized_stem: Normalized Hebrew stem
            is_proper: Whether this is potentially a proper name
            
        Returns:
            Tuple of (strong_number, confidence_score) or None
        """
        if not self._loaded:
            raise RuntimeError("Dictionary not loaded. Call load() first.")
        
        if len(normalized_stem) < MIN_STEM_LENGTH:
            return None
        
        # Direct lemma match
        entries = self.lookup_by_lemma(normalized_stem)
        if entries:
            # Prefer roots over derived forms
            roots = [e for e in entries if e.is_root]
            if roots:
                return roots[0].strong, 1.0
            
            # If all derived, return the first one (highest frequency usually)
            return entries[0].strong, 0.9
        
        # Try fuzzy matching for common morphological variations
        # This could be expanded with more sophisticated fuzzy matching
        
        return None
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the loaded dictionary."""
        return {
            'total_entries': len(self.entries),
            'root_entries': len(self.root_entries),
            'proper_names': len(self.proper_names),
            'unique_lemmas': len(self.lemma_index),
        }