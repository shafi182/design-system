#!/usr/bin/env python3
"""Pitch deck v0.4 — one slide spec, two renderers (pptx + html preview).

M2: the palette, token, geometry and pptx-emission foundation now lives in
build/base.py. This module keeps the slide content (SLIDES) and re-exports the
original public surface as a compatibility shim.

    python build/photos.py      # placeholders (replace the PNGs with real shots)
    python build/deck.py        # examples/pitch-deck.pptx
"""
from __future__ import annotations

import sys
from pathlib import Path

import base
from base import (ALIGN, H, M, PHOTOS, PX, ROOT, ROUNDED, TOK, W, add_chart, card,
                  chart, font_of, footer, hexof, img, kicker, load_palette,
                  photo_src, r, rounded_photo, stat, t, tok)

__all__ = [
    "ALIGN", "DARK", "H", "LIGHT", "M", "PALETTE", "PHOTOS", "PX", "ROOT",
    "ROUNDED", "SLIDES", "TOK", "W",
    "add_chart", "card", "chart", "font_of", "footer", "hexof", "img", "kicker",
    "load_palette", "photo_src", "r", "render_pptx", "rounded_photo", "stat",
    "t", "tok",
]

# PALETTE / LIGHT / DARK are deliberately not bound in this module: PEP 562
# forwarding keeps them live, so deck.LIGHT is always base.LIGHT.
_LIVE = ("PALETTE", "LIGHT", "DARK")


def __getattr__(name: str):
    if name in _LIVE:
        return getattr(base, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
        t(M + 860, 534, 250, 40, "0 sengketa", "brand.accent-text", size=20, bold=True,
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

        r(M, 280, 520, 300, "surface.raised", radius=18, stroke="border.strong", stroke_w=1.5),
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
        t(M + 900, 312, 236, 30, "+12%", "brand.accent-text", "dark", size=15, bold=True,
          font="mono", align="right"),
        r(M, 372, 1136, 1, "border.subtle", "dark"),

        t(M, 396, 460, 22, "Biaya serah terima", "text.secondary", "dark", size=12),
        t(M + 480, 390, 400, 44, "Rp 96 jt", "text.primary", "dark", size=36, bold=True,
          font="mono", leading=1.0, align="right"),
        t(M + 900, 402, 236, 30, "−11 hari", "brand.accent-text", "dark", size=15, bold=True,
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

def render_pptx(path: Path, *, palette=None, appearance=None, theme=None) -> None:
    """Compatibility wrapper: this deck renders its own SLIDES through base.

    ``palette=`` and ``appearance=`` are independent (M3); ``theme=`` is the
    deprecated alias for ``appearance=``.
    """
    base.render_pptx(path, SLIDES, palette=palette, appearance=appearance, theme=theme)


if __name__ == "__main__":
    load_palette(sys.argv[1] if len(sys.argv) > 1 else base.PALETTE)
    out = ROOT / "examples" / f"pitch-deck-{base.PALETTE}.pptx"
    out.parent.mkdir(exist_ok=True)
    render_pptx(out)
    print("wrote", out, len(SLIDES), "slides")
