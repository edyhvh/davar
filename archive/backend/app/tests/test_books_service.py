import unittest
from pathlib import Path

from app.data_loaders.book_mapping import BookNameMapper
from app.data_loaders.besorah import BesorahLoader
from app.data_loaders.tanaj import TanajLoader
from app.services.books import BooksService


class BooksServiceTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parents[3]
        data_root = project_root / "data"
        self.book_mapper = BookNameMapper()
        self.tanaj_loader = TanajLoader(str(data_root))
        self.besorah_loader = BesorahLoader(str(data_root))
        self.books_service = BooksService(
            self.tanaj_loader,
            self.besorah_loader,
            self.book_mapper,
        )

    def test_get_all_books_count(self):
        books = self.books_service.get_all_books()
        self.assertEqual(len(books), 66)
        orders = [book.order for book in books]
        self.assertEqual(orders, sorted(orders))
        self.assertEqual(orders[0], 1)
        self.assertEqual(orders[-1], 66)

    def test_abbreviation_resolves_to_book(self):
        normalized = self.book_mapper.normalize_book_name("1kgs")
        self.assertEqual(normalized, "Kings1")
        if normalized is None:
            self.fail("Expected normalization to return 'Kings1'")
        book = self.books_service.get_book(normalized)
        self.assertIsNotNone(book)
        if book:
            self.assertEqual(book.id, "kings1")
            self.assertEqual(book.name, "Kings1")


if __name__ == "__main__":
    unittest.main()
