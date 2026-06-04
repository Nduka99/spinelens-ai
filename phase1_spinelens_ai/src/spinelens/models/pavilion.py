"""Pavilion suitability: combine a weighted score with a hard-constraint risk gate.

A site can score well on suitability yet carry a constraint that must be cleared before
anything proceeds (here: helipad safeguarding and land ownership/consent). The risk gate
makes that explicit so a good score never hides a show-stopper.
"""

from __future__ import annotations

from typing import Mapping

RISK_LEVELS = {"low": 0, "medium": 1, "high": 2, "blocker": 3}

_VERDICT_BY_LEVEL = {
    0: "proceed",
    1: "proceed_with_care",
    2: "proceed_with_validation",
    3: "blocked",
}


def risk_gate(risks: Mapping[str, str]) -> dict:
    """Combine a risk register into an overall verdict.

    ``risks`` maps a risk name to a level in {low, medium, high, blocker}. The overall
    verdict tracks the worst level present; any high/blocker risk is surfaced as a
    validation item that must be cleared (e.g. CAA/Trust helipad consent, HM Land
    Registry ownership) before funding-facing commitment.
    """

    if not risks:
        return {"overall_risk": "low", "verdict": "proceed", "validation_items": []}
    for name, level in risks.items():
        if level not in RISK_LEVELS:
            raise ValueError(f"unknown risk level {level!r} for {name!r}")
    max_level = max(RISK_LEVELS[v] for v in risks.values())
    overall = next(k for k, v in RISK_LEVELS.items() if v == max_level)
    validation_items = sorted(k for k, v in risks.items() if RISK_LEVELS[v] >= 2)
    return {
        "overall_risk": overall,
        "verdict": _VERDICT_BY_LEVEL[max_level],
        "validation_items": validation_items,
    }
