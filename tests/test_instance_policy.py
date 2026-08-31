import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "dict"))

from instance_policy import (  # noqa: E402
    InstancePolicyConfig,
    classify_tier,
    process_instances,
    resolve_conflict,
)


def instance(number, confidence=0.5, signal=0, source_priority=0):
    return {
        "stable_id": f"id-{number}",
        "book": " Genesis ",
        "chapter": 1,
        "verse": number + 1,
        "word_positions": [0],
        "confidence": confidence,
        "linguistic_signal": signal,
        "canonical_source_priority": source_priority,
        "display": "  café  ",
    }


def test_tiers_and_high_surface_are_bounded_and_retain_full_set():
    config = InstancePolicyConfig()
    assert [classify_tier(n, config) for n in (0, 99, 100, 999, 1000)] == [
        "low", "low", "medium", "medium", "high"
    ]
    result = process_instances((instance(i) for i in range(1001)), config)
    assert result["instance_total"] == 1001
    assert result["instance_surface_count"] == 500
    assert result["omitted_count"] == 501
    assert len(result["instances"]) == 1001
    assert len(result["surface_instances"]) == 500
    assert result["instances"][0]["display"] == "café"


def test_duplicates_keep_highest_confidence_and_findings_are_machine_readable():
    low = instance(1, confidence=0.2)
    high = instance(1, confidence=0.9)
    malformed = {"stable_id": "bad", "book": "Genesis", "chapter": 0, "verse": 2, "confidence": 2}
    result = process_instances([low, high, malformed])
    assert result["instance_total"] == 1
    assert result["instances"][0]["confidence"] == 0.9
    assert {finding["code"] for finding in result["findings"]} >= {
        "duplicate_reference", "malformed_location", "invalid_confidence"
    }


def test_ranking_is_independent_of_input_order_and_conflicts_are_deterministic():
    a = instance(1, 0.7, 1, 0)
    b = instance(2, 0.7, 1, 0)
    first = process_instances([a, b])["instances"]
    second = process_instances([b, a])["instances"]
    assert [x["stable_id"] for x in first] == [x["stable_id"] for x in second]
    winner, needs_review, reason = resolve_conflict([
        {"candidate": "zeta", "confidence": 0.8, "linguistic_signal": 1, "independent_sources": 1},
        {"candidate": "alfa", "confidence": 0.8, "linguistic_signal": 1, "independent_sources": 1},
    ])
    assert winner["candidate"] == "alfa"
    assert needs_review is True
    assert reason == "lexicographic_fallback"