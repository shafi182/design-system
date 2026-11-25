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
    out.extend(fn(x + 12, y + 46, w - 24, h - 58))
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
    ("Grafik", "chart · hbar · hstack · waterfall · donut"),
    ("Diagram I", "pyramid · twin_pyramid · band_stack · pillars"),
    ("Diagram II", "concentric · ring_blocks · team_circle · radial"),
    ("Diagram III", "flow_chain · journey_lane · branch · layers"),
    ("Peta & media", "map_bubbles · map_regions · before_after · photo"),
]
A.add("light", "Atlas bentuk: semua varian layout, diagram, dan grafik di satu tempat",
      None,
      [*full("atlas / index",
             "Delapan keluarga bentuk, satu bahasa visual, palet tidak berubah",
             [*S.list_rows(M + 20, GRID_TOP + 52, W * 0.545, 300, families, "light",
                           rowh=34, num=True),
              *S.label(M + 20, GRID_TOP + 366, W * 0.545,
                       "Tiap fungsi di build/shapes.py mengembalikan list primitif "
                       "(t / r / img), jadi bisa digabung bebas dalam satu slide.",
                       "light", size=8),
              *S.kpi_grid(W * 0.60, GRID_TOP + 52, W * 0.345, 150,
                          [("28", "komponen siap pakai"), ("8", "keluarga bentuk"),
                           ("4", "tema: 2 palet x light/dark"), ("0", "warna baru")],
                          "light", cols=2),
              *S.label(W * 0.60, GRID_TOP + 214, W * 0.345, "CARA PAKAI", "light",
                       color="brand.primary", size=7),
              *S.bullets(W * 0.60, GRID_TOP + 228, W * 0.345, 120,
                         ["Buka panel sesuai jenis isi",
                          "Salin nama fungsi ke slide baru",
                          "Isi hanya token, jangan hex",
                          "Cek kontras: build.py --check"], "light", size=8, gap=17),
              *S.banner(M + 20, GRID_BOT - 66, W - 2 * M - 40, 46,
                        "Aturan pertama: pilih bentuk dari isi, bukan dari selera",
                        "light", "Angka banyak -> blok angka. Perbandingan -> tabel. "
                        "Urutan -> alur. Hubungan -> diagram.")])],
      A.FOOT, 1)

# ------------------------------------------------------------------ 02 numbers
A.add("light", "Blok angka: empat cara menaruh metrik tanpa kotak berlebih", None, [
    *box(0, 0, "kpi_strip", "Enam metrik sejajar untuk ringkasan entitas",
         lambda x, y, w, h: [
             *S.kpi_strip(x, y, w,
                          [("$548B", "aset"), ("$416B", "dana"), ("$317B", "kredit"),
                           ("2.100+", "cabang"), ("15 jt", "klien"), ("52 rb", "staf")],
                          "light", h=72),
             *S.label(x, y + 86, w, "VERSI TIGA KOLOM — untuk slide sempit", "light"),
             *S.kpi_strip(x, y + 100, w,
                          [("2-3x", "closing jarak jauh"), ("60%+", "produktivitas"),
                           ("34%", "CAGR perangkat AI")], "light", h=72),
             *S.label(x, y + 186, w,
                      "Pakai strip kalau angka adalah pembuka slide, bukan bukti "
                      "utama. Maksimal enam, satuannya konsisten.", "light", size=7.5)]),
    *box(1, 0, "kpi_grid", "Delapan angka dalam grid hairline, tanpa kartu",
         lambda x, y, w, h: S.kpi_grid(
             x, y, w, h, [("300 jt", "pengguna kripto"), ("$1,57 T", "kapitalisasi"),
                          ("$70 M", "stablecoin on-chain"), ("$8 M", "DeFi per hari"),
                          ("$1,17 T", "volume DEX"), ("$180 M", "stablecoin"),
                          ("$25 M", "NFT"), ("$30 M", "ventura")],
             "light", cols=4)),
    *box(0, 1, "stat_cards", "Tiga kartu: kicker, klaim, satu baris bukti",
         lambda x, y, w, h: S.stat_cards(
             x, y, w, h, [("B2C suara", "12 mnt perangkat",
                           "1,2 miliar perangkat AI 2024, CAGR 34%"),
                          ("B2C gim", "29% belanja iklan",
                           "86% pembeli pernah beli item virtual"),
                          ("B2B jarak jauh", "2-3x closing",
                           "60%+ kenaikan produktivitas tenaga penjual")], "light")),
    *box(1, 1, "stat_row", "Lima kolom, angka besar di atas label",
         lambda x, y, w, h: [
             *S.stat_row(x, y, w, h * 0.62,
                         [("63%", "Personalisasi", "mau berbagi data"),
                          ("65%", "Kemudahan", "dewasa AS punya Prime"),
                          ("79%", "Pengalaman", "bilang emosi itu penting"),
                          ("45%", "Komunitas", "terpengaruh KOL di China"),
                          ("78%", "Keberlanjutan", "minta aksi iklim")], "light"),
             *S.label(x, y + h * 0.66, w, "ANGKA SAMA, TANPA PITA", "light"),
             *S.donut_row(x, y + h * 0.80, w,
                          [(63, "Personalisasi"), (79, "Pengalaman")], "light", d=40)]),
], A.FOOT, 2)

# ------------------------------------------------------------------ 03 text
A.add("light", "Teks dan pernyataan: judul klaim, kutipan, pita penutup, checklist",
      None, [
    *box(0, 0, "headline + bullets", "Satu klaim, tiga turunan — bentuk paling dasar",
         lambda x, y, w, h: [
             *S.headline(x, y, w, 30,
                         "Kesiapan commissioning ditentukan lima celah bukti",
                         "light", size=13),
             *S.body_text(x, y + 36, w, 26,
                          "Bukan anggaran, bukan jadwal: yang menahan serah terima "
                          "adalah dokumen yang tidak pernah dibuat.", "light", size=8.5),
             *S.bullets(x, y + 74, w, h - 80,
                        ["Berkas uji tekan belum ditandatangani pemilik",
                         "Log audit peralatan hanya ada di spreadsheet pribadi",
                         "Vendor memakai versi checklist yang berbeda",
                         "Tidak ada satu register untuk lima pihak"], "light",
                        size=8.5, gap=(h - 84) / 4)]),
    *box(1, 0, "quote_block", "Suara pihak ketiga, bukan opini penulis",
         lambda x, y, w, h: S.quote_block(
             x, y, w, h,
             "Beralih ke kereta hidrogen adalah opsi yang cepat dan layak, "
             "menggantikan elektrifikasi yang mahal.",
             "Menteri Ekonomi, Energi, Transportasi Hessen", "light")),
    *box(0, 1, "banner + ticks", "Pita penutup, lalu daftar yang bisa dicentang",
         lambda x, y, w, h: [
             *S.banner(x, y, w, 48, "Satu register, lima pembaca, satu angka",
                       "light", "Bukti dikumpulkan sekali, dibaca lima pihak."),
             *S.ticks(x, y + 62, w, h - 68,
                      ["Kontraktor mencatat di lapangan",
                       "Auditor memverifikasi sampel 5%",
                       "Owner memutuskan di rapat 15 menit",
                       "Bank membaca dashboard yang sama",
                       "Vendor tidak lagi punya versi sendiri"], "light", size=8.5,
                      gap=(h - 68) / 5)]),
    *box(1, 1, "list_rows", "Lima baris bernomor untuk daftar gangguan",
         lambda x, y, w, h: S.list_rows(
             x, y, w, h,
             [("Space mining", "asteroid ditambang, material ke Bumi"),
              ("Konstruksi orbit", "perakitan di orbit, penopang wisata"),
              ("Pembangkit orbit", "surya 24 jam, emisi nol"),
              ("Aktivitas cislunar", "kemitraan publik-swasta Bumi-Bulan"),
              ("Wisata komersial", "penerbangan berbayar, bukan riset")],
             "light", rowh=h / 5)),
], A.FOOT, 3)

# ------------------------------------------------------------------ 04 tables
A.add("light", "Tabel dan blok kecil: banding dua periode, daftar ikon, delta", None, [
    *box(0, 0, "compare_table", "Dua periode + kolom delta; baris kunci disorot",
         lambda x, y, w, h: S.compare_table(
             x, y, w, h, ("Jangkauan", "2017", "2021"),
             [("Cabang", "5.150", "4.800", "-350"),
              ("Populasi AS", "61%", "79%", "+18"),
              ("Usaha kecil", "68%", "83%", "+15"),
              ("Dana addressable", "$4,4 T", "$7,4 T", "+68%"),
              ("Rumah per cabang", "5.300", "6.600", "+25%")],
             "light", rowh=(h - 26) / 5, highlight=1)),
    *box(1, 0, "tbl", "Tabel hairline tanpa zebra, angka rata kanan",
         lambda x, y, w, h: A.tbl(
             x, y, w, [("Temuan", "left"), ("Kesiapan", "right"),
                       ("Biaya", "right")],
             [["Berkas uji tekan", "62%", "Rp 1,4 M"],
              ["Log audit peralatan", "48%", "Rp 0,9 M"],
              ["Register vendor", "55%", "Rp 0,6 M"],
              ["Serah terima as-built", "71%", "Rp 1,1 M"],
              ["Kesepakatan pemilik", "39%", "Rp 2,0 M"]],
             "light", rowh=(h - 24) / 5, value_w=78)),
    *box(0, 1, "delta_rows", "Label, track, delta bertanda — untuk porsi tugas",
         lambda x, y, w, h: S.delta_rows(
             x, y, w, h, [("Administrasi & rutin", 74, 1),
                          ("Analisis data", 61, 1),
                          ("Dokumentasi teknis", 58, 1),
                          ("Koordinasi lapangan", 33, -1),
                          ("Inspeksi fisik", 12, -1)], "light", rowh=h / 5)),
    *box(1, 1, "icon_grid", "Delapan item berikon: label + satu baris fungsi",
         lambda x, y, w, h: S.icon_grid(
             x, y, w, h,
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
             x, y, w, h, ["2020", "2021", "2022", "2023", "2024"],
             [{"name": "Rencana", "values": [42, 48, 55, 61, 68],
               "color": "chart.series.1"},
              {"name": "Realisasi", "values": [38, 45, 52, 57, 64],
               "color": "chart.series.3"}], "bar", "light")),
    *box(1, 0, "chart (line)", "Garis untuk tren kontinu, maksimal empat seri",
         lambda x, y, w, h: S.chart(
             x, y, w, h, ["Q1", "Q2", "Q3", "Q4"],
             [{"name": "Waktu siklus", "values": [18, 16, 13, 11],
               "color": "chart.series.1"},
              {"name": "Rework", "values": [9, 8, 6, 4],
               "color": "chart.series.4"}], "line", "light")),
    *box(0, 1, "hbar + hstack", "Peringkat (hbar) dan porsi dari total (hstack)",
         lambda x, y, w, h: [
             *S.label(x, y - 8, 220, "PERINGKAT — hbar", "light"),
             A.hbar(x, y + 4, w, h * 0.46,
                    [("Kontraktor", 92), ("Owner", 74), ("Konsultan", 58),
                     ("Vendor", 41)], "light", label_w=74),
             *S.label(x, y + h * 0.56, 220, "PORSI — hstack", "light"),
             A.hstack(x, y + h * 0.68, w, h * 0.30,
                      [("Terverifikasi", 68, 100), ("Tercatat", 43, 100)],
                      "light")]),
    *box(1, 1, "waterfall", "Jembatan dari baseline ke hasil: naik, turun, total",
         lambda x, y, w, h: S.waterfall(
             x, y, w, h, [("Baseline", 100, "start"), ("Digital", 22, "up"),
                          ("Lean", 14, "up"), ("Rework", -18, "down"),
                          ("Hasil", 0, "total")], "light")),
], A.FOOT, 5)

# ------------------------------------------------------------------ 06 diagrams I
A.add("light", "Diagram I: piramida, sebelum-sesudah, pita strategi, kerangka pilar",
      None, [
    *box(0, 0, "pyramid", "Empat lapis, alas lebar; apex sempit di atas",
         lambda x, y, w, h: S.pyramid(
             x, y, w, h, [("Dampak", "satu angka yang dijual"),
                          ("Inisiatif", "tiga program berjalan"),
                          ("Kapabilitas", "orang, proses, sistem"),
                          ("Data", "satu register, lima pembaca")],
             "light", apex=0.42)),
    *box(1, 0, "twin_pyramid", "Sebelum vs sesudah, panah tuas di tengah",
         lambda x, y, w, h: S.twin_pyramid(
             x, y, w, h, [("Model bisnis", "cara menyalurkan nilai"),
                          ("Model operasi", "cara menjalankan"),
                          ("Model modal", "cara membiayai")],
             "light", "Sekarang", "Setelah SCT", "Tarik tuas")),
    *box(0, 1, "band_stack", "Pita selebar panel: label kiri, penjelasan kanan",
         lambda x, y, w, h: S.band_stack(
             x, y, w, h, [("Segmen klien", "Mass affluent · HNW · UHNW, satu funnel"),
                          ("Empat unit", "konsumen · advisory · private · bank"),
                          ("Kemampuan", "digital diperkuat, referral dirapikan"),
                          ("Sumbu", "digital-empowered ke advisor-led")], "light")),
    *box(1, 1, "pillar_framework", "Kepala, tiga pilar, tiga baris tanggung jawab",
         lambda x, y, w, h: S.pillar_framework(
             x, y, w, h, "Strategi: pertumbuhan berkelanjutan dan inklusif",
             ["Environment", "Social", "Governance"], ["Klien", "Firma", "Pemangku"],
             [["Transisi klien", "Inklusi akses", "Transparansi produk"],
              ["Net-zero 2030", "20 rb profesional", "Tata kelola risiko"],
              ["Jalur 1,5 C", "Investasi komunitas", "Kebijakan pajak"]], "light")),
], A.FOOT, 6)

# ------------------------------------------------------------------ 07 diagrams II
A.add("light", "Diagram II: cincin, blok mengelilingi pusat, hub radial", None, [
    *box(0, 0, "concentric", "Tiga cincin: klaim inti, tiga tuas, satu bingkai",
         lambda x, y, w, h: S.concentric(
             x + 6, y, w - 12, h, "Klien",
             ["Relasi", "Orang", "Eksekusi"], "Inovasi", "light")),
    *box(1, 0, "ring_blocks", "Empat unit di sekitar satu perusahaan",
         lambda x, y, w, h: S.ring_blocks(
             x, y, w, h, "Satu firma",
             ["Investment banking", "Global markets", "Consumer & wealth",
              "Asset management"], "light")),
    *box(0, 1, "team_circle", "Delapan simpul di sekitar satu klaim",
         lambda x, y, w, h: S.team_circle(
             x, y, w, h, "20 rb profesional\nkhusus risiko",
             ["Kepatuhan", "Risiko", "Keuangan", "Legal", "Kontrol", "Siber",
              "KYC & AML", "Fraud"], "light")),
    *box(1, 1, "radial", "Hub + lima satelit: siapa membaca angka yang sama",
         lambda x, y, w, h: A.radial(
             x, y, w, h, "Register",
             ["Kontraktor", "Owner", "Vendor", "Konsultan", "Bank"], "light")),
], A.FOOT, 7)

# ------------------------------------------------------------------ 08 diagrams III
A.add("light", "Diagram III: alur, perjalanan dua jalur, percabangan, matriks", None, [
    *box(0, 0, "flow_chain", "Empat langkah berurutan, catatan di bawah",
         lambda x, y, w, h: S.flow_chain(
             x, y, w, h, [("Temuan", "audit lapangan, 5 celah"),
                          ("Bukti", "dokumen + foto, satu format"),
                          ("Putusan", "rapat 15 menit, satu pemilik"),
                          ("Anggaran", "biaya per celah, disetujui")], "light")),
    *box(1, 0, "journey_lane", "Dua jalur (online/offline), lima tahap, satu rute",
         lambda x, y, w, h: S.journey_lane(
             x, y, w, h,
             ["Discovery", "Evaluation", "Purchase", "Support", "Returns"],
             ["Online", "Offline"],
             [(0, 0, "video"), (1, 1, "kunjungan"), (2, 0, "checkout"),
              (3, 1, "serah"), (4, 1, "retur")], "light")),
    *box(0, 1, "branch", "Satu batang, dua cabang, dua simpul per cabang",
         lambda x, y, w, h: S.branch(
             x, y, w, h, "Nilai", "Pembaca",
             [("Untuk merek", ["Alat paham konsumen", "Kanal rekrut advokat"]),
              ("Untuk ritel", ["Mitigasi risiko reputasi", "Sumber bisnis baru"])],
             "light")),
    *box(1, 1, "layers_matrix", "Baris lapis x kolom pilar: siapa mengerjakan apa",
         lambda x, y, w, h: A.layers_matrix(
             x, y, w, h, ["Catat", "Verifikasi", "Putusan"],
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
             x, y, w, h, [("China", 0.70, 0.42, "$740", 52),
                          ("AS", 0.22, 0.40, "$561", 44),
                          ("Rusia", 0.60, 0.24, "$110", 26),
                          ("Inggris", 0.46, 0.32, "$93", 24),
                          ("Jepang", 0.82, 0.40, "$87", 23),
                          ("Brasil", 0.32, 0.70, "$16", 13)], "light",
             "placeholder geo — ganti dengan SVG peta asli")),
    *box(1, 0, "map_regions", "Sebaran responden per kawasan di dalam bingkai",
         lambda x, y, w, h: S.map_regions(
             x, y, w, h, [("Americas", 43, "524 responden"),
                          ("EMEA", 37, "461 responden"),
                          ("APAC", 20, "245 responden")], "light",
             "placeholder geo — 1.230 responden, 11 industri, 14 negara")),
    *box(0, 1, "before_after", "Dua bingkai peta + label periode + jumlah titik",
         lambda x, y, w, h: S.before_after(
             x, y, w, h, ("2017", "5.150 cabang"), ("2021", "4.800 cabang"),
             "light", "placeholder geo — jumlah titik = jumlah cabang")),
    *box(1, 1, "photo + donut", "Foto sebagai blok, donut kecil sebagai bukti",
         lambda x, y, w, h: [
             *S.label(x, y - 8, 260, "FOTO PENUH — satu blok warna per slide",
                      "light"),
             img(x, y + 4, w * 0.52, h - 20, "photo-cover.png", radius=4),
             *S.donut_row(x + w * 0.56, y + h * 0.18, w * 0.44,
                          [(68, "Terverifikasi"), (43, "Tercatat")], "light", d=46)]),
], A.FOOT, 9)


# ------------------------------------------------------- 10 matrices + cards + ranks
A.add("light", "Matriks, kartu, peringkat: pernyataan di atas, sel di bawah", None, [
    *box(0, 0, "matrix_header", "Pil pernyataan + kolom pilar x baris pemangku",
         lambda x, y, w, h: S.matrix_header(
             x, y, w, h, "Strategi: mempercepat pertumbuhan yang berkelanjutan dan inklusif",
             ["Lingkungan", "Sosial", "Tata kelola"], ["Klien", "Perusahaan", "Pemangku"],
             [["Produk hijau", "Literasi finansial", "Etika data"],
              ["Emisi -50%", "Paritas upah", "Rapat dewan"],
              ["Bahan baku", "Program desa", "Transparansi"]], "light")),
    *box(1, 0, "benefit_panel", "Daftar manfaat di kiri, panel gelap kasus pakai di kanan",
         lambda x, y, w, h: S.benefit_panel(
             x, y, w, h,
             [("Keamanan", "Kontrak terenkripsi di rantai blok"),
              ("Kecepatan", "Kode mengeksekusi tanpa menunggu pihak ketiga"),
              ("Akurasi", "Menghapus kesalahan entri manual"),
              ("Otonomi", "Risiko pihak ketiga turun lewat disintermediasi"),
              ("Biaya", "Tanpa perantara, tanpa rekonsiliasi"),
              ("Cadangan", "Dokumen tersimpan dan pulih dari rantai")],
             "KASUS PAKAI", ["Properti: escrow, sertifikat, hipotek", "Pembiayaan dagang",
                             "Rantai pasok", "Pembayaran pemerintah", "Klaim asuransi",
                             "Jasa keuangan"], "light")),
    *box(0, 1, "country_cards", "Kartu per negara: klaim + metrik bertanda +/-",
         lambda x, y, w, h: S.country_cards(
             x, y, w, h,
             [("Indonesia", "E-commerce menarik ekonomi", [("E-commerce", "+54%", "+54%"),
                                                           ("GMV", "$8B", "+$6B"),
                                                           ("Travel", "$4B", "-60%")]),
              ("Filipina", "Kiriman makanan dan e-commerce", [("Food delivery", "+50%", "+50%"),
                                                              ("E-commerce", "+40%", "+40%"),
                                                              ("Travel", "-60%", "-60%")]),
              ("Thailand", "E-commerce naik, travel jatuh", [("E-commerce", "+8%", "+8%"),
                                                             ("Food delivery", "+4%", "+4%"),
                                                             ("Transport", "-53%", "-53%")]),
              ("Malaysia", "Food delivery dan e-commerce", [("E-commerce", "+8%", "+8%"),
                                                            ("Food delivery", "+44%", "+44%"),
                                                            ("Travel", "-39%", "-39%")]),
              ("Singapura", "Kekuatan regional, paparan travel", [("E-commerce", "+87%", "+87%"),
                                                                 ("Travel", "-70%", "-70%"),
                                                                 ("GMV", "dataran", "0")]),
              ("Vietnam", "Lonjakan di semua vertikal", [("Travel", "-28%", "-28%"),
                                                         ("E-commerce", "+46%", "+46%"),
                                                         ("Transport", "+32%", "+32%")])],
             "light")),
    *box(1, 1, "ranked_barriers", "Angka utama di kiri, peringkat berlatar di kanan",
         lambda x, y, w, h: S.ranked_barriers(
             x, y, w, h, ("67%", "Pedagang digital menaruh privasi dan keamanan sebagai "
                                "penghalang utama adopsi pinjaman digital"),
             [("Privasi dan keamanan", True), ("Pilihan bank dan asuransi lebih banyak", False),
              ("Tidak memenuhi syarat minimum", False), ("Tidak percaya jasa keuangan digital", True),
              ("Biaya penggunaan tinggi", False)], "light")),
], A.FOOT, 10)

# ---------------------------------------------------- 11 orbit + segments + hubs
A.add("light", "Orbit, segmen, hub ganda, dan empat aksi", None, [
    *box(0, 0, "orbit_ring", "Tujuh topik mengorbit satu pernyataan inti",
         lambda x, y, w, h: S.orbit_ring(
             x, y, w, h, "Pertumbuhan berkelanjutan dan inklusif",
             [("Pertumbuhan", "Persaingan dan produktivitas"),
              ("Pasar modal", "Investasi dan alokasi aset"),
              ("Konsumen", "Perilaku dan kesehatan"),
              ("Masyarakat", "Institusi dan kepercayaan"),
              ("Sumber daya", "Transisi energi dan lahan"),
              ("Tenaga kerja", "Keterampilan dan mobilitas"),
              ("Teknologi", "Difusi AI dan inovasi")], "light")),
    *box(1, 0, "segment_split", "Satu bar proporsional: pangsa di atas, nama di bawah",
         lambda x, y, w, h: S.segment_split(
             x, y, w, h,
             [("Pengguna mapan", 18), ("Digital native muda", 17), ("Arus utama kota", 18),
              ("Hemat", 12), ("Pinggiran kota", 41)], "light",
             "Definisi pinggiran kota: populasi 300-500 ribu, daring minimal dua minggu sekali")),
    *box(0, 1, "twin_hub", "Dua hub bersebelahan: peran sebelum dan sesudah",
         lambda x, y, w, h: S.twin_hub(
             x, y, w, h,
             ("Produk", ["Media", "Inspirasi", "Konten", "Pengalaman", "Layanan"],
              "MEREK SEBAGAI PRODUKSEN", "Semua lapis melayani produk"),
             ("Interaksi", ["Produsen", "Media", "Kurasi", "Layanan", "Komunitas"],
              "MEREK SEBAGAI KURATOR", "Semua lapis melayani interaksi"), "light")),
    *box(1, 1, "quad_actions", "Empat aksi bernomor dalam blok 2x2",
         lambda x, y, w, h: S.quad_actions(
             x, y, w, h,
             [("01", "Buka solusi yang sudah terbukti",
               "Rencana dekarbonisasi menyeluruh, kerangka dan insentif lebih kuat"),
              ("02", "Tangani biaya transisi energi",
               "Rinci biaya penuh dan sumber pendanaannya"),
              ("03", "Perkuat pembiayaan hijau",
               "Produk investasi dekarbonisasi menurunkan biaya modal"),
              ("04", "Dorong kolaborasi regional",
               "Kemitraan lintas rantai nilai, sektor, dan publik-swasta")], "light")),
], A.FOOT, 11)


# ------------------------------------------- 12 architecture + geo + nodes + cycle
A.add("light", "Arsitektur saluran, peta per segmen, node bertema, siklus tata kelola", None, [
    *box(0, 0, "channel_arch", "Saluran akuisisi di atas, merek di tengah, produk + chip strategi",
         lambda x, y, w, h: S.channel_arch(
             x, y, w, h,
             ["Pemasaran langsung", "Aplikasi alat finansial", "Merchant di titik jual",
              "Korporat via unit", "Relasi korporat"],
             "Merek inti", [("Cek", "bangun"), ("Kartu", "beli"), ("Pinjaman", "investasi"),
                            ("Tabungan", "kemitraan"), ("Investasi", "beli")],
             ["Bangun", "Beli", "Investasi", "Kemitraan"], "light")),
    *box(1, 0, "geo_columns", "Kolom angka di kiri, satu peta + butir per segmen",
         lambda x, y, w, h: S.geo_columns(
             x, y, w, h,
             [("Ticker", "USB"), ("Berdiri", "1863"), ("Kap. pasar", "$82B"),
              ("Cabang", "2.252"), ("ATM", "4.083"), ("Aset", "$567B")],
             [("Regional", "Ritel dan komersial, satu wilayah",
               ["Perbankan pribadi", "Usaha kecil", "Manajemen aset"]),
              ("Nasional", "Korporat dan investasi, seluruh negeri",
               ["Perbankan korporat", "Pasar modal", "Pembayaran"]),
              ("Internasional", "Pembayaran dan jasa investasi",
               ["Kliring", "Kustodi", "Valas"])], "light")),
    *box(0, 1, "node_grid", "Angka utama + dua pita label berisi node bulat",
         lambda x, y, w, h: S.node_grid(
             x, y, w, h, ("$750M", "Pembiayaan berkelanjutan sampai 2030"),
             ["Limbah dan material", "Pangan dan pertanian", "Jasa ekosistem",
              "Pendidikan terjangkau", "Kesehatan terjangkau", "Energi bersih",
              "Transportasi lestari", "Inklusi finansial", "Komunitas", "Air dan sanitasi"],
             ["Pertumbuhan inklusif", "Transisi iklim"], "light")),
    *box(1, 1, "cycle_checklist", "Siklus tiga langkah + daftar cek + chip risiko + angka",
         lambda x, y, w, h: S.cycle_checklist(
             x, y, w, h,
             ["Budaya risiko", "Perbaikan berkelanjutan", "Pengawasan proses"],
             ["Pengambil risiko di garis depan", "Fungsi kontrol independen",
              "Mark-to-market dan uji tekanan", "Insentif risiko yang hati-hati"],
             ["Kredit", "Pasar", "Operasional", "Likuiditas", "Modal", "Reputasi",
              "Kepatuhan", "Iklim", "Model"],
             [("+30%", "ekuitas biasa"), ("+70%", "aset likuid inti"),
              ("-11 pp", "pinjaman tanpa jaminan")], "light")),
], A.FOOT, 12)

# ------------------------------------ 13 diamond + platform rows + stages + columns
A.add("light", "Diamond segmen, baris platform, tahap vs contoh, tiga kolom progres", None, [
    *box(0, 0, "diamond_columns", "Empat segmen di diamond, tiga kolom pendukung",
         lambda x, y, w, h: S.diamond_columns(
             x, y, w, h,
             ["Konsumen dan kekayaan", "Perbankan investasi", "Manajemen aset",
              "Pasar global"],
             [("Akses modal", ["Klien ultra-high", "Klien institusi", "Neraca sendiri"]),
              ("Sumber deal", ["Relasi korporat", "Kemitraan klien", "Jejak global"]),
              ("Modal intelektual", ["Keahlian operasi", "Wawasan pasar", "Strategi keluar"])],
             "light")),
    *box(1, 0, "platform_rows", "Label baris + sel logo + chip metrik",
         lambda x, y, w, h: S.platform_rows(
             x, y, w, h,
             [("Mencocokkan orang dengan pekerjaan", 3,
               ["7.999 pencarian/menit", "364 juta anggota", "24 juta pengunjung"]),
              ("Kerja sesuai permintaan", 3,
               ["12,5 juta pengguna", "1 juta pengemudi", "25 ribu penyedia"]),
              ("Alat kelola talenta", 3, ["", "", ""])], "light")),
    *box(0, 1, "stages_compare", "Baris tahap + praktik terbaik vs contoh per negara",
         lambda x, y, w, h: S.stages_compare(
             x, y, w, h,
             ["Angkutan jalan", "Pelabuhan domestik", "Depot",
              "Perencanaan dan investasi"],
             ["Akses 24/7 dengan batas jalur", "Investasi swasta menaikkan throughput",
              "Jaringan rapat mengikuti jalan", "Kerangka investasi jangka panjang"],
             ["AS: batas jalur, 24/7. Prancis: 44 ton",
              "AS: swasta. Prancis: swasta, diatur negara",
              "Prancis: rapat. AS: bergantung infrastruktur swasta",
              "AS: dana federal. Prancis: kontrak negara"], "light")),
    *box(1, 1, "three_col_progress", "Peluang / aksi / progres, ditutup band hasil",
         lambda x, y, w, h: S.three_col_progress(
             x, y, w, h, ["Peluang", "Aksi yang diambil", "Progres sejauh ini"],
             [["Akuisisi klien", "Ekosistem digital dan pemasaran",
               "Tingkat penangkapan +12 pp"],
              ["Optimasi penjualan", "Model AI dan prioritas prospek",
               "Efisiensi >3x"],
              ["Otomasi pemenuhan", "Alur kerja otomatis",
               "Waktu underwriting -50%"]],
             "Target ROE 15% sepanjang siklus", "light")),
], A.FOOT, 13)


if __name__ == "__main__":
    out = ROOT / "examples" / f"atlas-{A.PALETTE}.pptx"
    A.render_pptx(out)
    html = ROOT / "examples" / f"preview-atlas-{A.PALETTE}.html"
    A.render_html(html)
    print("wrote", out.name, "+", html.name, len(A.SLIDES), "slides")
