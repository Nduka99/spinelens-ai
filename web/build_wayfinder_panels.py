"""Build the conceptual wayfinder panel content for the Vision view (Step 8+, slow build).

Reads the sanitised public wayfinders layer and assembles, per wayfinder, the
"digital panel" content the Vision cards show:
  - LIGHT panels (city-core): direction + "full guide at the Ryder St pavilion" + QR.
  - RICH panels (Nechells, no pavilion): find-by-need + general B-KQ opportunities
    + transport + QR.

Opportunities are CONCEPTUAL and GENERAL (functional offers, not dated events). Every
field is public-safe; live fields are flagged as dynamic (populated at deployment).

Run:  python build_wayfinder_panels.py     (stdlib only)
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WAYFINDERS_IN = ROOT / "public" / "content" / "layers" / "wayfinders.geojson"
OUT = ROOT / "public" / "content" / "wayfinder_panels.json"

FIND_BY_NEED = ["Study", "Work", "Eat", "Health", "Innovation"]

# General, evergreen "what's here" offers per B-KQ destination (conceptual examples).
OPPORTUNITIES = {
    "STEAMhouse": ["Free business support & mentoring", "Maker spaces, studios & equipment", "Innovation workshops & networking"],
    "Aston Business School": ["Triple-accredited business school", "Executive education", "Knowledge-transfer partnerships"],
    "Aston University": ["Health-tech accelerator (SPARK)", "Open days & short courses", "Enterprise hub for start-ups"],
    "Innovation Birmingham": ["Digital scale-up programmes", "Open-innovation challenges", "Tech careers & talent"],
    "BCU City Centre": ["Courses & open days", "Studios, labs & exhibitions", "Creative & tech facilities"],
    "BCU": ["Courses & open days", "Studios, labs & exhibitions", "Creative & tech facilities"],
    "Royal Birmingham Conservatoire": ["Concerts & performances", "Music & acting study", "Public events"],
    "Millennium Point": ["Thinktank science museum", "Public exhibitions & events", "STEM learning spaces"],
}
DEFAULT_OPPORTUNITIES = {
    "place": "Birmingham Knowledge Quarter",
    "items": ["Study, work & innovate", "Public events & exhibitions", "Two universities + an innovation hub"],
}

STATIC_FIELDS = ["heading", "walkTimeMin", "nextMarker", "findByNeed", "opportunities", "nearbyStops"]
DYNAMIC_FIELDS = ["liveEvents", "busDepartures", "accessibilityStatus"]


def match_opportunities(onward: str) -> list[dict]:
    """Map an onward-destinations string to a few curated, general opportunity sets."""
    out: list[dict] = []
    seen: set[str] = set()
    for part in [p.strip() for p in str(onward).split(",") if p.strip()]:
        for key, items in OPPORTUNITIES.items():
            if key.lower() in part.lower() and key not in seen:
                out.append({"place": part, "items": items})
                seen.add(key)
                break
    return out[:2]  # keep cards glanceable


def main() -> int:
    wf = json.loads(WAYFINDERS_IN.read_text(encoding="utf-8"))
    panels: dict[str, dict] = {}
    for f in wf["features"]:
        p = f["properties"]
        wid = str(p.get("id"))
        role = str(p.get("role", ""))
        rich = role.lower() == "dwell no pavilion"  # Nechells side - no pavilion to fall back on
        onward = str(p.get("onwardDestinations") or "")
        opportunities = match_opportunities(onward) if rich else []
        if rich and not opportunities:
            opportunities = [DEFAULT_OPPORTUNITIES]
        panels[wid] = {
            "id": wid,
            "side": "nechells" if rich else "city-core",
            "variant": "rich" if rich else "light",
            "type": p.get("type"),
            "destination": "Birmingham Knowledge Quarter",
            "heading": p.get("heading"),
            "walkTimeMin": p.get("walkTimeMin"),
            "nextMarker": p.get("nextMarker"),
            "nearbyStops": p.get("nearbyStops") or "",
            "crossingCaution": p.get("crossingCaution") or "",
            "findByNeed": FIND_BY_NEED if rich else [],
            "opportunities": opportunities,
            "pavilionGuide": not rich,  # city-core points to the pavilion for the full guide
            "static": STATIC_FIELDS,
            "dynamic": DYNAMIC_FIELDS,
        }

    out = {
        "schemaVersion": "0.1",
        "notes": "Conceptual wayfinder panel content. Opportunities are general/evergreen examples; "
                 "live fields (events, bus departures) are populated at deployment.",
        "sponsorship": {"model": "civic_partner", "maxScreenShare": 0.15, "guardrails": ["bounded", "no_tracking", "never_blocks_wayfinding"]},
        "panels": panels,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rich_n = sum(1 for v in panels.values() if v["variant"] == "rich")
    print(f"wrote {OUT.relative_to(ROOT)} | {len(panels)} panels ({rich_n} rich / {len(panels) - rich_n} light)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
