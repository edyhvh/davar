"""
Verses API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from typing import Optional
import hashlib
import orjson
from app.api.deps import require_api_key
from app.services.verses import VersesService
from app.data_loaders import (
    tanaj_loader,
    besorah_loader,
    translation_loader,
    variant_loader,
    book_mapper,
    translit_loader,
    dss_translit_loader,
)
from app.schemas.verse import VerseResponse

router = APIRouter()

# Initialize service with dependencies
verses_service = VersesService(
    tanaj_loader,
    besorah_loader,
    translation_loader,
    variant_loader,
    translit_loader,
    dss_translit_loader,
    book_mapper
)


@router.get("/verses/{book}/{chapter}", response_model=list[VerseResponse])
async def get_verses(
    book: str,
    chapter: int,
    response: Response,
    language: Optional[str] = Query(
        None, description="Translation language ('es' or 'en')"),
    show_dss: bool = Query(False, description="Include DSS variants"),
    hebrew_only: bool = Query(
        False, description="Return only Hebrew text (no translations)"),
    stream: bool = Query(
        False, description="Stream response for large payloads"),
    api_key: str = Depends(require_api_key)
):
    """
    Get verses for a specific book and chapter with translation and DSS support
    """
    try:
        # Validate language parameter
        if language and language not in ["es", "en"]:
            raise HTTPException(
                status_code=400, detail="Language must be 'es' or 'en'")

        etag_seed = f"{book}:{chapter}:{language}:{show_dss}:{hebrew_only}"
        etag = hashlib.sha256(etag_seed.encode("utf-8")).hexdigest()
        headers = {
            "Cache-Control": "public, max-age=31536000, immutable",
            "ETag": f'"{etag}"'
        }

        if stream:
            verse_iterator = verses_service.iter_verses(
                book=book,
                chapter=chapter,
                language=language,
                show_dss=show_dss,
                hebrew_only=hebrew_only
            )
            first_verse = next(verse_iterator, None)
            if not first_verse:
                raise HTTPException(
                    status_code=404, detail=f"Book '{book}' or chapter {chapter} not found")

            def verse_stream():
                yield b"["
                yield orjson.dumps(first_verse.model_dump())
                for verse in verse_iterator:
                    yield b","
                    yield orjson.dumps(verse.model_dump())
                yield b"]"

            return StreamingResponse(
                verse_stream(),
                media_type="application/json",
                headers=headers
            )

        verses = verses_service.get_verses(
            book=book,
            chapter=chapter,
            language=language,
            show_dss=show_dss,
            hebrew_only=hebrew_only
        )

        if not verses:
            raise HTTPException(
                status_code=404, detail=f"Book '{book}' or chapter {chapter} not found")

        for key, value in headers.items():
            response.headers[key] = value

        return verses
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving verses: {str(e)}")


@router.get("/verses/{book}/{chapter}/{verse}", response_model=VerseResponse)
async def get_verse(
    book: str,
    chapter: int,
    verse: int,
    response: Response,
    language: Optional[str] = Query(
        None, description="Translation language ('es' or 'en')"),
    show_dss: bool = Query(False, description="Include DSS variants"),
    hebrew_only: bool = Query(
        False, description="Return only Hebrew text (no translations)"),
    api_key: str = Depends(require_api_key)
):
    """Get a single verse with translation and DSS support"""
    try:
        if language and language not in ["es", "en"]:
            raise HTTPException(
                status_code=400, detail="Language must be 'es' or 'en'")

        verse_response = verses_service.get_verse(
            book=book,
            chapter=chapter,
            verse=verse,
            language=language,
            show_dss=show_dss,
            hebrew_only=hebrew_only
        )

        if not verse_response:
            raise HTTPException(
                status_code=404, detail=f"Book '{book}' chapter {chapter} verse {verse} not found")

        etag_seed = f"{book}:{chapter}:{verse}:{language}:{show_dss}:{hebrew_only}"
        etag = hashlib.sha256(etag_seed.encode("utf-8")).hexdigest()
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        response.headers["ETag"] = f'"{etag}"'

        return verse_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving verse: {str(e)}")
