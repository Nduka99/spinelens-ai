"""Transparent scoring primitives for route legibility.

The Route Legibility Index is a deliberately explainable composite: each component
is computed separately, normalised to 0..1 (1 = most legible), documented, and
weighted. Reference bands below are explicit assumptions, to be stress-tested with
a weight/threshold sensitivity analysis before any funding-facing claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, degrees, radians, sin


@dataclass(frozen=True)
class LegibilityWeights:
    directness: float = 0.25
    turn_burden: float = 0.20
    intersection_complexity: float = 0.20
    crossing_burden: float = 0.20
    continuity: float = 0.15


DEFAULT_WEIGHTS = LegibilityWeights()

# --- Documented reference bands (PROVISIONAL; subject to sensitivity analysis) ---
# These are set to span the values observed across dense Birmingham city-centre walk
# routes so the index discriminates rather than saturating. They are assumptions, not
# calibrated truth, and must be stress-tested (Stage 4) and checked against literature
# before any funding-facing claim.
# Cumulative angular change per km above which a route reads as "very tortuous".
TURN_REF_DEG_PER_KM = 1800.0
# Decision nodes (street_count >= 3) per km above which choices feel overwhelming.
DECISION_REF_PER_KM = 45.0
# Weighted road-crossing severity per km above which the route reads as hostile.
CROSSING_REF_SEVERITY_PER_KM = 6.0
# A turn at or above this angle is a genuine "which way?" direction decision.
SIGNIFICANT_TURN_DEG = 45.0
# Significant turns per km above which "follow the road" continuity breaks down.
CONTINUITY_REF_TURNS_PER_KM = 20.0

# Crossing severity by OSM highway class of the road being crossed.
CROSSING_SEVERITY = {
    "motorway": 5.0,
    "motorway_link": 5.0,
    "trunk": 4.0,
    "trunk_link": 4.0,
    "primary": 3.0,
    "primary_link": 3.0,
    "secondary": 2.0,
    "secondary_link": 2.0,
    "tertiary": 1.0,
    "tertiary_link": 1.0,
}


def weights_total(weights: LegibilityWeights = DEFAULT_WEIGHTS) -> float:
    """Return the sum of configured Route Legibility Index weights."""

    return (
        weights.directness
        + weights.turn_burden
        + weights.intersection_complexity
        + weights.crossing_burden
        + weights.continuity
    )


def weighted_legibility_score(
    components: dict[str, float],
    weights: LegibilityWeights = DEFAULT_WEIGHTS,
) -> float:
    """Calculate a weighted legibility score from normalized (0..1) inputs."""

    return (
        components.get("directness", 0.0) * weights.directness
        + components.get("turn_burden", 0.0) * weights.turn_burden
        + components.get("intersection_complexity", 0.0) * weights.intersection_complexity
        + components.get("crossing_burden", 0.0) * weights.crossing_burden
        + components.get("continuity", 0.0) * weights.continuity
    )


COMPONENT_KEYS = (
    "directness",
    "turn_burden",
    "intersection_complexity",
    "crossing_burden",
    "continuity",
)


def score_with_weights(
    components: dict[str, float],
    weights: dict[str, float],
) -> float:
    """Weighted legibility score for an arbitrary weight dict (auto-normalised).

    Used by the sensitivity analysis to score routes under many weightings without
    constructing a LegibilityWeights instance. Weights are normalised to sum to 1
    over the keys present, so only their relative sizes matter.
    """

    total = sum(weights.values())
    if total <= 0:
        return 0.0
    return sum(components.get(k, 0.0) * (w / total) for k, w in weights.items())


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def initial_bearing(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    """Initial compass bearing (degrees, 0..360) from a to b, both (lat, lon)."""

    lat1, lon1 = radians(point_a[0]), radians(point_a[1])
    lat2, lon2 = radians(point_b[0]), radians(point_b[1])
    d_lon = lon2 - lon1
    x = sin(d_lon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(d_lon)
    return (degrees(atan2(x, y)) + 360.0) % 360.0


def turn_angles(coords: list[tuple[float, float]]) -> list[float]:
    """Absolute turn angle (0..180 deg) at each interior vertex of a polyline."""

    angles: list[float] = []
    for i in range(1, len(coords) - 1):
        b1 = initial_bearing(coords[i - 1], coords[i])
        b2 = initial_bearing(coords[i], coords[i + 1])
        diff = abs(b2 - b1) % 360.0
        angles.append(diff if diff <= 180.0 else 360.0 - diff)
    return angles


def total_turning_deg(coords: list[tuple[float, float]]) -> float:
    """Cumulative absolute turning along a polyline, in degrees."""

    return sum(turn_angles(coords))


def directness_score(straight_m: float, network_m: float) -> float:
    """Straight-line distance / network distance, clamped to 0..1 (1 = direct)."""

    if network_m <= 0:
        return 0.0
    return _clamp01(straight_m / network_m)


def turn_burden_score(total_turn_deg: float, route_km: float,
                      ref_per_km: float = TURN_REF_DEG_PER_KM) -> float:
    """1 = little cumulative turning per km, 0 = at/above the tortuous reference."""

    if route_km <= 0:
        return 0.0
    return _clamp01(1.0 - (total_turn_deg / route_km) / ref_per_km)


def intersection_complexity_score(decision_count: int, route_km: float,
                                  ref_per_km: float = DECISION_REF_PER_KM) -> float:
    """1 = few decision nodes per km, 0 = at/above the overwhelming reference."""

    if route_km <= 0:
        return 0.0
    return _clamp01(1.0 - (decision_count / route_km) / ref_per_km)


def crossing_burden_score(severity_sum: float, route_km: float,
                          ref_per_km: float = CROSSING_REF_SEVERITY_PER_KM) -> float:
    """1 = comfortable (few/minor crossings), 0 = at/above the hostile reference."""

    if route_km <= 0:
        return 0.0
    return _clamp01(1.0 - (severity_sum / route_km) / ref_per_km)


def continuity_score(coords: list[tuple[float, float]], route_km: float,
                     significant_turn_deg: float = SIGNIFICANT_TURN_DEG,
                     ref_turns_per_km: float = CONTINUITY_REF_TURNS_PER_KM) -> float:
    """1 = "follow the road" (few hard turns per km), 0 = at/above the reference."""

    if route_km <= 0:
        return 0.0
    significant = sum(1 for a in turn_angles(coords) if a >= significant_turn_deg)
    return _clamp01(1.0 - (significant / route_km) / ref_turns_per_km)


def crossing_severity(highway_class: str) -> float:
    """Severity weight for crossing a road of the given OSM highway class."""

    return CROSSING_SEVERITY.get(str(highway_class), 0.0)
