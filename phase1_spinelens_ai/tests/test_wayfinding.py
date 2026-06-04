"""Tests for wayfinder placement optimisation."""

from __future__ import annotations

from spinelens.models import wayfinding as wf


def _setup():
    # demands a..e, weight 1 each
    weights = {d: 1.0 for d in "abcde"}
    covers = {
        "X": {"a", "b", "c"},   # best single (3)
        "Y": {"c", "d"},        # overlaps X on c
        "Z": {"d", "e"},        # complements X with d, e
        "W": {"a"},             # dominated
    }
    return weights, covers


def test_greedy_picks_max_then_complement() -> None:
    weights, covers = _setup()
    picks = wf.greedy_max_coverage(["X", "Y", "Z", "W"], covers, weights, k=2)
    assert picks[0]["node"] == "X"
    assert picks[0]["marginal_gain"] == 3.0
    # second pick should be Z (adds d,e = 2) over Y (adds only d = 1)
    assert picks[1]["node"] == "Z"
    assert picks[1]["marginal_gain"] == 2.0
    assert picks[1]["cumulative_gain"] == 5.0


def test_greedy_stops_when_no_gain() -> None:
    weights = {"a": 1.0}
    covers = {"X": {"a"}, "Y": {"a"}}
    picks = wf.greedy_max_coverage(["X", "Y"], covers, weights, k=5)
    assert len(picks) == 1  # second candidate adds nothing


def test_spacing_constraint_blocks_close_sites() -> None:
    weights, covers = _setup()
    # forbid choosing Z once X is chosen
    too_close = lambda a, b: {a, b} == {"X", "Z"}
    picks = wf.greedy_max_coverage(["X", "Y", "Z", "W"], covers, weights, k=2, too_close=too_close)
    assert picks[0]["node"] == "X"
    assert picks[1]["node"] == "Y"  # Z blocked, Y is next best


def test_coverage_curve_is_monotonic() -> None:
    weights, covers = _setup()
    curve = wf.coverage_curve(["X", "Y", "Z", "W"], covers, weights, max_k=4)
    assert curve == sorted(curve)  # cumulative gain never decreases
    assert curve[-1] == 5.0        # all of a..e covered
