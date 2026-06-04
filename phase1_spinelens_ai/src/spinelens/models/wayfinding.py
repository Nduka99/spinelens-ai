"""Wayfinding candidate ranking and placement optimisation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, Mapping


@dataclass(frozen=True)
class WayfindingCandidate:
    node_id: str
    latitude: float
    longitude: float
    intervention_type: str
    rationale: str
    estimated_cost_gbp: int
    priority_score: float


MIN_WAYFINDER_SPACING_METERS = 150

INTERVENTION_TYPES: tuple[str, ...] = (
    "directional_totem",
    "ground_graphic",
    "lighting_marker",
    "overhead_banner",
    "crossing_support",
)


def greedy_max_coverage(
    candidates: Iterable[Hashable],
    covers: Mapping[Hashable, set],
    demand_weight: Mapping[Hashable, float],
    k: int,
    too_close: Callable[[Hashable, Hashable], bool] | None = None,
) -> list[dict]:
    """Greedy maximal-coverage selection of up to ``k`` wayfinder sites.

    Each candidate "covers" a set of demand items (e.g. confusion/decision points
    along routes); each demand item has a weight (its legibility need). At every
    step we add the candidate giving the largest *marginal* gain in covered weight,
    optionally skipping candidates that are too close to an already-selected site
    (minimum-spacing constraint). This is the classic submodular greedy heuristic
    (1 - 1/e of optimum), and it is fully explainable.

    Returns the ordered list of selections with their marginal and cumulative gain.
    """

    candidates = list(candidates)
    selected: list[Hashable] = []
    covered: set = set()
    results: list[dict] = []
    cumulative = 0.0

    for _ in range(k):
        best, best_gain, best_new = None, 0.0, set()
        for c in candidates:
            if c in selected:
                continue
            if too_close is not None and any(too_close(c, s) for s in selected):
                continue
            new = covers.get(c, set()) - covered
            gain = sum(demand_weight.get(d, 0.0) for d in new)
            if gain > best_gain:
                best, best_gain, best_new = c, gain, new
        if best is None or best_gain <= 0:
            break
        selected.append(best)
        covered |= best_new
        cumulative += best_gain
        results.append({
            "node": best,
            "marginal_gain": round(best_gain, 4),
            "cumulative_gain": round(cumulative, 4),
            "newly_covered": len(best_new),
        })
    return results


def coverage_curve(
    candidates: Iterable[Hashable],
    covers: Mapping[Hashable, set],
    demand_weight: Mapping[Hashable, float],
    max_k: int,
    too_close: Callable[[Hashable, Hashable], bool] | None = None,
) -> list[float]:
    """Cumulative covered weight after each of 1..max_k greedy selections."""

    picks = greedy_max_coverage(candidates, covers, demand_weight, max_k, too_close)
    return [p["cumulative_gain"] for p in picks]

