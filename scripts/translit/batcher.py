"""
Batching utilities for transliteration requests.
"""

from typing import Iterable, List

from .config import BATCH_TOKEN_BUDGET, estimate_tokens
from .models import WordItem


def _estimate_word_tokens(word: WordItem) -> int:
    base = estimate_tokens(word.text)
    overhead = 8
    return base + overhead


def pack_batches(
    verses: Iterable[List[WordItem]],
    token_budget: int = BATCH_TOKEN_BUDGET
) -> List[List[WordItem]]:
    """
    Pack word items into batches using a mixed strategy:
    keep verses intact when possible, split when a single verse exceeds budget.
    """
    batches: List[List[WordItem]] = []
    current: List[WordItem] = []
    current_tokens = 0

    def flush():
        nonlocal current, current_tokens
        if current:
            batches.append(current)
        current = []
        current_tokens = 0

    for verse_words in verses:
        verse_tokens = sum(_estimate_word_tokens(w) for w in verse_words)

        if verse_tokens > token_budget:
            for word in verse_words:
                word_tokens = _estimate_word_tokens(word)
                if current_tokens + word_tokens > token_budget:
                    flush()
                current.append(word)
                current_tokens += word_tokens
            continue

        if current_tokens + verse_tokens > token_budget:
            flush()

        current.extend(verse_words)
        current_tokens += verse_tokens

    flush()
    return batches
