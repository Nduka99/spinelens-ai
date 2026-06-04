"""Validation-register helpers: track the gap to a fundable evidence level.

Forensic evidence ladder (see docs/forensic_evidence_protocol.md):
0 not tested, 1 source reachable, 2 raw acquired, 3 quality audited,
4 cross-checked, 5 field validated. Funding-facing claims need Level 4-5.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping

MAX_LEVEL = 5


def evidence_gap(current_level: int, required_level: int) -> dict:
    """Gap between an item's current and required evidence level."""

    gap = max(0, int(required_level) - int(current_level))
    return {"gap": gap, "status": "met" if gap == 0 else "open"}


def register_summary(rows: Iterable[Mapping[str, object]]) -> dict:
    """Summarise a validation register: open items, priorities, field-validation needs."""

    rows = list(rows)
    if not rows:
        return {"items": 0, "open": 0, "by_priority": {}, "field_validation_items": 0}
    open_items = sum(1 for r in rows if int(r.get("gap", 0)) > 0)
    field_items = sum(1 for r in rows if int(r.get("required_level", 0)) >= 5)
    by_priority = dict(Counter(str(r.get("priority", "")) for r in rows))
    return {
        "items": len(rows),
        "open": open_items,
        "by_priority": by_priority,
        "field_validation_items": field_items,
    }
