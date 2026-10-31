#!/usr/bin/env python3
"""Merge ProteomeCentral UI search exports into one keyword-tagged table.

Expected file naming in the target directory (what the PX UI downloads,
renamed per keyword — spaces in the keyword become underscores):

    <keyword>_proteomexchange_search.tsv          # full search result
    <keyword>_sdrf_proteomexchange_search.tsv     # OPTIONAL: SDRF-filtered rerun

For every full file it:
  1. adds an 'SDRF_Found' column (second position) — SDRF / NO-SDRF.
     Priority: (a) membership in the matching *_sdrf_* file if present,
     (b) an existing SDRF_Found column in the file (kept as-is),
     (c) fallback: the row's own 'curated valid'/'repository valid' text.
  2. adds a 'search_keyword' column (last position).
Then it writes:
  merged_px_searches.tsv        one row per (dataset x keyword)   [long format]
  merged_px_searches_dedup.tsv  one row per dataset, keywords joined, SDRF=any
and prints per-keyword counts, SDRF rates, and the deduplicated union size.

Stdlib only. Handles the two corruption classes seen in real exports:
encoding mojibake (UTF-8 read as cp1252: 'Î²' -> 'β') and ragged rows
(the UI emits more data columns than header names — extra columns are kept
and named extra_col_N rather than guessed).

Usage:
    python merge_px_searches.py [directory]      # default: current directory
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ACC_RE = re.compile(r"^(PXD\d+|MSV\d+|IPX\d+|JPST\d+)$")
SDRF_TEXT_RE = re.compile(r"\b(curated|repository|agentic)\s+valid\b", re.I)
FULL_SUFFIX = "_proteomexchange_search.tsv"
SDRF_SUFFIX = "_sdrf_proteomexchange_search.tsv"


def read_text(path: Path) -> str:
    """Read with encoding fallback, then repair UTF-8-as-cp1252 mojibake."""
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8"):
        try:
            txt = raw.decode(enc)
            break
        except UnicodeDecodeError:
            txt = None
    if txt is None:
        txt = raw.decode("cp1252", errors="replace")
    return txt


_MOJIBAKE_HINT = re.compile(r"Ã.|â€.|Î.")


def fix_mojibake(cell: str) -> str:
    """Repair UTF-8-read-as-cp1252 damage ('Î²' -> 'β'), cell by cell.

    Applied per field, not per file: real exports mix clean and damaged
    cells (e.g. after an Excel round-trip), so a whole-file repair fails
    on the first clean non-cp1252 character and silently fixes nothing.
    """
    if not _MOJIBAKE_HINT.search(cell):
        return cell
    try:
        repaired = cell.encode("cp1252").decode("utf-8")
        return repaired if "�" not in repaired else cell
    except (UnicodeEncodeError, UnicodeDecodeError):
        return cell


def read_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    """Parse a TSV; return (header, data_rows) with ragged rows preserved."""
    lines = [ln for ln in read_text(path).splitlines() if ln.strip()]
    rows = [[fix_mojibake(c) for c in r]
            for r in csv.reader(lines, delimiter="\t")]
    header, data = rows[0], rows[1:]
    data = [r for r in data if r and ACC_RE.match(r[0].strip())]
    width = max([len(header)] + [len(r) for r in data])
    # Name any unnamed trailing columns instead of guessing their meaning.
    header = header + [f"extra_col_{i}" for i in range(1, width - len(header) + 1)]
    data = [r + [""] * (width - len(r)) for r in data]
    return header, data


def sdrf_ids(path: Path) -> set[str]:
    _, data = read_rows(path)
    return {r[0].strip() for r in data}


def main(directory: str = ".") -> int:
    d = Path(directory)
    full_files = sorted(
        p for p in d.glob(f"*{FULL_SUFFIX}") if SDRF_SUFFIX not in p.name
    )
    if not full_files:
        print(f"No *{FULL_SUFFIX} files found in {d.resolve()}", file=sys.stderr)
        return 2

    merged_header: list[str] | None = None
    merged_rows: list[list[str]] = []
    per_dataset: dict[str, dict] = {}
    print(f"{'keyword':<28}{'datasets':>9}{'SDRF':>6}{'rate':>8}   flag source")

    for full in full_files:
        keyword = full.name[: -len(FULL_SUFFIX)].replace("_", " ")
        header, data = read_rows(full)
        twin = full.with_name(full.name.replace(FULL_SUFFIX, SDRF_SUFFIX))
        if twin.exists():
            flagged, source = sdrf_ids(twin), f"twin file ({twin.name})"
            get_flag = lambda r: "SDRF" if r[0].strip() in flagged else "NO-SDRF"
        elif "SDRF_Found" in header:
            idx = header.index("SDRF_Found")
            source = "existing SDRF_Found column"
            get_flag = lambda r, i=idx: ("SDRF" if "SDRF" == r[i].strip().upper()
                                         else "NO-SDRF")
        else:
            source = "row text ('… valid:' fallback)"
            get_flag = lambda r: ("SDRF" if any(SDRF_TEXT_RE.search(c) for c in r)
                                  else "NO-SDRF")

        # Canonical output columns: identifier, SDRF_Found, <rest>, search_keyword
        rest_cols = [h for h in header if h not in ("identifier", "SDRF_Found")]
        out_header = ["identifier", "SDRF_Found"] + rest_cols + ["search_keyword"]
        if merged_header is None:
            merged_header = out_header
        elif out_header != merged_header:
            # Align differing exports onto the first file's schema by name.
            rest_cols = [h for h in merged_header[2:-1]]

        n_sdrf = 0
        col_of = {h: i for i, h in enumerate(header)}
        for r in data:
            acc = r[0].strip()
            flag = get_flag(r)
            n_sdrf += flag == "SDRF"
            rest = [r[col_of[h]] if h in col_of else "" for h in rest_cols]
            merged_rows.append([acc, flag] + rest + [keyword])
            agg = per_dataset.setdefault(acc, {
                "SDRF_Found": "NO-SDRF", "keywords": [],
                "title": "", "repository": "", "species": "", "announce_date": "",
            })
            agg["keywords"].append(keyword)
            if flag == "SDRF":
                agg["SDRF_Found"] = "SDRF"
            for fld in ("title", "repository", "species", "announce_date"):
                if not agg[fld] and fld in col_of:
                    agg[fld] = r[col_of[fld]]
        rate = n_sdrf / len(data) if data else 0
        print(f"{keyword:<28}{len(data):>9}{n_sdrf:>6}{rate:>8.1%}   {source}")

    long_path = d / "merged_px_searches.tsv"
    with open(long_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(merged_header)
        w.writerows(merged_rows)

    dedup_path = d / "merged_px_searches_dedup.tsv"
    with open(dedup_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["identifier", "SDRF_Found", "n_keywords", "keywords",
                    "title", "repository", "species", "announce_date"])
        for acc in sorted(per_dataset):
            a = per_dataset[acc]
            w.writerow([acc, a["SDRF_Found"], len(a["keywords"]),
                        "; ".join(sorted(set(a["keywords"]))),
                        a["title"], a["repository"], a["species"],
                        a["announce_date"]])

    uniq = len(per_dataset)
    sdrf_any = sum(1 for a in per_dataset.values() if a["SDRF_Found"] == "SDRF")
    print("-" * 72)
    print(f"long format : {len(merged_rows)} rows -> {long_path}")
    print(f"deduplicated: {uniq} unique datasets "
          f"({sdrf_any} SDRF, {sdrf_any/uniq:.1%}) -> {dedup_path}")
    print(f"K1 check    : union {'≥' if uniq >= 150 else '<'} 150 "
          f"({'PASS' if uniq >= 150 else 'keep adding keywords'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

import pandas as pd
df = pd.read_csv("merged_px_searches_dedup.tsv", sep="\t")

print(df["repository"].value_counts())                       # PRIDE/MassIVE/iProX/jPOST mix
print(df["species"].value_counts().head(10))                 # human vs model-organism split
df["year"] = df["announce_date"].str.extract(r"(20\d\d)")
print(df.groupby("year").size())                             # archive growth curve (a figure!)
print(df.groupby("SDRF_Found").size())                       # curation reach overall

# The triage slice that matters: records found ONLY by the generic term —
# no disease keyword caught them, so they're the ambiguous tail to eyeball.
only_heart = df[(df["n_keywords"] == 1) & (df["keywords"] == "heart")]
print(f"heart-only tail: {len(only_heart)}")
only_heart[["identifier", "title", "species"]].to_csv("heart_only_tail.tsv", sep="\t", index=False)

