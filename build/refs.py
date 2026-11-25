#!/usr/bin/env python3
"""Reference shapes — nine layouts transcribed from the client's slide set.

Every function returns a flat primitive list and takes colours only as token
names, so both palettes render and the contrast gate still applies.

    twin_pyramid_flow   two pyramids, bridge, outcome rows      (SCT 590)
    matrix_grid         badge + 3x3 matrix of goals             (ESG 562)
    ring_list           donut + centre + rows/boxes             (588, premier)
    ring_stats          duties | ring of teams | stats + band   (fortress)
    channel_columns     three channel columns + closing band    (B2B/B2C)
    example_grid        intro block + 2x4 example cells         (IP 195)
    split_stats_story   three stats | story panel               (BCG 69)
    two_group_bullets   accent block + two bullet groups        (2nd-hand 66)
    orbit_stats         three stats + seven-node orbit          (MGI)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))

import analyst as A  # noqa: E402

t, r = A.t, A.r


def _tier(x, y, w, h, fill, theme, radius=3, stroke=None):
    return r(x, y, w, h, fill, theme, radius=radius, stroke=stroke)


# ------------------------------------------------------------------ 1 pyramids
def twin_pyramid_flow(x, y, w, h, left, right, bridge, outcomes, theme="light"):
    """left/right = (title, [(layer, note), ...]); outcomes = [(dir, text), ...]."""
    out = []
    out_h = 52
    ph = h - out_h - 12
    colw = (w - 120) / 2
    for i, (title, tiers) in enumerate((left, right)):
        px = x + i * (colw + 120)
        out.append(t(px, y - 2, colw, 12, title, "text.primary", theme, size=8.4, bold=True,
                     align="center", caps=True, spacing=0.08))
        for j, (layer, note) in enumerate(tiers):
            tw = colw * (1 - j * 0.2)
            ty = y + 18 + j * (ph - 18) / len(tiers)
            th = (ph - 18) / len(tiers) - 4
            fill = "brand.primary" if j == 0 else ("surface.raised" if j == 1 else "surface.band")
            out.append(_tier(px + (colw - tw) / 2, ty, tw, th, fill, theme, radius=3,
                             stroke=None if j == 0 else "border.strong"))
            col = "text.on-brand" if j == 0 else "text.primary"
            out.append(t(px + (colw - tw) / 2 + 6, ty + 5, tw - 12, 12, layer, col, theme,
                         size=7, bold=True, align="center"))
            out.append(t(px + (colw - tw) / 2 + 6, ty + 18, tw - 12, th - 22, note, col,
                         theme, size=6, align="center", leading=1.1))
    bx = x + colw + 12
    out.append(r(bx, y + ph / 2 - 16, 96, 32, "surface.band", theme, radius=16,
                 stroke="border.strong"))
    out.append(t(bx + 4, y + ph / 2 - 8, 88, 18, bridge, "text.primary", theme, size=6.4,
                 bold=True, align="center", leading=1.1))
    oy = y + h - out_h
    out.append(r(x, oy - 8, w, 1, "border.subtle", theme))
    ow = (w - 24) / len(outcomes)
    for i, (mark, text) in enumerate(outcomes):
        ox = x + i * (ow + 12)
        out.append(t(ox, oy, 12, 12, mark, "brand.primary", theme, size=8, bold=True))
        out.append(t(ox + 14, oy, ow - 18, out_h - 4, text, "text.secondary", theme, size=6.4,
                     leading=1.2))
    return out


# ------------------------------------------------------------------ 2 matrix
def matrix_grid(x, y, w, h, badge, cols, rows, cells, theme="light"):
    """cells[row][col] = (title, note)."""
    out = []
    bw = min(w * 0.5, 300)
    out.append(r(x + (w - bw) / 2, y, bw, 22, "brand.primary", theme, radius=11))
    out.append(t(x + (w - bw) / 2 + 10, y + 5, bw - 20, 14, badge, "text.on-brand", theme,
                 size=7.4, bold=True, align="center"))
    top = y + 34
    lw = w * 0.16
    cw = (w - lw) / len(cols)
    rh = (h - 34 - 18) / len(rows)
    for j, c in enumerate(cols):
        out.append(t(x + lw + j * cw + 4, top, cw - 8, 16, c, "brand.primary", theme,
                     size=7.2, bold=True, caps=True, spacing=0.08))
    for i, rw in enumerate(rows):
        ry = top + 18 + i * rh
        out.append(t(x, ry, lw - 8, rh, rw, "text.muted", theme, size=6.6, bold=True,
                     caps=True, spacing=0.06, leading=1.15))
        for j in range(len(cols)):
            title, note = cells[i][j]
            cx = x + lw + j * cw
            out.append(r(cx + 2, ry, cw - 8, rh - 6, "surface.raised", theme, radius=3,
                         stroke="border.subtle"))
            out.append(t(cx + 10, ry + 6, cw - 24, 12, title, "text.primary", theme, size=6.8,
                         bold=True, leading=1.1))
            out.append(t(cx + 10, ry + 20, cw - 24, rh - 30, note, "text.secondary", theme,
                         size=6.2, leading=1.15))
    return out


# ------------------------------------------------------------------ 3 ring + list
def ring_list(x, y, w, h, center, segs, rows, boxes=None, theme="light"):
    """segs = 3-4 labels around the ring; rows = [(title, note)]; boxes = [(head, [(k, v)])]."""
    out = []
    rw = w * 0.44 if (rows or boxes) else w
    cx, cy = x + rw / 2, y + h / 2
    rad = min(rw, h) * 0.30
    n = len(segs)
    for i, name in enumerate(segs):
        a0 = -math.pi / 2 + i * 2 * math.pi / n
        bx, by = cx + math.cos(a0) * rad * 1.05, cy + math.sin(a0) * rad * 1.05
        out.append(r(bx - rad * 0.48, by - rad * 0.18, rad * 0.96, rad * 0.36,
                     "chart.series.%d" % ((i % 4) + 1), theme, radius=3))
        out.append(t(bx - rad * 0.45, by - rad * 0.13, rad * 0.90, rad * 0.26, name,
                     "text.on-brand", theme, size=6, bold=True, align="center", leading=1.0))
    out.append(r(cx - rad * 0.45, cy - rad * 0.45, rad * 0.9, rad * 0.9, "surface.raised", theme,
                 radius=int(rad * 0.45), stroke="brand.primary"))
    out.append(t(cx - rad * 0.40, cy - rad * 0.14, rad * 0.80, rad * 0.28, center,
                 "text.primary", theme, size=6.6, bold=True, align="center", leading=1.05))
    rx = x + rw + 8
    if rows:
        rh = h / len(rows)
        for i, (title, note) in enumerate(rows):
            yy = y + i * rh
            out.append(r(rx, yy + 6, 4, 4, "brand.primary", theme, radius=1))
            out.append(t(rx + 12, yy, w - rw - 20, 12, title, "text.primary", theme, size=7,
                         bold=True, leading=1.1))
            out.append(t(rx + 12, yy + 14, w - rw - 20, rh - 18, note, "text.secondary", theme,
                         size=6.3, leading=1.2))
    for i, (head, items) in enumerate(boxes or []):
        bh = (h - 10) / len(boxes)
        by = y + i * (bh + 10)
        out.append(r(rx, by, w - rw - 8, bh, "surface.raised", theme, radius=3,
                     stroke="border.subtle"))
        out.append(t(rx + 8, by + 6, w - rw - 24, 10, head, "brand.primary", theme, size=6,
                     bold=True, caps=True, spacing=0.08))
        for k, (key, val) in enumerate(items):
            yy = by + 20 + k * ((bh - 24) / max(1, len(items)))
            out.append(t(rx + 8, yy, 40, 12, key, "text.muted", theme, size=6.2))
            out.append(t(rx + 50, yy, w - rw - 66, 12, val, "text.primary", theme, size=6.4,
                         bold=True))
    return out


# ------------------------------------------------------------------ 4 ring + stats
def ring_stats(x, y, w, h, duties, center, teams, stats, band, theme="light"):
    out = []
    band_h = 22 if band else 0
    body = h - band_h - (6 if band else 0)
    lw, mw = w * 0.30, w * 0.40
    sw = w - lw - mw - 16
    for i, d in enumerate(duties):
        yy = y + i * (body / len(duties))
        out.append(r(x, yy + 5, 4, 4, "brand.primary", theme, radius=1))
        out.append(t(x + 12, yy, lw - 16, body / len(duties) - 3, d, "text.secondary", theme,
                     size=6.6, leading=1.2))
    mx = x + lw + 6
    out.append(r(mx - 6, y, 1, body, "border.subtle", theme))
    cx, cy = mx + mw / 2, y + body / 2
    rad = min(mw * 0.25, body * 0.235)
    for i, name in enumerate(teams):
        a = -math.pi / 2 + i * 2 * math.pi / len(teams)
        nx, ny = cx + math.cos(a) * rad * 1.62, cy + math.sin(a) * rad * 1.62
        out.append(r(nx - rad * 0.46, ny - rad * 0.17, rad * 0.92, rad * 0.34, "surface.raised",
                     theme, radius=2, stroke="border.strong"))
        out.append(t(nx - rad * 0.44, ny - rad * 0.11, rad * 0.88, rad * 0.22, name,
                     "text.secondary", theme, size=5.6, align="center", leading=1.0))
    out.append(r(cx - rad * 0.62, cy - rad * 0.62, rad * 1.24, rad * 1.24, "brand.primary",
                 theme, radius=int(rad * 0.62)))
    out.append(t(cx - rad * 0.56, cy - rad * 0.2, rad * 1.12, rad * 0.4, center,
                 "text.on-brand", theme, size=6.4, bold=True, align="center", leading=1.1))
    sx = mx + mw + 10
    out.append(r(sx - 6, y, 1, body, "border.subtle", theme))
    for i, (val, cap) in enumerate(stats):
        yy = y + i * (body / len(stats))
        out.append(t(sx + 2, yy + 2, sw, 16, val, "brand.primary", theme, size=10.5,
                     bold=True))
        out.append(t(sx + 2, yy + 18, sw, body / len(stats) - 22, cap, "text.muted", theme,
                     size=6, leading=1.15))
    if band:
        by = y + h - band_h
        out.append(r(x, by, w, band_h, "brand.primary", theme, radius=3))
        out.append(t(x + 10, by + 5, w - 20, band_h - 8, band, "text.on-brand", theme,
                     size=7, bold=True, leading=1.1))
    return out


# ------------------------------------------------------------------ 5 channels
def channel_columns(x, y, w, h, cols, band, theme="light"):
    """cols = [(tag, title, strength, [(stat, note)], close)]."""
    out = []
    band_h = 22 if band else 0
    body = h - band_h - (6 if band else 0)
    gap = 10
    cw = (w - gap * (len(cols) - 1)) / len(cols)
    for i, (tag, title, strength, stats, close) in enumerate(cols):
        bx = x + i * (cw + gap)
        out.append(r(bx, y, cw, body, "surface.raised", theme, radius=3, stroke="border.subtle"))
        out.append(r(bx + 10, y + 10, 34, 14, "brand.primary", theme, radius=7))
        out.append(t(bx + 10, y + 13, 34, 9, tag, "text.on-brand", theme, size=5.6, bold=True,
                     align="center", caps=True, spacing=0.06))
        out.append(t(bx + 10, y + 30, cw - 20, 14, title, "text.primary", theme, size=8,
                     bold=True))
        out.append(t(bx + 10, y + 46, cw - 20, 10, strength, "brand.primary", theme, size=6.2,
                     bold=True, caps=True, spacing=0.06))
        sy = y + 62
        for k, (stat, note) in enumerate(stats):
            yy = sy + k * ((body - 104) / max(1, len(stats)))
            out.append(t(bx + 10, yy, cw - 20, 14, stat, "text.primary", theme, size=9.5,
                         bold=True))
            out.append(t(bx + 10, yy + 15, cw - 20, (body - 104) / max(1, len(stats)) - 17, note,
                         "text.secondary", theme, size=6.2, leading=1.2))
        out.append(t(bx + 10, y + body - 26, cw - 20, 22, close, "text.muted", theme, size=6.2,
                     leading=1.15))
    if band:
        by = y + h - band_h
        out.append(r(x, by, w, band_h, "status.success", theme, radius=3))
        out.append(t(x + 10, by + 5, w - 20, band_h - 8, band, "text.on-brand", theme, size=7,
                     bold=True, leading=1.1))
    return out


# ------------------------------------------------------------------ 6 example grid
def example_grid(x, y, w, h, intro, big, note, items, theme="light"):
    """items = [(label, note)] laid out 4 across, 2 rows."""
    out = []
    lw = w * 0.32
    out.append(t(x, y, lw - 16, 26, big, "brand.primary", theme, size=18, bold=True))
    out.append(t(x, y + 24, lw - 16, h - 40, intro, "text.secondary", theme, size=7,
                 leading=1.3))
    out.append(t(x, y + h - 14, lw - 16, 12, note, "text.muted", theme, size=6))
    gx = x + lw + 10
    out.append(r(gx - 8, y, 1, h, "border.subtle", theme))
    out.append(t(gx, y - 12, w - lw, 10, "Contoh ilustratif", "text.muted", theme, size=6.2,
                 caps=True, spacing=0.08))
    cols = 4
    cw = (w - lw - 20) / cols
    rh = (h - 12) / 2
    for i, (label, nt) in enumerate(items[:8]):
        cx = gx + (i % cols) * cw
        cy = y + (i // cols) * (rh + 8)
        out.append(r(cx, cy, cw - 8, rh - 4, "surface.raised", theme, radius=3,
                     stroke="border.subtle"))
        out.append(r(cx + 8, cy + 8, 12, 12, "brand.primary", theme, radius=3))
        out.append(t(cx + 8, cy + 26, cw - 24, 14, label, "text.primary", theme, size=6.6,
                     bold=True, leading=1.1))
        out.append(t(cx + 8, cy + 42, cw - 24, rh - 48, nt, "text.secondary", theme, size=6,
                     leading=1.15))
    return out


# ------------------------------------------------------------------ 7 stats + story
def split_stats_story(x, y, w, h, stats, panel_title, panel_rows, theme="light"):
    out = []
    lw = w * 0.42
    rh = h / len(stats)
    for i, (val, note) in enumerate(stats):
        yy = y + i * rh
        out.append(t(x, yy + 2, lw - 20, 22, val, "brand.primary", theme, size=16, bold=True))
        out.append(t(x, yy + 26, lw - 20, rh - 30, note, "text.secondary", theme, size=6.6,
                     leading=1.2))
        if i:
            out.append(r(x, yy - 4, lw - 20, 1, "border.subtle", theme))
    px = x + lw
    out.append(r(px, y, w - lw, h, "surface.band", theme, radius=4))
    out.append(t(px + 12, y + 10, w - lw - 24, 12, panel_title, "text.primary", theme, size=7.4,
                 bold=True, leading=1.1))
    ry = y + 28
    for i, (head, note) in enumerate(panel_rows):
        yy = ry + i * ((h - 36) / len(panel_rows))
        out.append(r(px + 12, yy + 5, 4, 4, "brand.primary", theme, radius=1))
        out.append(t(px + 24, yy, w - lw - 40, 12, head, "text.primary", theme, size=6.6,
                     bold=True, leading=1.1))
        out.append(t(px + 24, yy + 13, w - lw - 40, (h - 36) / len(panel_rows) - 15, note,
                     "text.secondary", theme, size=6.2, leading=1.15))
    return out


# ------------------------------------------------------------------ 8 two groups
def two_group_bullets(x, y, w, h, block, groups, theme="light"):
    """block = (title, note); groups = [(head, [(title, note)])]."""
    out = []
    lw = w * 0.36
    out.append(r(x, y, lw - 12, h, "status.success", theme, radius=4))
    out.append(t(x + 14, y + 14, lw - 40, 40, block[0], "text.on-brand", theme, size=8.6,
                 bold=True, leading=1.15))
    out.append(t(x + 14, y + h - 44, lw - 40, 30, block[1], "text.on-brand", theme, size=6.4,
                 leading=1.2))
    gx = x + lw + 4
    gw = w - lw - 4
    for gi, (head, items) in enumerate(groups):
        gy = y + gi * (h / len(groups))
        gh = h / len(groups) - 6
        out.append(t(gx, gy, gw, 10, head, "text.muted", theme, size=6.2, caps=True,
                     spacing=0.08))
        for k, (title, note) in enumerate(items):
            yy = gy + 16 + k * ((gh - 16) / len(items))
            out.append(r(gx, yy + 5, 5, 5, "brand.primary", theme, radius=2))
            out.append(t(gx + 14, yy, gw - 16, 12, title, "text.primary", theme, size=7,
                         bold=True, leading=1.1))
            out.append(t(gx + 14, yy + 14, gw - 16, (gh - 16) / len(items) - 16, note,
                         "text.secondary", theme, size=6.2, leading=1.15))
    return out


# ------------------------------------------------------------------ 9 orbit + stats
def orbit_stats(x, y, w, h, stats, center, nodes, theme="light"):
    """stats = [(val, cap)] top right; nodes = [(n, title, note)]."""
    out = []
    sh = 46
    sw = w / len(stats)
    for i, (val, cap) in enumerate(stats):
        sx = x + i * sw
        out.append(t(sx, y, sw - 12, 24, val, "brand.primary", theme, size=15, bold=True))
        out.append(t(sx, y + 24, sw - 12, sh - 24, cap, "text.muted", theme, size=6.2,
                     leading=1.15))
    out.append(r(x, y + sh, w, 1, "border.subtle", theme))
    cy0 = y + sh + 10
    ch = h - sh - 10
    cx, cy = x + w * 0.235, cy0 + ch / 2
    rad = min(w * 0.165, ch * 0.215)
    out.append(r(cx - rad, cy - rad, rad * 2, rad * 2, "brand.primary", theme,
                 radius=int(rad)))
    out.append(t(cx - rad * 0.82, cy - rad * 0.42, rad * 1.64, rad * 0.84, center,
                 "text.on-brand", theme, size=7, bold=True, align="center", leading=1.1))
    for i, (num, title, note) in enumerate(nodes):
        a = -math.pi / 2 + i * 2 * math.pi / len(nodes)
        nx, ny = cx + math.cos(a) * rad * 2.12, cy + math.sin(a) * rad * 2.12
        out.append(r(nx - 7, ny - 7, 14, 14, "surface.raised", theme, radius=7,
                     stroke="brand.primary"))
        out.append(t(nx - 7, ny - 4, 14, 8, str(num), "brand.primary", theme, size=5.6,
                     bold=True, align="center"))
        out.append(t(nx + 10, ny - 8, 74, 18, title, "text.primary", theme, size=6, bold=True,
                     leading=1.05))
    lx = x + w * 0.62
    out.append(r(lx - 10, cy0, 1, ch, "border.subtle", theme))
    for i, (num, title, note) in enumerate(nodes):
        yy = cy0 + i * (ch / len(nodes))
        out.append(t(lx, yy, 12, 8, str(num), "brand.primary", theme, size=5.6, bold=True))
        out.append(t(lx + 12, yy - 2, w - (lx - x) - 16, 10, title, "text.primary", theme,
                     size=6.4, bold=True, leading=1.05))
        out.append(t(lx + 12, yy + 9, w - (lx - x) - 16, ch / len(nodes) - 11, note,
                     "text.muted", theme, size=5.8, leading=1.1))
    return out


# ------------------------------------------------------------------ 10 metrics 4x2
def stat_octet(x, y, w, h, items, note, theme="light"):
    """items = [(value, label, detail), ...] eight entries, 4 columns x 2 rows."""
    out = []
    cols, rows = 4, 2
    cw, chh = w / cols, h / rows
    for i, (val, lab, det) in enumerate(items):
        cx = x + (i % cols) * cw
        cy = y + (i // cols) * chh
        out.append(r(cx + 8, cy + 6, cw - 16, chh - 12, "surface.raised", theme, radius=4,
                     stroke="border.subtle"))
        out.append(r(cx + 20, cy + 18, 20, 20, "brand.primary", theme, radius=4))
        out.append(t(cx + 20, cy + 24, 20, 8, "\u25b2", "text.on-brand", theme, size=5.6,
                     align="center"))
        out.append(t(cx + 48, cy + 16, cw - 62, 28, val, "brand.primary", theme, size=20,
                     bold=True))
        out.append(t(cx + 20, cy + 52, cw - 36, 24, lab, "text.primary", theme, size=7.2,
                     bold=True, leading=1.1))
        out.append(r(cx + 20, cy + 78, cw - 40, 1, "border.subtle", theme))
        out.append(t(cx + 20, cy + 86, cw - 40, chh - 124, det, "text.secondary", theme,
                     size=6.2, leading=1.35))
        out.append(t(cx + 20, cy + chh - 32, cw - 40, 10, f"{i + 1:02d}", "text.muted", theme,
                     size=5.8, align="right"))
    out.append(t(x, y + h - 10, w, 10, note, "text.muted", theme, size=5.8, align="right"))
    return out


# ------------------------------------------------------------------ 11 three panels
def stat_trio(x, y, w, h, items, note, theme="light"):
    """items = [(value, label, note[, [(t, v), ...]]), ...] three panels.

    If the third entry carries a series the layout stacks: two stats on top,
    the series panel full width below.
    """
    out = []
    gap = 14
    series = items[2][3] if len(items[2]) > 3 else None
    if series:
        top_h = (h - 16) * 0.40
        cw = (w - gap) / 2
        for i in range(2):
            val, lab, det = items[i][:3]
            cx = x + i * (cw + gap)
            out.append(r(cx, y, cw, top_h, "surface.raised", theme, radius=4,
                         stroke="border.subtle"))
            out.append(r(cx + 16, y + 18, 26, 3, "brand.primary", theme, radius=1))
            out.append(t(cx + 16, y + 28, cw - 32, 40, val, "brand.primary", theme, size=30,
                         bold=True))
            out.append(t(cx + 16, y + 74, cw - 32, 22, lab, "text.primary", theme, size=7.4,
                         bold=True, leading=1.15))
            out.append(t(cx + 16, y + 100, cw - 32, top_h - 112, det, "text.secondary",
                         theme, size=6.4, leading=1.3))
        by = y + top_h + gap
        bh = h - 16 - top_h - gap
        out.append(r(x, by, w, bh, "surface.raised", theme, radius=4, stroke="border.subtle"))
        out.append(r(x + 16, by + 18, 26, 3, "brand.primary", theme, radius=1))
        out.append(t(x + 16, by + 28, w * 0.34, 40, items[2][0], "brand.primary", theme,
                     size=30, bold=True))
        out.append(t(x + 16, by + 74, w * 0.34, 22, items[2][1], "text.primary", theme,
                     size=7.4, bold=True, leading=1.15))
        out.append(t(x + 16, by + 100, w * 0.32, bh - 116, items[2][2], "text.secondary",
                     theme, size=6.4, leading=1.3))
        bx = x + w * 0.40
        bw = w - (bx - x) - 26
        base = by + bh - 34
        span = bh - 92
        vmax = max(v for _, v in series)
        step = bw / len(series)
        out.append(r(bx, base, bw, 1, "border.strong", theme))
        for k, (lab, v) in enumerate(series):
            hh = (v / vmax) * span
            last = k == len(series) - 1
            out.append(r(bx + k * step + step * 0.16, base - hh, step * 0.68, hh,
                         "brand.primary" if last else "chart.series.3", theme, radius=2))
            out.append(t(bx + k * step, base - hh - 16, step, 12, str(v).replace(".", ","),
                         "text.primary", theme, size=7.4, bold=last, align="center"))
            out.append(t(bx + k * step, base + 6, step, 12, lab, "text.muted", theme,
                         size=6.2, align="center"))
    else:
        cw = (w - 2 * gap) / 3
        for i, (val, lab, det) in enumerate(items):
            cx = x + i * (cw + gap)
            out.append(r(cx, y, cw, h - 16, "surface.raised", theme, radius=4,
                         stroke="border.subtle"))
            out.append(r(cx + 16, y + 18, 26, 3, "brand.primary", theme, radius=1))
            out.append(t(cx + 16, y + 28, cw - 32, 40, val, "brand.primary", theme, size=30,
                         bold=True))
            out.append(t(cx + 16, y + 74, cw - 32, 24, lab, "text.primary", theme, size=7.4,
                         bold=True, leading=1.15))
            out.append(t(cx + 16, y + 104, cw - 32, h - 136, det, "text.secondary", theme,
                         size=6.8, leading=1.35))
    out.append(t(x, y + h - 12, w, 10, note, "text.muted", theme, size=5.8, align="right"))
    return out


# ------------------------------------------------------------------ 12 paired hbar
def hbar_paired(x, y, w, h, rows, legends, note, vmax=100, theme="light"):
    """rows = [(label, before, after), ...]; legends = (before, after)."""
    out = []
    lw = w * 0.30
    bw = w - lw - 34
    rh = (h - 40) / len(rows)
    out.append(t(x, y, lw, 8, "", "text.muted", theme, size=5.6))
    for i, (lab, a, b) in enumerate(rows):
        yy = y + 10 + i * rh
        out.append(t(x, yy + rh / 2 - 7, lw - 8, 14, lab, "text.primary", theme, size=6.4,
                     leading=1.05))
        out.append(r(x + lw, yy + rh / 2 - 9, max(1, bw * a / vmax), 7, "chart.series.3", theme,
                     radius=2))
        out.append(r(x + lw, yy + rh / 2 + 1, max(1, bw * b / vmax), 7, "brand.primary", theme,
                     radius=2))
        out.append(t(x + lw + bw * a / vmax + 4, yy + rh / 2 - 10, 26, 9, str(a),
                     "text.muted", theme, size=5.6))
        out.append(t(x + lw + bw * b / vmax + 4, yy + rh / 2 - 1, 30, 10, str(b),
                     "text.secondary", theme, size=5.8, bold=True))
    for g in (0, 50, 100):
        gx = x + lw + bw * g / vmax
        out.append(r(gx, y + 6, 1, h - 40, "border.subtle", theme))
        out.append(t(gx - 8, y + h - 20, 16, 8, str(g), "text.muted", theme, size=5.2,
                     align="center"))
    lx = x + lw
    for k, (name, tok) in enumerate(legends):
        out.append(r(lx + k * 92, y - 12, 8, 8, tok, theme, radius=2))
        out.append(t(lx + k * 92 + 12, y - 13, 80, 10, name, "text.muted", theme, size=5.8))
    out.append(t(x, y + h - 8, w, 10, note, "text.muted", theme, size=5.8, align="right"))
    return out


# ------------------------------------------------------------------ 13 ranked hbar
def hbar_ranked(x, y, w, h, rows, note, theme="light"):
    """rows = [(label, pct, tier)] tier 0..2 -> series 1/2/3."""
    out = []
    lw = w * 0.34
    bw = w - lw - 40
    rh = (h - 24) / len(rows)
    toks = {0: "chart.series.1", 1: "brand.primary", 2: "chart.series.3"}
    for i, (lab, pct, tier) in enumerate(rows):
        yy = y + i * rh
        out.append(t(x, yy + rh / 2 - 8, lw - 10, 16, lab, "text.primary", theme, size=6.6,
                     bold=True, leading=1.05))
        out.append(r(x + lw, yy + rh / 2 - 7, bw * pct / 100, 14, toks[tier], theme,
                     radius=2))
        out.append(t(x + lw + bw * pct / 100 + 6, yy + rh / 2 - 6, 34, 12, "%d%%" % pct,
                     "text.primary", theme, size=7, bold=True))
    out.append(r(x + lw - 1, y, 1, h - 16, "border.strong", theme))
    out.append(t(x, y + h - 8, w, 10, note, "text.muted", theme, size=5.8, align="right"))
    return out


# ------------------------------------------------------------------ 14 jobs waterfall rows
def waterfall_rows(x, y, w, h, groups, total, note, theme="light"):
    """groups = [(title, [(label, value), ...]), ...]; total = (label, value)."""
    out = []
    flat = [(g, lab, v) for g, items in groups for lab, v in items]
    vmax = max(max(v for _, _, v in flat), total[1])
    lw = w * 0.32
    bw = w - lw - 46
    rh = (h - 34) / (len(flat) + 1)
    for i, (g, lab, v) in enumerate(flat):
        yy = y + 16 + i * rh
        tok = "brand.primary" if g == groups[0][0] else "chart.series.3"
        out.append(t(x, yy + rh / 2 - 7, lw - 8, 14, lab, "text.primary", theme, size=6.2,
                     leading=1.05))
        out.append(r(x + lw, yy + rh / 2 - 6, max(1, bw * v / vmax), 12, tok, theme, radius=2))
        out.append(t(x + lw + bw * v / vmax + 5, yy + rh / 2 - 5, 36, 10, str(v),
                     "text.secondary", theme, size=6))
    ty = y + 16 + len(flat) * rh
    out.append(r(x + lw, ty + 2, max(1, bw * total[1] / vmax), 14, "surface.band", theme, radius=2,
                 stroke="border.strong"))
    out.append(t(x, ty + 1, lw - 8, 14, total[0], "text.primary", theme, size=6.6, bold=True))
    out.append(t(x + lw + bw * total[1] / vmax + 5, ty + 3, 40, 12, str(total[1]),
                 "text.primary", theme, size=6.6, bold=True))
    # group markers
    gy = y
    for k, (title, items) in enumerate(groups):
        if k:
            gy += 10
        out.append(t(x, gy, lw, 10, title, "text.muted", theme, size=5.6, caps=True,
                     spacing=0.06))
        out.append(r(x, gy + 11, lw - 12, 1, "border.subtle", theme))
        gy += 16 + len(items) * rh
    out.append(t(x, y + h - 8, w, 10, note, "text.muted", theme, size=5.8, align="right"))
    return out


# ------------------------------------------------------------------ 15 diverging split hbar
def hbar_split(x, y, w, h, rows, legends, note, theme="light"):
    """rows = [(industry, out_eu, out_other, stay_eu, stay_other), ...]."""
    out = []
    lw = w * 0.24
    half = (w - lw) / 2 - 12
    rh = (h - 40) / len(rows)
    vmax = max(max(a + b, c + d) for _, a, b, c, d in rows)
    for i, (ind, a, b, c, d) in enumerate(rows):
        yy = y + 14 + i * rh
        bh = min(11, rh - 8)
        out.append(t(x, yy + rh / 2 - 7, lw - 8, 14, ind, "text.primary", theme, size=6.2,
                     leading=1.05))
        # exit side grows leftwards from centre line
        cx = x + lw + half
        w1 = (half - 30) * a / vmax
        w2 = (half - 30) * b / vmax
        out.append(r(cx - w1 - w2, yy + rh / 2 - bh / 2, max(1, w2), bh, "chart.series.2", theme,
                     radius=1))
        out.append(r(cx - w1, yy + rh / 2 - bh / 2, max(1, w1), bh, "brand.primary", theme, radius=1))
        if a + b:
            out.append(t(cx - w1 - w2 - 22, yy + rh / 2 - 5, 20, 10, str(a + b),
                         "text.secondary", theme, size=5.8, align="right"))
        # stay side grows rightwards
        w3 = (half - 30) * c / vmax
        w4 = (half - 30) * d / vmax
        out.append(r(cx + 1, yy + rh / 2 - bh / 2, max(1, w3), bh, "brand.primary", theme, radius=1))
        out.append(r(cx + 1 + w3, yy + rh / 2 - bh / 2, max(1, w4), bh, "chart.series.2", theme,
                     radius=1))
        if c + d:
            out.append(t(cx + 1 + w3 + w4 + 3, yy + rh / 2 - 5, 22, 10, str(c + d),
                         "text.secondary", theme, size=5.8))
    cx = x + lw + half
    out.append(r(cx, y + 4, 1, h - 24, "border.strong", theme))
    out.append(t(x + lw, y - 10, half, 10, "Keluar / menyusut", "text.muted", theme,
                 size=5.8, align="right", caps=True, spacing=0.06))
    out.append(t(cx + 4, y - 10, half, 10, "Bertahan", "text.muted", theme, size=5.8,
                 caps=True, spacing=0.06))
    lgx = x + lw
    for k, (name, tok) in enumerate(legends):
        out.append(r(lgx + k * 150, y + h - 24, 8, 8, tok, theme, radius=2))
        out.append(t(lgx + k * 150 + 12, y + h - 25, 130, 10, name, "text.muted", theme,
                     size=6.2))
    out.append(t(x, y + h - 8, w * 0.4, 10, note, "text.muted", theme, size=5.8))
    return out


# ------------------------------------------------------------------ 16 attribution bars
def attribution_bars(x, y, w, h, panels, note, theme="light"):
    """panels = [(title, tone, [(label, value), ...]), ...] tone 0 = up, 1 = down."""
    out = []
    gap = 16
    cw = (w - gap) / len(panels)
    for i, (title, tone, rows) in enumerate(panels):
        px = x + i * (cw + gap)
        out.append(r(px, y, cw, h - 18, "surface.raised", theme, radius=4,
                     stroke="border.subtle"))
        out.append(t(px + 12, y + 10, cw - 24, 12, title, "text.primary", theme, size=7,
                     bold=True, caps=True, spacing=0.06))
        vmax = max(abs(v) for _, v in rows) or 1
        zero_y = y + 40 + (h - 100) * 0.5
        span = (h - 130) / 2
        out.append(r(px + 12, zero_y, cw - 24, 1, "border.strong", theme))
        bw = (cw - 40) / len(rows)
        for k, (lab, v) in enumerate(rows):
            bx = px + 20 + k * bw
            hh = abs(v) / vmax * span
            tok = "brand.primary" if tone == 0 else "chart.series.3"
            if v >= 0:
                out.append(r(bx, zero_y - max(1, hh), bw - 12, max(1, hh), tok, theme, radius=1))
                out.append(t(bx, zero_y - hh - 11, bw - 12, 10, ("%+.1f" % v).replace(".", ","),
                             "text.primary", theme, size=5.8, bold=True, align="center"))
            else:
                out.append(r(bx, zero_y + 1, bw - 12, max(1, hh), tok, theme, radius=1))
                out.append(t(bx, zero_y + hh + 2, bw - 12, 10, ("%+.1f" % v).replace(".", ","),
                             "text.muted", theme, size=5.8, align="center"))
            out.append(t(bx - 4, y + h - 42, bw - 4, 22, lab, "text.secondary", theme,
                         size=5.6, align="center", leading=1.05))
    out.append(t(x, y + h - 12, w, 10, note, "text.muted", theme, size=5.8, align="right"))
    return out


# ------------------------------------------------------------------ 17 bridge waterfall
def waterfall_bridge(x, y, w, h, start, levers, end, note, theme="light"):
    """start = (label, value); levers = [(label, delta), ...]; end = (label, lo, hi)."""
    out = []
    plot_h = h - 84
    base = y + 20 + plot_h
    vmax = start[1]
    scale = plot_h / vmax
    n = len(levers) + 2
    bw = (w - 20) / n
    out.append(r(x + 10, base - start[1] * scale, bw - 14, max(1, start[1] * scale),
                 "brand.primary", theme, radius=2))
    out.append(t(x + 10, base - start[1] * scale - 12, bw - 14, 10, str(start[1]),
                 "text.primary", theme, size=6.4, bold=True, align="center"))
    out.append(t(x + 10, base + 4, bw - 14, 16, start[0], "text.muted", theme, size=5.8,
                 align="center", leading=1.05))
    cur = start[1]
    for i, (lab, delta) in enumerate(levers):
        cx = x + 10 + (i + 1) * bw
        top = base - cur * scale
        hh = abs(delta) * scale
        out.append(r(cx, top, bw - 14, max(1, hh), "chart.series.2", theme, radius=2))
        out.append(t(cx, top - 12, bw - 14, 10, "%+d" % delta, "text.primary", theme,
                     size=6.2, bold=True, align="center"))
        out.append(t(cx - 4, base + 4, bw - 6, 24, lab, "text.muted", theme, size=5.6,
                     align="center", leading=1.05))
        out.append(r(cx - 10, top, 10, 1, "border.strong", theme))
        cur += delta
    ex = x + 10 + (n - 1) * bw
    out.append(r(ex, base - end[2] * scale, bw - 14, max(1, (end[2] - end[1]) * scale),
                 "surface.band", theme, radius=2, stroke="brand.primary"))
    out.append(t(ex, base - end[2] * scale - 12, bw - 14, 10, "%d–%d" % (end[1], end[2]),
                 "text.primary", theme, size=6.2, bold=True, align="center"))
    out.append(t(ex, base + 4, bw - 14, 16, end[0], "text.muted", theme, size=5.8,
                 align="center", leading=1.05))
    out.append(r(x + 10, base, w - 20, 1, "border.strong", theme))
    out.append(t(x, y + h - 10, w, 10, note, "text.muted", theme, size=5.8, align="right"))
    return out


# ------------------------------------------------------------------ 18 strategy trio
def strategy_trio(x, y, w, h, cols, note, theme="light"):
    """cols = [(title, [bullet, ...], goal), ...]."""
    out = []
    gap = 26
    cw = (w - 2 * gap) / 3
    for i, (title, bullets, goal) in enumerate(cols):
        cx = x + i * (cw + gap)
        out.append(r(cx, y, cw, h - 18, "surface.raised", theme, radius=4,
                     stroke="border.subtle"))
        out.append(r(cx, y, cw, 3, "brand.primary", theme, radius=1))
        out.append(t(cx + 14, y + 14, cw - 28, 24, title, "text.primary", theme, size=7.6,
                     bold=True, leading=1.1))
        top = y + 46
        goal_y = y + h - 52
        step = min(58, max(30, (goal_y - top - 16) / max(1, len(bullets))))
        for k, b in enumerate(bullets):
            yy = top + k * step
            out.append(r(cx + 14, yy + 4, 4, 4, "brand.primary", theme, radius=2))
            out.append(t(cx + 24, yy, cw - 40, step - 6, b, "text.secondary", theme, size=6.4,
                         leading=1.3))
        out.append(r(cx + 12, y + h - 52, cw - 24, 30, "brand.primary", theme, radius=3))
        out.append(t(cx + 18, y + h - 46, cw - 36, 20, goal, "text.on-brand", theme, size=6.4,
                     bold=True, leading=1.1))
        if i < len(cols) - 1:
            out.append(t(cx + cw, y + h / 2 - 10, gap, 12, "\u2192", "text.muted", theme,
                         size=9, align="center"))
    out.append(t(x, y + h - 12, w, 10, note, "text.muted", theme, size=5.8, align="right"))
    return out


# ------------------------------------------------------------------ 19 hex framework
def hex_framework(x, y, w, h, big, groups, note, theme="light"):
    """big = (value, label); groups = [(row label, [node, ...]), ...]."""
    out = []
    out.append(t(x, y - 2, w * 0.3, 34, big[0], "brand.primary", theme, size=22, bold=True))
    out.append(t(x, y + 30, w * 0.34, 34, big[1], "text.primary", theme, size=7.2, bold=True,
                 leading=1.2))
    for k, line in enumerate(big[2] if len(big) > 2 else []):
        out.append(r(x, y + 78 + k * 40, 1, 30, "border.subtle", theme))
        out.append(t(x + 8, y + 78 + k * 40, w * 0.32, 30, line, "text.muted", theme,
                     size=6, leading=1.2))
    gx = x + w * 0.36
    gw = w - (gx - x)
    rows = len(groups)
    rh = (h - 20) / rows
    for i, (lab, nodes) in enumerate(groups):
        ry = y + i * rh
        out.append(t(gx, ry, 100, 10, lab, "text.primary", theme, size=6.2, bold=True,
                     caps=True, spacing=0.06))
        out.append(r(gx, ry + 12, 1, rh - 18, "border.subtle", theme))
        nw = (gw - 108) / len(nodes)
        for k, node in enumerate(nodes):
            nx = gx + 108 + k * nw
            out.append(r(nx + 2, ry + 4, nw - 8, rh - 16, "brand.primary", theme,
                         radius=int(min(nw, rh) * 0.28)))
            out.append(t(nx + 6, ry + 8, nw - 16, rh - 24, node, "text.on-brand", theme,
                         size=6, align="center", leading=1.15))
    out.append(t(x, y + h - 8, w, 10, note, "text.muted", theme, size=5.8, align="right"))
    return out
