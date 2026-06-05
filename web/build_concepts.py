"""Optimise the local concept artwork into web-ready assets for the Concepts gallery.

Source images live in ../phase1concepts (local reference, gitignored). This script
writes web-optimised WebP at two sizes into web/public/concepts/ (committed app
assets) plus a concepts.json manifest with plain-English captions. Re-run whenever
the source artwork changes.

  display : max 1800px wide, quality 86  (lightbox / large view)
  thumb   : max 900px wide,  quality 82  (gallery cards, fast load)

Run:  python build_concepts.py            (needs Pillow)
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "phase1concepts"
OUT_DIR = ROOT / "web" / "public" / "concepts"
MANIFEST = ROOT / "web" / "public" / "concepts.json"

DISPLAY_MAX_W, DISPLAY_Q = 1800, 86
THUMB_MAX_W, THUMB_Q = 900, 82

# Curated order (follows the journey) + plain-English, public-friendly copy.
CONCEPTS = [
    {
        "file": "corridorconcept.png",
        "slug": "amber-route",
        "title": "The amber route",
        "caption": "A bright amber path on the ground leads you out of the city centre. Clear "
                   "wayfinders show the way and the walking time to the Knowledge Quarter.",
    },
    {
        "file": "safercrossing.png",
        "slug": "safer-crossing",
        "title": "The safer crossing",
        "caption": "A new signal-controlled crossing at the Dartmouth and Jennens junction, with an "
                   "island in the middle, so people on foot and on bikes can cross the main road safely.",
    },
    {
        "file": "Gatewaypavillionclose.png",
        "slug": "gateway-pavilion",
        "title": "The gateway pavilion",
        "caption": "A welcoming timber pavilion marks the front door to the Knowledge Quarter, with "
                   "seating, planting and a wayfinder hub. It can be taken away again later.",
    },
    {
        "file": "pavillionairview.png",
        "slug": "pavilion-aerial",
        "title": "The pavilion from above",
        "caption": "Seen from above, the pavilion sits on a public square where the amber route "
                   "arrives, giving the Knowledge Quarter a clear, green welcome.",
    },
]


def save_webp(img: Image.Image, max_w: int, quality: int, dest: Path) -> tuple[int, int]:
    out = img
    if img.width > max_w:
        h = round(img.height * max_w / img.width)
        out = img.resize((max_w, h), Image.LANCZOS)
    out.convert("RGB").save(dest, "WEBP", quality=quality, method=6)
    return out.width, out.height


def save_og(src: Path, dest: Path, size=(1200, 630), quality=88) -> None:
    """Centre-crop a hero image to a 1200x630 social share card (LinkedIn/Twitter)."""
    img = Image.open(src).convert("RGB")
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = (resized.width - tw) // 2
    top = (resized.height - th) // 2
    resized.crop((left, top, left + tw, top + th)).save(dest, "JPEG", quality=quality)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for c in CONCEPTS:
        src = SOURCE_DIR / c["file"]
        if not src.exists():
            print(f"  ! missing source: {src}")
            continue
        img = Image.open(src)
        disp = OUT_DIR / f"{c['slug']}.webp"
        thumb = OUT_DIR / f"{c['slug']}-thumb.webp"
        w, h = save_webp(img, DISPLAY_MAX_W, DISPLAY_Q, disp)
        save_webp(img, THUMB_MAX_W, THUMB_Q, thumb)
        manifest.append({
            "id": c["slug"],
            "title": c["title"],
            "caption": c["caption"],
            "alt": f"Concept artwork: {c['title'].lower()}. {c['caption']}",
            "src": f"concepts/{disp.name}",
            "thumb": f"concepts/{thumb.name}",
            "width": w,
            "height": h,
        })
        print(f"  {c['slug']}: {disp.name} ({w}x{h}, {disp.stat().st_size // 1024} KB) + thumb")

    # Social share card (Open Graph / Twitter) from the pavilion hero.
    og_src = SOURCE_DIR / "Gatewaypavillionclose.png"
    if og_src.exists():
        save_og(og_src, OUT_DIR.parent / "og.jpg")
        print(f"  og.jpg: 1200x630 ({(OUT_DIR.parent / 'og.jpg').stat().st_size // 1024} KB)")

    MANIFEST.write_text(
        json.dumps(
            {
                "schemaVersion": "0.1",
                "notes": "Concept artist's impressions of the Phase 1 improvements. Indicative only.",
                "concepts": manifest,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {MANIFEST.relative_to(ROOT)} | {len(manifest)} concepts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
