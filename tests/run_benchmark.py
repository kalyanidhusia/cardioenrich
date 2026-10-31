"""Benchmark / regression harness for cardioEnrich extraction.

Adapted from pxEnrich tests/run_benchmark.py with ONE change: records are
loaded from the seed snapshot and enriched in memory (the demo repo carries
no SQLite index). Scoring logic, error taxonomy, and the CI gate are
IDENTICAL — a shared harness is part of the architecture contract.

Usage:
    python tests/run_benchmark.py                          # example records
    python tests/run_benchmark.py path/to/benchmark.jsonl  # expert benchmark
    python tests/run_benchmark.py --include-holdout        # final eval only

Drop the student-curated expert benchmark into
tests/benchmark/benchmark_records.jsonl (same schema, see
cardio_benchmark_schema.json) and it is picked up automatically. Records with
"set": "holdout" are skipped unless --include-holdout is passed — freeze the
holdout BEFORE tuning rules.

Exit status: non-zero when any false assertion occurs. A confident answer
without support is a defect; CI blocks on it.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cardioenrich.models import DatasetRecord  # noqa: E402
from cardioenrich.extraction import enrich_record  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(os.path.dirname(HERE), "data", "seed", "cardio_seed_datasets.json")
DEFAULT_FILES = [
    os.path.join(HERE, "benchmark", "benchmark_records.jsonl"),  # expert set, if present
    os.path.join(HERE, "benchmark", "example_records.jsonl"),
]

ABSTAIN_STATES = {"unknown", "abstained", "conflicting", "not_evaluable", "mixed"}


def load_expectations(paths: list[str]) -> list[dict]:
    recs = []
    for p in paths:
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        recs.append(json.loads(line))
            break  # first existing file wins (expert set shadows examples)
    return recs


def load_enriched_index() -> dict:
    with open(SEED, encoding="utf-8") as f:
        payload = json.load(f)
    allowed = {f.name for f in DatasetRecord.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    index = {}
    for d in payload["datasets"]:
        rec = DatasetRecord(**{k: v for k, v in d.items() if k in allowed})
        index[rec.accession] = enrich_record(rec)
    return index


def score(records: list[dict], include_holdout: bool = False) -> dict:
    index = load_enriched_index()
    results = []
    for exp in records:
        if exp.get("set") == "holdout" and not include_holdout:
            continue
        rec = index.get(exp["accession"])
        if rec is None:
            results.append({**exp, "outcome": "dataset_missing"})
            continue
        actual = next((a for a in rec.assertions if a.field == exp["field"]), None)
        if actual is None:
            results.append({**exp, "outcome": "field_missing"})
            continue

        a_status = actual.status.value
        e_status = exp["expected_status"]
        outcome = "pass"

        if e_status in ABSTAIN_STATES and a_status == "asserted":
            outcome = "false_assertion"
        elif e_status == "asserted" and a_status in (ABSTAIN_STATES - {"mixed"}):
            outcome = "missed_value"
        elif e_status == "asserted" and a_status == "asserted":
            ev = (exp.get("expected_value") or "").lower()
            av = (actual.value or "").lower()
            match_mode = exp.get("value_match", "contains")
            ok = (ev == av) if match_mode == "exact" else (ev in av)
            if not ok:
                outcome = "scope_error"
        elif e_status != a_status:
            outcome = "scope_error" if a_status != "asserted" else "false_assertion"

        results.append({**exp, "actual_status": a_status,
                        "actual_value": actual.value, "outcome": outcome})

    scored = [r for r in results if r["outcome"] not in
              ("dataset_missing", "field_missing")]
    n = len(scored) or 1
    passes = sum(1 for r in scored if r["outcome"] == "pass")
    fa = sum(1 for r in scored if r["outcome"] == "false_assertion")
    mv = sum(1 for r in scored if r["outcome"] == "missed_value")
    se = sum(1 for r in scored if r["outcome"] == "scope_error")
    abst_expected = [r for r in scored
                     if r["expected_status"] in ("abstained", "unknown", "conflicting")]
    abst_correct = sum(1 for r in abst_expected
                       if r.get("actual_status") == r["expected_status"])

    return {
        "n_scored": len(scored),
        "n_skipped": len(results) - len(scored),
        "accuracy": round(passes / n, 3),
        "false_assertion_rate": round(fa / n, 3),
        "missed_value_rate": round(mv / n, 3),
        "scope_error_rate": round(se / n, 3),
        "correct_abstention_rate": round(
            abst_correct / len(abst_expected), 3) if abst_expected else None,
        "failures": [r for r in results if r["outcome"] != "pass"],
    }


# def main() -> int:
#     args = [a for a in sys.argv[1:]]
#     include_holdout = "--include-holdout" in args
#     paths = [a for a in args if not a.startswith("--")] or DEFAULT_FILES
#     records = load_expectations(paths if isinstance(paths, list) else [paths])
#     if not records:
#         print("No benchmark records found.", file=sys.stderr)
#         return 2
#     report = score(records, include_holdout)
#     print(json.dumps(report, indent=2, ensure_ascii=False))
#     blocking_outcomes = {
#         "false_assertion",
#         "dataset_missing",
#         "field_missing",
#         "scope_error",
#     }

#     has_blocker = any(
#         failure["outcome"] in blocking_outcomes
#         for failure in report["failures"]
#     )

#     return 1 if report["n_scored"] == 0 or has_blocker else 0

def main() -> int:
    args = sys.argv[1:]

    include_holdout = "--include-holdout" in args

    paths = [
        arg for arg in args
        if not arg.startswith("--")
    ] or DEFAULT_FILES

    records = load_expectations(paths)

    if not records:
        print("No benchmark records found.", file=sys.stderr)
        return 2

    report = score(records, include_holdout)

    print(json.dumps(report, indent=2, ensure_ascii=False))

    blocking_outcomes = {
        "false_assertion",
        "dataset_missing",
        "field_missing",
        "scope_error",
    }

    has_blocker = any(
        failure.get("outcome") in blocking_outcomes
        for failure in report["failures"]
    )

    if report["n_scored"] == 0:
        print(
            "ERROR: No benchmark expectations were scored.",
            file=sys.stderr,
        )
        return 2

    return 1 if has_blocker else 0


if __name__ == "__main__":
    raise SystemExit(main())

if __name__ == "__main__":
    raise SystemExit(main())
