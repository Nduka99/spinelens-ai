"""Budget model: transparent low/central/high cost lines, soft costs, envelope checks.

Quantities come from the analysis (corridor metres, wayfinder counts) and are reasonably
evidenced (Level 3). Unit costs are INDICATIVE benchmark assumptions (Level 1) pending a
quantity-surveyor costing - so everything is a range, never a single false-precision figure.
"""

from __future__ import annotations

from typing import Iterable, Mapping

_BANDS = ("low", "central", "high")


def line_total(quantity: float, unit_low: float, unit_central: float, unit_high: float) -> dict:
    """Cost of a line item = quantity x unit, as a low/central/high range."""

    return {
        "low": round(quantity * unit_low),
        "central": round(quantity * unit_central),
        "high": round(quantity * unit_high),
    }


def sum_costs(items: Iterable[Mapping[str, float]]) -> dict:
    """Element-wise sum of low/central/high across cost lines."""

    items = list(items)
    return {b: round(sum(i.get(b, 0) for i in items)) for b in _BANDS}


def add_percentage(cost: Mapping[str, float], pct: float) -> dict:
    """Apply a percentage uplift (e.g. design fees, contingency) to each band."""

    return {b: round(cost[b] * (1 + pct / 100.0)) for b in _BANDS}


def apply_offset(cost: Mapping[str, float], offset: Mapping[str, float]) -> dict:
    """Subtract an offset range (e.g. sponsorship) from a cost range, floored at 0."""

    return {b: max(0, round(cost[b] - offset.get(b, 0))) for b in _BANDS}


def envelope_check(cost: Mapping[str, float], envelope: float) -> dict:
    """Does the cost fit a funding envelope at each band? Plus central headroom."""

    return {
        "fits_low": cost["low"] <= envelope,
        "fits_central": cost["central"] <= envelope,
        "fits_high": cost["high"] <= envelope,
        "headroom_central": round(envelope - cost["central"]),
    }
