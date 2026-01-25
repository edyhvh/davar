"""
Prefixes service - handles business logic for prefix lookup operations.
"""
from typing import Optional
from app.schemas.prefix import PrefixResponse


class PrefixesService:
    """Service for prefix-related operations."""

    def __init__(self, dictionary_loader):
        self.dictionary_loader = dictionary_loader

    def get_prefix(self, prefix_id: str) -> Optional[PrefixResponse]:
        """
        Get prefix definition by ID.

        Args:
            prefix_id: Prefix ID (e.g., "Hb", "Hc", "Hd")

        Returns:
            PrefixResponse or None if not found
        """
        prefix_data = self.dictionary_loader.get_prefix(prefix_id)

        if not prefix_data:
            return None

        return PrefixResponse(
            id=prefix_id,
            main_form=prefix_data.get('main_form'),
            type=prefix_data.get('type'),
            transliteration_en=prefix_data.get('transliteration_en'),
            transliteration_es=prefix_data.get('transliteration_es'),
            meanings=prefix_data.get('meanings', {}),
            forms=prefix_data.get('forms', []),
            notes=prefix_data.get('notes')
        )
