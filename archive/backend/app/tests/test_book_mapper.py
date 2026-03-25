import unittest

from app.data_loaders.book_mapping import BookNameMapper


class BookMapperTests(unittest.TestCase):
    def setUp(self):
        self.book_mapper = BookNameMapper()

    def test_abbreviation_normalization(self):
        cases = {
            "1kgs": "Kings1",
            "2kgs": "Kings2",
            "1sam": "Samuel1",
            "2sam": "Samuel2",
            "1chr": "Chronicles1",
            "2chr": "Chronicles2",
        }
        for abbreviation, expected in cases.items():
            with self.subTest(abbreviation=abbreviation):
                normalized = self.book_mapper.normalize_book_name(abbreviation)
                self.assertEqual(normalized, expected)

    def test_book_metadata_completeness(self):
        books = self.book_mapper.get_all_books()
        self.assertEqual(len(books), 66)
        required_fields = {
            "section",
            "order",
            "chapters",
            "hebrew_name",
            "hebrew_transliteration",
            "spanish_name",
        }
        for book in books:
            with self.subTest(book=book):
                metadata = self.book_mapper.get_book_metadata(book)
                self.assertIsNotNone(metadata)
                if metadata is None:
                    self.fail(f"Missing metadata for {book}")
                self.assertTrue(required_fields.issubset(metadata.keys()))


if __name__ == "__main__":
    unittest.main()
