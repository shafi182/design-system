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
