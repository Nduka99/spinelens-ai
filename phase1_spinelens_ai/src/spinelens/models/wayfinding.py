"""Wayfinding candidate ranking structures."""

from __future__ import annotations

from dataclasses import dataclass


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
