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


# --- Tiered wayfinder UX: glanceable markers vs interactive dwell totems/hub ---
# A tier sets how rich a panel is, which keeps cost realistic (you do not put a screen
# at every point). Modules below are content families a panel can offer when someone stops.
TIER_HUB = "tier1_hub"          # the gateway pavilion: full interactive dwell experience
TIER_TOTEM = "tier2_totem"      # major interactive totems at convergence/origin nodes
TIER_MARKER = "tier3_marker"    # low-cost glanceable markers (ground graphic/lighting) + QR

TIER_MODULE_POLICY = {
    TIER_HUB: {"directory_find_by_need", "interactive_map", "whats_on",
               "accessibility_language", "qr_handoff"},
    TIER_TOTEM: {"interactive_map", "whats_on", "accessibility_language", "qr_handoff"},
    TIER_MARKER: {"qr_handoff"},
}


def assign_tier(routes_served: int, intervention_type: str, is_gateway: bool = False) -> str:
    """Assign a wayfinder tier from its role (drives richness and cost)."""

    if is_gateway:
        return TIER_HUB
    if routes_served >= 2 or intervention_type in ("directional_totem", "crossing_support"):
        return TIER_TOTEM
    return TIER_MARKER


def modules_for_tier(tier: str, enabled: set[str]) -> list[str]:
    """Modules a panel offers: the tier's capability intersected with project-enabled set."""

    return sorted(TIER_MODULE_POLICY.get(tier, set()) & set(enabled))


# Approaches that reach the gateway pavilion (so their en-route markers can stay light).
# The Nechells/Dartmouth approach has NO pavilion, so its wayfinders must carry hub-lite
# content. A small gateway teaser is universal.
HUB_APPROACHES = {"colmore", "new_street", "moor_street", "snow_hill"}
NO_PAVILION_BOOST = {"interactive_map", "directory_find_by_need", "whats_on"}
GATEWAY_TEASER = "gateway_teaser"


def serves_non_hub_approach(approaches: list[str]) -> bool:
    """True if a wayfinder serves an approach with no pavilion (e.g. Nechells)."""

    return any(a and a not in HUB_APPROACHES for a in approaches)


def content_role(tier: str, approaches: list[str]) -> str:
    """Label a panel's content role from its tier and the approaches it serves."""

    if tier == TIER_HUB:
        return "hub"
    if serves_non_hub_approach(approaches):
        return "dwell_no_pavilion"   # carries hub-lite content (no pavilion to fall back on)
    if tier == TIER_TOTEM:
        return "guide_totem"
    return "light_marker"


def effective_modules(tier: str, enabled: set[str], approaches: list[str],
                      gateway_teaser: bool = True) -> list[str]:
    """Modules for a panel, boosting no-pavilion approaches and adding a gateway teaser.

    City-core markers stay light (the pavilion does the heavy lifting); Nechells markers
    are upgraded with hub-lite modules; every panel gets a small gateway teaser.
    """

    mods = set(modules_for_tier(tier, enabled))
    if serves_non_hub_approach(approaches):
        mods |= (NO_PAVILION_BOOST & set(enabled))
    if gateway_teaser:
        mods.add(GATEWAY_TEASER)
    return sorted(mods)


def sponsorship_slot(tier: str, model: str = "civic_partner") -> dict:
    """Bounded, non-intrusive sponsorship slot (screened tiers only), with guardrails."""

    enabled = tier in (TIER_HUB, TIER_TOTEM)
    return {
        "enabled": enabled,
        "model": model if enabled else "none",
        "max_screen_share": 0.15 if enabled else 0.0,
        "guardrails": ["relevant_contextual", "no_tracking", "never_blocks_wayfinding",
                       "accessibility_preserved"] if enabled else [],
    }


WALK_SPEED_MS = 1.33  # ~4.8 km/h standard adult walking speed
_COMPASS_8 = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def bearing_to_compass(bearing_deg: float) -> str:
    """Map a compass bearing (degrees) to an 8-point direction for wayfinder text."""

    return _COMPASS_8[round((bearing_deg % 360) / 45) % 8]


def walk_time_minutes(distance_m: float, speed_ms: float = WALK_SPEED_MS) -> float:
    """Estimated walking time in minutes for a network distance (metres)."""

    if distance_m <= 0 or speed_ms <= 0:
        return 0.0
    return round(distance_m / speed_ms / 60.0, 1)


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

