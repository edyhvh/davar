"""
Main matching logic for assigning Strong's numbers to Hebrew words.

Uses the dictionary index and normalizer to find the best match for each word,
with proper handling of roots vs derived forms and Tanakh name filtering.
"""

import logging
from typing import Optional, Tuple, Dict, List, Any
from dataclasses import dataclass

from .dictionary_index import DictionaryIndex
from .normalizer import (
    normalize_hebrew, 
    extract_stem, 
    get_possible_stems,
    is_pronominal_form
)
from .config import MIN_STEM_LENGTH, PRONOMINAL_SUFFIXES

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of a Strong's number match attempt."""
    strong: Optional[str]
    confidence: float  # 0.0 to 1.0
    match_type: str  # 'exact', 'root', 'derived', 'pronominal', 'none'
    reason: str  # Explanation of the match or failure


class StrongMatcher:
    """
    Matches Hebrew words to Strong's numbers using dictionary lookup.
    
    Key features:
    1. Only assigns root Strong's numbers to actual root forms
    2. Filters proper names to Tanakh-only
    3. Handles pronominal suffixes appropriately
    4. Uses confidence scoring for match quality
    """
    
    def __init__(self, dictionary: DictionaryIndex):
        self.dictionary = dictionary
        self.match_stats = {
            'total_attempts': 0,
            'exact_matches': 0,
            'root_matches': 0,
            'derived_skipped': 0,
            'pronominal_skipped': 0,
            'name_filtered': 0,
            'no_match': 0,
        }
    
    def match(self, word: str, prefixes: List[str], is_proper_name: bool = False) -> MatchResult:
        """
        Attempt to find a Strong's number match for a Hebrew word.
        
        Args:
            word: Hebrew word text (with niqqud)
            prefixes: List of prefix codes
            is_proper_name: Whether this word is marked as a possible proper name
            
        Returns:
            MatchResult with strong number and confidence
        """
        self.match_stats['total_attempts'] += 1
        
        # Skip pronominal forms (preposition + suffix)
        if is_pronominal_form(word, prefixes):
            self.match_stats['pronominal_skipped'] += 1
            return MatchResult(
                strong=None,
                confidence=0.0,
                match_type='pronominal',
                reason='Pronominal suffix form - no Strong\'s assignment'
            )
        
        # Get possible stems for matching
        stems = get_possible_stems(word, prefixes)
        
        if not stems:
            self.match_stats['no_match'] += 0
            return MatchResult(
                strong=None,
                confidence=0.0,
                match_type='none',
                reason='Could not extract valid stem'
            )
        
        # Try each stem variation
        for stem in stems:
            if len(stem) < MIN_STEM_LENGTH:
                continue
            
            result = self._match_stem(stem, is_proper_name)
            if result.strong:
                return result
        
        self.match_stats['no_match'] += 1
        return MatchResult(
            strong=None,
            confidence=0.0,
            match_type='none',
            reason='No matching entry found in dictionary'
        )
    
    def _match_stem(self, stem: str, is_proper_name: bool) -> MatchResult:
        """
        Match a single stem against the dictionary.
        
        Args:
            stem: Normalized Hebrew stem
            is_proper_name: Whether this is potentially a proper name
            
        Returns:
            MatchResult
        """
        from .normalizer import extract_root_candidates
        
        # Get all possible root candidates by stripping suffixes and prefixes
        candidates = extract_root_candidates(stem)
        
        for candidate, transform_type in candidates:
            if len(candidate) < 2:
                continue
            
            # Look up entries by lemma
            entries = self.dictionary.lookup_by_lemma(candidate)
            
            if not entries:
                continue
            
            # Filter by proper name status if needed
            if is_proper_name:
                proper_entries = [e for e in entries if e.is_proper_name]
                if proper_entries:
                    entries = proper_entries
            
            # Separate roots from derived forms
            root_entries = [e for e in entries if e.is_root]
            derived_entries = [e for e in entries if not e.is_root]
            
            # Priority 1: Exact root match
            if root_entries:
                self.match_stats['exact_matches'] += 1
                self.match_stats['root_matches'] += 1
                
                # If multiple roots, pick the one with shortest lemma (most basic)
                best_root = min(root_entries, key=lambda e: len(e.normalized_lemma))
                
                return MatchResult(
                    strong=best_root.strong,
                    confidence=0.95,
                    match_type='root',
                    reason=f'Root match ({transform_type}): {best_root.lemma}'
                )
            
            # Priority 2: Derived form
            if derived_entries:
                best_derived = derived_entries[0]
                self.match_stats['exact_matches'] += 1
                
                return MatchResult(
                    strong=best_derived.strong,
                    confidence=0.85,
                    match_type='derived',
                    reason=f'Derived match ({transform_type}): {best_derived.lemma}'
                )
        
        return MatchResult(
            strong=None,
            confidence=0.0,
            match_type='none',
            reason='No suitable match found after trying all candidates'
        )
    
    def match_batch(self, words: List[Dict[str, Any]]) -> List[MatchResult]:
        """
        Match a batch of words.
        
        Args:
            words: List of word dicts with 'text', 'prefixes', 'possible_proper_name'
            
        Returns:
            List of MatchResults in same order
        """
        results = []
        for word_data in words:
            result = self.match(
                word=word_data.get('text', ''),
                prefixes=word_data.get('prefixes', []),
                is_proper_name=word_data.get('possible_proper_name', False)
            )
            results.append(result)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get matching statistics."""
        total = self.match_stats['total_attempts']
        if total == 0:
            return self.match_stats
        
        stats = self.match_stats.copy()
        stats['success_rate'] = (
            (stats['exact_matches']) / total * 100
        )
        stats['skip_rate'] = (
            (stats['pronominal_skipped'] + stats['derived_skipped'] + stats['name_filtered']) 
            / total * 100
        )
        return stats
    
    def reset_stats(self) -> None:
        """Reset matching statistics."""
        self.match_stats = {
            'total_attempts': 0,
            'exact_matches': 0,
            'root_matches': 0,
            'derived_skipped': 0,
            'pronominal_skipped': 0,
            'name_filtered': 0,
            'no_match': 0,
        }