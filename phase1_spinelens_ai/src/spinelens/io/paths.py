"""Canonical Phase 1 paths."""

from __future__ import annotations

from pathlib import Path

PHASE1_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PHASE1_ROOT / "data"
OUTPUTS_DIR = PHASE1_ROOT / "outputs"

RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

EXPORTS_DIR = OUTPUTS_DIR / "exports"
MAPS_DIR = OUTPUTS_DIR / "maps"
TABLES_DIR = OUTPUTS_DIR / "tables"
REPORTS_DIR = OUTPUTS_DIR / "reports"
