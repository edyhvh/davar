import json
from pathlib import Path

from scripts.hutter.verse_images import (
    CropBox,
    build_manifest,
    group_by_source_file,
    iter_verse_pointers,
    score_gap_for_cut,
    split_content_box,
    trim_content_bottom_for_trailing_blank,
)
from scripts.hutter.apply_crop_overrides import merge_regenerated_entries


def test_iter_verse_pointers_groups_source_files():
    payload = {
        "chapters": [
            {
                "number": 1,
                "verses": [
                    {
                        "number": 2,
                        "text_nikud": "ב",
                        "source_files": ["000002.png"],
                        "visual_uncertainty": ["check"],
                    },
                    {
                        "number": 1,
                        "text_nikud": "א",
                        "source_files": ["000002.png"],
                    },
                ],
            }
        ]
    }

    grouped = group_by_source_file(iter_verse_pointers("matthew", payload))

    assert list(grouped) == ["000002.png"]
    assert [(item.chapter, item.verse) for item in grouped["000002.png"]] == [(1, 1), (1, 2)]
    assert grouped["000002.png"][1].visual_uncertainty == ["check"]


def test_targeted_regeneration_removes_stale_page_entries():
    existing = [
        {"book": "john", "chapter": 17, "verse": 28, "source_file": "000212.png"},
        {"book": "john", "chapter": 18, "verse": 1, "source_file": "000214.png"},
    ]
    regenerated = [
        {"book": "john", "chapter": 17, "verse": 18, "source_file": "000212.png"}
    ]

    merged = merge_regenerated_entries(existing, regenerated, {"000212.png"})

    assert [(entry["chapter"], entry["verse"]) for entry in merged] == [(17, 18), (18, 1)]


def test_choose_cut_lines_keeps_sequence_balanced():
    from scripts.hutter.verse_images import choose_cut_lines

    gaps = [
        (59, 137),
        (190, 199),
        (210, 254),
        (417, 449),
        (720, 743),
        (839, 850),
        (913, 927),
        (1341, 1367),
        (1554, 1585),
        (1834, 1908),
        (1974, 2004),
    ]

    cuts, notes = choose_cut_lines(gaps, content_top=44, content_bottom=2161, verse_count=7)

    assert notes == []
    assert cuts == [433, 731, 920, 1354, 1569, 1871]


def test_choose_cut_lines_rejects_tiny_gloss_only_final_segment():
    from scripts.hutter.verse_images import choose_cut_lines

    gaps = [
        (528, 535),
        (555, 584),
        (624, 633),
        (655, 667),
        (679, 704),
        (858, 873),
        (909, 922),
        (945, 950),
        (971, 978),
        (1004, 1011),
        (1067, 1080),
        (1119, 1135),
        (1163, 1187),
        (1208, 1220),
        (1232, 1256),
        (1306, 1311),
        (1315, 1322),
        (1364, 1376),
        (1418, 1435),
        (1444, 1450),
        (1459, 1483),
        (1506, 1512),
        (1536, 1544),
        (1559, 1590),
        (1640, 1657),
        (1698, 1723),
        (1747, 1753),
        (1771, 1803),
        (1966, 1992),
        (2013, 2018),
        (2043, 2052),
    ]

    cuts, notes = choose_cut_lines(gaps, content_top=508, content_bottom=2063, verse_count=9)

    assert notes == []
    assert cuts[-1] == 1787
    assert 1979 not in cuts


def test_split_content_box_creates_padded_ordered_bands():
    bands = split_content_box(
        CropBox(left=20, top=100, right=220, bottom=400),
        count=3,
        padding=10,
        image_size=(300, 500),
    )

    assert bands == [
        CropBox(left=10, top=90, right=230, bottom=210),
        CropBox(left=10, top=190, right=230, bottom=310),
        CropBox(left=10, top=290, right=230, bottom=410),
    ]


def test_score_gap_for_cut_prefers_substantial_boundary_gap():
    boundary_gap = (1249, 1275)
    internal_gap = (1375, 1383)

    assert score_gap_for_cut(boundary_gap, target=1340, target_spacing=319) < score_gap_for_cut(
        internal_gap,
        target=1340,
        target_spacing=319,
    )


def test_trim_content_bottom_handles_broken_final_page_blank_tail():
    trimmed, note = trim_content_bottom_for_trailing_blank(
        content_top=58,
        content_bottom=1981,
        gaps=[
            (657, 689),
            (706, 729),
            (740, 758),
            (802, 814),
            (948, 969),
            (975, 993),
            (1005, 1193),
            (1195, 1323),
            (1341, 1369),
            (1371, 1446),
            (1449, 1601),
            (1617, 1648),
            (1656, 1673),
            (1676, 1712),
            (1722, 1929),
            (1938, 1966),
        ],
        image_height=2102,
    )

    assert trimmed == 947
    assert note == "trimmed_trailing_blank:1981->947"


def test_build_manifest_manifest_only(tmp_path: Path):
    staging = tmp_path / "staging"
    output = tmp_path / "verse_images"
    (staging / "output").mkdir(parents=True)
    (staging / "data" / "images" / "hebrew_images" / "matthew").mkdir(parents=True)
    (staging / "output" / "matthew.json").write_text(
        json.dumps(
            {
                "chapters": [
                    {
                        "number": 1,
                        "verses": [
                            {
                                "number": 1,
                                "text_nikud": "א",
                                "source_files": ["000002.png"],
                                "visual_uncertainty": [],
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    entries = build_manifest(
        book="matthew",
        staging_root=staging,
        output_root=output,
        manifest_only=True,
        padding=18,
    )

    assert len(entries) == 1
    assert entries[0].status == "planned"
    assert entries[0].output_image is None
    assert entries[0].crop_box is None
    assert "manifest_only: crop not generated" in entries[0].notes


def test_build_manifest_audit_only_reports_missing_source(tmp_path: Path):
    staging = tmp_path / "staging"
    output = tmp_path / "verse_images"
    (staging / "output").mkdir(parents=True)
    (staging / "data" / "images" / "hebrew_images" / "luke").mkdir(parents=True)
    (staging / "output" / "luke.json").write_text(
        json.dumps(
            {
                "chapters": [
                    {
                        "number": 1,
                        "verses": [
                            {
                                "number": 43,
                                "text_nikud": "א",
                                "source_files": ["manual_correction"],
                                "visual_uncertainty": [],
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    entries = build_manifest(
        book="luke",
        staging_root=staging,
        output_root=output,
        audit_only=True,
    )

    assert len(entries) == 1
    assert entries[0].status == "missing_source"
    assert entries[0].output_image is None
    assert entries[0].crop_box is None
    assert any(note.startswith("missing source image:") for note in entries[0].notes)
