"""
Books API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from typing import Optional
from app.api.deps import require_api_key
from app.services.books import BooksService
from app.data_loaders import tanaj_loader, besorah_loader, book_mapper
from app.schemas.book import BookResponse, BookSection

router = APIRouter()

# Initialize service with dependencies
books_service = BooksService(tanaj_loader, besorah_loader, book_mapper)


@router.get("/books", response_model=list[BookResponse])
async def get_books(
    response: Response,
    api_key: str = Depends(require_api_key),
    section: Optional[BookSection] = Query(
        None, description="Filter by book section")
):
    """
    Get all books with metadata and section filtering support
    """
    try:
        books = books_service.get_all_books(section if section else None)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return books
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving books: {str(e)}")


@router.get("/books/{book}/chapters")
async def get_book_chapters(
    book: str,
    response: Response,
    api_key: str = Depends(require_api_key)
):
    """
    Get list of chapter numbers for a specific book
    """
    try:
        chapters = books_service.get_chapters(book)
        if chapters is None:
            raise HTTPException(
                status_code=404, detail=f"Book '{book}' not found")
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return {"book": book, "chapters": chapters}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving chapters: {str(e)}")


@router.get("/books/lookup/{book_name}", response_model=BookResponse)
async def lookup_book(
    book_name: str,
    response: Response,
    api_key: str = Depends(require_api_key),
    source: Optional[str] = Query(
        None,
        description="Source format (oe, delitzsch, tth, ts2009, dss, auto)",
    ),
):
    """
    Normalize a book name from any source and return canonical metadata.
    """
    try:
        normalized = book_mapper.normalize_book_name(book_name, source or "auto")
        if not normalized:
            raise HTTPException(
                status_code=404,
                detail=f"Book '{book_name}' not found",
            )
        book = books_service.get_book(normalized)
        if not book:
            raise HTTPException(
                status_code=404,
                detail=f"Book '{book_name}' not found",
            )
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return book
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving book: {str(e)}")


@router.get("/books/{book}/chapters/{chapter}/verses")
async def get_chapter_verses(
    book: str,
    chapter: int,
    response: Response,
    api_key: str = Depends(require_api_key)
):
    """
    Get verse count for a specific chapter
    """
    try:
        verse_count = books_service.get_verse_count(book, chapter)
        if verse_count is None:
            raise HTTPException(
                status_code=404, detail=f"Book '{book}' or chapter {chapter} not found")
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return {"book": book, "chapter": chapter, "verse_count": verse_count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving verse count: {str(e)}")
