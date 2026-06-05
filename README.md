# The Innovation Spine — Phase 1 · SpineSense AI

**Reconnecting Birmingham Knowledge Quarter to the city core — proven with open data.**

SpineSense AI is the evidence and analysis layer behind *The Innovation Spine*, a submission to
the **West Midlands @ UKREiiF 2026 Next-Gen Placemaking & Urban Design Challenge**. It turns the
proposal's four Phase 1 interventions from an idea into a **measurable, testable, explainable**
case — built notebooks-first on free public data, with every claim carrying its evidence level.

> This README is a guide to the work so far: the problem, the method, and the evidence-backed
> Phase 1 solution. It is a work in progress; see **"What's proven vs assumed"** below.

---

## 1. The challenge — *Close in distance. Far in perception.*

Birmingham Knowledge Quarter (B-KQ) — home to Aston University, BCU and Millennium Point — sits
minutes from the commercial core, yet remains on the edge of the city's *psychological* map. The
UKREiiF brief frames three barriers:

- **Physical** — arterial roads (James Watt Queensway, **Dartmouth Middleway**) that are wide,
  fast and hostile to people on foot.
- **Perceptual** — no legible route tells a pedestrian *"something worth going to is this way."*
- **Social** — the surrounding wards (Nechells, Aston) are among Birmingham's most deprived and
  most disconnected from opportunity.

**The question this project answers:**

> *Where does the city-to-B-KQ journey become illegible, and which low-cost interventions create
> the highest route clarity per pound?*

## 2. The proposal — The Innovation Spine

*Three phases. One spine. A city reconnected to its own future.*

| Phase | Theme | Headline |
|---|---|---|
| **Phase 1 — £1,000,000** | **Make It Visible** | Wayfinder Network · Tactical Corridor · Pedestrian Crossing · Gateway Pavilion |
| Phase 2 — £10,000,000 | Make It Usable | Jennens Road boulevard, electric bus routes, redesigned stops |
| Phase 3 — strategic | Make It Investable | Innovation deck, blue-green strategy, smart-city layer |

This repository covers **Phase 1 only** — *"the first million proves the route."*

## 3. The approach

Not a generic dashboard — a **transparent computational urban-design toolkit**. Work moves
slowly through **evidence gates** under a forensic protocol, and every output is tagged on an
evidence ladder so a funder can see what is proven:

`0` not tested · `1` source reachable · `2` raw acquired · `3` quality audited · `4` cross-checked · `5` field validated.

Funding-facing claims need Level 4–5. **Nothing here is presented as funding-grade.** Built on
free open data, transparent algorithms, and local compute — zero paid APIs.

## 4. The journey, beginning to end (evidence-backed)

Each Phase 1 intervention was tested against real data:

**🧭 Route legibility — *where does it break down?*** (Level 3)
A transparent Route Legibility Index over the audited pedestrian network ranks the five inbound
approaches. **Colmore Row** reads as the most legible, **Snow Hill** the least — a ranking that
**holds up under 4,000 randomised weightings** (sensitivity-tested, not cherry-picked).

**🟧 Tactical corridor — *one spine or many?*** (Level 3)
Colmore Row and New Street **merge into a shared trunk** approaching the gateway — spurs feeding
one spine, not parallel corridors. Crucially, the city-core spine is **severance-free** (nearest
major road 71.5 m): the amber corridor can be a near-continuous, low-cost surface. The road
severance is concentrated at one place — the crossing.

**🚦 The crossing — *the barrier, evidenced*** (Level 3, cross-checked)
The Dartmouth Middleway carries **35,141 vehicles/day but only 43 cyclists/day**, with **20
injury collisions (5 serious) within 150 m over 2020–2024** (DfT STATS19). A multi-lane crossing
like this fails the zebra test — a **signalised crossing is warranted**. A multi-criteria
appraisal ranks the options; a Phase-1 *tactical enhancement* now, with a full upgrade as
later-phase highways capital.

**📍 Wayfinders — *clarity per pound*** (Level 3)
A budget-aware optimiser places **7 wayfinders covering ~92% of decision-point demand for ~£42k**,
in a **tiered** system (pavilion hub · interactive totems · low-cost markers + QR). Content is
**generated from evidence** (routes, the crossing caution, **real NaPTAN bus stops**), is
**updateable** (static/dynamic split), and is pedestrian-first. The **Nechells** approach — which
has no pavilion — gets hub-lite content on its wayfinders so it isn't left short.

**🏛️ Gateway pavilion — *a public information hub*** (Level 3, ownership screened)
The Ryder Street gateway is proposed as a **wooden, reversible (demountable) civic pavilion** —
a public, B-KQ-wide information hub where arrivals choose their destination, then move on via
the Aston green park. It's well-justified by demand and route convergence; the reversible form
**de-risks** the helipad-safeguarding and land-ownership constraints. HM Land Registry data pins
it to **one registered parcel** — turning ownership from "unknown" into "buy one title."

**💷 Budget — *everything in, within £1M*** (quantities Level 3; costs indicative)
With a reversible pavilion and a phased crossing, the **everything-in package fits £1,000,000 at
the central estimate (~£693k net of civic-partner sponsorship, ~£307k headroom)**. Costs are
**indicative pending a quantity-surveyor costing.**

## 5. What's proven vs assumed (honesty)

- **Real, verifiable evidence:** the traffic, collision, bus-stop, network and parcel data are
  acquired from authoritative sources (DfT, OS, NaPTAN, HM Land Registry, OSM) with checksums and
  provenance — reproducible by re-running the notebooks.
- **Model outputs:** the legibility index, corridor, placement and suitability scores are
  transparent, reproducible *hypotheses* built on **provisional anchors** and documented weights.
- **Assumptions (not evidence):** **all £ figures are Level-1 indicative** pending a QS. So are
  the option/criterion scores.
- A **validation register** lists every gap with its owner and next step. The remaining frontier
  is fieldwork, costing and consents — briefed, not yet done.

## 6. Data sources (all free / open)

OpenStreetMap (OSMnx) · OS Open Greenspace · **DfT Road Traffic (AADF)** · **DfT STATS19**
collisions · **NaPTAN** bus stops · **HM Land Registry INSPIRE** parcels · data.police.uk
(context only).

## 7. Repository guide

```text
phase1_spinelens_ai/
├── notebooks/        # the analysis, in order (start at 05 for a reading guide)
│   ├── 00–04  foundation + data acquisition & quality audit (Gates 0–0B)
│   ├── 05     context & reading guide
│   ├── 06     route legibility baseline + sensitivity
│   ├── 07     wayfinder placement (clarity per pound)
│   ├── 08     crossing evidence + options appraisal (Gate 0C)
│   ├── 09     tactical corridor synthesis
│   ├── 10     pavilion suitability + validation register
│   ├── 11     digital wayfinder content + tiered UX + sponsorship
│   ├── 12     budget pack (everything in, vs £1M)
│   ├── 13     evidence-pack export (web-app-ready)
│   └── 14     authoritative cross-check + ownership screen (Gate 0E)
├── src/spinelens/    # reusable, tested package (spatial, metrics, models, io)
└── tests/            # 80 tests
```

### Run it
```powershell
python -m venv .bkqproj
.\.bkqproj\Scripts\Activate.ps1
python -m pip install -r requirements-lock-py311.txt   # verified Python 3.11.9 lock
python -m pip install -e .                              # install local spinelens package
python -m pytest                                       # 80 tests
```
Notebooks run on the `bkqproj` kernel; execute with `jupyter nbconvert --to notebook --execute`.

## 8. Roadmap

- **Next:** the production-grade, zero-runtime-cost presentation web app described in
  `webapp_implementation_plan.md`. The app will be static Vite/React, fed by a sanitized public
  bundle generated from `evidence_pack.json` + GeoJSON layers, and tested locally for UX,
  accessibility and performance before deployment.
- **Then:** field validation, QS costing and consents (briefed in the validation register), and
  Phases 2–3.

## 9. Status & licence

Work in progress — an evidence-backed Phase 1 case, honest about its evidence levels. No licence
is set yet; until one is added the code is **all rights reserved** and not licensed for reuse.
