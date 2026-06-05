"""Build the sanitized public content bundle for the static web app.

The internal evidence exports keep source IDs, evidence levels, caveats and modelling language.
The presentation app should not ship that internal vocabulary directly. This script translates the
current Phase 1 evidence pack into a small public contract for the Vite/React app.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INTERNAL_EXPORTS = ROOT / "phase1_spinelens_ai" / "outputs" / "exports"
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
# Tuned by feel — easy to adjust. [lng, lat, zoom, pitch, bearing]
CHAPTER_FOCUS = {
    "challenge": [-1.8935, 52.4838, 13.6, 30, 16],  # wide — show the gap
    "one-spine": [-1.8924, 52.4840, 14.6, 45, 20],  # slight push — whole route
    "legibility": [-1.8950, 52.4828, 14.4, 35, 0],  # moderate — needs breadth
    "corridor": [-1.8918, 52.4840, 16.4, 55, 28],  # tight — the shared trunk
    "barrier": [-1.8844, 52.4864, 17.0, 60, 38],  # tightest — the junction
    "wayfinding": [-1.889, 52.4845, 14.6, 45, 12],  # widen — city-core + onward cluster network
    "gateway": [-1.892412, 52.484042, 17.3, 60, 30],  # tight — the pavilion site
    "budget": [-1.8930, 52.4838, 13.9, 30, 18],  # pull back — recap
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
                "Birmingham Knowledge Quarter is minutes from the city core, but the route feels "
                "unclear, broken and easy to miss."
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
            "title": "One Spine",
            "kicker": "The proposal",
            "body": (
                "Phase 1 makes the route visible: wayfinders, an amber tactical corridor, a safer "
                "crossing moment and a civic gateway pavilion."
            ),
            "confidence": "modelled",
            "stats": [{"label": "Phase 1 envelope", "value": budget["envelope_gbp"], "format": "gbp"}],
            "map": {"layers": ["corridor", "wayfinders"]},
        },
        {
            "id": "legibility",
            "title": "Why It Feels Far",
            "kicker": "Route clarity",
            "body": (
                "The approaches are not equally easy to read. The web app shows the route choices "
                "and the points where confidence drops."
            ),
            "confidence": "modelled",
            "stats": [
                {"label": "clearest approach", "value": route_public_name(stages["route_legibility"]["most_legible"])},
                {"label": "hardest approach", "value": route_public_name(stages["route_legibility"]["least_legible"])},
            ],
            "map": {"layers": ["routes", "anchors"]},
        },
        {
            "id": "corridor",
            "title": "The Corridor",
            "kicker": "A visible route",
            "body": (
                "The city-core approaches feed one shared trunk near the gateway, so Phase 1 can "
                "focus visual intensity where it matters most."
            ),
            "confidence": "modelled",
            "stats": [
                {"label": "shared trunk", "value": corridor["trunk_km"], "format": "km"},
                {"label": "nearest major road", "value": corridor["nearest_major_road_m"], "format": "m"},
            ],
            "map": {"layers": ["corridor", "routes"]},
        },
        {
            "id": "barrier",
            "title": "The Barrier",
            "kicker": "Crossing case",
            "body": (
                "The Dartmouth/Jennens crossing is the concentrated severance point. A tactical "
                "Phase 1 improvement keeps momentum while the fuller highways upgrade is developed."
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
            "kicker": "Clarity per pound",
            "body": (
                f"{wayfinders['count']} tiered wayfinders make the route legible end to end - on the "
                "city-core approaches and onward across the Dartmouth crossing into the Knowledge "
                "Quarter cluster, without overbuilding every decision point."
            ),
            "confidence": "modelled",
            "stats": [
                {"label": "wayfinders", "value": wayfinders["count"]},
                {"label": "interactive totems", "value": wayfinders["tiers"].get("tier2_totem", 0)},
                {"label": "light markers", "value": wayfinders["tiers"].get("tier3_marker", 0)},
            ],
            "map": {"layers": ["wayfinders", "anchors", "routes"]},
        },
        {
            "id": "gateway",
            "title": "The Gateway",
            "kicker": "First moment of arrival",
            "body": (
                "A reversible timber pavilion gives B-KQ a public welcome point while keeping site "
                "risk and long-term commitment manageable."
            ),
            "confidence": "modelled",
            "stats": [
                {"label": "site suitability", "value": pct(pavilion["score"]), "format": "percent"},
                {"label": "form", "value": "reversible timber pavilion"},
            ],
            "map": {"layers": ["anchors", "corridor"]},
        },
        {
            "id": "budget",
            "title": "Within Budget",
            "kicker": "The first million",
            "body": (
                "The central estimate fits the £1m envelope with headroom. Costs remain early "
                "estimates and must be confirmed before funding decisions."
            ),
            "confidence": "estimate",
            "stats": [
                {"label": "central estimate, net", "value": budget["net_of_sponsorship"]["central"], "format": "gbp"},
                {"label": "central headroom", "value": budget["envelope_check"]["headroom_central"], "format": "gbp"},
            ],
            "map": {"layers": ["corridor", "wayfinders"]},
        },
        {
            "id": "ask",
            "title": "The Ask",
            "kicker": "What backing unlocks",
            "body": (
                "Back Phase 1 to turn a winning concept into a visible, testable public route from "
                "the city core to B-KQ."
            ),
            "confidence": "estimate",
            "stats": [{"label": "package", "value": "wayfinding, corridor, crossing, gateway"}],
            "map": {"layers": ["routes", "corridor", "wayfinders"]},
        },
    ]


def build_metrics(evidence: dict[str, Any]) -> dict[str, Any]:
    routes = evidence["stages"]["route_legibility"]["routes"]
    return {
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
            "role": "Tactical corridor surface",
            "sharedRoutes": int(props.get("multiplicity", 0) or 0),
            "lengthM": round(float(props.get("length_m", 0) or 0), 1),
            "intensity": round(float(props.get("intensity", 0) or 0), 3),
            "suitability": pct(float(props.get("suitability", 0) or 0)),
        }

    if layer_name == "study_boundary":
        return {
            "name": "Phase 1 study area",
            "status": "Working boundary for the evidence story",
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
            "tagline": "Reconnecting Birmingham Knowledge Quarter to the city core.",
            "phase": "Phase 1 - Make It Visible",
            "envelope": "£1,000,000",
        },
        "chapters": chapters,
        "metrics": build_metrics(evidence),
        "layers": public_layers,
        "confidenceLabels": {
            "verified": "Verified data",
            "modelled": "Evidence-led model",
            "estimate": "Early estimate",
        },
        "disclaimer": (
            "Evidence-led concept for presentation and stakeholder discussion. Costs, consents "
            "and field conditions to be confirmed before funding decisions."
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
