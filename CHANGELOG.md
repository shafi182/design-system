# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.1.0/).
Versi mengikuti [SemVer](https://semver.org/lang/id/): rename token = major, tambah modul = minor,
perbaikan visual/kontras = patch.

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
