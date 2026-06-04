"""Tests for crossing warrant and multi-criteria appraisal."""

from __future__ import annotations

from spinelens.models import crossing as cr


def test_zebra_ok_on_quiet_single_lane() -> None:
    w = cr.crossing_warrant(speed_mph=30, lanes_each_way=1, aadf=5000)
    assert w["zebra_appropriate"] is True
    assert w["reasons"] == []


def test_zebra_blocked_on_multilane_high_flow() -> None:
    w = cr.crossing_warrant(speed_mph=30, lanes_each_way=2, aadf=35141)
    assert w["zebra_appropriate"] is False
    assert w["signal_recommended"] is True
    assert any("lanes each way" in r for r in w["reasons"])
    assert any("AADF" in r for r in w["reasons"])


def test_zebra_blocked_on_speed_alone() -> None:
    w = cr.crossing_warrant(speed_mph=40, lanes_each_way=1, aadf=3000)
    assert w["zebra_appropriate"] is False
    assert any("mph" in r for r in w["reasons"])


def test_multi_criteria_rank_orders_and_normalises() -> None:
    options = {
        "A": {"legibility": 0.9, "cost": 0.5},
        "B": {"legibility": 0.4, "cost": 0.9},
    }
    weights = {"legibility": 3, "cost": 1}  # legibility-led
    ranked = cr.multi_criteria_rank(options, weights)
    assert ranked[0]["option"] == "A"
    # weighted score for A = (0.9*3 + 0.5*1)/4 = 0.8
    assert abs(ranked[0]["score"] - 0.8) < 1e-9
    # component scores preserved for transparency
    assert ranked[0]["legibility"] == 0.9


def test_multi_criteria_zero_weights() -> None:
    ranked = cr.multi_criteria_rank({"A": {"x": 1.0}}, {"x": 0.0})
    assert ranked[0]["score"] == 0.0


def test_collision_rate_per_year() -> None:
    assert cr.collision_rate_per_year(20, 5) == 4.0
    assert cr.collision_rate_per_year(0, 0) == 0.0
