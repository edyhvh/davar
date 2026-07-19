from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from scripts.hutter.map_strongs import (
    StrongCandidate,
    align_similar_words,
    best_contextual_custom_match,
    build_unresolved_queue,
    contextual_custom_decision,
    contextual_custom_variant_decision,
    decide_from_indexes,
    load_lexicon_lemmas,
    ocr_crosscheck_decision,
    same_verse_spelling_decision,
    unresolved_reason,
)


def test_context_only_custom_entries_are_not_global_hutter_lemmas(
    tmp_path, monkeypatch
) -> None:
    lexicon_words = tmp_path / "words"
    lexicon_roots = tmp_path / "roots"
    lexicon_words.mkdir()
    lexicon_roots.mkdir()
    custom_definitions = tmp_path / "custom_definitions.json"
    custom_definitions.write_text(
        json.dumps(
            {
                "D0001": {"hebrew": "לִי", "mapping_scope": "instances_only"},
                "D0002": {"hebrew": "מָרְתָה", "mapping_scope": "global"},
                # Missing scope preserves compatibility for existing reviewed
                # corpus entries created before scoping was introduced.
                "D0003": {"hebrew": "תַּלְמוּד"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("scripts.hutter.map_strongs.LEXICON_WORDS_ROOT", lexicon_words)
    monkeypatch.setattr("scripts.hutter.map_strongs.LEXICON_ROOTS_ROOT", lexicon_roots)
    monkeypatch.setattr(
        "scripts.hutter.map_strongs.CUSTOM_DEFINITIONS_PATH", custom_definitions
    )

    lemmas = load_lexicon_lemmas()

    assert "לי" not in lemmas
    assert lemmas["מרתה"] == Counter({"D0002": 2})
    assert lemmas["תלמוד"] == Counter({"D0003": 2})


def test_exact_custom_lemma_matches_whole_pointed_token_without_prefix_leakage() -> None:
    exact_custom = {"לִי": Counter({"D0265": 3})}

    exact = decide_from_indexes("לִי", {}, {}, {}, {}, {}, exact_custom)
    longer = decide_from_indexes("בְּלִי", {}, {}, {}, {}, {}, exact_custom)
    conjoined = decide_from_indexes("וּלִי", {}, {}, {}, {}, {}, exact_custom)

    assert exact is not None
    assert exact.strong == "D0265"
    assert exact.method == "exact_custom_lemma"
    assert longer is None
    assert conjoined is not None
    assert conjoined.strong == "Hc/D0265"
    assert conjoined.prefixes == ("Hc",)


def test_contextual_custom_mapping_handles_hutter_name_spelling_without_position() -> None:
    decision = contextual_custom_decision(
        "לְטִימוֹתֵאוֹס",
        {"D0093": {"טימותיוס"}},
    )

    assert decision is not None
    assert decision.strong == "Hl/D0093"
    assert decision.prefixes == ("Hl",)
    assert decision.method == "verse_context_custom"
    assert "not word position" in decision.evidence


def test_contextual_custom_mapping_rejects_ambiguous_fuzzy_names() -> None:
    match = best_contextual_custom_match(
        "אבגדו",
        {
            "D0001": {"אבגדה"},
            "D0002": {"אבגדי"},
        },
    )

    assert match is None


def test_contextual_custom_mapping_breaks_same_entry_form_ties_deterministically() -> None:
    match = best_contextual_custom_match(
        "הקנא",
        {"D0086": {"קנאי", "הקני"}},
    )

    assert match is not None
    assert match.custom_surface == "הקני"


def test_contextual_variant_propagates_reviewed_form_with_prefix() -> None:
    decision = contextual_custom_variant_decision(
        "וְסְטֶפָנוֹס",
        {"סטפנוס": Counter({"D0015": 2})},
    )

    assert decision is not None
    assert decision.strong == "Hc/D0015"
    assert decision.confidence == "high"
    assert decision.method == "contextual_custom_variant"


def test_unresolved_items_explain_why_positional_mapping_was_rejected() -> None:
    reason = unresolved_reason(
        {"text": "מִלָּה", "strong": "H4405", "prefixes": []}
    )
    queue = build_unresolved_queue(
        [
            {
                "book": "acts",
                "chapter": 1,
                "verse": 4,
                "position": 1,
                "text": "וַיִּקָּהֲלֵם",
                "normalized": "ויקהלמ",
                "reason": reason,
            },
            {
                "book": "acts",
                "chapter": 2,
                "verse": 1,
                "position": 2,
                "text": "וַיִּקָּהֲלֵם",
                "normalized": "ויקהלמ",
                "reason": reason,
            },
        ]
    )

    assert "positional borrowing was rejected" in reason
    assert queue[0]["occurrence_count"] == 2
    assert queue[0]["first_occurrence"] == "acts 1:4#1"


def test_alternate_ocr_alignment_handles_an_inserted_word() -> None:
    aligned = align_similar_words(
        ["ראשון", "אחרון"],
        ["ראשון", "נוסף", "אחרון"],
    )

    assert aligned == {0: 0, 1: 2}


def test_same_verse_spelling_rejects_ambiguous_strongs() -> None:
    decision = same_verse_spelling_decision(
        "מִלִּים",
        [
            {"text": "מלימ", "strong": "H4405", "prefixes": []},
            {"text": "מלימ", "strong": "H4406", "prefixes": []},
        ],
    )

    assert decision is None


def test_same_verse_spelling_accepts_unique_nonpositional_match() -> None:
    decision = same_verse_spelling_decision(
        "מִלִּים",
        [
            {"text": "אחרת", "strong": "H312", "prefixes": []},
            {"text": "מלימ", "strong": "H4405", "prefixes": []},
        ],
    )

    assert decision is not None
    assert decision.strong == "H4405"


def ocr_decision(
    hutter_word: str,
    alternate_word: str,
    *,
    ocr_confidence: str = "medium",
    strong: str = "H1234",
    delitzsch_strongs: tuple[str, ...] = ("H1234",),
    custom_name_forms: dict[str, set[str]] | None = None,
    verse_custom_forms: dict[str, set[str]] | None = None,
):
    candidate = StrongCandidate(strong=strong, prefixes=())
    return ocr_crosscheck_decision(
        hutter_word,
        alternate_word,
        ocr_confidence,
        [
            {"text": f"word-{index}", "strong": item, "prefixes": []}
            for index, item in enumerate(delitzsch_strongs)
        ],
        {},
        {},
        {alternate_word: Counter({candidate: 2})},
        {},
        {},
        {},
        custom_name_forms or {},
        verse_custom_forms or {},
        {},
    )


def test_ocr_crosscheck_rejects_low_confidence_transcription() -> None:
    assert (
        ocr_decision("אבגדה", "אבגדי", ocr_confidence="low")
        is None
    )


def test_ocr_crosscheck_rejects_weak_ordinary_similarity() -> None:
    assert ocr_decision("אבגדה", "אזחטי") is None


def test_ocr_crosscheck_accepts_close_transcription_without_verse_support() -> None:
    decision = ocr_decision(
        "אבגדהוזחטי",
        "אבגדהוזחתי",
        delitzsch_strongs=("H9999",),
    )

    assert decision is not None
    assert decision.strong == "H1234"
    assert decision.method == "ocr_crosscheck"


def test_ocr_crosscheck_accepts_reviewed_proper_name_with_weaker_ocr_spelling() -> None:
    decision = ocr_decision(
        "כשפנוס",
        "סטפנוס",
        strong="D0015",
        delitzsch_strongs=("D0015",),
        custom_name_forms={"D0015": {"סטפנוס"}},
        verse_custom_forms={"D0015": {"סטפנוס"}},
    )

    assert decision is not None
    assert decision.strong == "D0015"


def test_ocr_crosscheck_rejects_different_name_from_same_verse() -> None:
    decision = ocr_decision(
        "פובלים",
        "פובליוס",
        strong="D0024",
        delitzsch_strongs=("D0024",),
        custom_name_forms={"D0024": {"פולוס"}},
        verse_custom_forms={"D0024": {"פולוס"}},
    )

    assert decision is None


def test_image_reviewed_hutter_names_have_lexicon_definitions() -> None:
    definitions = json.loads(
        Path("data/dict/lexicon/custom_definitions.json").read_text()
    )

    assert definitions["D0210"]["transliteration_en"] == "Martha"
    assert definitions["D0211"]["transliteration_en"] == "Caesar"
    assert definitions["D0212"]["transliteration_en"] == "Artemas"
    assert definitions["D0213"]["transliteration_en"] == "Nicopolis"
    assert definitions["D0214"]["transliteration_en"] == "twelve"
    assert definitions["D0215"]["transliteration_en"] == "onah"
    assert definitions["D0216"]["transliteration_en"] == "eizeh"
    assert definitions["D0217"]["transliteration_en"] == "othon"
    assert definitions["D0218"]["transliteration_en"] == "naor"
    assert definitions["D0219"]["transliteration_en"] == "shel"
    assert definitions["D0220"]["transliteration_en"] == "talmud"


def test_image_reviewed_titus_names_use_custom_mappings() -> None:
    mapping = json.loads(
        Path("data/hutter/strong_mappings/titus.json").read_text()
    )
    chapter = next(item for item in mapping["chapters"] if item["chapter"] == 3)
    verse = next(item for item in chapter["verses"] if item["verse"] == 12)
    mapped = {word["text"]: word.get("strong") for word in verse["words"]}

    assert mapped["אַרְטֵמָא"] == "D0212"
    assert mapped["בְּנִיקוֹפּוֹלִיס"] == "D0213"


def test_short_custom_clitics_map_exactly_without_leaking_into_longer_words() -> None:
    assert mapped_words("acts", 1, 6)["לוֹ"] == "D0266"
    assert mapped_words("romans", 2, 12)["בְּלִי"] == "H1097"
    assert mapped_words("romans", 12, 1)["לוֹבָה"] is None


def test_regeneration_safety_review_repairs_clitics_and_false_inner_matches() -> None:
    assert mapped_words("john", 4, 46)["וּבְנוֹ"] == "Hc/H1121"
    assert mapped_words("matthew", 28, 13)["בְּשָׁכְבֵּנוּ"] == "Hb/H7901"
    assert mapped_words("thessalonians1", 5, 11)["וּבְנוּ"] == "Hc/H1129"
    assert mapped_words("corinthians2", 10, 2)["הָלַכְנוּ"] == "H1980"


def test_regeneration_safety_review_uses_image_corrected_matthew_forms() -> None:
    assert mapped_words("matthew", 17, 20)["כְּמוֹ"] == "H3644"
    assert mapped_words("matthew", 17, 20)["גַרְעִין"] == "D0272"
    assert mapped_words("matthew", 19, 13)["הוּגְשׁוּ"] == "H5066"
    assert mapped_words("thessalonians1", 2, 6)["כְּמוֹ"] == "H3644"
    assert mapped_words("titus", 1, 10)["וּבְחוֹ"] is None


def mapped_words(
    book: str, chapter_number: int, verse_number: int
) -> dict[str, str | None]:
    mapping = json.loads(
        Path(f"data/hutter/strong_mappings/{book}.json").read_text()
    )
    chapter = next(
        item for item in mapping["chapters"] if item["chapter"] == chapter_number
    )
    verse = next(
        item for item in chapter["verses"] if item["verse"] == verse_number
    )
    return {word["text"]: word.get("strong") for word in verse["words"]}


def test_contextual_overrides_disambiguate_identical_hutter_spellings() -> None:
    assert mapped_words("john", 14, 8)["דִּינוּ"] == "H1767"
    assert mapped_words("mark", 14, 64)["דִּינוּ"] == "H1777"
    assert mapped_words("mark", 15, 26)["דִּינוֹ"] == "H1779"


def test_image_reviewed_numeral_abbreviation_is_mapped() -> None:
    words = mapped_words("revelation", 7, 8)

    assert words["(י״ב)"] == "D0214"


def test_repeated_forms_reviewed_against_images_are_mapped() -> None:
    assert mapped_words("luke", 24, 37)["וַיִּבָּהֲלוּ"] == "Hc/H926"
    assert mapped_words("mark", 11, 8)["וַיַּצִּיעוּ"] == "Hc/H3331"
    assert mapped_words("jude", 1, 21)["וְנִצְרוּ"] == "Hc/H5341"
    assert mapped_words("luke", 17, 14)["נִטְהֲרוּ"] == "H2891"
    assert mapped_words("mark", 11, 29)["תַּעֲנוּ"] == "H6030"
    assert mapped_words("matthew", 21, 33)["שֶׁל"] == "D0219"
    assert mapped_words("galatians", 4, 19)["יֻצַּר"] == "H3335"
    assert mapped_words("luke", 24, 11)["יָצֵר"] == "H3336"
    assert mapped_words("revelation", 22, 7)["יִצֹּר"] == "H5341"
    assert mapped_words("peter2", 3, 16)["נָדִים"] == "H5074"
    assert mapped_words("mark", 14, 44)["אֶשַּׁק"] == "H5401"
    assert mapped_words("john", 5, 14)["נִרְפֵּאתָ"] == "H7495"
    assert mapped_words("mark", 2, 12)["נִבְהָלִים"] == "H926"
    assert mapped_words("romans", 13, 2)["הַשִׁלְטוֹן"] == "Hd/H7983"
    assert mapped_words("matthew", 7, 28)["תַּלְמוּדוֹ׃"] == "D0220"
    assert mapped_words("ephesians", 5, 15)["תִּתְהַלְּכוּ"] == "H1980"


def test_false_repeated_forms_are_removed_by_image_corrections() -> None:
    assert "וַיְבֹהֲלוּ" not in mapped_words("luke", 24, 5)
    assert "וְנַצְרוּ" not in mapped_words("peter2", 3, 17)
    assert "שֶׁל־" not in mapped_words("hebrews", 8, 6)
    assert "יִכְלֶה" not in mapped_words("timothy1", 1, 17)
    assert "נֹדִים" not in mapped_words("john1", 5, 6)
    assert "יִשֶּׁה" not in mapped_words("timothy1", 3, 1)
    assert "לִגְּלוֹת" not in mapped_words("corinthians1", 7, 5)
    assert "נִבְהָלִים" not in mapped_words("john", 5, 21)
    assert "הַבְּחִירִים" not in mapped_words("john", 12, 18)
