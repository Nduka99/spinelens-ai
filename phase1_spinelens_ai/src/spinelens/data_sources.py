"""Data source registry for Phase 1.

Network calls and downloads should be implemented in notebooks first, then moved
here once the source, version, and storage path are stable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataSource:
    name: str
    purpose: str
    raw_path: Path
    source_url: str | None = None
    notes: str = ""


PHASE1_DATA_SOURCES: tuple[DataSource, ...] = (
    DataSource(
        name="OpenStreetMap",
        purpose="Pedestrian network, street geometry, crossings, and POIs",
        raw_path=Path("phase1_spinelens_ai/data/raw/osm"),
        source_url="https://www.openstreetmap.org/",
        notes="Access through OSMnx once dependencies are installed.",
    ),
)
