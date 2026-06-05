/**
 * VisionMap - the 3D "true experience" (Step 8).
 *
 * Real OSM building footprints extruded to height (named B-KQ buildings highlighted
 * + labelled, city-core start points, B-KQ context fabric), the proposed pavilion,
 * a before/after Toucan crossing, toggleable 3D wayfinder totems you can step through
 * one by one, and the amber spine - under a cinematic tilted camera.
 */
import { type ComponentProps, useEffect, useRef, useState } from "react";
import Map, { Layer, NavigationControl, Source, type MapRef } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

import { BASEMAP_STYLE_URL, motion, palette } from "../theme/tokens";
import { Buildings3D, CrossingImprovement, WayfinderTotems } from "../map/Buildings3D";
import { WayfinderPanel, type WfPanel } from "./WayfinderPanel";
import type { LayerReference } from "../types/content";

type LayerConfig = ComponentProps<typeof Layer>;

const VIEWS = {
  overview: { center: [-1.889, 52.4842] as [number, number], zoom: 14.1, pitch: 55, bearing: 18 },
  gateway: { center: [-1.89227, 52.48422] as [number, number], zoom: 18.4, pitch: 56, bearing: 28 },
  crossing: { center: [-1.883, 52.48622] as [number, number], zoom: 18.1, pitch: 62, bearing: 50 },
  cluster: { center: [-1.8858, 52.484] as [number, number], zoom: 15.4, pitch: 60, bearing: 22 },
} as const;
type ViewKey = keyof typeof VIEWS;
const VIEW_LABEL: Record<ViewKey, string> = {
  overview: "Overview",
  gateway: "Gateway",
  crossing: "Crossing",
  cluster: "B-KQ cluster",
};

type WfItem = {
  id: string;
  lon: number;
  lat: number;
  type: string;
  role: string;
  walkTimeMin: number | null;
  onward: string;
  caution: string;
};

const corridorLayer: LayerConfig = {
  id: "vision-corridor",
  type: "line",
  source: "corridor",
  layout: { "line-cap": "round", "line-join": "round" },
  paint: { "line-color": palette.amber, "line-width": 5, "line-blur": 0.4, "line-opacity": 0.95 },
};

function reduce(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

export function VisionMap({ layers }: { layers: LayerReference[] }) {
  const mapRef = useRef<MapRef>(null);
  const [view, setView] = useState<ViewKey>("overview");
  const [crossingAfter, setCrossingAfter] = useState(true);
  const [showWf, setShowWf] = useState(false);
  const [wfList, setWfList] = useState<WfItem[]>([]);
  const [wfIndex, setWfIndex] = useState(-1);
  const [panels, setPanels] = useState<Record<string, WfPanel>>({});
  const corridor = layers.find((l) => l.id === "corridor");
  const activeWf = wfIndex >= 0 ? wfList[wfIndex] : null;
  const activePanel = activeWf ? panels[activeWf.id] : null;

  useEffect(() => {
    fetch("/content/layers/wayfinder_totems.geojson")
      .then((r) => r.json())
      .then((d: { features: { properties: Record<string, unknown> }[] }) => {
        const items: WfItem[] = d.features.map((f) => ({
          id: String(f.properties.id),
          lon: Number(f.properties.lon),
          lat: Number(f.properties.lat),
          type: String(f.properties.type ?? ""),
          role: String(f.properties.role ?? ""),
          walkTimeMin: f.properties.walkTimeMin == null ? null : Number(f.properties.walkTimeMin),
          onward: String(f.properties.onwardDestinations ?? ""),
          caution: String(f.properties.crossingCaution ?? ""),
        }));
        items.sort((a, b) => Number(a.id.replace(/\D/g, "")) - Number(b.id.replace(/\D/g, "")));
        setWfList(items);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetch("/content/wayfinder_panels.json")
      .then((r) => r.json())
      .then((d: { panels: Record<string, WfPanel> }) => setPanels(d.panels ?? {}))
      .catch(() => {});
  }, []);

  // When the wayfinder panel is visible (bottom-centre), reserve that space so the
  // camera centres its target ABOVE the card instead of behind it. We size the
  // reserve from the panel VARIANT (rich Nechells cards are taller than light
  // city-core ones) rather than measuring the DOM, which would read the outgoing
  // card mid-transition. Padding is sticky in MapLibre, so we always pass it.
  function cameraPadding(wfId?: string) {
    if (!showWf || typeof window === "undefined") return { top: 0, right: 0, bottom: 0, left: 0 };
    // Wide screens: card is docked right, so reserve horizontal space and centre
    // the wayfinder in the open left area (comfortable vertical framing).
    if (window.innerWidth > 720) {
      return { top: 0, left: 0, bottom: 0, right: 392 };
    }
    // Narrow screens: card sits across the bottom, so push the target upward.
    const variant = panels[wfId ?? activeWf?.id ?? ""]?.variant;
    const frac = variant === "rich" ? 0.62 : 0.46;
    return { top: 0, right: 0, left: 0, bottom: Math.round(window.innerHeight * frac) };
  }

  function fly(
    target: { center: [number, number]; zoom: number; pitch: number; bearing: number },
    wfId?: string,
  ) {
    const map = mapRef.current;
    if (!map) return;
    const opts = { ...target, padding: cameraPadding(wfId) };
    if (reduce()) map.jumpTo(opts);
    else map.flyTo({ ...opts, duration: motion.slow * 2.0, curve: 1.5, essential: true });
  }

  useEffect(() => {
    fly(VIEWS[view]);
  }, [view]);

  function stepWf(delta: number) {
    if (wfList.length === 0) return;
    const i = wfIndex < 0 ? 0 : (wfIndex + delta + wfList.length) % wfList.length;
    setWfIndex(i);
    const w = wfList[i];
    fly({ center: [w.lon, w.lat], zoom: 18.2, pitch: 58, bearing: 32 }, w.id);
  }

  function toggleWf() {
    if (showWf) {
      setShowWf(false);
      setWfIndex(-1);
    } else {
      // Reveal all totems first (at the current view); stepping then flies one-by-one.
      setShowWf(true);
      setWfIndex(wfList.length ? 0 : -1);
    }
  }

  return (
    <div className="vision-map">
      <Map
        ref={mapRef}
        initialViewState={{
          longitude: VIEWS.overview.center[0],
          latitude: VIEWS.overview.center[1],
          zoom: VIEWS.overview.zoom,
          pitch: VIEWS.overview.pitch,
          bearing: VIEWS.overview.bearing,
        }}
        mapStyle={BASEMAP_STYLE_URL}
        style={{ position: "absolute", inset: 0 }}
        attributionControl={{ compact: true }}
        maxPitch={75}
        onLoad={(event) => {
          event.target.resize();
          if (import.meta.env.DEV) {
            (window as unknown as { __visionMap?: unknown }).__visionMap = event.target;
          }
        }}
      >
        <NavigationControl position="top-right" showCompass visualizePitch />
        <Buildings3D labels />
        {corridor && (
          <Source id="corridor" type="geojson" data={`/content/${corridor.file}`}>
            <Layer {...corridorLayer} />
          </Source>
        )}
        <CrossingImprovement after={crossingAfter} labels />
        <WayfinderTotems visible={showWf} activeId={activeWf?.id ?? null} />
      </Map>

      <div className="vision-controls">
        <div className="vision-controls__group" role="group" aria-label="Camera view">
          {(Object.keys(VIEWS) as ViewKey[]).map((key) => (
            <button key={key} type="button" className={view === key ? "is-active" : ""} onClick={() => setView(key)}>
              {VIEW_LABEL[key]}
            </button>
          ))}
        </div>
        <div className="vision-controls__toggle">
          <span className="vision-controls__toggle-label">Crossing</span>
          <button type="button" className={!crossingAfter ? "is-active" : ""} onClick={() => { setCrossingAfter(false); setView("crossing"); }}>
            Before
          </button>
          <button type="button" className={crossingAfter ? "is-active" : ""} onClick={() => { setCrossingAfter(true); setView("crossing"); }}>
            After
          </button>
        </div>
        <div className="vision-controls__toggle">
          <span className="vision-controls__toggle-label">Wayfinders</span>
          <button type="button" className={showWf ? "is-active" : ""} onClick={toggleWf}>
            {showWf ? "On" : "Off"}
          </button>
          {showWf && wfList.length > 0 && (
            <>
              <button type="button" onClick={() => stepWf(-1)} aria-label="Previous wayfinder">◀</button>
              <span className="vision-controls__count">{wfIndex + 1}/{wfList.length}</span>
              <button type="button" onClick={() => stepWf(1)} aria-label="Next wayfinder">▶</button>
            </>
          )}
        </div>
      </div>

      {showWf && activePanel && <WayfinderPanel panel={activePanel} />}

      <p className="vision-caption">
        Built from real building outlines. The pavilion, safer crossing and wayfinders are concept
        impressions.
      </p>
    </div>
  );
}
