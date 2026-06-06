/**
 * ExploreMap - the free, interactive 3D map (Step 7, rebuilt).
 *
 * Pan / tilt / zoom the whole evidence base in 3D, toggle every layer the project
 * produces (real OSM building footprints, the gateway pavilion, the improved
 * crossing, wayfinders, the tactical corridor and walking routes), and click any
 * feature for a plain-language popup. Everything comes from the sanitised public
 * GeoJSON - no internal vocabulary leaks through.
 */
import { type ComponentProps, useMemo, useRef, useState } from "react";
import Map, {
  Layer,
  NavigationControl,
  Popup,
  Source,
  type MapLayerMouseEvent,
  type MapRef,
} from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

import { BASEMAP_STYLE_URL, palette } from "../theme/tokens";
import { Buildings3D, CrossingImprovement, WayfinderTotems } from "../map/Buildings3D";
import type { LayerReference } from "../types/content";

type LayerConfig = ComponentProps<typeof Layer>;

// Toggle keys are our own (not raw content ids) because several are composite
// (the 3D buildings layer is one toggle covering buildings + labels, etc.).
type ToggleKey = "buildings" | "wayfinders" | "crossing" | "corridor" | "routes" | "study_boundary";

type Toggle = {
  key: ToggleKey;
  label: string;
  swatch: string;
  defaultOn: boolean;
  /** content layer id this toggle needs present (composite toggles need none). */
  needs?: string;
};

const TOGGLES: Toggle[] = [
  { key: "buildings", label: "B-KQ buildings (3D)", swatch: "#5b9bd5", defaultOn: true },
  { key: "wayfinders", label: "Wayfinders", swatch: palette.amber, defaultOn: true },
  { key: "crossing", label: "Improved crossing", swatch: "#fbbf24", defaultOn: true },
  { key: "corridor", label: "Amber route", swatch: palette.amber, defaultOn: true, needs: "corridor" },
  { key: "routes", label: "Walking routes", swatch: palette.paper, defaultOn: false, needs: "routes" },
  { key: "study_boundary", label: "Study area", swatch: palette.sky, defaultOn: false, needs: "study_boundary" },
];

// Centered between the city-core gateway (west) and the B-KQ cluster + crossing
// (east), tilted so the 3D reads at a glance.
const INITIAL_VIEW = { longitude: -1.8875, latitude: 52.4848, zoom: 13.7, pitch: 50, bearing: 16 };

const CATEGORY_LABEL: Record<string, string> = {
  destination: "B-KQ building",
  start: "City-core start point",
  context: "Local building",
  pavilion: "Gateway pavilion (concept)",
};

const corridorLayer: LayerConfig = {
  id: "expl-corridor",
  type: "line",
  source: "expl-corridor",
  layout: { "line-cap": "round", "line-join": "round" },
  paint: { "line-color": palette.amber, "line-width": 5, "line-opacity": 0.9, "line-blur": 0.3 },
};

const routesLayer: LayerConfig = {
  id: "expl-routes",
  type: "line",
  source: "expl-routes",
  layout: { "line-cap": "round", "line-join": "round" },
  paint: { "line-color": palette.paper, "line-width": 2, "line-opacity": 0.6 },
};

const studyLayer: LayerConfig = {
  id: "expl-study_boundary",
  type: "line",
  source: "expl-study_boundary",
  paint: { "line-color": palette.sky, "line-width": 1.4, "line-dasharray": [2, 2], "line-opacity": 0.5 },
};

type PopupInfo = { lng: number; lat: number; layerId: string; props: Record<string, unknown> };

function row(label: string, value: unknown): { label: string; value: string } | null {
  if (value === undefined || value === null || value === "" || value === false) return null;
  return { label, value: String(value) };
}

function popupFor(layerId: string, p: Record<string, unknown>): { title: string; rows: { label: string; value: string }[] } {
  const keep = (rs: ({ label: string; value: string } | null)[]) =>
    rs.filter((r): r is { label: string; value: string } => r !== null);

  if (layerId === "bkq-buildings") {
    const cat = String(p.category ?? "");
    return {
      title: String(p.name) || CATEGORY_LABEL[cat] || "Building",
      rows: keep([
        row("Type", CATEGORY_LABEL[cat] ?? cat),
        row("Height", p.heightM != null ? `${Math.round(Number(p.heightM))} m` : null),
      ]),
    };
  }
  if (layerId === "wf-totems" || layerId === "wf-markers") {
    return {
      title: `Wayfinder ${p.id ?? ""}`.trim(),
      rows: keep([
        row("Type", p.type),
        row("To", p.onwardDestinations),
        row("Walk time", p.walkTimeMin != null ? `${p.walkTimeMin} min` : null),
        row("Crossing", p.crossingCaution),
      ]),
    };
  }
  if (layerId === "vision-crossing-band") {
    return { title: "Safer crossing", rows: [{ label: "Status", value: "A safer place to cross, for people on foot and bikes (concept)" }] };
  }
  if (layerId === "expl-corridor") {
    return {
      title: "Amber route",
      rows: keep([
        row("Shared routes", p.sharedRoutes),
        row("Length", p.lengthM != null ? `${p.lengthM} m` : null),
        row("Suitability", p.suitability != null ? `${p.suitability}/100` : null),
      ]),
    };
  }
  if (layerId === "expl-routes") {
    return {
      title: String(p.name ?? "Route"),
      rows: keep([
        row("Priority", p.priority),
        row("Easy to follow", p.legibilityScore != null ? `${p.legibilityScore}/100` : null),
      ]),
    };
  }
  return { title: "Feature", rows: [] };
}

export function ExploreMap({ layers }: { layers: LayerReference[] }) {
  const mapRef = useRef<MapRef>(null);
  const [visible, setVisible] = useState<Record<ToggleKey, boolean>>(
    () => Object.fromEntries(TOGGLES.map((t) => [t.key, t.defaultOn])) as Record<ToggleKey, boolean>,
  );
  const [popup, setPopup] = useState<PopupInfo | null>(null);
  const [cursor, setCursor] = useState<"grab" | "pointer">("grab");
  // Layer panel: open on desktop, collapsed on small screens so it doesn't cover the map.
  const [panelOpen, setPanelOpen] = useState<boolean>(() => typeof window === "undefined" || window.innerWidth > 720);

  const present = useMemo(() => new Set(layers.map((l) => l.id)), [layers]);
  const toggles = TOGGLES.filter((t) => !t.needs || present.has(t.needs));
  const fileFor = (id: string) => layers.find((l) => l.id === id)?.file;

  const interactiveLayerIds = useMemo(() => {
    const ids: string[] = [];
    if (visible.buildings) ids.push("bkq-buildings");
    if (visible.wayfinders) ids.push("wf-totems", "wf-markers");
    if (visible.crossing) ids.push("vision-crossing-band");
    if (visible.corridor && present.has("corridor")) ids.push("expl-corridor");
    if (visible.routes && present.has("routes")) ids.push("expl-routes");
    return ids;
  }, [visible, present]);

  const onClick = (event: MapLayerMouseEvent) => {
    // Query the interactive layers ourselves (more reliable than event.features
    // across overlapping 3D layers). When layers overlap (e.g. the corridor line
    // crosses a building footprint), prefer the more intentional target: small
    // markers first, then buildings, then the crossing, then the lines.
    const map = event.target;
    const queryable = interactiveLayerIds.filter((id) => map.getLayer(id));
    const hits = queryable.length ? map.queryRenderedFeatures(event.point, { layers: queryable }) : [];
    const PRIORITY = ["wf-markers", "wf-totems", "bkq-buildings", "vision-crossing-band", "expl-corridor", "expl-routes"];
    const feature = hits
      .slice()
      .sort((a, b) => PRIORITY.indexOf(a.layer.id) - PRIORITY.indexOf(b.layer.id))[0];
    if (!feature) {
      setPopup(null);
      return;
    }
    setPopup({
      lng: event.lngLat.lng,
      lat: event.lngLat.lat,
      layerId: String(feature.layer.id),
      props: (feature.properties ?? {}) as Record<string, unknown>,
    });
  };

  const resetView = () => {
    const map = mapRef.current;
    if (!map) return;
    map.flyTo({
      center: [INITIAL_VIEW.longitude, INITIAL_VIEW.latitude],
      zoom: INITIAL_VIEW.zoom,
      pitch: INITIAL_VIEW.pitch,
      bearing: INITIAL_VIEW.bearing,
      duration: 900,
      essential: true,
    });
  };

  return (
    <div className="explore-map">
      <Map
        ref={mapRef}
        initialViewState={INITIAL_VIEW}
        mapStyle={BASEMAP_STYLE_URL}
        style={{ position: "absolute", inset: 0 }}
        attributionControl={{ compact: true }}
        maxPitch={75}
        interactiveLayerIds={interactiveLayerIds}
        cursor={cursor}
        onMouseEnter={() => setCursor("pointer")}
        onMouseLeave={() => setCursor("grab")}
        onClick={onClick}
        onLoad={(event) => {
          event.target.resize();
          if (import.meta.env.DEV) {
            (window as unknown as { __exploreMap?: unknown }).__exploreMap = event.target;
          }
        }}
      >
        <NavigationControl position="top-right" showCompass visualizePitch />

        {/* Tactical corridor + routes + study area (own sources, toggle by mount). */}
        {visible.corridor && fileFor("corridor") && (
          <Source id="expl-corridor" type="geojson" data={`/content/${fileFor("corridor")}`}>
            <Layer {...corridorLayer} />
          </Source>
        )}
        {visible.routes && fileFor("routes") && (
          <Source id="expl-routes" type="geojson" data={`/content/${fileFor("routes")}`}>
            <Layer {...routesLayer} />
          </Source>
        )}
        {visible.study_boundary && fileFor("study_boundary") && (
          <Source id="expl-study_boundary" type="geojson" data={`/content/${fileFor("study_boundary")}`}>
            <Layer {...studyLayer} />
          </Source>
        )}

        {/* Shared 3D layers. */}
        <Buildings3D visible={visible.buildings} labels />
        <CrossingImprovement after visible={visible.crossing} labels={false} />
        <WayfinderTotems visible={visible.wayfinders} />

        {popup && (
          <Popup
            longitude={popup.lng}
            latitude={popup.lat}
            anchor="bottom"
            offset={14}
            closeOnClick={false}
            onClose={() => setPopup(null)}
            className="explore-popup"
            maxWidth="280px"
          >
            <ExplorePopup layerId={popup.layerId} props={popup.props} />
          </Popup>
        )}
      </Map>

      <div className={`explore-controls ${panelOpen ? "is-open" : "is-collapsed"}`} role="group" aria-label="Map layers">
        <button
          type="button"
          className="explore-controls__toggle"
          aria-expanded={panelOpen}
          onClick={() => setPanelOpen((o) => !o)}
        >
          <span>Layers</span>
          <span className="explore-controls__chevron" aria-hidden="true">
            {panelOpen ? "▾" : "▸"}
          </span>
        </button>
        {panelOpen && (
          <div className="explore-controls__body">
            {toggles.map((t) => (
              <label key={t.key} className="explore-controls__row">
                <input
                  type="checkbox"
                  checked={visible[t.key]}
                  onChange={(e) => {
                    const on = e.target.checked;
                    setVisible((v) => ({ ...v, [t.key]: on }));
                    if (!on) setPopup(null);
                  }}
                />
                <span className="explore-controls__swatch" style={{ background: t.swatch }} aria-hidden="true" />
                {t.label}
              </label>
            ))}
            <button type="button" className="explore-controls__reset" onClick={resetView}>
              Reset view
            </button>
            <p className="explore-controls__hint">Drag to pan · right-drag to tilt · tap a feature for details.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ExplorePopup({ layerId, props }: { layerId: string; props: Record<string, unknown> }) {
  const { title, rows } = popupFor(layerId, props);
  return (
    <div className="explore-popup__body">
      <strong className="explore-popup__title">{title}</strong>
      <dl className="explore-popup__list">
        {rows.map((r) => (
          <div key={r.label} className="explore-popup__pair">
            <dt>{r.label}</dt>
            <dd>{r.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
