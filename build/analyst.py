#!/usr/bin/env python3
"""Analyst layout — the dense consulting grid, rendered from the same tokens.

Reference language: 2x3 panels per slide, 32px margin, per-panel title, per-panel
source line, tab strip at the top (Table / Chart / Panel / Framework / Visual),
hairline tables, chart series taken from `chart.series.*` in the active palette.
Nothing here invents a colour: every fill is a token, so both palettes work and
the contrast gate keeps applying.

    python build/analyst.py professional     # examples/analyst-professional.pptx
    python build/analyst.py adventurous
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))

PALETTE = sys.argv[1] if len(sys.argv) > 1 else "professional"
os.environ["SIGNAL_PALETTE"] = PALETTE

import deck as D  # noqa: E402  (primitives + palette loader)
import preview as PV  # noqa: E402  (svg chart for the HTML twin)

D.load_palette(PALETTE)

PX, W, H = 9525, 1280, 720
M = 32
GUT = 14
NAV_H = 34
TITLE_Y = 62
RULE_Y = 92
GRID_Y = 104
GRID_BOTTOM = 676
PANEL_R = 6
PAD = 10
SRC_H = 13
BODY_TOP = 54
TAB_H = 18
TABS = ["Table", "Chart", "Panel", "Framework", "Visual"]

ALIGN = {"left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT, "center": PP_ALIGN.CENTER}


def tok(theme, name):
    return (D.DARK if theme == "dark" else D.LIGHT)[name]


def hx(theme, name):
    return str(tok(theme, name)).lstrip("#").upper()


# ------------------------------------------------------------------ primitives
def t(x, y, w, h, text, color, theme="light", size: float = 9.5, bold=False, leading=1.3,
      spacing=0.0, caps=False, align="left", font="body"):
    return {"kind": "text", "x": x, "y": y, "w": w, "h": h, "text": text, "theme": theme,
            "color": color, "font": font, "size": size, "bold": bold, "leading": leading,
            "spacing": spacing, "caps": caps, "align": align}


def r(x, y, w, h, fill, theme="light", radius=0, stroke=None, stroke_w=1):
    return {"kind": "rect", "x": x, "y": y, "w": w, "h": h, "fill": fill, "theme": theme,
            "radius": radius, "stroke": stroke, "stroke_w": stroke_w}


def img(x, y, w, h, name="photo-43.png", theme="light", radius=6):
    return {"kind": "image", "x": x, "y": y, "w": w, "h": h, "src": name,
            "theme": theme, "radius": radius}


def hbar(x, y, w, h, rows, theme="light", maxv=None, color="chart.series.1",
         label_w=78, unit=""):
    return {"kind": "hbar", "x": x, "y": y, "w": w, "h": h, "rows": rows, "theme": theme,
            "max": maxv or max(v for _, v in rows), "color": color,
            "label_w": label_w, "unit": unit}


def hstack(x, y, w, h, rows, theme="light", unit=""):
    """rows: (label, part, whole) — part filled with series 1, rest with a track."""
    return {"kind": "hstack", "x": x, "y": y, "w": w, "h": h, "rows": rows,
            "theme": theme, "unit": unit}


def donut(x, y, d, value, label, theme="light", color="chart.series.1"):
    return {"kind": "donut", "x": x, "y": y, "w": d, "h": d, "value": value,
            "label": label, "theme": theme, "color": color}


# ------------------------------------------------------------------ layout helpers
PH = (GRID_BOTTOM - GRID_Y - 2 * GUT) / 3


def cell(col, row):
    pw = (W - 2 * M - GUT) / 2
    return (M + col * (pw + GUT), GRID_Y + row * (PH + GUT), pw, PH)


def body(col, row):
    """Inner box of a panel: everything below the title, above the source line."""
    x, y, w, h = cell(col, row)
    return x + PAD, y + BODY_TOP, w - 2 * PAD, h - BODY_TOP - SRC_H - 4


def nav(active, theme="light"):
    """Tab strip: five equal segments, active one filled with the brand colour."""
    out = []
    gap = 6
    tw = (W - 2 * M - gap * (len(TABS) - 1)) / len(TABS)
    for i, name in enumerate(TABS):
        x = M + i * (tw + gap)
        on = name == active
        out.append(r(x, 18, tw, NAV_H, "brand.primary" if on else "surface.raised", theme,
                     radius=6, stroke=None if on else "border.subtle"))
        out.append(t(x, 18 + 9, tw, 18, name,
                     "text.on-brand" if on else "text.secondary", theme, size=8.5,
                     bold=True, caps=True, spacing=0.12, align="center"))
    return out


def panel_head(x, y, w, title, theme="light", kicker=None):
    out = []
    ty = y + PAD
    if kicker:
        out.append(t(x + PAD, ty, w - 2 * PAD, 12, kicker, "brand.primary", theme,
                     size=7.5, bold=True, caps=True, spacing=0.14))
        ty += 12
    out.append(t(x + PAD, ty, w - 2 * PAD, 30, title, "text.primary", theme,
                 size=12.5, bold=True, leading=1.22))
    return out


def source(x, y, w, h, text, theme="light"):
    return t(x + PAD, y + h - SRC_H, w - 2 * PAD, 10, text, "text.muted", theme,
             size=7, leading=1.1)


def panel(col, row, title, body, src, theme="light", kicker=None):
    x, y, w, h = cell(col, row)
    out = [r(x, y, w, h, "surface.raised", theme, radius=PANEL_R, stroke="border.subtle"),
           *panel_head(x, y, w, title, theme, kicker)]
    out.extend(body)
    out.append(source(x, y, w, h, src, theme))
    return out


def tbl(x, y, w, header, rows, theme="light", rowh: float = 17, value_w=64, badge=False,
        rule=True):
    """Hairline table: caps header, one hairline under it, 18px rows, numbers right."""
    out = []
    if header:
        hx0 = x
        for i, (label, align) in enumerate(header):
            out.append(t(hx0, y, w if i == len(header) - 1 else value_w, 12, label,
                         "text.secondary", theme, size=7.5, bold=True, caps=True,
                         spacing=0.1, align=align))
        if rule:
            out.append(r(x, y + 14, w, 1, "border.strong", theme))
    cy = y + (18 if header else 0)
    for i, row in enumerate(rows):
        cells = row if isinstance(row, (list, tuple)) else [row]
        if badge:
            out.append(r(x, cy + 4, 11, 11, "brand.primary", theme, radius=2))
            out.append(t(x, cy + 4.5, 11, 10, str(i + 1), "text.on-brand", theme,
                         size=7, bold=True, align="center"))
            out.append(t(x + 17, cy, w - 17 - value_w, rowh, cells[0], "text.primary",
                         theme, size=9.5, leading=1.2))
            vx = x + w - value_w
        else:
            out.append(t(x, cy, w - value_w, rowh, cells[0], "text.primary", theme,
                         size=9.5, leading=1.2))
            vx = x + w - value_w
        if len(cells) > 1:
            out.append(t(vx, cy, value_w, rowh, str(cells[1]), "text.primary", theme,
                         size=9.5, bold=True, align="right", leading=1.2))
        if i < len(rows) - 1:
            out.append(r(x, cy + rowh - 1, w, 1, "border.subtle", theme))
        cy += rowh
    return out


def kpi(x, y, w, number, label, theme="light", size=26, color="text.primary"):
    return [t(x, y, w, size + 6, number, color, theme, size=size, bold=True, leading=1.0,
              font="mono"),
            t(x, y + size + 4, w, 24, label, "text.secondary", theme, size=8, leading=1.3)]


def bullets(x, y, w, items, theme="light", size=9.5, rowh=15):
    out = []
    for i, item in enumerate(items):
        out.append(r(x, y + i * rowh + 4, 3, 3, "brand.primary", theme))
        out.append(t(x + 9, y + i * rowh, w - 9, rowh, item, "text.primary", theme,
                     size=size, leading=1.25))
    return out


def pyramid(x, y, w, h, levels, theme="light"):
    """Stepped pyramid: centred bands, widest at the base, series ladder for fill."""
    out = []
    n = len(levels)
    gap = 3
    bh = (h - gap * (n - 1)) / n
    for i, (label, note) in enumerate(levels):
        # apex at the top: narrow first band, widest at the base
        frac = 0.5 + i * (0.5 / max(1, n - 1))
        bw = w * frac
        bx = x + (w - bw) / 2
        by = y + i * (bh + gap)
        fill = f"chart.series.{min(4, i + 1)}"
        fg = "text.on-brand" if i < 2 else "text.primary"
        out.append(r(bx, by, bw, bh, fill, theme, radius=3))
        out.append(t(bx + 8, by + bh / 2 - 7, bw - 16, 14, label, fg, theme, size=8.5,
                     bold=True, leading=1.1))
        if note:
            out.append(t(bx + 8, by + bh / 2 + 6, bw - 16, 12, note, fg, theme, size=7,
                         leading=1.1))
    return out


def hub(cx, cy, radius, center, ring, theme="light"):
    out = [r(cx - radius, cy - radius, radius * 2, radius * 2, "brand.primary", theme,
             radius=int(radius)),
           t(cx - radius, cy - 7, radius * 2, 14, center, "text.on-brand", theme,
             size=9, bold=True, align="center")]
    # satellites sit left / upper-right / lower-right so nothing touches the panel edge
    spots = [(cx - radius - 96, cy - 8), (cx + radius + 14, cy - 34),
             (cx + radius + 14, cy + 18)]
    for i, label in enumerate(ring[:3]):
        bx, by = spots[i]
        if i == 0:                      # left satellite -> line runs right to the hub
            out.append(r(bx + 80, by + 7, cx - radius - (bx + 80), 1, "border.strong", theme))
        else:                           # right satellites -> line runs left to the hub
            out.append(r(cx + radius, by + 7, bx - (cx + radius), 1, "border.strong", theme))
        out.append(r(bx, by, 80, 16, "surface.base", theme, radius=3, stroke="border.strong"))
        out.append(t(bx, by + 3, 80, 12, label, "text.primary", theme, size=7,
                     align="center"))
    return out


def radial(x, y, w, h, center, items, theme="light", radius=26):
    """Hub centred, satellites on the top and bottom rows only (no collision band)."""
    out = []
    cw, ch = w / 3, h / 3
    cx, cy = x + cw * 1.5, y + ch * 1.5
    out.append(r(cx - radius, cy - radius, radius * 2, radius * 2, "brand.primary", theme,
                 radius=int(radius)))
    out.append(t(cx - radius + 4, cy - 8, radius * 2 - 8, 16, center, "text.on-brand", theme,
                 size=8.5, bold=True, align="center", leading=1.05))
    slots = [(1, 0), (0, 0), (2, 0), (0, 2), (2, 2), (1, 2)]
    for i, label in enumerate(items[:6]):
        c, rw = slots[i]
        bx = x + c * cw + 6
        chip = min(28, ch * 0.42)
        by = y + rw * ch + (ch - chip) / 2
        bw = cw - 12
        out.append(r(bx, by, bw, chip, "surface.base", theme, radius=3,
                     stroke="border.strong"))
        out.append(t(bx, by + chip / 2 - 5, bw, 12, label, "text.primary", theme,
                     size=6.8, align="center"))
    return out


def layers_matrix(x, y, w, h, row_labels, col_labels, cells, theme="light", label_w=64):
    """Rows x columns grid with a label column and a header row (ESG-framework shape)."""
    out = []
    head = 17
    gw = w - label_w
    cw = gw / len(col_labels)
    rh = (h - head) / len(row_labels)
    for j, cl in enumerate(col_labels):
        out.append(t(x + label_w + j * cw + 3, y + 1, cw - 6, head - 2, cl, "text.muted",
                     theme, size=6.8, bold=True, align="center", leading=1.0))
    for i, rl in enumerate(row_labels):
        ry = y + head + i * rh
        out.append(t(x + 1, ry + rh / 2 - 8, label_w - 8, 16, rl, "text.primary", theme,
                     size=7.5, bold=True, leading=1.1))
        for j in range(len(col_labels)):
            cell_txt = cells[i][j] if i < len(cells) and j < len(cells[i]) else ""
            bx = x + label_w + j * cw
            out.append(r(bx + 1, ry + 1, cw - 2, rh - 2, "surface.band", theme, radius=3,
                         stroke="border.subtle"))
            out.append(t(bx + 8, ry + 6, cw - 16, rh - 10, cell_txt, "text.secondary", theme,
                         size=6.8, leading=1.15))
    return out


def kpi_grid(x, y, w, h, items, theme="light", cols=3):
    """n metrics in a hairline-separated grid; number first, label under."""
    out = []
    rows = (len(items) + cols - 1) // cols
    cw, ch = w / cols, h / rows
    size = 22 if cols >= 4 else 26
    for i, (num, lab) in enumerate(items):
        c, rw = i % cols, i // cols
        bx, by = x + c * cw, y + rw * ch
        if c:
            out.append(r(bx, by + 4, 1, ch - 8, "border.subtle", theme))
        if rw:
            out.append(r(bx + 4, by, cw - 8, 1, "border.subtle", theme))
        out.append(t(bx + 6, by + 4, cw - 12, size + 4, num, "text.primary", theme, size=size,
                     bold=True, leading=1.0, font="mono"))
        out.append(t(bx + 6, by + size + 8, cw - 12, 20, lab, "text.secondary", theme, size=7.5,
                     leading=1.2))
    return out


def ticks(x, y, w, items, theme="light", cols=1, rowh=17, size=8.5):
    """Checklist: hollow square + text, one or two columns."""
    out = []
    cw = w / cols
    for i, item in enumerate(items):
        c, rw = i % cols, i // cols
        bx = x + c * cw
        by = y + rw * rowh
        out.append(r(bx, by + 4, 5, 5, "surface.base", theme, stroke="brand.primary"))
        out.append(t(bx + 10, by, cw - 10, rowh, item, "text.primary", theme, size=size,
                     leading=1.25))
    return out


def flow(x, y, w, steps, theme="light", h=34):
    out = []
    n = len(steps)
    gap = 16
    bw = (w - gap * (n - 1)) / n
    for i, (head, note) in enumerate(steps):
        bx = x + i * (bw + gap)
        out.append(r(bx, y, bw, h, "surface.band", theme, radius=4, stroke="border.subtle"))
        out.append(t(bx + 7, y + 5, bw - 14, 12, head, "text.primary", theme, size=8,
                     bold=True, leading=1.1))
        out.append(t(bx + 7, y + 18, bw - 14, 12, note, "text.secondary", theme, size=7,
                     leading=1.1))
        if i < n - 1:
            out.append(t(bx + bw + 3, y + h / 2 - 8, 12, 14, "›", "brand.primary", theme,
                         size=12, bold=True, align="center"))
    return out


def stackbar(x, y, w, rows, theme="light", h=26, gap=6):
    """Layered stack: label column left, one band per row, share of width."""
    out = []
    for i, (label, value, pct) in enumerate(rows):
        by = y + i * (h + gap)
        out.append(t(x, by + 6, 96, 14, label, "text.primary", theme, size=8.5, bold=True))
        out.append(r(x + 100, by, w - 100 - 46, h, "surface.band", theme, radius=3))
        out.append(r(x + 100, by, (w - 100 - 46) * pct, h,
                     f"chart.series.{min(4, i + 1)}", theme, radius=3))
        out.append(t(x + w - 44, by + 7, 44, 14, value, "text.primary", theme, size=8.5,
                     bold=True, align="right"))
    return out


def matrix(x, y, w, h, quads, theme="light"):
    out = []
    gap = 4
    qw, qh = (w - gap) / 2, (h - gap) / 2
    for i, (head, note) in enumerate(quads):
        cx = x + (i % 2) * (qw + gap)
        cy = y + (i // 2) * (qh + gap)
        out.append(r(cx, cy, qw, qh, "surface.band" if i % 3 else "brand.subtle", theme,
                     radius=4, stroke="border.subtle"))
        out.append(t(cx + 8, cy + 8, qw - 16, 12, head, "text.primary", theme, size=8.5,
                     bold=True, caps=True, spacing=0.08))
        out.append(t(cx + 8, cy + 22, qw - 16, qh - 28, note, "text.secondary", theme,
                     size=7.5, leading=1.25))
    return out


# ------------------------------------------------------------------ slides
SLIDES = []


def add(theme, title, active, elements, footer_note, page):
    els = [*nav(active, theme),
           t(M, TITLE_Y, W - 2 * M - 60, 22, title, "text.primary", theme, size=15,
             bold=True, leading=1.15),
           r(M, RULE_Y, W - 2 * M, 1, "border.strong", theme),
           *elements,
           r(M, H - 30, W - 2 * M, 1, "border.subtle", theme),
           t(M, H - 22, W - 2 * M - 60, 12, footer_note, "text.muted", theme, size=7.5),
           t(W - M - 40, H - 22, 40, 12, f"{page:02d}", "text.muted", theme, size=7.5,
             align="right")]
    SLIDES.append({"theme": theme, "elements": els})


FOOT = f"Signal v0.10 · analyst layout · palet {PALETTE}"

# 01 — TABLE
bx0, by0, bw, bh = body(0, 0)
bx1, _, _, _ = body(1, 0)
add("light", "Kesiapan commissioning: lima celah bukti, satu pemilik per celah", "Table", [
    *panel(0, 0, "Jadwal bocor di lima titik handover",
           tbl(bx0, by0, bw, [("Tahap", "left"), ("Hari", "right")],
               [("Commissioning plan", 3), ("Pre-functional check", 6), ("Functional test", 4),
                ("Integrated system", 2), ("Handover dossier", 2)], badge=True),
           "Sumber: log commissioning Q4 2026, 18 paket", kicker="01 — TEMUAN"),
    *panel(1, 0, "Kesiapan diukur per paket, bukan per sistem",
           tbl(bx1, by0, bw, [("Paket", "left"), ("Siap", "right")],
               [("AHU & tata udara", "92%"), ("Panel listrik", "74%"), ("Plumbing", "58%"),
                ("Otomasi BMS", "41%")]),
           "Sumber: readiness register, 24 Nov 2026", kicker="02 — KESIAPAN"),
    *panel(0, 1, "Tiap milestone menuntut tiga jenis bukti",
           tbl(bx0, body(0, 1)[1], bw, [("Milestone", "left"), ("Bukti", "right")],
               [("Pre-functional", "Dokumen"), ("Functional", "Foto + log"),
                ("Integrated", "Tanda tangan"), ("Handover", "Dossier")]),
           "Sumber: kontrak EPC pasal 9.3", kicker="03 — BUKTI"),
    *panel(1, 1, "Satu nama per temuan, tenggat di kalender",
           tbl(bx1, body(1, 1)[1], bw, [("Pemilik", "left"), ("Tenggat", "right")],
               [("Rina — mekanikal", "12 Des"), ("Adi — elektrikal", "14 Des"),
                ("Sari — otomasi", "18 Des")]),
           "Sumber: rapat mingguan, keputusan 21 Nov", kicker="04 — PEMILIK"),
    *panel(0, 2, "Rework menelan 3,4 hari per minggu", [
        *kpi(bx0, body(0, 2)[1], bw, "3,4 hari", "rata-rata per minggu, 6 minggu terakhir"),
        *tbl(bx0, body(0, 2)[1] + 66, bw, None,
             [("Penyebab: dokumen", "48%"), ("Penyebab: akses", "31%")])],
        "Sumber: time sheet tim commissioning", kicker="05 — BIAYA"),
    *panel(1, 2, "Progres 12 bulan, bukan 12 minggu",
           tbl(bx1, body(1, 2)[1], bw, None,
               [("Waktu siklus", "−12 pts"), ("Frekuensi audit", "3×"),
                ("Waktu buka-tutup", "−50%")]),
           "Sumber: baseline 2025 vs capaian 2026", kicker="06 — HASIL"),
], FOOT, 1)

# 02 — CHART
add("light", "Di mana waktunya habis, dan seberapa yakin kita", "Chart", [
    *panel(0, 0, "Waktu per fase: rencana vs aktual", [
        D.chart(bx0, by0, bw, bh,
                ["Plan", "Pre-func", "Func", "Integ", "Handover"],
                [{"name": "Rencana", "values": [3, 6, 4, 2, 2], "color": "chart.series.2"},
                 {"name": "Aktual", "values": [4, 7, 5, 3, 2], "color": "chart.series.1"}])],
        "Sumber: log commissioning, hari kerja", kicker="01 — DURASI"),
    *panel(1, 0, "Temuan per sistem, urut dari terbesar", [
        hbar(bx1, by0, bw, bh,
             [("HVAC", 34), ("Elektrikal", 28), ("Plumbing", 21), ("BMS", 14), ("Fire", 9)])],
        "Sumber: punch list 24 Nov 2026, n=106", kicker="02 — TEMUAN"),
    *panel(0, 1, "Kesiapan paket: sisa pekerjaan di ujung bar", [
        hstack(bx0, body(0, 1)[1], bw, bh,
               [("AHU", 92, 100), ("Listrik", 74, 100), ("Plumbing", 58, 100),
                ("BMS", 41, 100)], unit="%")],
        "Sumber: readiness register", kicker="03 — KESIAPAN"),
    *panel(1, 1, "Enam indikator yang dipantau mingguan", [
        *[donut(bx1 + i * 106, body(1, 1)[1] + 22, 46, v, lab)
          for i, (v, lab) in enumerate([(92, "AHU"), (74, "Listrik"), (58, "Plumbing"),
                                        (41, "BMS"), (66, "Dokumen"), (88, "Safety")])]],
        "Sumber: dashboard commissioning", kicker="04 — INDIKATOR"),
    *panel(0, 2, "Volume handover naik 2,6× dalam empat bulan", [
        hbar(bx0, body(0, 2)[1], bw, bh,
             [("Sep", 12), ("Okt", 18), ("Nov", 26), ("Des", 31)], label_w=40)],
        "Sumber: jadwal serah terima", kicker="05 — VOLUME"),
    *panel(1, 2, "Penyebab tunggu: dokumen, bukan alat", [
        hbar(bx1, body(1, 2)[1], bw, bh,
             [("Dokumen", 26), ("Akses", 19), ("Alat", 14), ("Cuaca", 8)],
             color="chart.series.4")],
        "Sumber: catatan delay, jam", kicker="06 — PENYEBAB"),
], FOOT, 2)

# 03 — PANEL
add("light", "Satu halaman, enam blok: apa yang berubah, siapa yang menjalankan", "Panel", [
    *panel(0, 0, "Nilai kontrak yang dipertaruhkan", [
        *kpi(bx0, by0, bw, "Rp 4,2 M", "tertahan sampai dossier handover lengkap"),
        *tbl(bx0, by0 + 66, bw, None,
             [("Per hari terlambat", "Rp 38 jt"), ("Batas kontrak", "31 Des")])],
        "Sumber: kontrak EPC, adendum 2", kicker="01 — EKSPOSUR"),
    *panel(1, 0, "Kami mengubah cara bukti dikumpulkan", bullets(
        bx1, by0 + 2, bw,
        ["Satu register, bukan tujuh spreadsheet",
         "Foto lapangan langsung menempel ke temuan",
         "Tanda tangan digital di lokasi, bukan di kantor",
         "Status terbaca semua pihak tanpa rapat"], rowh=17),
        "Sumber: desain proses, Nov 2026", kicker="02 — PERUBAHAN"),
    *panel(0, 1, "Tiga alur kerja yang dipertahankan",
           tbl(bx0, body(0, 1)[1], bw, [("Alur", "left"), ("Pemilik", "right")],
               [("Pre-functional", "Mekanikal"), ("Functional", "Elektrikal"),
                ("Integrated", "Otomasi")], badge=True),
           "Sumber: SOP commissioning 2026", kicker="03 — ALUR"),
    *panel(1, 1, "Yang berhenti minggu ini",
           tbl(bx1, body(1, 1)[1], bw, None,
               [("Laporan harian manual", "stop"), ("Rapat status 60 menit", "stop"),
                ("Tanda tangan basah", "stop")]),
           "Sumber: keputusan steering 21 Nov", kicker="04 — DIHENTIKAN"),
    *panel(0, 2, "Yang mulai Senin",
           tbl(bx0, body(0, 2)[1], bw, None,
               [("Dashboard 07.00", "mulai"), ("Huddle 15 menit", "mulai"),
                ("Audit sampel 5%", "mulai")]),
           "Sumber: rencana implementasi", kicker="05 — DIMULAI"),
    *panel(1, 2, "Satu kalimat untuk seluruh tim", [
        r(bx1, body(1, 2)[1] + 2, bw, bh - 12, "brand.primary", "light", radius=4),
        t(bx1 + 14, body(1, 2)[1] + 22, bw - 28, 50,
          "Kalau tidak ada bukti, itu belum selesai.", "text.on-brand", "light", size=12,
          bold=True, leading=1.25)],
        "Sumber: standar internal", kicker="06 — PRINSIP"),
], FOOT, 3)

# 04 — FRAMEWORK
add("light", "Kerangka: dari temuan lapangan ke keputusan anggaran", "Framework", [
    *panel(0, 0, "Empat lapis bukti, satu arah", pyramid(
        bx0, by0, bw, bh,
        [("Keputusan", "owner: steering"), ("Validasi", "audit sampel"),
         ("Bukti", "foto, log, tanda tangan"), ("Temuan", "punch list")]),
        "Sumber: kerangka commissioning Signal", kicker="01 — LAPIS"),
    *panel(1, 0, "Satu register, lima pihak membaca angka yang sama", radial(
        bx1, by0, bw, bh, "Register",
        ["Kontraktor", "Owner", "Vendor", "Konsultan", "Bank"]),
        "Sumber: model tata kelola", kicker="02 — PUSAT"),
    *panel(0, 1, "Tiga lapis, tiga pilar: siapa mengerjakan apa", layers_matrix(
        bx0, body(0, 1)[1] + 2, bw, bh - 4,
        ["Orang", "Proses", "Sistem"],
        ["Catat", "Verifikasi", "Putuskan"],
        [["Teknisi", "Auditor", "Steering"],
         ["Checklist", "Sampel 5%", "Rapat 15 mnt"],
         ["Form + foto", "Log audit", "Dashboard"]]),
        "Sumber: matriks peran, Nov 2026", kicker="03 — MATRIKS"),
    *panel(1, 1, "Empat langkah, satu pemilik per langkah", flow(
        bx1, body(1, 1)[1] + 22, bw,
        [("Catat", "lapangan"), ("Verifikasi", "audit"), ("Putuskan", "steering"),
         ("Tutup", "dossier")]),
        "Sumber: alur keputusan", kicker="04 — ALUR"),
    *panel(0, 2, "Prioritas: dampak tinggi, usaha rendah", matrix(
        bx0, body(0, 2)[1], bw, bh,
        [("Quick win", "Register + foto"), ("Proyek", "Integrasi BMS"),
         ("Isi ulang", "Template audit"), ("Tunda", "Dashboard vendor")]),
        "Sumber: workshop prioritisasi", kicker="05 — PRIORITAS"),
    *panel(1, 2, "Hasil yang dijanjikan", kpi_grid(
        bx1, body(1, 2)[1], bw, bh - 6,
        [("−12 pts", "siklus handover"), ("3×", "frekuensi audit"),
         ("−50%", "waktu buka-tutup")]),
        "Sumber: target 2027", kicker="06 — HASIL"),
], FOOT, 4)

# 05 — VISUAL
add("light", "Bukti lapangan: foto, blok warna, dan angka yang menahan mata", "Visual", [
    *panel(0, 0, "Foto penuh panel, callout menempel di atasnya", [
        img(bx0, by0, bw, bh, "photo-43.png", radius=4),
        r(bx0 + 8, by0 + bh - 30, 150, 24, "surface.base", "light", radius=3),
        t(bx0 + 14, by0 + bh - 25, 138, 14, "AHU-02 · commissioning",
          "text.primary", "light", size=8, bold=True)],
        "Sumber: dokumentasi lapangan, 24 Nov", kicker="01 — FOTO"),
    *panel(1, 0, "Angka besar memecah kepadatan teks", [
        *kpi(bx1, by0, bw, "106", "temuan terbuka, 18 paket"),
        *tbl(bx1, by0 + 66, bw, None,
             [("Ditutup minggu ini", "34"), ("Lewat tenggat", "7")])],
        "Sumber: register per 24 Nov", kicker="02 — ANGKA"),
    *panel(0, 1, "Blok warna penuh untuk satu pesan", [
        r(bx0, body(0, 1)[1] + 2, bw, bh - 12, "brand.primary", "light", radius=4),
        t(bx0 + 14, body(0, 1)[1] + 18, bw - 28, 30, "31 Des", "text.on-brand", "light",
          size=24, bold=True, leading=1.0, font="mono"),
        t(bx0 + 14, body(0, 1)[1] + 52, bw - 28, 44,
          "batas kontrak. Sesudah ini, biaya keterlambatan berjalan.",
          "text.on-brand", "light", size=9.5, leading=1.3)],
        "Sumber: adendum kontrak", kicker="03 — TENGGAT"),
    *panel(1, 1, "Dua foto berdampingan, satu keterangan", [
        img(bx1, body(1, 1)[1] + 2, 128, bh - 14, "photo-43.png", radius=4),
        img(bx1 + 136, body(1, 1)[1] + 2, 128, bh - 14, "photo-cover.png", radius=4),
        t(bx1 + 274, body(1, 1)[1] + 4, bw - 274, bh - 18,
          "Sebelum: temuan di kertas.\nSesudah: temuan dengan foto, jam, dan nama.",
          "text.secondary", "light", size=8.5, leading=1.45)],
        "Sumber: dokumentasi internal", kicker="04 — SEBELUM/SESUDAH"),
    *panel(0, 2, "Tiga angka, satu baris, tanpa dekorasi", [
        *kpi(bx0, body(0, 2)[1] + 16, 180, "92%", "AHU"),
        *kpi(bx0 + 190, body(0, 2)[1] + 16, 180, "74%", "Listrik"),
        *kpi(bx0 + 380, body(0, 2)[1] + 16, 180, "41%", "BMS")],
        "Sumber: readiness register", kicker="05 — RINGKASAN"),
    *panel(1, 2, "Foto kecil, teks yang menjelaskan", [
        img(bx1, body(1, 2)[1] + 2, 92, bh - 14, "photo-cover.png", radius=4),
        *ticks(bx1 + 104, body(1, 2)[1] + 6, bw - 104,
                ["Foto menempel ke temuan, bukan ke folder",
                 "Nama pemilik terlihat di lapangan",
                 "Riwayat perubahan tidak hilang"], rowh=19)],
        "Sumber: panduan lapangan", kicker="06 — CARA"),
], FOOT, 5)




# ------------------------------------------------------------------ pptx
def add_chart(slide, el, theme):
    x, y, w, h = (Emu(int(el[k] * PX)) for k in ("x", "y", "w", "h"))
    kind = el["kind"]
    if kind == "hbar":
        cd = CategoryChartData()
        cd.categories = [lab for lab, _ in el["rows"]][::-1]
        cd.add_series("nilai", [v for _, v in el["rows"]][::-1])
        gf = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, x, y, w, h, cd)
        ch = gf.chart
        ch.has_legend = False
        ch.has_title = False
        plot = ch.plots[0]
        plot.gap_width = 55
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.font.size = Pt(7)
        dl.font.name = D.font_of("mono")
        dl.font.color.rgb = RGBColor.from_string(hx(theme, "text.primary"))
        dl.position = XL_LABEL_POSITION.OUTSIDE_END
        ser = plot.series[0]
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = RGBColor.from_string(hx(theme, el["color"]))
        ch.value_axis.maximum_scale = el["max"] * 1.18
        ch.value_axis.minimum_scale = 0
        ch.value_axis.has_major_gridlines = False
        ch.value_axis.visible = False
        ch.category_axis.has_major_gridlines = False
        ch.category_axis.format.line.color.rgb = RGBColor.from_string(hx(theme, "border.subtle"))
        ch.category_axis.tick_labels.font.size = Pt(7)
        ch.category_axis.tick_labels.font.name = D.font_of("body")
        ch.category_axis.tick_labels.font.color.rgb = RGBColor.from_string(
            hx(theme, "text.secondary"))
        return
    if kind == "hstack":
        cd = CategoryChartData()
        cd.categories = [lab for lab, _, _ in el["rows"]][::-1]
        cd.add_series("selesai", [p for _, p, _ in el["rows"]][::-1])
        cd.add_series("sisa", [wh - p for _, p, wh in el["rows"]][::-1])
        gf = slide.shapes.add_chart(XL_CHART_TYPE.BAR_STACKED, x, y, w, h, cd)
        ch = gf.chart
        ch.has_legend = False
        ch.has_title = False
        plot = ch.plots[0]
        plot.gap_width = 50
        plot.overlap = 100
        for i, name in enumerate(("chart.series.1", "border.subtle")):
            ser = plot.series[i]
            ser.format.fill.solid()
            ser.format.fill.fore_color.rgb = RGBColor.from_string(hx(theme, name))
        ch.value_axis.maximum_scale = 100
        ch.value_axis.minimum_scale = 0
        ch.value_axis.has_major_gridlines = False
        ch.value_axis.visible = False
        ch.category_axis.has_major_gridlines = False
        ch.category_axis.format.line.color.rgb = RGBColor.from_string(hx(theme, "border.subtle"))
        ch.category_axis.tick_labels.font.size = Pt(7)
        ch.category_axis.tick_labels.font.name = D.font_of("body")
        ch.category_axis.tick_labels.font.color.rgb = RGBColor.from_string(
            hx(theme, "text.secondary"))
        return
    if kind == "donut":
        cd = CategoryChartData()
        cd.categories = ["nilai", "sisa"]
        cd.add_series("p", (el["value"], 100 - el["value"]))
        gf = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, x, y, w, h, cd)
        ch = gf.chart
        ch.has_legend = False
        ch.has_title = False
        plot = ch.plots[0]
        plot.has_data_labels = False
        for i, name in enumerate(("chart.series.1", "border.subtle")):
            pt = plot.series[0].points[i]
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = RGBColor.from_string(hx(theme, name))
        hole = ch.plots[0]
        hole.donut_hole_size = 66
        box = slide.shapes.add_textbox(x, Emu(int((el["y"] + el["h"] / 2 - 8) * PX)),
                                       w, Emu(int(16 * PX)))
        tf = box.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = f"{el['value']}%"
        run.font.size = Pt(9)
        run.font.bold = True
        run.font.name = D.font_of("mono")
        run.font.color.rgb = RGBColor.from_string(hx(theme, "text.primary"))
        lab = slide.shapes.add_textbox(x, Emu(int((el["y"] + el["h"] - 2) * PX)), w,
                                       Emu(int(12 * PX)))
        tf2 = lab.text_frame
        tf2.margin_left = tf2.margin_right = tf2.margin_top = tf2.margin_bottom = 0
        p2 = tf2.paragraphs[0]
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = el["label"]
        r2.font.size = Pt(6.5)
        r2.font.name = D.font_of("body")
        r2.font.color.rgb = RGBColor.from_string(hx(theme, "text.secondary"))
        return
    D.add_chart(slide, el, theme)


def render_pptx(path: Path) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(W * PX), Emu(H * PX)
    blank = prs.slide_layouts[6]
    for spec in SLIDES:
        theme = spec["theme"]
        slide = prs.slides.add_slide(blank)
        for el in spec["elements"]:
            x, y, w, h = (Emu(int(el[k] * PX)) for k in ("x", "y", "w", "h"))
            if el["kind"] == "rect":
                rad = int(el.get("radius") or 0)
                if rad > 0:
                    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
                    shape.adjustments[0] = min(0.5, rad / min(el["w"], el["h"]))
                else:
                    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
                shape.fill.solid()
                shape.fill.fore_color.rgb = RGBColor.from_string(hx(theme, el["fill"]))
                if el.get("stroke"):
                    shape.line.color.rgb = RGBColor.from_string(hx(theme, el["stroke"]))
                    shape.line.width = Pt(el.get("stroke_w", 1) * 0.75)
                else:
                    shape.line.fill.background()
                shape.shadow.inherit = False
                continue
            if el["kind"] == "image":
                rad = int(el.get("radius") or 0)
                src = (D.rounded_photo(D.photo_src(el["src"]), int(el["w"]), int(el["h"]), rad)
                       if rad > 0 else D.PHOTOS / D.photo_src(el["src"]))
                slide.shapes.add_picture(str(src), x, y, w, h)
                continue
            if el["kind"] in ("chart", "hbar", "hstack", "donut"):
                add_chart(slide, el, theme)
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
                f.name = D.font_of(el.get("font", "body"))
                f.color.rgb = RGBColor.from_string(hx(theme, el["color"]))
                if el.get("spacing"):
                    f._rPr.set("spc", str(int(el["spacing"] * 100)))
    prs.save(str(path))


# ------------------------------------------------------------------ html
def el_html(el, theme):
    base = (f"position:absolute;left:{el['x']}px;top:{el['y']}px;"
            f"width:{el['w']}px;height:{el['h']}px;")
    col = lambda name: str(tok(theme, name))
    if el["kind"] == "rect":
        rad = el.get("radius") or 0
        stroke = (f"border:{el.get('stroke_w', 1)}px solid {col(el['stroke'])};"
                  if el.get("stroke") else "")
        return (f'<div style="{base}background:{col(el["fill"])};{stroke}'
                f'border-radius:{rad}px;"></div>')
    if el["kind"] == "image":
        rad = el.get("radius") or 0
        return (f'<img src="file://{D.PHOTOS / D.photo_src(el["src"])}" style="{base}'
                f'object-fit:cover;border-radius:{rad}px;display:block;">')
    if el["kind"] == "hbar":
        rows, maxv = el["rows"], el["max"]
        lab_w = el.get("label_w", 78)
        rowh = (el["h"]) / len(rows)
        parts = [f'<div style="{base}">']
        for i, (lab, v) in enumerate(rows):
            bw = (el["w"] - lab_w - 30) * (v / maxv)
            parts.append(
                f'<div style="position:absolute;left:0;top:{i * rowh + 2}px;width:{lab_w}px;'
                f'height:{rowh - 3}px;font-size:8px;color:{col("text.secondary")};'
                f'display:flex;align-items:center;">{lab}</div>'
                f'<div style="position:absolute;left:{lab_w}px;top:{i * rowh + 2}px;'
                f'width:{max(2, bw)}px;height:{rowh - 3}px;background:{col(el["color"])};'
                f'border-radius:2px;"></div>'
                f'<div style="position:absolute;left:{lab_w + max(2, bw) + 5}px;'
                f'top:{i * rowh + 2}px;height:{rowh - 3}px;font-size:8px;font-weight:700;'
                f'color:{col("text.primary")};display:flex;align-items:center;">{v}</div>')
        parts.append("</div>")
        return "".join(parts)
    if el["kind"] == "hstack":
        rowh = el["h"] / len(el["rows"])
        parts = [f'<div style="{base}">']
        for i, (lab, part, whole) in enumerate(el["rows"]):
            pct = part / whole
            parts.append(
                f'<div style="position:absolute;left:0;top:{i * rowh + 2}px;width:78px;'
                f'height:{rowh - 4}px;font-size:8px;color:{col("text.secondary")};'
                f'display:flex;align-items:center;">{lab}</div>'
                f'<div style="position:absolute;left:78px;top:{i * rowh + 2}px;'
                f'width:{el["w"] - 78}px;height:{rowh - 4}px;background:{col("border.subtle")};'
                f'border-radius:2px;overflow:hidden;">'
                f'<div style="width:{pct * 100}%;height:100%;background:'
                f'{col("chart.series.1")};"></div></div>'
                f'<div style="position:absolute;right:0;top:{i * rowh + 2}px;'
                f'height:{rowh - 4}px;font-size:8px;font-weight:700;color:'
                f'{col("text.primary")};display:flex;align-items:center;">{part}%</div>')
        parts.append("</div>")
        return "".join(parts)
    if el["kind"] == "donut":
        d = el["w"]
        deg = el["value"] / 100 * 360
        return (f'<div style="{base}">'
                f'<div style="position:absolute;left:0;top:0;width:{d}px;height:{d}px;'
                f'border-radius:50%;background:conic-gradient({col(el["color"])} {deg}deg,'
                f' {col("border.subtle")} {deg}deg);"></div>'
                f'<div style="position:absolute;left:7px;top:7px;width:{d - 14}px;'
                f'height:{d - 14}px;border-radius:50%;background:{col("surface.raised")};'
                f'display:flex;align-items:center;justify-content:center;font-size:9px;'
                f'font-weight:700;color:{col("text.primary")};">{el["value"]}%</div>'
                f'<div style="position:absolute;left:0;top:{d + 1}px;width:{d}px;'
                f'font-size:7px;color:{col("text.secondary")};text-align:center;">'
                f'{el["label"]}</div></div>')
    if el["kind"] == "chart":
        return PV.svg_chart(el, theme)
    text = el["text"].upper() if el.get("caps") else el["text"]
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace("\n", "<br>")
    return (f'<div style="{base}font-family:\'{D.font_of(el.get("font", "body"))}\';'
            f'font-size:{el["size"]}px;color:{col(el["color"])};'
            f'font-weight:{700 if el.get("bold") else 400};'
            f'line-height:{el.get("leading", 1.2)};letter-spacing:{el.get("spacing", 0)}em;'
            f'text-align:{el.get("align", "left")};white-space:pre-wrap;'
            f'font-variant-numeric:tabular-nums;">{text}</div>')


def render_html(path: Path) -> None:
    slides = []
    for i, spec in enumerate(SLIDES, 1):
        theme = spec["theme"]
        inner = "\n".join(el_html(el, theme) for el in spec["elements"])
        slides.append(f'<section class="slide" id="s{i}" style="background:'
                      f'{tok(theme, "surface.base")};">{inner}</section>')
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Analyst layout — {PALETTE}</title>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#333;display:flex;flex-direction:column;gap:24px;padding:24px;width:{W + 48}px}}
.slide{{position:relative;width:{W}px;height:{H}px;overflow:hidden;font-family:Manrope,sans-serif}}
</style></head><body>
{chr(10).join(slides)}
</body></html>"""
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    out = ROOT / "examples" / f"analyst-{PALETTE}.pptx"
    render_pptx(out)
    html = ROOT / "examples" / f"preview-analyst-{PALETTE}.html"
    render_html(html)
    print("wrote", out.name, "+", html.name, len(SLIDES), "slides")
