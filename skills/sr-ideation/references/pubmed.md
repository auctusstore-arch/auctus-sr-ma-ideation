# Koneksi dan query PubMed

Endpoint provider: https://pubmed.caseyjhand.com/mcp
Dokumentasi provider: https://pubmed.caseyjhand.com/
Transport: Streamable HTTP. Jangan menambah API key/token ke package.
Ikuti auth flow host jika provider kelak memerlukannya.

Schema runtime menjadi rujukan utama. Saat build, tool search bernama
`pubmed_search_articles`; fetch metadata `pubmed_fetch_articles`. Prefix
namespace host dapat berbeda. Enumerate tools dan baca schema sebelum call.

## Search yang benar

Contoh argument shape berikut memakai placeholder, bukan literal query:

```json
{
  "query": "(<CONDITION TERMS>) NOT (Review[pt] OR Systematic Review[pt] OR Meta-Analysis[pt])",
  "dateRange": {
    "minDate": "<TODAY MINUS THREE YEARS: YYYY/MM/DD>",
    "maxDate": "<TODAY: YYYY/MM/DD>",
    "dateType": "pdat"
  },
  "maxResults": 50,
  "offset": 0,
  "sort": "pub_date",
  "summaryCount": 30
}
```

Both date bounds wajib nonempty agar filter aktif. DateType `pdat` untuk
publication date, bukan indexing date. Leap-day window disesuaikan ke tanggal
kalender valid. Sort aktual `pub_date`, bukan `most_recent`.

Validasi tanggal records yang dikembalikan. Journal issue date dapat terlihat
lebih baru daripada tanggal pencarian meski artikel telah tersedia secara
elektronik. Jika demikian, fetch metadata dan bedakan electronic publication
date dari print/issue date; tandai konflik/uncertainty. Jangan menghitung
`studies_1yr` secara pasti dari tahun saja atau menganggap filter menjamin
semua displayed dates berada dalam window.

Untuk SR/MA gunakan parenthesized condition terms dan
`publicationTypes: ["Systematic Review", "Meta-Analysis"]` dengan window
satu tahun (eksplorasi) atau lima tahun (mapping). Untuk novelty konfirmasi,
tambahkan review keywords dalam title/abstract dan pencarian tanpa batas
tanggal. Misalnya `(<P AND I>) AND (Systematic Review[pt] OR Meta-Analysis[pt]
OR systematic review[tiab] OR meta-analysis[tiab])`. Metadata review filter
saja dapat melewatkan artikel yang belum diindeks.

Exclude reviews dalam discovery tidak membuktikan semua hasil original
studies: cek desain dan abstrak. Jangan membatasi bahasa/species/free-full-text
secara default tanpa alasan scope yang eksplisit. Mulai dari P/I terms;
outcome/comparator terms dapat mengurangi sensitivitas.

`totalCount` adalah query hit count, bukan jumlah studi eligible. Laporkan
jumlah returned/read serta cap/pagination. Gunakan `offset` untuk page
berikutnya bila dibutuhkan. Batas sampling awal adalah untuk ideasi, bukan
comprehensive systematic search. Catat query, effectiveQuery, filter, waktu,
hit count, PMIDs retrieved, records fetched, dan alasan stopping.

## Metadata dan full text

`pubmed_fetch_articles` dengan daftar `pmids` memberikan metadata/abstract.
Ikuti required booleans schema aktual seperti includeMesh, includeGrants,
dan includeInvestigators. Ambil small batches. Jika response memberikan
`deferred.ids` atau unavailable PMIDs, proses secara eksplisit, jangan
mengklaim metadata semuanya sudah dibaca.

`pubmed_fetch_fulltext` dipakai hanya bila diperlukan untuk spot check,
menggunakan PMID/PMCID/DOI sesuai schema aktual. Full text tersedia hanya
untuk sumber yang dapat diakses provider. Catat unavailable dan layer sumber
yang dikembalikan; jangan menyimpulkan eligibility dari gagal fetch.

`pubmed_lookup_mesh` membantu menyusun query. Citation formatting dan
related-article tools tersedia bila didukung discovery. Jangan menjadikan
tool citation export sebagai pengganti membaca bukti.

## Source provenance

[UP:filename] = koleksi unggahan; [PM] = PubMed; [CN] = Consensus opsional.
Gabungkan tags untuk paper yang sama dan simpan record linkage. Overlap
retrieval tidak menjadikan paper lebih kuat secara metodologis.

Koneksi endpoint yang berhasil saat build bukan bukti plugin telah dipasang
di akun pengguna atau server akan selalu tersedia. Setelah instalasi, uji
search kecil dan fetch salah satu PMID hasil search dengan tools plugin.
