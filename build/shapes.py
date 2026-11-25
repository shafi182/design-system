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
