#!/usr/bin/env python3
"""Generate sample deck + report straight from the built tokens.

Proves the same token file drives Office output, not just CSS.
    python build/examples.py
"""
from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from pptx import Presentation
from pptx.dml.color import RGBColor as PPColor
from pptx.util import Emu, Inches, Pt as PPPt

ROOT = Path(__file__).resolve().parent.parent
TOK = json.loads((ROOT / "dist" / "json" / "tokens.resolved.json").read_text())["light"]


def c(name: str) -> str:
    """Token name -> 'RRGGBB'."""
    return str(TOK[name]).lstrip("#").upper()


def rgb(name: str) -> PPColor:
    return PPColor.from_string(c(name))


def font(name: str) -> str:
    fam = TOK[name]
    if isinstance(fam, list):
        return str(fam[0])
    return fam.split(",")[0].strip().strip("'")


HEAD, BODY = font("type.family.heading"), font("type.family.body")


# ------------------------------------------------------------------ deck
def build_deck(path: Path) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    def text(slide, txt, left, top, width, height, *, size, color, bold=False,
             serif=True, spacing=None):
        box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = txt
        run.font.size = PPPt(size)
        run.font.bold = bold
        run.font.name = HEAD if serif else BODY
        run.font.color.rgb = rgb(color)
        if spacing:
            run.font._rPr.set("spc", str(int(spacing * 100)))
        return box

    # --- cover: navy field, sand rule
    s = prs.slides.add_slide(blank)
    bg = s.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = rgb("surface.inverse")
    bg.line.fill.background()

    rule = s.shapes.add_shape(1, Inches(1.1), Inches(3.05), Inches(1.4), Emu(28575 * 2))
    rule.fill.solid()
    rule.fill.fore_color.rgb = rgb("brand.primary")
    rule.line.fill.background()

    text(s, "NV5 · CIKARANG · 2026", 1.1, 1.9, 9, 0.4,
         size=11, color="brand.primary", bold=True, serif=False, spacing=0.18)
    text(s, "Commissioning,\nwithout the guesswork.", 1.1, 3.35, 9.5, 2.2,
         size=54, color="color.ivory.500", bold=True)
    text(s, "Muhammad Shafiyuddin · November 2026", 1.1, 5.9, 7, 0.9,
         size=12, color="color.olive.500", serif=False)

    # --- content: warm canvas, serif heading, table
    s = prs.slides.add_slide(blank)
    bg = s.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = rgb("surface.base")
    bg.line.fill.background()

    text(s, "01 · FINDINGS", 0.9, 0.62, 6, 0.3,
         size=10, color="text.secondary", serif=False, spacing=0.14)
    text(s, "Three systems still open", 0.9, 1.0, 10, 0.8,
         size=30, color="text.primary", bold=True)
    text(s, "Semua temuan di bawah berasal dari inspeksi 20–24 November dan "
            "belum ditutup oleh kontraktor.", 0.9, 1.85, 9.2, 0.7,
         size=13, color="text.secondary", serif=False)

    rows = [("Chiller CH-01", "Passed", "24 Nov", "status.success"),
            ("AHU-03 airflow", "Pending", "—", "status.warning"),
            ("Fire damper FD-12", "Failed", "23 Nov", "status.danger"),
            ("BMS point mapping", "Passed", "22 Nov", "status.success")]
    top, left, row_h = 2.85, 0.9, 0.52
    widths = [3.6, 2.2, 2.0, 1.0]
    heads = ["Equipment", "Status", "Verified", ""]

    x = left
    for head, w in zip(heads, widths):
        text(s, head.upper(), x, top - 0.36, w, 0.3, size=9,
             color="text.secondary", serif=False, spacing=0.1)
        x += w

    for i, (eq, st, dt, tok) in enumerate(rows):
        y = top + i * row_h
        line = s.shapes.add_shape(1, Inches(left), Inches(y - 0.06),
                                  Inches(sum(widths) + 1.4), Emu(9525))
        line.fill.solid()
        line.fill.fore_color.rgb = rgb("border.subtle")
        line.line.fill.background()
        text(s, eq, left, y, widths[0], 0.35, size=13, color="text.primary", serif=False)
        text(s, st, left + widths[0], y, widths[1], 0.35, size=13, color=tok, serif=False, bold=True)
        text(s, dt, left + widths[0] + widths[1], y, widths[2], 0.35,
             size=13, color="text.secondary", serif=False)

    text(s, "Corporate Calm · token-driven sample", 0.9, 6.9, 6, 0.3,
         size=9, color="text.muted", serif=False)

    prs.save(path)


# ------------------------------------------------------------------ docx
def build_report(path: Path) -> None:
    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Inches(1.15)
    sec.top_margin = Inches(1.0)
    sec.bottom_margin = Inches(1.0)

    normal = doc.styles["Normal"]
    normal.font.name = BODY
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor.from_string(c("text.primary"))
    normal.paragraph_format.line_spacing = 1.45
    normal.paragraph_format.space_after = Pt(8)

    for name, size, color in (("Heading 1", 20, "text.primary"),
                              ("Heading 2", 13, "text.primary")):
        st = doc.styles[name]
        st.font.name = HEAD
        st.font.size = Pt(size)
        st.font.color.rgb = RGBColor.from_string(c(color))
        st.font.bold = True

    p = doc.add_paragraph("COMMISSIONING READINESS REVIEW")
    p.runs[0].font.size = Pt(9)
    p.runs[0].font.name = BODY
    p.runs[0].font.color.rgb = RGBColor.from_string(c("text.secondary"))

    h = doc.add_heading("System handover for Building B", level=1)
    h.paragraph_format.space_before = Pt(4)

    lead = doc.add_paragraph(
        "Laporan ini merangkum status kesiapan serah terima Building B per 24 November 2026. "
        "Dua dari empat sistem utama sudah lulus verifikasi; dua lainnya masih terbuka.")
    lead.runs[0].font.color.rgb = RGBColor.from_string(c("text.secondary"))

    doc.add_heading("Temuan utama", level=2)
    for txt in [
        "AHU-03 belum mencapai laju aliran udara desain pada beban 80%.",
        "Fire damper FD-12 gagal uji tutup otomatis; perlu penggantian aktuator.",
        "Pemetaan titik BMS sudah sesuai sequence of operation.",
    ]:
        doc.add_paragraph(txt, style="List Bullet")

    doc.add_heading("Ringkasan verifikasi", level=2)
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    hdr = table.rows[0].cells
    for cell, label in zip(hdr, ("Equipment", "Status", "Verified")):
        cell.text = ""
        run = cell.paragraphs[0].add_run(label.upper())
        run.font.size = Pt(8)
        run.font.name = BODY
        run.font.bold = True
        run.font.color.rgb = RGBColor.from_string(c("text.secondary"))

    for eq, st, dt, tok in [("Chiller CH-01", "Passed", "24 Nov", "status.success"),
                            ("AHU-03", "Pending", "—", "status.warning"),
                            ("Fire damper FD-12", "Failed", "23 Nov", "status.danger")]:
        cells = table.add_row().cells
        for cell, val, col in zip(cells, (eq, st, dt),
                                  ("text.primary", tok, "text.secondary")):
            cell.text = ""
            run = cell.paragraphs[0].add_run(val)
            run.font.size = Pt(10)
            run.font.name = BODY
            run.font.color.rgb = RGBColor.from_string(c(col))

    foot = doc.add_paragraph()
    foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    fr = foot.add_run("Corporate Calm · token-driven sample")
    fr.font.size = Pt(8)
    fr.font.color.rgb = RGBColor.from_string(c("text.muted"))

    doc.save(path)


if __name__ == "__main__":
    out = ROOT / "examples"
    out.mkdir(exist_ok=True)
    # the deck lives in build/deck.py; this script only proves the Word target
    build_report(out / "sample-report.docx")
    print("examples:", *(f.name for f in sorted(out.iterdir())))
