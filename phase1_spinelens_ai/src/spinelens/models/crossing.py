"""Crossing-type warrant and multi-criteria options appraisal.

These functions encode UK-practice rules of thumb and a transparent multi-criteria
appraisal so the crossing recommendation is explainable and evidence-driven rather
than asserted. Thresholds are PROVISIONAL documented assumptions, to be checked
against the highway authority's standards before a business case.
"""

from __future__ import annotations

from typing import Mapping

# --- Indicative thresholds from UK crossing practice (PROVISIONAL) ---
# Zebra crossings are discouraged on multi-lane carriageways (multiple-threat risk),
# higher speeds, and high flows; signal control is preferred there.
ZEBRA_MAX_LANES_EACH_WAY = 1
ZEBRA_MAX_SPEED_MPH = 30
ZEBRA_MAX_AADF = 8000
SIGNAL_AADF_TRIGGER = 12000


def crossing_warrant(speed_mph: float, lanes_each_way: int, aadf: float) -> dict:
    """Assess whether a zebra is appropriate and whether signals are warranted.

    Returns a dict with booleans and the human-readable reasons, so the decision
    can be defended line by line.
    """

    reasons: list[str] = []
    zebra_ok = True
    if lanes_each_way > ZEBRA_MAX_LANES_EACH_WAY:
        zebra_ok = False
        reasons.append(f"{lanes_each_way} lanes each way (multiple-threat risk)")
    if speed_mph > ZEBRA_MAX_SPEED_MPH:
        zebra_ok = False
        reasons.append(f"{speed_mph:g} mph above the {ZEBRA_MAX_SPEED_MPH} mph zebra guideline")
    if aadf > ZEBRA_MAX_AADF:
        zebra_ok = False
        reasons.append(f"AADF {aadf:,.0f} above the {ZEBRA_MAX_AADF:,} zebra guideline")

    signal_recommended = (aadf >= SIGNAL_AADF_TRIGGER) or (lanes_each_way >= 2)
    if not zebra_ok and signal_recommended:
        summary = "Zebra not appropriate; signal-controlled crossing warranted."
    elif zebra_ok:
        summary = "A zebra may be appropriate subject to a site speed/flow survey."
    else:
        summary = "Zebra not appropriate; consider signal control or geometry change."

    return {
        "zebra_appropriate": zebra_ok,
        "signal_recommended": signal_recommended,
        "reasons": reasons,
        "summary": summary,
    }


def multi_criteria_rank(
    options: Mapping[str, Mapping[str, float]],
    weights: Mapping[str, float],
) -> list[dict]:
    """Rank options by a weighted sum of per-criterion scores (0..1, higher better).

    Weights are auto-normalised, so only their relative sizes matter. Returns rows
    sorted best-first, each carrying the component scores for transparency.
    """

    total_w = sum(weights.values())
    rows: list[dict] = []
    for name, crit in options.items():
        if total_w > 0:
            score = sum(crit.get(c, 0.0) * w for c, w in weights.items()) / total_w
        else:
            score = 0.0
        row = {"option": name, "score": round(score, 4)}
        row.update({c: crit.get(c, 0.0) for c in weights})
        rows.append(row)
    return sorted(rows, key=lambda r: r["score"], reverse=True)


def collision_rate_per_year(collisions: int, years: int) -> float:
    """Collisions per year (a simple, defensible normalisation for the safety case)."""

    if years <= 0:
        return 0.0
    return round(collisions / years, 2)
