import unittest
from pathlib import Path

from app.data_loaders.translations import TTH_BOOK_MAPPING, TS2009_BOOK_MAPPING, TranslationLoader
from app.data_loaders.book_mapping import BookNameMapper


class TranslationMappingTests(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[3]
        self.data_root = self.project_root / "data"
        self.translation_loader = TranslationLoader(str(self.data_root))
        self.book_mapper = BookNameMapper()

    def _json_stems(self, directory: Path) -> set[str]:
        return {path.stem for path in directory.glob("*.json")}

    def test_tth_2_mapping_matches_files(self):
        tth_json_dir = self.data_root / "tth_2" / "json"
        tth_files = self._json_stems(tth_json_dir)
        mapping_values = set(TTH_BOOK_MAPPING.values())
        self.assertEqual(
            tth_files,
            mapping_values,
            "tth_2 mapping must match JSON filenames exactly"
        )

    def test_ts2009_mapping_matches_files(self):
        ts2009_dir = self.data_root / "ts2009"
        ts2009_files = self._json_stems(ts2009_dir)
        mapping_values = set(TS2009_BOOK_MAPPING.values())
        self.assertEqual(
            ts2009_files,
            mapping_values,
            "ts2009 mapping must match JSON filenames exactly"
        )

    def test_tth_2_roundtrip_mapping(self):
        tth_json_dir = self.data_root / "tth_2" / "json"
        for path in tth_json_dir.glob("*.json"):
            english_name = self.book_mapper.to_english(path.stem)
            self.assertIsNotNone(english_name, f"No English mapping for {path.stem}")
            mapped_name = self.translation_loader._english_to_tth_book_name(english_name)
            self.assertEqual(path.stem, mapped_name)

    def test_ts2009_roundtrip_mapping(self):
        ts2009_dir = self.data_root / "ts2009"
        for path in ts2009_dir.glob("*.json"):
            english_name = self.book_mapper.to_english(path.stem)
            self.assertIsNotNone(english_name, f"No English mapping for {path.stem}")
            mapped_name = self.translation_loader._english_to_hebrew_book_name(english_name)
            self.assertEqual(path.stem, mapped_name)


if __name__ == "__main__":
    unittest.main()
