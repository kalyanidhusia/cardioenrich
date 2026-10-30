# cardioEnrich — Feasibility & Execution Report (10 lenses)
**Date:** 2026-10-30 · **For:** K. Dhusia & R. Bagchi
**Companions:** `RULES_DIFF.md` (the method), `REVIEWER_EVALUATION.md` (§6 experiment designs), `DUE_DILIGENCE.md` (corpus counts, competitive sweep, kill-criteria list).
**What is new here:** everything below marked **[RAN TODAY]** was actually executed in this session, not projected.

---

## 1. /FeasibilityCheck — resource-by-resource

| Resource | Status | Evidence / gap |
|---|---|---|
| Core architecture | ✅ exists | pxEnrich running; rule:cardio-v0.1 ported, 17 unit tests + 32-pair benchmark green **[RAN TODAY]** |
| Domain expertise | ✅ available, ⚠ unscheduled | Bagchi lab (fibrosis/fibroblast states); the subtype-axis meeting is still the gating human step |
| Corpus access | ✅ measured | PROXI counts taken live today (heart 193 … myocardial 0); full-text PRIDE ingest runs on her machine with the existing pxEnrich connectors |
| Descriptions / supplements | ⚠ network-gated | this environment cannot fetch long fields verbatim; her machine can (pridepy/PROXI). Blocks nothing except description-level recovery rates |
| Processed matrices (CS1/CS3) | ❓ **unmeasured** | the single biggest feasibility unknown — see /KillCriteria K2 |
| Student workforce | ✅ precedented, ⚠ throughput-bound | 6-student Harding cohort exists for pxEnrich; 550 person-hours for a 500-study gold set vs ~450 h/semester at 10×3 h/wk → scope 300 or two semesters |
| Compute | ✅ trivial | engine is stdlib; full-corpus extraction is minutes on a laptop; only re-quantification (deferred) needs HPC |
| Funding runway | ✅ mapped | AHA IPA (Dec 9) → NLM PAR-25-131 (Jan 15) → R15-via-PUI / NSF IUSE → R01 |
| Maintainer bandwidth | ⚠ | single-architect risk; mitigations in DUE_DILIGENCE §10 |

**Feasibility verdict:** nothing method-shaped blocks execution; the two open risks are *data-shaped* (matrix availability) and *calendar-shaped* (Bagchi meeting, student cohort start).

## 2. /ExperimentDesign — frozen designs (deltas to REVIEWER_EVALUATION §6)

- **CS1 (sex recovery + molecular ground truth)** — unchanged, with one addition from today's statistics: the corroboration set must report *technical evaluability* as its own denominator, and the cross-study differential-abundance step pre-registers Benjamini–Hochberg FDR ≤ 0.05 within study and random-effects pooling across studies (effect-size, not p-value, pooling).
- **CS2 (HFpEF vs HFrEF synthesis)** — add the explicit negative-result branch from RQ-subtype: if <10% of human-HF datasets are subtype-resolvable, the deliverable becomes the quantified impossibility claim.
- **CS3 (claim-vs-matrix contradiction audit)** — chamber markers (NPPA/MYL4 vs MYL2/MYL3) and NPPB-program checks, run only on the matrix-available subset measured in the pilot.
- **CS0 (new, costless, already half-done): the ablation study** — systematically re-enable each banned/guarded rule (epidemiological donor propagation; EF-without-HF-context; conflict auto-resolution) and show the benchmark catches every one. Today's first ablation **[RAN TODAY]**: re-enabling "disease term ⟹ failing" produced exactly 2 false assertions (PXD018678, PXD060431), FA-rate 0.062, **CI exit 1**. This becomes a figure: *the trust claims are mechanically enforced, demonstrated by sabotage.*

## 3. /KillCriteria — numeric, dated, owned

| # | Criterion (measure by) | Kill threshold | Consequence if tripped |
|---|---|---|---|
| K1 | Deduplicated cardio-vocabulary corpus, PRIDE full-text (wk 1) | **< 150 datasets** | descope to "HF + cardiomyopathy + I/R" core and add MassIVE/iProX union before any grant number is quoted |
| K2 | Fraction of cardiac corpus with parseable processed matrices (wk 2) | **< 20%** | CS1/CS3 corroboration becomes a sub-study on the available subset; re-quantification moves to a later aim; grant text pre-written for this branch |
| K3 | Sex stated anywhere in 50 full records (wk 2) | **> 85% stated** | retire the SABV-gap headline; pivot Significance to subtype/donor-status gaps |
| K4 | Subtype-resolvable fraction of human-HF datasets (wk 3) | **< 10%** | CS2 flips to the negative-result paper branch |
| K5 | Student κ after 2 training rounds, easy fields (sex, sample_type) | **< 0.60** | codebook redesign before scaling; do not grow the cohort into a broken protocol |
| K6 | Rule-tier coverage on full records at 0 observed FA | **< 40%** | promote Tier-2 (gated LLM candidates) from optional to core in the proposal's Approach |

## 4. /FastFalsify — cheapest tests first (cost-ordered)

| Cost | Test | Status |
|---|---|---|
| **$0, done** | Does the CI gate actually catch a bad rule? | ✅ **[RAN TODAY]** ablation caught 2/2, exit 1 |
| **$0, done** | Do all assertion states occur on real metadata? | ✅ 10 real records: asserted/mixed/conflicting/abstained/unknown all fired; 1 real conflict (PXD047728) |
| **$0, done** | Is discovery-by-keyword sufficient? | ❌ falsified — "myocardial" = 0 hits (no stemming); vocabulary-union + full-text required |
| ~1 h, her machine | K1 dedup corpus count | pending |
| ~2–4 h | K2 matrix availability over the 36 "heart failure" + 22 "cardiomyopathy" hits | pending |
| ~1 day | K3/K6 on 50 full records (descriptions in) | pending |
| ~1 wk | K5 mini-gold with 2 annotators on 25 records | pending |

## 5. /MVP — definition and exit criteria

**Already built (today):** rule:cardio-v0.1 engine, 12-record seed, benchmark harness + CI workflow, notebook, docs.
**MVP = that plus three additions, nothing else:**
1. **Full-record ingest** of the deduplicated cardio corpus (pxEnrich connectors, her machine), descriptions included;
2. **FTS5 index + the ported read-only MCP server** (both port unchanged from pxEnrich);
3. **A 50-record pilot gold set** (2 annotators + adjudication) replacing my 32 author-written expectations.

**MVP exit criteria:** corpus ingested with dated snapshot; per-field recovery rates reported by evidence stratum; FA = 0 on the pilot gold set with the 0/N bound stated; one end-to-end plain-language query answered over MCP with provenance. **Everything else (GEO, imaging links, student scale-up, web UI polish) is post-MVP.**

## 6. /PilotPlan — the two-week pilot (her machine; network available there)

| Day | Task | Output |
|---|---|---|
| 1 | Vocabulary-union discovery: PROXI union + PRIDE full-text per term; dedup by accession | **K1 number** + dated snapshot JSON |
| 2–3 | Full-record ingest (details pass) for the corpus; re-run extractor | per-field recovery by stratum (structured/description) |
| 3–4 | Matrix-availability scan (file listings: `*.txt/tsv/xlsx` processed tables) over HF+CM subsets | **K2 fraction** |
| 4–5 | 50-record manual read: sex/EF/donor stated anywhere? | **K3, K6** |
| 6–10 | Mini-gold: 25 records × 11 fields × 2 annotators (Kalyani + 1 Bagchi student), adjudicate, κ per field | **K5**; replaces author-written expectations |
| 10 | Freeze holdout (10 of 25) **before** touching rules; re-run gate | pilot FA bound (0/≈165 ⇒ ≤1.8%) |
| 11–14 | Write the pilot memo; decide K-branches; v0.2 rule diff from adjudication disagreements | go/no-go inputs for AHA/NLM text |

## 7. /PilotRun — what was actually executed **[RAN TODAY]**

- **Extraction pilot:** 12 records (10 real + 2 labeled synthetic) × 11 fields = 132 assertions; distribution 38 asserted / 3 mixed / 2 conflicting / 5 abstained / 84 unknown; every state exercised on evidence; outputs in `out/assertions.jsonl`, `out/evidence_report.md`.
- **Benchmark pilot:** 32 curated expectations → accuracy 1.0, FA 0.0, correct-abstention 1.0, exit 0; 17 unit tests on D1–D5 pass.
- **Sabotage/ablation run:** banned propagation re-enabled → FA 0.062, 2 false assertions caught by name, **exit 1** (the gate demonstrably blocks).
- **Risk–coverage probe** on the 32-pair set using rule confidences: 59.4% answer rate at **100% selective accuracy**, degrading only in coverage (37.5%) as the threshold rises to 0.85 — i.e., on compact metadata the engine already sits on the zero-risk frontier; the open question is coverage on *full* records (K6).
- **Honest scope limits:** this pilot ran on compact fields; the 32 expectations were written by the rule author over the same records, so today's numbers are **regression-grade, not evidence-grade** — the independent mini-gold in /PilotPlan is what upgrades them.

## 8. /QC — gates at every stage (status)

| Stage | Gate | Status |
|---|---|---|
| Ingest | dated snapshot; accession-level upsert; retry/backoff; truncation detection (two PROXI truncations observed today — handled by skip-and-log) | design carried from pxEnrich |
| Seed hygiene | synthetic records flagged (`synthetic: true`), excluded from corpus stats; meta-text kept out of extracted fields (`demo_note`) | ✅ implemented |
| Extraction | every `asserted` must carry evidence_text + source (unit-tested) ; rule version stamped on every assertion | ✅ implemented |
| Benchmark | frozen holdout honored; FA > 0 ⇒ exit 1 ⇒ CI blocks merge (`.github/workflows/benchmark.yml`) | ✅ implemented, sabotage-verified |
| Annotation | dual-annotate → adjudicate → per-field κ gates (≥0.75), blind 10% re-audit | protocol defined, pilot pending |
| Release | FA bound stated with N; retrieval dates on all counts; zero PII; non-diagnostic notice | convention set |

## 9. /Benchmark — the comparison the papers/grants need

**Systems to compare on the same frozen gold set:** (1) rule-tier only (deterministic); (2) rule + open-weight LLM Tier-2, abstention-gated; (3) rule + frontier LLM Tier-2; (4) **HAMLET** output where PRIDE provides it (turn the competitor into a row; PRIDE's own caveat about its accuracy becomes context); (5) a Rogic-style GPT-4o quote-grounded annotator as the LLM-only baseline.
**Metrics (per field and pooled):** precision/recall/F1 on asserted; FA rate + exact 0/N bound; missed-value rate; correct-abstention rate; scope-error rate; risk–coverage AURC; κ of the gold set itself.
**Sizing (from /StatsAudit):** release-gating set ≥ 300 record-field pairs (bound ≤ 0.994%); publication headline set ≈ 500+ (≤ 0.6%); today's 32-pair set is CI plumbing only.
**Protocol:** holdout frozen before tuning; annotators never see system outputs before labeling; benchmark JSONL schema already shared between pxEnrich and cardioEnrich (one harness, two domains — a selling point).

## 10. /StatsAudit — the numbers, computed today **[RAN TODAY]**

**Zero-event exact upper bounds (one-sided 95%, x = 0):**

| Gold-set size N | FA upper bound |
|---|---|
| 12 | 22.1% (why the demo set proves nothing) |
| 32 | 8.9% |
| 100 | 2.95% |
| **300** | **0.99%** ← minimum defensible release gate |
| 500 | 0.60% |
| 3,300 | 0.09% (what a "<0.1%" claim would require) |

**Cohen's κ precision vs N (simulation, 2 raters, 5-category field):** N=50 ⇒ ±0.15 (too wide to certify κ≥0.75); N=100 ⇒ ±0.09; **N=300 ⇒ ±0.06**; N=500 ⇒ ±0.04. So the pilot's 25-record mini-gold estimates κ coarsely (screening only); the semester-scale set certifies it.
**Risk–coverage (today's 32 pairs):** 59.4% coverage at 100% selective accuracy (conf ≥ 0), falling to 37.5% at conf ≥ 0.85 with accuracy flat — note the rule confidences are **ordinal, not calibrated**; report ECE only after Tier-2 exists, and never present 0.85 as a probability.
**Pre-registered analysis notes for CS1/CS2:** within-study BH-FDR ≤ 0.05; across-study random-effects on effect sizes with heterogeneity (I²) reported; sex-stratified contrasts declared before looking; the SABV-gap percentage reported with a Wilson interval and stratified by evidence source.
**Known statistical self-criticisms (state them before reviewers do):** author-written expectations = circularity until the independent gold set lands; compact-field recovery rates underestimate full-record recovery (never mix the two denominators); corpus counts are time-stamped moving targets (308 vs 307 in 19 days).

---
**Net:** the method is feasibility-proven at demo scale *with its safety property demonstrated by sabotage*; the remaining feasibility questions are four numbers (K1–K4) obtainable in two weeks on a network-enabled machine, and the statistics now dictate concrete benchmark sizes (300/500) instead of adjectives.
