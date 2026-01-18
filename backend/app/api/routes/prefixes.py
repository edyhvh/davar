"""
Prefixes API routes
"""

from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import require_api_key
from app.services.prefixes import PrefixesService
from app.data_loaders import dictionary_loader
from app.schemas.prefix import PrefixResponse

router = APIRouter()

# Initialize service with dependencies
prefixes_service = PrefixesService(dictionary_loader)

@router.get("/prefixes/{prefix_id}", response_model=PrefixResponse)
async def get_prefix(prefix_id: str, api_key: str = Depends(require_api_key)):
    """
    Get prefix meanings in both languages
    """
    try:
        prefix = prefixes_service.get_prefix(prefix_id)
        if prefix is None:
            raise HTTPException(status_code=404, detail=f"Prefix '{prefix_id}' not found")
        return prefix
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving prefix: {str(e)}")