"""Tactical-corridor synthesis: which segments carry the amber spine, how strongly.

Pure, testable logic. The notebook supplies graph geometry and highway tags; this
module decides segment sharing (route multiplicity), corridor intensity, and physical
suitability. Grounded in the pavilion-gateway model: the amber corridor serves the
city-core approaches into the Ryder Street gateway (the Nechells side is handled by the
crossing + wayfinders, not the corridor).
"""

from __future__ import annotations

from typing import Hashable, Mapping, Sequence

# Highway classes a ground-level tactical corridor surface can run along.
TREATABLE_HIGHWAY = {
    "footway", "path", "pedestrian", "living_street", "residential",
    "service", "unclassified", "track", "tertiary", "tertiary_link",
}
# Major carriageways: you cross these, you do not pave them as corridor.
CROSSING_HIGHWAY = {
    "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link",
}


def edge_key(u: Hashable, v: Hashable) -> tuple:
    """Undirected edge identity (order-independent)."""

    return (u, v) if str(u) <= str(v) else (v, u)


def segment_multiplicity(
    routes: Mapping[str, Sequence[Hashable]],
) -> dict[tuple, set]:
    """Map each undirected edge to the set of route names that traverse it.

    Edges shared by 2+ routes are the corridor trunk; single-route edges are spurs.
    """

    used: dict[tuple, set] = {}
    for name, path in routes.items():
        for u, v in zip(path[:-1], path[1:]):
            used.setdefault(edge_key(u, v), set()).add(name)
    return used


def normalize(values: Sequence[float]) -> list[float]:
    """Min-max normalise to 0..1 (constant input -> all zeros)."""

    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi <= lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def corridor_intensity(
    multiplicity_frac: float,
    proximity_frac: float,
    w_multiplicity: float = 0.6,
    w_proximity: float = 0.4,
) -> float:
    """Amber-corridor intensity (0..1): blends route-sharing with nearness to gateway.

    The deck calls for intensity to ramp up approaching the Ryder Street gateway; the
    proximity term encodes that, while the multiplicity term concentrates intensity on
    the shared spine. Weights are documented assumptions.
    """

    total = w_multiplicity + w_proximity
    if total <= 0:
        return 0.0
    return (w_multiplicity * multiplicity_frac + w_proximity * proximity_frac) / total


def segment_suitability(highway: str, severity: float = 0.0) -> dict:
    """Classify a segment's physical suitability for the tactical corridor.

    Returns role + a 0..1 score (1 = readily treatable as corridor surface).
    """

    hw = str(highway)
    if hw in CROSSING_HIGHWAY:
        return {"role": "crossing_required", "score": 0.2,
                "note": "major carriageway - treat as a crossing point, not corridor surface"}
    if hw == "steps":
        return {"role": "unsuitable_access", "score": 0.1,
                "note": "steps - step-free alternative required"}
    if hw in TREATABLE_HIGHWAY:
        score = max(0.0, 1.0 - 0.1 * severity)
        return {"role": "corridor_surface", "score": round(score, 3),
                "note": "treatable as tactical corridor surface"}
    return {"role": "review", "score": 0.5, "note": "unclassified - review on site"}


def corridor_summary(multiplicity: Mapping[tuple, set]) -> dict:
    """Headline split of the corridor into shared trunk vs single-route spurs."""

    if not multiplicity:
        return {"segments": 0, "trunk_segments": 0, "spur_segments": 0, "max_multiplicity": 0}
    sizes = [len(s) for s in multiplicity.values()]
    return {
        "segments": len(multiplicity),
        "trunk_segments": sum(1 for n in sizes if n >= 2),
        "spur_segments": sum(1 for n in sizes if n == 1),
        "max_multiplicity": max(sizes),
    }
