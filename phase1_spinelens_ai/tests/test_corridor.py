"""Tests for tactical-corridor synthesis."""

from __future__ import annotations

from spinelens.models import corridor as co


def test_edge_key_is_undirected() -> None:
    assert co.edge_key(1, 2) == co.edge_key(2, 1)


def test_segment_multiplicity_counts_shared_edges() -> None:
    routes = {
        "r1": [1, 2, 3, 9],     # edges 1-2, 2-3, 3-9
        "r2": [4, 2, 3, 9],     # edges 4-2, 2-3, 3-9  (shares 2-3 and 3-9)
    }
    mult = co.segment_multiplicity(routes)
    assert mult[co.edge_key(2, 3)] == {"r1", "r2"}
    assert mult[co.edge_key(3, 9)] == {"r1", "r2"}
    assert mult[co.edge_key(1, 2)] == {"r1"}


def test_corridor_summary_trunk_vs_spur() -> None:
    routes = {"r1": [1, 2, 3], "r2": [4, 2, 3]}  # 2-3 shared, others single
    s = co.corridor_summary(co.segment_multiplicity(routes))
    assert s["segments"] == 3
    assert s["trunk_segments"] == 1
    assert s["spur_segments"] == 2
    assert s["max_multiplicity"] == 2


def test_normalize_bounds_and_constant() -> None:
    assert co.normalize([10, 20, 30]) == [0.0, 0.5, 1.0]
    assert co.normalize([5, 5, 5]) == [0.0, 0.0, 0.0]
    assert co.normalize([]) == []


def test_corridor_intensity_blend() -> None:
    # equal weights -> mean
    assert abs(co.corridor_intensity(1.0, 0.0, 0.5, 0.5) - 0.5) < 1e-9
    # default weights favour multiplicity
    hi = co.corridor_intensity(1.0, 0.0)
    lo = co.corridor_intensity(0.0, 1.0)
    assert hi > lo
    assert co.corridor_intensity(0.5, 0.5) == 0.5


def test_segment_suitability_roles() -> None:
    assert co.segment_suitability("footway")["role"] == "corridor_surface"
    assert co.segment_suitability("primary")["role"] == "crossing_required"
    assert co.segment_suitability("steps")["role"] == "unsuitable_access"
    assert co.segment_suitability("raceway")["role"] == "review"
    # severity reduces a treatable score
    assert co.segment_suitability("footway", severity=3)["score"] < 1.0
