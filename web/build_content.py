"""Build the sanitized public content bundle for the static web app.

The internal evidence exports keep source IDs, evidence levels, caveats and modelling language.
The presentation app should not ship that internal vocabulary directly. This script translates the
current Phase 1 evidence pack into a small public contract for the Vite/React app.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INTERNAL_EXPORTS = ROOT / "phase1_spinelens_ai" / "outputs" / "exports"
INTERNAL_TABLES = ROOT / "phase1_spinelens_ai" / "outputs" / "tables"
PUBLIC_CONTENT = ROOT / "web" / "public" / "content"


ROUTE_LABELS = {
    "colmore_to_ryder_gateway": "Colmore Row",
    "new_street_to_ryder_gateway": "New Street",
    "nechells_dartmouth_to_ryder_gateway": "Nechells / Dartmouth",
    "moor_street_to_ryder_gateway": "Moor Street",
    "snow_hill_to_ryder_gateway": "Snow Hill",
}

ROLE_LABELS = {
    "deck_route_1_city_core_origin": "City core origin",
    "deck_route_2_moor_street_origin": "Station origin",
    "deck_route_3_nechells_origin": "Neighbourhood origin",
    "experimental_phase1_tactical_corridor_origin": "Additional tested origin",
    "gateway_site_search_area": "Gateway area",
    "priority_crossing_barrier": "Crossing barrier",
    "bkq_anchor": "B-KQ destination",
}

INTERVENTION_LABELS = {
    "directional_totem": "Directional totem",
    "ground_graphic": "Ground marker",
    "lighting_marker": "Lighting marker",
    "overhead_banner": "Overhead marker",
    "crossing_support": "Crossing support",
}

# Per-chapter camera for the cinematic map fly-through: [lng, lat, zoom, pitch, bearing].
DEFAULT_FOCUS = [-1.8924, 52.4845, 14.0, 35, 18]
# Narrative zoom rhythm: open wide for context, push in TIGHT on the three
# intervention points (corridor, barrier, gateway), then pull back for the close.
# Tuned by feel - easy to adjust. [lng, lat, zoom, pitch, bearing]
CHAPTER_FOCUS = {
    "challenge": [-1.8935, 52.4838, 13.6, 30, 16],  # wide - show the gap
    "one-spine": [-1.8924, 52.4840, 14.6, 45, 20],  # slight push - whole route
    "legibility": [-1.8950, 52.4828, 14.4, 35, 0],  # moderate - needs breadth
    "corridor": [-1.8918, 52.4840, 16.0, 55, 28],  # tight - the shared trunk (eased back a touch)
    "barrier": [-1.883, 52.48622, 16.8, 60, 44],  # tightest - the real Dartmouth/Jennens junction
    "wayfinding": [-1.889, 52.4839, 14.7, 40, 8],  # centred on the wayfinder cluster; fits all 12 with margin
    "gateway": [-1.89227, 52.48422, 18.4, 58, 30],  # very close on the pavilion
    "budget": [-1.8930, 52.4838, 13.9, 30, 18],  # pull back - recap
    "case": [-1.8905, 52.4838, 13.8, 34, 14],  # wide confident overview - the whole spine
    "ask": [-1.8922, 52.4845, 14.3, 40, 24],  # confident wide finish
}


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def route_public_name(route_id: str) -> str:
    return ROUTE_LABELS.get(route_id, route_id.replace("_", " ").title())


def pct(value: float) -> int:
    return round(float(value) * 100)


def public_role(value: str) -> str:
    return ROLE_LABELS.get(value, value.replace("_", " ").title())


def public_intervention(value: str) -> str:
    return INTERVENTION_LABELS.get(value, value.replace("_", " ").title())


def public_priority(value: Any) -> str:
    if str(value).isdigit():
        return f"Priority {value}"
    if value:
        return "Additional tested route"
    return "Route"


def build_chapters(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    stages = evidence["stages"]
    crossing = stages["crossing"]
    corridor = stages["corridor"]
    wayfinders = stages["wayfinders"]
    pavilion = stages["pavilion"]
    budget = evidence["budget"]

    return [
        {
            "id": "challenge",
            "title": "Close, Yet Far",
            "kicker": "The problem",
            "body": (
                "The Knowledge Quarter is only minutes from the city centre, but the way there is "
                "unclear, broken up and easy to miss."
            ),
            "confidence": "modelled",
            "stats": [
                {"label": "vehicles a day at the main barrier", "value": crossing["aadf_a4540"]},
                {"label": "injury collisions nearby, 2020-2024", "value": crossing["collisions_150m_2020_2024"]},
            ],
            "map": {"layers": ["routes", "study_boundary"]},
        },
        {
            "id": "one-spine",
            "title": "One Route",
            "kicker": "The proposal",
            "body": (
                "Phase 1 makes the route easy to see and follow: clear wayfinders, a bright amber "
                "route on the ground, a safer place to cross, and a welcoming pavilion at the entrance."
            ),
            "confidence": "modelled",
            "stats": [{"label": "Phase 1 budget", "value": budget["envelope_gbp"], "format": "gbp"}],
            "map": {"layers": ["corridor", "wayfinders"]},
        },
        {
            "id": "legibility",
            "title": "Why It Feels Far",
            "kicker": "Following the route",
            "body": (
                "Some approaches are far easier to follow than others. SpineLens AI shows each "
                "route and the points where people are most likely to lose their way."
            ),
            "confidence": "modelled",
            "stats": [
                {"label": "easiest approach", "value": route_public_name(stages["route_legibility"]["most_legible"])},
                {"label": "hardest approach", "value": route_public_name(stages["route_legibility"]["least_legible"])},
            ],
            "map": {"layers": ["routes"]},
        },
        {
            "id": "corridor",
            "title": "The Amber Route",
            "kicker": "One clear route",
            "body": (
                "Near the entrance, the city-centre approaches join into one main route. That lets "
                "Phase 1 focus on making this stretch unmistakable."
            ),
            "confidence": "modelled",
            "stats": [
                {"label": "shared stretch", "value": corridor["trunk_km"], "format": "km"},
                {"label": "nearest major road", "value": corridor["nearest_major_road_m"], "format": "m"},
            ],
            "map": {"layers": ["corridor", "routes"]},
        },
        {
            "id": "barrier",
            "title": "The Barrier",
            "kicker": "The crossing",
            "body": (
                "The Dartmouth/Jennens junction is the hardest place to cross, and a real barrier "
                "between the two areas. A quick Phase 1 fix improves it now, while a bigger road "
                "upgrade is worked out."
            ),
            "confidence": "verified",
            "stats": [
                {"label": "vehicles a day", "value": crossing["aadf_a4540"]},
                {"label": "cycles a day", "value": crossing["cycles_a4540"]},
                {"label": "serious or fatal collisions nearby", "value": crossing["serious_or_fatal_150m"]},
            ],
            "map": {"layers": ["routes", "corridor", "wayfinders"]},
        },
        {
            "id": "wayfinding",
            "title": "Find Your Way",
            "kicker": "Value for money",
            "body": (
                f"{wayfinders['count']} wayfinders guide you the whole way. They run across the "
                "city-centre approaches and over the Dartmouth crossing into the Knowledge Quarter, "
                "without cluttering every corner."
            ),
            "confidence": "modelled",
            "stats": [
                {"label": "wayfinders", "value": wayfinders["count"]},
                {"label": "large interactive signs", "value": wayfinders["tiers"].get("tier2_totem", 0)},
                {"label": "small markers", "value": wayfinders["tiers"].get("tier3_marker", 0)},
            ],
            "map": {"layers": ["wayfinders", "routes"]},
        },
        {
            "id": "gateway",
            "title": "The Gateway",
            "kicker": "Arriving at B-KQ",
            "body": (
                "A timber pavilion gives the Knowledge Quarter a welcoming front door. It can be "
                "removed later, so the risk and long-term commitment stay low."
            ),
            "confidence": "modelled",
            "stats": [
                {"label": "site suitability", "value": pct(pavilion["score"]), "format": "percent"},
                {"label": "form", "value": "removable timber pavilion"},
            ],
            "map": {"layers": ["corridor"]},
        },
        {
            "id": "budget",
            "title": "Within Budget",
            "kicker": "The first million",
            "body": (
                "The likely cost fits inside the £1m budget, with money to spare. These are early "
                "estimates and would be confirmed before anything is funded."
            ),
            "confidence": "estimate",
            "stats": [
                {"label": "likely cost", "value": budget["net_of_sponsorship"]["central"], "format": "gbp"},
                {"label": "money to spare", "value": budget["envelope_check"]["headroom_central"], "format": "gbp"},
            ],
            "map": {"layers": ["corridor", "wayfinders"]},
        },
        {
            "id": "case",
            "title": "Why Back It",
            "kicker": "Why it's worth it",
            "body": (
                "Phase 1 links the city centre to the Knowledge Quarter's two universities and "
                "innovation hub with a clearer, safer walk. It is built to be low-risk: a removable "
                "pavilion and a step-by-step crossing fix, with the likely cost inside the £1m budget "
                "and money to spare. Local sponsors help pay for the wayfinders."
            ),
            "confidence": "estimate",
            "stats": [
                {"label": "connects", "value": "2 universities + innovation hub"},
                {"label": "built to be", "value": "removable + step by step"},
                {"label": "part-funded by", "value": "local sponsors"},
            ],
            "map": {"layers": ["routes", "corridor", "wayfinders"]},
        },
        {
            "id": "ask",
            "title": "The Ask",
            "kicker": "What your backing unlocks",
            "body": (
                "Back Phase 1, with its wayfinders, amber route, safer crossing and removable "
                "gateway, to turn a strong idea into a real, visible walk from the city centre to "
                "the Knowledge Quarter that we can test, learn from and build on."
            ),
            "confidence": "estimate",
            "stats": [
                {"label": "Phase 1 ask", "value": budget["envelope_gbp"], "format": "gbp"},
                {"label": "what you get", "value": "wayfinders, route, crossing, gateway"},
            ],
            "map": {"layers": ["routes", "corridor", "wayfinders"]},
        },
    ]


def load_legibility_before_after() -> list[dict[str, Any]]:
    """Route legibility before vs after wayfinding (from notebook 07), as 0-100 scores.

    Read from the internal tables and sanitised to public route names. Returns [] if the
    table is absent so the bundle still builds.
    """
    path = INTERNAL_TABLES / "wayfinder_before_after_rli.csv"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                {
                    "route": route_public_name(f"{row['route_family']}_to_ryder_gateway"),
                    "before": pct(float(row["RLI_before"])),
                    "after": pct(float(row["RLI_after"])),
                    "delta": pct(float(row["delta"])),
                }
            )
    rows.sort(key=lambda r: r["after"], reverse=True)
    return rows


def build_metrics(evidence: dict[str, Any]) -> dict[str, Any]:
    routes = evidence["stages"]["route_legibility"]["routes"]
    return {
        "legibilityBeforeAfter": load_legibility_before_after(),
        "legibility": [
            {
                "route": route_public_name(row["route_family"]),
                "score": pct(row["RLI"]),
                "walkTimeMin": row["walk_time_min"],
                "directness": pct(row["directness"]),
            }
            for row in routes
        ],
        "budget": {
            "envelope": evidence["budget"]["envelope_gbp"],
            "centralNet": evidence["budget"]["net_of_sponsorship"]["central"],
            "headroomCentral": evidence["budget"]["envelope_check"]["headroom_central"],
            "highEstimateFits": evidence["budget"]["envelope_check"]["fits_high"],
        },
        "wayfinders": evidence["stages"]["wayfinders"],
        "crossing": {
            "vehiclesPerDay": evidence["stages"]["crossing"]["aadf_a4540"],
            "cyclesPerDay": evidence["stages"]["crossing"]["cycles_a4540"],
            "nearbyCollisions": evidence["stages"]["crossing"]["collisions_150m_2020_2024"],
            "seriousOrFatal": evidence["stages"]["crossing"]["serious_or_fatal_150m"],
        },
    }


def clean_layer_properties(layer_name: str, props: dict[str, Any]) -> dict[str, Any]:
    """Keep only public-safe display properties for map interactions."""

    if layer_name == "anchors":
        return {
            "name": props.get("anchor_name"),
            "role": public_role(str(props.get("anchor_role", ""))),
            "status": "To be confirmed on site",
        }

    if layer_name == "routes":
        return {
            "name": route_public_name(str(props.get("route_family", ""))),
            "priority": public_priority(props.get("priority")),
            "legibilityScore": pct(float(props.get("RLI", 0) or 0)),
        }

    if layer_name == "corridor":
        return {
            "role": "Amber route",
            "sharedRoutes": int(props.get("multiplicity", 0) or 0),
            "lengthM": round(float(props.get("length_m", 0) or 0), 1),
            "intensity": round(float(props.get("intensity", 0) or 0), 3),
            "suitability": pct(float(props.get("suitability", 0) or 0)),
        }

    if layer_name == "study_boundary":
        return {
            "name": "Phase 1 study area",
            "status": "The area we looked at",
        }

    if layer_name == "wayfinders":
        return {
            "id": props.get("wayfinder_id"),
            "type": public_intervention(str(props.get("intervention_type", ""))),
            "heading": props.get("heading_to_gateway"),
            "walkTimeMin": props.get("walk_time_to_gateway_min"),
            "nextMarker": props.get("next_marker"),
            "nearbyStops": props.get("nearby_bus_stops") or "",
            "onwardDestinations": props.get("onward_destinations"),
            "crossingCaution": props.get("crossing_caution") or "",
            "role": str(props.get("content_role", "")).replace("_", " ").title(),
            "sponsorshipEnabled": bool(props.get("sponsorship_enabled")),
        }

    return {}


def sanitize_geojson(layer_name: str, source: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": feature.get("geometry"),
                "properties": clean_layer_properties(layer_name, feature.get("properties") or {}),
            }
            for feature in source.get("features", [])
        ],
    }


def copy_layers(evidence: dict[str, Any], output_dir: Path) -> list[dict[str, str]]:
    layers_out = output_dir / "layers"
    layers_out.mkdir(parents=True, exist_ok=True)
    public_layers = []
    for layer in evidence["layers"]:
        src = INTERNAL_EXPORTS / layer["file"]
        dst = layers_out / Path(layer["file"]).name
        source_geojson = read_json(src)
        write_json(dst, sanitize_geojson(layer["name"], source_geojson))
        public_layers.append(
            {
                "id": layer["name"],
                "file": f"layers/{dst.name}",
                "kind": "geojson",
            }
        )
    return public_layers


def build_public_bundle() -> dict[str, Any]:
    evidence = read_json(INTERNAL_EXPORTS / "evidence_pack.json")
    public_layers = copy_layers(evidence, PUBLIC_CONTENT)

    chapters = build_chapters(evidence)
    for chapter in chapters:
        chapter["map"]["focus"] = CHAPTER_FOCUS.get(chapter["id"], DEFAULT_FOCUS)

    return {
        "schemaVersion": "0.1.0",
        "project": {
            "title": "The Innovation Spine",
            "product": "SpineLens AI",
            "tagline": "A clear, safe walk from Birmingham city centre to the Knowledge Quarter.",
            "phase": "Phase 1 - Make It Visible",
            "envelope": "£1,000,000",
        },
        "chapters": chapters,
        "metrics": build_metrics(evidence),
        "layers": public_layers,
        "confidenceLabels": {
            "verified": "Measured data",
            "modelled": "Our analysis",
            "estimate": "Early estimate",
        },
        "disclaimer": (
            "A concept to show what's possible and start the conversation. The figures are early "
            "estimates, and costs and details would be checked before anything is built."
        ),
    }


def validate_public_files(bundle: dict[str, Any]) -> list[str]:
    banned_terms = [
        "OSM",
        "OSMnx",
        "DfT",
        "STATS19",
        "AADF",
        "NaPTAN",
        "HM Land Registry",
        "INSPIRE",
        "Gate 0",
        "Evidence Level",
        "source_id",
        "route_family",
        "quality_audited",
    ]
    public_files = [PUBLIC_CONTENT / "spine.json"]
    public_files.extend((PUBLIC_CONTENT / "layers").glob("*.geojson"))

    text = json.dumps(bundle, ensure_ascii=False)
    for path in public_files:
        if path.exists():
            text += "\n" + path.read_text(encoding="utf-8")
    return [term for term in banned_terms if term.lower() in text.lower()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if the public bundle leaks internal terms.")
    args = parser.parse_args()

    bundle = build_public_bundle()
    write_json(PUBLIC_CONTENT / "spine.json", bundle)

    leaks = validate_public_files(bundle)
    if leaks:
        print("Public content build completed with internal-term leaks:")
        for leak in leaks:
            print(f"- {leak}")
        return 1 if args.check else 0

    print(f"Built {PUBLIC_CONTENT / 'spine.json'}")
    print(f"Copied {len(bundle['layers'])} public GeoJSON layers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
