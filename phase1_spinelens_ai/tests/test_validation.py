"""Tests for validation-register helpers."""

from __future__ import annotations

from spinelens import validation as val


def test_evidence_gap_open_and_met() -> None:
    assert val.evidence_gap(2, 5) == {"gap": 3, "status": "open"}
    assert val.evidence_gap(4, 4) == {"gap": 0, "status": "met"}
    # already above requirement -> no negative gap
    assert val.evidence_gap(5, 3) == {"gap": 0, "status": "met"}


def test_register_summary_counts() -> None:
    rows = [
        {"priority": "high", "gap": 3, "required_level": 5},
        {"priority": "high", "gap": 1, "required_level": 4},
        {"priority": "medium", "gap": 0, "required_level": 4},
    ]
    s = val.register_summary(rows)
    assert s["items"] == 3
    assert s["open"] == 2
    assert s["field_validation_items"] == 1
    assert s["by_priority"] == {"high": 2, "medium": 1}


def test_register_summary_empty() -> None:
    s = val.register_summary([])
    assert s["items"] == 0 and s["open"] == 0
