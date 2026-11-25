#!/usr/bin/env python3
"""Render the same slide spec to HTML, so the deck can be seen without PowerPoint.

    python build/preview.py     # examples/preview.html + examples/slide-NN.png (via browser)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))

from deck import LIGHT, DARK, SLIDES, W, H  # noqa: E402


def color(theme: str, name: str) -> str:
    return (DARK if theme == "dark" else LIGHT)[name]


def el_html(el: dict, theme: str) -> str:
    base = (f"position:absolute;left:{el['x']}px;top:{el['y']}px;"
            f"width:{el['w']}px;height:{el['h']}px;")
    if el["kind"] == "rect":
        return f'<div style="{base}background:{color(theme, el["fill"])};"></div>'
    fam = LIGHT[f"type.family.{el.get('font', 'body')}"]
    fam = fam[0] if isinstance(fam, list) else fam.split(",")[0].strip().strip("'")
    text = el["text"].upper() if el.get("caps") else el["text"]
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace("\n", "<br>")
    return (
        f'<div style="{base}font-family:\'{fam}\';font-size:{el["size"]}px;'
        f'color:{color(theme, el["color"])};'
        f'font-weight:{700 if el.get("bold") else 400};'
        f'line-height:{el.get("leading", 1.2)};'
        f'letter-spacing:{el.get("spacing", 0)}em;'
        f'text-align:{el.get("align", "left")};'
        f'white-space:pre-wrap;">{text}</div>'
    )


def build(path: Path) -> None:
    slides = []
    for i, spec in enumerate(SLIDES, 1):
        theme = spec["theme"]
        bg = color(theme, "surface.base")
        inner = "\n".join(el_html(el, theme) for el in spec["elements"])
        slides.append(
            f'<section class="slide" id="s{i}" style="background:{bg};">{inner}</section>'
        )

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Pitch deck preview</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#333;display:flex;flex-direction:column;gap:24px;padding:24px;width:{W + 48}px}}
.slide{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}
</style></head><body>
{chr(10).join(slides)}
</body></html>"""
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    out = ROOT / "examples" / "preview.html"
    out.parent.mkdir(exist_ok=True)
    build(out)
    print("wrote", out)
