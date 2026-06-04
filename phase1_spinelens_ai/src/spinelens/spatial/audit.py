"""Gate 0B quality-audit helpers.

These functions support the forensic quality audit (Evidence Level 2 -> 3) of
acquired raw spatial data. They are intentionally dependency-light: they operate
on plain Python structures (coordinate dicts, lists of rows) so they can be unit
tested without downloading data or importing heavy geospatial libraries.

The notebook is responsible for extracting graph/geometry inputs (via osmnx,
networkx, geopandas) and for visualisation. The reusable, testable judgement
logic lives here.
"""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from statistics import mean, median
from typing import Iterable, Mapping, Sequence

EARTH_RADIUS_M = 6_371_000.0

# Snap-distance thresholds (metres) for judging how well a provisional anchor
# lands on the acquired pedestrian network.
SNAP_GOOD_M = 25.0
SNAP_ACCEPTABLE_M = 75.0


def haversine_m(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    """Great-circle distance in metres between two (lat, lon) points."""

    lat1, lon1 = point_a
    lat2, lon2 = point_b
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    h = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * asin(sqrt(h))


def nearest_node(
    node_coords: Mapping[object, tuple[float, float]],
    point: tuple[float, float],
) -> tuple[object, float]:
    """Return the (node_id, distance_m) of the nearest node to a (lat, lon) point.

    Brute force over the node set. Exact enough and fast for Gate 0B scale.
    """

    if not node_coords:
        raise ValueError("node_coords is empty; cannot snap point to graph")
    best_id = None
    best_dist = float("inf")
    for node_id, coord in node_coords.items():
        dist = haversine_m(point, coord)
        if dist < best_dist:
            best_dist = dist
            best_id = node_id
    return best_id, best_dist


def classify_snap(distance_m: float) -> str:
    """Classify how cleanly an anchor snaps onto the network."""

    if distance_m <= SNAP_GOOD_M:
        return "good"
    if distance_m <= SNAP_ACCEPTABLE_M:
        return "acceptable"
    return "poor"


def snap_report(
    node_coords: Mapping[object, tuple[float, float]],
    anchors: Iterable[Mapping[str, object]],
    lat_key: str = "latitude",
    lon_key: str = "longitude",
    id_key: str = "anchor_id",
    name_key: str = "anchor_name",
) -> list[dict[str, object]]:
    """Snap each anchor to its nearest network node and flag snap quality."""

    rows: list[dict[str, object]] = []
    for anchor in anchors:
        point = (float(anchor[lat_key]), float(anchor[lon_key]))
        node_id, dist = nearest_node(node_coords, point)
        rows.append(
            {
                "anchor_id": anchor.get(id_key, ""),
                "anchor_name": anchor.get(name_key, ""),
                "nearest_node_id": node_id,
                "snap_distance_m": round(dist, 1),
                "snap_quality": classify_snap(dist),
            }
        )
    return rows


def summary_stats(values: Sequence[float]) -> dict[str, float]:
    """Return count/min/max/mean/median/total for a numeric sequence."""

    clean = [float(v) for v in values]
    if not clean:
        return {"count": 0, "min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0, "total": 0.0}
    return {
        "count": len(clean),
        "min": round(min(clean), 2),
        "max": round(max(clean), 2),
        "mean": round(mean(clean), 2),
        "median": round(median(clean), 2),
        "total": round(sum(clean), 2),
    }


def degree_stats(degrees: Sequence[int]) -> dict[str, object]:
    """Summarise node-degree distribution for a pedestrian graph.

    Dead-ends (degree 1) and decision points (degree >= 4) are reported because
    they matter for legibility: dead-ends fragment routing and high-degree nodes
    are candidate wayfinding decision points.
    """

    if not degrees:
        return {"count": 0, "dead_ends": 0, "decision_nodes": 0, "mean_degree": 0.0}
    return {
        "count": len(degrees),
        "dead_ends": sum(1 for d in degrees if d <= 1),
        "decision_nodes": sum(1 for d in degrees if d >= 4),
        "mean_degree": round(mean(degrees), 2),
    }


def resolve_route_family_references(
    route_families: Iterable[Mapping[str, object]],
    known_anchor_ids: Iterable[str],
) -> list[dict[str, object]]:
    """Check that route-family node references resolve to known anchor IDs.

    Returns one row per route family with a list of unresolved references. An
    empty ``unresolved`` list means every origin/gateway/onward ID is valid.
    This catches provenance drift between the route ledger and the anchor table.
    """

    known = set(known_anchor_ids)
    ref_fields = ("origin_node_id", "gateway_node_id", "onward_anchor_id")
    rows: list[dict[str, object]] = []
    for family in route_families:
        unresolved = [
            str(family[field])
            for field in ref_fields
            if field in family and str(family[field]) and str(family[field]) not in known
        ]
        rows.append(
            {
                "route_family_id": family.get("route_family_id", ""),
                "resolves": not unresolved,
                "unresolved": unresolved,
            }
        )
    return rows


def evidence_verdict(checks: Mapping[str, bool]) -> dict[str, object]:
    """Combine boolean audit checks into a Gate 0B verdict.

    A source can advance to Evidence Level 3 ("quality audited", descriptive
    claims only) only if every check passes. Any failure keeps it at Level 2.
    The verdict never grants funding use; that requires Levels 4-5.
    """

    failed = sorted(name for name, ok in checks.items() if not ok)
    passed = bool(checks) and not failed
    return {
        "passed": passed,
        "failed_checks": failed,
        "evidence_level": 3 if passed else 2,
        "forensic_status": "quality_audited" if passed else "raw_acquired_pending_quality_audit",
        "can_support_funding_claim": False,
    }
