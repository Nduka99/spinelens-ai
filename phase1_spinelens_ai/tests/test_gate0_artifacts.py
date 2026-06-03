"""Integrity checks for Evidence Gate 0 artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


PHASE1_ROOT = Path(__file__).resolve().parents[1]
DATA = PHASE1_ROOT / "data"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_acquisition_status_matches_source_registry() -> None:
    registry = _read_csv(DATA / "source_registry_phase1.csv")
    acquisition = _read_csv(DATA / "source_acquisition_status_phase1.csv")

    registry_ids = {row["source_id"] for row in registry}
    acquisition_ids = {row["source_id"] for row in acquisition}

    assert acquisition_ids == registry_ids
    assert len(acquisition) == len(acquisition_ids)


def test_gate0_anchor_file_is_explicitly_provisional() -> None:
    anchors = _read_csv(DATA / "study_area_anchors_phase1.csv")

    assert len(anchors) >= 5
    assert {row["validation_status"] for row in anchors} == {"not_validated"}
    assert {row["coordinate_status"] for row in anchors} == {"provisional"}
    assert any(row["anchor_id"] == "ryder_street_pavilion_search_area" for row in anchors)
    assert any(row["anchor_id"] == "new_street_station" for row in anchors)
    assert any(row["anchor_id"] == "snow_hill_station" for row in anchors)


def test_gate0_boundary_metadata_is_not_funding_approved() -> None:
    metadata_path = DATA / "interim" / "study_area_boundary_phase1_metadata.json"
    boundary_path = DATA / "interim" / "study_area_boundary_phase1.geojson"

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    boundary = json.loads(boundary_path.read_text(encoding="utf-8"))

    assert metadata["status"] == "provisional_not_field_validated"
    assert metadata["funding_use"] == "not_approved"
    assert metadata["buffer_meters"] == 500
    assert boundary["features"][0]["properties"]["funding_use"] == "not_approved"


def test_claim_source_references_are_known_or_blank() -> None:
    registry = _read_csv(DATA / "source_registry_phase1.csv")
    claims = _read_csv(DATA / "evidence_claims_register.csv")
    registry_ids = {row["source_id"] for row in registry}

    for claim in claims:
        refs = [source_id for source_id in claim["source_ids"].split(";") if source_id]
        assert all(source_id in registry_ids for source_id in refs)


def test_raw_data_manifest_has_provenance_columns() -> None:
    manifest_path = DATA / "raw_data_manifest_phase1.csv"
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])

    required = {
        "source_id",
        "raw_file_path",
        "file_size_bytes",
        "sha256",
        "download_url",
        "downloaded_at_utc",
        "license",
        "quality_status",
    }
    assert required <= columns


def test_gate0a_route_nodes_have_one_primary_gateway() -> None:
    nodes = _read_csv(DATA / "route_nodes_phase1.csv")

    node_ids = [row["node_id"] for row in nodes]
    assert len(node_ids) == len(set(node_ids))
    assert {row["validation_status"] for row in nodes} == {"not_validated"}

    gateways = [
        row for row in nodes if row["route_role"] == "primary_phase1_pavilion_site_search_area"
    ]
    assert len(gateways) == 1
    assert gateways[0]["node_id"] == "ryder_street_pavilion_search_area"


def test_gate0a_route_families_reference_known_nodes() -> None:
    nodes = _read_csv(DATA / "route_nodes_phase1.csv")
    families = _read_csv(DATA / "route_families_phase1.csv")
    node_ids = {row["node_id"] for row in nodes}

    assert families
    for family in families:
        assert family["origin_node_id"] in node_ids
        assert family["gateway_node_id"] in node_ids
        assert family["gateway_node_id"] == "ryder_street_pavilion_search_area"
        assert family["onward_anchor_id"] in node_ids


def test_gate0a_experimental_station_corridors_are_explicit() -> None:
    families = _read_csv(DATA / "route_families_phase1.csv")

    experimental = {
        row["route_family_id"]
        for row in families
        if row["priority"] == "experimental_phase1"
    }

    assert "new_street_to_ryder_gateway" in experimental
    assert "snow_hill_to_ryder_gateway" in experimental


def test_gate0a_pavilion_candidate_site_is_explicitly_provisional() -> None:
    sites = _read_csv(DATA / "pavilion_candidate_sites_phase1.csv")

    assert any(row["candidate_site_id"] == "ryder_grassland_search_area" for row in sites)
    assert {row["evidence_status"] for row in sites} == {"not_validated"}


def test_pavilion_visual_context_is_recorded_as_orientation_only() -> None:
    note_path = PHASE1_ROOT / "docs" / "pavilion_site_visual_context_note.md"
    note = note_path.read_text(encoding="utf-8")

    assert "orientation_only_not_validated" in note
    assert "curved grass island" in note
    assert "not an authoritative public dataset" in note


def test_gate0a_wayfinder_content_requirements_cover_core_phase1_assets() -> None:
    requirements = _read_csv(DATA / "wayfinder_content_requirements_phase1.csv")
    requirement_ids = {row["content_id"] for row in requirements}

    assert "pavilion_arrival_panel" in requirement_ids
    assert "origin_new_street_wayfinder" in requirement_ids
    assert "origin_snow_hill_wayfinder" in requirement_ids
    assert "tactical_ground_graphics" in requirement_ids
    assert "crossing_wayfinder" in requirement_ids
