#!/usr/bin/env python3
"""Pitch deck v0.4 — one slide spec, two renderers (pptx + html preview).

Adds the Style 1 module set (KPI cards, charts, pricing, budget, contact) and
photo slots on top of the v0.3 language. Coordinates are slide pixels (1280x720);
1px = 9525 EMU, so the pptx is exactly 13.333in x 7.5in and the preview matches.

    python build/photos.py      # placeholders (replace the PNGs with real shots)
    python build/deck.py        # examples/pitch-deck.pptx
"""
from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

ROOT = Path(__file__).resolve().parent.parent
TOK = json.loads((ROOT / "dist" / "json" / "tokens.resolved.json").read_text())
LIGHT, DARK = TOK["light"], TOK["dark"]

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


def card(x, y, w, h, number, label, delta, theme="dark", delta_color="brand.primary"):
    return [r(x, y, w, h, "surface.raised", theme, radius=18),
            t(x + 24, y + 28, w - 48, 64, number, "text.primary", theme,
              size=46, bold=True, font="mono", leading=1.0),
            t(x + 24, y + 100, w - 48, 40, label, "text.secondary", theme, size=13, leading=1.4),
            t(x + 24, y + h - 44, w - 48, 22, delta, delta_color, theme, size=11, font="mono")]


# ------------------------------------------------------------------ slides
SLIDES = [
    # 01 — cover: navy field + portrait photo panel
    {"theme": "dark", "elements": [
        r(0, 0, W, H, "surface.base", "dark"),
        img(780, 48, 452, 624, "photo-cover.png", "dark", radius=28),
        *kicker(96, "NV5 · CIKARANG · 2026", "dark"),
        t(M, 194, 620, 260, "Commissioning,\nwithout the guesswork.", "text.primary", "dark",
          font="heading", size=62, bold=True, leading=1.06, spacing=-0.03),
        t(M, 428, 600, 70, "Satu catatan hidup per aset — dari instalasi sampai serah terima.",
          "text.secondary", "dark", size=18, leading=1.5),
        r(M, H - 108, 620, 1, "border.subtle", "dark"),
        t(M, H - 92, 620, 20, "Muhammad Shafiyuddin · November 2026",
          "slide.footer-fg", "dark", size=10, font="mono"),
    ]},

    # 02 — problem: text left, 4:3 photo right
    {"theme": "light", "elements": [
        r(0, 0, W, H, "surface.base"),
        *kicker(92, "01 — PROBLEM"),
        t(M, 168, 600, 190, "Handover slips because nobody owns the checklist.",
          "text.primary", font="heading", size=42, bold=True, leading=1.06, spacing=-0.02),
        t(M, 380, 540, 90, "Inspeksi tersebar di empat spreadsheet, dua grup WhatsApp, "
          "dan satu binder yang tidak pernah ikut rapat.", "text.primary", size=15, leading=1.65),
        t(M, 500, 120, 60, "37%", "brand.primary", size=44, bold=True, font="mono", leading=1.0),
        t(M + 130, 516, 380, 44, "temuan berulang karena tidak ada pemilik",
          "text.secondary", size=13, leading=1.4),
        img(700, 168, 508, 381, "photo-43.png"),
        t(700, 562, 508, 40, "Foto lapangan: temuan, alat ukur, kondisi aktual.",
          "text.secondary", size=13, leading=1.5),
        *footer(2),
    ]},

    # 03 — solution: three modules + sand callout
    {"theme": "light", "elements": [
        r(0, 0, W, H, "surface.raised"),
        *kicker(92, "02 — SOLUTION"),
        t(M, 168, 760, 60, "One live record per asset.", "text.primary",
          font="heading", size=44, bold=True, leading=1.05, spacing=-0.02),
        t(M, 236, 640, 30, "Bukan platform baru. Proses yang sama, dengan satu sumber status.",
          "text.primary", size=15),
        t(M, 292, 60, 20, "01", "brand.calm", size=12, bold=True, font="mono"),
        r(M, 320, 352, 2, "border.default"),
        t(M, 340, 340, 30, "Capture", "text.primary", font="heading", size=24, bold=True),
        t(M, 378, 340, 90, "Foto, angka uji, dan tanda tangan masuk ke record aset yang sama, di lokasi.",
          "text.primary", size=13, leading=1.6),
        t(M + 380, 292, 60, 20, "02", "brand.calm", size=12, bold=True, font="mono"),
        r(M + 380, 320, 352, 2, "border.default"),
        t(M + 380, 340, 340, 30, "Verify", "text.primary", font="heading", size=24, bold=True),
        t(M + 380, 378, 340, 90, "Status hanya berubah kalau ada bukti. Satu penolakan butuh satu alasan tertulis.",
          "text.primary", size=13, leading=1.6),
        t(M + 760, 292, 60, 20, "03", "brand.calm", size=12, bold=True, font="mono"),
        r(M + 760, 320, 352, 2, "border.default"),
        t(M + 760, 340, 340, 30, "Hand over", "text.primary", font="heading", size=24, bold=True),
        t(M + 760, 378, 340, 90, "Laporan serah terima dihasilkan dari record, bukan diketik ulang.",
          "text.primary", size=13, leading=1.6),
        r(M, 500, 1136, 100, "slide.callout-bg", radius=18),
        t(M + 28, 524, 700, 26, "Setiap temuan punya pemilik, bukti, dan tanggal.",
          "text.primary", font="heading", size=17, bold=True),
        t(M + 28, 556, 700, 24, "Yang tidak punya ketiganya, tidak masuk laporan serah terima.",
          "text.secondary", size=13),
        t(M + 860, 534, 250, 40, "0 sengketa", "brand.primary", size=20, bold=True,
          font="mono", align="right"),
        *footer(3),
    ]},

    # 04 — KPI cards
    {"theme": "dark", "elements": [
        r(0, 0, W, H, "surface.base", "dark"),
        *kicker(92, "03 — HASIL", "dark"),
        t(M, 168, 900, 60, "Eighteen months, three sites.", "text.primary", "dark",
          font="heading", size=42, bold=True, leading=1.05, spacing=-0.02),
        t(M, 232, 700, 24, "Empat angka yang dipakai untuk menilai apakah ini bekerja.",
          "text.secondary", "dark", size=14),
        *card(M, 300, 266, 240, "412", "aset tercatat", "▲ 128 sejak Jan 2026", "dark"),
        *card(M + 290, 300, 266, 240, "3", "gedung serah terima", "▲ 1 kuartal ini", "dark"),
        *card(M + 580, 300, 266, 240, "0", "sengketa pasca-serahan", "= tetap nol", "dark"),
        *card(M + 870, 300, 266, 240, "11", "hari lebih cepat", "▼ dari 11 ke 4 hari", "dark"),
        t(M, 580, 900, 24, "Angka dari tiga proyek percontohan di Cikarang, Jan 2025 – Jun 2026.",
          "text.secondary", "dark", size=11),
        *footer(4, "dark"),
    ]},

    # 05 — chart: waktu per fase
    {"theme": "light", "elements": [
        r(0, 0, W, H, "surface.base"),
        *kicker(92, "04 — DI MANA WAKTUNYA HABIS"),
        t(M, 168, 900, 60, "Delapan hari hilang di punch list.", "text.primary",
          font="heading", size=42, bold=True, leading=1.05, spacing=-0.02),
        t(M, 232, 640, 24, "Hari kerja per fase, rencana versus aktual, satu gedung.",
          "text.primary", size=14),
        chart(M, 292, 760, 320, ["Survey", "Instalasi", "Uji", "Punch list", "Serah terima"],
              [{"name": "Rencana", "values": [3, 6, 4, 2, 2], "color": "brand.calm"},
               {"name": "Aktual", "values": [4, 7, 5, 9, 3], "color": "brand.primary"}],
              kind="bar"),
        t(M + 800, 292, 336, 20, "PUNCH LIST", "text.secondary", size=10, caps=True,
          spacing=0.14, font="mono"),
        t(M + 800, 320, 336, 70, "9 hari", "brand.primary", size=44, bold=True, font="mono", leading=1.0),
        t(M + 800, 392, 336, 90, "Rencana 2 hari. Selisihnya bukan pekerjaan teknis — "
          "menunggu keputusan siapa yang menutup temuan.", "text.primary", size=13, leading=1.6),
        r(M + 800, 500, 336, 1, "border.default"),
        t(M + 800, 518, 336, 60, "Pilot memangkas fase ini ke 3 hari dengan satu pemilik per temuan.",
          "text.secondary", size=13, leading=1.5),
        *footer(5),
    ]},

    # 06 — pricing
    {"theme": "light", "elements": [
        r(0, 0, W, H, "surface.base"),
        *kicker(92, "05 — PAKET"),
        t(M, 168, 900, 60, "Dua cara masuk.", "text.primary",
          font="heading", size=42, bold=True, leading=1.05, spacing=-0.02),

        r(M, 280, 520, 300, "surface.raised", radius=18, stroke="border.default", stroke_w=1),
        t(M + 28, 304, 300, 22, "PILOT · SATU GEDUNG", "text.secondary", size=10, caps=True,
          spacing=0.14, font="mono"),
        t(M + 28, 336, 300, 60, "Rp 0", "text.primary", size=44, bold=True, font="mono", leading=1.0),
        t(M + 28, 396, 300, 22, "6 minggu, 1 tim, 120 aset", "text.secondary", size=12),
        t(M + 28, 432, 460, 90, "Kami kerjakan bersama tim kamu. Yang dibutuhkan: satu orang "
          "yang berani menutup temuan.", "text.primary", size=13, leading=1.6),
        t(M + 28, 528, 300, 22, "Termasuk pelatihan & template laporan", "text.secondary",
          size=11, font="mono"),

        r(M + 560, 280, 576, 300, "brand.primary", radius=18),
        t(M + 588, 304, 400, 22, "FULL · SEMUA GEDUNG", "text.on-brand", size=10, caps=True,
          spacing=0.14, font="mono"),
        t(M + 588, 336, 400, 60, "Rp 48 jt", "text.on-brand", size=44, bold=True, font="mono", leading=1.0),
        t(M + 588, 396, 400, 22, "per gedung, per siklus serah terima", "text.on-brand", size=12),
        t(M + 588, 432, 500, 90, "Record, verifikasi, dan laporan serah terima. "
          "Termasuk pendampingan sampai serah terima diterima klien.",
          "text.on-brand", size=13, leading=1.6),
        t(M + 588, 528, 400, 22, "SLA 5 hari kerja per temuan", "text.on-brand", size=11, font="mono"),
        *footer(6),
    ]},

    # 07 — budget / revenue
    {"theme": "dark", "elements": [
        r(0, 0, W, H, "surface.base", "dark"),
        *kicker(92, "06 — ANGKA", "dark"),
        t(M, 168, 900, 60, "Satu siklus, tiga baris.", "text.primary", "dark",
          font="heading", size=42, bold=True, leading=1.05, spacing=-0.02),

        r(M, 282, 1136, 1, "border.subtle", "dark"),
        t(M, 306, 460, 22, "Nilai proyek per gedung", "text.secondary", "dark", size=12),
        t(M + 480, 300, 400, 44, "Rp 1,2 M", "text.primary", "dark", size=36, bold=True,
          font="mono", leading=1.0, align="right"),
        t(M + 900, 312, 236, 30, "+12%", "brand.primary", "dark", size=15, bold=True,
          font="mono", align="right"),
        r(M, 372, 1136, 1, "border.subtle", "dark"),

        t(M, 396, 460, 22, "Biaya serah terima", "text.secondary", "dark", size=12),
        t(M + 480, 390, 400, 44, "Rp 96 jt", "text.primary", "dark", size=36, bold=True,
          font="mono", leading=1.0, align="right"),
        t(M + 900, 402, 236, 30, "−11 hari", "brand.primary", "dark", size=15, bold=True,
          font="mono", align="right"),
        r(M, 462, 1136, 1, "border.subtle", "dark"),

        t(M, 486, 460, 22, "Sengketa setelah serah terima", "text.secondary", "dark", size=12),
        t(M + 480, 480, 400, 44, "Rp 0", "brand.primary", "dark", size=36, bold=True,
          font="mono", leading=1.0, align="right"),
        t(M + 900, 492, 236, 26, "= 0", "text.secondary", "dark", size=13, font="mono",
          align="right"),
        r(M, 552, 1136, 1, "border.subtle", "dark"),
        t(M, 574, 700, 24, "Satu siklus serah terima, diukur per gedung — bukan rata-rata proyek.",
          "text.secondary", "dark", size=12),
        t(M + 900, 570, 236, 24, "Jan – Jun 2026", "text.secondary", "dark", size=11,
          font="mono", align="right"),
        *footer(7, "dark"),
    ]},

    # 08 — roadmap
    {"theme": "light", "elements": [
        r(0, 0, W, H, "surface.base"),
        *kicker(92, "07 — ROADMAP"),
        t(M, 168, 900, 60, "Four quarters, one metric.", "text.primary",
          font="heading", size=42, bold=True, leading=1.05, spacing=-0.02),
        t(M, 236, 700, 30, "Target: waktu serah terima turun dari 11 hari ke 4 hari.",
          "text.primary", size=15),
        r(M, 356, W - 2 * M, 2, "border.strong"),
        t(M, 326, 60, 20, "Q1", "brand.primary", size=12, bold=True, font="mono"),
        t(M, 380, 240, 30, "Pilot satu gedung", "text.primary", font="heading", size=20, bold=True),
        t(M, 414, 240, 60, "Record aset untuk 120 unit, satu tim.", "text.primary", size=13, leading=1.5),
        t(M + 280, 326, 60, 20, "Q2", "brand.primary", size=12, bold=True, font="mono"),
        t(M + 280, 380, 240, 30, "Template serah terima", "text.primary", font="heading", size=20, bold=True),
        t(M + 280, 414, 240, 60, "Laporan otomatis dari record, bukan diketik.", "text.primary", size=13, leading=1.5),
        t(M + 560, 326, 60, 20, "Q3", "brand.primary", size=12, bold=True, font="mono"),
        t(M + 560, 380, 240, 30, "Tiga gedung paralel", "text.primary", font="heading", size=20, bold=True),
        t(M + 560, 414, 240, 60, "Satu orang bisa pegang tiga proyek.", "text.primary", size=13, leading=1.5),
        t(M + 840, 326, 60, 20, "Q4", "brand.primary", size=12, bold=True, font="mono"),
        t(M + 840, 380, 240, 30, "Serah terima 4 hari", "text.primary", font="heading", size=20, bold=True),
        t(M + 840, 414, 240, 60, "Target metrik, diukur per gedung.", "text.primary", size=13, leading=1.5),
        r(M, 512, 1136, 1, "border.default"),
        t(M, 532, 640, 24, "Metrik yang sama dipakai di ketiga proyek — bukan KPI baru.",
          "text.secondary", size=13),
        *footer(8),
    ]},

    # 09 — contact
    {"theme": "dark", "elements": [
        r(0, 0, W, H, "surface.base", "dark"),
        *kicker(96, "08 — KONTAK", "dark"),
        t(M, 194, 700, 160, "Two engineers.\nOne quarter.", "text.primary", "dark",
          font="heading", size=56, bold=True, leading=1.06, spacing=-0.03),
        t(M, 380, 620, 60, "Butuh dua orang yang bisa memegang record, bukan spreadsheet.",
          "text.secondary", "dark", size=17, leading=1.5),

        r(M, 480, 500, 1, "border.subtle", "dark"),
        t(M, 500, 120, 20, "EMAIL", "text.secondary", "dark", size=10, caps=True, spacing=0.14, font="mono"),
        t(M, 522, 460, 24, "shafimihradi@gmail.com", "text.primary", "dark", size=14, font="mono"),
        t(M + 560, 500, 120, 20, "TELEPON", "text.secondary", "dark", size=10, caps=True, spacing=0.14, font="mono"),
        t(M + 560, 522, 460, 24, "+62 812 0000 0000", "text.primary", "dark", size=14, font="mono"),
        r(M, 572, 500, 1, "border.subtle", "dark"),
        t(M, 592, 620, 24, "Langkah berikutnya: pilot 6 minggu, satu gedung, mulai Januari 2027.",
          "text.primary", "dark", size=13),

        img(760, 168, 448, 336, "photo-43.png", "dark"),
        *footer(9, "dark"),
    ]},
]


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


# ------------------------------------------------------------------ pptx
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
                shape.fill.fore_color.rgb = RGBColor.from_string(hexof(theme, el["fill"]))
                if el.get("stroke"):
                    shape.line.color.rgb = RGBColor.from_string(hexof(theme, el["stroke"]))
                    shape.line.width = Pt(el.get("stroke_w", 1) * 0.75)
                else:
                    shape.line.fill.background()
                shape.shadow.inherit = False
                continue

            if el["kind"] == "image":
                rad = int(el.get("radius") or 0)
                src = (rounded_photo(el["src"], int(el["w"]), int(el["h"]), rad)
                       if rad > 0 else PHOTOS / el["src"])
                slide.shapes.add_picture(str(src), x, y, w, h)
                continue

            if el["kind"] == "chart":
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
                f.name = font_of(el.get("font", "body"))
                f.color.rgb = RGBColor.from_string(hexof(theme, el["color"]))
                if el.get("spacing"):
                    f._rPr.set("spc", str(int(el["spacing"] * 100)))

    prs.save(path)


if __name__ == "__main__":
    out = ROOT / "examples" / "pitch-deck.pptx"
    out.parent.mkdir(exist_ok=True)
    render_pptx(out)
    print("wrote", out, len(SLIDES), "slides")
