"""
Verses API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.api.deps import require_api_key
from app.services.verses import VersesService
from app.data_loaders import tanaj_loader, besorah_loader, translation_loader, variant_loader, book_mapper
from app.schemas.verse import VerseResponse

router = APIRouter()

# Initialize service with dependencies
verses_service = VersesService(
    tanaj_loader,
    besorah_loader,
    translation_loader,
    variant_loader,
    book_mapper
)

@router.get("/verses/{book}/{chapter}", response_model=list[VerseResponse])
async def get_verses(
    book: str,
    chapter: int,
    language: Optional[str] = Query(None, description="Translation language ('es' or 'en')"),
    show_dss: bool = Query(False, description="Include DSS variants"),
    hebrew_only: bool = Query(False, description="Return only Hebrew text (no translations)"),
    api_key: str = Depends(require_api_key)
):
    """
    Get verses for a specific book and chapter with translation and DSS support
    """
    try:
        # Validate language parameter
        if language and language not in ["es", "en"]:
            raise HTTPException(status_code=400, detail="Language must be 'es' or 'en'")

        verses = verses_service.get_verses(
            book=book,
            chapter=chapter,
            language=language,
            show_dss=show_dss,
            hebrew_only=hebrew_only
        )

        if not verses:
            raise HTTPException(status_code=404, detail=f"Book '{book}' or chapter {chapter} not found")

        return verses
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving verses: {str(e)}")