# Corporate Calm — Design System

Satu sumber kebenaran untuk **deck, dokumen, web, dan aplikasi**.
Nilai mentah hanya hidup di lapis *core*; semua yang dipakai sehari-hari merujuk lewat token *semantic*.

```
tokens/
  core/        color · type · space · misc        <- primitif, tidak dipakai langsung oleh komponen
  semantic/    light · dark                        <- alias ke core, INI yang dipakai komponen
  component/   button · card · table               <- hanya kalau token semantic kurang spesifik
build/
  build.py     resolver alias + generator output
  examples.py  deck + laporan contoh dari token
dist/          hasil generate, jangan diedit manual
examples/      sample-deck.pptx · sample-report.docx
```

## Pakai

```bash
python build/build.py          # generate dist/
python build/build.py --check  # validasi saja (alias + kontras WCAG), exit 1 kalau gagal
python build/examples.py       # regenerate contoh Office
```

## Output yang dihasilkan

| File | Dipakai untuk |
|---|---|
| `dist/css/tokens.css` | web, HTML, docs |
| `dist/css/tokens-dark.css` | tema gelap via `[data-theme="dark"]` |
| `dist/tailwind/preset.js` | `presets: [require('./dist/tailwind/preset.js')]` |
| `dist/ts/tokens.ts` | autocomplete + type-safety di app |
| `dist/json/tokens.resolved.json` | sumber untuk python-pptx / docx / openpyxl |
| `dist/office/theme-scheme.xml` | `<a:clrScheme>` + `<a:fontScheme>` untuk `.potx`/`.dotx` |
| `dist/docs/index.html` | halaman spec, bisa dibuka langsung di browser |

## Aturan

1. **Semantic wajib alias.** `{"$value": "{color.navy.700}"}`, bukan `"#1E4B7A"`. Hex langsung di semantic mematikan theming dan dark mode.
2. **Komponen tidak menyentuh core.** Kalau butuh `color.navy.700`, ambil `brand.primary`.
3. **Rename token = breaking change.** Anggap token sebagai API publik; naikkan major version.
4. **Tambah token hanya kalau dipakai ≥2 komponen.** Kalau cuma satu tempat, pakai nilai turunan di komponen itu.
5. **`dist/` tidak pernah diedit tangan.** Semua perubahan lewat `tokens/`.
6. **Kontras dijaga di CI.** `build.py --check` menolak kombinasi di bawah ambang WCAG.

## Palet

- Kanvas `#FAFAF7` (sand.100) — hangat, tidak menyilaukan saat diproyeksikan
- Tinta `#12304F` (navy.900) — kontras 12.86:1 di kanvas
- Brand `#1E4B7A` (navy.700) — aksi primer, heading
- Aksen status: `#2E7D5B` hijau, `#B8791A` amber, `#B23B32` merah

## Tipografi

- **Heading** — Source Serif 4. Terbaca di proyektor *dan* di kertas; memberi bobot yang tidak dimiliki sans-serif.
- **Body** — Inter. Netral, tinggi x yang lega, aman di 13–17px.
- **Mono** — IBM Plex Mono. Label, metadata, angka di tabel.

Kalau font belum terpasang di mesin target, jatuh ke Georgia / Helvetica / Consolas — metrik masih mirip.

## Versioning

`v0.1.0` — struktur awal. Perubahan warna/tipografi yang tidak memutus = minor; rename atau hapus token = major.
