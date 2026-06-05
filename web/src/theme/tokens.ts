/**
 * Design tokens for the Innovation Spine experience.
 * Single source of truth for the brand palette, motion and map styling, so the
 * whole app re-themes from one file. Mirrors the CSS variables in styles.css.
 */

export const palette = {
  ink: "#0f172a", // deep navy base
  panel: "#111827",
  paper: "#f8fafc", // text on dark
  muted: "#94a3b8",
  amber: "#f59e0b", // the spine
  timber: "#c8a165", // pavilion warmth
  civic: "#10b981", // connection / go
  sky: "#38bdf8",
  rose: "#fb7185",
} as const;

export const confidenceColor: Record<string, string> = {
  verified: palette.civic,
  modelled: palette.sky,
  estimate: palette.amber,
};

export const motion = {
  // durations (ms) and easings, shared by Framer Motion + map flyTo
  fast: 220,
  base: 480,
  slow: 900,
  ease: [0.22, 0.61, 0.36, 1] as [number, number, number, number],
} as const;

/** Free, keyless dark basemap style for MapLibre (used from Step 1). */
export const BASEMAP_STYLE_URL =
  "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";
