"""Tests for the budget model."""

from __future__ import annotations

from spinelens.models import budget as bg


def test_line_total_range() -> None:
    t = bg.line_total(100, 1.0, 2.0, 3.0)
    assert t == {"low": 100, "central": 200, "high": 300}


def test_sum_costs() -> None:
    a = {"low": 100, "central": 200, "high": 300}
    b = {"low": 10, "central": 20, "high": 30}
    assert bg.sum_costs([a, b]) == {"low": 110, "central": 220, "high": 330}


def test_add_percentage() -> None:
    base = {"low": 100, "central": 200, "high": 300}
    up = bg.add_percentage(base, 10)
    assert up == {"low": 110, "central": 220, "high": 330}


def test_apply_offset_floors_at_zero() -> None:
    cost = {"low": 100, "central": 200, "high": 300}
    off = {"low": 150, "central": 50, "high": 40}
    out = bg.apply_offset(cost, off)
    assert out == {"low": 0, "central": 150, "high": 260}  # low floored at 0


def test_envelope_check() -> None:
    cost = {"low": 800_000, "central": 1_100_000, "high": 1_400_000}
    e = bg.envelope_check(cost, 1_000_000)
    assert e["fits_low"] is True
    assert e["fits_central"] is False
    assert e["fits_high"] is False
    assert e["headroom_central"] == -100_000
