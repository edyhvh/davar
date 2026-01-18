"""
Verses service - handles business logic for verse-related operations.
"""
from typing import Optional
from app.schemas.verse import VerseResponse, WordResponse, DssVariant, TranslationFootnote
from app.data_loaders.tanaj import TanajLoader
from app.data_loaders.besorah import BesorahLoader
from app.data_loaders.translations import TranslationLoader
from app.data_loaders.variants import VariantLoader
from app.data_loaders.book_mapping import BookNameMapper as BookMapper


class VersesService:
    """Service for verse-related operations."""
    
    def __init__(
        self,
        tanaj_loader: TanajLoader,
        besorah_loader: BesorahLoader,
        translations_loader: TranslationLoader,
        variants_loader: VariantLoader,
        book_mapper: BookMapper
    ):
        self.tanaj_loader = tanaj_loader
        self.besorah_loader = besorah_loader
        self.translations_loader = translations_loader
        self.variants_loader = variants_loader
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

        # Get Hebrew text (try Tanaj first, then Besorah)
        # OE data uses lowercase book names
        book_oe = book_en.lower()
        verses_data = self.tanaj_loader.get_verses(book_oe, chapter)
        if not verses_data:
            verses_data = self.besorah_loader.get_verses(book_en, chapter)
        
        if not verses_data:
            return []
        
        # Build response
        verses = []
        for verse_data in verses_data:
            # Build words
            words = []
            for idx, word_data in enumerate(verse_data.get('words', [])):
                word = WordResponse(
                    position=idx + 1,
                    text=word_data.get('text', ''),
                    text_no_nikud=word_data.get('text_no_nikud', ''),
                    strong=word_data.get('strong'),
                    morph=word_data.get('morph'),
                    prefixes=word_data.get('prefixes', []),
                    has_dss_variant=False
                )
                words.append(word)
            
            # Get translation if requested
            translation = None
            translation_language = None
            translation_footnotes = None
            if not hebrew_only and language:
                translation_data = self.translations_loader.get_translation(
                    book_en, chapter, verse_data['verse'], language
                )
                if translation_data:
                    translation = translation_data.get("translation")
                    footnotes = translation_data.get("footnotes")
                    if footnotes:
                        translation_footnotes = []
                        for footnote in footnotes:
                            translation_footnotes.append(TranslationFootnote(
                                marker=footnote.get("marker", ""),
                                number=footnote.get("number", ""),
                                word=footnote.get("word", ""),
                                explanation=footnote.get("explanation", "")
                            ))
                    translation_language = language
            
            # Get DSS variants if requested
            dss_variants = None
            if show_dss:
                dss_data = self.variants_loader.get_dss_variants(
                    book_en, chapter, verse_data['verse']
                )
                if dss_data:
                    dss_variants = []
                    for variant in dss_data:
                        dv = DssVariant(
                            word_position=variant.get('word_position', 0),
                            dss_text=variant.get('dss_text', ''),
                            manuscript=variant.get('manuscript', ''),
                            commentary=variant.get('commentary')
                        )
                        dss_variants.append(dv)

                        # Mark words with DSS variants
                        if dv.word_position > 0 and dv.word_position <= len(words):
                            words[dv.word_position - 1].has_dss_variant = True
            
            verse = VerseResponse(
                chapter=verse_data['chapter'],
                verse=verse_data['verse'],
                hebrew=verse_data.get('hebrew', ''),
                hebrew_no_nikud=verse_data.get('hebrew_no_nikud', ''),
                words=words,
                translation=translation,
                translation_language=translation_language,
                translation_footnotes=translation_footnotes,
                dss=dss_variants if show_dss else None
            )
            verses.append(verse)
        
        return verses
