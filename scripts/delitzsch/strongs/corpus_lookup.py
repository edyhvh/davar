"""
Corpus-based Strong's lookup.

Scans all Delitzsch parsed books to build a stem → Strong's index.
~54% of null-strong words can be auto-assigned at near-perfect accuracy
by matching their consonant stem against forms already known in the corpus.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Hebrew letter codepoints: alef (U+05D0) to tav (U+05EA)
_HEBREW_LETTERS = set(range(0x05D0, 0x05EB))


def _normalize(text: str) -> str:
    """Extract consonant letters only (strips niqqud, cantillation, punctuation)."""
    return ''.join(c for c in text if ord(c) in _HEBREW_LETTERS)


def _strip_prefix_codes(strong: str) -> Optional[str]:
    """Extract bare H#### from 'Hl/Hk/H3442' format."""
    if not strong:
        return None
    if '/' not in strong:
        return strong if (strong[0] == 'H' and len(strong) > 1 and strong[1:].isdigit()) else None
    for part in reversed(strong.split('/')):
        if part and part[0] == 'H' and len(part) > 1 and part[1:].isdigit():
            return part
    return None


class CorpusLookup:
    """
    Builds and queries a corpus-based Strong's index from Delitzsch parsed data.

    For each word already assigned in the corpus:
      - strip niqqud → consonants
      - strip prefix letters (1 per prefix code)
      - record stem → {H####: count}

    Lookup then finds the best candidate for a null-strong word.
    """

    MIN_STEM_LEN = 3        # Reject stems < 3 consonants (e.g. pronoun suffixes כם, הם)
    MIN_FREQ_AUTO = 3       # Must appear ≥ 3 times for auto-assignment
    MIN_DOMINANCE = 0.80    # Top candidate must be ≥ 80% of all occurrences for auto-assign

    def __init__(self) -> None:
        self._index: Dict[str, Dict[str, int]] = {}  # stem → {H####: count}
        self._built = False

    def build(self, parsed_dir: Path) -> None:
        """Scan all book directories and populate the index."""
        total = 0
        for book_dir in sorted(parsed_dir.iterdir()):
            if not book_dir.is_dir() or book_dir.name == 'strongs':
                continue
            for chapter_file in sorted(book_dir.glob('*.json')):
                try:
                    data = json.load(open(chapter_file))
                    for verse in data[0]['verses']:
                        for word in verse['words']:
                            strong = word.get('strong')
                            text = word.get('text', '')
                            if strong is None or not text:
                                continue
                            clean = _strip_prefix_codes(strong)
                            if not clean:
                                continue
                            consonants = _normalize(text)
                            n_pfx = len(word.get('prefixes', []))
                            stem = consonants[n_pfx:] if len(consonants) > n_pfx else consonants
                            if len(stem) < self.MIN_STEM_LEN:
                                continue
                            entry = self._index.setdefault(stem, {})
                            entry[clean] = entry.get(clean, 0) + 1
                            total += 1
                except Exception as e:
                    logger.warning(f'Error scanning {chapter_file}: {e}')
        self._built = True
        logger.info(f'Corpus index: {len(self._index)} stems from {total} words')

    def lookup(self, word_text: str, prefixes: list) -> Tuple[Optional[str], int, bool]:
        """
        Look up a word's consonant stem in the corpus index.

        Args:
            word_text: Full Hebrew word text (with niqqud).
            prefixes: List of prefix codes, e.g. ['Hc', 'Hd']. One code = one dropped consonant.

        Returns:
            (strong, total_count, is_auto_assignable)
            - strong: best matching Strong's number, or None if not found
            - total_count: total corpus sightings for this stem
            - is_auto_assignable: True when confidence is high enough to skip the API
        """
        if not self._built:
            raise RuntimeError('CorpusLookup.build() must be called before lookup()')

        consonants = _normalize(word_text)
        n_pfx = len(prefixes)
        stem = consonants[n_pfx:] if len(consonants) > n_pfx else consonants
        if len(stem) < self.MIN_STEM_LEN:
            return None, 0, False

        candidates = self._index.get(stem)
        if not candidates:
            return None, 0, False

        total = sum(candidates.values())
        best = max(candidates, key=lambda key: candidates[key])
        best_count = candidates[best]
        dominance = best_count / total

        is_auto = best_count >= self.MIN_FREQ_AUTO and dominance >= self.MIN_DOMINANCE
        return best, total, is_auto
