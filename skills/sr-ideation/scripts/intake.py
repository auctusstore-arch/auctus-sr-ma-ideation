#!/usr/bin/env python3
"""Normalize bibliographic files; phase hints are not clinical assessment."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import difflib
import io
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ALIASES = {
    "title": ["title", "article title", "ti", "judul", "document title"],
    "abstract": ["abstract", "ab", "abstrak", "abstract note"],
    "year": ["year", "publication year", "publication date", "pubdate", "dp", "tahun", "date"],
    "doi": ["doi", "digital object identifier"],
    "pmid": ["pmid", "pubmed id", "pubmed identifier"],
    "authors": ["authors", "author", "au", "penulis"],
    "journal": ["journal", "journal title", "source title", "publication title", "jt"],
    "publication_types": ["publication type", "publication types", "document type", "article type", "pt", "type"],
    "study_design": ["study design", "design", "desain", "desain studi"],
    "population": ["population", "populasi", "p population"],
    "intervention": ["intervention", "exposure", "intervention exposure", "intervensi", "eksposur"],
    "comparator": ["comparator", "comparison", "control", "komparator"],
    "outcomes": ["outcome", "outcomes", "primary outcome", "luaran"],
    "sample_size": ["sample size", "total n", "n", "jumlah sampel"],
    "country": ["country", "negara"],
    "last_search_date": ["last search date", "search date", "tanggal pencarian"],
    "source_reported": ["source", "database", "source database", "sumber"],
}


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalized(value):
    value = unicodedata.normalize("NFKD", clean(value)).casefold()
    return "".join(c for c in value if c.isalnum())


def title_key(value):
    value = unicodedata.normalize("NFKD", clean(value)).casefold()
    return " ".join(re.findall(r"[^\W_]+", value, flags=re.UNICODE))


def doi_value(value):
    # PII and accession numbers are not DOI identifiers.
    match = re.search(r"10\.\d{4,9}/[^\s\"<>]+", clean(value), flags=re.I)
    return match.group(0).rstrip(".,;").casefold() if match else ""


def pmid_value(value):
    value = clean(value)
    if value.isdigit():
        return value
    match = re.search(r"(?:pubmed\.ncbi\.nlm\.nih\.gov/|ncbi\.nlm\.nih\.gov/pubmed/|PMID\s*[:=]?\s*)(\d+)", value, re.I)
    return match.group(1) if match else ""


def year_value(value):
    match = re.search(r"\b((?:18|19|20|21)\d{2})\b", clean(value))
    return int(match.group(1)) if match else None


def read_text(path):
    data = path.read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16"), "utf-16", []
    try:
        return data.decode("utf-8-sig"), "utf-8-sig", []
    except UnicodeDecodeError:
        return data.decode("cp1252"), "cp1252", ["encoding_fallback_cp1252"]


def parse_csv(text):
    try:
        dialect = csv.Sniffer().sniff(text[:32768], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    headers = reader.fieldnames or []
    mapping = {}
    for field, names in ALIASES.items():
        matches = [h for h in headers if normalized(h) in {normalized(n) for n in names}]
        if matches:
            mapping[field] = matches[0]
    if not any(field in mapping for field in ("title", "doi", "pmid")):
        raise ValueError("CSV requires an identifiable title, DOI, or PMID header; headerless/ambiguous CSV was not silently reinterpreted.")
    rows = []
    for index, row in enumerate(reader, 1):
        if all(not clean(v) for v in row.values()):
            continue
        warning = []
        if None in row:
            warning.append("csv_extra_cells")
        if any(v is None for v in row.values()):
            warning.append("csv_missing_cells")
        raw = {str(k) if k is not None else "_extra_cells": v for k, v in row.items()}
        fields = {field: row.get(header, "") for field, header in mapping.items()}
        rows.append((index, fields, raw, warning))
    return rows, {"headers": headers, "mapped_columns": mapping, "delimiter": dialect.delimiter}


def parse_tagged(text, kind):
    records, tags, warnings = [], {}, []
    last = None

    def flush():
        nonlocal tags, warnings, last
        if tags:
            records.append((len(records) + 1, tags, list(warnings)))
        tags, warnings, last = {}, [], None

    pattern = r"^([A-Z0-9]{2})\s+-\s?(.*)$" if kind == "ris" else r"^([A-Z0-9]{2,4})\s*-\s?(.*)$"
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            # NBIB exports use blank lines between records; RIS abstracts may
            # contain blanks within a record, so ER/TY delimit RIS instead.
            if kind == "nbib":
                flush()
            continue
        match = re.match(pattern, line)
        if match:
            tag, value = match.groups()
            if kind == "ris" and tag == "TY" and tags:
                warnings.append("ris_missing_ER")
                flush()
            if kind == "nbib" and tag == "PMID" and tags:
                flush()
            if kind == "ris" and tag == "ER":
                flush()
                continue
            tags.setdefault(tag, []).append(value.strip())
            last = tag
        elif line[:1].isspace() and last:
            tags[last][-1] = clean(tags[last][-1] + " " + line.strip())
        else:
            warnings.append(f"unparsed_line_{line_no}")
    if kind == "ris" and tags:
        warnings.append("ris_missing_ER")
    flush()
    rows = []
    for index, raw, warning in records:
        def first(*keys):
            for key in keys:
                if raw.get(key):
                    return clean(" ".join(raw[key]))
            return ""
        if kind == "ris":
            accession = first("AN")
            explicit_pmid = pmid_value(accession) if re.search("pmid", accession, re.I) else ""
            fields = {"title": first("TI", "T1", "CT"), "abstract": first("AB", "N2"),
                      "authors": raw.get("AU", raw.get("A1", [])), "year": first("PY", "Y1", "DA"),
                      "doi": first("DO"), "pmid": first("PM") or explicit_pmid or pmid_value(first("UR")),
                      "journal": first("JO", "JF", "T2"), "publication_types": raw.get("TY", [])}
            if "TY" not in raw:
                warning.append("ris_missing_TY")
        else:
            identifiers = raw.get("AID", []) + raw.get("LID", [])
            dois = [doi_value(v) for v in identifiers if "[pii]" not in v.casefold() and doi_value(v)]
            fields = {"title": first("TI"), "abstract": first("AB"), "authors": raw.get("FAU", raw.get("AU", [])),
                      "year": first("DP"), "doi": dois[0] if dois else "", "pmid": first("PMID"),
                      "journal": first("JT", "TA"), "publication_types": raw.get("PT", [])}
        rows.append((index, fields, raw, warning))
    return rows, {}


def list_value(value):
    if isinstance(value, list):
        return [clean(v) for v in value if clean(v)]
    return [v.strip() for v in re.split(r"[;|]", clean(value)) if v.strip()]


def classify(record):
    metadata = " ".join([record["title"], record["study_design"], *record["publication_types"]]).casefold()
    text = metadata + " " + record["abstract"].casefold()
    if re.search(r"\b(protocol|protocols)\b", record["title"].casefold()) or "study protocol" in record["study_design"].casefold():
        return "protocol"
    if re.search(r"systematic\s+review|meta[ -]?analys|network meta|scoping\s+review", metadata):
        return "systematic_review_or_meta_analysis"
    if any("review" in t.casefold() for t in record["publication_types"]) or re.search(r"\b(narrative review|review of|a review)\b", record["title"].casefold()):
        return "narrative_review"
    if re.search(r"randomi[sz]ed|clinical trial|\brct\b|cohort|case[ -]control|cross[ -]sectional|observational|registry|retrospective|prospective", text):
        return "primary_study_candidate"
    return "unknown"


def make_record(index, fields, raw, warnings, path, source_index):
    record = {name: clean(fields.get(name)) for name in ALIASES if name not in ("authors", "publication_types", "year")}
    record.update({"record_id": f"UP{index:05d}", "record_ids": [f"UP{index:05d}"],
                   "authors": list_value(fields.get("authors", [])),
                   "publication_types": list_value(fields.get("publication_types", [])),
                   "year": year_value(fields.get("year")), "publication_date_raw": clean(fields.get("year")),
                   "doi": doi_value(fields.get("doi")), "pmid": pmid_value(fields.get("pmid")),
                   "source_tags": [f"UP:{path.name}"],
                   "origins": [{"file": path.name, "record_number": source_index, "raw_fields": raw}],
                   "warnings": list(warnings), "extraction_level": "mapped_fields_only",
                   "eligibility": "not_assessed", "independent_study_id": None})
    if fields.get("doi") and not record["doi"]:
        record["warnings"].append("invalid_DOI")
    if fields.get("pmid") and not record["pmid"]:
        record["warnings"].append("invalid_PMID")
    if not record["abstract"]:
        record["warnings"].append("missing_abstract")
    if not record["year"]:
        record["warnings"].append("missing_or_unparsed_year")
    record["usable_bibliography"] = bool(record["title"] or record["doi"] or record["pmid"])
    if not record["usable_bibliography"]:
        record["warnings"].append("missing_bibliographic_identity")
    record["type_hint"] = classify(record)
    return record


def identifier_conflict(a, b):
    return any(a.get(key) and b.get(key) and a[key] != b[key] for key in ("doi", "pmid"))


def merge_records(a, b):
    for field in ALIASES:
        if field in ("authors", "publication_types"):
            a[field] = list(dict.fromkeys(a[field] + b[field]))
        elif not a.get(field) and b.get(field):
            a[field] = b[field]
        elif a.get(field) and b.get(field) and a[field] != b[field]:
            a["warnings"].append(f"metadata_disagreement_{field}")
    a["origins"].extend(b["origins"])
    if not a["publication_date_raw"]:
        a["publication_date_raw"] = b["publication_date_raw"]
    a["record_ids"].extend(b["record_ids"])
    a["source_tags"] = list(dict.fromkeys(a["source_tags"] + b["source_tags"]))
    a["warnings"] = list(dict.fromkeys(a["warnings"] + b["warnings"]))
    if a["abstract"]:
        a["warnings"] = [w for w in a["warnings"] if w != "missing_abstract"]
    if a["year"]:
        a["warnings"] = [w for w in a["warnings"] if w != "missing_or_unparsed_year"]
    a["type_hint"] = classify(a)


def deduplicate(records):
    kept, decisions, flags = [], [], []
    identifiers, titles = {}, {}
    for record in records:
        keys = [(field, record[field]) for field in ("pmid", "doi") if record[field]]
        tk = (title_key(record["title"]), record["year"]) if record["title"] and record["year"] else None
        candidates = list(dict.fromkeys([i for key in keys for i in identifiers.get(key, [])] + titles.get(tk, [])))
        target = None
        for i in candidates:
            previous = kept[i]
            if identifier_conflict(previous, record):
                flags.append({"a": previous["record_id"], "b": record["record_id"], "reason": "identifier_conflict"})
                previous["warnings"].append("identifier_conflict")
                record["warnings"].append("identifier_conflict")
                continue
            target = i
            break
        if target is not None:
            previous = kept[target]
            reason = "identifier_match" if any(previous.get(k) == v for k, v in keys) else "exact_title_and_year"
            decisions.append({"kept": previous["record_id"], "merged": record["record_id"], "reason": reason})
            merge_records(previous, record)
            for key in keys:
                if target not in identifiers.setdefault(key, []):
                    identifiers[key].append(target)
            if tk and target not in titles.setdefault(tk, []):
                titles[tk].append(target)
        else:
            position = len(kept)
            kept.append(record)
            for key in keys:
                identifiers.setdefault(key, []).append(position)
            if tk:
                titles.setdefault(tk, []).append(position)
    # No automatic merge from fuzzy similarity. Runtime work is bounded and
    # the partial-scan flag is part of the audit result.
    comparisons, partial = 0, False
    known = {(f["a"], f["b"]) for f in flags}
    for i, a in enumerate(kept):
        if not a["title"]:
            continue
        for b in kept[i + 1:]:
            if comparisons >= 200000:
                partial = True
                break
            comparisons += 1
            if not b["title"] or (a["record_id"], b["record_id"]) in known:
                continue
            ratio = difflib.SequenceMatcher(None, title_key(a["title"]), title_key(b["title"]), autojunk=False).ratio()
            if ratio >= 0.8:
                flags.append({"a": a["record_id"], "b": b["record_id"], "reason": "possible_duplicate_title", "similarity": round(ratio, 3)})
        if partial:
            break
    return kept, decisions, flags, partial


def phase_hint(records, intent, selected_topic):
    if selected_topic or intent == "validate":
        return {"mode": "D+C", "phase": 4, "confidence": "high_for_explicit_intent",
                "reason": "User selected a topic or explicitly requested validation; prior evidence still needs audit."}
    if intent == "explore":
        return {"mode": "D+A", "phase": 1, "confidence": "high_for_explicit_intent",
                "reason": "User explicitly requested field exploration."}
    counts = Counter(r["type_hint"] for r in records if r["usable_bibliography"])
    if intent == "map":
        phase, reason = 2, "User requested mapping; continue automatically to recommendations."
    elif counts["primary_study_candidate"] and counts["systematic_review_or_meta_analysis"]:
        phase, reason = 3, "Both study candidates and reviews are present; audit scope in phase 2 before ideation."
    elif counts["systematic_review_or_meta_analysis"] and not counts["primary_study_candidate"]:
        phase, reason = 1, "Review-dominant bibliography; agent must assess whether one condition is already selected."
    else:
        phase, reason = 2, "Literature collection needs mapping and study/review verification before scoring."
    return {"mode": "D", "phase": phase, "confidence": "low_heuristic",
            "reason": reason, "agent_semantic_assessment_required": True}


def safe_cell(value):
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    value = "" if value is None else str(value)
    if value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")) or value.startswith(("\t", "\r", "\n")):
        return "'" + value
    return value


def run(paths, out_dir, intent=None, selected_topic=None, as_of=None):
    as_of = as_of or dt.date.today()
    records, files = [], []
    for path in paths:
        info = {"file": path.name}
        try:
            text, encoding, warning = read_text(path)
            stripped = text.lstrip()
            if path.suffix.casefold() == ".csv":
                kind = "csv"
            elif re.match(r"TY\s+-", stripped) or path.suffix.casefold() == ".ris":
                kind = "ris"
            elif re.match(r"PMID\s*-", stripped) or path.suffix.casefold() in (".nbib", ".medline"):
                kind = "nbib"
            else:
                raise ValueError("Unsupported/ambiguous bibliography format; expected CSV, RIS, or NBIB.")
            rows, detail = parse_csv(text) if kind == "csv" else parse_tagged(text, kind)
            if not rows:
                raise ValueError("No bibliographic records parsed; content was not treated as a successful empty dataset.")
            info.update({"format": kind, "encoding": encoding, "records_parsed": len(rows), "warnings": warning, **detail})
            for source_index, fields, raw, warnings in rows:
                records.append(make_record(len(records) + 1, fields, raw, warnings, path, source_index))
        except (OSError, UnicodeError, ValueError, csv.Error) as error:
            info.update({"error": str(error), "records_parsed": 0})
        files.append(info)
    unique, decisions, possible, partial = deduplicate(records)
    usable = [r for r in unique if r["usable_bibliography"]]
    for record in unique:
        if record["year"] and record["year"] > as_of.year:
            record["warnings"].append("publication_year_after_analysis_date_verify")
    years = [r["year"] for r in usable if r["year"]]
    report = {
        "schema_version": "1.0", "analysis_date": as_of.isoformat(), "files": files,
        "summary": {"parsed_records": len(records), "unique_records": len(unique),
                    "usable_unique_citation_records": len(usable), "duplicate_records_merged": len(decisions),
                    "possible_duplicates_or_conflicts": len(possible), "fuzzy_scan_partial": partial,
                    "abstract_present": sum(bool(r["abstract"]) for r in usable),
                    "abstract_coverage": round(sum(bool(r["abstract"]) for r in usable) / len(usable), 3) if usable else None,
                    "year_min": min(years) if years else None, "year_max": max(years) if years else None,
                    "type_hints": dict(Counter(r["type_hint"] for r in usable)),
                    "independent_eligible_studies": "not_assessed",
                    "failed_files": sum("error" in f for f in files)},
        "phase_hint": phase_hint(usable, intent, selected_topic),
        "duplicate_decisions": decisions, "possible_duplicates": possible, "records": unique,
        "limitations": ["Type and phase hints require agent review.", "Citation records are not independent eligible studies.",
                        "No clinical extraction, novelty validation, scoring, or recommendation is performed by this parser.",
                        "Raw input fields are untrusted data; CSV output formula-like cells are escaped."]}
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "intake.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    columns = ["record_id", "title", "abstract", "authors", "year", "publication_date_raw", "doi", "pmid", "journal",
               "publication_types", "type_hint", "study_design", "population", "intervention", "comparator", "outcomes",
               "sample_size", "country", "last_search_date", "source_reported", "source_tags", "warnings", "eligibility"]
    with (out_dir / "records.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows({key: safe_cell(r.get(key)) for key in columns} for r in unique)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", type=Path, nargs="+")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--intent", choices=["explore", "map", "validate"])
    parser.add_argument("--selected-topic")
    parser.add_argument("--as-of", type=dt.date.fromisoformat, help="Use current date from host context: YYYY-MM-DD")
    args = parser.parse_args()
    report = run(args.files, args.out_dir, args.intent, args.selected_topic, args.as_of)
    print(json.dumps({"summary": report["summary"], "phase_hint": report["phase_hint"],
                      "output": str(args.out_dir.resolve())}, ensure_ascii=False))
    return 2 if report["summary"]["failed_files"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
