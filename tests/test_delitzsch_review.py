import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.delitzsch.review.workflow import (
    LexiconIndex,
    apply_decisions,
    iter_occurrences,
)


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_occurrence_identity_includes_verse(tmp_path):
    parsed = tmp_path / "data" / "delitzsch_parsed"
    write_json(
        parsed / "matthew" / "1.json",
        [
            {
                "chapter": 1,
                "verses": [
                    {
                        "chapter": 1,
                        "verse": 1,
                        "hebrew": "WORD ONE",
                        "words": [{"text": "אָדָם", "strong": None, "prefixes": []}],
                    },
                    {
                        "chapter": 1,
                        "verse": 2,
                        "hebrew": "WORD TWO",
                        "words": [{"text": "דָּוִד", "strong": "H1732", "prefixes": []}],
                    },
                ],
            }
        ],
    )

    occurrences = list(iter_occurrences(parsed, ["matthew"]))

    assert [item.key for item in occurrences] == ["matthew.1.1.0", "matthew.1.2.0"]
    assert occurrences[0].verse == 1
    assert occurrences[1].verse == 2


def test_apply_dry_run_does_not_modify_chapter_or_write_log(tmp_path):
    parsed = tmp_path / "data" / "delitzsch_parsed"
    lexicon_dir = tmp_path / "data" / "dict" / "lexicon" / "words"
    log_dir = tmp_path / "data" / "delitzsch_review" / "decisions"
    chapter_path = parsed / "matthew" / "1.json"
    write_json(
        chapter_path,
        [
            {
                "chapter": 1,
                "verses": [
                    {
                        "chapter": 1,
                        "verse": 1,
                        "hebrew": "WORD",
                        "words": [{"text": "אָדָם", "strong": None, "prefixes": []}],
                    }
                ],
            }
        ],
    )
    write_json(
        lexicon_dir / "H120.json",
        {"strong_number": "H120", "lemma": "אָדָם", "normalized": "אדמ", "definitions": []},
    )
    decisions_path = tmp_path / "batch.json"
    write_json(
        decisions_path,
        {
            "decisions": [
                {
                    "action": "set_strong",
                    "occurrence": {
                        "book": "matthew",
                        "chapter": 1,
                        "verse": 1,
                        "word_index": 0,
                        "text": "אָדָם",
                        "strong": None,
                    },
                    "previous_strong": None,
                    "new_strong": "H120",
                    "confidence": 1.0,
                    "reason": "test",
                    "evidence": ["test"],
                }
            ]
        },
    )

    before = chapter_path.read_text(encoding="utf-8")
    stats = apply_decisions(
        decisions_path,
        parsed,
        LexiconIndex(lexicon_dir),
        log_dir,
        dry_run=True,
    )

    assert stats.word_updates == 1
    assert stats.files_changed == 1
    assert chapter_path.read_text(encoding="utf-8") == before
    assert not log_dir.exists()


def test_apply_create_custom_entry_updates_word_and_custom_dictionary(tmp_path):
    parsed = tmp_path / "data" / "delitzsch_parsed"
    lexicon_dir = tmp_path / "data" / "dict" / "lexicon" / "words"
    custom_path = tmp_path / "data" / "dict" / "lexicon" / "custom_definitions.json"
    log_dir = tmp_path / "data" / "delitzsch_review" / "decisions"
    chapter_path = parsed / "acts" / "1.json"
    write_json(
        chapter_path,
        [
            {
                "chapter": 1,
                "verses": [
                    {
                        "chapter": 1,
                        "verse": 13,
                        "hebrew": "פֶּטְרוֹס",
                        "words": [{"text": "פֶּטְרוֹס", "strong": None, "prefixes": []}],
                    }
                ],
            }
        ],
    )
    write_json(custom_path, {})
    decisions_path = tmp_path / "batch.json"
    write_json(
        decisions_path,
        {
            "decisions": [
                {
                    "action": "create_custom_entry",
                    "custom_key": "D0001",
                    "occurrence": {
                        "book": "acts",
                        "chapter": 1,
                        "verse": 13,
                        "word_index": 0,
                        "text": "פֶּטְרוֹס",
                        "strong": None,
                    },
                    "previous_strong": None,
                    "definition": {
                        "text_en": "Peter",
                        "text_es": "Pedro",
                    },
                    "confidence": 0.9,
                    "reason": "Greek proper name in Delitzsch text",
                    "evidence": ["Acts 1:13"],
                }
            ]
        },
    )

    stats = apply_decisions(
        decisions_path,
        parsed,
        LexiconIndex(lexicon_dir),
        log_dir,
        dry_run=False,
    )

    updated_chapter = json.loads(chapter_path.read_text(encoding="utf-8"))
    custom = json.loads(custom_path.read_text(encoding="utf-8"))
    assert stats.word_updates == 1
    assert stats.definition_updates == 1
    assert updated_chapter[0]["verses"][0]["words"][0]["strong"] == "D0001"
    assert custom["D0001"]["definitions"][0]["text_en"] == "Peter"
    assert custom["D0001"]["nt_instances"][0]["book"] == "acts"


def test_apply_upsert_custom_definition_for_existing_strong(tmp_path):
    parsed = tmp_path / "data" / "delitzsch_parsed"
    lexicon_dir = tmp_path / "data" / "dict" / "lexicon" / "words"
    custom_path = tmp_path / "data" / "dict" / "lexicon" / "custom_definitions.json"
    log_dir = tmp_path / "data" / "delitzsch_review" / "decisions"
    write_json(
        lexicon_dir / "H3442.json",
        {
            "strong_number": "H3442",
            "lemma": "יֵשׁוּעַ",
            "normalized": "ישוע",
            "translit_en": "yeshua",
            "translit_es": "yeshua",
            "definitions": [],
        },
    )
    write_json(custom_path, {})
    decisions_path = tmp_path / "definitions.json"
    write_json(
        decisions_path,
        {
            "decisions": [
                {
                    "action": "upsert_custom_definition",
                    "strong": "H3442",
                    "definition": {
                        "text_en": "YHVH saves",
                        "text_es": "YHVH salva",
                    },
                    "confidence": 0.95,
                    "reason": "Name meaning review",
                    "evidence": ["custom review"],
                }
            ]
        },
    )

    stats = apply_decisions(
        decisions_path,
        parsed,
        LexiconIndex(lexicon_dir),
        log_dir,
        dry_run=False,
    )

    custom = json.loads(custom_path.read_text(encoding="utf-8"))
    assert stats.definition_updates == 1
    assert custom["H3442"]["hebrew"] == "יֵשׁוּעַ"
    assert custom["H3442"]["definitions"][0]["text_es"] == "YHVH salva"


def test_john1_custom_grammar_entries_have_definitions():
    root = Path(__file__).resolve().parents[1]
    custom_path = root / "data" / "dict" / "lexicon" / "custom_definitions.json"
    custom = json.loads(custom_path.read_text(encoding="utf-8"))

    assert custom["D0208"]["definitions"][0]["text_en"]
    assert custom["D0208"]["definitions"][0]["text_es"]
    assert custom["D0209"]["definitions"][0]["text_en"]
    assert custom["D0209"]["definitions"][0]["text_es"]


def test_john1_has_no_null_strongs_after_custom_grammar_pass():
    root = Path(__file__).resolve().parents[1]
    parsed_dir = root / "data" / "delitzsch_parsed" / "john1"
    nulls = []

    for chapter_path in sorted(parsed_dir.glob("*.json"), key=lambda path: int(path.stem)):
        chapter_data = json.loads(chapter_path.read_text(encoding="utf-8"))
        chapter = chapter_data[0]
        for verse in chapter["verses"]:
            for word_index, word in enumerate(verse["words"]):
                if word.get("strong") is None:
                    nulls.append(
                        (
                            chapter["chapter"],
                            verse["verse"],
                            word_index,
                            word.get("text"),
                        )
                    )

    assert nulls == []
