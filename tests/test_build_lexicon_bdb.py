import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.dict.build_lexicon import extract_bdb_definitions_with_sense
from scripts.dict import validator


BDB_NS = "http://openscriptures.github.com/morphhb/namespace"


def test_extract_bdb_definitions_prefers_primary_homonym_and_keeps_senses():
    bdb_root = ET.fromstring(
        f"""
        <bdb xmlns="{BDB_NS}">
          <entry id="t.ai.aa" type="root" mod="I">
            <w>רָבָה</w>
            <def>be</def>, <def>become</def>, <def>much</def>, <def>many</def>, <def>great</def>
            <sense><stem>Qal</stem>
              <sense n="1"><def>become many</def>, <def>numerous</def></sense>
              <sense n="2">
                <sense n="a"><def>be great</def></sense>
                <sense n="b"><def>grow great</def></sense>
              </sense>
            </sense>
            <sense><stem>Pi</stem>. <def>make large</def>, <def>increase</def></sense>
            <sense><stem>Hiph</stem>.
              <sense n="1"><def>make much</def> or <def>many</def></sense>
              <sense n="2"><def>make great</def></sense>
            </sense>
          </entry>
          <entry id="t.aj.aa" type="root" mod="II">
            <w>רָבָה</w>
            <def>shoot</def>
          </entry>
        </bdb>
        """
    )
    lexical_index = {
        "strong_to_bdb": {"H7235": ["t.ai.aa", "t.aj.aa"]},
        "bdb_to_def": {"t.ai.aa": "be much", "t.aj.aa": "shoot"},
    }

    definitions = extract_bdb_definitions_with_sense(
        "H7235",
        "רָבָה",
        bdb_root,
        lexical_index,
    )

    texts = [definition["text_en"] for definition in definitions]
    assert texts == [
        "be much",
        "become many",
        "numerous",
        "be great",
        "grow great",
        "make large",
        "increase",
        "make much",
        "many",
        "make great",
    ]
    assert "shoot" not in texts
    assert all(text not in texts for text in ["be", "become", "much", "great"])


def test_single_word_synonyms_are_not_collapsed_to_single_word_lexical_gloss():
    bdb_root = ET.fromstring(
        f"""
        <bdb xmlns="{BDB_NS}">
          <entry id="r.bk.aa" type="root" mod="II">
            <w>צוּר</w>
            <def>confine</def>, <def>bind</def>, <def>besiege</def>
          </entry>
        </bdb>
        """
    )
    lexical_index = {
        "strong_to_bdb": {"H6696": ["r.bk.aa"]},
        "bdb_to_def": {"r.bk.aa": "confine"},
    }

    definitions = extract_bdb_definitions_with_sense(
        "H6696",
        "צוּר",
        bdb_root,
        lexical_index,
    )

    assert [definition["text_en"] for definition in definitions] == ["confine", "bind", "besiege"]


def test_validator_flags_fragmented_main_bdb_definitions(tmp_path, monkeypatch):
    roots_dir = tmp_path / "roots"
    words_dir = tmp_path / "words"
    roots_dir.mkdir()
    words_dir.mkdir()
    (roots_dir / "H7235.json").write_text(
        json.dumps(
            {
                "strong_number": "H7235",
                "definitions": [
                    {"text_en": "be", "source": "bdb", "sense": "0"},
                    {"text_en": "become", "source": "bdb", "sense": "0"},
                    {"text_en": "much", "source": "bdb", "sense": "0"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator.config, "LEXICON_ROOTS_DIR", roots_dir)
    monkeypatch.setattr(validator.config, "LEXICON_WORDS_DIR", words_dir)

    result = validator.check_fragmented_main_bdb_definitions()

    assert result["count"] == 1
    assert result["samples"][0]["strong_number"] == "H7235"
