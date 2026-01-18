# Pydantic schemas for API models

from .error import ErrorResponse
from .book import BookResponse, BookSection
from .verse import WordResponse, DssVariant, TranslationFootnote, VerseResponse
from .lexicon import LexiconResponse, DefinitionItem
from .prefix import PrefixResponse

__all__ = [
    "ErrorResponse",
    "BookResponse",
    "BookSection",
    "WordResponse",
    "DssVariant",
    "TranslationFootnote",
    "VerseResponse",
    "LexiconResponse",
    "DefinitionItem",
    "PrefixResponse"
]