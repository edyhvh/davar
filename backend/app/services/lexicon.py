"""
Lexicon service - handles business logic for lexicon/word lookup operations.
"""
from typing import Optional
from app.schemas.lexicon import LexiconResponse, DefinitionItem
from app.data_loaders.dictionary import DictionaryLoader


class LexiconService:
    """Service for lexicon-related operations."""
    
    def __init__(self, dictionary_loader: DictionaryLoader):
        self.dictionary_loader = dictionary_loader
    
    def get_lexicon_entry(self, strong_number: str) -> Optional[LexiconResponse]:
        """
        Get lexicon entry for a Strong number.
        
        Args:
            strong_number: Strong's number (e.g., "H430", "G3056")
        
        Returns:
            LexiconResponse or None if not found
        """
        # Get custom definition first (priority)
        custom_def = self.dictionary_loader.get_custom_definition(strong_number)
        
        # Get full lexicon entry (includes Strong/BDB)
        lexicon_entry = self.dictionary_loader.get_lexicon_entry(strong_number)
        
        if not lexicon_entry and not custom_def:
            return None
        
        # Build definitions list (custom first, then Strong/BDB)
        definitions = []
        if custom_def:
            definitions.append(DefinitionItem(
                text=custom_def.get('definition', ''),
                source='custom',
                language=custom_def.get('language', 'en')
            ))
        
        if lexicon_entry:
            # Add Strong/BDB definitions
            for def_item in lexicon_entry.get('definitions', []):
                definitions.append(DefinitionItem(
                    text=def_item.get('text', ''),
                    source=def_item.get('source', 'strong'),
                    language=def_item.get('language', 'en')
                ))
        
        # Get root information if available
        root = lexicon_entry.get('root') if lexicon_entry else None
        root_strong = lexicon_entry.get('root_strong') if lexicon_entry else None
        root_definitions = None
        
        if root_strong:
            root_entry = self.dictionary_loader.get_lexicon_entry(root_strong)
            if root_entry:
                root_definitions = [
                    DefinitionItem(
                        text=d.get('text', ''),
                        source=d.get('source', 'strong'),
                        language=d.get('language', 'en')
                    )
                    for d in root_entry.get('definitions', [])
                ]
        
        # Get occurrences count
        occurrences_count = lexicon_entry.get('occurrences_count', 0) if lexicon_entry else 0
        
        return LexiconResponse(
            strong_number=strong_number,
            hebrew=lexicon_entry.get('hebrew', '') if lexicon_entry else '',
            transliteration=lexicon_entry.get('transliteration', '') if lexicon_entry else '',
            definitions=definitions,
            root=root,
            root_strong=root_strong,
            root_definitions=root_definitions,
            occurrences_count=occurrences_count
        )
