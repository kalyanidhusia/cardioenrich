"""cardioEnrich demo runner — rule:cardio-v0.1 over the seed snapshot.

Usage:
    python demo.py                 # evidence cards to stdout + reports to out/
    python demo.py --json          # raw assertions as JSON to stdout

Deterministic, offline, stdlib-only. No LLM anywhere in this path.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cardioenrich.models import DatasetRecord  # noqa: E402
from cardioenrich.extraction import RULE_VERSION, enrich_record  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, "data", "seed", "cardio_seed_datasets.json")
OUT = os.path.join(HERE, "out")

STATUS_ICON = {
    "asserted": "✔ asserted",
    "unknown": "· unknown",
    "mixed": "◆ mixed",
    "conflicting": "⚠ CONFLICTING",
    "abstained": "○ abstained",
    "not_evaluable": "– not evaluable",
}


def load_records() -> list[DatasetRecord]:
    with open(SEED, encoding="utf-8") as f:
        payload = json.load(f)
    records = []
    allowed = {f.name for f in DatasetRecord.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    for d in payload["datasets"]:
        records.append(DatasetRecord(**{k: v for k, v in d.items() if k in allowed}))
    return records


def main() -> int:
    records = [enrich_record(r) for r in load_records()]
    as_json = "--json" in sys.argv

    if as_json:
        print(json.dumps([r.to_dict() for r in records], indent=2, ensure_ascii=False))
        return 0

    os.makedirs(OUT, exist_ok=True)
    jsonl_path = os.path.join(OUT, "assertions.jsonl")
    md_path = os.path.join(OUT, "evidence_report.md")

    lines = [f"# cardioEnrich demo — {RULE_VERSION} over "
             f"{len(records)} seed records",
             "",
             "Every value below carries its own evidence snippet, source, scope,",
             "and extractor version. Non-answers (`unknown`, `abstained`, `mixed`,",
             "`conflicting`) are first-class outputs, not failures.",
             ""]
    counts: Counter = Counter()

    with open(jsonl_path, "w", encoding="utf-8") as jf:
        for rec in records:
            tag = "  **[SYNTHETIC — demo only]**" if rec.synthetic else ""
            lines.append(f"## {rec.accession}{tag}")
            lines.append(f"*{rec.title}*  ")
            lines.append(f"Repository: {rec.repository} · Species: {rec.species} · "
                         f"Announced: {rec.announce_date}")
            lines.append("")
            lines.append("| field | status | value | evidence | note |")
            lines.append("|---|---|---|---|---|")
            for a in rec.assertions:
                counts[a.status.value] += 1
                jf.write(json.dumps(a.to_dict(), ensure_ascii=False) + "\n")
                ev = (a.evidence_text or "—").replace("|", "\\|").replace("\n", " ")
                note = (a.note or "—").replace("|", "\\|").replace("\n", " ")
                val = (a.value or "—").replace("|", "\\|")
                lines.append(f"| {a.field} | {STATUS_ICON[a.status.value]} | {val} "
                             f"| {ev} | {note} |")
            lines.append("")

    lines.append("## Assertion-state tally (all records × all fields)")
    lines.append("")
    for k in ("asserted", "mixed", "conflicting", "abstained", "unknown"):
        lines.append(f"- {k}: **{counts.get(k, 0)}**")
    lines.append("")
    lines.append(f"Extractor: `{RULE_VERSION}` · deterministic · no LLM in this path · "
                 "non-diagnostic research metadata tool.")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Console summary
    print(f"{RULE_VERSION}: enriched {len(records)} records "
          f"({sum(1 for r in records if r.synthetic)} synthetic).")
    for k in ("asserted", "mixed", "conflicting", "abstained", "unknown"):
        print(f"  {STATUS_ICON[k]:<16} {counts.get(k, 0)}")
    print(f"\nWrote {jsonl_path}\nWrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
