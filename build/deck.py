#!/usr/bin/env python3
"""Pitch deck: one slide spec, two renderers (pptx + html preview).

Coordinates are in slide pixels (1280x720). 1px = 9525 EMU, so the pptx is a
13.333in x 7.5in 16:9 deck and the HTML preview is pixel-identical.

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

PX = 9525  # EMU per slide pixel


def tok(theme: str, name: str):
    return (DARK if theme == "dark" else LIGHT)[name]


def font_of(theme: str, which: str) -> str:
    fam = LIGHT[f"type.family.{which}"]
    return fam[0] if isinstance(fam, list) else fam.split(",")[0].strip().strip("'")


# ------------------------------------------------------------------ spec
M = 80          # margin x
W, H = 1280, 720


def kicker(y, label, theme="light"):
    return [{"kind": "text", "x": M, "y": y, "w": 520, "h": 24, "text": label,
             "theme": theme, "color": "slide.kicker-fg", "font": "mono",
             "size": 11, "bold": True, "caps": True, "spacing": 0.18},
            {"kind": "rect", "x": M, "y": y + 30, "w": 56, "h": 4,
             "fill": "slide.rule", "theme": theme}]


def footer(page, theme="light", label="Commissioning readiness · NV5"):
    return [
        {"kind": "text", "x": M, "y": H - 56, "w": 700, "h": 20, "text": label,
         "theme": theme, "color": "slide.footer-fg", "font": "mono", "size": 10},
        {"kind": "text", "x": W - M - 80, "y": H - 56, "w": 80, "h": 20, "text": f"{page:02d}",
         "theme": theme, "color": "slide.page-no-fg", "font": "mono", "size": 10, "align": "right"},
    ]


SLIDES = [
    # 01 cover
    {"theme": "dark", "elements": [
        {"kind": "rect", "x": 0, "y": 0, "w": W, "h": H, "fill": "surface.base", "theme": "dark"},
        {"kind": "text", "x": M, "y": 150, "w": 600, "h": 24, "text": "NV5 · CIKARANG · 2026",
         "theme": "dark", "color": "slide.kicker-fg", "font": "mono", "size": 11,
         "bold": True, "caps": True, "spacing": 0.18},
        {"kind": "rect", "x": M, "y": 182, "w": 56, "h": 4, "fill": "slide.rule", "theme": "dark"},
        {"kind": "text", "x": M, "y": 250, "w": 900, "h": 240,
         "text": "Commissioning,\nwithout the guesswork.",
         "theme": "dark", "color": "text.primary", "font": "heading", "size": 76,
         "bold": True, "leading": 0.98, "spacing": -0.045},
        {"kind": "text", "x": M, "y": 520, "w": 620, "h": 60,
         "text": "Satu catatan hidup per aset — dari instalasi sampai serah terima.",
         "theme": "dark", "color": "text.secondary", "font": "body", "size": 19, "leading": 1.4},
        {"kind": "text", "x": M, "y": 620, "w": 600, "h": 20,
         "text": "Muhammad Shafiyuddin · November 2026",
         "theme": "dark", "color": "slide.footer-fg", "font": "mono", "size": 10},
        {"kind": "text", "x": W - M - 80, "y": 620, "w": 80, "h": 20, "text": "01",
         "theme": "dark", "color": "slide.page-no-fg", "font": "mono", "size": 10, "align": "right"},
    ]},

    # 02 problem
    {"theme": "light", "elements": [
        {"kind": "rect", "x": 0, "y": 0, "w": W, "h": H, "fill": "surface.base", "theme": "light"},
        *kicker(96, "02 — PROBLEM"),
        {"kind": "text", "x": M, "y": 160, "w": 900, "h": 180,
         "text": "Handover slips because\nnobody owns the checklist.",
         "theme": "light", "color": "text.primary", "font": "heading", "size": 52,
         "bold": True, "leading": 1.02, "spacing": -0.025},
        {"kind": "text", "x": M, "y": 380, "w": 520, "h": 90,
         "text": "Inspeksi tersebar di empat spreadsheet, dua grup WhatsApp, "
                 "dan satu binder yang tidak pernah ikut rapat.",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 16, "leading": 1.6},
        {"kind": "rect", "x": 720, "y": 380, "w": 1, "h": 220, "fill": "border.subtle", "theme": "light"},
        {"kind": "text", "x": 780, "y": 380, "w": 300, "h": 64, "text": "37%",
         "theme": "light", "color": "brand.primary", "font": "mono", "size": 52, "bold": True},
        {"kind": "text", "x": 780, "y": 448, "w": 360, "h": 40,
         "text": "temuan berulang karena tidak ada pemilik",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 14},
        {"kind": "text", "x": 780, "y": 512, "w": 320, "h": 64, "text": "11 hari",
         "theme": "light", "color": "brand.primary", "font": "mono", "size": 52, "bold": True},
        {"kind": "text", "x": 780, "y": 580, "w": 360, "h": 40,
         "text": "rata-rata keterlambatan serah terima per gedung",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 14},
        *footer(2),
    ]},

    # 03 solution
    {"theme": "light", "elements": [
        {"kind": "rect", "x": 0, "y": 0, "w": W, "h": H, "fill": "surface.base", "theme": "light"},
        *kicker(96, "03 — SOLUTION"),
        {"kind": "text", "x": M, "y": 160, "w": 900, "h": 70,
         "text": "One live record per asset.",
         "theme": "light", "color": "text.primary", "font": "heading", "size": 52,
         "bold": True, "leading": 1.05, "spacing": -0.025},
        {"kind": "text", "x": M, "y": 240, "w": 620, "h": 30,
         "text": "Bukan platform baru. Proses yang sama, dengan satu sumber status.",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 16},
        # three columns
        {"kind": "text", "x": M, "y": 330, "w": 60, "h": 20, "text": "01",
         "theme": "light", "color": "brand.primary", "font": "mono", "size": 12, "bold": True},
        {"kind": "rect", "x": M, "y": 356, "w": 320, "h": 2, "fill": "border.strong", "theme": "light"},
        {"kind": "text", "x": M, "y": 376, "w": 320, "h": 34, "text": "Capture",
         "theme": "light", "color": "text.primary", "font": "heading", "size": 26, "bold": True},
        {"kind": "text", "x": M, "y": 416, "w": 320, "h": 80,
         "text": "Foto, angka uji, dan tanda tangan masuk ke record aset yang sama, di lokasi.",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 14, "leading": 1.55},

        {"kind": "text", "x": 480, "y": 330, "w": 60, "h": 20, "text": "02",
         "theme": "light", "color": "brand.primary", "font": "mono", "size": 12, "bold": True},
        {"kind": "rect", "x": 480, "y": 356, "w": 320, "h": 2, "fill": "border.strong", "theme": "light"},
        {"kind": "text", "x": 480, "y": 376, "w": 320, "h": 34, "text": "Verify",
         "theme": "light", "color": "text.primary", "font": "heading", "size": 26, "bold": True},
        {"kind": "text", "x": 480, "y": 416, "w": 320, "h": 80,
         "text": "Status hanya berubah kalau ada bukti. Satu penolakan butuh satu alasan tertulis.",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 14, "leading": 1.55},

        {"kind": "text", "x": 880, "y": 330, "w": 60, "h": 20, "text": "03",
         "theme": "light", "color": "brand.primary", "font": "mono", "size": 12, "bold": True},
        {"kind": "rect", "x": 880, "y": 356, "w": 320, "h": 2, "fill": "border.strong", "theme": "light"},
        {"kind": "text", "x": 880, "y": 376, "w": 320, "h": 34, "text": "Hand over",
         "theme": "light", "color": "text.primary", "font": "heading", "size": 26, "bold": True},
        {"kind": "text", "x": 880, "y": 416, "w": 320, "h": 80,
         "text": "Laporan serah terima dihasilkan dari record, bukan diketik ulang.",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 14, "leading": 1.55},
        *footer(3),
    ]},

    # 04 traction (dark)
    {"theme": "dark", "elements": [
        {"kind": "rect", "x": 0, "y": 0, "w": W, "h": H, "fill": "surface.base", "theme": "dark"},
        *kicker(96, "04 — TRACTION", theme="dark"),
        {"kind": "text", "x": M, "y": 160, "w": 900, "h": 70,
         "text": "Eighteen months, three sites.",
         "theme": "dark", "color": "text.primary", "font": "heading", "size": 52,
         "bold": True, "leading": 1.05, "spacing": -0.025},
        {"kind": "rect", "x": M, "y": 300, "w": 1120, "h": 1, "fill": "border.subtle", "theme": "dark"},

        {"kind": "text", "x": M, "y": 340, "w": 260, "h": 80, "text": "412",
         "theme": "dark", "color": "text.primary", "font": "mono", "size": 64, "bold": True},
        {"kind": "text", "x": M, "y": 424, "w": 260, "h": 40, "text": "aset tercatat",
         "theme": "dark", "color": "text.secondary", "font": "body", "size": 14},

        {"kind": "text", "x": 360, "y": 340, "w": 260, "h": 80, "text": "3",
         "theme": "dark", "color": "text.primary", "font": "mono", "size": 64, "bold": True},
        {"kind": "text", "x": 360, "y": 424, "w": 260, "h": 40, "text": "gedung diserahterimakan",
         "theme": "dark", "color": "text.secondary", "font": "body", "size": 14},

        {"kind": "text", "x": 640, "y": 340, "w": 260, "h": 80, "text": "0",
         "theme": "dark", "color": "brand.primary", "font": "mono", "size": 64, "bold": True},
        {"kind": "text", "x": 640, "y": 424, "w": 260, "h": 40, "text": "sengketa pasca-serahan",
         "theme": "dark", "color": "text.secondary", "font": "body", "size": 14},

        {"kind": "text", "x": 920, "y": 340, "w": 260, "h": 80, "text": "11",
         "theme": "dark", "color": "brand.primary", "font": "mono", "size": 64, "bold": True},
        {"kind": "text", "x": 920, "y": 424, "w": 260, "h": 40, "text": "hari lebih cepat per gedung",
         "theme": "dark", "color": "text.secondary", "font": "body", "size": 14},

        {"kind": "text", "x": M, "y": 540, "w": 900, "h": 60,
         "text": "Angka dari tiga proyek percontohan di Cikarang, Jan 2025 – Jun 2026.",
         "theme": "dark", "color": "text.muted", "font": "body", "size": 13},
        *footer(4, theme="dark"),
    ]},

    # 05 roadmap
    {"theme": "light", "elements": [
        {"kind": "rect", "x": 0, "y": 0, "w": W, "h": H, "fill": "surface.base", "theme": "light"},
        *kicker(96, "05 — ROADMAP"),
        {"kind": "text", "x": M, "y": 160, "w": 900, "h": 70, "text": "Four quarters, one metric.",
         "theme": "light", "color": "text.primary", "font": "heading", "size": 52,
         "bold": True, "leading": 1.05, "spacing": -0.025},
        {"kind": "text", "x": M, "y": 244, "w": 700, "h": 30,
         "text": "Target: waktu serah terima turun dari 11 hari ke 4 hari.",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 16},

        {"kind": "rect", "x": M, "y": 360, "w": 1120, "h": 2, "fill": "border.strong", "theme": "light"},

        {"kind": "text", "x": M, "y": 330, "w": 60, "h": 20, "text": "Q1",
         "theme": "light", "color": "brand.primary", "font": "mono", "size": 12, "bold": True},
        {"kind": "text", "x": M, "y": 384, "w": 240, "h": 30, "text": "Pilot satu gedung",
         "theme": "light", "color": "text.primary", "font": "heading", "size": 20, "bold": True},
        {"kind": "text", "x": M, "y": 418, "w": 240, "h": 60,
         "text": "Record aset untuk 120 unit, satu tim.",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 13, "leading": 1.5},

        {"kind": "text", "x": 360, "y": 330, "w": 60, "h": 20, "text": "Q2",
         "theme": "light", "color": "brand.primary", "font": "mono", "size": 12, "bold": True},
        {"kind": "text", "x": 360, "y": 384, "w": 240, "h": 30, "text": "Template serah terima",
         "theme": "light", "color": "text.primary", "font": "heading", "size": 20, "bold": True},
        {"kind": "text", "x": 360, "y": 418, "w": 240, "h": 60,
         "text": "Laporan otomatis dari record, bukan diketik.",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 13, "leading": 1.5},

        {"kind": "text", "x": 640, "y": 330, "w": 60, "h": 20, "text": "Q3",
         "theme": "light", "color": "brand.primary", "font": "mono", "size": 12, "bold": True},
        {"kind": "text", "x": 640, "y": 384, "w": 240, "h": 30, "text": "Tiga gedung paralel",
         "theme": "light", "color": "text.primary", "font": "heading", "size": 20, "bold": True},
        {"kind": "text", "x": 640, "y": 418, "w": 240, "h": 60,
         "text": "Satu orang bisa pegang tiga proyek.",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 13, "leading": 1.5},

        {"kind": "text", "x": 920, "y": 330, "w": 60, "h": 20, "text": "Q4",
         "theme": "light", "color": "brand.primary", "font": "mono", "size": 12, "bold": True},
        {"kind": "text", "x": 920, "y": 384, "w": 240, "h": 30, "text": "Serah terima 4 hari",
         "theme": "light", "color": "text.primary", "font": "heading", "size": 20, "bold": True},
        {"kind": "text", "x": 920, "y": 418, "w": 240, "h": 60,
         "text": "Target metrik, diukur per gedung.",
         "theme": "light", "color": "text.secondary", "font": "body", "size": 13, "leading": 1.5},
        *footer(5),
    ]},

    # 06 ask (brand field)
    {"theme": "light", "elements": [
        {"kind": "rect", "x": 0, "y": 0, "w": W, "h": H, "fill": "brand.primary", "theme": "light"},
        {"kind": "text", "x": M, "y": 150, "w": 600, "h": 24, "text": "06 — THE ASK",
         "theme": "light", "color": "text.on-brand", "font": "mono", "size": 11,
         "bold": True, "caps": True, "spacing": 0.18},
        {"kind": "rect", "x": M, "y": 182, "w": 56, "h": 4, "fill": "text.on-brand", "theme": "light"},
        {"kind": "text", "x": M, "y": 250, "w": 880, "h": 220,
         "text": "Two engineers.\nOne quarter.",
         "theme": "light", "color": "text.on-brand", "font": "heading", "size": 76,
         "bold": True, "leading": 0.98, "spacing": -0.045},
        {"kind": "text", "x": M, "y": 500, "w": 700, "h": 60,
         "text": "Butuh dua orang yang bisa memegang record, bukan spreadsheet.",
         "theme": "light", "color": "text.on-brand", "font": "body", "size": 19, "leading": 1.4},
        {"kind": "text", "x": M, "y": 600, "w": 700, "h": 24,
         "text": "shafimihradi@gmail.com",
         "theme": "light", "color": "text.on-brand", "font": "mono", "size": 13, "bold": True},
        {"kind": "text", "x": W - M - 80, "y": 600, "w": 80, "h": 20, "text": "06",
         "theme": "light", "color": "text.on-brand", "font": "mono", "size": 10, "align": "right"},
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
                f.size = Pt(el["size"] * 0.75)          # px -> pt
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
