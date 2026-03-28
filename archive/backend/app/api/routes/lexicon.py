"""
Lexicon API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.deps import require_api_key
from app.services.lexicon import LexiconService
from app.data_loaders import dictionary_loader
from app.schemas.lexicon import LexiconResponse

router = APIRouter()

# Initialize service with dependencies
lexicon_service = LexiconService(dictionary_loader)


@router.get("/lexicon/{strong}", response_model=LexiconResponse)
async def get_lexicon_entry(
    strong: str, 
    language: str = Query(None, description="Language filter ('en' or 'es')"),
    hebrew: str | None = Query(None, description="Override Hebrew display word"),
    api_key: str = Depends(require_api_key)
):
    """
    Get lexicon entry for a Strong's number with custom definitions priority
    """
    try:
        entry = lexicon_service.get_lexicon_entry(
            strong,
            language,
            display_hebrew=hebrew,
        )
        if entry is None:
            raise HTTPException(
                status_code=404, detail=f"Strong number '{strong}' not found")
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving lexicon entry: {str(e)}")


@router.get("/search", response_model=list[LexiconResponse])
async def search_lexicon(
    q: str = Query(..., min_length=1,
                   description="Search query (Hebrew or transliteration)"),
    limit: int = Query(
        50, ge=1, le=200, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Results offset for pagination"),
    api_key: str = Depends(require_api_key)
):
    """Search lexicon entries with basic pagination"""
    try:
        results = lexicon_service.search_lexicon(q, limit=limit, offset=offset)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching lexicon: {str(e)}")
