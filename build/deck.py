#!/usr/bin/env python3
"""Pitch deck v0.3 — one slide spec, two renderers (pptx + html preview).

Merged language: pitch-deck discipline (Signal) + infographic modules (Style 2).
Coordinates in slide pixels, 1280x720. 1px = 9525 EMU, so the pptx is exactly
13.333in x 7.5in and the HTML preview is pixel-identical.

    python build/deck.py        # examples/pitch-deck.pptx
"""
from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

ROOT = Path(__file__).resolve().parent.parent
TOK = json.loads((ROOT / "dist" / "json" / "tokens.resolved.json").read_text())
LIGHT, DARK = TOK["light"], TOK["dark"]

PX = 9525
W, H = 1280, 720
M = 72


def tok(theme: str, name: str):
    return (DARK if theme == "dark" else LIGHT)[name]


def font_of(theme: str, which: str) -> str:
    fam = LIGHT[f"type.family.{which}"]
    return fam[0] if isinstance(fam, list) else fam.split(",")[0].strip().strip("'")


# ------------------------------------------------------------------ helpers
def t(x, y, w, h, text, color, theme="light", font="body", size=16, bold=False,
      leading=1.3, spacing=0.0, caps=False, align="left"):
    return {"kind": "text", "x": x, "y": y, "w": w, "h": h, "text": text,
            "theme": theme, "color": color, "font": font, "size": size,
            "bold": bold, "leading": leading, "spacing": spacing,
            "caps": caps, "align": align}


def r(x, y, w, h, fill, theme="light"):
    return {"kind": "rect", "x": x, "y": y, "w": w, "h": h, "fill": fill, "theme": theme}


def kicker(y, label, theme="light"):
    return [r(M, y + 2, 10, 10, "brand.primary", theme),
            t(M + 24, y - 2, 560, 22, label, "slide.kicker-fg", theme,
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


# ------------------------------------------------------------------ slides
SLIDES = [
    # 01 — cover, navy field
    {"theme": "dark", "elements": [
        r(0, 0, W, H, "surface.base", "dark"),
        *kicker(96, "NV5 · CIKARANG · 2026", "dark"),
        t(M, 194, 1000, 260, "Commissioning,\nwithout the guesswork.", "text.primary", "dark",
          font="heading", size=68, bold=True, leading=1.06, spacing=-0.03),
        t(M, 448, 620, 70, "Satu catatan hidup per aset — dari instalasi sampai serah terima.",
          "text.secondary", "dark", size=18, leading=1.5),
        r(M, H - 108, W - 2 * M, 1, "border.subtle", "dark"),
        t(M, H - 92, 700, 20, "Muhammad Shafiyuddin · November 2026",
          "slide.footer-fg", "dark", size=10, font="mono"),
    ]},

    # 02 — problem, ivory, two stacked stats instead of a photo
    {"theme": "light", "elements": [
        r(0, 0, W, H, "surface.base"),
        *kicker(92, "01 — PROBLEM"),
        t(M, 168, 620, 190, "Handover slips because nobody owns the checklist.",
          "text.primary", font="heading", size=44, bold=True, leading=1.06, spacing=-0.02),
        t(M, 392, 540, 90, "Inspeksi tersebar di empat spreadsheet, dua grup WhatsApp, "
          "dan satu binder yang tidak pernah ikut rapat.", "text.primary", size=15, leading=1.65),

        r(700, 168, 508, 1, "border.default"),
        *stat(700, 196, 460, "37%", "temuan berulang karena tidak ada pemilik"),
        r(700, 320, 508, 1, "border.default"),
        t(700, 348, 120, 70, "11", "brand.primary", size=60, bold=True, font="mono", leading=1.0),
        t(768, 388, 120, 30, "hari", "brand.primary", size=24, bold=True, font="mono"),
        t(700, 424, 460, 44, "rata-rata keterlambatan serah terima per gedung",
          "text.secondary", size=13, leading=1.4),
        r(700, 472, 508, 1, "border.default"),
        t(700, 492, 508, 60, "Angka dari audit internal tiga proyek, 2025–2026.",
          "text.secondary", size=13, leading=1.5),
        *footer(2),
    ]},

    # 03 — solution, cream, three modules + sand callout
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

        r(M, 500, 1136, 100, "slide.callout-bg"),
        t(M + 28, 524, 700, 26, "Setiap temuan punya pemilik, bukti, dan tanggal.",
          "text.primary", font="heading", size=17, bold=True),
        t(M + 28, 556, 700, 24, "Yang tidak punya ketiganya, tidak masuk laporan serah terima.",
          "text.secondary", size=13),
        t(M + 860, 534, 250, 40, "0 sengketa", "brand.primary", size=20, bold=True,
          font="mono", align="right"),
        *footer(3),
    ]},

    # 04 — traction, navy, stats + bars
    {"theme": "dark", "elements": [
        r(0, 0, W, H, "surface.base", "dark"),
        *kicker(92, "03 — TRACTION", "dark"),
        t(M, 168, 900, 60, "Eighteen months, three sites.", "text.primary", "dark",
          font="heading", size=44, bold=True, leading=1.05, spacing=-0.02),
        r(M, 268, W - 2 * M, 1, "border.subtle", "dark"),

        *stat(M, 310, 240, "412", "aset tercatat", "dark", "text.primary"),
        *stat(M + 280, 310, 240, "3", "gedung diserahterimakan", "dark", "text.primary"),
        *stat(M + 560, 310, 240, "0", "sengketa pasca-serahan", "dark", "brand.primary"),
        *stat(M + 840, 310, 240, "11", "hari lebih cepat per gedung", "dark", "brand.primary"),

        r(M, 470, W - 2 * M, 1, "border.subtle", "dark"),
        t(M, 496, 260, 20, "WAKTU SERAH TERIMA", "text.secondary", "dark",
          size=10, caps=True, spacing=0.14, font="mono"),
        r(M, 528, 700, 14, "border.default", "dark"),
        r(M, 528, 434, 14, "brand.calm", "dark"),
        t(M + 716, 524, 120, 24, "11 hari", "text.secondary", "dark", size=12, font="mono"),
        r(M, 558, 700, 14, "border.default", "dark"),
        r(M, 558, 154, 14, "brand.primary", "dark"),
        t(M + 716, 554, 120, 24, "4 hari", "brand.primary", "dark", size=12, font="mono"),
        t(M, 594, 400, 18, "target Q4", "text.muted", "dark", size=11, font="mono"),

        t(M, 640, 760, 22, "Angka dari tiga proyek percontohan di Cikarang, Jan 2025 – Jun 2026.",
          "text.secondary", "dark", size=11),
        *footer(4, "dark"),
    ]},

    # 05 — roadmap, ivory
    {"theme": "light", "elements": [
        r(0, 0, W, H, "surface.base"),
        *kicker(92, "04 — ROADMAP"),
        t(M, 168, 900, 60, "Four quarters, one metric.", "text.primary",
          font="heading", size=44, bold=True, leading=1.05, spacing=-0.02),
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
        *footer(5),
    ]},

    # 06 — ask, orange field, charcoal text
    {"theme": "light", "elements": [
        r(0, 0, W, H, "brand.primary"),
        t(M, 92, 620, 22, "05 — THE ASK", "text.on-brand", size=11, bold=True,
          caps=True, spacing=0.18, font="mono"),
        r(M, 126, 132, 3, "text.on-brand"),
        t(M, 194, 900, 220, "Two engineers.\nOne quarter.", "text.on-brand",
          font="heading", size=68, bold=True, leading=1.06, spacing=-0.03),
        t(M, 452, 700, 60, "Butuh dua orang yang bisa memegang record, bukan spreadsheet.",
          "text.on-brand", size=18, leading=1.5),
        t(M, 580, 700, 24, "shafimihradi@gmail.com", "text.on-brand", size=13, bold=True, font="mono"),
        t(W - M - 80, 580, 80, 20, "06", "text.on-brand", size=10, font="mono", align="right"),
    ]},
]


# ------------------------------------------------------------------ pptx
ALIGN = {"left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT, "center": PP_ALIGN.CENTER}


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
                shape = slide.shapes.add_shape(1, x, y, w, h)
                shape.fill.solid()
                shape.fill.fore_color.rgb = RGBColor.from_string(tok(theme, el["fill"]).lstrip("#").upper())
                shape.line.fill.background()
                shape.shadow.inherit = False
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
                f.name = font_of(theme, el.get("font", "body"))
                f.color.rgb = RGBColor.from_string(tok(theme, el["color"]).lstrip("#").upper())
                if el.get("spacing"):
                    f._rPr.set("spc", str(int(el["spacing"] * 100)))

    prs.save(path)


if __name__ == "__main__":
    out = ROOT / "examples" / "pitch-deck.pptx"
    out.parent.mkdir(exist_ok=True)
    render_pptx(out)
    print("wrote", out, len(SLIDES), "slides")
