#!/usr/bin/env python3
"""Signal shared foundation — tokens, palette state, geometry, IR, pptx emission.

Extracted from build/deck.py in M2. Nothing here knows about slide content;
build/deck.py keeps the SLIDES spec and re-exports this module as a shim.

Coordinates are slide pixels (1280x720); 1px = 9525 EMU, so the pptx is exactly
13.333in x 7.5in and the HTML preview matches.
"""
from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

import compat

__all__ = [
    "ALIGN", "DARK", "H", "LIGHT", "M", "PALETTE", "PHOTOS", "PX", "ROOT",
    "ROUNDED", "TOK", "W",
    "add_chart", "card", "chart", "current_palette", "font_of", "footer", "hexof",
    "img", "kicker", "load_palette", "palette_scope", "palette_stack_depth",
    "photo_src", "r", "render_pptx", "rounded_photo", "stat", "t", "tok",
    "NEW_KINDS", "add_geometry", "chevron_abs_points", "chevron_adj",
    "geom_number", "geometry_box", "geometry_fill", "geometry_stroke",
    "poly_abs_points", "poly_points",
]


ROOT = Path(__file__).resolve().parent.parent
TOK = json.loads((ROOT / "dist" / "json" / "tokens.resolved.json").read_text())

# Two palettes, each with a light and a dark side. Pick with
#   python build/deck.py adventurous
PALETTE = compat.validate_palette(os.environ.get("SIGNAL_PALETTE", compat.DEFAULT_PALETTE))

# Saved (PALETTE, LIGHT, DARK) triples for nested palette scopes (M3, D2/P2).
_PALETTE_STACK: list[tuple[str, dict, dict]] = []


def _select_palette(name: str) -> None:
    global PALETTE, LIGHT, DARK
    PALETTE = name
    LIGHT, DARK = TOK[f"{name}.light"], TOK[f"{name}.dark"]


def load_palette(name: str) -> None:
    """Select *name* as the process-wide palette.

    Raises ``ValueError`` for an unsupported name (pre-M3 this leaked a
    ``KeyError`` from the token dict lookup).
    """
    _select_palette(compat.validate_palette(name))


@contextlib.contextmanager
def palette_scope(name: str):
    """Select *name* for the duration of the block, then restore the previous.

    Scopes nest; the ``finally`` restores even when the body raises, so a failed
    render cannot leak palette state into the next one.
    """
    global PALETTE, LIGHT, DARK
    name = compat.validate_palette(name)
    _PALETTE_STACK.append((PALETTE, LIGHT, DARK))
    _select_palette(name)
    try:
        yield name
    finally:
        PALETTE, LIGHT, DARK = _PALETTE_STACK.pop()


def current_palette() -> str:
    """Palette currently selected."""
    return PALETTE


def palette_stack_depth() -> int:
    """Number of active palette scopes (0 outside a scoped render)."""
    return len(_PALETTE_STACK)


LIGHT, DARK = TOK[f"{PALETTE}.light"], TOK[f"{PALETTE}.dark"]

PX = 9525
W, H = 1280, 720
M = 72
PHOTOS = ROOT / "examples" / "photos"

def tok(theme: str, name: str):
    return (DARK if theme == "dark" else LIGHT)[name]


def hexof(theme: str, name: str) -> str:
    return str(tok(theme, name)).lstrip("#").upper()


def font_of(which: str) -> str:
    fam = LIGHT[f"type.family.{which}"]
    return fam[0] if isinstance(fam, list) else fam.split(",")[0].strip().strip("'")

# ------------------------------------------------------------------ helpers
def t(x, y, w, h, text, color, theme="light", font="body", size=16, bold=False,
      leading=1.3, spacing=0.0, caps=False, align="left"):
    return {"kind": "text", "x": x, "y": y, "w": w, "h": h, "text": text,
            "theme": theme, "color": color, "font": font, "size": size,
            "bold": bold, "leading": leading, "spacing": spacing,
            "caps": caps, "align": align}


def r(x, y, w, h, fill, theme="light", radius=0, stroke=None, stroke_w=1):
    return {"kind": "rect", "x": x, "y": y, "w": w, "h": h, "fill": fill,
            "theme": theme, "radius": radius, "stroke": stroke, "stroke_w": stroke_w}


def img(x, y, w, h, name="photo-43.png", theme="light", radius=28):
    return {"kind": "image", "x": x, "y": y, "w": w, "h": h, "src": name,
            "theme": theme, "radius": radius}


def chart(x, y, w, h, categories, series, kind="bar", theme="light", title=""):
    return {"kind": "chart", "x": x, "y": y, "w": w, "h": h, "categories": categories,
            "series": series, "chart": kind, "theme": theme, "title": title}


def kicker(y, label, theme="light"):
    return [r(M, y + 2, 10, 10, "brand.primary", theme),
            t(M + 24, y - 2, 620, 22, label, "slide.kicker-fg", theme,
              size=11, bold=True, caps=True, spacing=0.18, font="mono"),
            r(M, y + 34, 132, 3, "slide.rule", theme)]


def footer(page, theme="light", label="Commissioning readiness · NV5"):
    return [r(M, H - 108, W - 2 * M, 1, "border.subtle", theme),
            t(M, H - 92, 700, 20, label, "slide.footer-fg", theme, size=10, font="mono"),
            t(W - M - 80, H - 92, 80, 20, f"{page:02d}", "slide.page-no-fg", theme,
              size=10, font="mono", align="right")]


def stat(x, y, w, number, label, theme="light", accent="brand.primary"):
    return [t(x, y, w, 70, number, accent, theme, size=60, bold=True, font="mono", leading=1.0),
            t(x, y + 76, w, 44, label, "text.secondary", theme, size=13, leading=1.4)]


def card(x, y, w, h, number, label, delta, theme="dark", delta_color="brand.accent-text"):
    return [r(x, y, w, h, "surface.raised", theme, radius=18),
            t(x + 24, y + 28, w - 48, 64, number, "text.primary", theme,
              size=46, bold=True, font="mono", leading=1.0),
            t(x + 24, y + 100, w - 48, 40, label, "text.secondary", theme, size=13, leading=1.4),
            t(x + 24, y + h - 44, w - 48, 22, delta, delta_color, theme, size=11, font="mono")]

def photo_src(name: str) -> str:
    """Warm palette gets its own stand-in art; real photos can be dropped per palette."""
    if PALETTE == "professional":
        return name
    alt = f"{Path(name).stem}-{PALETTE}.png"
    return alt if (PHOTOS / alt).exists() else name


# ------------------------------------------------------------------ rounding
ROUNDED = PHOTOS / "rounded"


def rounded_photo(name: str, w: int, h: int, radius: int) -> Path:
    """Crop the slot to a rounded rectangle once, so any replacement photo inherits it."""
    from PIL import Image, ImageDraw

    ROUNDED.mkdir(parents=True, exist_ok=True)
    out = ROUNDED / f"{Path(name).stem}-{w}x{h}-r{radius}.png"
    if out.exists():
        return out
    src = Image.open(PHOTOS / name).convert("RGB").resize((w, h), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    src.putalpha(mask)
    src.save(out)
    return out

ALIGN = {"left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT, "center": PP_ALIGN.CENTER}

def add_chart(slide, el, theme):
    cd = CategoryChartData()
    cd.categories = el["categories"]
    for s in el["series"]:
        cd.add_series(s["name"], s["values"])
    kind = XL_CHART_TYPE.LINE_MARKERS if el.get("chart") == "line" else XL_CHART_TYPE.COLUMN_CLUSTERED
    gf = slide.shapes.add_chart(kind, Emu(el["x"] * PX), Emu(el["y"] * PX),
                                Emu(el["w"] * PX), Emu(el["h"] * PX), cd)
    ch = gf.chart
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.TOP
    ch.legend.include_in_layout = False
    ch.font.size = Pt(10)
    ch.font.name = font_of("mono")
    ch.font.color.rgb = RGBColor.from_string(hexof(theme, "text.secondary"))
    ch.has_title = bool(el.get("title"))
    if el.get("title"):
        ch.chart_title.text_frame.text = el["title"]

    plot = ch.plots[0]
    plot.gap_width = 60
    plot.has_data_labels = False
    va = ch.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor.from_string(hexof(theme, "border.subtle"))
    va.major_gridlines.format.line.width = Pt(0.5)
    va.format.line.color.rgb = RGBColor.from_string(hexof(theme, "border.default"))
    va.tick_labels.font.size = Pt(9)
    va.tick_labels.font.name = font_of("mono")
    ca = ch.category_axis
    ca.format.line.color.rgb = RGBColor.from_string(hexof(theme, "border.default"))
    ca.tick_labels.font.size = Pt(10)
    ca.tick_labels.font.name = font_of("body")
    ca.tick_labels.font.color.rgb = RGBColor.from_string(hexof(theme, "text.primary"))

    for i, s in enumerate(el["series"]):
        ser = plot.series[i]
        col = RGBColor.from_string(hexof(theme, s["color"]))
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = col
        ser.format.line.color.rgb = col
        if el.get("chart") == "line":
            ser.format.line.width = Pt(2.5)
            ser.smooth = False


def render_pptx(path: Path, slides, *, palette=None, appearance=None, theme=None) -> None:
    """Render *slides* to *path*.

    ``palette=`` and ``appearance=`` are independent dimensions (M3). ``theme=``
    is the deprecated alias for ``appearance=`` and never selects a palette.
    A per-slide appearance in the IR wins over ``appearance=``, which wins over
    the document default (the first slide's appearance, D1/D6).
    """
    resolved_palette, document_appearance = compat.resolve_document(
        slides, palette, appearance, theme)
    with palette_scope(resolved_palette):
        _render_pptx(path, slides, document_appearance)


def _render_pptx(path: Path, slides, document_appearance: str) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(W * PX), Emu(H * PX)
    blank = prs.slide_layouts[6]

    for spec in slides:
        theme = compat.resolve_slide(spec, document_appearance)
        slide = prs.slides.add_slide(blank)
        for el in spec["elements"]:
            el_theme = compat.appearance_of(el, theme) or theme
            x, y, w, h = (Emu(int(el[k] * PX)) for k in ("x", "y", "w", "h"))
            if el["kind"] == "rect":
                rad = int(el.get("radius") or 0)
                if rad > 0:
                    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
                    shape.adjustments[0] = min(0.5, rad / min(el["w"], el["h"]))
                else:
                    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
                shape.fill.solid()
                shape.fill.fore_color.rgb = RGBColor.from_string(hexof(el_theme, el["fill"]))
                if el.get("stroke"):
                    shape.line.color.rgb = RGBColor.from_string(hexof(el_theme, el["stroke"]))
                    shape.line.width = Pt(el.get("stroke_w", 1) * 0.75)
                else:
                    shape.line.fill.background()
                shape.shadow.inherit = False
                continue

            if el["kind"] in NEW_KINDS:
                add_geometry(slide, el, el_theme)
                continue

            if el["kind"] == "image":
                rad = int(el.get("radius") or 0)
                src = (rounded_photo(photo_src(el["src"]), int(el["w"]), int(el["h"]), rad)
                       if rad > 0 else PHOTOS / photo_src(el["src"]))
                slide.shapes.add_picture(str(src), x, y, w, h)
                continue

            if el["kind"] == "chart":
                add_chart(slide, el, el_theme)
                continue

            box = slide.shapes.add_textbox(x, y, w, h)
            tf = box.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.TOP
            for i, line in enumerate(el["text"].split("\n")):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.alignment = ALIGN.get(el.get("align", "left"), PP_ALIGN.LEFT)
                p.line_spacing = el.get("leading", 1.2)
                run = p.add_run()
                run.text = line.upper() if el.get("caps") else line
                f = run.font
                f.size = Pt(el["size"] * 0.75)
                f.bold = bool(el.get("bold"))
                f.name = font_of(el.get("font", "body"))
                f.color.rgb = RGBColor.from_string(hexof(el_theme, el["color"]))
                if el.get("spacing"):
                    f._rPr.set("spc", str(int(el["spacing"] * 100)))

    prs.save(path)


# --------------------------------------------------------------------------
# geometry primitives (M4): poly / chevron / ellipse
# --------------------------------------------------------------------------
# Shared by every pptx consumer (deck, analyst, atlas, atlas_v0). Geometry is
# always resolved in slide pixels here, so both pptx and html agree on points;
# html rendering lives in preview.el_html / analyst.el_html.

NEW_KINDS = ("poly", "chevron", "ellipse")


def geom_number(el, key, default=None):
    """Numeric field of a geometry element; rejects bools and strings."""
    if key not in el:
        if default is None:
            raise ValueError("%s: missing required field %r" % (el.get("kind"), key))
        return float(default)
    v = el[key]
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError("%s: %s must be a number, got %r" % (el.get("kind"), key, v))
    return float(v)


def geometry_box(el):
    """Validated (x, y, w, h) of a geometry element, in slide pixels."""
    for k in ("x", "y", "w", "h"):
        geom_number(el, k)
    w, h = float(el["w"]), float(el["h"])
    if w <= 0 or h <= 0:
        raise ValueError("%s: w and h must be > 0" % el.get("kind"))
    return float(el["x"]), float(el["y"]), w, h


def poly_points(el):
    """Validated normalised points of a poly element (>= 3 pairs in 0..1)."""
    pts = el.get("points")
    if not isinstance(pts, (list, tuple)) or len(pts) < 3:
        raise ValueError("poly: points must be a list of at least 3 [u, v] pairs")
    out = []
    for i, p in enumerate(pts):
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            raise ValueError("poly: points[%d] must be a [u, v] pair" % i)
        pair = []
        for j, c in enumerate(p):
            if isinstance(c, bool) or not isinstance(c, (int, float)):
                raise ValueError("poly: points[%d][%d] must be a number" % (i, j))
            if not 0.0 <= float(c) <= 1.0:
                raise ValueError("poly: points[%d][%d] must be in 0..1" % (i, j))
            pair.append(float(c))
        out.append(pair)
    return out


def poly_abs_points(el):
    """Normalised poly points mapped into slide pixels (bbox-relative)."""
    x, y, w, h = geometry_box(el)
    return [(int(round(x + u * w)), int(round(y + v * h))) for u, v in poly_points(el)]


def chevron_adj(el):
    adj = geom_number(el, "adj", 0.5)
    if not 0.0 <= adj <= 1.0:
        raise ValueError("chevron: adj must be in 0..1")
    return adj


def chevron_abs_points(el):
    """Chevron hexagon (6 points): x1 = adj * min(w, h), tip at mid-height,
    concave notch on left. Points: top-left, top-notch, right-tip, bottom-notch,
    bottom-left, left-notch (inward).
    """
    x, y, w, h = geometry_box(el)
    x1 = chevron_adj(el) * min(w, h)
    return [
        (int(round(x)), int(round(y))),
        (int(round(x + w - x1)), int(round(y))),
        (int(round(x + w)), int(round(y + h / 2.0))),
        (int(round(x + w - x1)), int(round(y + h))),
        (int(round(x)), int(round(y + h))),
        (int(round(x + x1)), int(round(y + h / 2.0))),
    ]


def geometry_fill(el, theme):
    """Resolved fill hex, or None for an unfilled outline shape."""
    fill = el.get("fill")
    if fill is None:
        return None
    try:
        return hexof(theme, fill)
    except KeyError:
        raise ValueError("%s: unknown token %r for theme %r"
                         % (el.get("kind"), fill, theme)) from None


def geometry_stroke(el, theme):
    """Resolved (stroke hex, width px); (None, 0) when there is no stroke."""
    stroke = el.get("stroke")
    if stroke is None:
        return None, 0.0
    try:
        return hexof(theme, stroke), geom_number(el, "stroke_w", 1)
    except KeyError:
        raise ValueError("%s: unknown token %r for theme %r"
                         % (el.get("kind"), stroke, theme)) from None


def _geometry_style(shp, fill, stroke, stroke_w):
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = RGBColor.from_string(fill)
    if stroke is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = RGBColor.from_string(stroke)
        shp.line.width = Pt(stroke_w * 0.75)


def _insets(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def add_geometry(slide, el, theme):
    """Emit a poly / chevron / ellipse element onto a pptx slide."""
    kind = el["kind"]
    if kind == "poly":
        pts = poly_abs_points(el)
        x0, y0 = pts[0]
        fb = slide.shapes.build_freeform(PX * x0, PX * y0, scale=1.0)
        fb.add_line_segments([(PX * px, PX * py) for px, py in pts[1:]], close=True)
        shp = fb.convert_to_shape()
    elif kind == "chevron":
        x, y, w, h = geometry_box(el)
        shp = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, PX * x, PX * y, PX * w, PX * h)
        shp.adjustments[0] = chevron_adj(el)
    elif kind == "ellipse":
        x, y, w, h = geometry_box(el)
        shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, PX * x, PX * y, PX * w, PX * h)
    else:
        raise ValueError("unknown geometry kind: %r" % kind)

    fill = geometry_fill(el, theme)
    stroke, stroke_w = geometry_stroke(el, theme)

    _geometry_style(shp, fill, stroke, stroke_w)
    rot = geom_number(el, "rotation", 0)
    if rot:
        shp.rotation = rot
    return shp
