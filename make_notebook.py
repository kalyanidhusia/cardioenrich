"""Generate cardioenrich_demo.ipynb (dev helper; not part of the product)."""
import json

cells = []


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": src})


def code(src):
    cells.append({"cell_type": "code", "metadata": {}, "source": src,
                  "outputs": [], "execution_count": None})


md("""# cardioEnrich demo — `rule:cardio-v0.1`

Deterministic cardiovascular evidence extraction over real ProteomeXchange
records — the domain-layer port of **pxEnrich**. Runs fully offline on the
bundled seed snapshot; the engine is stdlib-only (pandas is used here only to
display tables).

The rule diff against pxEnrich `rule:v0.1` is in `docs/RULES_DIFF.md`.
Non-diagnostic research-metadata tool.""")

code("""import json
import pandas as pd

from cardioenrich.models import DatasetRecord
from cardioenrich.extraction import RULE_VERSION, enrich_record

with open("data/seed/cardio_seed_datasets.json", encoding="utf-8") as f:
    payload = json.load(f)

allowed = set(DatasetRecord.__dataclass_fields__)
records = [enrich_record(DatasetRecord(**{k: v for k, v in d.items() if k in allowed}))
           for d in payload["datasets"]]
print(RULE_VERSION, "—", len(records), "records "
      f"({sum(r.synthetic for r in records)} synthetic, flagged)")
print("Snapshot retrieved:", payload["retrieved"])""")

md("""## 1. Every field gets an answer — and a non-answer is an answer

One row per (record × field). `unknown`, `abstained`, `mixed`, and
`conflicting` are first-class statuses: the engine never confuses
*we did not look* with *we looked and found nothing*, and never papers over a
disagreement.""")

code("""rows = [a.to_dict() for r in records for a in r.assertions]
df = pd.DataFrame(rows)[["dataset_accession", "field", "status", "value",
                         "evidence_text", "scope", "note"]]
df.status.value_counts().to_frame("count")""")

code("""# All non-unknown findings, with their evidence snippets:
pd.set_option("display.max_colwidth", 90)
df[df.status != "unknown"][["dataset_accession", "field", "status", "value",
                            "evidence_text"]].reset_index(drop=True)""")

md("""## 2. The derivation rules in action (D1–D5)

**D1** — a stated LVEF is banded by the 2021 Universal Definition
(HFrEF ≤40 %, HFmrEF 41–49 %, HFpEF ≥50 %; named simplification).
**D4** — when the stated term and the stated EF disagree, the answer is
`conflicting`, with both evidences attached — never a silent resolution.""")

code("""for acc, fld in (("CARDIO-DEMO-0001", "hf_subtype"),
                 ("CARDIO-DEMO-0002", "hf_subtype"),
                 ("PXD047728", "organism_context")):
    rec = next(r for r in records if r.accession == acc)
    a = next(x for x in rec.assertions if x.field == fld)
    print(f"— {acc}" + ("  [SYNTHETIC]" if rec.synthetic else "  [real record]"))
    print(f"  {a.field}: {a.status.value.upper()}  value={a.value!r}")
    print(f"  evidence: {a.evidence_text}")
    print(f"  note: {a.note}")
    print()""")

md("""## 3. The rule that is deliberately *absent*

pxEnrich's TNBC → ER−/PR−/HER2− propagation is **definitional**. The tempting
cardio analogue — "cardiomyopathy study ⟹ failing cohort" — is only
**epidemiological**: PXD018678 names ICM and DCM in its title yet contains
age-matched donor controls. rule D2 therefore bans that propagation, and the
engine correctly returns `unknown` with the reason attached:""")

code("""rec = next(r for r in records if r.accession == "PXD018678")
a = next(x for x in rec.assertions if x.field == "donor_status")
print("PXD018678 donor_status →", a.status.value)
print(a.note)""")

md("""## 4. A quantified metadata gap, pxEnrich-style

pxEnrich's headline preliminary number was the subtype gap (recoverable in
32.4 % of free text, structured in 0.3 %). The cardio twin on this 10-record
real slice: **sex is stated in 0/10 compact records** — the SABV gap both
Bagchi-flagged papers stratify on.""")

code("""real = df[~df.dataset_accession.str.startswith("CARDIO-DEMO")]
sex = real[real.field == "sex_context"]
print(f"sex_context unknown in {int((sex.status == 'unknown').sum())} / {len(sex)} real records")""")

md("""## 5. The benchmark gate

Same harness, metrics, and CI contract as pxEnrich: **any false assertion
fails the build** (exit ≠ 0). 32 curated expectations over this seed:""")

code("""import subprocess, sys
p = subprocess.run([sys.executable, "tests/run_benchmark.py"],
                   capture_output=True, text=True)
report = json.loads(p.stdout)
print(json.dumps({k: v for k, v in report.items() if k != "failures"}, indent=2))
print("exit status:", p.returncode, "(0 = CI green)")""")

md("""## Next (v0.2 — after the Bagchi meeting)

1. Her **primary subtype axis**: EF bands (D1) vs failing/non-failing (D2) vs
   fibroblast activation state (`cell_state_context`) — all three run today.
2. Live ingest on a network-enabled machine (pxEnrich's `pridepy`/PROXI path)
   to add verbatim descriptions and the quotable corpus count.
3. Port the unchanged layers: FTS5 index, Flask API, MCP server, student
   benchmark-curation assignment (cardio accessions, same schema).""")

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python",
                       "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
with open("cardioenrich_demo.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("wrote cardioenrich_demo.ipynb")
