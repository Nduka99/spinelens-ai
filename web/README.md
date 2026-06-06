# SpineLens AI · Web App (Phase 1)

The **presentation layer** of *The Innovation Spine, Phase 1*. A static, zero-backend single-page app (Vite + React + TypeScript + MapLibre GL) that presents the Phase 1 evidence as an interactive experience.

It reads only the **sanitised public bundle** in `public/content/` (generated from the research layer in `../phase1_spinelens_ai/`), so no internal data, source IDs or evidence-level language ever ships to the browser. For the full research-to-deployment architecture, see the [root README](../README.md).

**▶ Live app: https://spinelens-ai.pages.dev**

## Views
- **The Walk** - scrollytelling along the route; the camera flies to each chapter.
- **Explore** - interactive 3D map: toggle layers (buildings, wayfinders, crossing, amber route), click any feature for plain-language detail.
- **The Evidence** - animated charts (route legibility, wayfinding uplift, the barrier, budget vs £1M).
- **The Vision** - cinematic 3D: before/after crossing and a steppable wayfinder walk-through.
- **Concepts** - concept-art gallery with an accessible lightbox.

Plus a first-load intro, WCAG 2.2 AA accessibility, code-split performance, and a mobile-first responsive pass.

## Stack
Vite 6 · React 19 · TypeScript (strict) · Tailwind · MapLibre GL via `react-map-gl/maplibre` (keyless CARTO dark-matter basemap) · Framer Motion · Recharts · self-hosted variable fonts (`@fontsource-variable/space-grotesk` + `inter`). Tooling: ESLint · Vitest · Playwright.

## Develop, verify, build

From `web/`:

```bash
npm install        # one-time
npm run dev        # local dev server (http://127.0.0.1:5173)
npm run verify     # content-check (bleed-guard) + lint + tests + production build
npm run build      # production build into ./dist
npm run preview    # serve the built ./dist locally
```

## Content / asset build scripts (Python)

These regenerate the sanitised public data and assets the app reads. Run them only when the underlying evidence changes; the generated files in `public/` are committed.

```bash
python build_content.py --check     # public spine.json + map layers (fails on internal-term bleed)
python build_3d_buildings.py        # 3D building / crossing / wayfinder GeoJSON (needs osmnx + geopandas)
python build_wayfinder_panels.py    # wayfinder panel content
python build_concepts.py            # optimise ../phase1concepts/*.png -> public/concepts/*.webp + og.jpg
```

Source artwork lives in `../phase1concepts/` (kept local); `build_concepts.py` writes the web-optimised WebP plus the social share card to `public/`.

## Deploy (zero ongoing cost)

Static SPA: `npm run build` emits `./dist` with no runtime backend. `public/_redirects` (SPA fallback), `public/_headers` (asset caching) and `.node-version` (Node 20 pin) are picked up automatically.

**Cloudflare Pages (recommended, Git-connected auto-deploy):**
1. Cloudflare dashboard → Workers & Pages → Create → open the **Pages** tab → Connect to Git → pick the repo.
   - *Gotcha:* the "Import a repository" flow under **Workers** deploys a Worker, not a static site (it shows a "Deploy command: `npx wrangler deploy`" field). Use the **Pages** tab; the right screen asks for a **Build output directory** and has no deploy command.
2. Settings: Production branch `main` · Framework preset `None` (or `Vite`) · **Root directory `web`** · Build command `npm run build` · Build output directory `dist`.
3. Save and Deploy. Every push to `main` then auto-redeploys; branches get preview URLs.

**Vercel / Netlify:** also free. Vercel uses the committed `vercel.json` rewrite for the SPA fallback (root directory `web`, output `dist`). Netlify: base `web`, publish `web/dist`.

After the first deploy, set the **absolute** `og:image`, `og:url` and `<link rel="canonical">` in `index.html` to `https://<your-domain>/…` so LinkedIn renders the share card.

## Structure

```text
web/
├── build_*.py          # sanitise + asset generation (see above)
├── public/content/     # the committed public bundle the app reads
├── src/
│   ├── app/            # shell, intro, view switch, branding
│   ├── walk/ explore/ evidence/ vision/ concepts/   # the five views
│   ├── map/            # MapLibre stage, 3D layers, camera
│   ├── components/ lib/ theme/                       # shared UI, hooks, design tokens
│   └── styles.css
├── _redirects · _headers · vercel.json · .node-version   # deploy config
└── README.md
```
