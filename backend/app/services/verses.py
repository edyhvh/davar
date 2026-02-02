"""
Verses service - handles business logic for verse-related operations.
"""
import logging
from typing import Optional
from app.schemas.verse import VerseResponse, WordResponse, DssVariant, TranslationFootnote
from app.data_loaders.tanaj import TanajLoader
from app.data_loaders.besorah import BesorahLoader
from app.data_loaders.translations import TranslationLoader
from app.data_loaders.variants import VariantLoader
from app.data_loaders.book_mapping import BookNameMapper as BookMapper
from app.data_loaders.translit import TranslitLoader


class VersesService:
    """Service for verse-related operations."""

    def __init__(
        self,
        tanaj_loader: TanajLoader,
        besorah_loader: BesorahLoader,
        translations_loader: TranslationLoader,
        variants_loader: VariantLoader,
        translit_loader: TranslitLoader,
        book_mapper: BookMapper
    ):
        self.tanaj_loader = tanaj_loader
        self.besorah_loader = besorah_loader
        self.translations_loader = translations_loader
        self.variants_loader = variants_loader
        self.translit_loader = translit_loader
        self.book_mapper = book_mapper

    def get_verses(
        self,
        book: str,
        chapter: int,
        language: Optional[str] = None,
        show_dss: bool = False,
        hebrew_only: bool = False
    ) -> list[VerseResponse]:
        """
        Get verses for a book and chapter.

        Args:
            book: English book name
            chapter: Chapter number
            language: Translation language ('es' or 'en')
            show_dss: Whether to include DSS variants
            hebrew_only: Whether to return only Hebrew text (no translations)

        Returns:
            List of VerseResponse objects
        """
        # Normalize book name
        book_en = self.book_mapper.to_english(book)
        if not book_en:
            return []

        # Get Hebrew text (try Tanaj first, then Besorah)
        # OE data uses lowercase book names
        book_oe = book_en.lower()
        verses_data = self.tanaj_loader.get_verses(book_oe, chapter)
        if not verses_data:
            verses_data = self.besorah_loader.get_verses(book_oe, chapter)

        if not verses_data:
            return []

        # Build response
        verses = []
        for verse_data in verses_data:
            verse = self._build_verse_response(
                book_en=book_en,
                verse_data=verse_data,
                language=language,
                show_dss=show_dss,
                hebrew_only=hebrew_only
            )
            verses.append(verse)

        return verses

    def get_verse(
        self,
        book: str,
        chapter: int,
        verse: int,
        language: Optional[str] = None,
        show_dss: bool = False,
        hebrew_only: bool = False
    ) -> Optional[VerseResponse]:
        """Get a single verse for a book and chapter."""
        book_en = self.book_mapper.to_english(book)
        if not book_en:
            return None
        book_oe = book_en.lower()

        verse_data = self.tanaj_loader.load_verse(book_oe, chapter, verse)
        if not verse_data:
            verse_data = self.besorah_loader.load_verse(
                book_oe, chapter, verse)
        if not verse_data:
            return None

        return self._build_verse_response(
            book_en=book_en,
            verse_data=verse_data,
            language=language,
            show_dss=show_dss,
            hebrew_only=hebrew_only
        )

    def iter_verses(
        self,
        book: str,
        chapter: int,
        language: Optional[str] = None,
        show_dss: bool = False,
        hebrew_only: bool = False
    ):
        """Yield VerseResponse items for streaming responses."""
        book_en = self.book_mapper.to_english(book)
        if not book_en:
            return
        book_oe = book_en.lower()

        verses_data = self.tanaj_loader.get_verses(book_oe, chapter)
        if not verses_data:
            verses_data = self.besorah_loader.get_verses(book_oe, chapter)

        for verse_data in verses_data or []:
            yield self._build_verse_response(
                book_en=book_en,
                verse_data=verse_data,
                language=language,
                show_dss=show_dss,
                hebrew_only=hebrew_only
            )

    def _build_verse_response(
        self,
        book_en: str,
        verse_data: dict,
        language: Optional[str],
        show_dss: bool,
        hebrew_only: bool
    ) -> VerseResponse:
        """Build a VerseResponse from raw verse data."""
        words = []
        translit_words = self.translit_loader.get_verse_words(
            book_en.lower(),
            verse_data.get("chapter", 0),
            verse_data.get("verse", 0),
        )

        verse_words = verse_data.get('words', [])
        # Validate transliteration word count matches verse word count
        if verse_words and translit_words and len(translit_words) != len(verse_words):
            logging.warning(
                f"Transliteration word count mismatch for {book_en} "
                f"{verse_data.get('chapter', 0)}:{verse_data.get('verse', 0)}: "
                f"expected {len(verse_words)} words but got {len(translit_words)}. "
                f"Words may be misaligned."
            )

        for idx, word_data in enumerate(verse_words):
            translit_data = (
                translit_words[idx] if idx < len(translit_words) else {}
            )
            word = WordResponse(
                position=idx + 1,
                text=word_data.get('text', ''),
                text_no_nikud=word_data.get('text_no_nikud'),
                strong=word_data.get('strong'),
                morph=word_data.get('morph'),
                prefixes=word_data.get('prefixes', []),
                has_dss_variant=False,
                translit_en=translit_data.get('translit_en'),
                translit_es=translit_data.get('translit_es')
            )
            words.append(word)

        translation = None
        translation_language = None
        translation_footnotes = None
        if not hebrew_only and language:
            translation_data = self.translations_loader.get_translation(
                book_en, verse_data.get('chapter', 0), verse_data.get(
                    'verse', 0), language
            )
            if translation_data:
                translation = translation_data.get("translation")
                footnotes = translation_data.get("footnotes")
                if footnotes:
                    translation_footnotes = [
                        TranslationFootnote(
                            marker=footnote.get("marker", ""),
                            number=footnote.get("number", ""),
                            word=footnote.get("word", ""),
                            explanation=footnote.get("explanation", "")
                        )
                        for footnote in footnotes
                    ]
                translation_language = language

        dss_variants = None
        if show_dss:
            dss_data = self.variants_loader.get_dss_variants(
                book_en, verse_data.get(
                    'chapter', 0), verse_data.get('verse', 0)
            )
            if dss_data:
                dss_variants = []
                for variant in dss_data:
                    dv = DssVariant(
                        book=variant.get('book', book_en),
                        chapter=variant.get('chapter', verse_data.get('chapter', 0)),
                        verse=variant.get('verse', verse_data.get('verse', 0)),
                        position=variant.get('position', 0),
                        dss_word=variant.get('dss_word', ''),
                        masoretic_word=variant.get('masoretic_word', ''),
                        comment_v2_en=variant.get('comment_v2_en'),
                        comment_v2_es=variant.get('comment_v2_es'),
                        comment_v2_he=variant.get('comment_v2_he'),
                        masoretic_strong=variant.get('masoretic_strong'),
                        dss_strong=variant.get('dss_strong')
                    )
                    dss_variants.append(dv)

                    if dv.position > 0 and dv.position <= len(words):
                        words[dv.position - 1].has_dss_variant = True

        return VerseResponse(
            chapter=verse_data.get('chapter', 0),
            verse=verse_data.get('verse', 0),
            hebrew=verse_data.get('hebrew', ''),
            words=words,
            translation=translation,
            translation_language=translation_language,
            translation_footnotes=translation_footnotes,
            dss=dss_variants if show_dss else None
        )
