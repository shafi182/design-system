# Signal — pitch deck system

Satu sumber kebenaran untuk **deck pitch, dokumen, web, dan app**.
Nilai mentah hanya hidup di lapis *core*; semua yang dipakai sehari-hari merujuk lewat token *semantic*.

```
tokens/
  core/        color · type · space · misc (+ layout slide)   <- primitif
  semantic/    light (slide terang) · dark (slide gelap)      <- alias, INI yang dipakai komponen
  component/   button · card · table · slide                  <- hanya kalau semantic kurang spesifik
build/
  build.py     resolver alias + generator (css/tailwind/ts/json/office/docs)
  deck.py      spec slide 1280x720 -> pptx
  preview.py   spec yang sama -> HTML, untuk lihat tanpa PowerPoint
  examples.py  cover + laporan contoh
dist/          hasil generate, jangan diedit manual
examples/      pitch-deck.pptx · sample-report.docx · preview.html
```

## Pakai

```bash
python3 build/build.py          # generate dist/
python3 build/build.py --check  # validasi alias + kontras WCAG, exit 1 kalau gagal
python3 build/deck.py           # examples/pitch-deck.pptx
python3 build/preview.py        # examples/preview.html
```

## Kenapa gaya ini

Deck pitch dinilai dalam hitungan detik, bukan dibaca seperti laporan. Yang membuatnya bekerja:

- **Satu ide per slide.** Display 76px memaksa satu kalimat. Kalau tidak muat, idenya masih dua.
- **Kanvas bergantian.** Cover dan traction gelap (`#08090B`), isi terang (`#F6F4EE`). Ritme gelap–terang–gelap menjaga perhatian tanpa animasi.
- **Satu aksen.** Oranye `#FF5A1F` hanya untuk angka yang ingin diingat dan kicker. Kalau oranye ada di semua tempat, tidak ada yang menonjol.
- **Teks di atas oranye = hitam, bukan putih.** Hitam 6.39:1; putih cuma 3.13:1 dan gagal WCAG. Ini kesalahan paling sering di deck "berani".
- **Angka pakai mono.** Lebar digit seragam, jadi `412 / 3 / 0 / 11` bisa dibandingkan sekilas.
- **Sudut tajam (2–4px).** Kartu membulat terasa produk; pitch terasa editorial.

## Output

| File | Dipakai untuk |
|---|---|
| `dist/css/tokens.css` | web, HTML, docs |
| `dist/css/tokens-dark.css` | tema gelap via `[data-theme="dark"]` |
| `dist/tailwind/preset.js` | `presets: [require('./dist/tailwind/preset.js')]` |
| `dist/ts/tokens.ts` | autocomplete + type-safety |
| `dist/json/tokens.resolved.json` | sumber python-pptx / docx / openpyxl |
| `dist/office/theme-scheme.xml` | `<a:clrScheme>` + `<a:fontScheme>` untuk `.potx`/`.dotx` |
| `dist/docs/index.html` | halaman spec, buka langsung di browser |

## Aturan

1. **Semantic wajib alias.** `{"$value": "{color.signal.500}"}`, bukan `"#FF5A1F"`. Hex langsung mematikan theming.
2. **Komponen tidak menyentuh core.** Butuh oranye? Ambil `brand.primary`.
3. **Rename token = breaking change.** Token adalah API publik; naikkan major version.
4. **Token baru hanya kalau dipakai ≥2 komponen.** Selain itu, nilai turunan cukup inline.
5. **`dist/` tidak pernah diedit tangan.**
6. **Kontras dijaga CI.** `build.py --check` memeriksa tema terang *dan* gelap.

## Palet

- Kanvas terang `#F6F4EE` (bone.100) · kanvas gelap `#08090B` (ink.950)
- Tinta `#0F1115` (ink.900) — 17.18:1 di kanvas terang
- Aksen `#FF5A1F` (signal.500) — satu per slide
- Teks link `#B93509` (signal.700) — 5.34:1; signal.600 hanya 3.66:1, gagal
- Status: `#0F8A5F` hijau · `#9A6B0A` amber · `#C0322A` merah

## Tipografi

- **Display** — Space Grotesk, tracking −0.045em di 76px, leading 0.98. Fallback Archivo → Helvetica.
- **Body** — Inter 16–19px, leading 1.4–1.6.
- **Mono** — IBM Plex Mono untuk angka, kicker, footer.

## Layout slide

`layout.slide-width 1280` · `slide-height 720` · `margin-x 80` (6.25%). Semua koordinat di `build/deck.py` memakai piksel slide; pptx mengonversi 1px = 9525 EMU, jadi preview HTML dan file PowerPoint identik.

## Versioning

`v0.2.0` — rebrand dari Corporate Calm ke Signal (pitch). v0.1.0 punya palet navy/sand dan serif; token name tetap, nilainya berubah — kalau ada konsumen lama, ini minor bump yang perlu rebuild.
