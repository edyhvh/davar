"""
Metadata API routes
"""

import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from app.api.deps import require_api_key
from app.data_loaders import tanaj_loader, besorah_loader

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_verse_counts(chapter_counts: dict[str, list[int]]) -> dict[str, dict[str, int]]:
    """Build verse counts map keyed by book/chapter."""
    verse_counts: dict[str, dict[str, int]] = {}
    for book_id, chapters in chapter_counts.items():
        verse_counts[book_id] = {}
        for chapter in chapters:
            verses = tanaj_loader.get_verses(
                book_id, chapter
            ) or besorah_loader.get_verses(book_id, chapter)
            verse_counts[book_id][str(chapter)] = len(verses)
    return verse_counts


@router.get("/metadata/preload")
async def get_preloaded_metadata(
    request: Request,
    response: Response,
    api_key: str = Depends(require_api_key)
):
    """Return metadata preloaded at application startup"""
    try:
        metadata = getattr(request.app.state, "preload_metadata", None)
        if not metadata:
            raise HTTPException(
                status_code=503, detail="Metadata not available")

        if metadata.get("verse_counts") is None:
            chapter_counts = metadata.get("chapter_counts")
            if not isinstance(chapter_counts, dict):
                raise HTTPException(
                    status_code=503,
                    detail="Metadata verse counts not available",
                )
            logger.info("Computing verse_counts lazily for metadata response")
            verse_counts = await asyncio.to_thread(_build_verse_counts, chapter_counts)
            metadata["verse_counts"] = verse_counts
            request.app.state.preload_metadata = metadata
            request.app.state.metadata_preload_status = "ready"

        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving metadata: {str(e)}")
