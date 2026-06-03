"""Transparent scoring primitives for route legibility."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LegibilityWeights:
    directness: float = 0.25
    turn_burden: float = 0.20
    intersection_complexity: float = 0.20
    crossing_burden: float = 0.20
    continuity: float = 0.15


DEFAULT_WEIGHTS = LegibilityWeights()


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
    """Calculate a first-pass weighted legibility score from normalized inputs."""

    return (
        components.get("directness", 0.0) * weights.directness
        + components.get("turn_burden", 0.0) * weights.turn_burden
        + components.get("intersection_complexity", 0.0) * weights.intersection_complexity
        + components.get("crossing_burden", 0.0) * weights.crossing_burden
        + components.get("continuity", 0.0) * weights.continuity
    )
