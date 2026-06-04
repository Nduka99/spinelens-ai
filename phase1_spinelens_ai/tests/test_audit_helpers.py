"""Tests for Gate 0B quality-audit helpers."""

from __future__ import annotations

from spinelens.spatial import audit


def test_haversine_known_distance() -> None:
    # ~111.2 km per degree of latitude near the equator.
    d = audit.haversine_m((52.0, -1.9), (52.01, -1.9))
    assert 1100 < d < 1120


def test_nearest_node_picks_closest() -> None:
    coords = {"a": (52.480, -1.900), "b": (52.490, -1.880), "c": (52.4805, -1.9001)}
    node_id, dist = audit.nearest_node(coords, (52.4801, -1.9000))
    assert node_id == "a"
    assert dist < 20


def test_nearest_node_empty_raises() -> None:
    try:
        audit.nearest_node({}, (52.0, -1.9))
    except ValueError:
        return
    raise AssertionError("expected ValueError on empty node_coords")


def test_classify_snap_thresholds() -> None:
    assert audit.classify_snap(10) == "good"
    assert audit.classify_snap(25) == "good"
    assert audit.classify_snap(50) == "acceptable"
    assert audit.classify_snap(120) == "poor"


def test_snap_report_flags_quality() -> None:
    coords = {1: (52.4800, -1.9000), 2: (52.4900, -1.8800)}
    anchors = [
        {"anchor_id": "near", "anchor_name": "Near", "latitude": 52.4801, "longitude": -1.9001},
        {"anchor_id": "far", "anchor_name": "Far", "latitude": 52.4700, "longitude": -1.9200},
    ]
    rows = audit.snap_report(coords, anchors)
    by_id = {r["anchor_id"]: r for r in rows}
    assert by_id["near"]["snap_quality"] == "good"
    assert by_id["near"]["nearest_node_id"] == 1
    assert by_id["far"]["snap_quality"] == "poor"


def test_summary_stats_basic() -> None:
    s = audit.summary_stats([10, 20, 30])
    assert s["count"] == 3
    assert s["min"] == 10 and s["max"] == 30
    assert s["mean"] == 20 and s["median"] == 20
    assert s["total"] == 60


def test_summary_stats_empty() -> None:
    s = audit.summary_stats([])
    assert s["count"] == 0 and s["total"] == 0.0


def test_degree_stats_counts() -> None:
    s = audit.degree_stats([1, 1, 2, 3, 4, 5])
    assert s["count"] == 6
    assert s["dead_ends"] == 2
    assert s["decision_nodes"] == 2


def test_resolve_route_family_references_detects_mismatch() -> None:
    families = [
        {"route_family_id": "ok", "origin_node_id": "a", "gateway_node_id": "g", "onward_anchor_id": "o"},
        {"route_family_id": "bad", "origin_node_id": "missing", "gateway_node_id": "g", "onward_anchor_id": "o"},
    ]
    rows = audit.resolve_route_family_references(families, ["a", "g", "o"])
    by_id = {r["route_family_id"]: r for r in rows}
    assert by_id["ok"]["resolves"] is True
    assert by_id["bad"]["resolves"] is False
    assert by_id["bad"]["unresolved"] == ["missing"]


def test_evidence_verdict_pass_and_fail() -> None:
    passed = audit.evidence_verdict({"crs_known": True, "valid": True})
    assert passed["passed"] is True
    assert passed["evidence_level"] == 3
    assert passed["can_support_funding_claim"] is False

    failed = audit.evidence_verdict({"crs_known": True, "valid": False})
    assert failed["passed"] is False
    assert failed["evidence_level"] == 2
    assert failed["failed_checks"] == ["valid"]


def test_evidence_verdict_empty_is_not_passed() -> None:
    v = audit.evidence_verdict({})
    assert v["passed"] is False
