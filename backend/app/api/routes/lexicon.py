"""
Lexicon API routes
"""

from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import require_api_key
from app.services.lexicon import LexiconService
from app.data_loaders import dictionary_loader
from app.schemas.lexicon import LexiconResponse

router = APIRouter()

# Initialize service with dependencies
lexicon_service = LexiconService(dictionary_loader)

@router.get("/lexicon/{strong}", response_model=LexiconResponse)
async def get_lexicon_entry(strong: str, api_key: str = Depends(require_api_key)):
    """
    Get lexicon entry for a Strong's number with custom definitions priority
    """
    try:
        entry = lexicon_service.get_lexicon_entry(strong)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Strong number '{strong}' not found")
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving lexicon entry: {str(e)}")