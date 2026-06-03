"""Gate 0B source reachability and provenance helpers."""

from __future__ import annotations

import csv
import hashlib
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Iterable

import requests


PRIORITY_1_SOURCE_IDS = {
    "osm_network",
    "os_open_roads",
    "os_open_map_local",
    "ons_open_geography",
    "os_open_names",
    "birmingham_city_observatory",
}

OS_DOWNLOAD_PRODUCT_IDS = {
    "os_open_roads": "OpenRoads",
    "os_open_map_local": "OpenMapLocal",
    "os_open_names": "OpenNames",
    "os_open_greenspace": "OpenGreenspace",
}


@dataclass(frozen=True)
class ReachabilityResult:
    """A single source reachability observation."""

    source_id: str
    checked_at_utc: str
    url: str
    method: str
    reachable: str
    status_code: str
    final_url: str
    content_type: str
    content_length: str
    elapsed_seconds: str
    forensic_status: str
    notes: str


@dataclass(frozen=True)
class DownloadResult:
    """A controlled raw-file download observation."""

    path: Path
    file_name: str
    file_size_bytes: int
    sha256: str
    md5: str
    downloaded_at_utc: str
    final_url: str


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file as dictionaries."""

    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, rows: Iterable[dict[str, str]], fieldnames: list[str]) -> None:
    """Write dictionaries to CSV, preserving a declared column order."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def utc_now_iso() -> str:
    """Return a UTC timestamp suitable for provenance ledgers."""

    return datetime.now(UTC).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    """Calculate a SHA-256 checksum for a local file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def md5_file(path: Path) -> str:
    """Calculate an MD5 checksum when a source publishes MD5 metadata."""

    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_file_with_checks(
    url: str,
    output_path: Path,
    expected_md5: str = "",
    max_bytes: int = 20_000_000,
    timeout_seconds: int = 60,
) -> DownloadResult:
    """Download a bounded raw file and verify source-published MD5 when available."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    if temp_path.exists():
        temp_path.unlink()

    headers = {"User-Agent": "BKQ-SpineLens-Gate0B/0.1 controlled-raw-acquisition"}
    with requests.get(url, stream=True, timeout=timeout_seconds, headers=headers) as response:
        response.raise_for_status()
        total = 0
        with temp_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_bytes:
                    temp_path.unlink(missing_ok=True)
                    raise ValueError(
                        f"Download exceeded max_bytes={max_bytes}: {url}"
                    )
                handle.write(chunk)
        final_url = response.url

    os.replace(temp_path, output_path)
    actual_md5 = md5_file(output_path)
    if expected_md5 and actual_md5.lower() != expected_md5.lower():
        raise ValueError(
            f"MD5 mismatch for {output_path}: expected {expected_md5}, got {actual_md5}"
        )

    return DownloadResult(
        path=output_path,
        file_name=output_path.name,
        file_size_bytes=output_path.stat().st_size,
        sha256=sha256_file(output_path),
        md5=actual_md5,
        downloaded_at_utc=utc_now_iso(),
        final_url=final_url,
    )


def build_manifest_row(
    manifest_id: str,
    source_id: str,
    raw_file_path: Path,
    phase1_root: Path,
    download_url: str,
    source_publication_date: str,
    source_version: str,
    license_name: str,
    provenance_note: str,
    quality_status: str = "raw_acquired_not_quality_audited",
    reviewer: str = "Codex",
) -> dict[str, str]:
    """Build a raw-data manifest row from a local file."""

    return {
        "manifest_id": manifest_id,
        "source_id": source_id,
        "raw_file_path": str(raw_file_path.relative_to(phase1_root)).replace("\\", "/"),
        "file_name": raw_file_path.name,
        "file_size_bytes": str(raw_file_path.stat().st_size),
        "sha256": sha256_file(raw_file_path),
        "download_url": download_url,
        "downloaded_at_utc": utc_now_iso(),
        "source_publication_date": source_publication_date,
        "source_version": source_version,
        "license": license_name,
        "provenance_note": provenance_note,
        "quality_status": quality_status,
        "reviewer": reviewer,
    }


def upsert_manifest_rows(
    existing_rows: Iterable[dict[str, str]],
    new_rows: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    """Upsert manifest rows by manifest ID."""

    by_id = {row["manifest_id"]: dict(row) for row in existing_rows}
    for row in new_rows:
        by_id[row["manifest_id"]] = dict(row)
    return sorted(by_id.values(), key=lambda row: row["manifest_id"])


def mark_sources_raw_acquired(
    acquisition_rows: Iterable[dict[str, str]],
    source_ids: set[str],
) -> list[dict[str, str]]:
    """Mark sources as raw-acquired while keeping quality/funding gates closed."""

    updated: list[dict[str, str]] = []
    note = "Gate 0B acquired first raw extract and recorded checksum; quality audit still pending."
    for row in acquisition_rows:
        next_row = dict(row)
        if row["source_id"] in source_ids:
            next_row["forensic_status"] = "raw_acquired_pending_quality_audit"
            next_row["evidence_level"] = "2"
            next_row["raw_data_acquired"] = "yes"
            next_row["checksum_recorded"] = "yes"
            next_row["quality_audited"] = "no"
            next_row["cross_checked"] = "no"
            next_row["can_support_funding_claim"] = "no"
            next_row["next_action"] = "Run quality audit before using in route or site scoring."
            if note not in next_row["notes"]:
                next_row["notes"] = f"{next_row['notes']} {note}".strip()
        updated.append(next_row)
    return updated


def priority_1_registry_rows(registry_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    """Return registry rows for the Gate 0B Priority 1 source set."""

    return [row for row in registry_rows if row["source_id"] in PRIORITY_1_SOURCE_IDS]


def check_url_reachability(
    source_id: str,
    url: str,
    timeout_seconds: int = 20,
    session: requests.Session | None = None,
) -> ReachabilityResult:
    """Check a source URL without downloading bulk data."""

    client = session or requests.Session()
    headers = {
        "User-Agent": "BKQ-SpineLens-Gate0B/0.1 source-reachability-check",
        "Accept": "text/html,application/json,application/xml,text/plain,*/*;q=0.8",
    }
    checked_at = utc_now_iso()
    started = perf_counter()

    try:
        response = client.head(url, allow_redirects=True, timeout=timeout_seconds, headers=headers)
        method = "HEAD"
        if response.status_code in {403, 405, 406}:
            response.close()
            response = client.get(
                url,
                allow_redirects=True,
                timeout=timeout_seconds,
                headers={**headers, "Range": "bytes=0-2047"},
                stream=True,
            )
            method = "GET_STREAM_RANGE"
        elapsed = perf_counter() - started
        status_code = str(response.status_code)
        reachable = "yes" if 200 <= response.status_code < 400 else "no"
        forensic_status = "source_reachable" if reachable == "yes" else "reachability_failed"
        notes = "HTTP response received; no bulk raw data downloaded."
        result = ReachabilityResult(
            source_id=source_id,
            checked_at_utc=checked_at,
            url=url,
            method=method,
            reachable=reachable,
            status_code=status_code,
            final_url=response.url,
            content_type=response.headers.get("content-type", ""),
            content_length=response.headers.get("content-length", ""),
            elapsed_seconds=f"{elapsed:.3f}",
            forensic_status=forensic_status,
            notes=notes,
        )
        response.close()
        return result
    except requests.RequestException as exc:
        elapsed = perf_counter() - started
        return ReachabilityResult(
            source_id=source_id,
            checked_at_utc=checked_at,
            url=url,
            method="HEAD_OR_GET",
            reachable="no",
            status_code="",
            final_url="",
            content_type="",
            content_length="",
            elapsed_seconds=f"{elapsed:.3f}",
            forensic_status="reachability_error",
            notes=f"{type(exc).__name__}: {exc}",
        )


def run_reachability_checks(
    registry_rows: Iterable[dict[str, str]],
    source_ids: set[str] | None = None,
    timeout_seconds: int = 20,
) -> list[dict[str, str]]:
    """Run reachability checks for selected source registry rows."""

    selected_ids = source_ids or PRIORITY_1_SOURCE_IDS
    selected = [row for row in registry_rows if row["source_id"] in selected_ids]
    with requests.Session() as session:
        results = [
            asdict(
                check_url_reachability(
                    source_id=row["source_id"],
                    url=row["url"],
                    timeout_seconds=timeout_seconds,
                    session=session,
                )
            )
            for row in selected
        ]
    return sorted(results, key=lambda row: row["source_id"])


def fetch_os_download_candidates(
    product_ids: dict[str, str] | None = None,
    areas_of_interest: set[str] | None = None,
    timeout_seconds: int = 30,
) -> list[dict[str, str]]:
    """Fetch OS Downloads API metadata without downloading data files."""

    selected_products = product_ids or OS_DOWNLOAD_PRODUCT_IDS
    selected_areas = areas_of_interest or {"GB", "SP", "SO", "SK"}
    rows: list[dict[str, str]] = []

    with requests.Session() as session:
        for source_id, product_id in selected_products.items():
            url = f"https://api.os.uk/downloads/v1/products/{product_id}/downloads"
            response = session.get(url, timeout=timeout_seconds)
            response.raise_for_status()
            for item in response.json():
                area = str(item.get("area", ""))
                if area not in selected_areas:
                    continue
                rows.append(
                    {
                        "source_id": source_id,
                        "os_product_id": product_id,
                        "area": area,
                        "file_name": str(item.get("fileName", "")),
                        "format": str(item.get("format", "")),
                        "subformat": str(item.get("subformat", "")),
                        "size_bytes": str(item.get("size", "")),
                        "md5": str(item.get("md5", "")),
                        "download_url": str(item.get("url", "")),
                        "metadata_checked_at_utc": utc_now_iso(),
                        "download_decision": _download_decision(source_id, area, item),
                    }
                )
    return sorted(rows, key=lambda row: (row["source_id"], row["area"], row["format"]))


def _download_decision(source_id: str, area: str, item: dict[str, object]) -> str:
    """Classify a download candidate for cautious Gate 0B acquisition."""

    size = int(item.get("size") or 0)
    file_name = str(item.get("fileName", ""))
    if source_id == "os_open_greenspace" and area == "SP" and size <= 5_000_000:
        return "safe_small_candidate_for_pavilion_context"
    if source_id == "os_open_map_local" and area == "SP":
        return "useful_but_large_tile_review_before_download"
    if source_id in {"os_open_roads", "os_open_names"} and area == "GB":
        return "large_national_file_defer_until_storage_plan"
    if file_name:
        return "metadata_only_not_selected"
    return "metadata_unusable"


def update_acquisition_status_from_reachability(
    acquisition_rows: Iterable[dict[str, str]],
    reachability_rows: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    """Update the acquisition ledger after Gate 0B reachability checks."""

    reachability_by_id = {row["source_id"]: row for row in reachability_rows}
    updated: list[dict[str, str]] = []
    for row in acquisition_rows:
        next_row = dict(row)
        source_result = reachability_by_id.get(row["source_id"])
        if source_result is not None:
            next_row["forensic_status"] = source_result["forensic_status"]
            next_row["evidence_level"] = "1" if source_result["reachable"] == "yes" else "0"
            next_row["raw_data_acquired"] = "no"
            next_row["checksum_recorded"] = "no"
            next_row["quality_audited"] = "no"
            next_row["cross_checked"] = "no"
            next_row["can_support_funding_claim"] = "no"
            if source_result["reachable"] == "yes":
                next_row["next_action"] = "Acquire smallest useful extract and record checksum."
                confirmation_note = (
                    "Gate 0B confirmed source page/API reachability; no raw data downloaded."
                )
                if confirmation_note not in next_row["notes"]:
                    next_row["notes"] = f"{next_row['notes']} {confirmation_note}".strip()
            else:
                next_row["next_action"] = "Manually review URL or alternate official access path."
                issue_note = f"Gate 0B reachability issue: {source_result['notes']}"
                if issue_note not in next_row["notes"]:
                    next_row["notes"] = f"{next_row['notes']} {issue_note}".strip()
        updated.append(next_row)
    return updated


def reachability_fieldnames() -> list[str]:
    """Return the Gate 0B reachability report column order."""

    return [
        "source_id",
        "checked_at_utc",
        "url",
        "method",
        "reachable",
        "status_code",
        "final_url",
        "content_type",
        "content_length",
        "elapsed_seconds",
        "forensic_status",
        "notes",
    ]


def os_download_candidate_fieldnames() -> list[str]:
    """Return the OS download-candidate report column order."""

    return [
        "source_id",
        "os_product_id",
        "area",
        "file_name",
        "format",
        "subformat",
        "size_bytes",
        "md5",
        "download_url",
        "metadata_checked_at_utc",
        "download_decision",
    ]


def raw_data_manifest_fieldnames() -> list[str]:
    """Return the raw-data manifest column order."""

    return [
        "manifest_id",
        "source_id",
        "raw_file_path",
        "file_name",
        "file_size_bytes",
        "sha256",
        "download_url",
        "downloaded_at_utc",
        "source_publication_date",
        "source_version",
        "license",
        "provenance_note",
        "quality_status",
        "reviewer",
    ]
