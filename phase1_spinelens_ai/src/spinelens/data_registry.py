"""Phase 1 data registry helpers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RegistryPaths:
    """Canonical paths for the Phase 1 data registry."""

    phase1_root: Path

    @property
    def source_registry(self) -> Path:
        return self.phase1_root / "data" / "source_registry_phase1.csv"


def default_registry_paths() -> RegistryPaths:
    """Return registry paths relative to the installed source tree."""

    phase1_root = Path(__file__).resolve().parents[2]
    return RegistryPaths(phase1_root=phase1_root)


def load_source_registry(path: Path | None = None) -> list[dict[str, str]]:
    """Load the Phase 1 source registry as plain dictionaries."""

    registry_path = path or default_registry_paths().source_registry
    with registry_path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
