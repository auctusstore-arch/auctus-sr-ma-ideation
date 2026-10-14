# Enam fase sr-ideation Auctus

Fase adalah posisi pekerjaan, bukan status yang otomatis selesai saat ada
file. Simpan keputusan scope, evidence pool, dan check yang belum selesai
agar user dapat melanjutkan di percakapan berikutnya.

## Fase 1: Field exploration

Cari SR/MA satu tahun terakhir untuk bidang yang dipilih. Target awal 20-30
records, sort publication date newest first. Kelompokkan berdasarkan kondisi
atau prosedur; tampilkan frekuensi dalam sampel, 3-5 kondisi dominan, 1-2 tema
emerging/niche, dan tiga rekomendasi. Frekuensi retrieval bukan prevalensi
seluruh literatur atau ukuran kualitas topik.

Jika input berupa bibliografi luas, gunakan koleksi sebagai seed, lalu cek
tren dengan PubMed jika tersedia. User dengan intent ide dari file langsung
mendapat daftar ide provisional; jangan berhenti pada tabel kondisi saja.
Untuk eksplorasi bidang tanpa file, setelah hasil tampil minta pilihan 1-2
kondisi sebelum mapping mendalam.

## Fase 2: Literature mapping

Jalankan dua pencarian PubMed terpisah:

1. Original studies: query kondisi, exclude review types, window tiga tahun,
   target awal 30-50 records.
2. Existing SR/MA: query kondisi dengan review filters, window lima tahun,
   target awal 20-30 records.

Filter tersebut adalah pengumpulan awal untuk ideasi. Tipe publikasi bisa
belum terindeks; klasifikasikan hasil dengan metadata/abstrak. Jangan memakai
window sempit sebagai bukti tidak ada review/studi sebelum window. Pada
konfirmasi novelty kandidat teratas, tambah pencarian tanpa batas tanggal
untuk menemukan review seminal atau scope yang tumpang tindih.

Jika Consensus tersedia, cari pertanyaan klinis natural language dan existing
SR secara terpisah. Merge bibliografi dan pertahankan source tags. Validasi
publication year hasil Consensus. Jika mengambil studi di luar window,
sertakan alasannya. Untuk unggahan, simpan seluruh pool dan buat kolom
`in_recent_window`, bukan menghapus records lama dari evidence ledger.

Original studies table: record/study ID, judul, penulis, tahun, negara, desain,
P/I/C/O, outcome/timepoint, N, source, identifier, extraction level, dan
eligibility status. Existing SR table: judul, pertanyaan/PICO, tipe review,
last search date atau NR, kesimpulan/gap yang benar-benar dilaporkan, scope
overlap, source dan identifier. Pisahkan protocols dari completed reviews.

Laporkan unique citation records, confirmed independent studies, possible
companion reports, dan unknown types. Lanjut otomatis ke fase 3.

## Fase 3: Coverage mapping, ideasi, dan scoring

Kelompokkan original studies menurut tema. Bandingkan dengan PICO dan search
date existing SR:

| Coverage | Arti yang dapat dipertanggungjawabkan |
|---|---|
| Covered | SR dengan scope langsung relevan dan search date dalam dua tahun |
| Partially covered | Scope/populasi/outcome berbeda, sintesis terbatas, atau last search date lebih dari dua tahun |
| Not found in assessed sources | Tidak ditemukan review sesuai scope dalam koleksi/pencarian yang dicatat |
| Unknown | Existing SR tidak tersedia, metadata tidak cukup, atau last search date NR |

Tidak boleh mengganti unknown dengan not covered. SR dengan search date NR
bisa punya overlap PICO yang jelas, tetapi recency tetap unknown. Review
lama tidak otomatis layak diupdate: cek adanya studi baru dan value-add.

Utamakan partially covered atau gap yang benar-benar didukung bukti. Untuk
setiap kandidat, tulis relevansi klinis/akademik 1-2 kalimat, PICO draft,
jumlah reports dan independent studies, bukti langsung, coverage, kemungkinan
pooling, serta next validation. Estimasi studi di luar koleksi hanya boleh
diberi label hipotesis dan alasan; jangan menambah feasibility count.

| Domain | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Novelty | SR komprehensif terkini dengan PICO sama, tanpa value-add jelas | SR outdated dan ada alasan update | Coverage parsial dengan gap substantif | Tidak ditemukan SR yang sesuai setelah cek scope dan sumber yang dinyatakan |
| Interest | Relevansi rendah | Relevansi terbatas | Relevan klinis/akademik | Potensi dampak tinggi dengan alasan jelas |
| Feasibility | <3 studi | 3-4 studi | 5-9 studi | >=10 studi |

Feasibility label: Low <5, Medium 5-9, High >=10. Jumlah independent studies
harus confirmed atau dinyatakan rentang confirmed-potential. RCT dan cohort
yang menjawab pertanyaan berbeda tidak boleh dikumpulkan demi skor tinggi.
Laporkan eligibility berdasarkan abstrak sebagai provisional, bukan hasil
full-text screening. Hitung `studies_1yr` hanya dari studi dengan tanggal
yang cukup presisi; year-only yang menyentuh batas window diberi uncertainty.

Unknown novelty memakai `?` atau rentang 0-3. Total yang mengandung unknown
dinyatakan interval, bukan angka pasti. Ranking: gunakan total konservatif
dengan confidence sebagai pertimbangan; tie-breaker: feasibility confirmed,
poolability, lalu relevansi yang dapat dijelaskan. Jangan menyamakan skor
tinggi dengan rekomendasi otomatis Proceed.

Tampilkan sampai lima rekomendasi dan workbook sesuai kontrak output.
Undang user memilih satu atau dua ide untuk fase 4 setelah hasil tersedia.

## Fase 4: Feasibility validation dan FINER

Konfirmasi studies untuk topik terpilih dengan query spesifik, metadata,
abstract, dan full text bila tersedia. Mulai window 3-5 tahun, lalu perluas
jika sedikit studi atau timeline topik memerlukannya. Merge papers baru
tanpa double count dan verifikasi companion reports.

Periksa existing SR menggunakan PubMed serta Cochrane Library, Google
Scholar, dan Consensus bila dapat diakses. Catat akses tiap sumber; jangan
melaporkan database yang tidak diperiksa sebagai sudah clear. PROSPERO:
cari kondisi + intervensi, verifikasi record yang relevan, status dan tanggal
update yang tersedia, serta overlap PICO. Search-engine snippets saja tidak
membuktikan tidak adanya registrasi. Bila akses registry tidak berhasil,
tulis `belum terverifikasi` dan query/tautan untuk pengecekan berikutnya.

| FINER | Yang dinilai |
|---|---|
| Feasible | Independent studies, kompatibilitas desain/outcome/timepoint, effect data, poolability |
| Interesting | Relevansi klinis/akademik dan gap nyata |
| Novel | Overlap PICO, last search date, studi baru, value-add, registrasi |
| Ethical | Penggunaan data, pelaporan etis dan konflik kepentingan yang relevan |
| Relevant | Kesesuaian prioritas kesehatan dan tujuan user |

Gunakan status ✓, ✗, atau ? dengan bukti dan tindakan. Bias publikasi, risk of
bias, heterogeneity, dan certainty of evidence diperiksa sebagai domain
metodologi; jangan menyatakan Ethic gagal hanya karena bias publikasi ada.
Rekomendasikan Proceed / Proceed with modification / Reconsider. Proceed
tetap dapat bersyarat pada pemeriksaan full text atau registry yang tersisa.

Jika SR parsial ada, jelaskan covered scope, gap aktual, refinement, dan
value-add spesifik. Mengganti judul atau menambah outcome tanpa alasan
substansial bukan novelty yang cukup.

## Fase 5: PICO operasional

Gunakan [template PICO](output-contract.md). P harus spesifik tanpa
overspecification, I definisi kelas intervensi/eksposur, C jelas dan node NMA
tidak overlap, O memuat definisi serta timepoint. Pilih desain sesuai
pertanyaan: therapy umumnya RCT; harm/prognosis dapat memakai observational
studies sesuai justifikasi. Outcome primary harus memiliki metode sintesis
yang jelas; SR tetap dapat memakai narrative synthesis jika pooling tidak
layak. Secondary outcomes maksimal tiga sesuai alur sumber.

Buat search string PubMed dan draft Embase dengan platform disebutkan
(Embase.com vs Ovid). Jangan memakai sintaks campuran. Validasi MeSH/Emtree
bila tools tersedia; term yang belum dicek diberi label draft. Comparator dan
outcome terms opsional untuk menjaga sensitivitas retrieval.

Tentukan eligibility, subgroup, follow-up, jenis MA, dan target studi yang
pragmatis. Bila fase 4 belum tuntas, beri label `PICO operasional provisional`
dan daftar cek tersisa. Jangan merujuk ke skill sr-pipeline atau
sr-manuscript-analysis sebagai dependency wajib: skill itu tidak dibundel.
Jika tersedia dan user meminta, boleh tawarkan handoff.

## Fase 6: Full-text spot check opsional

Dengan full text yang dapat diakses, ekstrak PICO aktual, cocokkan dengan
draft, beri included/excluded/uncertain berikut alasan, dan hitung ulang
independent eligible studies serta outcome-compatible subsets. Bedakan
jumlah PDF yang dibaca dari total pool. Abstract-only bukan full-text check.
Finalkan PICO untuk subset yang benar-benar diperiksa dan laporkan scope
pemeriksaan. Spot check tidak menggantikan full systematic screening.
