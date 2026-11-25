#!/usr/bin/env python3
"""Shape library — every layout / diagram / chart type the deck language needs.

Each function returns a flat list of primitives (`t` text, `r` rect, `img`), so a
slide is just `[*shapes.twin_pyramid(...), *shapes.banner(...)]`. No function picks
a colour literal: fills come from tokens (`chart.series.1..4`, `brand.*`, `surface.*`,
`status.*`), so both palettes render correctly and the contrast gate keeps applying.

Naming: <noun>_<form> — `kpi_strip`, `twin_pyramid`, `journey_lane`, `ring_blocks`.
Geometry is in slide pixels (1280x720), origin top-left.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))

import analyst as A  # noqa: E402  (t / r / tokens / palette loader)

t, r = A.t, A.r
SERIES = ["chart.series.1", "chart.series.2", "chart.series.3", "chart.series.4"]


# --------------------------------------------------------------------- text blocks
def label(x, y, w, text, theme="light", color="text.muted", size: float = 7):
    """Micro caption — used under every component in the atlas."""
    return [t(x, y, w, 10, text, color, theme, size=size, leading=1.15)]


def headline(x, y, w, h, text, theme="light", size: float = 15, color="text.primary"):
    """The one claim a slide makes. Sentence case, no full stop."""
    return [t(x, y, w, h, text, color, theme, size=size, bold=True, leading=1.15)]


def kicker(x, y, w, text, theme="light"):
    return [t(x, y, w, 11, text, "brand.primary", theme, size=7.5, bold=True, caps=True,
              spacing=0.14)]


def body_text(x, y, w, h, text, theme="light", size: float = 9):
    return [t(x, y, w, h, text, "text.secondary", theme, size=size, leading=1.35)]


def bullets(x, y, w, h, items, theme="light", size: float = 9, gap: float = 15, color="text.secondary"):
    """Square marker + one line of text. No bullets glyphs, no indents."""
    out = []
    for i, item in enumerate(items):
        yy = y + i * gap
        out.append(r(x, yy + 4, 5, 5, "brand.primary", theme, radius=1))
        out.append(t(x + 12, yy, w - 12, gap, item, color, theme, size=size, leading=1.2))
    return out


def ticks(x, y, w, h, items, theme="light", size: float = 8.5, gap: float = 17, cols=1):
    """Hollow box + text, one or two columns — the checklist form."""
    out = []
    cw = w / cols
    for i, item in enumerate(items):
        cx = x + (i % cols) * cw
        cy = y + (i // cols) * gap
        out.append(r(cx, cy + 1, 8, 8, "surface.base", theme, radius=1,
                     stroke="brand.primary"))
        out.append(t(cx + 14, cy, cw - 16, gap, item, "text.primary", theme, size=size,
                     leading=1.2))
    return out


def quote_block(x, y, w, h, text, attrib, theme="light"):
    """Left rule + italic-free quote + attribution. For voice-of-customer slides."""
    out = [r(x, y, 2, h, "brand.primary", theme),
           t(x + 14, y, w - 14, h - 16, f"\u201c{text}\u201d", "text.primary", theme,
             size=10, leading=1.35),
           t(x + 14, y + h - 14, w - 14, 12, attrib, "text.muted", theme, size=7.5,
             caps=True, spacing=0.08)]
    return out


def banner(x, y, w, h, text, theme="light", sub=None):
    """Full-width statement band — closes a slide with the takeaway."""
    out = [r(x, y, w, h, "brand.primary", theme, radius=4),
           t(x + 14, y + (h - 14) / 2 - (5 if sub else 0), w - 28, 14, text,
             "text.on-brand", theme, size=10, bold=True)]
    if sub:
        out.append(t(x + 14, y + h / 2 + 7, w - 28, 12, sub, "text.on-brand", theme,
                     size=7.5))
    return out


# ---------------------------------------------------------------------- KPI / stats
def kpi_strip(x, y, w, items, theme="light", h=44, gap=8):
    """Six-across metric bar with hairline separators (company overview)."""
    out = []
    n = len(items)
    cw = (w - gap * (n - 1)) / n
    for i, (value, name) in enumerate(items):
        cx = x + i * (cw + gap)
        out.append(r(cx, y, cw, h, "surface.raised", theme, radius=4,
                     stroke="border.subtle"))
        out.append(t(cx + 8, y + 7, cw - 16, 18, value, "text.primary", theme, size=13,
                     bold=True))
        out.append(t(cx + 8, y + 27, cw - 16, 12, name, "text.muted", theme, size=7,
                     caps=True, spacing=0.1))
    return out


def kpi_grid(x, y, w, h, items, theme="light", cols=4):
    """Numbers in a hairline grid — 4 or 8 metrics, no boxes, only rules."""
    out = []
    rows = (len(items) + cols - 1) // cols
    cw, rh = w / cols, h / rows
    for i, (value, name) in enumerate(items):
        cx, cy = x + (i % cols) * cw, y + (i // cols) * rh
        if i % cols:
            out.append(r(cx, cy, 1, rh - 4, "border.subtle", theme))
        if i >= cols:
            out.append(r(cx, cy, cw, 1, "border.subtle", theme))
        out.append(t(cx + 8, cy + 6, cw - 16, 20, value, "text.primary", theme, size=15,
                     bold=True))
        out.append(t(cx + 8, cy + 27, cw - 16, rh - 30, name, "text.secondary", theme,
                     size=7.5, leading=1.2))
    return out


def stat_cards(x, y, w, h, cards, theme="light", gap=10):
    """2–4 equal cards: kicker, big claim, supporting line."""
    out = []
    n = len(cards)
    cw = (w - gap * (n - 1)) / n
    for i, (kic, claim, note) in enumerate(cards):
        cx = x + i * (cw + gap)
        out.append(r(cx, y, cw, h, "surface.raised", theme, radius=5,
                     stroke="border.subtle"))
        out.extend(kicker(cx + 10, y + 10, cw - 20, kic, theme))
        out.append(t(cx + 10, y + 24, cw - 20, 18, claim, "text.primary", theme,
                     size=12.5, bold=True))
        out.append(t(cx + 10, y + 44, cw - 20, h - 50, note, "text.secondary", theme,
                     size=7.5, leading=1.3))
    return out


def stat_row(x, y, w, h, items, theme="light"):
    """Five columns, big number over label over note — the 'expectations' form."""
    out = []
    cw = w / len(items)
    for i, (big, name, note) in enumerate(items):
        cx = x + i * cw
        if i:
            out.append(r(cx - 6, y, 1, h, "border.subtle", theme))
        out.append(t(cx + 6, y, cw - 18, 26, big, "brand.primary", theme, size=20,
                     bold=True))
        out.append(t(cx + 6, y + 30, cw - 18, 14, name, "text.primary", theme, size=8.5,
                     bold=True))
        out.append(t(cx + 6, y + 46, cw - 18, h - 46, note, "text.secondary", theme,
                     size=7, leading=1.25))
    return out


def delta_rows(x, y, w, h, rows, theme="light", rowh: float = 20, label_w=150):
    """Label + track bar + signed delta. Use for 'X% of tasks are exposed'."""
    out = []
    peak = max(abs(v) for _, v, _ in rows) or 1
    for i, (name, value, sign) in enumerate(rows):
        yy = y + i * rowh
        if i:
            out.append(r(x, yy - 4, w, 1, "border.subtle", theme))
        out.append(t(x, yy + 3, label_w, 14, name, "text.primary", theme, size=7.5))
        bx, bw = x + label_w + 6, w - label_w - 46
        out.append(r(bx, yy + 6, bw, 7, "surface.band", theme, radius=2))
        out.append(r(bx, yy + 6, bw * abs(value) / peak, 7,
                     "chart.series.1" if sign > 0 else "chart.series.3", theme, radius=2))
        out.append(t(x + w - 36, yy + 2, 36, 14, f"{sign * value:+.0f}", "text.primary",
                     theme, size=7.5, bold=True, align="right"))
    return out


# ------------------------------------------------------------------------ tables
def compare_table(x, y, w, h, head, rows, theme="light", rowh=18, value_w=58,
                  delta_w=42, highlight=None):
    """Two-period table with a signed delta column (before / after)."""
    out = []
    out.append(t(x, y, w - 2 * (value_w + delta_w), 12, head[0], "text.secondary", theme,
                 size=7.5, bold=True, caps=True, spacing=0.1))
    for i, name in enumerate(head[1:], 1):
        out.append(t(x + w - (3 - i) * value_w - delta_w, y, value_w, 12, name,
                     "text.secondary", theme, size=7.5, bold=True, caps=True,
                     spacing=0.1, align="right"))
    out.append(t(x + w - delta_w, y, delta_w, 12, "Δ", "text.secondary", theme, size=7.5,
                 bold=True, align="right"))
    out.append(r(x, y + 14, w, 1, "border.strong", theme))
    for i, row in enumerate(rows):
        name, before, after = row[0], row[1], row[2]
        delta = row[3] if len(row) > 3 else ""
        yy = y + 18 + i * rowh
        if i:
            out.append(r(x, yy - 4, w, 1, "border.subtle", theme))
        if highlight == i:
            out.append(r(x - 4, yy - 2, w + 8, rowh, "brand.subtle", theme, radius=3))
        out.append(t(x, yy + 3, w - 2 * value_w - delta_w, 13, name, "text.primary",
                     theme, size=8))
        out.append(t(x + w - 2 * value_w - delta_w, yy + 3, value_w, 13, before,
                     "text.secondary", theme, size=8, align="right"))
        out.append(t(x + w - value_w - delta_w, yy + 3, value_w, 13, after,
                     "text.primary", theme, size=8, bold=True, align="right"))
        out.append(t(x + w - delta_w, yy + 3, delta_w, 13, delta, "brand.primary",
                     theme, size=7.5, bold=True, align="right"))
    return out


def icon_grid(x, y, w, h, items, theme="light", cols=4, gap=8):
    """Square glyph + label + note. The glyph is a brand square until an icon exists."""
    out = []
    rows = (len(items) + cols - 1) // cols
    cw, ch = (w - gap * (cols - 1)) / cols, (h - gap * (rows - 1)) / rows
    for i, (name, note) in enumerate(items):
        cx = x + (i % cols) * (cw + gap)
        cy = y + (i // cols) * (ch + gap)
        out.append(r(cx, cy, 16, 16, "brand.subtle", theme, radius=3,
                     stroke="border.subtle"))
        out.append(r(cx + 5, cy + 5, 6, 6, "brand.primary", theme, radius=1))
        out.append(t(cx + 22, cy + 1, cw - 24, 14, name, "text.primary", theme,
                     size=8, bold=True))
        out.append(t(cx + 22, cy + 14, cw - 24, ch - 16, note, "text.secondary", theme,
                     size=7, leading=1.2))
    return out


def list_rows(x, y, w, h, rows, theme="light", rowh: float = 24, num=True):
    """Numbered rows, one claim each — for 'five disruptions' style slides."""
    out = []
    for i, (name, note) in enumerate(rows):
        yy = y + i * rowh
        if i:
            out.append(r(x, yy, w, 1, "border.subtle", theme))
        if num:
            out.append(t(x, yy + 5, 16, 12, f"{i + 1:02d}", "brand.primary", theme,
                         size=7.5, bold=True))
        out.append(t(x + (18 if num else 0), yy + 5, 150, 14, name, "text.primary",
                     theme, size=8.5, bold=True))
        out.append(t(x + (18 if num else 0) + 156, yy + 6, w - 174, 14, note,
                     "text.secondary", theme, size=7.5))
    return out


def agenda(x, y, w, h, head, note, sections, theme="light", split=0.38):
    """Dark panel left, sectioned agenda right with hollow ticks."""
    out = [r(x, y, w, h, "surface.inverse", theme, radius=5),
           t(x + 18, y + 18, w * split - 36, 40, head, "text.inverse", theme, size=13,
             bold=True, leading=1.15),
           t(x + 18, y + h - 46, w * split - 36, 32, note, "text.inverse", theme,
             size=7.5, leading=1.25)]
    rx = x + w * split + 8
    rw = w - w * split - 26
    sy = y + 12
    for i, (title, items) in enumerate(sections):
        sh = 22 + len(items) * 15
        out.append(r(rx, sy, rw, sh, "surface.raised" if i % 2 else "brand.subtle", theme,
                     radius=3, stroke="border.subtle"))
        out.append(t(rx + 10, sy + 7, rw - 20, 14, title, "text.primary", theme,
                     size=8.5, bold=True))
        out.extend(ticks(rx + 10, sy + 24, rw - 20, sh - 26, items, theme, size=7.5,
                         gap=15))
        sy += sh + 8
    return out


# ------------------------------------------------------------------------ charts
def chart(x, y, w, h, categories, series, kind="bar", theme="light", title=""):
    """Native chart: kind='bar' (clustered columns) or 'line'. Series colours are
    tokens — `chart.series.1..4`. Max four series, legend on top, no data labels."""
    res = A.D.chart(x, y, w, h, categories, series, kind, theme, title)
    return res if isinstance(res, list) else [res]


def waterfall(x, y, w, h, steps, theme="light"):
    """steps: (label, value, kind) with kind in start/up/down/total."""
    out = []
    total = sum(v for _, v, k in steps if k in ("up", "down"))
    base = next((v for _, v, k in steps if k == "start"), 0)
    peak = max(base, base + total) or 1
    cw = w / len(steps)
    bw = cw * 0.56
    run = base
    for i, (name, value, kind) in enumerate(steps):
        cx = x + i * cw + (cw - bw) / 2
        if kind == "start":
            top, height, col = base, base, "chart.series.2"
        elif kind == "total":
            top, height, col = base + total, base + total, "chart.series.1"
        elif kind == "up":
            top, height, col = run + value, value, "chart.series.1"
            run += value
        else:
            run += value
            top, height, col = run, abs(value), "chart.series.3"
        bh = max(3, (height / peak) * (h - 26))
        out.append(r(cx, y + (h - 26) - bh, bw, bh, col, theme, radius=2))
        out.append(t(x + i * cw, y + h - 22, cw, 10, name, "text.secondary", theme,
                     size=6.8, align="center"))
        if kind in ("up", "down"):
            out.append(t(x + i * cw, y + (h - 26) - bh - 12, cw, 11,
                         f"{value:+d}", "text.primary", theme, size=7.5, bold=True,
                         align="center"))
    return out


def donut_row(x, y, w, values, theme="light", d=44, gap=10):
    """Small multiples of donuts: one metric each, label under."""
    out = []
    n = len(values)
    cw = (w - gap * (n - 1)) / n
    for i, (value, name) in enumerate(values):
        out.append(A.donut(x + i * (cw + gap) + (cw - d) / 2, y, d, value, name, theme,
                           SERIES[i % 4]))
    return out


# ---------------------------------------------------------------------- diagrams
def pyramid(x, y, w, h, tiers, theme="light", apex=0.5):
    """Tiers top-down; each row narrows by `apex` of the width."""
    out = []
    n = len(tiers)
    th = h / n
    for i, (name, note) in enumerate(tiers):
        frac = apex + i * ((1 - apex) / max(1, n - 1))
        tw = w * frac
        cx = x + (w - tw) / 2
        cy = y + i * th
        out.append(r(cx, cy + 1, tw, th - 3, "brand.subtle" if i % 2 else "surface.band",
                     theme, radius=3, stroke="border.subtle"))
        out.append(t(cx + 10, cy + th / 2 - 11, tw - 20, 12, name, "text.primary", theme,
                     size=8.5, bold=True, align="center"))
        if note:
            out.append(t(cx + 10, cy + th / 2 + 1, tw - 20, 11, note, "text.secondary",
                         theme, size=6.8, align="center"))
    return out


def twin_pyramid(x, y, w, h, tiers, theme="light", left="Current state",
                 right="Future state", arrow="Pull levers"):
    """Before / after pyramids with a labelled arrow between them."""
    out = []
    pw = w * 0.40
    out.extend(pyramid(x, y, pw, h, tiers, theme, apex=0.52))
    out.extend(pyramid(x + w - pw, y, pw, h, tiers, theme, apex=0.62))
    out.append(t(x, y - 14, pw, 12, left, "text.secondary", theme, size=7.5, bold=True,
                 caps=True, spacing=0.1))
    out.append(t(x + w - pw, y - 14, pw, 12, right, "text.secondary", theme, size=7.5,
                 bold=True, caps=True, spacing=0.1, align="right"))
    ax, aw = x + pw + 12, w - 2 * pw - 24
    out.append(r(ax, y + h / 2 - 1, aw, 2, "brand.primary", theme))
    out.append(r(ax + aw - 6, y + h / 2 - 5, 6, 10, "brand.primary", theme, radius=1))
    out.append(t(ax, y + h / 2 - 18, aw, 12, arrow, "brand.primary", theme, size=7,
                 bold=True, caps=True, spacing=0.1, align="center"))
    return out


def band_stack(x, y, w, h, bands, theme="light", gap=4):
    """Full-width bands, label left / note right — strategy-page skeleton."""
    out = []
    n = len(bands)
    bh = (h - gap * (n - 1)) / n
    for i, (label, note) in enumerate(bands):
        by = y + i * (bh + gap)
        out.append(r(x, by, w, bh, "surface.band" if i % 2 else "brand.subtle", theme,
                     radius=3, stroke="border.subtle"))
        out.append(t(x + 12, by + bh / 2 - 8, w * 0.42, 14, label, "text.primary", theme,
                     size=9, bold=True))
        out.append(t(x + w * 0.46, by + bh / 2 - 7, w * 0.5 - 12, bh - 6, note,
                     "text.secondary", theme, size=7.5, leading=1.25))
    return out


def pillar_framework(x, y, w, h, head, pillars, rows, cells, theme="light"):
    """Head block on top, pillar header row, then rows x pillars grid (ESG form)."""
    out = []
    out.append(r(x, y, w, 26, "brand.primary", theme, radius=3))
    out.append(t(x + 12, y + 7, w - 24, 14, head, "text.on-brand", theme, size=8.5,
                 bold=True, align="center"))
    grid_y = y + 34
    label_w = w * 0.24
    cw = (w - label_w) / len(pillars)
    for i, name in enumerate(pillars):
        out.append(t(x + label_w + i * cw + 8, grid_y, cw - 12, 12, name,
                     "brand.primary", theme, size=8, bold=True, caps=True,
                     spacing=0.1))
    out.append(r(x, grid_y + 14, w, 1, "border.strong", theme))
    rh = (h - 34 - 16) / len(rows)
    for j, name in enumerate(rows):
        ry = grid_y + 16 + j * rh
        if j:
            out.append(r(x, ry, w, 1, "border.subtle", theme))
        out.append(t(x, ry + 6, label_w - 8, rh - 8, name, "text.primary", theme,
                     size=8, bold=True))
        for i in range(len(pillars)):
            txt = cells[j][i] if j < len(cells) and i < len(cells[j]) else ""
            out.append(t(x + label_w + i * cw + 8, ry + 6, cw - 14, rh - 8, txt,
                         "text.secondary", theme, size=7, leading=1.22))
    return out


def concentric(x, y, w, h, center, inner, outer, theme="light"):
    """Three rings: centre claim, three spokes, one outer frame."""
    out = []
    cx, cy = x + w / 2, y + h / 2
    rad = min(w, h) / 2 - 4
    out.append(r(cx - rad, cy - rad, rad * 2, rad * 2, "surface.band", theme,
                 radius=int(rad), stroke="border.default"))
    out.append(r(cx - rad * 0.74, cy - rad * 0.74, rad * 1.48, rad * 1.48,
                 "brand.subtle", theme, radius=int(rad * 0.74), stroke="border.subtle"))
    out.append(r(cx - rad * 0.40, cy - rad * 0.40, rad * 0.80, rad * 0.80,
                 "brand.primary", theme, radius=int(rad * 0.4)))
    out.append(t(cx - rad * 0.4, cy - 6, rad * 0.8, 12, center, "text.on-brand", theme,
                 size=7.5, bold=True, align="center"))
    for i, name in enumerate(inner):
        ang = -90 + i * (360 / max(1, len(inner)))
        import math
        px = cx + math.cos(math.radians(ang)) * rad * 0.58 - 34
        py = cy + math.sin(math.radians(ang)) * rad * 0.58 - 5
        out.append(t(px, py, 68, 10, name, "text.primary", theme, size=6.5, bold=True,
                     align="center"))
    out.append(t(cx - rad, cy - rad - 2, rad * 2, 10, outer, "text.muted", theme,
                 size=6.5, caps=True, spacing=0.1, align="center"))
    return out


def ring_blocks(x, y, w, h, center, items, theme="light"):
    """Four blocks around a centre disc — the 'one firm, four businesses' form."""
    out = []
    cx, cy = x + w / 2, y + h / 2
    bw, bh = w * 0.40, h * 0.34
    spots = [(x, y), (x + w - bw, y), (x, y + h - bh), (x + w - bw, y + h - bh)]
    for i, name in enumerate(items[:4]):
        bx, by = spots[i]
        out.append(r(bx, by, bw, bh, "surface.band", theme, radius=4,
                     stroke="border.subtle"))
        out.append(t(bx + 8, by + bh / 2 - 10, bw - 16, 20, name, "text.primary", theme,
                     size=7.5, bold=True, align="center", leading=1.15))
    d = min(w, h) * 0.30
    out.append(r(cx - d / 2, cy - d / 2, d, d, "brand.primary", theme, radius=int(d / 2)))
    out.append(t(cx - d / 2, cy - 5, d, 10, center, "text.on-brand", theme, size=7,
                 bold=True, align="center"))
    return out


def team_circle(x, y, w, h, center, nodes, theme="light", radius=None):
    """Ring of small nodes around a labelled hub — teams / stakeholders."""
    import math
    out = []
    cx, cy = x + w / 2, y + h / 2
    rad = radius or min(w, h) / 2 - 22
    for i, name in enumerate(nodes):
        ang = -90 + i * (360 / max(1, len(nodes)))
        nx = cx + math.cos(math.radians(ang)) * rad
        ny = cy + math.sin(math.radians(ang)) * rad
        out.append(r(nx - 5, ny - 5, 10, 10, "brand.primary", theme, radius=5))
        out.append(t(nx - 34, ny + 7, 68, 10, name, "text.secondary", theme, size=6.3,
                     align="center"))
    out.append(t(cx - 40, cy - 8, 80, 16, center, "text.primary", theme, size=7.5,
                 bold=True, align="center", leading=1.15))
    return out


def flow_chain(x, y, w, h, steps, theme="light"):
    """Four boxes, arrow between, note under each."""
    out = []
    n = len(steps)
    gap = 10
    bw = (w - gap * (n - 1)) / n
    for i, (name, note) in enumerate(steps):
        bx = x + i * (bw + gap)
        bh = h * 0.88
        out.append(r(bx, y, bw, bh, "surface.raised", theme, radius=4,
                     stroke="border.subtle"))
        out.append(r(bx, y, 2, bh, "brand.primary", theme))
        out.append(t(bx + 10, y + 10, bw - 18, 16, name, "text.primary", theme, size=8.5,
                     bold=True))
        out.append(t(bx + 10, y + 30, bw - 18, bh - 40, note, "text.secondary",
                     theme, size=7, leading=1.25))
        if i < n - 1:
            out.append(t(bx + bw + 2, y + bh / 2 - 8, gap - 2, 14, "\u203a",
                         "brand.primary", theme, size=12, bold=True, align="center"))
    return out


def journey_lane(x, y, w, h, stages, rows, marks, theme="light"):
    """Swimlane: stages across, one lane per channel, markers joined by a path."""
    out = []
    head = 16
    label_w = 46
    cw = (w - label_w) / len(stages)
    lane_h = (h - head) / len(rows)
    for i, name in enumerate(stages):
        out.append(t(x + label_w + i * cw, y, cw - 4, 12, name, "text.secondary", theme,
                     size=7, bold=True, caps=True, spacing=0.08, align="center"))
    for j, name in enumerate(rows):
        ly = y + head + j * lane_h
        out.append(r(x + label_w, ly, w - label_w, lane_h - 2,
                     "surface.band" if j % 2 == 0 else "surface.raised", theme,
                     radius=2))
        out.append(t(x, ly + lane_h / 2 - 5, label_w - 6, 10, name, "text.muted", theme,
                     size=6.5, caps=True, spacing=0.06))
    pts = []
    for stage, row, name in marks:
        cx = x + label_w + stage * cw + cw / 2
        cy = y + head + row * lane_h + lane_h / 2
        pts.append((cx, cy, name))
    for i in range(len(pts) - 1):
        x1, y1, _ = pts[i]
        x2, y2, _ = pts[i + 1]
        if abs(y1 - y2) < 1:
            out.append(r(min(x1, x2), y1 - 1, abs(x2 - x1), 2, "brand.primary", theme))
        else:
            out.append(r(x1 - 1, min(y1, y2), 2, abs(y2 - y1), "brand.primary", theme))
            out.append(r(min(x1, x2), y2 - 1, abs(x2 - x1), 2, "brand.primary", theme))
    for i, (cx, cy, name) in enumerate(pts):
        out.append(r(cx - 5, cy - 5, 10, 10, "brand.primary", theme, radius=5))
        out.append(t(cx - 4, cy - 4, 8, 8, str(i + 1), "text.on-brand", theme, size=5.5,
                     bold=True, align="center"))
        out.append(t(cx - 42, cy + 8, 84, 16, name, "text.secondary", theme, size=5.8,
                     leading=1.1, align="center"))
    return out


def branch(x, y, w, h, left, right, branches, theme="light"):
    """Two diverging stems with two nodes each — 'for brands / for retailers'."""
    out = []
    cx = x + w * 0.18
    out.append(r(cx, y + h / 2 - 3, w * 0.10, 6, "brand.primary", theme, radius=3))
    for bi, (head, nodes) in enumerate(branches):
        sy = y + 12 + h * (0.24 + 0.52 * bi)
        out.append(r(cx + w * 0.10, sy, w * 0.14, 2, "brand.primary", theme))
        out.append(t(x + w * 0.26, sy - 8, 110, 12, head, "text.primary", theme, size=7.5,
                     bold=True, caps=True, spacing=0.08))
        for ni, node in enumerate(nodes):
            nx = x + w * 0.44 + ni * (w * 0.28)
            out.append(r(nx, sy - 26, w * 0.26, 52, "surface.band", theme, radius=3,
                         stroke="border.subtle"))
            out.append(t(nx + 8, sy - 18, w * 0.26 - 16, 40, node, "text.secondary",
                         theme, size=7.2, leading=1.25))
            if ni == 0:
                out.append(r(nx - w * 0.02, sy - 1, w * 0.02, 2, "brand.primary", theme))
    out.append(t(x, y, 90, 10, left, "text.muted", theme, size=6.5, caps=True,
                 spacing=0.1))
    out.append(t(x + w - 90, y, 90, 10, right, "text.muted", theme, size=6.5, caps=True,
                 spacing=0.1, align="right"))
    return out


# ------------------------------------------------------------------------- maps
def map_bubbles(x, y, w, h, points, theme="light", note="placeholder geo"):
    """Proportional-symbol map: frame + bubbles at relative (0-1) coordinates."""
    out = [r(x, y, w, h, "surface.band", theme, radius=4, stroke="border.subtle")]
    for i in range(1, 4):
        out.append(r(x + w * i / 4, y + 6, 1, h - 12, "border.subtle", theme))
        out.append(r(x + 6, y + h * i / 4, w - 12, 1, "border.subtle", theme))
    for name, cx, cy, value, size in points:
        d = size
        bx, by = x + cx * w - d / 2, y + cy * h - d / 2
        out.append(r(bx, by, d, d, "brand.primary", theme, radius=int(d / 2)))
        out.append(t(bx, by + d / 2 - 5, d, 10, value, "text.on-brand", theme, size=6.5,
                     bold=True, align="center"))
        out.append(t(bx - 14, by + d + 1, d + 28, 9, name, "text.muted", theme, size=6,
                     align="center"))
    out.append(t(x + 6, y + h - 11, w - 12, 9, note, "text.muted", theme, size=5.8))
    return out


def map_regions(x, y, w, h, regions, theme="light", note="placeholder geo"):
    """Frame split into labelled regions with a share each (survey footprint)."""
    out = [r(x, y, w, h, "surface.band", theme, radius=4, stroke="border.subtle")]
    n = len(regions)
    bw = (w - 12) / n
    for i, (name, pct, count) in enumerate(regions):
        bx = x + 6 + i * bw
        out.append(r(bx + 2, y + 6, bw - 6, h - 24, "brand.subtle" if i % 2 else
                     "surface.raised", theme, radius=3, stroke="border.subtle"))
        out.append(t(bx + 8, y + 14, bw - 16, 18, f"{pct}%", "brand.primary", theme,
                     size=13, bold=True))
        out.append(t(bx + 8, y + 34, bw - 16, 11, name, "text.primary", theme, size=7.5,
                     bold=True, caps=True, spacing=0.08))
        out.append(t(bx + 8, y + 46, bw - 16, 11, count, "text.muted", theme, size=6.5))
    out.append(t(x + 6, y + h - 11, w - 12, 9, note, "text.muted", theme, size=5.8))
    return out


def before_after(x, y, w, h, left, right, theme="light", note="placeholder geo"):
    """Two map frames side by side with period labels — coverage shift."""
    out = []
    gap = 10
    fw = (w - gap) / 2
    for i, (period, caption) in enumerate((left, right)):
        fx = x + i * (fw + gap)
        out.append(r(fx, y, fw, h - 16, "surface.band", theme, radius=4,
                     stroke="border.subtle"))
        for k in range(1, 4):
            out.append(r(fx + fw * k / 4, y + 4, 1, h - 24, "border.subtle", theme))
        dots = 9 if i else 5
        for k in range(dots):
            dx = fx + 14 + (k % 3) * (fw - 40) / 2.4
            dy = y + 16 + (k // 3) * (h - 52) / 1.6
            out.append(r(dx, dy, 7, 7, "brand.primary", theme, radius=4))
        out.append(t(fx + 8, y + 4, fw - 16, 11, period, "text.primary", theme, size=7.5,
                     bold=True, caps=True, spacing=0.1))
        out.append(t(fx, y + h - 14, fw, 11, caption, "text.muted", theme, size=6.5))
    out.append(t(x, y + h - 2, w, 9, note, "text.muted", theme, size=5.8))
    return out


# ------------------------------------------------- matrices, cards, ranked, hubs
def matrix_header(x, y, w, h, statement, col_labels, row_labels, cells, theme="light",
                  label_w=88, head_h=24):
    """Statement pill on top, then columns x rows grid (the ESG framework form)."""
    out = [r(x, y, w, head_h, "brand.primary", theme, radius=int(head_h / 2)),
           t(x + 16, y + head_h / 2 - 6, w - 32, 12, statement, "text.on-brand", theme,
             size=8.5, bold=True)]
    gy = y + head_h + 12
    cw = (w - label_w) / len(col_labels)
    for i, c in enumerate(col_labels):
        out.append(t(x + label_w + i * cw + 8, gy, cw - 16, 12, c, "brand.primary", theme,
                     size=7.5, bold=True, caps=True, spacing=0.1))
        if i:
            out.append(r(x + label_w + i * cw, gy + 18, 1, h - (gy - y) - 18,
                         "border.subtle", theme))
    out.append(r(x, gy + 18, w, 1, "border.strong", theme))
    rows_y = gy + 24
    rh = (h - (rows_y - y)) / len(row_labels)
    for j, rl in enumerate(row_labels):
        yy = rows_y + j * rh
        if j:
            out.append(r(x, yy, w, 1, "border.subtle", theme))
        out.append(t(x, yy + rh / 2 - 6, label_w - 10, 12, rl, "text.muted", theme,
                     size=7.2, caps=True, spacing=0.08))
        for i, cell in enumerate(cells[j]):
            out.append(t(x + label_w + i * cw + 8, yy + rh / 2 - 12, cw - 16, rh - 8, cell,
                         "text.primary", theme, size=7.6, leading=1.25))
    return out


def benefit_panel(x, y, w, h, items, panel_title, panel_items, theme="light", split=0.60):
    """Rows of benefit + a filled side panel of use cases (smart-contract form)."""
    out = []
    lw = w * split
    rowh = h / len(items)
    for i, (name, desc) in enumerate(items):
        yy = y + i * rowh
        if i:
            out.append(r(x, yy, lw, 1, "border.subtle", theme))
        out.append(r(x, yy + rowh / 2 - 7, 14, 14, "brand.subtle", theme, radius=2,
                     stroke="border.subtle"))
        out.append(t(x + 22, yy + rowh / 2 - 9, lw * 0.30, 14, name, "text.primary", theme,
                     size=7.8, bold=True))
        out.append(t(x + 22 + lw * 0.30, yy + rowh / 2 - 10, lw * 0.70 - lw * 0.30,
                     rowh - 8, desc, "text.secondary", theme, size=7.2, leading=1.25))
    px, pw = x + lw + 16, w - lw - 16
    out.append(r(px, y, pw, h, "brand.primary", theme, radius=4))
    out.append(t(px + 12, y + 10, pw - 24, 26, panel_title, "text.on-brand", theme, size=7.8,
                 bold=True, leading=1.2))
    for i, it in enumerate(panel_items):
        yy = y + 40 + i * ((h - 50) / len(panel_items))
        out.append(t(px + 12, yy, pw - 24, 12, it, "text.on-brand", theme, size=7.2,
                     leading=1.2))
    return out


def country_cards(x, y, w, h, cards, theme="light", cols=3, gap=10):
    """Card grid: country, one-line claim, then metric + signed delta rows."""
    out = []
    rows = math.ceil(len(cards) / cols)
    cw = (w - gap * (cols - 1)) / cols
    ch = (h - gap * (rows - 1)) / rows
    for i, (name, claim, metrics) in enumerate(cards):
        bx = x + (i % cols) * (cw + gap)
        by = y + (i // cols) * (ch + gap)
        out.append(r(bx, by, cw, ch, "surface.raised", theme, radius=4,
                     stroke="border.subtle"))
        out.append(t(bx + 10, by + 8, cw - 20, 12, name, "brand.primary", theme, size=7.2,
                     bold=True, caps=True, spacing=0.1))
        out.append(t(bx + 10, by + 24, cw - 20, 24, claim, "text.primary", theme, size=7,
                     leading=1.2))
        for j, (lab, val, delta) in enumerate(metrics[:3]):
            yy = by + 52 + j * ((ch - 58) / 3)
            out.append(t(bx + 10, yy, cw - 20, 10, lab, "text.muted", theme, size=6.4))
            out.append(t(bx + 10, yy + 10, cw * 0.55, 14, val, "text.primary", theme,
                         size=8.2, bold=True))
            out.append(t(bx + cw * 0.55, yy + 11, cw * 0.45 - 10, 12, delta,
                         "status.success" if delta.startswith("+") else "status.danger",
                         theme, size=7, bold=True, align="right"))
    return out


def ranked_barriers(x, y, w, h, hero, items, theme="light", split=0.34):
    """Hero stat on a band, then a ranked list with highlighted rows."""
    out = []
    lw = w * split
    out.append(r(x, y, lw, h, "surface.band", theme, radius=4, stroke="border.subtle"))
    out.append(t(x + 16, y + 16, lw - 32, 40, hero[0], "brand.primary", theme, size=27,
                 bold=True))
    out.append(t(x + 16, y + 60, lw - 32, h - 74, hero[1], "text.secondary", theme,
                 size=7.6, leading=1.3))
    px, pw = x + lw + 18, w - lw - 18
    rowh = h / len(items)
    for i, (name, hot) in enumerate(items):
        yy = y + i * rowh
        if hot:
            out.append(r(px - 5, yy + 1, pw + 10, rowh - 2, "brand.subtle", theme, radius=2))
        out.append(t(px, yy + rowh / 2 - 7, 22, 12, f"#{i + 1}",
                     "brand.primary" if hot else "text.muted", theme, size=7.4, bold=True))
        out.append(t(px + 24, yy + rowh / 2 - 9, pw - 24, rowh - 6, name, "text.primary",
                     theme, size=7.6, leading=1.2))
        if i < len(items) - 1:
            out.append(r(px, yy + rowh - 1, pw, 1, "border.subtle", theme))
    return out


def segment_split(x, y, w, h, segments, theme="light", note=None):
    """One proportional bar, share above, segment name below."""
    out = [t(x, y, w, 10, "SEGMEN", "text.muted", theme, size=6.6, caps=True,
              spacing=0.1)]
    bar_y, barh = y + h * 0.34, 18
    bx, total = x, sum(p for _, p in segments)
    for i, (name, pct) in enumerate(segments):
        sw = w * pct / total
        out.append(r(bx, bar_y, max(sw - 2, 4), barh, SERIES[i % 4], theme, radius=2))
        out.append(t(bx, bar_y - 15, max(sw - 2, 34), 12, f"{pct:.0f}%", "text.primary",
                     theme, size=8, bold=True))
        out.append(t(bx, bar_y + barh + 7, max(sw - 2, 58), 26, name, "text.secondary",
                     theme, size=6.8, leading=1.15))
        bx += sw
    if note:
        out.append(t(x, bar_y + barh + 44, w, h - (bar_y - y) - barh - 44, note,
                     "text.muted", theme, size=7, leading=1.25))
    return out


def twin_hub(x, y, w, h, left, right, theme="light", caption_h=30):
    """Two hub diagrams side by side: before/after role of the centre."""
    out = []
    cw = (w - 16) / 2
    for k, (center, sats, foot, note) in enumerate((left, right)):
        ox, oy = x + k * (cw + 16), y
        ch = h - caption_h
        cx, cy = ox + cw / 2, oy + ch / 2
        rad = min(cw, ch) * 0.19
        out.append(r(cx - rad, cy - rad, rad * 2, rad * 2, "brand.primary", theme,
                     radius=int(rad)))
        out.append(t(cx - rad + 4, cy - 6, rad * 2 - 8, 12, center, "text.on-brand", theme,
                     size=6.8, bold=True, align="center"))
        n = len(sats)
        for i, name in enumerate(sats):
            ang = -math.pi / 2 + 2 * math.pi * i / n
            sx = cx + math.cos(ang) * cw * 0.36
            sy = cy + math.sin(ang) * ch * 0.38
            out.append(r(sx - 31, sy - 9, 62, 18, "surface.band", theme, radius=2,
                         stroke="border.subtle"))
            out.append(t(sx - 29, sy - 5, 58, 10, name, "text.primary", theme, size=6,
                         align="center"))
            out.append(r(cx + math.cos(ang) * rad * 1.08 - 1.5,
                         cy + math.sin(ang) * rad * 1.08 - 1.5, 3, 3, "brand.primary",
                         theme, radius=1))
        out.append(t(ox, oy + ch + 2, cw, 12, foot, "text.muted", theme, size=6.8,
                     caps=True, spacing=0.08, align="center"))
        out.append(t(ox, oy + ch + 14, cw, caption_h - 14, note, "text.secondary", theme,
                     size=6.8, align="center", leading=1.2))
    return out


def quad_actions(x, y, w, h, items, theme="light", gap=10):
    """Four numbered actions in a 2x2 of filled blocks."""
    out = []
    cw, ch = (w - gap) / 2, (h - gap) / 2
    for i, (num, name, body) in enumerate(items[:4]):
        bx = x + (i % 2) * (cw + gap)
        by = y + (i // 2) * (ch + gap)
        out.append(r(bx, by, cw, ch, "brand.primary", theme, radius=4))
        out.append(t(bx + 14, by + 10, cw - 28, 16, num, "text.on-brand", theme, size=11,
                     bold=True))
        out.append(t(bx + 14, by + 30, cw - 28, 28, name, "text.on-brand", theme, size=8.2,
                     bold=True, leading=1.2))
        out.append(t(bx + 14, by + 62, cw - 28, ch - 70, body, "text.on-brand", theme,
                     size=7.2, leading=1.3))
    return out


def orbit_ring(x, y, w, h, center, items, theme="light"):
    """Seven topics orbiting one statement — the institute-overview form."""
    out = []
    cx, cy = x + w / 2, y + h / 2
    rad = min(w * 0.22, h * 0.26)
    out.append(r(cx - rad, cy - rad, rad * 2, rad * 2, "brand.primary", theme,
                 radius=int(rad)))
    out.append(t(cx - rad * 0.74, cy - 16, rad * 1.48, 32, center, "text.on-brand", theme,
                 size=8, bold=True, align="center", leading=1.2))
    n = len(items)
    for i, (name, desc) in enumerate(items):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        bx = cx + math.cos(ang) * w * 0.40 - 66
        by = cy + math.sin(ang) * h * 0.42 - 14
        out.append(t(bx, by, 132, 12, name, "text.primary", theme, size=7, bold=True,
                     align="center"))
        out.append(t(bx, by + 12, 132, 22, desc, "text.secondary", theme, size=6.2,
                     align="center", leading=1.15))
        out.append(r(cx + math.cos(ang) * rad * 1.10 - 1.5,
                     cy + math.sin(ang) * rad * 1.10 - 1.5, 3, 3, "brand.primary", theme,
                     radius=1))
    return out


# ------------------------------------- architectures, cycles, node grids, compare
def channel_arch(x, y, w, h, channels, brand, products, legend, theme="light"):
    """Acquisition channels on top, brand in the middle, product stack with strategy chips."""
    out = []
    n = len(channels)
    gap = 8
    cw = (w - gap * (n - 1)) / n
    for i, c in enumerate(channels):
        bx = x + i * (cw + gap)
        out.append(r(bx, y, cw, 26, "surface.raised", theme, radius=3,
                     stroke="border.subtle"))
        out.append(t(bx + 5, y + 4, cw - 10, 18, c, "text.primary", theme, size=6.4,
                     align="center", leading=1.15))
        out.append(r(bx + cw / 2 - 0.5, y + 26, 1, 12, "border.strong", theme))
    out.append(r(x + w * 0.20, y + 38, w * 0.60, 22, "brand.primary", theme, radius=3))
    out.append(t(x + w * 0.20, y + 43, w * 0.60, 14, brand, "text.on-brand", theme,
                 size=8.5, bold=True, align="center"))
    py = y + 70
    ph = h - (py - y) - 24
    pw = (w - gap * (len(products) - 1)) / len(products)
    for i, (name, strat) in enumerate(products):
        bx = x + i * (pw + gap)
        out.append(r(bx, py, pw, ph, "surface.raised", theme, radius=3,
                     stroke="border.subtle"))
        out.append(t(bx + 4, py + 8, pw - 8, 22, name, "text.primary", theme, size=7.2,
                     bold=True, align="center", leading=1.15))
        out.append(r(bx, py + ph - 16, pw, 16, SERIES[i % 4], theme, radius=2))
        out.append(t(bx, py + ph - 13, pw, 12, strat, "text.on-brand", theme, size=6.2,
                     bold=True, caps=True, align="center"))
    ly = y + h - 14
    lx = x
    for i, lab in enumerate(legend):
        out.append(r(lx, ly + 3, 7, 7, SERIES[i % 4], theme, radius=1))
        out.append(t(lx + 11, ly, 70, 10, lab, "text.muted", theme, size=6.4))
        lx += 76
    return out


def geo_columns(x, y, w, h, stats, regions, theme="light"):
    """Stat column on the left, then one map block + bullets per region."""
    out = []
    sw = w * 0.24
    rowh = (h - 8) / len(stats)
    for i, (lab, val) in enumerate(stats):
        yy = y + i * rowh
        out.append(t(x, yy, sw - 10, 10, lab, "text.muted", theme, size=6.4, caps=True,
                     spacing=0.08))
        out.append(t(x, yy + 10, sw - 10, 14, val, "text.primary", theme, size=9,
                     bold=True))
        out.append(r(x, yy + rowh - 3, sw - 10, 1, "border.subtle", theme))
    cw = (w - sw - 16) / len(regions)
    for k, (name, claim, items) in enumerate(regions):
        bx = x + sw + 16 + k * cw
        out.append(t(bx, y, cw - 10, 12, name, "brand.primary", theme, size=7.4, bold=True,
                     caps=True, spacing=0.1))
        out.append(t(bx, y + 14, cw - 10, 26, claim, "text.secondary", theme, size=6.8,
                     leading=1.2))
        out.append(r(bx, y + 44, cw - 12, h * 0.38, "surface.band", theme, radius=3,
                     stroke="border.subtle"))
        out.append(t(bx + 6, y + 44 + h * 0.19 - 5, cw - 24, 10, "placeholder geo",
                     "text.muted", theme, size=6, align="center"))
        for j, it in enumerate(items):
            yy = y + 48 + h * 0.38 + j * 13
            out.append(r(bx, yy + 4, 4, 4, "brand.primary", theme, radius=1))
            out.append(t(bx + 10, yy, cw - 20, 13, it, "text.secondary", theme, size=6.4,
                         leading=1.15))
    return out


def node_grid(x, y, w, h, hero, items, bands, theme="light", per_row=5):
    """Hero number, then two labelled bands of round nodes (the 10-theme form)."""
    out = []
    out.append(t(x, y, w * 0.5, 40, hero[0], "brand.primary", theme, size=26, bold=True))
    out.append(t(x, y + 40, w * 0.5, 14, hero[1], "text.secondary", theme, size=7.4))
    gy = y + 62
    rows = [items[:per_row], items[per_row:per_row * 2]]
    band_h = 14
    for b, row in enumerate(rows):
        by = gy + b * ((h - 62) / 2)
        if b < len(bands):
            out.append(t(x, by, w, band_h, bands[b], "text.muted", theme, size=6.4,
                         caps=True, spacing=0.12))
        cell = w / per_row
        d = min(cell - 12, ((h - 62) / 2) - 26)
        for i, name in enumerate(row):
            cx = x + i * cell + cell / 2
            cy = by + 20 + d / 2
            out.append(r(cx - d / 2, cy - d / 2, d, d, "surface.raised", theme,
                         radius=int(d / 2), stroke="brand.primary"))
            out.append(t(cx - d / 2 + 5, cy - 11, d - 10, 22, name, "text.primary", theme,
                         size=6.2, align="center", leading=1.15))
    return out


def cycle_checklist(x, y, w, h, cycle, checks, risks, stats, theme="light"):
    """Three-step loop on the left, checklist under it, risk chips right, stats at foot."""
    out = []
    lw = w * 0.44
    cx, cy = x + lw / 2, y + h * 0.26
    rad = min(lw, h * 0.5) * 0.14
    out.append(r(cx - rad * 2.6, cy - rad * 2.6, rad * 5.2, rad * 5.2, "surface.base",
                 theme, radius=int(rad * 2.6), stroke="border.subtle"))
    for i, name in enumerate(cycle[:3]):
        ang = -math.pi / 2 + 2 * math.pi * i / 3
        nx, ny = cx + math.cos(ang) * rad * 2.15, cy + math.sin(ang) * rad * 2.15
        out.append(r(nx - rad, ny - rad, rad * 2, rad * 2, "brand.primary", theme,
                     radius=int(rad)))
        out.append(t(nx - rad, ny - 9, rad * 2, 18, str(i + 1), "text.on-brand", theme,
                     size=10, bold=True, align="center"))
        out.append(t(nx - rad * 1.8, ny + rad + 4, rad * 3.6, 20, name, "text.primary",
                     theme, size=6.4, bold=True, align="center", leading=1.15))
    out.append(t(cx - 30, cy - 5, 60, 10, "INTI", "text.muted", theme, size=6, caps=True,
                 align="center"))
    cy2 = y + h * 0.56
    for i, c in enumerate(checks):
        yy = cy2 + i * 14
        out.append(r(x, yy + 4, 6, 6, "surface.base", theme, radius=1,
                     stroke="brand.primary"))
        out.append(t(x + 12, yy, lw - 14, 14, c, "text.secondary", theme, size=6.6,
                     leading=1.15))
    rx, rw = x + lw + 16, w - lw - 16
    out.append(t(rx, y, rw, 10, "JENIS RISIKO", "text.muted", theme, size=6.4, caps=True,
                 spacing=0.1))
    cols = 3
    cw = (rw - 6 * (cols - 1)) / cols
    for i, rk in enumerate(risks):
        bx = rx + (i % cols) * (cw + 6)
        by = y + 16 + (i // cols) * 22
        out.append(r(bx, by, cw, 18, "surface.raised", theme, radius=2,
                     stroke="border.subtle"))
        out.append(t(bx + 3, by + 4, cw - 6, 12, rk, "text.primary", theme, size=6.2,
                     align="center"))
    sy = y + h - 26
    out.append(r(rx, sy, rw, 1, "border.strong", theme))
    stw = rw / len(stats)
    for i, (val, lab) in enumerate(stats):
        bx = rx + i * stw
        out.append(t(bx, sy + 4, stw - 8, 14, val, "brand.primary", theme, size=8.5,
                     bold=True))
        out.append(t(bx, sy + 17, stw - 8, 10, lab, "text.muted", theme, size=6,
                     leading=1.1))
    return out


def diamond_columns(x, y, w, h, segments, columns, theme="light"):
    """Four segments on a diamond, three supporting columns to the right."""
    out = []
    dw = w * 0.36
    cx, cy = x + dw / 2, y + h / 2
    bw, bh = dw * 0.46, 22
    spots = [(0, -1), (-1, 0), (1, 0), (0, 1)]
    for i, seg in enumerate(segments[:4]):
        dx, dy = spots[i]
        bx = cx + dx * (dw * 0.22) - bw / 2
        by = cy + dy * (h * 0.30) - bh / 2
        out.append(r(bx, by, bw, bh, "brand.primary" if i == 0 else "surface.raised",
                     theme, radius=2, stroke="border.subtle"))
        out.append(t(bx + 4, by + 5, bw - 8, 12, seg,
                     "text.on-brand" if i == 0 else "text.primary", theme, size=6.2,
                     bold=True, align="center", leading=1.1))
    px, pw = x + dw + 12, w - dw - 12
    cw = (pw - 10 * (len(columns) - 1)) / len(columns)
    for k, (title, items) in enumerate(columns):
        bx = px + k * (cw + 10)
        out.append(t(bx, y, cw, 12, title, "brand.primary", theme, size=7, bold=True,
                     caps=True, spacing=0.08))
        out.append(r(bx, y + 16, cw, 1, "border.strong", theme))
        for j, it in enumerate(items):
            yy = y + 24 + j * ((h - 24) / len(items))
            out.append(t(bx, yy, cw, 12, it, "text.secondary", theme, size=6.8,
                         leading=1.2))
            if j < len(items) - 1:
                out.append(r(bx, yy + (h - 24) / len(items) - 4, cw, 1, "border.subtle",
                             theme))
    return out


def platform_rows(x, y, w, h, rows, theme="light"):
    """Row label on the left, logo placeholders + metric chips on the right."""
    out = []
    lw = w * 0.30
    for i, (name, logos, metrics) in enumerate(rows):
        yy = y + i * (h / len(rows))
        rh = h / len(rows)
        if i:
            out.append(r(x, yy, w, 1, "border.subtle", theme))
        out.append(t(x, yy + 8, lw - 12, rh - 12, name, "text.primary", theme, size=7.4,
                     bold=True, leading=1.2))
        cell = (w - lw) / logos
        for j in range(logos):
            bx = x + lw + j * cell
            out.append(r(bx + 4, yy + 8, cell - 14, 26, "surface.raised", theme,
                         radius=2, stroke="border.subtle"))
            out.append(t(bx + 6, yy + 17, cell - 18, 10, "LOGO", "text.muted", theme,
                         size=5.8, caps=True, align="center", spacing=0.1))
            if j < len(metrics) and metrics[j]:
                out.append(t(bx + 4, yy + 38, cell - 12, 12, metrics[j], "brand.primary",
                             theme, size=7, bold=True))
    return out


def stages_compare(x, y, w, h, stages, practice, examples, theme="light", split=0.42):
    """Stage rows on the left, best practice vs example columns to the right."""
    out = []
    lw = w * 0.26
    ew = (w - lw) / 2
    out.append(t(x, y, lw, 10, "TAHAP", "text.muted", theme, size=6.2, caps=True,
                 spacing=0.1))
    for k, hd in enumerate(("PRAKTIK TERBAIK", "CONTOH: AS / PRANCIS")):
        out.append(t(x + lw + k * ew, y, ew - 10, 10, hd, "brand.primary", theme,
                     size=6.2, bold=True, caps=True, spacing=0.1))
    out.append(r(x, y + 14, w, 1, "border.strong", theme))
    ry = y + 20
    rowh = (h - (ry - y)) / len(stages)
    for i, st in enumerate(stages):
        yy = ry + i * rowh
        if i:
            out.append(r(x, yy, w, 1, "border.subtle", theme))
        out.append(t(x, yy + 4, lw - 10, rowh - 8, st, "text.primary", theme, size=7.2,
                     bold=True, leading=1.2))
        out.append(t(x + lw, yy + 4, ew - 10, rowh - 8, practice[i], "text.secondary",
                     theme, size=6.6, leading=1.25))
        out.append(t(x + lw + ew, yy + 4, ew - 10, rowh - 8, examples[i], "text.secondary",
                     theme, size=6.6, leading=1.25))
    return out


def three_col_progress(x, y, w, h, headers, rows, band, theme="light", band_h=26):
    """Three columns of paired cells, then a full-width closing band."""
    out = []
    cw = w / len(headers)
    for i, hd in enumerate(headers):
        out.append(t(x + i * cw, y, cw - 10, 10, hd, "brand.primary", theme, size=6.6,
                     bold=True, caps=True, spacing=0.1))
    out.append(r(x, y + 14, w, 1, "border.strong", theme))
    ry = y + 20
    rh = (h - (ry - y) - band_h - 10) / len(rows)
    for i, row in enumerate(rows):
        yy = ry + i * rh
        if i:
            out.append(r(x, yy, w, 1, "border.subtle", theme))
        for j, cell in enumerate(row):
            out.append(t(x + j * cw + 2, yy + 4, cw - 14, rh - 8, cell,
                         "text.primary" if j == 0 else "text.secondary", theme,
                         size=7.2 if j == 0 else 6.8, bold=(j == 0), leading=1.25))
    by = y + h - band_h
    out.append(r(x, by, w, band_h, "status.danger", theme, radius=3))
    out.append(t(x + 12, by + band_h / 2 - 6, w - 24, 12, band, "text.on-brand", theme,
                 size=8, bold=True))
    return out


# ------------------------------- wealth bands, levers, paired bars, meters
def wealth_bands(x, y, w, h, bands, axis, theme="light"):
    """Stacked client bands: name + note, two market sizes, share badge, service axis."""
    out = []
    ah = 20
    bh = (h - ah - 4) / len(bands)
    for i, (name, note, size_a, size_b, share) in enumerate(bands):
        by = y + i * bh
        if i:
            out.append(r(x, by, w, 1, "border.subtle", theme))
        out.append(t(x, by + 8, w * 0.32, 12, name, "text.primary", theme, size=8.4,
                     bold=True))
        out.append(t(x, by + 22, w * 0.32, bh - 26, note, "text.muted", theme, size=6.6,
                     leading=1.2))
        mx = x + w * 0.34
        for j, (val, cap) in enumerate(((size_a, "pasar total"), (size_b, "pasar sasaran"))):
            out.append(t(mx + j * (w * 0.16), by + 10, w * 0.15, 14, val, "brand.primary",
                         theme, size=9.5, bold=True))
            out.append(t(mx + j * (w * 0.16), by + 26, w * 0.15, 10, cap, "text.muted",
                         theme, size=6, caps=True, spacing=0.06))
        sw = w * 0.10
        out.append(r(x + w - sw, by + bh / 2 - 11, sw, 22, "surface.band", theme, radius=11))
        out.append(t(x + w - sw, by + bh / 2 - 6, sw, 12, share, "text.primary", theme,
                     size=8, bold=True, align="center"))
    ay = y + h - ah
    out.append(r(x, ay, w, 1, "border.strong", theme))
    out.append(t(x, ay + 5, w * 0.3, 10, axis[0], "text.muted", theme, size=6.2, caps=True,
                 spacing=0.08))
    out.append(t(x + w * 0.35, ay + 5, w * 0.3, 10, axis[1], "text.muted", theme, size=6.2,
                 caps=True, spacing=0.08, align="center"))
    out.append(t(x + w * 0.7, ay + 5, w * 0.3, 10, axis[2], "text.muted", theme, size=6.2,
                 caps=True, spacing=0.08, align="right"))
    return out


def levers_rows(x, y, w, h, rows, theme="light", reason_w=0.30):
    """Numbered lever rows: title + actions on the left, why-it-matters on the right."""
    out = []
    rw = w * reason_w
    lw = w - rw - 16
    rowh = h / len(rows)
    out.append(t(x, y - 12, lw, 10, "LEVER", "text.muted", theme, size=6.2, caps=True,
                 spacing=0.1))
    out.append(t(x + w - rw, y - 12, rw, 10, "ALASAN", "text.muted", theme, size=6.2,
                 caps=True, spacing=0.1))
    for i, (name, actions, reason) in enumerate(rows):
        yy = y + i * rowh
        if i:
            out.append(r(x, yy, w, 1, "border.subtle", theme))
        out.append(r(x, yy + 10, 18, 18, "brand.primary", theme, radius=9))
        out.append(t(x, yy + 14, 18, 12, str(i + 1), "text.on-brand", theme, size=7.5,
                     bold=True, align="center"))
        out.append(t(x + 26, yy + 8, lw - 26, 13, name, "text.primary", theme, size=7.8,
                     bold=True))
        out.append(t(x + 26, yy + 22, lw - 26, rowh - 26, actions, "text.secondary", theme,
                     size=6.6, leading=1.25))
        out.append(t(x + w - rw, yy + 8, rw, rowh - 12, reason, "text.secondary", theme,
                     size=6.6, leading=1.25))
    return out


def paired_bars(x, y, w, h, groups, legend, theme="light", label_w=0.30):
    """Grouped horizontal bars: baseline series in series.4, accent series in brand."""
    out = []
    lx, bw = x, w * label_w
    out.append(r(lx, y + 4, 7, 7, "chart.series.4", theme, radius=1))
    out.append(t(lx + 11, y + 1, 90, 10, legend[0], "text.muted", theme, size=6.4))
    out.append(r(lx + 110, y + 4, 7, 7, "brand.primary", theme, radius=1))
    out.append(t(lx + 121, y + 1, 90, 10, legend[1], "text.muted", theme, size=6.4))
    gy = y + 20
    blocks = len(groups)
    rows_total = sum(len(g[1]) for g in groups)
    avail = h - 20 - blocks * 14
    rh = avail / rows_total
    barh = min(7, rh * 0.30)
    cx = lx + bw
    cw = w - bw
    for gname, items in groups:
        out.append(t(lx, gy, w, 12, gname, "brand.primary", theme, size=6.6, bold=True,
                     caps=True, spacing=0.1))
        gy += 14
        for name, without, withgen in items:
            out.append(t(lx, gy + 2, bw - 10, 12, name, "text.secondary", theme, size=6.6))
            out.append(r(cx, gy + 1, max(2, cw * without / 100), barh, "chart.series.4",
                         theme, radius=2))
            out.append(r(cx, gy + 1 + barh + 2, max(2, cw * withgen / 100), barh,
                         "brand.primary", theme, radius=2))
            out.append(t(cx + cw * withgen / 100 + 4, gy + 1 + barh + 1, 26, 10,
                         f"{withgen}", "text.primary", theme, size=6, bold=True))
            gy += rh
    return out


def meter_grid(x, y, w, h, items, theme="light", cols=3):
    """Big percentage + track meter + caption, in a grid. items: (pct, title, note)."""
    out = []
    rows = math.ceil(len(items) / cols)
    cw = w / cols
    ch = h / rows
    for i, (pct, title, note) in enumerate(items):
        bx = x + (i % cols) * cw
        by = y + (i // cols) * ch
        col = SERIES[i % 3]
        out.append(t(bx, by, cw - 14, 26, f"{pct}%", col, theme, size=20, bold=True))
        out.append(t(bx, by + 28, cw - 14, 12, title, "text.primary", theme, size=7.2,
                     bold=True))
        out.append(r(bx, by + 44, cw - 16, 5, "surface.band", theme, radius=2))
        out.append(r(bx, by + 44, max(2, (cw - 16) * pct / 100), 5, col, theme, radius=2))
        out.append(t(bx, by + 54, cw - 14, ch - 56, note, "text.muted", theme, size=6.2,
                     leading=1.2))
    return out


def grouped_hbar(x, y, w, h, groups, theme="light", total=None, label_w=0.34):
    """Horizontal bars grouped under subheads, value at the bar end, optional total."""
    out = []
    lx, bw = x, w * label_w
    cw = w - bw
    blocks = len(groups)
    rows = sum(len(g[1]) for g in groups)
    avail = h - (14 * blocks) - (22 if total else 0)
    rh = avail / rows
    barh = min(9, rh * 0.42)
    peak = max(v for _, items in groups for _, v in items) or 1
    gy = y
    for gname, items in groups:
        out.append(t(lx, gy, w, 12, gname, "brand.primary", theme, size=6.6, bold=True,
                     caps=True, spacing=0.1))
        gy += 14
        for name, val in items:
            out.append(t(lx, gy + (rh - 12) / 2, bw - 12, 12, name, "text.secondary",
                         theme, size=6.6))
            out.append(r(lx + bw, gy + (rh - barh) / 2, max(2, cw * 0.86 * val / peak),
                         barh, SERIES[0], theme, radius=2))
            out.append(t(lx + bw + cw * 0.86 * val / peak + 4, gy + (rh - 10) / 2, 40, 10,
                         f"{val:,}".replace(",", "."), "text.primary", theme, size=6.4,
                         bold=True))
            gy += rh
    if total:
        ty = y + h - 20
        out.append(r(x, ty - 6, w, 1, "border.strong", theme))
        out.append(t(lx, ty, bw, 12, total[0], "text.primary", theme, size=7.2, bold=True))
        out.append(t(lx + bw, ty, cw, 12, total[1], "text.primary", theme, size=7.2,
                     bold=True))
    return out


def diverging_bars(x, y, w, h, rows, heads, theme="light"):
    """Back-to-back bars from a centre axis: left = exit, right = stay."""
    out = []
    lw = w * 0.30
    cx = x + lw + (w - lw) / 2
    half = (w - lw) / 2 - 12
    out.append(t(x, y, lw, 10, heads[2], "text.muted", theme, size=6.2, caps=True,
                 spacing=0.1))
    out.append(t(cx - half, y, half, 10, heads[0], "text.muted", theme, size=6.2, caps=True,
                 spacing=0.1, align="right"))
    out.append(t(cx, y, half, 10, heads[1], "text.muted", theme, size=6.2, caps=True,
                 spacing=0.1))
    out.append(r(x, y + 12, w, 1, "border.strong", theme))
    ry = y + 18
    rowh = (h - (ry - y)) / len(rows)
    peak = max(max(a, b) for _, a, b, _ in rows) or 1
    barh = min(14, rowh * 0.46)
    for i, (name, left, right, note) in enumerate(rows):
        yy = ry + i * rowh
        if i:
            out.append(r(x, yy, w, 1, "border.subtle", theme))
        out.append(t(x, yy + (rowh - 12) / 2, lw - 10, 12, name, "text.primary", theme,
                     size=7, bold=True))
        lb = max(2, half * left / peak)
        rb = max(2, half * right / peak)
        by = yy + (rowh - barh) / 2
        out.append(r(cx - lb, by, lb, barh, "brand.primary", theme, radius=2))
        out.append(r(cx, by, rb, barh, "chart.series.4", theme, radius=2))
        out.append(t(cx - lb - 30, by + barh / 2 - 5, 26, 10, str(left), "text.primary",
                     theme, size=6.6, bold=True, align="right"))
        out.append(t(cx + rb + 4, by + barh / 2 - 5, 30, 10, str(right), "text.primary",
                     theme, size=6.6, bold=True))
        if note:
            out.append(t(cx + rb + 34, by + barh / 2 - 5, 60, 10, note, "text.muted", theme,
                         size=6))
    return out


def driver_bars(x, y, w, h, drivers, totals, theme="light"):
    """Driver decomposition: winners above the baseline, laggards below."""
    out = []
    top_max = max(v for _, v, _ in drivers if v > 0) or 1
    bot_max = max(abs(v) for _, _, v in drivers if v < 0) or 1
    peak = max(top_max, bot_max)
    cw = w / (len(drivers) + 1)
    bw = cw * 0.58
    plot = h - 18
    mid = y + plot / 2
    out.append(r(x, mid, w, 1, "border.strong", theme))
    for i, (name, up, down) in enumerate(drivers):
        bx = x + i * cw + (cw - bw) / 2
        if up:
            bh = (up / peak) * (plot / 2 - 30)
            out.append(r(bx, mid - bh, bw, bh, "brand.primary", theme, radius=2))
            out.append(t(bx - 4, mid - bh - 13, bw + 8, 11, f"+{up}", "text.primary", theme,
                         size=7, bold=True, align="center"))
        if down:
            bh = (abs(down) / peak) * (plot / 2 - 30)
            out.append(r(bx, mid, bw, bh, "chart.series.4", theme, radius=2))
            out.append(t(bx - 4, mid + bh + 2, bw + 8, 11, f"{down}", "text.primary",
                         theme, size=7, bold=True, align="center"))
        out.append(t(bx - 10, y + plot + 2, bw + 20, 12, name, "text.muted", theme,
                     size=6.2, align="center", leading=1.1))
    tx = x + len(drivers) * cw + (cw - bw) / 2
    for val, col in ((totals[0], "brand.primary"), (totals[1], "chart.series.4")):
        bh = (abs(val) / peak) * (plot / 2 - 30)
        if val > 0:
            out.append(r(tx, mid - bh, bw, bh, col, theme, radius=2))
            out.append(t(tx - 4, mid - bh - 13, bw + 8, 11, f"+{val}", "text.primary",
                         theme, size=7.5, bold=True, align="center"))
        else:
            out.append(r(tx, mid, bw, bh, col, theme, radius=2))
            out.append(t(tx - 4, mid + bh + 2, bw + 8, 11, f"{val}", "text.primary", theme,
                         size=7.5, bold=True, align="center"))
    out.append(t(tx - 10, y + plot + 2, bw + 20, 12, "TOTAL", "text.primary", theme,
                 size=6.6, bold=True, align="center"))
    return out


def pillar_targets(x, y, w, h, pillars, theme="light", pill_h=30):
    """Three (or more) pillars: header, bullet list, target pill at the foot."""
    out = []
    gap = 10
    cw = (w - gap * (len(pillars) - 1)) / len(pillars)
    for i, (name, note, items, target) in enumerate(pillars):
        bx = x + i * (cw + gap)
        out.append(r(bx, y, cw, h, "surface.raised", theme, radius=4,
                     stroke="border.subtle"))
        out.append(r(bx, y, cw, 26, "brand.primary", theme, radius=4))
        out.append(t(bx + 8, y + 7, cw - 16, 13, name, "text.on-brand", theme, size=8,
                     bold=True))
        out.append(t(bx + 10, y + 34, cw - 20, 24, note, "text.muted", theme, size=6.4,
                     leading=1.2))
        for j, it in enumerate(items):
            yy = y + 62 + j * 15
            out.append(r(bx + 10, yy + 4, 4, 4, "brand.primary", theme, radius=1))
            out.append(t(bx + 18, yy, cw - 28, 14, it, "text.secondary", theme, size=6.6,
                         leading=1.15))
        ty = y + h - pill_h - 8
        out.append(r(bx + 10, ty, cw - 20, pill_h, "surface.band", theme, radius=3))
        out.append(t(bx + 14, ty + 5, cw - 28, pill_h - 8, target, "text.primary", theme,
                     size=7, bold=True, leading=1.2))
    return out


# ------------- loop + columns, shift columns, percent columns, opportunity track
def loop_columns(x, y, w, h, loop, mid, infra, theme="light"):
    """Left: closed-loop hub. Middle: value points. Right: shared infrastructure checks."""
    out = []
    lw = w * 0.34
    mw = w * 0.31
    iw = w - lw - mw - 20
    cx, cy = x + lw / 2, y + h / 2 - 6
    rad = min(lw, h) * 0.13
    for i, (name, note) in enumerate(loop):
        ang = -math.pi / 2 + i * (2 * math.pi / len(loop))
        nx, ny = cx + math.cos(ang) * rad * 2.55, cy + math.sin(ang) * rad * 2.55
        out.append(r(nx - rad * 1.05, ny - rad * 0.5, rad * 2.1, rad * 1.0, "surface.raised",
                     theme, radius=3, stroke="border.strong"))
        out.append(t(nx - rad * 1.0, ny - rad * 0.36, rad * 2.0, rad * 0.72, name,
                     "text.primary", theme, size=6.4, bold=True, align="center", leading=1.1))
    out.append(r(cx - rad * 1.2, cy - rad * 0.55, rad * 2.4, rad * 1.1, "brand.primary",
                 theme, radius=3))
    out.append(t(cx - rad * 1.12, cy - rad * 0.34, rad * 2.24, rad * 0.68, "Wholesale payments",
                 "text.on-brand", theme, size=6.6, bold=True, align="center", leading=1.1))
    mx = x + lw + 10
    out.append(r(mx - 6, y, 1, h, "border.subtle", theme))
    for i, (name, note) in enumerate(mid):
        yy = y + i * (h / len(mid))
        out.append(r(mx + 4, yy + 4, 14, 14, "brand.primary", theme, radius=7))
        out.append(t(mx + 4, yy + 7, 14, 10, str(i + 1), "text.on-brand", theme, size=6.4,
                     bold=True, align="center"))
        out.append(t(mx + 24, yy + 2, mw - 34, 12, name, "text.primary", theme, size=7,
                     bold=True))
        out.append(t(mx + 24, yy + 16, mw - 34, h / len(mid) - 20, note, "text.muted",
                     theme, size=6.2, leading=1.2))
    ix = mx + mw + 10
    out.append(r(ix - 6, y, 1, h, "border.subtle", theme))
    out.append(t(ix + 4, y - 12, iw, 10, "Infrastruktur bersama", "text.muted", theme,
                 size=6.2, caps=True, spacing=0.08))
    for i, it in enumerate(infra):
        yy = y + i * ((h - 6) / len(infra))
        out.append(r(ix + 4, yy + 5, 8, 8, "brand.primary", theme, radius=2))
        out.append(t(ix + 18, yy, iw - 20, 12, it, "text.secondary", theme, size=6.6,
                     leading=1.2))
    return out


def shift_columns(x, y, w, h, cols, theme="light"):
    """Columns of before/after/result: (head, note, items, tone) with hairline separators."""
    out = []
    gap = 12
    cw = (w - gap * (len(cols) - 1)) / len(cols)
    for i, (head, note, items, tone) in enumerate(cols):
        bx = x + i * (cw + gap)
        out.append(r(bx, y, cw, 3, "brand.primary" if tone == "accent" else "border.strong",
                     theme))
        out.append(t(bx, y + 10, cw, 14, head, "text.primary", theme, size=8.2, bold=True))
        out.append(t(bx, y + 26, cw, 24, note, "text.muted", theme, size=6.4, leading=1.2))
        for j, it in enumerate(items):
            yy = y + 54 + j * ((h - 60) / len(items))
            out.append(r(bx, yy + 4, 4, 4, "brand.primary", theme, radius=1))
            out.append(t(bx + 10, yy, cw - 14, (h - 60) / len(items) - 4, it,
                         "text.secondary", theme, size=6.6, leading=1.2))
    return out


def percent_columns(x, y, w, h, cols, band, theme="light"):
    """Five columns: big percent, caps title, note; closing band at the foot."""
    out = []
    bh = 24 if band else 0
    body = h - bh - (6 if band else 0)
    cw = w / len(cols)
    for i, (pct, name, note) in enumerate(cols):
        bx = x + i * cw
        if i:
            out.append(r(bx - 4, y, 1, body, "border.subtle", theme))
        out.append(t(bx + 8, y, cw - 16, 24, pct, "brand.primary", theme, size=17, bold=True))
        out.append(t(bx + 8, y + 30, cw - 16, 24, name, "text.primary", theme, size=6.8,
                     bold=True, caps=True, spacing=0.06, leading=1.15))
        out.append(t(bx + 8, y + 58, cw - 16, body - 60, note, "text.secondary", theme,
                     size=6.4, leading=1.25))
    if band:
        by = y + h - bh
        out.append(r(x, by, w, bh, "brand.primary", theme, radius=3))
        out.append(t(x + 10, by + 6, w - 20, bh - 10, band, "text.on-brand", theme, size=6.8,
                     bold=True, leading=1.15))
    return out


def opportunity_track(x, y, w, h, opp, checks, progress, theme="light"):
    """Opportunity numbers | value checks | progress blocks — three tracks side by side."""
    out = []
    lw = w * 0.22
    mw = w * 0.38
    pw = w - lw - mw - 20
    for i, (val, cap) in enumerate(opp):
        yy = y + i * (h / len(opp))
        out.append(t(x, yy + 6, lw - 8, 24, val, "brand.primary", theme, size=17, bold=True))
        out.append(t(x, yy + 34, lw - 8, h / len(opp) - 38, cap, "text.muted", theme,
                     size=6.4, leading=1.2))
        if i:
            out.append(r(x, yy, lw - 8, 1, "border.subtle", theme))
    mx = x + lw + 6
    out.append(r(mx - 6, y, 1, h, "border.subtle", theme))
    out.append(t(mx + 6, y - 12, mw, 10, "PROPOSISI NILAI", "text.muted", theme, size=6.2,
                 caps=True, spacing=0.08))
    for i, it in enumerate(checks):
        yy = y + i * ((h - 4) / len(checks))
        out.append(r(mx + 6, yy + 5, 8, 8, "brand.primary", theme, radius=2))
        out.append(t(mx + 20, yy, mw - 26, (h - 4) / len(checks) - 2, it, "text.secondary",
                     theme, size=6.8, leading=1.2))
    px = mx + mw + 8
    out.append(r(px - 6, y, 1, h, "border.subtle", theme))
    out.append(t(px + 4, y - 12, pw, 10, "PROGRES", "text.muted", theme, size=6.2, caps=True,
                 spacing=0.08))
    for i, (tag, line) in enumerate(progress):
        yy = y + i * ((h - 4) / len(progress))
        out.append(r(px + 4, yy, pw - 8, (h - 4) / len(progress) - 4, "surface.band", theme,
                     radius=3))
        out.append(t(px + 10, yy + 4, pw - 20, 10, tag, "brand.primary", theme, size=6,
                     bold=True, caps=True, spacing=0.06))
        out.append(t(px + 10, yy + 16, pw - 20, (h - 4) / len(progress) - 22, line,
                     "text.primary", theme, size=6.4, leading=1.15))
    return out


def orbit_compare(x, y, w, h, banner, left, right, theme="light"):
    """Two radial hubs side by side, same outer ring, three notes each; optional banner.

    left/right = (centre, role, nodes, notes)
    """
    out = []
    bh = 20 if banner else 0
    if banner:
        out.append(r(x, y, w, bh, "brand.primary", theme, radius=3))
        out.append(t(x + 10, y + 5, w - 20, bh - 8, banner, "text.on-brand", theme, size=7.2,
                     bold=True, caps=True, spacing=0.03))
    by = y + bh + (8 if banner else 0)
    body = h - bh - (8 if banner else 0)
    note_h = 34
    orbit_h = body - note_h - 6
    half = w / 2
    for i, (centre, role, nodes, notes) in enumerate((left, right)):
        hx = x + i * half
        if i:
            out.append(r(hx - 3, by, 1, body, "border.subtle", theme))
        cx, cy = hx + half / 2, by + orbit_h / 2
        rad = min(half, orbit_h) * 0.155
        for j, name in enumerate(nodes):
            ang = -math.pi / 2 + j * (2 * math.pi / len(nodes))
            nx, ny = cx + math.cos(ang) * rad * 2.45, cy + math.sin(ang) * rad * 2.45
            out.append(r(nx - rad, ny - rad * 0.4, rad * 2, rad * 0.8, "surface.raised", theme,
                         radius=2, stroke="border.strong"))
            out.append(t(nx - rad * 0.94, ny - rad * 0.3, rad * 1.88, rad * 0.6, name,
                         "text.secondary", theme, size=5.8, align="center", leading=1.05))
        out.append(r(cx - rad * 1.15, cy - rad * 0.62, rad * 2.3, rad * 1.24, "brand.primary",
                     theme, radius=3))
        out.append(t(cx - rad * 1.1, cy - rad * 0.52, rad * 2.2, rad * 0.42, role,
                     "text.on-brand", theme, size=6.2, align="center", spacing=0.02))
        out.append(t(cx - rad * 1.08, cy - rad * 0.02, rad * 2.16, rad * 0.46, centre,
                     "text.on-brand", theme, size=7.2, bold=True, align="center"))
        ny0 = by + orbit_h + 6
        for k, note in enumerate(notes):
            yy = ny0 + k * (note_h / len(notes))
            out.append(r(hx + 8, yy + 3, 3, 3, "brand.primary", theme, radius=1))
            out.append(t(hx + 16, yy, half - 26, note_h / len(notes) - 2, note,
                         "text.secondary", theme, size=6.2, leading=1.15))
    return out
