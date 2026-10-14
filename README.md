# Auctus SR-MA Ideation

<img src="assets/auctus-logo-v0.1.1.jpg" alt="Logo Auctus" width="128" height="128">

Plugin Auctus untuk menemukan dan mengevaluasi ide systematic review (SR),
meta-analisis (MA), dan network meta-analisis (NMA). Versi plugin: **0.1.1**.

Unggah CSV, RIS, atau NBIB berisi literatur. Plugin membaca koleksi,
mengidentifikasi fase berdasarkan isi dan tujuan pengguna, memetakan bukti,
lalu merekomendasikan ide dengan skor, PICO draft, dan sumber pendukung.
Novelty yang belum diverifikasi tetap ditandai sebagai provisional/unknown.

## Instalasi untuk user Auctus

### ChatGPT melalui ZIP

1. Unduh [ZIP plugin v0.1.1](https://github.com/auctusstore-arch/auctus-sr-ma-ideation/releases/download/v0.1.1/auctus-sr-ma-ideation-0.1.1.zip).
2. Buka ChatGPT dan pilih **@Plugin Creator**.
3. Unggah ZIP lalu tulis: **"Buat plugin privat dari ZIP ini, lalu berikan
   tautan untuk memasangnya."**
4. Buka tautan hasilnya, pasang plugin, dan selesaikan setup yang ditampilkan.

Setiap pengguna membuat salinan di akun/workspace sendiri. Salinan ini tidak
otomatis mengikuti perubahan repo. Untuk versi baru, gunakan ZIP rilis baru
dan minta Plugin Creator memperbarui plugin yang sudah ada.

### Codex melalui marketplace GitHub

Dengan Codex CLI yang mendukung plugin marketplaces:

```sh
codex plugin marketplace add auctusstore-arch/auctus-sr-ma-ideation --ref main
```

Buka Plugins Directory di host desktop yang mendukung marketplace, pilih
**Auctus Plugins**, lalu pasang **Auctus SR-MA Ideation**. Jika belum muncul,
restart aplikasi sesuai [panduan resmi OpenAI](https://developers.openai.com/plugins/build/plugins).

Untuk menyegarkan source marketplace:

```sh
codex plugin marketplace upgrade auctus
```

Perintah marketplace mengatur source. Instalasi dan koneksi plugin tetap
mengikuti flow host. Repo publik ini tidak otomatis menerbitkan plugin ke
direktori publik OpenAI. Admin workspace dapat memakai repo sebagai sumber
marketplace sesuai [panduan impor GitHub](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github).

## Mulai memakai

- "Cari ide SR/MA di bidang kardiologi."
- "Analisis RIS yang aku unggah, identifikasi faseku, lalu rekomendasikan
  lima ide SR/MA beserta skor, PICO draft, dan bukti pendukung."
- "Validasi novelty dan feasibility topik pilihanku, lakukan FINER check,
  lalu buat PICO operasional."

Plugin mengikuti enam fase: eksplorasi bidang, literature mapping,
ideasi/scoring, validasi FINER, PICO operasional, dan full-text spot check.
Untuk unggahan bibliografi, pengguna tidak perlu memilih fase terlebih dulu.

## Koneksi PubMed

Endpoint: **https://pubmed.caseyjhand.com/mcp**, melalui Streamable HTTP.
Koneksi ini ada di `mcp.json` dan `.mcp.json`. Package tidak berisi API key
atau kredensial. Plugin memakai schema tool aktual dan hanya mengirim query
atau identifier bibliografi yang diperlukan ke PubMed.

Pencarian dan fetch metadata endpoint sudah diuji saat pembuatan plugin.
Ketersediaan server dapat berubah; instalasi di setiap host tetap perlu
diuji. Consensus dipakai jika sudah tersedia di host, bukan dependency wajib.

## File dan hasil

CSV/RIS/NBIB dibaca melalui fasilitas attachment dan file/code runtime host.
Parser Python standard library menormalisasi bibliografi, menyimpan
provenance, serta menandai masalah metadata dan possible duplicates.
Keputusan fase final, interpretasi klinis, dan rekomendasi dilakukan agent
dengan instruksi skill. Parser sendiri tidak menghasilkan skor klinis.

Hasil dapat berupa tabel ide, evidence ledger, JSON/CSV, dan workbook Excel
enam sheet bila runtime mendukung. Workbook memerlukan `openpyxl` atau
fasilitas spreadsheet host. Plugin tidak menyediakan upload UI terpisah.

Record artikel tidak otomatis dihitung sebagai studi independen. Judul
mirip tidak langsung digabungkan. Titles-only tetap dapat menghasilkan ide
eksploratif dengan keterbatasan yang dinyatakan.

## Struktur repo

```text
.agents/plugins/marketplace.json    Marketplace Auctus
plugin.json                       Portable Agent Plugins 1.0 manifest
mcp.json                          Portable PubMed MCP configuration
.codex-plugin/plugin.json         Compatibility manifest
.mcp.json                         Compatibility MCP configuration
assets/                           Logo Auctus
skills/sr-ideation/SKILL.md        Entry workflow
skills/sr-ideation/references/     Fase, intake, output, PubMed, metodologi
skills/sr-ideation/scripts/        Intake dan exporter workbook
scripts/package_plugin.py         Validasi dan build ZIP
tests/test_plugin.py              Synthetic file-handling tests
.github/workflows/check.yml       CI tests dan validasi package
```

## Mengembangkan dan membangun ZIP

Python 3.10+ diperlukan untuk helper dan pengujian. Dari root repo:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/package_plugin.py
```

ZIP dibuat di `dist/auctus-sr-ma-ideation-<version>.zip`. ZIP hanya berisi
plugin, skills, logo, README, dan MCP configuration; tidak menyertakan Git
history, tests, CI, atau runtime dependencies.

Untuk rilis baru, sinkronkan versi di kedua manifest, perbarui README serta
CHANGELOG, jalankan checks, lalu buat GitHub Release dengan ZIP hasil build.

## Prinsip metodologi

Alur mengikuti skill sr-ideation Auctus dengan guardrails: evidence harus
traceable, tidak ditemukannya SR bukan bukti novelty universal, search date
berbeda dari publication year, dan jumlah studi saja tidak membuktikan
poolability. Detail ada di
[catatan metodologi](skills/sr-ideation/references/methodology.md).

## Hak penggunaan

Logo dan materi Auctus tetap milik pemiliknya. Repo tersedia untuk distribusi
plugin kepada user Auctus; belum ada lisensi open-source yang ditetapkan.
