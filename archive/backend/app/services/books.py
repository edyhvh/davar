"""
Books service - handles business logic for book-related operations.
"""
from typing import Optional
from app.schemas.book import BookResponse, BookSection
from app.data_loaders.tanaj import TanajLoader
from app.data_loaders.besorah import BesorahLoader
from app.data_loaders.book_mapping import BookNameMapper as BookMapper


class BooksService:
    """Service for book-related operations."""

    def __init__(
        self,
        tanaj_loader: TanajLoader,
        besorah_loader: BesorahLoader,
        book_mapper: BookMapper
    ):
        self.tanaj_loader = tanaj_loader
        self.besorah_loader = besorah_loader
        self.book_mapper = book_mapper

    def get_all_books(self, section: Optional[str] = None) -> list[BookResponse]:
        """
        Get all books, optionally filtered by section.

        Args:
            section: Optional section filter (torah, neviim, ketuvim, besorah)

        Returns:
            List of BookResponse objects
        """
        books = []

        # Get Tanaj books (Torah, Neviim, Ketuvim)
        tanaj_books = self.tanaj_loader.get_books_metadata()
        for book_data in tanaj_books:
            book_name_en = self.book_mapper.to_english(book_data['name'])
            if not book_name_en:
                continue  # Skip if book name couldn't be normalized

            # Get metadata from book_mapper
            metadata = self.book_mapper.get_book_metadata(book_name_en)
            if not metadata:
                # Fallback to data from loader
                section_str = book_data.get('section', '')
                chapters = book_data.get('total_chapters', 0)
                hebrew_name = book_data.get('hebrew_name', '')
                hebrew_transliteration = book_data.get('tth_name', '')
                spanish_name = book_data.get('spanish_name', '')
            else:
                section_str = metadata.get('section', '')
                chapters = metadata.get('chapters', 0)
                hebrew_name = metadata.get('hebrew_name', '')
                hebrew_transliteration = metadata.get(
                    'hebrew_transliteration', '')
                spanish_name = metadata.get('spanish_name', '')

            # Convert section string to enum
            try:
                book_section = BookSection(section_str)
            except ValueError:
                continue  # Skip if invalid section

            book = BookResponse(
                id=book_name_en.lower(),
                name=book_name_en,
                section=book_section,
                chapters=chapters,
                order=metadata.get('order', 99) if metadata else 99,
                hebrew_name=hebrew_name,
                hebrew_transliteration=hebrew_transliteration,
                spanish_name=spanish_name
            )
            books.append(book)

        # Get Besorah books
        besorah_books = self.besorah_loader.get_books_metadata()
        for book_data in besorah_books:
            book_name_en = self.book_mapper.to_english(book_data['name'])
            if not book_name_en:
                continue  # Skip if book name couldn't be normalized

            # Get metadata from book_mapper
            metadata = self.book_mapper.get_book_metadata(book_name_en)
            if not metadata:
                # Fallback to data from loader
                chapters = book_data.get('total_chapters', 0)
                hebrew_name = book_data.get('hebrew_name', '')
                hebrew_transliteration = book_data.get('tth_name', '')
                spanish_name = book_data.get('spanish_name', '')
            else:
                chapters = metadata.get('chapters', 0)
                hebrew_name = metadata.get('hebrew_name', '')
                hebrew_transliteration = metadata.get(
                    'hebrew_transliteration', '')
                spanish_name = metadata.get('spanish_name', '')

            book = BookResponse(
                id=book_name_en.lower(),
                name=book_name_en,
                section=BookSection.BESORAH,
                chapters=chapters,
                order=metadata.get('order', 99) if metadata else 99,
                hebrew_name=hebrew_name,
                hebrew_transliteration=hebrew_transliteration,
                spanish_name=spanish_name
            )
            books.append(book)

        # Filter by section if provided
        if section:
            if isinstance(section, BookSection):
                books = [b for b in books if b.section == section]
            else:
                books = [b for b in books if b.section.value == section]

        # Sort by canonical order
        books.sort(key=lambda b: b.order)

        return books

    def get_book(self, book_name: str) -> Optional[BookResponse]:
        """
        Get a single book by name.

        Args:
            book_name: English book name (e.g., "Genesis", "Matthew")

        Returns:
            BookResponse or None if not found
        """
        all_books = self.get_all_books()
        for book in all_books:
            if book.id.lower() == book_name.lower():
                return book
        return None

    def get_chapters(self, book_name: str) -> Optional[list[int]]:
        """
        Get list of chapter numbers for a book.

        Args:
            book_name: English book name

        Returns:
            List of chapter numbers or None if book not found
        """
        book = self.get_book(book_name)
        if not book:
            return None

        # Try Tanaj first
        tanaj_chapters = self.tanaj_loader.get_chapters(book_name)
        if tanaj_chapters:
            return tanaj_chapters

        # Try Besorah
        besorah_chapters = self.besorah_loader.get_chapters(book_name)
        if besorah_chapters:
            return besorah_chapters

        return None

    def get_verse_count(self, book_name: str, chapter: int) -> Optional[int]:
        """
        Get verse count for a specific chapter.

        Args:
            book_name: English book name
            chapter: Chapter number

        Returns:
            Verse count or None if not found
        """
        # Try Tanaj first
        verses = self.tanaj_loader.get_verses(book_name, chapter)
        if verses:
            return len(verses)

        # Try Besorah
        verses = self.besorah_loader.get_verses(book_name, chapter)
        if verses:
            return len(verses)

        return None
