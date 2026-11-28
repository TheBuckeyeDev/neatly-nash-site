#!/usr/bin/env python3
"""
Generate responsive WebP copies of the site photos in static/images/.
Re-run after adding or replacing a photo: python3 optimize_images.py
Needs Pillow locally (pip install pillow); the Netlify build does not run this.
"""
from pathlib import Path

from PIL import Image

IMAGES = Path(__file__).parent / "static" / "images"

# source file -> output widths. Keep in sync with the srcset attributes in templates/.
WIDTHS = {
    "hero.jpg": [640, 1200],
    "work-1.jpg": [480, 800],
    "work-2.jpg": [480, 800],
    "work-3.jpg": [480, 800],
    "project-1.jpg": [520, 1000],
    "project-2.jpg": [520, 1000],
}


def main():
    for name, widths in WIDTHS.items():
        src = IMAGES / name
        with Image.open(src) as im:
            im = im.convert("RGB")
            for w in widths:
                w = min(w, im.width)
                h = round(im.height * w / im.width)
                out = IMAGES / f"{src.stem}-{w}.webp"
                im.resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=78, method=6)
                print(f"{out.name}: {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
