# Signal v0.4 — deck system (navy · ivory · orange)

Satu sumber kebenaran untuk **deck, dokumen, web, dan app**.
Dua bahasa digabung: disiplin deck pitch (satu ide per slide, display besar, angka mono) dan bahasa
infografik (garis hairline, label small-caps, modul bernomor, blok statistik).

```
tokens/
  core/        color · type · space · misc (+ layout slide)   <- primitif
  semantic/    light (kanvas ivory) · dark (kanvas navy)      <- alias, dipakai komponen
  component/   button · card · table · slide
build/
  build.py     resolver alias + generator (css/tailwind/ts/json/office/docs)
  deck.py      spec slide 1280x720 -> pptx (rect · text · chart · image)
  preview.py   spec yang sama -> HTML (chart jadi SVG, foto file yang sama)
  photos.py    placeholder foto (ganti PNG-nya, layout tidak bergeser)
  examples.py  laporan contoh
dist/          hasil generate, jangan diedit manual
examples/      pitch-deck.pptx · sample-report.docx · preview.html
```

## Pakai

```bash
python3 build/build.py          # generate dist/
python3 build/build.py --check  # validasi alias + kontras WCAG (terang & gelap)
python3 build/photos.py         # placeholder foto (sekali saja)
python3 build/deck.py           # examples/pitch-deck.pptx
python3 build/preview.py        # examples/preview.html
```

## Palet

Dua kelompok, satu sistem:

**Profesional · Sophisticated · Intellectual**
- Deep Navy `#142C36` — kanvas gelap + teks utama di kanvas terang (11.55:1)
- Deep Teal `#24545A` — teks sekunder di kanvas terang (6.69:1)
- Muted Sage `#527C78` — garis, chart, blok; **bukan** teks kecil (3.69:1)
- Soft Olive `#B6B9A5` — teks sekunder di navy (7.26:1), hairline di terang
- Warm Ivory `#E9E5D9` — kanvas terang

**Adventurous · Creative · Approachable**
- Cream `#FAF3E1` — panel dan kartu
- Sand `#F5E7C6` — band callout
- Vibrant Orange `#FF6D1F` — aksen tunggal, maksimal satu per slide
- Charcoal `#222222` — teks isi di cream, dan teks di atas oranye (5.65:1)

Aturan keras: **teks di atas oranye selalu charcoal**. Putih di atas `#FF6D1F` hanya 3.13:1 — gagal WCAG
dan itu kesalahan paling umum di deck "berani". Link di kanvas terang pakai orange.800 `#A8430B` (4.80:1);
orange.700 cuma 3.64:1.

## Tipografi

- **Display** — Manrope 68/44px, tracking −0.03em, leading 1.06
- **Body** — Inter 13–18px, leading 1.45–1.65
- **Mono** — IBM Plex Mono untuk angka statistik, kicker, footer, nomor halaman

Manrope diambil dari Style 2: grotesk humanis, lebih hangat dari Space Grotesk tapi tetap presisi di 68px.

## Layout slide

`layout.slide-width 1280` · `slide-height 720` · `margin-x 72`. Koordinat di `build/deck.py` memakai piksel
slide; pptx mengonversi 1px = 9525 EMU, jadi preview HTML dan file PowerPoint identik.

## Aturan

1. **Semantic wajib alias.** Hex langsung mematikan theming dan dark mode.
2. **Komponen tidak menyentuh core.** Butuh oranye? `brand.primary`.
3. **Rename token = breaking change.** Naikkan major version.
4. **Token baru hanya kalau dipakai ≥2 komponen.**
5. **`dist/` tidak pernah diedit tangan.**
6. **Kontras dijaga CI** — `build.py --check` memeriksa tema terang dan gelap.

## Modul (v0.4)

Diambil dari Style 1/2, tapi ditulis ulang dengan body 13–18px — bukan 6.4pt:

- **KPI card** — angka mono 46px, label 13px, delta kecil; border atas oranye 2px.
- **Chart** — bar berkategori dan line dua seri. Di pptx ini chart native (bisa diedit di
  PowerPoint); di preview digambar SVG dari angka yang sama.
- **Pricing** — dua panel: netral (ivory + hairline) dan penuh oranye dengan teks charcoal.
- **Budget** — tiga baris label/angka/delta, dipisah hairline; baris terakhir pakai aksen.
- **Contact** — 2 kolom label mono + value, garis tipis di atas.
- **Photo slot** — dua rasio tetap: `photo-cover.png` (780×1080, panel kanan cover) dan
  `photo-43.png` (1024×768). Foto asli menimpa file itu; koordinat slide tidak berubah.

Foto **tidak pernah** menutupi teks: slot selalu di sisi kanan atau panel terpisah, teks tetap
di kolom kiri. Placeholder sengaja diberi label `PHOTO` supaya kelihatan belum diisi.

## Versioning

- `v0.4.0` — modul Style 1 (KPI card, chart bar/line, pricing, budget, contact) + slot foto. Deck 9 slide.
- `v0.3.0` — palet navy/ivory/orange, Manrope, bahasa infografik Style 2. Deck 6 slide tanpa slot foto.
- `v0.2.0` — Signal pitch: ink/bone/orange, Space Grotesk.
- `v0.1.0` — Corporate Calm: navy/sand, Source Serif 4.
