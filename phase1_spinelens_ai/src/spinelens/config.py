"""Configuration for the Phase 1 SpineLens evidence layer."""

from __future__ import annotations

from dataclasses import dataclass

PHASE1_TOTAL_BUDGET_GBP = 1_000_000

PHASE1_BUDGET_LINES: dict[str, int] = {
    "tactical_ground_graphics": 80_000,
    "wayfinding_lighting_banners": 120_000,
    "crossing_enhancements": 60_000,
    "pavilion_design_build": 180_000,
    "activation_furniture_landscape": 100_000,
    "project_management_contingency": 160_000,
    "events_evaluation_maintenance_community": 300_000,
}


@dataclass(frozen=True)
class Landmark:
    """A named point used to seed route and intervention analysis."""

    name: str
    role: str
    latitude: float
    longitude: float
    needs_validation: bool = True


SEED_LANDMARKS: tuple[Landmark, ...] = (
    Landmark("Colmore Row", "city_core_origin", 52.4810, -1.9000),
    Landmark("Birmingham New Street Station", "experimental_tactical_corridor_origin", 52.4778, -1.8988),
    Landmark("Moor Street Queensway", "route_origin", 52.4791, -1.8926),
    Landmark("Birmingham Snow Hill Station", "experimental_tactical_corridor_origin", 52.4835, -1.8990),
    Landmark("Dartmouth Middleway / Nechells Approach", "route_origin", 52.4900, -1.8848),
    Landmark("Ryder Street Pavilion Search Area", "gateway_site_search_area", 52.484042, -1.892412),
    Landmark("Dartmouth Middleway / Jennens Road Crossing", "priority_crossing_barrier", 52.4864, -1.8844),
    Landmark("Millennium Point", "bkq_anchor", 52.4827, -1.8859),
    Landmark("Aston University", "bkq_anchor", 52.4867, -1.8886),
)


def phase1_budget_total() -> int:
    """Return the configured Phase 1 budget total."""

    return sum(PHASE1_BUDGET_LINES.values())


def budget_is_balanced() -> bool:
    """Check whether configured budget lines match the Phase 1 total."""

    return phase1_budget_total() == PHASE1_TOTAL_BUDGET_GBP
