# SpineLens AI · The Innovation Spine (Phase 1)

**Reconnecting Birmingham Knowledge Quarter to the city core, proven with open data and shipped as an interactive web experience.**

**▶ Live app: https://spinelens-ai.pages.dev**

SpineLens AI is the Phase 1 layer of *The Innovation Spine*, a submission to the **West Midlands @ UKREiiF 2026 Next-Gen Placemaking & Urban Design Challenge**. It takes the proposal's four £1M "Make It Visible" interventions and turns them from an idea into a **measurable, testable, explainable** case: modelled notebooks-first on free public data, then presented in a production, zero-cost web app.

This repository is the full pipeline, end to end: **research → evidence → sanitised public bundle → web app → deploy.**

---

## 1. The challenge: close in distance, far in perception

Birmingham Knowledge Quarter (B-KQ), home to Aston University, BCU and Millennium Point, sits minutes from the commercial core yet remains on the edge of the city's *psychological* map. The UKREiiF brief frames three barriers:

- **Physical:** arterial roads (James Watt Queensway, Dartmouth Middleway) that are wide, fast and hostile to people on foot.
- **Perceptual:** no legible route tells a pedestrian *"something worth going to is this way."*
- **Social:** the surrounding wards (Nechells, Aston) are among Birmingham's most deprived and most disconnected from opportunity.

**The question this project answers:** *where does the city-to-B-KQ journey become illegible, and which low-cost interventions create the highest route clarity per pound?*

## 2. The proposal: The Innovation Spine

*Three phases. One spine. A city reconnected to its own future.* The challenge asks for three budget levels; this repo is **Phase 1 only**.

| Phase | Budget | Theme | Headline interventions |
|---|---|---|---|
| **Phase 1 (this repo)** | **£1M** | **Make It Visible** | Wayfinder network · tactical (amber) corridor · pedestrian crossing · gateway pavilion |
| Phase 2 | £10M | Make It Usable | Jennens Road boulevard, electric bus routes, redesigned stops |
| Phase 3 | strategic | Make It Investable | Innovation deck, blue-green strategy, smart-city layer |

## 3. Architecture: research to deployment

The project is a three-layer system. Evidence is modelled first; the app only ever *presents* what the evidence proves.

```text
Public open data  (OSM · DfT STATS19/AADF · NaPTAN · OS · HM Land Registry)
      │   acquire, audit and model through evidence gates 0..0E
      ▼
[1] RESEARCH / EVIDENCE      phase1_spinelens_ai/   (Jupyter notebooks 00-14 + tested Python package)
      │   exports one internal artifact: outputs/exports/evidence_pack.json (+ GeoJSON layers)
      ▼
[2] SANITISE / BUILD         web/build_*.py         (strip internal vocabulary, bleed-check, optimise assets)
      │   writes the public contract: web/public/content/spine.json + layers + 3D + concept imagery
      ▼
[3] PRESENTATION             web/                   (Vite + React + MapLibre, 5 views, a11y / perf / mobile)
      │   npm run build  ->  static dist/
      ▼
Cloudflare Pages  (free tier, Git-connected, auto-deploy on push)  ->  https://spinelens-ai.pages.dev
```

**Why split it this way:** the research is reproducible and auditable on its own; the sanitise step guarantees no internal jargon, source IDs or evidence-level language ever reaches the public app (a `--check` bleed-guard fails the build if it does); the app is a static SPA with no backend, so hosting is free and nothing can break at runtime.

### Tech stack
- **Research / modelling (Python 3.11):** Jupyter, `osmnx`, `geopandas`, `shapely`, `networkx`, `pandas`, `numpy`, `matplotlib`; a tested `spinelens` package.
- **Sanitise / build (Python):** `build_content.py` (public bundle + bleed-check), `build_3d_buildings.py`, `build_wayfinder_panels.py`, `build_concepts.py` (`Pillow` image optimisation).
- **Web app:** Vite 6 · React 19 · TypeScript · Tailwind · MapLibre GL (via `react-map-gl`, keyless CARTO basemap) · Framer Motion · Recharts · self-hosted variable fonts (Space Grotesk + Inter).
- **Quality / deploy:** ESLint · Vitest · Playwright headless checks · `npm run verify` · Cloudflare Pages.

### The web app (five views)
**The Walk** (scrollytelling along the route, camera flies each chapter) · **Explore** (interactive 3D map, layer toggles, click-for-detail) · **The Evidence** (animated charts) · **The Vision** (cinematic 3D with before/after crossing and a steppable wayfinder walk-through) · **Concepts** (concept-art gallery + lightbox). Plus a first-load intro, WCAG 2.2 AA accessibility, code-split performance, and a mobile-first responsive pass.

## 4. The approach: evidence gates

Not a generic dashboard, a **transparent computational urban-design toolkit**. Work moves through **evidence gates** under a forensic protocol, and every output is tagged on an evidence ladder:

`0` not tested · `1` source reachable · `2` raw acquired · `3` quality audited · `4` cross-checked · `5` field validated.

Funding-facing claims need Level 4 to 5. **Nothing here is presented as funding-grade.** Free open data, transparent algorithms, local compute, zero paid APIs.

## 5. The evidence (each Phase 1 intervention, tested)

- **Route legibility (Level 3):** a transparent Route Legibility Index over the audited pedestrian network ranks the inbound approaches. Colmore Row reads most legible, Snow Hill least, a ranking that holds under 4,000 randomised weightings (sensitivity-tested, not cherry-picked).
- **Tactical corridor (Level 3):** Colmore Row and New Street merge into a shared trunk near the gateway. The city-core spine is severance-free (nearest major road 71.5 m), so the amber corridor can be a near-continuous low-cost surface; the road severance is concentrated at one place, the crossing.
- **The crossing (Level 3, cross-checked):** Dartmouth Middleway carries 35,141 vehicles/day but only 43 cyclists/day, with 20 injury collisions (5 serious) within 150 m over 2020-2024 (DfT STATS19). A multi-lane crossing like this warrants a signalised fix; a multi-criteria appraisal ranks the options (tactical enhancement now, full upgrade as later-phase highways capital).
- **Wayfinders (Level 3):** a budget-aware greedy maximal-coverage optimiser places 12 wayfinders (8 interactive totems + 4 low-cost markers) at the junctions where people can go wrong, in a tiered system (pavilion hub · interactive totems · low-cost markers + QR). The city-core approaches were optimised first for maximum decision-point coverage, then the network was extended across the Dartmouth crossing into the B-KQ cluster. Content is generated from evidence (routes, crossing caution, real NaPTAN bus stops), updateable (static/dynamic split), and pedestrian-first. The Nechells approach (no pavilion) gets hub-lite content so it is not left short.
- **Gateway pavilion (Level 3, ownership screened):** a wooden, reversible (demountable) civic information hub at Ryder Street. Well-justified by demand and route convergence; the reversible form de-risks helipad-safeguarding and land constraints. HM Land Registry data pins it to one registered parcel.
- **Budget (quantities Level 3; costs indicative):** with a reversible pavilion and a phased crossing, the everything-in package fits £1,000,000 at the central estimate (~£693k net of civic-partner sponsorship, ~£307k headroom). Costs are indicative pending a quantity-surveyor costing.

## 6. What's proven vs assumed (honesty)

- **Real, verifiable evidence:** traffic, collision, bus-stop, network and parcel data from authoritative sources (DfT, OS, NaPTAN, HM Land Registry, OSM) with provenance, reproducible by re-running the notebooks.
- **Model outputs:** the legibility index, corridor, placement and suitability scores are transparent, reproducible *hypotheses* on documented weights and provisional anchors.
- **Assumptions (not evidence):** all £ figures are Level-1 indicative pending a QS, as are the option/criterion scores.
- A **validation register** lists every gap with its owner and next step. The frontier is fieldwork, costing and consents: briefed, not yet done.

## 7. Data sources (all free / open)

OpenStreetMap (OSMnx) · OS Open Greenspace · DfT Road Traffic (AADF) · DfT STATS19 collisions · NaPTAN bus stops · HM Land Registry INSPIRE parcels · data.police.uk (context only).

## 8. Repository guide

```text
phase1_spinelens_ai/         # the research / evidence layer
├── notebooks/ 00-14         # the analysis in order (start at 05 for a reading guide)
│   00-04  foundation + data acquisition & quality audit (Gates 0..0B)
│   05     context & reading guide
│   06     route legibility baseline + sensitivity
│   07     wayfinder placement (clarity per pound)
│   08     crossing evidence + options appraisal (Gate 0C)
│   09     tactical corridor synthesis
│   10     pavilion suitability + validation register
│   11     digital wayfinder content + tiered UX + sponsorship
│   12     budget pack (everything in, vs £1M)
│   13     evidence-pack export (web-app-ready)
│   14     authoritative cross-check + ownership screen (Gate 0E)
├── src/spinelens/           # reusable, tested package (spatial, metrics, models, io)
└── tests/                   # unit tests

web/                         # the sanitise/build + presentation layers
├── build_content.py         # evidence_pack.json -> public spine.json + layers (+ bleed-check)
├── build_3d_buildings.py    # 3D building / crossing / wayfinder GeoJSON
├── build_wayfinder_panels.py# wayfinder panel content
├── build_concepts.py        # concept art -> optimised WebP + OG share card
├── public/content/          # the committed public bundle the app reads
└── src/                     # Vite + React + MapLibre app (five views)
```

## 9. Run it

**Research / evidence layer** (from repo root):
```bash
python -m venv .bkqproj
.\.bkqproj\Scripts\Activate.ps1                       # PowerShell (use source .../activate on macOS/Linux)
python -m pip install -r requirements-lock-py311.txt  # verified Python 3.11 lock
python -m pip install -e .                            # install the local spinelens package
python -m pytest                                      # run the tests
# notebooks run on the bkqproj kernel: jupyter nbconvert --to notebook --execute notebooks/<nb>.ipynb
```

**Web app** (from `web/`):
```bash
npm install
npm run dev        # local dev server (http://127.0.0.1:5173)
npm run verify     # content-check (bleed-guard) + lint + tests + production build
npm run build      # static production build into web/dist
```
Regenerate the public bundle only when the evidence changes: `python build_content.py --check` (and the other `build_*.py` scripts as needed). See `web/README.md` for full build and deploy detail.

## 10. Deploy (zero ongoing cost)

Static SPA, no backend. `npm run build` emits `web/dist`, deployed on **Cloudflare Pages** (Git-connected, auto-deploys on push; root directory `web`, build `npm run build`, output `dist`). `public/_redirects`, `public/_headers` and `web/.node-version` ship the SPA fallback, asset caching and Node pin. Full runbook in `web/README.md`.

## 11. Roadmap

Phase 1 is complete, verified and deployed. Phases 2 (£10M "Make It Usable") and 3 (strategic "Make It Investable") reuse this same research-to-deployment architecture, keeping the SpineLens AI / Innovation Spine branding. The remaining Phase 1 frontier is field validation, QS costing and consents (briefed in the validation register).

## 12. Status & licence

An evidence-backed Phase 1 case, honest about its evidence levels, shipped as a live web experience. No licence is set yet; until one is added the code is **all rights reserved** and not licensed for reuse.
