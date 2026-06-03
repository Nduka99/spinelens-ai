"""Pedestrian network loading and route helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteSeed:
    """Origin-destination pair for Phase 1 legibility analysis."""

    origin_name: str
    destination_name: str


DEFAULT_ROUTE_SEEDS: tuple[RouteSeed, ...] = (
    RouteSeed("Colmore Row", "Millennium Point"),
    RouteSeed("Moor Street Station", "Aston University"),
)
