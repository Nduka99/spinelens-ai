"""Tests for pavilion risk gate."""

from __future__ import annotations

import pytest

from spinelens.models import pavilion as pv


def test_empty_risks_proceed() -> None:
    g = pv.risk_gate({})
    assert g["verdict"] == "proceed"
    assert g["validation_items"] == []


def test_high_risk_requires_validation() -> None:
    g = pv.risk_gate({"helipad": "high", "demand": "low"})
    assert g["verdict"] == "proceed_with_validation"
    assert g["overall_risk"] == "high"
    assert g["validation_items"] == ["helipad"]


def test_blocker_blocks() -> None:
    g = pv.risk_gate({"ownership": "blocker", "helipad": "high"})
    assert g["verdict"] == "blocked"
    assert g["overall_risk"] == "blocker"
    assert set(g["validation_items"]) == {"ownership", "helipad"}


def test_medium_only_proceeds_with_care() -> None:
    g = pv.risk_gate({"footprint": "medium", "movement": "low"})
    assert g["verdict"] == "proceed_with_care"
    assert g["validation_items"] == []


def test_unknown_level_raises() -> None:
    with pytest.raises(ValueError):
        pv.risk_gate({"x": "severe"})
