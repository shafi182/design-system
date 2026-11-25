# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.1.0/).
Versi mengikuti [SemVer](https://semver.org/lang/id/): rename token = major, tambah modul = minor,
perbaikan visual/kontras = patch.

## [0.14.0] — 2026-11-25

### Atlas diperluas ke dua puluh layout referensi

Sepuluh referensi gelombang kedua ditranskrip menjadi slide 11–20. Palet tidak
disentuh sama sekali — hanya bentuk, komposisi, dan tipografi.

- Shape baru di `build/refs.py`: `stat_octet` (8 metrik 4×2, McKinsey 32),
  `stat_trio` (3 panel; varian bertumpuk saat panel ketiga membawa seri),
  `hbar_paired` (Gen AI vs potensi otomasi, MGI 255), `steps_ranked` (prioritas CHRO),
  `waterfall_rows` (1,7 juta pekerjaan otomotif, BCG 253),
  `hbar_split` (Fortune 500 keluar Rusia), `attribution_bars` (TSR M&A, 276),
  `strategy_trio` (arah strategi, 170), `waterfall_bridge` (jalur emisi 2023–2030, 275),
  `hex_framework` ($750 Bn keuangan berkelanjutan, Goldman 194).
- `build/atlas.py` kini 20 slide; slide 1–10 tidak diubah.
- Perbaikan hasil audit: lebar bar dijaga `max(1, …)` agar tidak ada
  `ZeroDivisionError` pada nilai nol; skala waterfall memakai total sebagai
  batas; label industri di `hbar_split` diberi gutter; bar awal
  `waterfall_bridge` digambar dari garis dasar ke atas, bukan ke bawah.
- Legenda, tick sumbu, dan nilai kedua seri ditambahkan agar tiap diagram
  bisa dibaca tanpa teks pendamping.

## [0.13.0] — 2026-11-25

### Reset bentuk: atlas mengikuti sepuluh referensi

Bukan penambahan shape — katalog atlas diganti total. Sepuluh layout klien
ditranskrip ulang, satu slide per layout. 57 shape lama tetap ada di
`build/shapes.py` dan atlas lamanya diarsipkan di `build/atlas_v0.py`.

- `build/refs.py` baru — `twin_pyramid_flow` (SCT 590), `matrix_grid` (ESG 562),
  `ring_list` (588 + premier franchise), `ring_stats` (fortress risk),
  `channel_columns` (B2B/B2C), `example_grid` (Ford IP 195), `split_stats_story` (BCG 69),
  `two_group_bullets` (2nd-hand 66), `orbit_stats` (MGI).
- `build/atlas.py` ditulis ulang: 10 slide, satu shape per slide, panel penuh.
- Palet tidak disentuh — token, semantic, dan `--check` sama persis.

### Perbaikan dari audit

- `ring_list`: label segmen kini duduk di 1,05r dengan kotak 0,96r; tidak lagi
  menabrak hub maupun label tetangga (tumpang 13 × 47 px hilang).
- `ring_stats`: radius cincin dibatasi 0,25 lebar / 0,235 tinggi; simpul bawah
  tidak lagi menyentuh band merah.
- `orbit_stats`: pusat digeser ke 0,235 lebar, radius 0,165 lebar / 0,215 tinggi;
  label simpul tidak lagi menabrak kolom statistik kanan.
- `channel_columns`: tinggi blok statistik dikurangi 26 px supaya baris penutup
  tidak bertumpang dengan catatan terakhir.

## [0.12.0] — 2026-11-25

### Bentuk gelombang keenam (56 → 57)

- `orbit_compare` — dua orbit berdampingan dengan cincin simpul identik, pusat berbeda (peran kecil + kata utama), tiga catatan per sisi, banner opsional di atas. Untuk perbandingan model: produsen vs interaksi.

Atlas 16 → 17 slide, panel penuh selebar kanvas.

### Perbaikan

- `orbit_compare`: label peran di hub tadinya menabrak kata utama (tumpang 4,6 px) — kotak hub dinaikkan ke 1,24r, peran 0,42r di atas, kata utama 0,46r di bawah. Orbit 2,35r → 2,45r untuk jarak simpul ke hub.
- Peran hub tidak lagi pakai caps 5,6 px (huruf S terbaca seperti 5); kini 6,2 px normal case.
- Footer analyst, kicker `dist/`, dan `package.json` naik ke v0.12.

## [0.11.0] — 2026-11-25

### Bentuk gelombang kelima (52 → 56)

- `loop_columns` — loop tertutup empat simpul + hub merek di kiri, poin nilai bernomor di tengah, checklist infrastruktur di kanan (wholesale payments).
- `shift_columns` — kolom sekarang / nanti / hasil dengan garis atas aksen pada kolom target (corporate bank roadmap).
- `percent_columns` — lima kolom persen besar + judul caps + catatan, pita penutup penuh di kaki (customer expectations).
- `opportunity_track` — angka peluang | checklist proposisi nilai | blok progres bertag (transaction banking).

Atlas 15 → 16 slide. Slide 16 keempat bentuk di atas.

### Perbaikan

- `loop_columns`: orbit 1,95r → 2,55r, radius simpul 0,19 → 0,13, lebar kotak 2,5r → 2,1r; kotak kiri/kanan tidak lagi menabrak hub tengah.
- Footer analyst, kicker `dist/`, dan `package.json` naik ke v0.11.

## [0.10.0] — 2026-11-25

### Bentuk gelombang keempat (44 → 52)

Delapan bentuk baru dari referensi wealth spectrum, cost levers, McKinsey AI, CHRO priorities, BCG automotive, Yale/McKinsey Russia exits, M&A TSR, dan pilar People/Profit/Planet:

- `wealth_bands` — pita klien bertumpuk: nama + catatan aset, dua ukuran pasar, badge pangsa, sumbu layanan advisor→digital.
- `levers_rows` — baris tuas bernomor + aksi di kiri, alasan di kolom kanan.
- `paired_bars` — batang horizontal berpasangan dikelompokkan per tema, legenda dua seri.
- `meter_grid` — angka persen besar + meter trek + catatan, grid tiga kolom.
- `grouped_hbar` — batang horizontal berkelompok dengan nilai di ujung dan baris total.
- `diverging_bars` — batang dua arah dari poros tengah: keluar vs tetap.
- `driver_bars` — dekomposisi driver di atas dan di bawah garis dasar, kolom total di kanan.
- `pillar_targets` — pilar: header berwarna, butir, pil target di kaki.

Atlas 13 → 15 slide. Slide 14 pita segmen / tuas / batang berpasangan / meter; slide 15 batang berkelompok / bercabang / driver / pilar.

### Perbaikan

- `driver_bars`: area plot disisakan 18 px untuk nama kategori; tinggi batang dihitung dari area plot sehingga label tidak menyentuh tepi kartu.
- Footer analyst, kicker `dist/`, dan `package.json` naik ke v0.10.

## [0.9.0] — 2026-11-25

### Added
- **`build/shapes.py`** — 44 bentuk siap pakai yang hanya memakai token (tidak ada hex):
  blok angka (`kpi_strip`, `kpi_grid`, `stat_cards`, `stat_row`), teks
  (`headline`, `body_text`, `bullets`, `ticks`, `quote_block`, `banner`),
  tabel (`compare_table` dua periode + kolom delta, `delta_rows`, `icon_grid`, `list_rows`,
  `agenda`), grafik (`chart` batang/garis, `waterfall`, `donut_row`),
  diagram (`pyramid`, `twin_pyramid`, `band_stack`, `pillar_framework`, `concentric`,
  `ring_blocks`, `team_circle`, `flow_chain`, `journey_lane`, `branch`, `before_after`),
  peta (`map_bubbles`, `map_regions`).
- Bentuk gelombang kedua, dari referensi deck konsultan: `matrix_header` (pil pernyataan +
  kolom pilar x baris pemangku), `benefit_panel` (daftar manfaat + panel kasus pakai),
  `country_cards` (kartu negara, delta bertanda), `ranked_barriers` (angka utama + peringkat
  tersorot), `orbit_ring` (7 topik mengorbit satu pernyataan), `segment_split` (bar
  proporsional ternormalisasi), `twin_hub` (peran sebelum/sesudah), `quad_actions` (4 aksi
  2x2).
- Bentuk gelombang ketiga, dari referensi perbankan dan industri: `channel_arch` (saluran
  akuisisi di atas, merek di tengah, produk + chip strategi + legenda), `geo_columns`
  (kolom angka + satu blok peta + butir per segmen), `node_grid` (angka utama + dua pita
  label berisi node bulat), `cycle_checklist` (siklus bernomor + daftar cek + chip risiko +
  angka kaki), `diamond_columns` (empat segmen di diamond, tiga kolom pendukung),
  `platform_rows` (label baris + sel logo + chip metrik), `stages_compare` (baris tahap +
  praktik terbaik vs contoh per negara), `three_col_progress` (peluang/aksi/progres ditutup
  band hasil).
- **`build/atlas.py`** — deck katalog 13 slide, satu keluarga bentuk per slide, setiap panel
  diberi nama fungsi + aturan pakai. `examples/atlas-<palette>.pptx` dan
  `examples/preview-atlas-<palette>.html`.
- `compare_table` menerima baris 3- atau 4-tuple `(nama, sebelum, sesudah[, delta])`;
  baris yang disorot memakai band `brand.subtle`.

### Changed
- `label`, `headline`, `kicker` mengembalikan **list** primitif, bukan dict, supaya bisa
  displat (`*S.kicker(...)`) saat menyusun panel.
- Bentuk yang menerima `h` sekarang benar-benar memakai tinggi panel penuh
  (`compare_table`, `delta_rows`, `list_rows` menambah hairline antar baris;
  `flow_chain` 88% tinggi; `branch` menyebar 0,24–0,76; chip `radial` ikut tinggi baris).
- Footer analyst dan kicker `dist/` naik ke v0.9.

### Not changed
- Palet. Nol warna baru, nol hex baru. `build.py --check` lulus di keempat kombinasi
  palet × mode.

## [0.8.0] — 2026-11-25

### Added
- **Lapisan visual `analyst`** — tata letak consulting padat, dirender dari token yang sama:
  grid panel 2×3 dengan gutter 14px, tab bar 5 item (Table / Chart / Panel / Framework / Visual),
  margin 32px, radius panel 6px, judul per panel + baris sumber per panel.
- Primitif baru di `build/analyst.py`: `hbar`, `hstack`, `donut`, `pyramid`, `hub`, `flow`,
  `stackbar`, `matrix`, `tbl` (header caps + hairline, tanpa zebra, angka rata kanan),
  `radial` (hub + 5–6 satelit), `layers_matrix` (matriks lapis × pilar), `kpi_grid`
  (angka + hairline pemisah), `ticks` (checklist).
- Token `chart.series.1…4` di keempat tema — tangga seri per palet, bukan warna baru.
- `tokens/component/analyst.tokens.json` — `analyst.layout.*` dan `analyst.type.*` (9,5px body, 8px mikro).
- `examples/analyst-<palette>.pptx` + `examples/preview-analyst-<palette>.html` (5 slide per palet).

### Changed
- Tab aktif memakai `brand.primary` dengan `text.on-brand`; tab pasif `surface.raised` + `border.subtle`.
- Chart consulting memakai label langsung di ujung bar dan sumbu nilai yang disembunyikan.

### Unchanged
- **Palet tidak disentuh.** Professional tetap lima warna, adventurous tetap cream/sand/orange/charcoal;
  semua kombinasi masih lulus gate kontras `build.py --check`.

## [0.7.0] — 2026-11-25

### Changed
- **Professional dikunci ke lima warna brand**: Deep Navy `#142C36`, Deep Teal `#24545A`,
  Muted Sage `#527C78`, Soft Olive `#B6B9A5`, Warm Ivory `#E9E5D9`. Oranye dihapus dari palet ini.
- `brand.primary` professional = teal.700 (terang) / sage.300 (gelap). Panel terpilih jadi teal.
- `slide.callout-bg` tidak lagi hard-code sand; sekarang alias ke token baru `surface.band`
  (olive.100 di professional, sand.500 di adventurous).
- Placeholder foto professional tidak lagi memakai garis oranye.

### Added
- `surface.band` — warna band callout per palet.
- `brand.accent-text` — aksen yang aman sebagai teks kecil (orange.800 di terang, orange.300/200 di gelap).
- Stop warna `charcoal.600`, `charcoal.950`, `orange.200`, `green/amber/red.300` untuk kanvas gelap.

## [0.6.0] — 2026-11-25

### Added
- Dua palet dalam satu sistem: `professional` dan `adventurous`, masing-masing terang + gelap.
- Generator multi-palet: `tokens.css` / `tokens-adventurous.css`, `preset*.js`, `tokens*.ts`,
  `theme-scheme*.xml`, `index*.html`.

### Changed
- Font tunggal **Manrope** untuk display, body, label, dan angka. Slot `type.family.mono` tetap ada
  tapi dialias ke Manrope; angka pakai `font-variant-numeric: tabular-nums`.
- Deck dirender per palet: `python3 build/deck.py <palette>`.

## [0.5.0] — 2026-11-25

### Changed
- Sudut membulat: `radius.lg` 18px (kartu, panel, callout), `radius.xl` 28px (foto).
  Hairline dan rule tetap 0.
- Kartu netral memakai outline 1px `border.strong`, tanpa shadow.

### Added
- `rounded_photo()` — foto dipotong membulat sekali saat build ke `examples/photos/rounded/`.

## [0.4.0] — 2026-11-25

### Added
- Modul dari Style 1: KPI card, chart bar/line, pricing, budget, contact.
- Slot foto dua rasio tetap (`photo-cover.png` 780×1080, `photo-43.png` 1024×768).
- `build/photos.py` untuk placeholder.

### Changed
- Deck naik dari 6 ke 9 slide.

## [0.3.0] — 2026-11-25

### Added
- Palet navy/ivory/orange, Manrope display, bahasa infografik (kicker + rule, band callout,
  kolom bernomor, stat stack, bar comparison).

## [0.2.0] — 2026-11-25

### Changed
- Arah desain diganti ke bahasa pitch deck: ink/bone/orange, Space Grotesk, display 76px, radius 2–4px.

### Added
- `build/deck.py` (spec → pptx) dan `build/preview.py` (spec sama → HTML).

## [0.1.0] — 2026-11-25

### Added
- Rilis pertama: DTCG tokens (core / semantic / component), resolver alias tanpa dependensi,
  emitter CSS, Tailwind, TypeScript, JSON, Office theme, docs, dan pemeriksaan kontras WCAG.
