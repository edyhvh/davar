"""
Lexicon service - handles business logic for lexicon/word lookup operations.
"""
from typing import Optional, List
from app.schemas.lexicon import LexiconResponse, DefinitionItem
from app.data_loaders.dictionary import DictionaryLoader


class LexiconService:
    """Service for lexicon-related operations."""

    def __init__(self, dictionary_loader: DictionaryLoader):
        self.dictionary_loader = dictionary_loader

    def get_lexicon_entry(
        self,
        strong_number: str,
        language: Optional[str] = None,
        display_hebrew: Optional[str] = None,
    ) -> Optional[LexiconResponse]:
        """
        Get lexicon entry for a Strong number.

        Args:
            strong_number: Strong's number (e.g., "H430", "G3056")
            language: Optional language filter ('en' or 'es')

        Returns:
            LexiconResponse or None if not found
        """
        # Get custom definition first (priority)
        custom_def = self.dictionary_loader.get_custom_definition(
            strong_number)

        # Load base entries for words/root data
        words_entry = self.dictionary_loader.load_words_lexicon().get(strong_number)
        roots_entry = self.dictionary_loader.load_roots_lexicon().get(strong_number)

        # Prefer custom definitions for display fields, but keep base data for occurrences
        lexicon_entry = custom_def or words_entry or roots_entry

        if not lexicon_entry and not custom_def and not words_entry and not roots_entry:
            return None

        # Helper to normalize text: remove cantillation and slashes (preserve nikud)
        def _normalize_text(s: str) -> str:
            if not s:
                return ''
            # Remove cantillation U+0591-U+05AF
            s = __import__('re').sub(r"[\u0591-\u05AF]", "", s)
            # Remove slash separators
            s = s.replace('/', '')
            return s.strip()

        def _append_definition_items(
            target: list[DefinitionItem],
            def_item: dict,
            default_source: str,
        ) -> None:
            """Append definition items for both EN/ES when available."""
            text = def_item.get('text')
            language_hint = def_item.get('language')

            if text and not text.strip().startswith('id.:'):
                target.append(DefinitionItem(
                    text=_normalize_text(text),
                    source=def_item.get('source', default_source),
                    language=language_hint or 'en'
                ))
                return

            text_en = def_item.get('text_en')
            if text_en and not text_en.strip().startswith('id.:'):
                target.append(DefinitionItem(
                    text=_normalize_text(text_en),
                    source=def_item.get('source', default_source),
                    language='en'
                ))

            text_es = def_item.get('text_es')
            if text_es and not text_es.strip().startswith('id.:'):
                target.append(DefinitionItem(
                    text=_normalize_text(text_es),
                    source=def_item.get('source', default_source),
                    language='es'
                ))

        # Build definitions list (custom first, then Strong/BDB)
        definitions = []
        if custom_def:
            for def_item in custom_def.get('definitions', []):
                _append_definition_items(definitions, def_item, 'custom')

        if (words_entry or roots_entry) and lexicon_entry != custom_def:
            # Add Strong/BDB definitions
            base_entry = words_entry or roots_entry or {}
            for def_item in base_entry.get('definitions', []):
                _append_definition_items(definitions, def_item, 'strong')

        # Get root information if available
        root = (lexicon_entry or {}).get('root')
        root_strong = (lexicon_entry or {}).get('root_strong')
        root_definitions = None
        root_transliteration = None

        if root_strong:
            root_entry = self.dictionary_loader.get_lexicon_entry(root_strong)
            if root_entry:
                root_transliteration = (
                    root_entry.get('transliteration')
                    or root_entry.get('transliteration_en')
                    or root_entry.get('transliteration_es')
                )
                root_definitions = []
                for def_item in root_entry.get('definitions', []):
                    _append_definition_items(
                        root_definitions, def_item, 'strong')

        # Get occurrences count
        occurrences_count = (lexicon_entry or {}).get('occurrences_count', 0)
        if not occurrences_count:
            occurrences_count = (
                (words_entry or {}).get("occurrences", {})
                .get("total", 0)
            )

        # Build instances list from occurrences and manual instances
        instances = self._build_instances(
            base_entry=words_entry or roots_entry or {},
            custom_entry=custom_def or {},
        )

        # Filter definitions by language if specified
        if language:
            definitions = [d for d in definitions if d.language == language]
            if root_definitions:
                root_definitions = [
                    d for d in root_definitions if d.language == language]

        return LexiconResponse(
            strong_number=strong_number,
            hebrew=(
                (display_hebrew or '').strip()
                or (lexicon_entry or {}).get('hebrew')
                or (lexicon_entry or {}).get('lemma')
                or ''
            ),
            transliteration=(
                (lexicon_entry or {}).get('transliteration')
                or (lexicon_entry or {}).get('transliteration_en')
                or (lexicon_entry or {}).get('transliteration_es')
                or ''
            ),
            definitions=definitions,
            root=root,
            root_strong=root_strong,
            root_transliteration=root_transliteration,
            root_definitions=root_definitions,
            occurrences_count=occurrences_count,
            instances=instances
        )

    def _build_instances(
        self,
        base_entry: dict,
        custom_entry: dict,
    ) -> List[str]:
        """Build list of instance references for display."""
        instances: list[str] = []

        # Occurrences references (words lexicon)
        occurrences = base_entry.get("occurrences", {}) if base_entry else {}
        for ref in occurrences.get("references", []) or []:
            formatted = self._format_occurrence_reference(ref)
            if formatted:
                instances.append(formatted)

        # Custom instance lists (manual / OE / NT)
        for key in ("manual_instances", "oe_instances", "nt_instances"):
            for ref in custom_entry.get(key, []) or []:
                if isinstance(ref, str) and ref.strip():
                    instances.append(ref.strip())

        # De-duplicate while preserving order
        seen = set()
        deduped: list[str] = []
        for ref in instances:
            if ref not in seen:
                seen.add(ref)
                deduped.append(ref)

        return deduped

    def _format_occurrence_reference(self, ref: str) -> str:
        """Format occurrence references like 'prov.27.20' to 'Prov 27:20'."""
        if not ref or not isinstance(ref, str):
            return ""

        parts = ref.split(".")
        if len(parts) != 3:
            return ref

        book_key, chapter, verse = parts
        book = self._format_book_abbr(book_key)
        return f"{book} {chapter}:{verse}"

    def _format_book_abbr(self, abbr: str) -> str:
        """Format book abbreviations from lexicon data."""
        mapping = {
            "gen": "Gen",
            "ex": "Ex",
            "exod": "Exod",
            "lev": "Lev",
            "num": "Num",
            "deut": "Deut",
            "josh": "Josh",
            "judg": "Judg",
            "ruth": "Ruth",
            "1sam": "1Sam",
            "2sam": "2Sam",
            "1kgs": "1Kgs",
            "2kgs": "2Kgs",
            "1chr": "1Chr",
            "2chr": "2Chr",
            "ezra": "Ezra",
            "neh": "Neh",
            "esth": "Esth",
            "job": "Job",
            "ps": "Ps",
            "prov": "Prov",
            "eccl": "Eccl",
            "song": "Song",
            "isa": "Isa",
            "jer": "Jer",
            "lam": "Lam",
            "ezek": "Ezek",
            "dan": "Dan",
            "hos": "Hos",
            "joel": "Joel",
            "amos": "Amos",
            "obad": "Obad",
            "jonah": "Jonah",
            "mic": "Mic",
            "nah": "Nah",
            "hab": "Hab",
            "zeph": "Zeph",
            "hag": "Hag",
            "zech": "Zech",
            "mal": "Mal",
            "matt": "Matt",
            "mark": "Mark",
            "luke": "Luke",
            "john": "John",
            "acts": "Acts",
            "rom": "Rom",
            "1cor": "1Cor",
            "2cor": "2Cor",
            "gal": "Gal",
            "eph": "Eph",
            "phil": "Phil",
            "col": "Col",
            "1thess": "1Thess",
            "2thess": "2Thess",
            "1tim": "1Tim",
            "2tim": "2Tim",
            "titus": "Titus",
            "phlm": "Phlm",
            "heb": "Heb",
            "jas": "Jas",
            "1pet": "1Pet",
            "2pet": "2Pet",
            "1john": "1John",
            "2john": "2John",
            "3john": "3John",
            "jude": "Jude",
            "rev": "Rev",
        }

        key = abbr.lower()
        return mapping.get(key, abbr.capitalize())

    def search_lexicon(self, query: str, limit: int = 50, offset: int = 0) -> list[LexiconResponse]:
        """Search lexicon entries by Hebrew or transliteration."""
        raw_results = self.dictionary_loader.search_lexicon(
            query, limit=limit + offset)
        sliced_results = raw_results[offset:offset + limit]
        results: list[LexiconResponse] = []

        for entry in sliced_results:
            strong_number = entry.get('strong_number') or entry.get('strong')
            if not strong_number:
                continue

            definitions = []
            for def_item in entry.get('definitions', []):
                text = def_item.get('text')
                language = def_item.get('language', 'en')
                if not text:
                    if def_item.get('text_en'):
                        text = def_item.get('text_en')
                        language = 'en'
                    elif def_item.get('text_es'):
                        text = def_item.get('text_es')
                        language = 'es'
                    else:
                        text = ''
                definitions.append(DefinitionItem(
                    text=text,
                    source=def_item.get('source', 'custom'),
                    language=language
                ))

            results.append(LexiconResponse(
                strong_number=strong_number,
                hebrew=entry.get('hebrew'),
                transliteration=entry.get(
                    'transliteration_en') or entry.get('transliteration_es'),
                definitions=definitions,
                root=entry.get('root'),
                root_strong=entry.get('root_strong'),
                root_definitions=None,
                occurrences_count=entry.get('occurrences_count', 0)
            ))

        return results
