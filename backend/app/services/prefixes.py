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
            hebrew=prefix_data.get('hebrew', ''),
            meaning_en=prefix_data.get('meaning_en', ''),
            meaning_es=prefix_data.get('meaning_es', ''),
            examples=prefix_data.get('examples', [])
        )
