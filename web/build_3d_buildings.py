"""Generate the 3D layers for the webapp Vision view + Walk (Step 8).

Precise selection (per project direction):
- City core: ONLY the buildings constituting each start point (full station complexes).
- B-KQ: all named B-KQ buildings (highlighted + labelled, ALL footprint parts) PLUS
  the entrance-to-B-KQ and cluster fabric as low neutral context. No city-core noise.
- Pavilion: organic deck + floating canopy, sited on the Ryder St grass island.
- Improved crossing: a safer signal-controlled crossing for people on foot and bikes
  on the real Dartmouth Middleway / Jennens Road junction - a crossing band + signal heads,
  coloured before/after by the renderer.

Run:  python build_3d_buildings.py        (needs osmnx + geopandas + shapely)
Footprints/road geometry (c) OpenStreetMap contributors, ODbL.
"""

from __future__ import annotations

import json
import math
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.geometry import LineString, Point, mapping, shape
from shapely.ops import nearest_points

ROOT = Path(__file__).resolve().parent
LAYERS = ROOT / "public" / "content" / "layers"
OUT_BUILDINGS = LAYERS / "bkq_buildings_3d.geojson"
OUT_CROSSING = LAYERS / "crossing_improvement.geojson"
OUT_TOTEMS = LAYERS / "wayfinder_totems.geojson"
WAYFINDERS_IN = LAYERS / "wayfinders.geojson"

CENTER = (52.4842, -1.8905)
DIST = 1100

DESTINATIONS = {
    "Aston University - Main Building": "Aston University",
    "Aston Business School / Conference Aston": "Aston Business School",
    "Millennium Point": "Millennium Point",
    "STEAMhouse": "STEAMhouse",
    "Curzon Building": "BCU - Curzon Building",
    "The Parkside Building": "BCU - Parkside",
    "Joseph Priestley Building": "BCU - Joseph Priestley",
    "The Royal Birmingham Conservatoire": "Royal Birmingham Conservatoire",
    "Faraday Wharf": "Innovation Birmingham - Faraday Wharf",
    "iCentrum": "iCentrum",
    "University Locks": "University Locks",
    "One Eastside": "One Eastside",
}
ORIGINS = [
    {"name": "New Street Station", "at": (52.4778, -1.8988), "mode": "one"},
    {"name": "Moor Street Station", "at": (52.4791, -1.8926), "mode": "complex", "radius": 60, "max_area": 9000},
    {"name": "Snow Hill Station", "at": (52.483741, -1.898833), "mode": "cluster", "radius": 60},
    {"name": "Colmore Row", "at": (52.4810, -1.9000), "mode": "one"},
]
PAVILION = (52.48422, -1.89227)  # Ryder St grass island centroid (designated land)
GATEWAY_ANCHOR = (52.484042, -1.892412)
JUNCTION = (52.48622, -1.88300)  # Dartmouth Middleway x Jennens Road

HEIGHT_DEST, HEIGHT_START, HEIGHT_CONTEXT = 22.0, 16.0, 11.0
CONTEXT_MAX_H, CONTEXT_BUFFER_M, CONTEXT_CAP = 15.0, 140, 150
MLAT = 1.0 / 111_320.0


def mlon(lat: float) -> float:
    return 1.0 / (111_320.0 * math.cos(math.radians(lat)))


def parse_height(row, default: float) -> float:
    for key, scale in (("height", 1.0), ("building:levels", 3.2)):
        raw = row.get(key)
        try:
            if raw is not None and str(raw).strip() not in ("", "nan"):
                return round(float(str(raw).split(";")[0].split()[0]) * scale, 1)
        except (ValueError, TypeError):
            continue
    return default


def ellipse(lat, lon, a_m, b_m, rot_deg, n=22):
    r = math.radians(rot_deg)
    ml = mlon(lat)
    ring = []
    for i in range(n + 1):
        th = 2 * math.pi * i / n
        ex, ey = a_m * math.cos(th), b_m * math.sin(th)
        rx = ex * math.cos(r) - ey * math.sin(r)
        ry = ex * math.sin(r) + ey * math.cos(r)
        ring.append([lon + rx * ml, lat + ry * MLAT])
    return ring


def square(lat, lon, half_m):
    ml = mlon(lat)
    return [[lon - half_m * ml, lat - half_m * MLAT], [lon + half_m * ml, lat - half_m * MLAT],
            [lon + half_m * ml, lat + half_m * MLAT], [lon - half_m * ml, lat + half_m * MLAT],
            [lon - half_m * ml, lat - half_m * MLAT]]


def rot_rect(lat, lon, along_m, across_m, road_brg_deg):
    ml = mlon(lat)
    ar = math.radians(road_brg_deg)
    pr = ar + math.pi / 2
    ring = []
    for a, c in [(-along_m / 2, -across_m / 2), (along_m / 2, -across_m / 2),
                 (along_m / 2, across_m / 2), (-along_m / 2, across_m / 2), (-along_m / 2, -across_m / 2)]:
        dlat = (math.cos(ar) * a + math.cos(pr) * c) * MLAT
        dlon = (math.sin(ar) * a + math.sin(pr) * c) * ml
        ring.append([lon + dlon, lat + dlat])
    return ring


def main() -> int:
    fetch = getattr(ox, "features_from_point", None) or ox.geometries_from_point
    print("fetching OSM buildings...")
    gdf = fetch(CENTER, tags={"building": True}, dist=DIST)
    gdf = gdf[gdf.geometry.apply(lambda g: g is not None and g.geom_type in ("Polygon", "MultiPolygon"))].reset_index(drop=True)
    proj = gdf.to_crs(27700)
    names = gdf["name"] if "name" in gdf.columns else pd.Series([None] * len(gdf))
    print(f"  {len(gdf)} building polygons")

    # Wayfinder points: keep a small clear radius so buildings don't block their 3D markers.
    wf_geo = json.loads(WAYFINDERS_IN.read_text(encoding="utf-8"))
    wf_buf = (
        gpd.GeoSeries([Point(f["geometry"]["coordinates"]) for f in wf_geo["features"]], crs=4326)
        .to_crs(27700)
        .buffer(18)
        .union_all()
    )

    used: set[int] = set()
    features: list[dict] = []

    def add(geom, category, name, height, base=0.0):
        features.append({
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {"category": category, "name": name,
                           "heightM": round(float(height), 1), "baseM": round(float(base), 1)},
        })

    # --- Destinations: ALL footprint parts; label the largest part only ---
    for osm_name, public in DESTINATIONS.items():
        match = gdf[names == osm_name]
        if len(match) == 0:
            print(f"  ! not found: {osm_name}")
            continue
        primary = proj.loc[match.index].geometry.area.idxmax()
        for idx in match.index:
            used.add(idx)
            add(gdf.loc[idx].geometry, "destination", public if idx == primary else "",
                parse_height(gdf.loc[idx], HEIGHT_DEST))
        print(f"  destination: {public} ({len(match)} part[s])")

    # --- City-core start points ---
    for o in ORIGINS:
        pt = gpd.GeoSeries([Point(o["at"][1], o["at"][0])], crs=4326).to_crs(27700).iloc[0]
        d = proj.geometry.distance(pt)
        if o["mode"] == "one":
            idxs = [d.idxmin()] if d.min() <= 130 else []
        elif o["mode"] == "cluster":
            idxs = list(d[d <= o["radius"]].index)
        else:  # complex: connected station mass, excluding huge retail
            near = d[d <= o["radius"]].index
            idxs = [i for i in near if proj.loc[i].geometry.area <= o["max_area"]]
        idxs = [i for i in idxs if not proj.loc[i].geometry.intersects(wf_buf)]  # don't block wayfinders
        primary = max(idxs, key=lambda i: proj.loc[i].geometry.area) if idxs else None
        for idx in idxs:
            if idx in used:
                continue
            used.add(idx)
            add(gdf.loc[idx].geometry, "start", o["name"] if idx == primary else "",
                parse_height(gdf.loc[idx], HEIGHT_START))
        print(f"  start: {o['name']} ({len(idxs)} building[s])")

    # --- Context: entrance-to-B-KQ + cluster fabric (east of the gateway only) ---
    cluster_centroid = proj.loc[[i for i in used if gdf.loc[i].geometry.centroid.x > -1.889]].geometry.union_all().centroid
    entrance = LineString([
        gpd.GeoSeries([Point(PAVILION[1], PAVILION[0])], crs=4326).to_crs(27700).iloc[0].coords[0],
        gpd.GeoSeries([Point(JUNCTION[1], JUNCTION[0])], crs=4326).to_crs(27700).iloc[0].coords[0],
        (cluster_centroid.x, cluster_centroid.y),
    ])
    focus = entrance.buffer(CONTEXT_BUFFER_M)
    gateway_x = gpd.GeoSeries([Point(GATEWAY_ANCHOR[1], GATEWAY_ANCHOR[0])], crs=4326).to_crs(27700).iloc[0].x
    pav_pt = gpd.GeoSeries([Point(PAVILION[1], PAVILION[0])], crs=4326).to_crs(27700).iloc[0]
    cand = proj[proj.geometry.intersects(focus) & ~proj.index.isin(used)].copy()
    cand = cand[cand.geometry.centroid.x >= gateway_x - 30]  # nothing west of the gateway
    cand = cand[cand.geometry.distance(pav_pt) > 38]  # keep the pavilion's grass island clear
    cand = cand[~cand.geometry.intersects(wf_buf)]  # don't block wayfinder markers
    cand["__a"] = cand.geometry.area
    context_added = 0
    for idx in cand.sort_values("__a", ascending=False).head(CONTEXT_CAP).index:
        add(gdf.loc[idx].geometry, "context", "", min(parse_height(gdf.loc[idx], HEIGHT_CONTEXT), CONTEXT_MAX_H))
        context_added += 1
    print(f"  context (entrance + cluster): {context_added}")

    # --- Pavilion on the grass island ---
    add(shape({"type": "Polygon", "coordinates": [ellipse(*PAVILION, 13, 7, 30)]}), "pavilion", "Gateway pavilion (concept)", 1.0)
    add(shape({"type": "Polygon", "coordinates": [ellipse(*PAVILION, 15.5, 9, 30)]}), "pavilion", "", 5.4, base=4.6)
    print("  pavilion: on grass island", PAVILION)

    OUT_BUILDINGS.write_text(json.dumps({
        "type": "FeatureCollection",
        "attribution": "Building footprints (c) OpenStreetMap contributors, ODbL",
        "features": features,
    }), encoding="utf-8")
    by_cat: dict[str, int] = {}
    for f in features:
        by_cat[f["properties"]["category"]] = by_cat.get(f["properties"]["category"], 0) + 1
    print(f"wrote {OUT_BUILDINGS.name} | {len(features)} features | {by_cat}")

    # --- Safer crossing across the A4540 DUAL carriageway (two stages + refuge) ---
    rd = fetch(JUNCTION, tags={"highway": True}, dist=200)
    rd = rd[rd.geometry.type == "LineString"]
    refc = rd["ref"].astype(str) if "ref" in rd.columns else pd.Series([""] * len(rd))
    namec = rd["name"].astype(str) if "name" in rd.columns else pd.Series([""] * len(rd))
    road = rd[refc.str.contains("A4540", na=False) | namec.str.contains("Dartmouth", na=False)]
    jp = Point(JUNCTION[1], JUNCTION[0])
    seg = min(road.geometry, key=lambda g: g.distance(jp))
    t = seg.project(jp)
    cp = seg.interpolate(t)  # the point ON the carriageway nearest the junction
    p1, p2 = seg.interpolate(max(0, t - 14)), seg.interpolate(min(seg.length, t + 14))
    brg = math.degrees(math.atan2(p2.x - p1.x, p2.y - p1.y)) % 360
    ml = mlon(cp.y)
    pr = math.radians(brg + 90)  # across-road (crossing) direction

    def across(dist):  # point offset from the carriageway point along the crossing direction
        return (cp.y + math.cos(pr) * dist * MLAT, cp.x + math.sin(pr) * dist * ml)

    feats = []
    # Two crossing bands (going + coming carriageways), refuge island in the median.
    for centre in (-11.5, 11.5):
        clat, clon = across(centre)
        feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [rot_rect(clat, clon, 7.0, 13.0, brg)]},
                      "properties": {"kind": "band", "name": "Safer crossing (concept)"}})
    rlat, rlon = across(0)
    feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [rot_rect(rlat, rlon, 7.0, 9.0, brg)]},
                  "properties": {"kind": "refuge"}})
    # signal heads at the outer kerbs + refuge edges
    for d in (-18, -4.5, 4.5, 18):
        slat, slon = across(d)
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [slon, slat]},
                      "properties": {"kind": "signal"}})

    crossing = {
        "type": "FeatureCollection",
        "attribution": "Road geometry (c) OpenStreetMap contributors, ODbL",
        "features": feats,
    }
    OUT_CROSSING.write_text(json.dumps(crossing), encoding="utf-8")
    print(f"wrote {OUT_CROSSING.name} | dual-carriageway Toucan at lat={cp.y:.5f} lon={cp.x:.5f} (brg {brg:.0f})")

    # --- 3D wayfinders: tall TOTEMS (directional/crossing) vs flat MARKERS (ground/lighting) ---
    totems = []
    for f in wf_geo["features"]:
        lon, lat = f["geometry"]["coordinates"]
        p = f["properties"]
        typ = str(p.get("type", ""))
        is_totem = any(k in typ.lower() for k in ("totem", "crossing", "directional"))
        props = {
            "id": p.get("id"), "type": typ, "role": p.get("role"), "heading": p.get("heading"),
            "walkTimeMin": p.get("walkTimeMin"), "onwardDestinations": p.get("onwardDestinations"),
            "crossingCaution": p.get("crossingCaution") or "",
            "form": "totem" if is_totem else "marker", "heightM": 6.0 if is_totem else 0.0,
            "lon": lon, "lat": lat,
        }
        geom = ({"type": "Polygon", "coordinates": [square(lat, lon, 1.5)]} if is_totem
                else {"type": "Point", "coordinates": [lon, lat]})
        totems.append({"type": "Feature", "geometry": geom, "properties": props})
    OUT_TOTEMS.write_text(json.dumps({
        "type": "FeatureCollection",
        "attribution": "Derived from wayfinder placement; basemap (c) OpenStreetMap contributors",
        "features": totems,
    }), encoding="utf-8")
    print(f"wrote {OUT_TOTEMS.name} | {len(totems)} wayfinder totems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
