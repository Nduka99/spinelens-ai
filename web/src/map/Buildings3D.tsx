/**
 * Shared 3D layers (Step 8): real OSM building footprints extruded to height
 * (named B-KQ destinations highlighted, city-core start points, B-KQ context
 * fabric, organic pavilion) + the improved crossing as road lines. Used by both
 * the Walk map and the Vision view so the journey itself is 3D.
 */
import { type ComponentProps } from "react";
import { Layer, Source } from "react-map-gl/maplibre";
import type { ExpressionSpecification } from "maplibre-gl";

import { palette } from "../theme/tokens";

type LayerConfig = ComponentProps<typeof Layer>;

const BUILDINGS_URL = "/content/layers/bkq_buildings_3d.geojson";
const CROSSING_URL = "/content/layers/crossing_improvement.geojson";
const TOTEMS_URL = "/content/layers/wayfinder_totems.geojson";

const buildingColor: ExpressionSpecification = [
  "match",
  ["get", "category"],
  "destination",
  "#5b9bd5", // named B-KQ buildings - highlighted
  "pavilion",
  "#5b9bd5", // the gateway pavilion - highlighted to match B-KQ
  "start",
  "#7a8aa0", // city-core start points
  "context",
  "#262d3d", // B-KQ fabric - recedes
  "#262d3d",
] as unknown as ExpressionSpecification;

const buildingsLayer: LayerConfig = {
  id: "bkq-buildings",
  type: "fill-extrusion",
  source: "buildings3d",
  paint: {
    "fill-extrusion-color": buildingColor,
    "fill-extrusion-height": ["get", "heightM"],
    "fill-extrusion-base": ["get", "baseM"],
    "fill-extrusion-opacity": 0.95,
    "fill-extrusion-vertical-gradient": true,
  },
};

const labelsLayer: LayerConfig = {
  id: "bkq-labels",
  type: "symbol",
  source: "buildings3d",
  filter: ["!=", ["get", "name"], ""],
  layout: {
    "text-field": ["get", "name"],
    "text-size": 11,
    "text-offset": [0, 0.6],
    "text-anchor": "top",
    "text-max-width": 9,
    "symbol-z-order": "source",
  },
  paint: {
    "text-color": "#f8fafc",
    "text-halo-color": "rgba(8,12,22,0.92)",
    "text-halo-width": 1.6,
  },
};

// Safer crossing: a signal-controlled crossing band across the carriageway +
// signal heads at the kerbs (after). Before = no safe crossing today (red, no signals).
function crossingBandLayer(after: boolean): LayerConfig {
  return {
    id: "vision-crossing-band",
    type: "fill",
    source: "crossingImprovement",
    filter: ["==", ["get", "kind"], "band"],
    paint: {
      "fill-color": after ? palette.amber : palette.rose, // amber fix vs red severance (in scheme)
      "fill-opacity": after ? 0.6 : 0.4,
      "fill-outline-color": after ? "#fde68a" : "#fb7185",
    },
  };
}

function crossingRefugeLayer(after: boolean): LayerConfig {
  return {
    id: "vision-crossing-refuge",
    type: "fill",
    source: "crossingImprovement",
    filter: ["==", ["get", "kind"], "refuge"],
    paint: {
      "fill-color": "#94a3b8", // pedestrian refuge island (after only)
      "fill-opacity": after ? 0.8 : 0,
      "fill-outline-color": "#cbd5e1",
    },
  };
}

function crossingSignalsLayer(after: boolean): LayerConfig {
  return {
    id: "vision-crossing-signals",
    type: "circle",
    source: "crossingImprovement",
    filter: ["==", ["get", "kind"], "signal"],
    paint: {
      "circle-radius": after ? 5 : 0,
      "circle-color": "#fbbf24",
      "circle-stroke-color": "#0b1220",
      "circle-stroke-width": 1.5,
      "circle-opacity": after ? 1 : 0,
    },
  };
}

function crossingLabelLayer(after: boolean): LayerConfig {
  return {
    id: "vision-crossing-label",
    type: "symbol",
    source: "crossingImprovement",
    filter: ["==", ["get", "kind"], "band"],
    layout: {
      "text-field": after ? "Safer crossing" : "No safe crossing today",
      "symbol-placement": "point",
      "text-size": 11,
      "text-offset": [0, -1.6],
    },
    paint: {
      "text-color": after ? "#bbf7d0" : "#fecaca",
      "text-halo-color": "rgba(8,12,22,0.92)",
      "text-halo-width": 1.6,
    },
  };
}

export function Buildings3D({ labels = true, visible = true }: { labels?: boolean; visible?: boolean }) {
  if (!visible) return null;
  return (
    <Source id="buildings3d" type="geojson" data={BUILDINGS_URL}>
      <Layer {...buildingsLayer} />
      {labels && <Layer {...labelsLayer} />}
    </Source>
  );
}

// Tall totems (directional/crossing) extruded; flat markers (ground/lighting) as discs.
const totemLayer: LayerConfig = {
  id: "wf-totems",
  type: "fill-extrusion",
  source: "wfTotems",
  filter: ["==", ["get", "form"], "totem"],
  paint: {
    "fill-extrusion-color": palette.amber,
    "fill-extrusion-height": ["get", "heightM"],
    "fill-extrusion-base": 0,
    "fill-extrusion-opacity": 0.92,
    "fill-extrusion-vertical-gradient": true,
  },
};

const markerLayer: LayerConfig = {
  id: "wf-markers",
  type: "circle",
  source: "wfTotems",
  filter: ["==", ["get", "form"], "marker"],
  paint: {
    "circle-radius": 6,
    "circle-color": palette.amber,
    "circle-stroke-color": palette.ink,
    "circle-stroke-width": 2,
    "circle-opacity": 0.9,
  },
};

function totemActiveLayer(activeId: string | null): LayerConfig {
  return {
    id: "wf-totem-active",
    type: "fill-extrusion",
    source: "wfTotems",
    filter: ["all", ["==", ["get", "id"], activeId ?? "__none__"], ["==", ["get", "form"], "totem"]],
    paint: { "fill-extrusion-color": "#fde68a", "fill-extrusion-height": 11, "fill-extrusion-base": 0, "fill-extrusion-opacity": 1 },
  };
}

function markerActiveLayer(activeId: string | null): LayerConfig {
  return {
    id: "wf-marker-active",
    type: "circle",
    source: "wfTotems",
    filter: ["all", ["==", ["get", "id"], activeId ?? "__none__"], ["==", ["get", "form"], "marker"]],
    paint: { "circle-radius": 11, "circle-color": "#fde68a", "circle-stroke-color": palette.amber, "circle-stroke-width": 2 },
  };
}

export function WayfinderTotems({ visible, activeId = null }: { visible: boolean; activeId?: string | null }) {
  if (!visible) return null;
  return (
    <Source id="wfTotems" type="geojson" data={TOTEMS_URL}>
      <Layer {...markerLayer} />
      <Layer {...totemLayer} />
      <Layer {...markerActiveLayer(activeId)} />
      <Layer {...totemActiveLayer(activeId)} />
    </Source>
  );
}

export function CrossingImprovement({ after, labels = true, visible = true }: { after: boolean; labels?: boolean; visible?: boolean }) {
  if (!visible) return null;
  return (
    <Source id="crossingImprovement" type="geojson" data={CROSSING_URL}>
      <Layer {...crossingRefugeLayer(after)} />
      <Layer {...crossingBandLayer(after)} />
      <Layer {...crossingSignalsLayer(after)} />
      {labels && <Layer {...crossingLabelLayer(after)} />}
    </Source>
  );
}
