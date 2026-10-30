# cardioEnrich — Evidence Map, Red Team, Go/No-Go, Paper & Proposal Plan
**Date:** 2026-10-30 · **For:** K. Dhusia & R. Bagchi
**Closes the series:** `RULES_DIFF` (method) → `REVIEWER_EVALUATION` (peer-review lens) → `DUE_DILIGENCE` (market/data) → `FEASIBILITY_EXECUTION` (pilot, stats, kill criteria) → **this document** (synthesis → decision → writing plan).

---

## 1. /EvidenceMap — every core claim, its evidence, its status

| # | Claim | Evidence today | Status |
|---|---|---|---|
| C1 | The architecture works on cardiovascular metadata | rule:cardio-v0.1 running; 12-record demo; all 5 assertion states fired on real records | ✅ **proven (demo scale)** |
| C2 | The trust gate is mechanical, not rhetorical | sabotage ablation: banned rule re-enabled → 2 FAs caught by name → CI exit 1 | ✅ **proven by sabotage** |
| C3 | Zero false assertions, quantified | 0/32 (bound ≤ 8.9%) — author-written expectations | ⚠ **regression-grade**; needs independent 300-pair gold (bound ≤ 0.99%) |
| C4 | Real conflicts exist in the wild | PXD047728 (species=Mus, keyword "human") found in a 10-record probe | ✅ proven (n=1; archive-wide rate pending) |
| C5 | The SABV gap is large | 0/10 sex in compact fields; eLife mouse-literature precedent (PMID 26939790) | ⚠ **compact-field only**; K3 test on full records decides the headline |
| C6 | The cardio corpus is tractable and real | live PROXI counts (heart 193, HF 36, CM 22; breast-ca calibration 308 vs 307) | ✅ lower bounds measured; K1 dedup count pending |
| C7 | Keyword discovery is insufficient | "myocardial" = 0 hits (no stemming) | ✅ **falsified the naive approach** — vocabulary-union + full-text mandated |
| C8 | Only definitional propagation is safe | PXD018678 donor-control counter-example; D2 codified; ablation demonstrates the failure | ✅ proven |
| C9 | Niche is unoccupied | 2026 sweep: 4 adjacent LLM-curation works, HAMLET, MetaSRA, ProMetaDB — none with assertion states/CI gate/physiology derivation | ✅ verified **today**; decays ~monthly |
| C10 | Molecular self-validation is possible (sex/chamber/failing markers) | design only | ❓ **unproven**; gated on K2 (matrix availability) |
| C11 | Students can produce evidence-grade gold | pxEnrich precedent (Harding cohort); κ protocol defined | ⚠ precedented, not yet measured (K5) |
| C12 | Abstention preserves useful coverage | 59.4% coverage @ 100% selective accuracy on compact fields | ⚠ compact-field only; K6 on full records decides |

**Reading:** 6 proven, 4 pending on the two-week pilot (K1–K6), 1 decaying asset (C9 — the clock), 1 design-only (C10). Nothing is disproven; one naive assumption (C7) was killed and replaced, which is what diligence is for.

## 2. /ValidationPlan — the five-layer pyramid (each layer independent of the one below)

1. **Mechanical** — unit tests (D1–D5) + CI gate + **standing ablation suite** (CS0): every guard sabotaged on purpose each release; a guard whose removal changes nothing is dead code or an untested claim. *Status: running.*
2. **Human (internal)** — 25-record mini-gold, 2 annotators, adjudication, per-field κ (screening). *Pilot week 2.*
3. **Human (independent)** — semester-scale ≥300-pair gold by the student cohort who never saw system output pre-labeling; frozen holdout; blind 10% expert re-audit. *Semester 1.*
4. **Molecular (no humans anywhere)** — RPS4Y1/DDX3Y vs recovered sex; NPPA/MYL4 vs MYL2/MYL3 vs claimed chamber; NPPB program vs claimed failing — with technical-evaluability denominators. *Gated on K2.*
5. **Utility (the layer the other docs missed)** — Bagchi-lab members pose ~10 real research questions through the MCP/web interface; score answer usefulness, provenance-check time, and trust calibration (did users double-check abstentions less than assertions?). Accuracy without utility doesn't fund R01s; this is the layer that produces quotable PI testimony and the TPA narrative. *Post-MVP.*

## 3. /RedTeam — attacks not yet raised in prior docs, with counters

- **"36 heart-failure datasets? The corpus is trivial."** The sharpest attack available. Counters: (a) 36 is a *no-stemming keyword lower bound* — full-text union is the real number (K1), (b) each record is a human-heart cohort: dataset-count understates sample-count and acquisition cost (quote total samples/files, not just datasets), (c) pxEnrich's validated scale is the same order (308) — the method is sized for exactly this regime, and (d) the architecture ports to the full 60k-archive once the cardio beachhead proves it. If K1 < 150, concede scope and multi-repository-union *before* a reviewer forces it.
- **"Assertion states are a UI skin over confidence thresholds."** Counter: states are *categorical epistemics with distinct evidence requirements* (conflicting requires two contradicting spans; mixed requires enumerated groups; abstained-at-study_focus requires a topic match without a status claim) — thresholding a scalar cannot produce them, and the ablation shows removing one state-rule creates named false assertions.
- **"Your derivation rules and your gold labels share a codebook — definition leakage."** Partially valid and must be conceded smartly: for *derived* fields (hf_subtype from EF), gold and system share the Universal Definition by design — the test there is extraction + arithmetic fidelity, not concept discovery. The leakage-free tests are the stated-term fields and layer-4 molecular validation. Say this in Limitations first.
- **"You'll be scooped by HAMLET/PRIDE or a frontier model before the paper lands."** Counter is strategic, already adopted: benchmark them as baselines, emit SDRF upstream, publish P1 ≤ mid-2027. Verify this week that HAMLET's agentic SDRFs are downloadable per accession (ProteomeCentral lists them) so the baseline is practical.
- **"Inferring sex the submitters didn't state — is that OK?"** Yes at cohort level over public de-identified data, but write it down: report dataset-level sex *composition*, never per-patient re-identification claims; cite the public-data scope; get a UAMS **non-human-subjects determination** on file (one email, big grant insurance).
- **"Undergrads as cheap annotation labor."** Optics attack with an easy win: graded, credited coursework (the existing pxEnrich assignment), CRediT-taxonomy authorship policy published in the repo, κ-growth reported as a *learning outcome* — the training arm is the point, not a cost dodge.
- **Compliance nits that bite late:** EBI/PRIDE API rate-limits for bulk ingest (observed today — throttle + bulk endpoints), repository metadata reuse terms (PRIDE metadata is openly licensed — cite the exact license string in the repo), and Zenodo DOIs for every published snapshot so counts are citable.

## 4. /WhatAmIMissing — genuinely new items (not in the four prior docs)

1. **IRB/non-human-subjects determination letter** (above) — cheap now, painful later.
2. **Metadata license audit** — one paragraph in DATA_PROVENANCE naming each repository's reuse terms.
3. **Student authorship & credit policy** (CRediT) committed to the repo before the cohort starts — prevents end-of-semester disputes and reads well in training grants.
4. **The SDRF give-back channel exists already**: ProteomeCentral's "curated" SDRFs come from the community BigBio GitHub — cardioEnrich's validated outputs have a ready submission path. That converts "emit SDRF" from aspiration to a named mechanism (and a deliverable: N corrected SDRFs merged upstream).
5. **Language bias**: iProX/jPOST records can carry non-English or bilingual free text; rule:cardio-v0.1 is English-only — name it as a limitation and a Tier-2 task, don't let a reviewer find it.
6. **Negative-control field**: run the *breast-cancer* vocabulary over the cardiac corpus (and vice versa) as a contamination/specificity check — a free QC figure and a cute demonstration that the domain layers are truly modular.
7. **Versioned persistence**: snapshot DOIs (Zenodo) + a one-line sunset plan (static index + SDRF exports survive even if the service dies) — NAR will ask.
8. **Calendar collision**: the two-week pilot, the Dec 1 CDA check, and the Dec 9 IPA all land in a 6-week window that also contains the PI meeting — the Gantt is people, not compute.

## 5. /RealityCheck — what changed since this morning's brutal pass

Three updates, all favorable but none decisive: the gate is now *demonstrated* (sabotage run), the statistics now dictate sizes instead of adjectives (300/500), and the competitive clock got a face (four named 2026 systems to benchmark). Unchanged and still the真 risks: **matrix availability (K2) is the only item that can kill a flagship experiment**, and **single-maintainer bandwidth** is the only item that can kill the project. Everything else is writing.

## 6. /GoNoGo — the decision, structured

| Gate | Date | GO requires | Current |
|---|---|---|---|
| **G0 (today)** | 2026-10-30 | method works, niche open, pilot defined | ✅ **GO** — proceed to pilot |
| **G1 (pilot out)** | ~Nov 13 | K1 ≥ 150 dedup · K2 ≥ 20% matrices · K3 confirms a reportable gap · K5 κ ≥ 0.6 on easy fields | pending |
| **G2 (IPA submit)** | Dec 9, 3 p.m. CT | G1 passed in any branch (even K-tripped branches are fundable — the *negative-result framings are pre-written*) + Bagchi membership/UAMS sign-off | pending human steps |
| **G3 (NLM PAR-25-131)** | Jan 15, 2027 | pilot numbers as preliminary data; mini-gold FA bound stated | pending |

Note the asymmetry that makes this a robust GO: **every kill criterion has a fundable fallback branch** (descoped corpus, corroboration sub-study, subtype-impossibility finding). The only true no-go combination is K1 *and* K2 *and* K3 all tripping — jointly unlikely and knowable in two weeks.

## 7. /PaperStory — P1 narrative arc

**Working titles:** "cardioEnrich: assertion-graded recovery of cardiovascular phenotypes from public proteomics" · alt: "What the archive won't tell you: a trust-gated audit of phenotype metadata in public cardiac proteomics."
**Arc (section beats):**
1. *Hook (Intro):* a researcher asks a simple question — "which public datasets compare HFpEF and HFrEF myocardium in women?" — and today no system can answer it, not because the data don't exist but because the phenotypes live in free text; the 2026 LLM-curation wave extracts but does not *grade*.
2. *Idea:* epistemic status as a first-class output; only definitional propagation; abstention as a release gate.
3. *System:* the tiered engine, 11 fields, D1–D5; one paragraph of Related Work pre-empting the "regex scored 6%" comparison (entity-linking ≠ bounded field extraction).
4. *The audit (the headline):* per-field, per-stratum recovery and gap percentages; the SABV number; the conflict census.
5. *The trust result:* FA 0/N with the exact bound; risk–coverage curves vs HAMLET and an LLM-only baseline; **the sabotage figure** — the memorable image reviewers retell.
6. *Corroboration vignette:* one claim-vs-matrix story (chamber or sex) told end-to-end with provenance.
7. *Limitations first-person:* codebook leakage on derived fields, English-only, compact-vs-full denominators, corpus date-stamping.
8. *Close:* validated SDRF flowing back upstream via the existing community channel — the archive gets better because the tool existed.
**P2 teaser (separate paper):** the sex-stratified cross-study HF reanalysis P1 makes possible.

## 8. /FigurePlan — P1 figures, panel by panel

- **Fig 1 — The epistemic engine.** (a) architecture: repositories → deterministic tier → gated LLM tier → assertion store → MCP/web; (b) the five states + study_focus scope with one real evidence-card each; (c) D1 EF-banding schematic with the preserved-EF guard.
- **Fig 2 — Corpus & the gap.** (a) PRISMA-style flow with dated counts; (b) per-field recovery by evidence stratum (structured / description / supplement), sex and hf_subtype highlighted; (c) the conflict census bar (D4/D5 classes, with PXD047728 called out).
- **Fig 3 — Trust, measured.** (a) benchmark table across systems (rule-tier, +open-weight, +frontier, HAMLET, LLM-only), per-field F1 + FA bounds; (b) risk–coverage curves with AURC; (c) κ-per-field of the gold set (the benchmark's own credentials).
- **Fig 4 — Sabotage.** Each guard ablated → named false assertions appear → CI exit 1; a before/after assertion-graph panel (the reified-evidence figure, cardio edition).
- **Fig 5 — Corroboration vignette.** Claimed phenotype → evidence span → deposited-matrix marker panel → verdict (corroborated/contradicted/insufficient), one real accession end-to-end.
- **Supplement:** full lexicons (rule:cardio-vX diff), codebook, annotator κ by round (the training-outcome curve), negative-control (cross-domain vocabulary) specificity check, API/ingest QC stats.

## 9. /Proposal — one-page skeletons (drop-in drafts)

### 9a. AHA IPA pre-proposal skeleton (blinded; ≤50 lines; **no names, no tool names, no URLs, no preliminary results**)
> **Problem.** Public cardiac proteomics holds hundreds of human and model-system datasets, but the phenotypes that make them reusable — ejection-fraction-defined heart-failure subtype, failing vs non-failing donor status, biological sex, etiology, cell activation state — exist mainly as free text, unqueryable and unaudited. Sex, mandated as a biological variable, is frequently unstated; subtype-resolved synthesis of HFpEF versus HFrEF biology across studies is currently impossible by construction.
> **Paradigm.** Where current AI extracts fluently, we propose extraction that *knows what it does not know*: every recovered phenotype carries an epistemic state (asserted, unknown, mixed, conflicting, abstained), a verbatim evidence span, and a rule version; only definitional clinical derivations are permitted (a stated ejection fraction maps to guideline-banded subtype; a disease mention never implies a failing cohort); and no system version is released while a curated benchmark detects a single unsupported assertion. Trustworthiness becomes an engineering invariant rather than a promise — inverting the generative-AI paradigm.
> **Aims.** (1) A cardiovascular phenotype layer with physiological derivation rules and a dual-annotated, expert-adjudicated gold standard with chance-corrected agreement gates. (2) An archive-wide audit quantifying, per phenotype and evidence stratum, what the public cardiac archive states, omits, and contradicts — including the first measured sex-reporting gap for cardiac proteomics. (3) An open, provenance-complete evidence index returning community-standard sample annotations to the archive.
> **Impact.** Enables subtype- and sex-resolved reuse of existing cardiac data; the team has previously built and benchmarked this architecture in another disease domain (technique competency; no results included per program rules).

### 9b. NLM PAR-25-131 Specific Aims skeleton (preliminary data *wanted* — the inverse document)
- **Significance:** manual curation cannot scale (the NOFO's own language); the measured gap numbers (K1–K3 pilot) + eLife sex-bias precedent.
- **Innovation:** assertion-state semantics; CI-gated FA bound (0/N exact); definitional-propagation discipline; sabotage-verified gating (include the ablation result as preliminary data).
- **Aim 1:** corpus-scale assertion-graded extraction (deterministic + gated-LLM tiers), benchmarked vs HAMLET and LLM-only baselines on a ≥300-pair independent gold set (κ-gated).
- **Aim 2:** the cardiovascular metadata audit + molecular corroboration layer (matrix-gated, per K2 branch).
- **Aim 3:** curation-at-scale training pipeline (dual-annotation protocol, κ-as-learning-outcome) + SDRF give-back via the community channel; MPI structure available under PAR-26-040 if preferred.
- **Preliminary data slots:** pxEnrich benchmark; today's demo + ablation; pilot K1–K3 numbers; mini-gold κ.

---
**Net:** GO at G0; the project's fate for the next six weeks is four numbers, two humans (PI meeting, student cohort), and one deadline — and both paper and proposals are now outlined down to the figure panels, so the pilot's outputs drop into prepared slots instead of starting blank pages.
