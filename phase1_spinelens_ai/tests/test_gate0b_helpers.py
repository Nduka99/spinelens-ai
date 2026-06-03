"""Tests for Gate 0B source acquisition helpers."""

from __future__ import annotations

from pathlib import Path

from spinelens.gate0b import (
    PRIORITY_1_SOURCE_IDS,
    build_manifest_row,
    mark_sources_raw_acquired,
    os_download_candidate_fieldnames,
    priority_1_registry_rows,
    raw_data_manifest_fieldnames,
    sha256_file,
    update_acquisition_status_from_reachability,
    upsert_manifest_rows,
)


def test_priority_1_registry_rows_are_selected_by_source_id() -> None:
    rows = [
        {"source_id": "osm_network"},
        {"source_id": "dft_stats19"},
        {"source_id": "os_open_roads"},
    ]

    selected = priority_1_registry_rows(rows)

    assert {row["source_id"] for row in selected} == {"osm_network", "os_open_roads"}
    assert "dft_stats19" not in PRIORITY_1_SOURCE_IDS


def test_os_download_candidate_schema_keeps_provenance_columns() -> None:
    fields = set(os_download_candidate_fieldnames())

    assert "source_id" in fields
    assert "file_name" in fields
    assert "size_bytes" in fields
    assert "md5" in fields
    assert "download_url" in fields
    assert "download_decision" in fields


def test_raw_data_manifest_schema_keeps_required_columns() -> None:
    fields = raw_data_manifest_fieldnames()

    assert fields[0] == "manifest_id"
    assert "sha256" in fields
    assert "downloaded_at_utc" in fields
    assert "quality_status" in fields


def test_reachability_update_keeps_funding_claims_blocked() -> None:
    acquisition_rows = [
        {
            "source_id": "osm_network",
            "priority_group": "Priority 1",
            "forensic_status": "not_started",
            "evidence_level": "0",
            "raw_data_acquired": "no",
            "checksum_recorded": "no",
            "quality_audited": "no",
            "cross_checked": "no",
            "field_validation_needed": "yes",
            "can_support_funding_claim": "no",
            "next_action": "Lock study boundary",
            "notes": "Volunteer data must be validated",
        }
    ]
    reachability_rows = [
        {
            "source_id": "osm_network",
            "reachable": "yes",
            "forensic_status": "source_reachable",
            "notes": "HTTP response received",
        }
    ]

    updated = update_acquisition_status_from_reachability(acquisition_rows, reachability_rows)

    assert updated[0]["forensic_status"] == "source_reachable"
    assert updated[0]["evidence_level"] == "1"
    assert updated[0]["raw_data_acquired"] == "no"
    assert updated[0]["checksum_recorded"] == "no"
    assert updated[0]["can_support_funding_claim"] == "no"


def test_reachability_update_does_not_duplicate_notes_on_rerun() -> None:
    note = "Gate 0B confirmed source page/API reachability; no raw data downloaded."
    acquisition_rows = [
        {
            "source_id": "osm_network",
            "priority_group": "Priority 1",
            "forensic_status": "source_reachable",
            "evidence_level": "1",
            "raw_data_acquired": "no",
            "checksum_recorded": "no",
            "quality_audited": "no",
            "cross_checked": "no",
            "field_validation_needed": "yes",
            "can_support_funding_claim": "no",
            "next_action": "Acquire smallest useful extract and record checksum.",
            "notes": f"Volunteer data must be validated {note}",
        }
    ]
    reachability_rows = [
        {
            "source_id": "osm_network",
            "reachable": "yes",
            "forensic_status": "source_reachable",
            "notes": "HTTP response received",
        }
    ]

    updated = update_acquisition_status_from_reachability(acquisition_rows, reachability_rows)

    assert updated[0]["notes"].count(note) == 1


def test_manifest_row_records_checksum_and_relative_path(tmp_path: Path) -> None:
    phase1_root = tmp_path / "phase1"
    raw_file = phase1_root / "data" / "raw" / "example.txt"
    raw_file.parent.mkdir(parents=True)
    raw_file.write_text("evidence", encoding="utf-8")

    row = build_manifest_row(
        manifest_id="test_manifest",
        source_id="osm_network",
        raw_file_path=raw_file,
        phase1_root=phase1_root,
        download_url="https://example.org/data",
        source_publication_date="unknown",
        source_version="test",
        license_name="ODbL",
        provenance_note="unit test",
    )

    assert row["raw_file_path"] == "data/raw/example.txt"
    assert row["sha256"] == sha256_file(raw_file)
    assert row["quality_status"] == "raw_acquired_not_quality_audited"


def test_manifest_upsert_replaces_existing_row() -> None:
    existing = [{"manifest_id": "a", "file_name": "old.txt"}]
    new = [{"manifest_id": "a", "file_name": "new.txt"}]

    rows = upsert_manifest_rows(existing, new)

    assert rows == [{"manifest_id": "a", "file_name": "new.txt"}]


def test_mark_sources_raw_acquired_keeps_quality_and_funding_gates_closed() -> None:
    acquisition_rows = [
        {
            "source_id": "osm_network",
            "priority_group": "Priority 1",
            "forensic_status": "source_reachable",
            "evidence_level": "1",
            "raw_data_acquired": "no",
            "checksum_recorded": "no",
            "quality_audited": "no",
            "cross_checked": "no",
            "field_validation_needed": "yes",
            "can_support_funding_claim": "no",
            "next_action": "Acquire smallest useful extract and record checksum.",
            "notes": "Volunteer data must be validated",
        }
    ]

    updated = mark_sources_raw_acquired(acquisition_rows, {"osm_network"})

    assert updated[0]["forensic_status"] == "raw_acquired_pending_quality_audit"
    assert updated[0]["evidence_level"] == "2"
    assert updated[0]["raw_data_acquired"] == "yes"
    assert updated[0]["checksum_recorded"] == "yes"
    assert updated[0]["quality_audited"] == "no"
    assert updated[0]["cross_checked"] == "no"
    assert updated[0]["can_support_funding_claim"] == "no"
