"""
Davar FastAPI Backend
Hebrew Scripture API with authentication, caching, and DSS variants
"""

import logging
import uuid
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

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.env == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address,
                  default_limits=[settings.rate_limit])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Preload lightweight metadata at startup."""
    books_service = BooksService(tanaj_loader, besorah_loader, book_mapper)
    try:
        books_list = books_service.get_all_books()
        books_payload = [book.model_dump() for book in books_list]
        chapter_counts: dict[str, list[int]] = {}
        verse_counts: dict[str, dict[str, int]] = {}

        for book in books_list:
            book_id = book.id
            chapters = tanaj_loader.get_chapters(
                book_id) or besorah_loader.get_chapters(book_id)
            chapter_counts[book_id] = chapters
            verse_counts[book_id] = {}
            for chapter in chapters:
                verses = tanaj_loader.get_verses(
                    book_id, chapter) or besorah_loader.get_verses(book_id, chapter)
                verse_counts[book_id][str(chapter)] = len(verses)

        app.state.preload_metadata = {
            "books": books_payload,
            "chapter_counts": chapter_counts,
            "verse_counts": verse_counts
        }
        logger.info("Preloaded metadata for %s books", len(books_payload))
    except Exception as exc:
        logger.error("Failed to preload metadata: %s", exc, exc_info=True)
        app.state.preload_metadata = None

    yield


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
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Davar API - Hebrew Scripture Study",
        "docs": "/docs",
        "health": "/health"
    }
