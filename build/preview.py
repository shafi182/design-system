#!/usr/bin/env python3
"""Render the same slide spec to HTML, so the deck can be seen without PowerPoint.

Charts are drawn as SVG from the same numbers the pptx chart uses; photos are the
same PNG files, so the preview and the .pptx stay in step.

    python build/preview.py     # examples/preview.html
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))

import compat  # noqa: E402

PALETTE = compat.validate_palette(sys.argv[1] if len(sys.argv) > 1 else compat.DEFAULT_PALETTE)
os.environ["SIGNAL_PALETTE"] = PALETTE

import base  # noqa: E402
from base import LIGHT, DARK, W, H, photo_src  # noqa: E402
from deck import SLIDES  # noqa: E402

# Geometry kinds introduced in M4; resolved by base.add_geometry / svg_geometry.
GEOM_KINDS = base.NEW_KINDS

PHOTOS = ROOT / "examples" / "photos"


def color(theme: str, name: str) -> str:
    """Return CSS custom property reference for a token.
    
    Example: color("light", "text.primary") → "var(--ds-text-primary)"
    
    Chart series are mapped to indexed vars: "chart.series.0" → "var(--ds-chart-series-0)"
    """
    if not name:
        return ""
    # Handle chart.series.{index} → --ds-chart-series-{index}
    if name.startswith("chart.series."):
        idx = name.split(".")[-1]
        return f"var(--ds-chart-series-{idx})"
    # Standard tokens: family.slot → --ds-family-slot
    family, _, slot = name.partition(".")
    if slot:
        return f"var(--ds-{family}-{slot})"
    return ""


def fam(name: str) -> str:
    return base.font_of(name)


def svg_chart(el, theme) -> str:
    w, h = el["w"], el["h"]
    cats, series = el["categories"], el["series"]
    pad_l, pad_b, pad_t, pad_r = 44, 34, 10, 8
    plot_w, plot_h = w - pad_l - pad_r, h - pad_b - pad_t
    peak = max(max(s["values"]) for s in series) or 1
    import math
    top = max(4, math.ceil(peak / 4) * 4)   # nice round axis top
    line = color(theme, "border.subtle")
    axis = color(theme, "border.default")
    muted = color(theme, "text.secondary")
    strong = color(theme, "text.primary")

    parts = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
             f'style="position:absolute;left:{el["x"]}px;top:{el["y"]}px;">']

    # gridlines + value labels
    for i in range(1, 5):
        val = top * i / 4
        y = pad_t + plot_h - plot_h * i / 4
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" '
                     f'stroke="{line}" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l - 8}" y="{y + 3:.1f}" text-anchor="end" '
                     f'font-family="{fam("mono")}" font-size="9" fill="{muted}">{val:.0f}</text>')

    n = len(cats)
    slot = plot_w / n
    if el.get("chart") == "line":
        for s in series:
            pts = []
            for i, v in enumerate(s["values"]):
                x = pad_l + slot * (i + 0.5)
                y = pad_t + plot_h - (v / top) * plot_h
                pts.append(f"{x:.1f},{y:.1f}")
            col = color(theme, s["color"])
            parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" '
                         f'stroke-width="2.5" stroke-linejoin="round"/>')
            for p in pts:
                cx, cy = p.split(",")
                parts.append(f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="{col}"/>')
    else:
        group_w = slot * 0.62
        bar_w = group_w / len(series)
        for i in range(n):
            gx = pad_l + slot * i + (slot - group_w) / 2
            for j, s in enumerate(series):
                v = s["values"][i]
                bh = (v / top) * plot_h
                parts.append(
                    f'<rect x="{gx + j * bar_w:.1f}" y="{pad_t + plot_h - bh:.1f}" '
                    f'width="{bar_w - 3:.1f}" height="{bh:.1f}" '
                    f'fill="{color(theme, s["color"])}"/>')

    parts.append(f'<line x1="{pad_l}" y1="{pad_t + plot_h}" x2="{w - pad_r}" '
                 f'y2="{pad_t + plot_h}" stroke="{axis}" stroke-width="1"/>')
    for i, c in enumerate(cats):
        x = pad_l + slot * (i + 0.5)
        parts.append(f'<text x="{x:.1f}" y="{h - 12}" text-anchor="middle" '
                     f'font-family="{fam("body")}" font-size="11" fill="{strong}">{c}</text>')

    # legend, top-left
    lx = pad_l
    for s in series:
        parts.append(f'<rect x="{lx}" y="2" width="9" height="9" fill="{color(theme, s["color"])}"/>')
        parts.append(f'<text x="{lx + 14}" y="10" font-family="{fam("mono")}" font-size="9" '
                     f'fill="{muted}">{s["name"].upper()}</text>')
        lx += 20 + len(s["name"]) * 7

    parts.append("</svg>")
    return "".join(parts)


def svg_geometry(el, theme) -> str:
    """Inline SVG for a poly / chevron / ellipse element (M4)."""
    kind = el["kind"]
    x, y, w, h = base.geometry_box(el)
    fill = color(theme, el["fill"]) if el.get("fill") is not None else None
    stroke = color(theme, el["stroke"]) if el.get("stroke") is not None else None
    paint = f'fill="{fill}"' if fill else 'fill="none"'
    if stroke:
        paint += f' stroke="{stroke}" stroke-width="{el.get("stroke_w", 1)}"'
    if kind == "ellipse":
        shape = (f'<ellipse cx="{x + w / 2.0:g}" cy="{y + h / 2.0:g}" '
                 f'rx="{w / 2.0:g}" ry="{h / 2.0:g}" {paint}/>')
    else:
        pts = base.poly_abs_points(el) if kind == "poly" else base.chevron_abs_points(el)
        shape = '<polygon points="%s" %s/>' % (
            " ".join(f"{px},{py}" for px, py in pts), paint)
    rot = base.geom_number(el, "rotation", 0)
    if rot:
        shape = (f'<g transform="rotate({rot:g} {x + w / 2.0:g} {y + h / 2.0:g})">'
                 f'{shape}</g>')
    return (f'<svg style="position:absolute;left:0;top:0;overflow:visible;" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">{shape}</svg>')


def el_html(el, theme) -> str:
    base = (f"position:absolute;left:{el['x']}px;top:{el['y']}px;"
            f"width:{el['w']}px;height:{el['h']}px;")
    if el["kind"] == "rect":
        rad = el.get("radius") or 0
        stroke = (f'border:{el.get("stroke_w", 1)}px solid {color(theme, el["stroke"])};'
                  if el.get("stroke") else "")
        return (f'<div style="{base}background:{color(theme, el["fill"])};{stroke}'
                f'border-radius:{rad}px;"></div>')
    if el["kind"] == "image":
        rad = el.get("radius") or 0
        return (f'<img src="file://{PHOTOS / photo_src(el["src"])}" style="{base}object-fit:cover;'
                f'border-radius:{rad}px;display:block;">')
    if el["kind"] in GEOM_KINDS:
        return svg_geometry(el, theme)
    if el["kind"] == "chart":
        return svg_chart(el, theme)
    text = el["text"].upper() if el.get("caps") else el["text"]
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace("\n", "<br>")
    return (f'<div style="{base}font-family:\'{fam(el.get("font", "body"))}\';'
            f'font-size:{el["size"]}px;color:{color(theme, el["color"])};'
            f'font-weight:{700 if el.get("bold") else 400};'
            f'line-height:{el.get("leading", 1.2)};letter-spacing:{el.get("spacing", 0)}em;'
            f'text-align:{el.get("align", "left")};white-space:pre-wrap;">{text}</div>')


def build(path: Path, *, palette=None, appearance=None, theme=None) -> None:
    """Render the pitch-deck preview to HTML.

    ``palette=`` and ``appearance=`` are independent dimensions (M3); ``theme=``
    is the deprecated alias for ``appearance=``.
    """
    resolved_palette, document_appearance = compat.resolve_document(
        SLIDES, palette, appearance, theme)
    with base.palette_scope(resolved_palette):
        _build(path, document_appearance)


def _build(path: Path, document_appearance: str) -> None:
    palette = base.PALETTE
    slides = []
    for i, spec in enumerate(SLIDES, 1):
        theme = compat.resolve_slide(spec, document_appearance)
        bg = color(theme, "surface.base")
        inner = "\n".join(el_html(el, compat.appearance_of(el, theme) or theme)
                          for el in spec["elements"])
        slides.append(
            f'<section class="slide" id="s{i}" data-theme="{theme}" '
            f'style="background:{bg};">{inner}</section>')

    # Generate scoped CSS rules for all palette × appearance combinations
    import css_gen
    themes = {
        f"{palette}.light": base.LIGHT,
        f"{palette}.dark": base.DARK,
    }
    scoped_css = css_gen.generate_all_scoped_rules(themes)

    html = f"""<!doctype html><html data-palette="{palette}" data-theme="{document_appearance}"><head><meta charset="utf-8">
<title>Pitch deck preview — {palette}</title>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
.num{{font-variant-numeric:tabular-nums}}
body{{background:#333;display:flex;flex-direction:column;gap:24px;padding:24px;width:{W + 48}px}}
.slide{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}

/* Design token CSS variables (M5) */
{scoped_css}
</style></head><body>
{chr(10).join(slides)}
</body></html>"""
    path.write_text(html, encoding="utf-8")


def main(argv=None) -> None:
    """CLI entry point: render the requested palette into ``examples/``.

    The palette must be forwarded explicitly: ``build()`` defaults ``palette=None``
    to ``compat.DEFAULT_PALETTE`` (professional), which would otherwise override the
    palette parsed from argv at import time.
    """
    argv = sys.argv[1:] if argv is None else argv
    palette = compat.validate_palette(argv[0] if argv else PALETTE)
    out = ROOT / "examples" / f"preview-{palette}.html"
    out.parent.mkdir(exist_ok=True)
    build(out, palette=palette)
    print("wrote", out, len(SLIDES), "slides")


if __name__ == "__main__":
    main()
