#!/usr/bin/env python3
"""Atlas — one slide per component family, every variant labelled.

This is the reference deck: open it, find the form you want, copy the call from
`build/shapes.py`. Each panel is captioned with the function name (top right) and
the rule that decides when to use it (top left). Nothing here invents a colour.

    python build/atlas.py professional     # examples/atlas-professional.pptx
    python build/atlas.py adventurous
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))

import analyst as A  # noqa: E402
import shapes as S  # noqa: E402
from analyst import M, W, img, r, t  # noqa: E402

A.SLIDES.clear()  # analyst.py builds its own deck at import; the atlas starts empty

GUT2 = 16
GRID_TOP, GRID_BOT = 104, 676


def big(col, row):
    pw = (W - 2 * M - GUT2) / 2
    ph = (GRID_BOT - GRID_TOP - GUT2) / 2
    return M + col * (pw + GUT2), GRID_TOP + row * (ph + GUT2), pw, ph


def box(col, row, name, claim, fn, src="shapes.py"):
    """Panel chrome + body. `fn(ix, iy, iw, ih)` draws inside the panel."""
    x, y, w, h = big(col, row)
    out = [r(x, y, w, h, "surface.raised", "light", radius=6, stroke="border.subtle"),
           *S.kicker(x + 12, y + 9, w - 130, name),
           t(x + 12, y + 23, w - 24, 16, claim, "text.primary", "light", size=10.5,
             bold=True, leading=1.2)]
    if src:
        out.append(t(x + w - 132, y + 9, 120, 10, src, "text.muted", "light", size=6,
                     align="right"))
    out.extend(fn(x + 12, y + 46, w - 24, h - 56))
    return out


def full(name, claim, body, src="shapes.py"):
    x, y, w, h = M, GRID_TOP, W - 2 * M, GRID_BOT - GRID_TOP
    out = [r(x, y, w, h, "surface.raised", "light", radius=6, stroke="border.subtle"),
           *S.kicker(x + 14, y + 10, w - 200, name),
           t(x + 14, y + 24, w - 28, 18, claim, "text.primary", "light", size=11,
             bold=True)]
    if src:
        out.append(t(x + w - 150, y + 10, 136, 10, src, "text.muted", "light", size=6,
                     align="right"))
    out.extend(body)
    return out


# ------------------------------------------------------------------ 01 index
families = [
    ("Blok angka", "kpi_strip · kpi_grid · stat_cards · stat_row"),
    ("Teks & pernyataan", "headline · bullets · quote_block · banner · ticks"),
    ("Tabel & banding", "tbl · compare_table · delta_rows · icon_grid"),
    ("Grafik", "chart bar · chart line · hbar · hstack · waterfall · donut"),
    ("Diagram I", "pyramid · twin_pyramid · band_stack · pillar_framework"),
    ("Diagram II", "concentric · ring_blocks · team_circle · radial"),
    ("Diagram III", "flow_chain · journey_lane · branch · layers_matrix"),
    ("Peta & media", "map_bubbles · map_regions · before_after · photo"),
]
A.add("light", "Atlas bentuk: semua varian layout, diagram, dan grafik di satu tempat",
      None,
      [*full("atlas / index",
             "Delapan keluarga bentuk, satu bahasa visual, palet tidak berubah",
             [*S.list_rows(M + 20, GRID_TOP + 52, W * 0.50, 340, families, "light",
                           rowh=30, num=True),
              *S.label(M + 20, GRID_TOP + 300, W * 0.50,
                       "Tiap fungsi di build/shapes.py mengembalikan list primitif "
                       "(t / r / img), jadi bisa digabung bebas dalam satu slide.",
                       "light")]),
       *S.kpi_grid(W * 0.60, GRID_TOP + 60, W * 0.32, 130,
                   [("28", "komponen siap pakai"), ("8", "keluarga bentuk"),
                    ("4", "tema: 2 palet x light/dark"), ("0", "warna baru")],
                   "light", cols=2),
       *S.label(W * 0.60, GRID_TOP + 210, W * 0.32,
                "Palet professional dan adventurous tidak disentuh: setiap isian "
                "memakai token, jadi atlas benar di kedua palet tanpa edit.", "light"),
       *S.banner(M + 20, GRID_TOP + 400, W - 2 * M - 40, 46,
                 "Aturan pertama: pilih bentuk dari isi, bukan dari selera",
                 "light", "Angka banyak -> blok angka. Perbandingan -> tabel. "
                 "Urutan -> alur. Hubungan -> diagram.")],
      A.FOOT, 1)

# ------------------------------------------------------------------ 02 numbers
A.add("light", "Blok angka: empat cara menaruh metrik tanpa kotak berlebih", None, [
    *box(0, 0, "kpi_strip", "Enam metrik sejajar untuk ringkasan entitas",
         lambda x, y, w, h: S.kpi_strip(
             x, y, w, [("$548B", "aset"), ("$416B", "dana"), ("$317B", "kredit"),
                       ("2.100+", "cabang"), ("15 jt", "klien"), ("52 rb", "staf")],
             "light", h=52)),
    *box(1, 0, "kpi_grid", "Delapan angka dalam grid hairline, tanpa kartu",
         lambda x, y, w, h: S.kpi_grid(
             x, y, w, 190, [("300 jt", "pengguna kripto"), ("$1,57 T", "kapitalisasi"),
                            ("$70 M", "stablecoin on-chain"), ("$8 M", "DeFi per hari"),
                            ("$1,17 T", "volume DEX"), ("$180 M", "stablecoin"),
                            ("$25 M", "NFT"), ("$30 M", "ventura")],
             "light", cols=4)),
    *box(0, 1, "stat_cards", "Tiga kartu: kicker, klaim, satu baris bukti",
         lambda x, y, w, h: S.stat_cards(
             x, y, w, 150, [("B2C suara", "12 mnt perangkat",
                             "1,2 miliar perangkat AI 2024, CAGR 34%"),
                            ("B2C gim", "29% belanja iklan",
                             "86% pembeli pernah beli item virtual"),
                            ("B2B jarak jauh", "2-3x closing",
                             "60%+ kenaikan produktivitas tenaga penjual")], "light")),
    *box(1, 1, "stat_row", "Lima kolom, angka besar di atas label",
         lambda x, y, w, h: S.stat_row(
             x, y, w, 150, [("63%", "Personalisasi", "mau berbagi data"),
                            ("65%", "Kemudahan", "dewasa AS punya Prime"),
                            ("79%", "Pengalaman", "bilang emosi itu penting"),
                            ("45%", "Komunitas", "terpengaruh KOL di China"),
                            ("78%", "Keberlanjutan", "minta aksi iklim")], "light")),
], A.FOOT, 2)

# ------------------------------------------------------------------ 03 text
A.add("light", "Teks dan pernyataan: judul klaim, kutipan, pita penutup, checklist",
      None, [
    *box(0, 0, "headline + bullets", "Satu klaim, tiga turunan — bentuk paling dasar",
         lambda x, y, w, h: [
             *S.headline(x, y, w, 30,
                         "Kesiapan commissioning ditentukan lima celah bukti",
                         "light", size=12),
             *S.body_text(x, y + 34, w, 24,
                          "Bukan anggaran, bukan jadwal: yang menahan serah terima "
                          "adalah dokumen yang tidak pernah dibuat.", "light", size=8),
             *S.bullets(x, y + 66, w, 120,
                        ["Berkas uji tekan belum ditandatangani pemilik",
                         "Log audit peralatan hanya ada di spreadsheet pribadi",
                         "Vendor memakai versi checklist yang berbeda",
                         "Tidak ada satu register untuk lima pihak"], "light", size=8)]),
    *box(1, 0, "quote_block", "Suara pihak ketiga, bukan opini penulis",
         lambda x, y, w, h: S.quote_block(
             x, y + 10, w, 110,
             "Beralih ke kereta hidrogen adalah opsi yang cepat dan layak, "
             "menggantikan elektrifikasi yang mahal.",
             "Menteri Ekonomi, Energi, Transportasi Hessen", "light")),
    *box(0, 1, "banner + ticks", "Pita penutup, lalu daftar yang bisa dicentang",
         lambda x, y, w, h: [
             *S.banner(x, y, w, 40, "Satu register, lima pembaca, satu angka",
                       "light"),
             *S.ticks(x, y + 54, w, 120,
                      ["Kontraktor mencatat di lapangan",
                       "Auditor memverifikasi sampel 5%",
                       "Owner memutuskan di rapat 15 menit",
                       "Bank membaca dashboard yang sama",
                       "Vendor tidak lagi punya versi sendiri"], "light", size=8,
                      gap=19)]),
    *box(1, 1, "list_rows", "Lima baris bernomor untuk daftar gangguan",
         lambda x, y, w, h: S.list_rows(
             x, y, w, 150,
             [("Space mining", "asteroid ditambang, material ke Bumi"),
              ("Konstruksi orbit", "perakitan di orbit, penopang wisata"),
              ("Pembangkit orbit", "surya 24 jam, emisi nol"),
              ("Aktivitas cislunar", "kemitraan publik-swasta Bumi-Bulan"),
              ("Wisata komersial", "penerbangan berbayar, bukan riset")],
             "light", rowh=30)),
], A.FOOT, 3)

# ------------------------------------------------------------------ 04 tables
A.add("light", "Tabel dan blok kecil: banding dua periode, daftar ikon, delta", None, [
    *box(0, 0, "compare_table", "Dua periode + kolom delta; baris kunci disorot",
         lambda x, y, w, h: S.compare_table(
             x, y, w, 160, ("Jangkauan", "2017", "2021"),
             [("Cabang", "5.150", "4.800", "-350"),
              ("Populasi AS", "61%", "79%", "+18"),
              ("Usaha kecil", "68%", "83%", "+15"),
              ("Dana addressable", "$4,4 T", "$7,4 T", "+68%"),
              ("Rumah per cabang", "5.300", "6.600", "+25%")],
             "light", rowh=20, highlight=1)),
    *box(1, 0, "tbl", "Tabel hairline tanpa zebra, angka rata kanan",
         lambda x, y, w, h: A.tbl(
             x, y, w, [("Temuan", "left"), ("Kesiapan", "right"),
                       ("Biaya", "right")],
             [["Berkas uji tekan", "62%", "Rp 1,4 M"],
              ["Log audit peralatan", "48%", "Rp 0,9 M"],
              ["Register vendor", "55%", "Rp 0,6 M"],
              ["Serah terima as-built", "71%", "Rp 1,1 M"],
              ["Kesepakatan pemilik", "39%", "Rp 2,0 M"]],
             "light", rowh=19, value_w=70)),
    *box(0, 1, "delta_rows", "Label, track, delta bertanda — untuk porsi tugas",
         lambda x, y, w, h: S.delta_rows(
             x, y, w, 150, [("Administrasi & rutin", 74, 1),
                            ("Analisis data", 61, 1),
                            ("Dokumentasi teknis", 58, 1),
                            ("Koordinasi lapangan", 33, -1),
                            ("Inspeksi fisik", 12, -1)], "light", rowh=24)),
    *box(1, 1, "icon_grid", "Delapan item berikon: label + satu baris fungsi",
         lambda x, y, w, h: S.icon_grid(
             x, y, w, 160,
             [("Pemantauan pesawat", "paten Ford dipakai avionik"),
              ("Robot bedah", "kontrol presisi otomotif"),
              ("Kebugaran", "sensor gerak turunan otomotif"),
              ("Teknologi visual", "kamera & lidar lintas industri"),
              ("Perangkat medis", "aktuator & katup"),
              ("Farmasi", "otomasi lini produksi"),
              ("Audio", "peredam bising kabin"),
              ("Otomasi rumah", "sensor & konektivitas")], "light", cols=4)),
], A.FOOT, 4)

# ------------------------------------------------------------------ 05 charts
A.add("light", "Grafik: batang, garis, batang horizontal, waterfall", None, [
    *box(0, 0, "chart (bar)", "Batang berkelompok untuk dua seri",
         lambda x, y, w, h: S.chart(
             x, y, w, 190, ["2020", "2021", "2022", "2023", "2024"],
             [{"name": "Rencana", "values": [42, 48, 55, 61, 68],
               "color": "chart.series.1"},
              {"name": "Realisasi", "values": [38, 45, 52, 57, 64],
               "color": "chart.series.3"}], "bar", "light")),
    *box(1, 0, "chart (line)", "Garis untuk tren kontinu, maksimal empat seri",
         lambda x, y, w, h: S.chart(
             x, y, w, 190, ["Q1", "Q2", "Q3", "Q4"],
             [{"name": "Waktu siklus", "values": [18, 16, 13, 11],
               "color": "chart.series.1"},
              {"name": "Rework", "values": [9, 8, 6, 4],
               "color": "chart.series.4"}], "line", "light")),
    *box(0, 1, "hbar + hstack", "Peringkat (hbar) dan porsi dari total (hstack)",
         lambda x, y, w, h: [
             *S.label(x, y - 8, 200, "PERINGKAT — hbar", "light"),
             A.hbar(x, y + 4, w, 76,
                     [("Kontraktor", 92), ("Owner", 74), ("Konsultan", 58),
                      ("Vendor", 41)], "light", label_w=74),
             *S.label(x, y + 86, 200, "PORSI — hstack", "light"),
             A.hstack(x, y + 98, w, 60,
                       [("Terverifikasi", 68, 100), ("Tercatat", 43, 100)],
                       "light")]),
    *box(1, 1, "waterfall", "Jembatan dari baseline ke hasil: naik, turun, total",
         lambda x, y, w, h: S.waterfall(
             x, y + 6, w, 150, [("Baseline", 100, "start"), ("Digital", 22, "up"),
                                ("Lean", 14, "up"), ("Rework", -18, "down"),
                                ("Hasil", 0, "total")], "light")),
], A.FOOT, 5)

# ------------------------------------------------------------------ 06 diagrams I
A.add("light", "Diagram I: piramida, sebelum-sesudah, pita strategi, kerangka pilar",
      None, [
    *box(0, 0, "pyramid", "Empat lapis, alas lebar; apex sempit di atas",
         lambda x, y, w, h: S.pyramid(
             x, y, w, 180, [("Dampak", "satu angka yang dijual"),
                            ("Inisiatif", "tiga program berjalan"),
                            ("Kapabilitas", "orang, proses, sistem"),
                            ("Data", "satu register, lima pembaca")],
             "light", apex=0.42)),
    *box(1, 0, "twin_pyramid", "Sebelum vs sesudah, panah tuas di tengah",
         lambda x, y, w, h: S.twin_pyramid(
             x, y + 14, w, 165, [("Model bisnis", "cara menyalurkan nilai"),
                                 ("Model operasi", "cara menjalankan"),
                                 ("Model modal", "cara membiayai")],
             "light", "Sekarang", "Setelah SCT", "Tarik tuas")),
    *box(0, 1, "band_stack", "Pita selebar panel: label kiri, penjelasan kanan",
         lambda x, y, w, h: S.band_stack(
             x, y, w, 180, [("Segmen klien", "Mass affluent · HNW · UHNW, satu funnel"),
                            ("Empat unit", "konsumen · advisory · private · bank"),
                            ("Kemampuan", "digital diperkuat, referral dirapikan"),
                            ("Sumbu", "digital-empowered ke advisor-led")], "light")),
    *box(1, 1, "pillar_framework", "Kepala, tiga pilar, tiga baris tanggung jawab",
         lambda x, y, w, h: S.pillar_framework(
             x, y, w, 180, "Strategi: pertumbuhan berkelanjutan dan inklusif",
             ["Environment", "Social", "Governance"], ["Klien", "Firma", "Pemangku"],
             [["Transisi klien", "Inklusi akses", "Transparansi produk"],
              ["Net-zero 2030", "20 rb profesional", "Tata kelola risiko"],
              ["Jalur 1,5 C", "Investasi komunitas", "Kebijakan pajak"]], "light")),
], A.FOOT, 6)

# ------------------------------------------------------------------ 07 diagrams II
A.add("light", "Diagram II: cincin, blok mengelilingi pusat, hub radial", None, [
    *box(0, 0, "concentric", "Tiga cincin: klaim inti, tiga tuas, satu bingkai",
         lambda x, y, w, h: S.concentric(
             x + 6, y - 6, w - 12, 190, "Klien",
             ["Relasi", "Orang", "Eksekusi"], "Inovasi", "light")),
    *box(1, 0, "ring_blocks", "Empat unit di sekitar satu perusahaan",
         lambda x, y, w, h: S.ring_blocks(
             x, y + 4, w, 175, "Satu firma",
             ["Investment banking", "Global markets", "Consumer & wealth",
              "Asset management"], "light")),
    *box(0, 1, "team_circle", "Delapan simpul di sekitar satu klaim",
         lambda x, y, w, h: S.team_circle(
             x, y + 2, w, 180, "20 rb profesional\nkhusus risiko",
             ["Kepatuhan", "Risiko", "Keuangan", "Legal", "Kontrol", "Siber",
              "KYC & AML", "Fraud"], "light")),
    *box(1, 1, "radial", "Hub + lima satelit: siapa membaca angka yang sama",
         lambda x, y, w, h: A.radial(
             x, y + 2, w, 180, "Register",
             ["Kontraktor", "Owner", "Vendor", "Konsultan", "Bank"], "light")),
], A.FOOT, 7)

# ------------------------------------------------------------------ 08 diagrams III
A.add("light", "Diagram III: alur, perjalanan dua jalur, percabangan, matriks", None, [
    *box(0, 0, "flow_chain", "Empat langkah berurutan, catatan di bawah",
         lambda x, y, w, h: S.flow_chain(
             x, y + 20, w, 140, [("Temuan", "audit lapangan, 5 celah"),
                                 ("Bukti", "dokumen + foto, satu format"),
                                 ("Putusan", "rapat 15 menit, satu pemilik"),
                                 ("Anggaran", "biaya per celah, disetujui")],
             "light")),
    *box(1, 0, "journey_lane", "Dua jalur (online/offline), lima tahap, satu rute",
         lambda x, y, w, h: S.journey_lane(
             x, y + 6, w, 180,
             ["Discovery", "Evaluation", "Purchase", "Support", "Returns"],
             ["Online", "Offline"],
             [(0, 0, "video"), (1, 1, "kunjungan"), (2, 0, "checkout"),
              (3, 1, "serah"), (4, 1, "retur")], "light")),
    *box(0, 1, "branch", "Satu batang, dua cabang, dua simpul per cabang",
         lambda x, y, w, h: S.branch(
             x, y + 10, w, 170, "Nilai", "Pembaca",
             [("Untuk merek", ["Alat paham konsumen", "Kanal rekrut advokat"]),
              ("Untuk ritel", ["Mitigasi risiko reputasi", "Sumber bisnis baru"])],
             "light")),
    *box(1, 1, "layers_matrix", "Baris lapis x kolom pilar: siapa mengerjakan apa",
         lambda x, y, w, h: A.layers_matrix(
             x, y + 6, w, 170, ["Catat", "Verifikasi", "Putusan"],
             ["Orang", "Proses", "Sistem"],
             [["Teknisi", "Auditor", "Steering"],
              ["Checklist", "Sampel 5%", "Rapat 15 mnt"],
              ["Form + foto", "Log audit", "Dashboard"]], "light")),
], A.FOOT, 8)

# ------------------------------------------------------------------ 09 maps + media
A.add("light", "Peta dan media: gelembung proporsional, region, sebelum-sesudah, foto",
      None, [
    *box(0, 0, "map_bubbles", "Ukuran lingkaran = nilai; koordinat relatif 0-1",
         lambda x, y, w, h: S.map_bubbles(
             x, y, w, 170, [("China", 0.70, 0.42, "$740", 52),
                            ("AS", 0.22, 0.40, "$561", 44),
                            ("Rusia", 0.60, 0.24, "$110", 26),
                            ("Inggris", 0.46, 0.32, "$93", 24),
                            ("Jepang", 0.82, 0.40, "$87", 23),
                            ("Brasil", 0.32, 0.70, "$16", 13)], "light",
             "placeholder geo — ganti dengan SVG peta asli")),
    *box(1, 0, "map_regions", "Sebaran responden per kawasan di dalam bingkai",
         lambda x, y, w, h: S.map_regions(
             x, y, w, 170, [("Americas", 43, "524 responden"),
                            ("EMEA", 37, "461 responden"),
                            ("APAC", 20, "245 responden")], "light",
             "placeholder geo — 1.230 responden, 11 industri, 14 negara")),
    *box(0, 1, "before_after", "Dua bingkai peta + label periode + jumlah titik",
         lambda x, y, w, h: S.before_after(
             x, y, w, 165, ("2017", "5.150 cabang"), ("2021", "4.800 cabang"),
             "light", "placeholder geo — jumlah titik = jumlah cabang")),
    *box(1, 1, "photo + donut", "Foto sebagai blok, donut kecil sebagai bukti",
         lambda x, y, w, h: [
             *S.label(x, y - 8, 260, "FOTO PENUH — satu blok warna per slide",
                      "light"),
             img(x, y + 4, w * 0.52, 120, "photo-cover.png", radius=4),
             *S.donut_row(x + w * 0.56, y + 26, w * 0.44,
                          [(68, "Terverifikasi"), (43, "Tercatat")], "light", d=44)]),
], A.FOOT, 9)


if __name__ == "__main__":
    out = ROOT / "examples" / f"atlas-{A.PALETTE}.pptx"
    A.render_pptx(out)
    html = ROOT / "examples" / f"preview-atlas-{A.PALETTE}.html"
    A.render_html(html)
    print("wrote", out.name, "+", html.name, len(A.SLIDES), "slides")
