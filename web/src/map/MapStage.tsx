/**
 * MapStage - the real Birmingham map the journey plays out on.
 *
 * Step 1: MapLibre GL + free keyless dark basemap + our five sanitised GeoJSON
 *         layers, on-brand, interactive.
 * Step 2: cinematic camera - flies to the active chapter's focus (pitch/zoom/
 *         bearing) and emphasises that chapter's layers. Honours reduced-motion.
 */
import { type ComponentProps, useEffect, useRef } from "react";
import Map, { Layer, NavigationControl, Source, type MapRef } from "react-map-gl/maplibre";
import type { ExpressionSpecification } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import { BASEMAP_STYLE_URL, motion, palette } from "../theme/tokens";
import { Buildings3D, CrossingImprovement } from "./Buildings3D";
import type { Focus, LayerReference } from "../types/content";

type LayerConfig = ComponentProps<typeof Layer>;

const DEFAULT_FOCUS: Focus = [-1.8924, 52.4845, 14.0, 35, 18];

/* --- Animated spine (the corridor) ----------------------------------------
 * The corridor is THE motif. Instead of a static line we paint it with a
 * line-gradient (requires `lineMetrics` on the source) and animate two things:
 *   1. a draw-in reveal (0 -> 1) when the spine becomes the active layer, and
 *   2. a glow band that travels along it - a sense of walking the route.
 * Reduced-motion users get a clean static line, no animation loop.
 */
const SPINE_LAYER_ID = "corridor-line";
const SPINE_DRAW_MS = 1500; // draw-in duration when the spine activates
const SPINE_PULSE_MS = 3400; // one traversal of the travelling glow
const SPINE_BASE_ON = "rgba(245, 158, 11, 0.92)";
const SPINE_BASE_OFF = "rgba(245, 158, 11, 0.32)";
const SPINE_GLOW_ON = "rgba(255, 228, 160, 1)";
const SPINE_GLOW_OFF = "rgba(245, 158, 11, 0.55)";
const SPINE_CLEAR = "rgba(245, 158, 11, 0)";

/** Build a valid (strictly-ascending stops) line-gradient for the spine. */
function spineGradient(reveal: number, pulse: number, on: boolean): ExpressionSpecification {
  const base = on ? SPINE_BASE_ON : SPINE_BASE_OFF;
  const glow = on ? SPINE_GLOW_ON : SPINE_GLOW_OFF;
  const r = Math.max(0.0008, Math.min(1, reveal));
  const band = 0.06;
  const c = Math.min(r, Math.max(0, pulse) * r); // glow centre, only within the revealed part
  const lo = Math.max(0, c - band);
  const hi = Math.min(r, c + band);
  const raw: Array<[number, string]> = [
    [0, base],
    [lo, base],
    [c, glow],
    [hi, base],
    [r, base],
  ];
  if (r < 1) {
    raw.push([Math.min(1, r + 0.002), SPINE_CLEAR]);
    raw.push([1, SPINE_CLEAR]);
  }
  // Enforce strictly-ascending, in-range stops by skipping any that don't advance.
  const stops: Array<number | string> = [];
  let last = -1;
  const EPS = 0.0006;
  for (const [pos, col] of raw) {
    const x = Math.min(1, Math.max(0, pos));
    if (x > last + EPS) {
      stops.push(x, col);
      last = x;
    }
  }
  if (last < 1 - EPS) stops.push(1, r < 1 ? SPINE_CLEAR : base);
  return ["interpolate", ["linear"], ["line-progress"], ...stops] as unknown as ExpressionSpecification;
}

/** Flat (no pulse) gradient for the initial paint and reduced-motion. */
function spineStatic(on: boolean): ExpressionSpecification {
  const base = on ? SPINE_BASE_ON : SPINE_BASE_OFF;
  return [
    "interpolate",
    ["linear"],
    ["line-progress"],
    0,
    base,
    1,
    base,
  ] as unknown as ExpressionSpecification;
}

const SPINE_GRADIENT_INITIAL = spineStatic(false);

function viewStateFromFocus(focus: Focus) {
  const [longitude, latitude, zoom, pitch, bearing] = focus;
  return { longitude, latitude, zoom, pitch, bearing };
}

function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

function layerConfig(id: string, active: boolean): LayerConfig {
  switch (id) {
    case "corridor":
      // Colour/alpha come from the animated line-gradient (see spineGradient);
      // here we only vary width so the gradient is never clobbered on re-render.
      return {
        id: SPINE_LAYER_ID,
        source: "corridor",
        type: "line",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: {
          "line-width": active ? 5.5 : 4,
          "line-blur": 0.5,
          "line-opacity": 1,
          "line-gradient": SPINE_GRADIENT_INITIAL,
        },
      };
    case "routes":
      return {
        id: "routes-line",
        source: "routes",
        type: "line",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: {
          "line-color": palette.paper,
          "line-width": 2,
          "line-opacity": active ? 0.85 : 0.2,
        },
      };
    case "study_boundary":
      return {
        id: "study_boundary-line",
        source: "study_boundary",
        type: "line",
        paint: {
          "line-color": palette.sky,
          "line-width": 1.4,
          "line-dasharray": [2, 2],
          "line-opacity": active ? 0.6 : 0.18,
        },
      };
    case "wayfinders":
      return {
        id: "wayfinders-circle",
        source: "wayfinders",
        type: "circle",
        paint: {
          "circle-radius": 6,
          "circle-color": palette.amber,
          "circle-stroke-color": palette.ink,
          "circle-stroke-width": 2,
          "circle-opacity": active ? 1 : 0.4,
        },
      };
    case "anchors":
      return {
        id: "anchors-circle",
        source: "anchors",
        type: "circle",
        paint: {
          "circle-radius": 5,
          "circle-color": palette.sky,
          "circle-stroke-color": palette.ink,
          "circle-stroke-width": 1.5,
          "circle-opacity": active ? 0.95 : 0.3,
        },
      };
    default:
      return {
        id: `${id}-line`,
        source: id,
        type: "line",
        paint: { "line-color": palette.muted, "line-width": 1 },
      };
  }
}

type MapStageProps = {
  layers: LayerReference[];
  /** Camera for the active chapter; falls back to a wide default. */
  focus?: Focus;
  /** Layer ids the active chapter emphasises. Empty/undefined = all emphasised. */
  activeLayerIds?: string[];
};

export function MapStage({ layers, focus, activeLayerIds }: MapStageProps) {
  const mapRef = useRef<MapRef>(null);
  const allActive = !activeLayerIds || activeLayerIds.length === 0;
  const focusKey = focus ? focus.join(",") : "";
  const spineActive = allActive || !!activeLayerIds?.includes("corridor");

  useEffect(() => {
    if (!focus) return;
    const map = mapRef.current;
    if (!map) return;
    const [longitude, latitude, zoom, pitch, bearing] = focus;
    // Pad the camera away from the scene card so the focus frames into the visible
    // map area, not behind the card: right on wide screens (card docked right),
    // bottom on mobile (card docked along the bottom).
    const wide = typeof window !== "undefined" && window.innerWidth >= 760;
    const padding = wide
      ? { top: 0, bottom: 0, left: 0, right: Math.min(460, Math.round(window.innerWidth * 0.34)) }
      : { top: 0, left: 0, right: 0, bottom: Math.round((typeof window !== "undefined" ? window.innerHeight : 800) * 0.5) };
    const target = { center: [longitude, latitude] as [number, number], zoom, pitch, bearing, padding };
    if (prefersReducedMotion()) {
      map.jumpTo(target);
    } else {
      map.flyTo({ ...target, duration: motion.slow * 1.9, curve: 1.42, essential: true });
    }
  }, [focus, focusKey]);

  // Animate the spine: draw-in when it activates + a travelling glow band.
  useEffect(() => {
    const map = mapRef.current?.getMap?.();
    if (!map) return;

    const applyStatic = () => {
      if (map.getLayer(SPINE_LAYER_ID)) {
        map.setPaintProperty(SPINE_LAYER_ID, "line-gradient", spineStatic(spineActive));
      }
    };

    if (prefersReducedMotion()) {
      if (map.isStyleLoaded()) applyStatic();
      else map.once("idle", applyStatic);
      return;
    }

    let raf = 0;
    let pulseStart = 0;
    let drawStart: number | null = null;
    const loop = (t: number) => {
      if (map.getLayer(SPINE_LAYER_ID)) {
        if (!pulseStart) pulseStart = t;
        if (drawStart === null) drawStart = t;
        const reveal = spineActive ? Math.min(1, (t - drawStart) / SPINE_DRAW_MS) : 1;
        const pulse = ((t - pulseStart) % SPINE_PULSE_MS) / SPINE_PULSE_MS;
        try {
          map.setPaintProperty(SPINE_LAYER_ID, "line-gradient", spineGradient(reveal, pulse, spineActive));
        } catch {
          // style mid-reload; the next frame will retry
        }
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [spineActive]);

  return (
    <div className="map-stage" role="region" aria-label="Innovation Spine map">
      <Map
        ref={mapRef}
        initialViewState={viewStateFromFocus(focus ?? DEFAULT_FOCUS)}
        mapStyle={BASEMAP_STYLE_URL}
        style={{ position: "absolute", inset: 0 }}
        attributionControl={{ compact: true }}
        onLoad={(event) => {
          event.target.resize();
          // DEV-only handle for camera/projection verification (stripped from prod builds).
          if (import.meta.env.DEV) {
            (window as unknown as { __spineMap?: unknown }).__spineMap = event.target;
          }
        }}
      >
        <NavigationControl position="top-right" showCompass visualizePitch />
        {/* 3D massing under the spine; labels off to keep the journey clean. */}
        <Buildings3D labels={false} />
        {/* The 3D buildings are the anchors now - drop the flat blue anchor dots. */}
        {layers.filter((layer) => layer.id !== "anchors").map((layer) => {
          const active = allActive || activeLayerIds!.includes(layer.id);
          return (
            <Source
              key={layer.id}
              id={layer.id}
              type="geojson"
              data={`/content/${layer.file}`}
              lineMetrics={layer.id === "corridor" ? true : undefined}
            >
              <Layer {...layerConfig(layer.id, active)} />
            </Source>
          );
        })}
        <CrossingImprovement after labels={false} />
      </Map>
    </div>
  );
}
