"""
Metadata API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from app.api.deps import require_api_key

router = APIRouter()


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
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving metadata: {str(e)}")
