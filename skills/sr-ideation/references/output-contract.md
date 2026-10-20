# Kontrak output

## Paket hasil unggahan

Tampilkan ringkasan fase dan alasan, evidence quality, coverage map, lalu
ranked ideas. Tabel rekomendasi minimal:

```text
ID | Topik | Gap/value-add | PICO draft | Reports unik | Independent studies
confirmed/potential | Studies_1yr | Coverage | Novelty(0-3/?) | Interest(0-3)
| Feasibility(0-3/range) | Total(0-9/range) | Confidence | Evidence IDs
| Rationale | Next step
```

Seluruh candidate ideas harus traceable ke evidence IDs. `UP00001` dan source
file/record cukup untuk records tanpa PMID/DOI. Jangan memalsukan citation.
Berikan link PubMed/DOI hanya dari identifier yang valid dan tersedia.

## Blok verifikasi untuk Auctus Idea Board

User Auctus memeriksa klaim feasibility dan novelty di Idea Board dengan
menempel PMID dari chat. Di bawah setiap ide yang direkomendasikan, tulis dua
baris ini dengan format persis:

```text
BUKTI FEASIBILITY (PMID): <PMID studi original pendukung, dipisah koma>
SR TERAKHIR (PMID, tahun): <PMID SR/MA terbaru tentang topik ini (tahun)> | belum ada
```

- Hanya cantumkan PMID yang benar-benar didapat dari PubMed atau file unggahan
  dan sudah dicek metadata-nya. Jangan menebak atau menyusun PMID.
- BUKTI FEASIBILITY berisi studi original independen yang menjadi dasar skor
  Feasibility, bukan review.
- SR TERAKHIR adalah SR/MA terbaru yang menjadi dasar skor Novelty. Tulis
  `belum ada` hanya jika pencarian SR sudah dilakukan dan tidak menemukan apa pun.
- Jika PMID belum bisa diverifikasi (misalnya PubMed tidak terhubung), tulis
  `belum terverifikasi` dan jelaskan alasannya.

Jika runtime tersedia, simpan:

- `intake/intake.json`: canonical records, origins, warnings, counts, phase
  hint, duplicate decisions. Raw fields disimpan untuk audit.
- `intake/records.csv`: normalized records dengan formula escaping.
- `analysis.json`: keputusan fase agent, ideas, original studies, existing
  reviews, PICO drafts, search log, audit notes.
- `auctus-ideation.xlsx`: Prioritas, Studi_Original, Existing_SR, PICO_Draft,
  Audit, dan Search_Log. PICO draft awal boleh partial/NR; update setelah
  validasi dan pilihan user, tidak perlu menunggu fase 4 untuk membuat sheet.

Agent membuat `analysis.json` dari analisis yang benar-benar dilakukan,
bukan menyalin jumlah otomatis sebagai skor. Schema fleksibel berikut:

```json
{
  "phase": {"mode": "D+B", "phase": 3, "confidence": "sedang", "reason": "..."},
  "ideas": [
    {"id": "I01", "topic": "...", "gap": "...", "pico_draft": "...",
     "unique_reports": 0, "independent_studies_confirmed": 0,
     "independent_studies_potential": 0, "studies_1yr": "NR",
     "coverage": "unknown", "novelty_score": "?", "interest_score": 2,
     "feasibility_score": "0-1", "total": "2-6", "confidence": "rendah",
     "evidence_ids": ["UP00001"], "rationale": "...", "next_steps": "..."}
  ],
  "original_studies": [],
  "existing_reviews": [],
  "pico_drafts": [],
  "audit": [{"item": "...", "detail": "..."}],
  "search_log": []
}
```

Arrays untuk study/review/PICO/search log berisi objek dengan column keys
yang jelas. Empty arrays berarti belum tersedia, bukan clear/null result.
Jangan tampilkan contoh schema di atas sebagai hasil studi yang nyata.

Workbook dapat dibuat dengan helper:

```text
python3 <skill-dir>/scripts/export_workbook.py <analysis.json> --output <host-output-dir>/auctus-ideation.xlsx
```

Helper memakai openpyxl jika tersedia. Untuk file workbook besar atau
integrasi spreadsheet host, baca skill spreadsheet yang tersedia. Tidak ada
ketergantungan pada `/mnt/skills/public/xlsx/SKILL.md` atau direktori Claude.
Jika openpyxl tidak tersedia dan host tidak mendukung workbook, hasil JSON,
CSV, dan tabel tetap diberikan beserta keterbatasannya.

## PICO operasional

```text
TOPIK SR:
STATUS: provisional / validated scope-limited
REVIEW TYPE: SR / pairwise MA / NMA / diagnostic / prognostic / scoping

P: kondisi, usia/setting/severity, inklusi dan eksklusi populasi
I/E: kelas intervensi/eksposur, variasi, eksklusi
C: active comparator, placebo/standard care, NMA nodes bila relevan
O primary: definisi, effect measure/data yang diperlukan, timepoint
O secondary: maksimal tiga, definisi dan timepoint
S: desain inklusi/eksklusi dan minimum follow-up

ELIGIBILITY: kriteria inklusi/eksklusi operasional
PUBMED QUERY: P terms, I/E terms, C/O optional, full Boolean string
EMBASE DRAFT: platform dan sintaks eksplisit; term yang belum diverifikasi
SUBGROUPS: sampai tiga yang punya alasan klinis dan dukungan data
SYNTHESIS: jenis MA atau narrative synthesis, alasan, unit of analysis
FEASIBILITY: eligible independent studies confirmed/potential dan data gaps
VALIDATION REMAINING: full text, effect data, study linkage, registry, dll
```

Pembaca harus dapat membedakan data yang diekstrak, inferensi, dan hipotesis
ide. Semua file diberi tautan ke artefak yang benar-benar dibuat di host.
