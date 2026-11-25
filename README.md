# Signal v0.7 — deck system, dua palet

Satu sumber kebenaran untuk **deck, dokumen, web, dan app**.
Dua bahasa digabung: disiplin deck pitch (satu ide per slide, display besar) dan bahasa
infografik (garis hairline, label small-caps, modul bernomor, blok statistik).

```
tokens/
  core/        color · type · space · misc (+ layout slide)      <- primitif
  semantic/    professional.{light,dark} · adventurous.{light,dark}
  component/   button · card · table · slide
build/
  build.py     resolver alias + generator (css/tailwind/ts/json/office/docs)
  deck.py      spec slide 1280x720 -> pptx (rect · text · chart · image)
  preview.py   spec yang sama -> HTML (chart jadi SVG, foto file yang sama)
  photos.py    placeholder foto, dua tone (cool / warm)
  examples.py  laporan contoh
dist/          hasil generate, jangan diedit manual
examples/      pitch-deck-professional.pptx · pitch-deck-adventurous.pptx · preview-*.html
```

## Pakai

```bash
python3 build/build.py               # generate dist/ (semua palet)
python3 build/build.py --check       # validasi alias + kontras WCAG (4 kombinasi)
python3 build/photos.py              # placeholder foto
python3 build/deck.py professional   # examples/pitch-deck-professional.pptx
python3 build/deck.py adventurous    # examples/pitch-deck-adventurous.pptx
python3 build/preview.py adventurous # examples/preview-adventurous.html
```

Di web/app, palet dipilih lewat atribut, bukan file berbeda:

```html
<html data-palette="adventurous" data-theme="dark">
```

`dist/css/tokens.css` memuat palet default di `:root`; `tokens-adventurous.css` memuat
`[data-palette="adventurous"]` plus varian dark-nya. Tailwind: `preset.js` dan
`preset-adventurous.js`. Office: `theme-scheme.xml` dan `theme-scheme-adventurous.xml`.

## Dua palet

**Professional · Sophisticated · Intellectual** — lima warna saja, tanpa oranye. Aksen = teal.

- Deep Navy `#142C36` — kanvas gelap, teks utama di terang (11.55:1)
- Deep Teal `#24545A` — aksen tunggal: brand, tautan, panel terpilih, teks sekunder (6.69:1)
- Muted Sage `#527C78` — aksen di kanvas gelap (`brand.primary` = sage.300), fokus
- Soft Olive `#B6B9A5` — hairline, teks sekunder di navy (7.26:1), seri kedua chart
- Warm Ivory `#E9E5D9` — kanvas terang

Tidak ada oranye di palet ini — `brand.primary` = teal.700 di terang, sage.300 di gelap.
Chart dua seri pakai teal (aktual) versus olive (rencana), jadi bedanya value, bukan hue.
Semantic profesional hanya mereferensikan lima warna itu; oranye tetap ada di `tokens/core`
sebagai bahan palet adventurous, bukan bagian brand ini.

**Adventurous · Creative · Approachable** — kanvas krem, charcoal sebagai tinta, oranye sebagai brand.

- Cream `#FAF3E1` — kanvas terang
- Sand `#F5E7C6` — surface naik, border halus
- Vibrant Orange `#FF6D1F` — brand, aksen, panel harga
- Charcoal `#222222` — tinta utama (14.37:1 di krem) dan kanvas gelap

Aturan keras yang berlaku di kedua palet:

1. **Teks di atas oranye selalu charcoal.** Putih di `#FF6D1F` hanya 3.13:1 — gagal WCAG.
2. **Link di kanvas terang pakai orange.800 `#A8430B`**, bukan orange.500.
3. **Status di kanvas charcoal pakai stop 300** (green/amber/red) — stop 500 terlalu gelap.

## Tipografi

Satu keluarga untuk semua peran: **Manrope** (display, body, label, angka).
Bobot 400–800; display 42–62px tracking −0.03em; body 13–18px leading 1.45–1.65.

Slot `type.family.mono` tetap ada tapi sudah alias ke Manrope — angka pakai
`font-variant-numeric: tabular-nums` supaya kolom tetap rata. Kalau nanti butuh mono
sungguhan (kode, ID), ubah satu token itu saja.

## Layout & radius

`layout.slide-width 1280` · `slide-height 720` · `margin-x 72`. Koordinat di `build/deck.py`
memakai piksel slide; pptx mengonversi 1px = 9525 EMU, jadi preview HTML dan PowerPoint identik.

`surface.band` (band callout) adalah token semantik, bukan warna tetap: olive.100 di professional,
sand.500 di adventurous. Ganti palet, band ikut.

Radius: `sm` 6 · `md` 12 · `lg` 18 (kartu, panel, callout) · `xl` 28 (foto) · `pill` 999.
Hairline dan rule tetap 0 — yang membulat hanya permukaan. Tanpa shadow: pemisahan dari beda
tone dan satu outline 1px (`border.strong`) di kartu netral.

## Modul

- **KPI card** — angka besar, label, delta; surface `radius.lg`.
- **Chart** — bar berkategori dan line dua seri. Di pptx chart native (bisa diedit di
  PowerPoint); di preview digambar SVG dari angka yang sama.
- **Pricing** — dua panel: netral (outline) dan penuh oranye dengan teks charcoal.
- **Budget** — tabel tiga baris label/nilai/delta, dipisah hairline.
- **Contact** — dua kolom label + value, plus baris langkah berikutnya.
- **Photo slot** — rasio tetap `photo-cover.png` (780×1080) dan `photo-43.png` (1024×768),
  dengan varian `-adventurous` bertone hangat. Foto asli menimpa file itu; dipotong membulat
  sekali saat build ke `examples/photos/rounded/`, jadi koordinat slide tidak pernah bergeser.

Foto **tidak pernah** menutupi teks: slot selalu di sisi kanan atau panel terpisah, teks tetap
di kolom kiri. Placeholder diberi label `PHOTO` supaya kelihatan belum diisi.

## Aturan

1. **Semantic wajib alias.** Hex langsung mematikan theming dan dark mode.
2. **Komponen tidak menyentuh core.** Butuh oranye? `brand.primary`.
3. **Rename token = breaking change.** Naikkan major version.
4. **Token baru hanya kalau dipakai ≥2 komponen.**
5. **`dist/` tidak pernah diedit tangan.**
6. **Sudut membulat, bukan kotak.** Permukaan pakai `radius.lg` (18) atau `radius.xl` (28); garis tetap 0.
7. **Kontras dijaga CI** — `build.py --check` memeriksa keempat kombinasi palet × mode.

## Versioning

- `v0.7.0` — professional dikunci ke lima warna (tanpa oranye), band callout ikut palet lewat `surface.band`.
- `v0.6.0` — dua palet (professional / adventurous), font tunggal Manrope, generator multi-palet.
- `v0.5.0` — sudut membulat: kartu 18px, foto 28px, outline 1px untuk kartu netral.
- `v0.4.0` — modul Style 1 (KPI card, chart, pricing, budget, contact) + slot foto. Deck 9 slide.
- `v0.3.0` — palet navy/ivory/orange, Manrope, bahasa infografik Style 2.
- `v0.2.0` — Signal pitch: ink/bone/orange, Space Grotesk.
- `v0.1.0` — Corporate Calm: navy/sand, Source Serif 4.
