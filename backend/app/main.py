"""
Davar FastAPI Backend
Hebrew Scripture API with authentication, caching, and DSS variants
"""

import logging
import uuid
import asyncio
from time import perf_counter
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.api.routes import books, verses, lexicon, prefixes, metadata, export
from app.schemas.error import ErrorResponse
from app.data_loaders import tanaj_loader, besorah_loader, book_mapper
from app.services.books import BooksService
from app.services.ts2009_sync import sync_ts2009_files

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.env == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address,
                  default_limits=[settings.rate_limit])


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


async def _sync_ts2009_in_background(app: FastAPI):
    """Run TS2009 sync without blocking API startup."""
    try:
        result = await asyncio.to_thread(sync_ts2009_files, logger)
        app.state.ts2009_sync = {
            "status": "ready",
            "listed": result.listed,
            "downloaded": result.downloaded,
            "skipped": result.skipped,
        }
        logger.info(
            "TS2009 background sync finished: listed=%s downloaded=%s skipped=%s",
            result.listed,
            result.downloaded,
            result.skipped,
        )
    except Exception as exc:
        app.state.ts2009_sync = {
            "status": "failed",
            "error": str(exc),
        }
        logger.error("TS2009 background sync failed: %s", exc, exc_info=True)


async def _preload_verse_counts_in_background(app: FastAPI):
    """Precompute verse counts after startup to reduce cold-start blocking."""
    metadata = getattr(app.state, "preload_metadata", None) or {}
    chapter_counts = metadata.get("chapter_counts")
    if not isinstance(chapter_counts, dict):
        app.state.metadata_preload_status = "failed"
        return

    try:
        verse_counts = await asyncio.to_thread(_build_verse_counts, chapter_counts)
        metadata["verse_counts"] = verse_counts
        app.state.preload_metadata = metadata
        app.state.metadata_preload_status = "ready"
        logger.info("Finished background preload of verse counts")
    except Exception as exc:
        app.state.metadata_preload_status = "failed"
        logger.error("Background verse-count preload failed: %s", exc, exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Preload lightweight metadata at startup."""
    startup_started_at = perf_counter()

    app.state.ts2009_sync = {"status": "disabled"}
    app.state.ts2009_sync_task = None
    app.state.metadata_preload_status = "running"
    app.state.metadata_preload_task = None

    if settings.supabase_url and settings.supabase_service_key:
        app.state.ts2009_sync = {"status": "running"}
        app.state.ts2009_sync_task = asyncio.create_task(
            _sync_ts2009_in_background(app)
        )
        logger.info("Started TS2009 sync in background")

    books_service = BooksService(tanaj_loader, besorah_loader, book_mapper)
    try:
        books_list = books_service.get_all_books()
        books_payload = [book.model_dump() for book in books_list]
        chapter_counts: dict[str, list[int]] = {}

        for book in books_list:
            book_id = book.id
            chapters = tanaj_loader.get_chapters(
                book_id) or besorah_loader.get_chapters(book_id)
            chapter_counts[book_id] = chapters

        app.state.preload_metadata = {
            "books": books_payload,
            "chapter_counts": chapter_counts,
            "verse_counts": None,
        }
        app.state.metadata_preload_task = asyncio.create_task(
            _preload_verse_counts_in_background(app)
        )
        logger.info("Preloaded metadata for %s books", len(books_payload))
    except Exception as exc:
        logger.error("Failed to preload metadata: %s", exc, exc_info=True)
        app.state.preload_metadata = None
        app.state.metadata_preload_status = "failed"

    startup_elapsed_ms = (perf_counter() - startup_started_at) * 1000
    logger.info("Startup preload completed in %.2fms", startup_elapsed_ms)

    yield

    sync_task = getattr(app.state, "ts2009_sync_task", None)
    if sync_task and not sync_task.done():
        sync_task.cancel()

    metadata_task = getattr(app.state, "metadata_preload_task", None)
    if metadata_task and not metadata_task.done():
        metadata_task.cancel()


# Create FastAPI app
app = FastAPI(
    title="Davar API",
    description="Hebrew Scripture API for contemplative study",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    default_response_class=ORJSONResponse
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# GZip middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    books.router,
    prefix="/api/v1",
    tags=["books"]
)
app.include_router(
    verses.router,
    prefix="/api/v1",
    tags=["verses"]
)
app.include_router(
    lexicon.router,
    prefix="/api/v1",
    tags=["lexicon"]
)
app.include_router(
    prefixes.router,
    prefix="/api/v1",
    tags=["prefixes"]
)
app.include_router(
    metadata.router,
    prefix="/api/v1",
    tags=["metadata"]
)
app.include_router(
    export.router,
    prefix="/api/v1",
    tags=["export"]
)

# Request ID middleware


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to each request for tracing"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Add request ID to logger
    logger.info(f"Request {request_id}: {request.method} {request.url}")

    response = await call_next(request)

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    return response

# Global exception handlers


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"Request {request_id}: HTTP {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail, error_code=str(exc.status_code)).dict()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"Request {request_id}: ValueError - {str(exc)}")

    return JSONResponse(
        status_code=400,
        content=ErrorResponse(detail="Invalid input data",
                              error_code="VALIDATION_ERROR").dict()
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    """Handle missing data files"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"Request {request_id}: FileNotFoundError - {str(exc)}")

    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            detail="Requested resource not found", error_code="NOT_FOUND").dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Request {request_id}: Unexpected error - {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Internal server error",
                              error_code="INTERNAL_ERROR").dict()
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "ts2009_sync": getattr(app.state, "ts2009_sync", {"status": "unknown"}),
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Davar API - Hebrew Scripture Study",
        "docs": "/docs",
        "health": "/health"
    }
