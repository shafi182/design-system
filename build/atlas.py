#!/usr/bin/env python3
"""Atlas — one slide per reference layout.

Reset 2026-11-25: the catalogue now follows the nine client references
(SCT 590, ESG 562, investing 588, fortress risk, premier franchise, B2B/B2C
channels, Ford IP 195, BCG 69, luxury 2nd-hand 66, MGI). The earlier 57-shape
catalogue is preserved verbatim in `build/atlas_v0.py` and `build/shapes.py`.

    python build/atlas.py professional
    python build/atlas.py adventurous
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))

import analyst as A  # noqa: E402
import refs as R  # noqa: E402
import shapes as S  # noqa: E402
from analyst import M, W, r, t  # noqa: E402

A.SLIDES.clear()

GRID_TOP, GRID_BOT = 104, 676


def full(name, claim, body, src="refs.py"):
    x, y, w, h = M, GRID_TOP, W - 2 * M, GRID_BOT - GRID_TOP
    out = [r(x, y, w, h, "surface.raised", "light", radius=6, stroke="border.subtle"),
           *S.kicker(x + 14, y + 10, w - 240, name),
           t(x + 14, y + 24, w - 28, 18, claim, "text.primary", "light", size=11, bold=True)]
    if src:
        out.append(t(x + w - 150, y + 10, 136, 10, src, "text.muted", "light", size=6,
                     align="right"))
    out.extend(body)
    return out


def panel(name, claim, body, src="refs.py"):
    return [*full(name, claim, body, src)]


# ---------------------------------------------------------------- 01 SCT
A.add("light", "Model bisnis, model operasi, model modal: tiga lapis yang digeser bersama", None,
      [*panel("twin_pyramid_flow",
              "Keadaan kini dan tujuan akhir memakai kerangka sama; tuas SCT menggeser ketiganya",
              [*R.twin_pyramid_flow(
                  M + 26, GRID_TOP + 62, W - 2 * M - 52, GRID_BOT - GRID_TOP - 84,
                  ("Keadaan kini", [("Model bisnis", "Cara organisasi menciptakan nilai"),
                                    ("Model operasi", "Cara organisasi berjalan"),
                                    ("Model modal", "Cara operasi dibiayai")]),
                  ("Tujuan akhir", [("Model bisnis", "Portofolio selaras strategi"),
                                    ("Model operasi", "Biaya tetap lebih rendah"),
                                    ("Model modal", "Modal dialokasikan ulang")]),
                  "Tuas SCT",
                  [("↑", "Peluang lebih tinggi untuk mewujudkan strategi organisasi"),
                   ("↓", "Sumber daya mengalir lebih baik ke area prioritas strategi"),
                   ("↕", "Fungsi bisnis lebih selaras satu sama lain")])])],
      A.FOOT, 1)

# ---------------------------------------------------------------- 02 ESG
A.add("light", "Kerangka ESG: sembilan komitmen, tiga pemangku kepentingan", None,
      [*panel("matrix_grid",
              "Satu badge tujuan, tiga pilar, tiga penerima manfaat — tiap sel punya target sendiri",
              [*R.matrix_grid(
                  M + 26, GRID_TOP + 62, W - 2 * M - 52, GRID_BOT - GRID_TOP - 84,
                  "Mempercepat pertumbuhan berkelanjutan dan inklusif",
                  ["Lingkungan", "Sosial", "Tata kelola"],
                  ["Pelanggan", "Perusahaan", "Masyarakat"],
                  [[("Net zero 2030", "Jalur 1,5 °C untuk emisi cakupan 1 dan 2"),
                    ("Keuangan inklusif", "Akses produk dasar bagi 10 juta nasabah baru"),
                    ("Transparansi produk", "Label dampak pada produk inti")],
                   [("Operasi rendah karbon", "Efisiensi energi dan armada listrik"),
                    ("Tempat kerja inklusif", "Paritas gender di semua level"),
                    ("Akuntabilitas", "Remunerasi terikat target iklim")],
                   [("Rantai pasok", "Pemasok wajib lulus uji ESG"),
                    ("Kontribusi komunitas", "Program literasi dan kesehatan"),
                    ("Kepatuhan", "Nol pelanggaran sanksi dan AML")]])])],
      A.FOOT, 2)

# ---------------------------------------------------------------- 03 investing
A.add("light", "Kami berinvestasi pada relasi, orang, dan eksekusi — sambil berinovasi", None,
      [*panel("ring_list",
              "Empat program berjalan di bawah satu klien; inovasi menopang semuanya",
              [*R.ring_list(
                  M + 26, GRID_TOP + 62, W - 2 * M - 52, GRID_BOT - GRID_TOP - 84,
                  "Klien", ["Relasi", "Eksekusi", "Orang"],
                  [("Memperluas dan mengoptimalkan cakupan",
                    "AI/ML memperbesar kapasitas; prioritas ditinjau berkala; kolaborasi lintas unit"),
                   ("Mengembangkan produk dan proses",
                    "Solusi terbaik untuk perusahaan privat; penawaran IPO dirancang ulang"),
                   ("Merekrut dan mempertahankan talenta terbaik",
                    "Teknologi memperbesar tenaga kerja masa depan; bankir diberi ruang"),
                   ("Berinvestasi pada teknologi dan analitik",
                    "Wawasan berbasis data; model operasi lebih efisien; titik gesek alur kerja")])])],
      A.FOOT, 3)

# ---------------------------------------------------------------- 04 fortress risk
A.add("light", "Manajemen risiko dan kontrol: lima tanggung jawab, tidak bisa ditawar", None,
      [*panel("ring_stats",
              "Tanggung jawab di kiri, tim pelaksana di tengah, bukti skala di kanan",
              [*R.ring_stats(
                  M + 26, GRID_TOP + 62, W - 2 * M - 52, GRID_BOT - GRID_TOP - 84,
                  ["Ketahanan dan keamanan operasi",
                   "Menjalankan sanksi lintas yurisdiksi",
                   "Melindungi aset, dana, dan data klien",
                   "Menurunkan risiko fraud dan siber",
                   "Menjalankan kewajiban KYC/AML"],
                  "±20.000 profesional",
                  ["Kepatuhan", "Fraud", "Risiko", "KYC & AML", "Keuangan", "Hukum", "Siber",
                   "Kontrol"],
                  [("$30 M+", "Pembiayaan bersama 1,1 triliun dolar pinjaman, melayani 400.000+ klien"),
                   ("2,5 jt", "Rekening klien menerima penundaan pembayaran dan pembebasan biaya"),
                   ("$70 M", "Keringanan pokok dan bunga atas 2 juta+ rekening"),
                   ("$2,2 T", "Kredit dan modal dihimpun untuk klien wholesale dan ritel")],
                  "Kami adalah bagian dari sistem keuangan yang aman dan sehat")])],
      A.FOOT, 4)

# ---------------------------------------------------------------- 05 premier franchise
A.add("light", "Franchise premier menaikkan pangsa dompet dan pertumbuhan", None,
      [*panel("ring_list",
              "Satu klien, empat mesin bisnis, dua bukti pangsa, empat metrik inisiatif",
              [*R.ring_list(
                  M + 26, GRID_TOP + 62, W - 2 * M - 52, GRID_BOT - GRID_TOP - 84,
                  "Klien", ["Manajemen aset", "Perbankan investasi", "Pasar global", "Kekayaan"],
                  [],
                  boxes=[("Pertumbuhan pangsa 2020–2022",
                          [("IB", "+360 bps"), ("GM", "+250 bps")]),
                         ("Metrik inisiatif kunci",
                          [("Alternatif", "$100 M+ pembiayaan"),
                           ("Kekayaan", "475 perusahaan dilayani"),
                           ("Transaksi", ">90% klien eksisting"),
                           ("Ritel", "8 program kemitraan")])])])],
      A.FOOT, 5)

# ---------------------------------------------------------------- 06 channels
A.add("light", "Saluran penjualan baru tumbuh di sekitar suara, gim, dan interaksi jarak jauh", None,
      [*panel("channel_columns",
              "Tiap saluran punya profil pembeli, bukti tarikan, dan satu syarat masuk",
              [*R.channel_columns(
                  M + 26, GRID_TOP + 62, W - 2 * M - 52, GRID_BOT - GRID_TOP - 84,
                  [("B2C", "Suara", "Potensi kuat",
                    [("1,2 miliar", "Perangkat ber-AI terpasang pada 2020"),
                     ("34% CAGR", "Pertumbuhan asisten suara lima tahun")],
                    "Menang di pencarian jawaban, bukan tautan"),
                   ("B2C", "Gim", "Momentum naik",
                    [("+29%", "Pertumbuhan belanja iklan dalam gim"),
                     ("86%", "Pemain membeli barang virtual")],
                    "Iklan harus terasa seperti bagian permainan"),
                   ("B2B", "Jarak jauh / hibrida", "Akan bertahan",
                    [("2–3×", "Rasio panggilan penjualan via konferensi"),
                     ("60%+", "Kenaikan penjualan pada model hibrida")],
                    "Ruang rapat jadi ruang penjualan utama")],
                  "Pengalaman lintas saluran yang mulus makin menentukan pilihan pembeli")])],
      A.FOOT, 6)

# ---------------------------------------------------------------- 07 Ford IP
A.add("light", "Kekayaan intelektual satu industri menyuburkan industri lain", None,
      [*panel("example_grid",
              "Sitasi lintas industri menunjukkan transfer pengetahuan yang sudah terjadi",
              [*R.example_grid(
                  M + 26, GRID_TOP + 62, W - 2 * M - 52, GRID_BOT - GRID_TOP - 84,
                  "Paten perusahaan otomotif dikutip dari pertanian sampai biofarmasi.",
                  "±23.000",
                  "Sitasi lintas industri, 2013–2017. Sumber: BCG.",
                  [("Pemantauan pesawat", "Data operasi memberi pandangan kesehatan aset"),
                   ("Robot bedah", "Kontrol sistem dengan bantuan tingkat keyakinan"),
                   ("Alat olahraga", "Jalur virtual dengan simulasi video dan medan"),
                   ("Teknologi penglihatan", "ML membaca bahasa tubuh untuk interaksi"),
                   ("Perangkat medis", "Stimulasi saraf yang dapat diprogram"),
                   ("Farmasi", "Pelepasan larutan obat terkendali"),
                   ("Teknologi audio", "Pencarian suara dan pesan pada earbud"),
                   ("Otomasi rumah", "Deteksi dan mitigasi gas berbahaya")])])],
      A.FOOT, 7)

# ---------------------------------------------------------------- 08 BCG adoption
A.add("light", "Pengguna pertama mendorong adopsi digital, lalu kebiasaan mengeras", None,
      [*panel("split_stats_story",
              "Tiga angka adopsi di kiri, satu preseden sejarah di kanan",
              [*R.split_stats_story(
                  M + 26, GRID_TOP + 62, W - 2 * M - 52, GRID_BOT - GRID_TOP - 84,
                  [("50%", "Pengguna pasar berkembang melaporkan belanja ritel daring naik"),
                   ("51%", "Pemakaian dompet digital meningkat dibanding sebelum pandemi"),
                   ("52%", "Langganan streaming bertambah pada periode yang sama")],
                  "Preseden: SARS dan e-commerce Tiongkok",
                  [("Titik balik", "SARS dianggap momen internet menjadi media massa"),
                   ("Kanal terpaksa", "Perjalanan bisnis terhenti, B2B Alibaba pindah daring"),
                   ("Ledakan", "4.000 anggota baru dan 9.000 listing per hari, 3–5× lipat")])])],
      A.FOOT, 8)

# ---------------------------------------------------------------- 09 2nd-hand luxury
A.add("light", "Barang bekas bersertifikat: alat pemasaran bagi merek, sumber laba bagi peritel", None,
      [*panel("two_group_bullets",
              "Manfaatnya berbeda tergantung siapa yang menjalankan",
              [*R.two_group_bullets(
                  M + 26, GRID_TOP + 62, W - 2 * M - 52, GRID_BOT - GRID_TOP - 84,
                  ("Mengapa barang bekas bersertifikat relevan bagi pemain mewah?",
                   "Sumber: BCG"),
                  [("Terutama untuk merek",
                    [("Alat pemasaran", "Memahami konsumen dari data sirkulasi ulang"),
                     ("Kanal rekrut", "Menjangkau konsumen baru dan advokat merek")]),
                   ("Terutama untuk peritel",
                    [("Kendali reputasi", "Memantau dan meredam risiko reputasi merek"),
                     ("Sumber laba", "Lini bisnis baru dengan margin sehat")])])])],
      A.FOOT, 9)

# ---------------------------------------------------------------- 10 MGI
A.add("light", "Tujuh agenda riset, satu pertanyaan: pertumbuhan yang inklusif", None,
      [*panel("orbit_stats",
              "Skala institusi di atas, tujuh tema riset mengelilingi satu misi",
              [*R.orbit_stats(
                  M + 26, GRID_TOP + 62, W - 2 * M - 52, GRID_BOT - GRID_TOP - 84,
                  [("31", "Tahun usia lembaga"), ("300+", "Publikasi terbit"),
                   ("#1", "Think tank sektor privat, empat tahun")],
                  "Mempercepat pertumbuhan berkelanjutan dan inklusif",
                  [(1, "Pertumbuhan dan kompetisi", "Dinamika industri, produktivitas, daya saing"),
                   (2, "Pasar keuangan dan investasi", "Alokasi modal, stabilitas, inklusi"),
                   (3, "Perilaku konsumen", "Belanja, kesehatan, preferensi yang bergeser"),
                   (4, "Masyarakat dan institusi", "Tata kelola, demografi, kepercayaan"),
                   (5, "Sumber daya dan keberlanjutan", "Energi, material, transisi iklim"),
                   (6, "Pekerjaan dan pasar kerja", "Keterampilan, mobilitas, otomasi"),
                   (7, "Teknologi dan inovasi", "AI, komputasi, difusi teknologi")])])],
      A.FOOT, 10)


if __name__ == "__main__":
    out = ROOT / "examples" / f"atlas-{A.PALETTE}.pptx"
    A.render_pptx(out)
    html = ROOT / "examples" / f"preview-atlas-{A.PALETTE}.html"
    A.render_html(html)
    print("wrote", out.name, "+", html.name, len(A.SLIDES), "slides")
