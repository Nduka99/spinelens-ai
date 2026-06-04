"""Tests for the Route Legibility Index primitives."""

from __future__ import annotations

from spinelens.metrics import legibility as lg


def test_initial_bearing_cardinal_directions() -> None:
    north = lg.initial_bearing((52.48, -1.90), (52.49, -1.90))
    east = lg.initial_bearing((52.48, -1.90), (52.48, -1.89))
    assert north < 1 or north > 359
    assert 89 < east < 91


def test_turn_angles_straight_and_right_angle() -> None:
    straight = lg.turn_angles([(52.48, -1.90), (52.49, -1.90), (52.50, -1.90)])
    assert max(straight) < 1.0
    corner = lg.turn_angles([(52.48, -1.90), (52.49, -1.90), (52.49, -1.89)])
    assert 80 < corner[0] < 100


def test_directness_score_bounds() -> None:
    assert lg.directness_score(100, 100) == 1.0
    assert lg.directness_score(50, 100) == 0.5
    assert lg.directness_score(100, 0) == 0.0


def test_turn_burden_score_extremes() -> None:
    assert lg.turn_burden_score(0, 1.0) == 1.0
    assert lg.turn_burden_score(lg.TURN_REF_DEG_PER_KM, 1.0) == 0.0
    assert lg.turn_burden_score(10, 0) == 0.0


def test_intersection_complexity_score() -> None:
    assert lg.intersection_complexity_score(0, 1.0) == 1.0
    assert lg.intersection_complexity_score(int(lg.DECISION_REF_PER_KM), 1.0) == 0.0


def test_crossing_burden_score() -> None:
    assert lg.crossing_burden_score(0, 1.0) == 1.0
    assert lg.crossing_burden_score(lg.CROSSING_REF_SEVERITY_PER_KM, 1.0) == 0.0


def test_continuity_score_counts_hard_turns() -> None:
    # one ~90 deg turn over a 1 km route
    coords = [(52.48, -1.90), (52.49, -1.90), (52.49, -1.89)]
    assert lg.continuity_score(coords, 1.0) < 1.0
    straight = [(52.48, -1.90), (52.49, -1.90), (52.50, -1.90)]
    assert lg.continuity_score(straight, 1.0) == 1.0


def test_crossing_severity_lookup() -> None:
    assert lg.crossing_severity("primary") == 3.0
    assert lg.crossing_severity("footway") == 0.0
    assert lg.crossing_severity("unknown_class") == 0.0


def test_weighted_score_all_perfect_is_one() -> None:
    comps = {k: 1.0 for k in ("directness", "turn_burden", "intersection_complexity",
                              "crossing_burden", "continuity")}
    assert abs(lg.weighted_legibility_score(comps) - lg.weights_total()) < 1e-9
    assert abs(lg.weights_total() - 1.0) < 1e-9


def test_score_with_weights_normalises() -> None:
    comps = {"a": 0.2, "b": 0.8}
    # Unnormalised equal weights -> simple mean.
    assert abs(lg.score_with_weights(comps, {"a": 1, "b": 1}) - 0.5) < 1e-9
    # Scaling weights does not change the result (auto-normalised).
    assert abs(lg.score_with_weights(comps, {"a": 10, "b": 10}) - 0.5) < 1e-9
    # All weight on b.
    assert abs(lg.score_with_weights(comps, {"a": 0, "b": 1}) - 0.8) < 1e-9


def test_score_with_weights_zero_total() -> None:
    assert lg.score_with_weights({"a": 0.5}, {"a": 0.0}) == 0.0
