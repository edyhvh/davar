"""
Data models for transliteration pipeline.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class WordItem:
    book_id: str
    chapter: int
    verse: int
    word_index: int
    text: str
    source: str

    @property
    def word_id(self) -> str:
        return f"{self.book_id}:{self.chapter}:{self.verse}:{self.word_index}"


@dataclass
class TransliterationResult:
    translit_en: str
    translit_es: str


@dataclass
class BatchResult:
    results: Dict[str, TransliterationResult]
    input_tokens: int
    output_tokens: int
