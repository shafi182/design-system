#!/usr/bin/env python3
"""Placeholder photography for the deck slots.

Real photos drop in by replacing these files; the crop ratios are fixed so the
layout never shifts. Generated with PIL, no external assets.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "examples" / "photos"

NAVY = (20, 44, 54)
TEAL = (36, 84, 90)
OLIVE = (182, 185, 165)


def _font(size: int):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make(path: Path, w: int, h: int, label: str, note: str) -> None:
    img = Image.new("RGB", (w, h), (26, 52, 62))   # a touch lighter than the navy
    # canvas, so the slot edge stays visible against a dark slide
    d = ImageDraw.Draw(img)
    # diagonal band so it reads as a placeholder, not a flat colour
    d.polygon([(0, h), (w, 0), (w, h * 0.42), (0, h)], fill=TEAL)
    d.polygon([(0, h), (w * 0.55, h * 0.35), (w * 0.55, h * 0.52), (0, h)], fill=OLIVE)
    f_big, f_small = _font(max(20, w // 26)), _font(max(13, w // 52))
    d.text((w // 22, h // 24), label, font=f_big, fill=(233, 229, 217))
    d.text((w // 22, h // 24 + max(30, w // 20)), note, font=f_small, fill=(233, 229, 217))
    d.rectangle([w // 22, h // 24 + max(66, w // 12), w // 22 + max(60, w // 10),
                 h // 24 + max(66, w // 12) + 4], fill=(255, 109, 31))
    d.rectangle([0, 0, w - 1, h - 1], outline=OLIVE, width=2)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True)
    print(f"  {path.name}  {w}x{h}")


def build() -> dict[str, Path]:
    print("photos:")
    cover = OUT / "photo-cover.png"     # 780x1080, right panel of the cover
    wide = OUT / "photo-43.png"         # 1024x768, standard 4:3 slot
    make(cover, 780, 1080, "PHOTO", "cover · 780×1080 · crop portrait")
    make(wide, 1024, 768, "PHOTO", "slot · 1024×768 · crop 4:3")
    return {"cover": cover, "wide": wide}


if __name__ == "__main__":
    build()
