"""
Lexicon processor module.

Handles loading, processing, and updating lexicon JSON files with translations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, NamedTuple

logger = logging.getLogger(__name__)


class LexiconProcessor:
    """Processes lexicon JSON files for translation."""
    
    def __init__(
        self,
        target_lang: str,
        batch_size: int = 50
    ):
        """
        Initialize the processor.

        Args:
            target_lang: Target language code (e.g., 'es', 'pt')
            batch_size: Number of definitions to translate per API call
        """
        from .config import (
            SUPPORTED_LANGUAGES,
            DEFAULT_BATCH_SIZE,
            ROOTS_FILE,
            WORDS_FILE,
            ROOTS_PRETTY_FILE,
            WORDS_PRETTY_FILE,
            validate_language
        )

        if not validate_language(target_lang):
            raise ValueError(f"Unsupported language: {target_lang}")
        
        self.target_lang = target_lang.lower()
        self.text_field = f"text_{self.target_lang}"
        self.batch_size = batch_size

        # Initialize Grok translator
        from .translator import GrokTranslator
        self.translator = GrokTranslator()
    
    def _load_json_file(self, file_path: Path) -> Dict:
        """Load JSON file, handling both minified and pretty formats."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise
    
    def _save_json_file(self, data: Dict, file_path: Path, pretty: bool = False):
        """Save JSON file in minified or pretty format."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    
    def _extract_definitions_to_translate(
        self,
        entry: Dict
    ) -> List[Tuple[int, Dict]]:
        """
        Extract definitions that need translation from an entry.

        Returns list of (index, definition_dict) tuples for definitions
        that need translation, sorted by order field.
        """
        definitions = entry.get('definitions', [])
        to_translate = []

        for idx, defn in enumerate(definitions):
            # Check if translation already exists
            if self.text_field in defn:
                continue

            # Check if we have English text to translate
            text_en = defn.get('text_en') or defn.get('text')
            if text_en:
                to_translate.append((idx, defn))

        # Sort by order field to ensure 1, 2, 3, 4, 5 sequence
        return sorted(to_translate, key=lambda x: x[1].get('order', 999))

    def _sort_definitions_by_order(self, definitions: List[Dict]) -> List[Dict]:
        """
        Sort definitions by order field to ensure 1, 2, 3, 4, 5 sequence.

        Args:
            definitions: List of definition dictionaries

        Returns:
            Sorted list of definitions
        """
        return sorted(definitions, key=lambda d: d.get('order', 999))

    def _update_entry_definitions(
        self,
        entry: Dict,
        translations: List[str],
        indices: List[int]
    ):
        """
        Update entry definitions with translations.
        
        Args:
            entry: Entry dictionary to update
            translations: List of translated texts
            indices: List of definition indices that were translated
        """
        definitions = entry.get('definitions', [])
        
        for idx, translation in zip(indices, translations):
            if idx < len(definitions):
                defn = definitions[idx]
                
                # Migrate 'text' to 'text_en' if needed
                if 'text' in defn and 'text_en' not in defn:
                    defn['text_en'] = defn.pop('text')
                
                # Add translation
                defn[self.text_field] = translation.strip()
    
    def _process_entry(
        self,
        entry: Dict,
        entry_key: str
    ) -> Tuple[int, int]:
        """
        Process a single entry, translating its definitions.

        Returns:
            Tuple of (definitions_processed, definitions_translated)
        """
        definitions_to_translate = self._extract_definitions_to_translate(entry)

        if not definitions_to_translate:
            return 0, 0

        # Extract texts and create keys for batch processing
        texts_to_translate = []
        indices = []
        batch_keys = []

        for idx, defn in definitions_to_translate:
            text_en = defn.get('text_en') or defn.get('text', '')
            texts_to_translate.append(text_en)
            indices.append(idx)

            # Create key for batch processing: {entry_key}-def-{order}
            order = defn.get('order', idx + 1)  # Use order field, fallback to index + 1
            batch_keys.append(f"{entry_key}-def-{order}")
        
        # Translate in batches
        total_translated = 0
        
        for i in range(0, len(texts_to_translate), self.batch_size):
            batch_texts = texts_to_translate[i:i + self.batch_size]
            batch_indices = indices[i:i + self.batch_size]
            batch_keys_subset = batch_keys[i:i + self.batch_size]

            try:
                translations = self.translator.translate_batch(
                    batch_texts,
                    self.target_lang,
                    keys=batch_keys_subset
                )
                
                # Update entry with translations
                self._update_entry_definitions(
                    entry,
                    translations,
                    batch_indices
                )
                
                total_translated += len(translations)
                logger.info(
                    f"Translated {len(translations)} definitions for {entry_key}"
                )
                
            except Exception as e:
                logger.error(
                    f"Failed to translate batch for {entry_key}: {e}"
                )
                # Continue with next batch
        
        return len(definitions_to_translate), total_translated

    def _process_entries_cross_batch(self, entries: Dict) -> Tuple[int, int]:
        """
        Process multiple entries using cross-entry batching for better efficiency.

        Instead of processing each entry individually, this collects definitions
        from all entries and batches them together for optimal API usage.

        Args:
            entries: Dictionary of entries to process

        Returns:
            Tuple of (total_definitions_processed, total_definitions_translated)
        """
        class DefinitionRef(NamedTuple):
            entry_key: str
            definition_idx: int
            text: str
            batch_key: str

        # Collect all definitions that need translation
        definitions_to_translate = []
        total_definitions_processed = 0

        for entry_key, entry in entries.items():
            entry_definitions = self._extract_definitions_to_translate(entry)
            total_definitions_processed += len(entry_definitions)

            for def_idx, defn in entry_definitions:
                text_en = defn.get('text_en') or defn.get('text', '')
                order = defn.get('order', def_idx + 1)
                batch_key = f"{entry_key}-def-{order}"

                definitions_to_translate.append(DefinitionRef(
                    entry_key=entry_key,
                    definition_idx=def_idx,
                    text=text_en,
                    batch_key=batch_key
                ))

        if not definitions_to_translate:
            return 0, 0

        logger.info(f"Collected {len(definitions_to_translate)} definitions to translate across {len(entries)} entries")

        # Batch and translate all definitions together
        total_translated = 0

        for i in range(0, len(definitions_to_translate), self.batch_size):
            batch_refs = definitions_to_translate[i:i + self.batch_size]
            batch_texts = [ref.text for ref in batch_refs]
            batch_keys = [ref.batch_key for ref in batch_refs]

            try:
                translations = self.translator.translate_batch(
                    batch_texts,
                    self.target_lang,
                    keys=batch_keys
                )

                # Distribute translations back to their respective entries
                for ref, translation in zip(batch_refs, translations):
                    entry = entries[ref.entry_key]
                    definitions = entry.get('definitions', [])

                    if ref.definition_idx < len(definitions):
                        defn = definitions[ref.definition_idx]

                        # Migrate 'text' to 'text_en' if needed
                        if 'text' in defn and 'text_en' not in defn:
                            defn['text_en'] = defn.pop('text')

                        # Add translation
                        defn[self.text_field] = translation.strip()

                total_translated += len(translations)
                logger.info(
                    f"Translated batch {i//self.batch_size + 1}: {len(translations)} definitions "
                    f"(total translated: {total_translated}/{len(definitions_to_translate)})"
                )

            except Exception as e:
                logger.error(f"Failed to translate batch starting at index {i}: {e}")
                # Continue with next batch
                continue

        return total_definitions_processed, total_translated

    def process_file(
        self,
        file_path: Path,
        pretty_file_path: Optional[Path] = None,
        strong_number: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Process a lexicon file, translating all definitions.
        
        Args:
            file_path: Path to JSON file to process
            pretty_file_path: Optional path to pretty-printed version
            strong_number: Optional Strong's number to process only that entry
            
        Returns:
            Dictionary with processing statistics
        """
        logger.info(f"Loading file: {file_path}")
        data = self._load_json_file(file_path)
        
        stats = {
            'entries_processed': 0,
            'entries_total': len(data),
            'definitions_processed': 0,
            'definitions_translated': 0,
        }
        
        # Filter entries if strong_number is specified
        entries_to_process = {}
        if strong_number:
            # Try to find entry by key or strong_number field
            if strong_number in data:
                entries_to_process[strong_number] = data[strong_number]
            else:
                # Search by strong_number field
                for key, entry in data.items():
                    if entry.get('strong_number') == strong_number:
                        entries_to_process[key] = entry
                        break
            
            if not entries_to_process:
                logger.warning(f"Strong's number {strong_number} not found")
                return stats
        else:
            entries_to_process = data
        
        logger.info(
            f"Processing {len(entries_to_process)} entries "
            f"(target language: {self.target_lang})"
        )

        # Choose processing method based on whether we're processing a single entry or multiple entries
        if strong_number:
            # For single entry processing, use the original per-entry method
            processed, translated = 0, 0
            for entry_key, entry in entries_to_process.items():
                try:
                    entry_processed, entry_translated = self._process_entry(entry, entry_key)
                    processed += entry_processed
                    translated += entry_translated

                    stats['entries_processed'] += 1

                    if entry_processed > 0:
                        logger.info(
                            f"Entry {entry_key}: {entry_translated}/{entry_processed} definitions translated"
                        )

                except Exception as e:
                    logger.error(f"Error processing entry {entry_key}: {e}")
                    continue
        else:
            # For full processing, use cross-entry batching for better efficiency
            processed, translated = self._process_entries_cross_batch(entries_to_process)
            stats['entries_processed'] = len(entries_to_process)

        stats['definitions_processed'] = processed
        stats['definitions_translated'] = translated
        
        # Save updated file (unless dry run)
        if not dry_run:
            logger.info(f"Saving updated file: {file_path}")
            self._save_json_file(data, file_path, pretty=False)
            
            if pretty_file_path:
                logger.info(f"Saving pretty file: {pretty_file_path}")
                self._save_json_file(data, pretty_file_path, pretty=True)
        else:
            logger.info("DRY RUN MODE - Skipping file save")
        
        return stats
    
    def process_roots(
        self,
        strong_number: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, int]:
        """Process roots.json file."""
        from .config import ROOTS_FILE, ROOTS_PRETTY_FILE

        return self.process_file(
            ROOTS_FILE,
            ROOTS_PRETTY_FILE,
            strong_number,
            dry_run
        )
    
    def process_words(
        self,
        strong_number: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, int]:
        """Process words.json file."""
        from .config import WORDS_FILE, WORDS_PRETTY_FILE

        return self.process_file(
            WORDS_FILE,
            WORDS_PRETTY_FILE,
            strong_number,
            dry_run
        )