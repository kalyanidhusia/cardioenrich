# cardioEnrich — Due-Diligence Report (10 lenses)
**Date:** 2026-10-30 · **For:** K. Dhusia & R. Bagchi
**Evidence basis:** live ProteomeCentral PROXI corpus counts measured today; PubMed sweep (PMIDs + DOIs verified); direct inspection of ProMetaDB; the running rule:cardio-v0.1 demo (12-record seed, benchmark green). Reviewer judgments are labeled as such.

---

## 1. /IdeaTriage — go/no-go scorecard

| Axis | Score | Basis |
|---|---|---|
| Impact | **4/5** | SABV + reuse mandates; sex-dimorphic HF biology is active; the audit yields quotable field-level numbers no one has |
| Feasibility | **4/5** | pxEnrich exists; rule:cardio-v0.1 ran green today; the unknowns are data-shaped (matrix availability), not method-shaped |
| Novelty | **3.5/5** ⬇ | *Downgraded today* — a 2026 wave of LLM-metadata-curation papers (see /PubMedSweep) crowds the general claim; novelty survives on four specific axes (see /NoveltyCheck) |
| Timing | **5/5** | the same wave proves the field is moving *now*; first-mover window on the cardio/assertion-graded niche is ~12 months |
| Team/fit | **5/5** | Dhusia (architecture, proven) + Bagchi (fibrosis/fibroblast biology) + AR INBRE curation pipeline |

**Verdict: GO**, conditional on (a) publishing the tool+audit paper within ~12 months, (b) measuring processed-matrix availability before promising molecular corroboration at scale (/DataRealityCheck), (c) never again framing novelty as "AI metadata extraction" — that claim is now taken.

## 2. /ResearchQuestion — sharpened and falsifiable

**Primary RQ:** *Across the public cardiovascular proteomics archive, what fraction of physiologically decisive phenotype metadata (HF subtype / stated LVEF, failing vs non-failing donor status, biological sex, etiology, model system, cell activation state) is recoverable from free text but absent from structured fields — and can an assertion-graded, deterministic-first extractor recover it with a false-assertion rate statistically indistinguishable from zero while retaining usable coverage (≥95% selective accuracy at ≥80% coverage)?*

Sub-questions, each with a falsification condition:
- **RQ-SABV:** What % of cardiac datasets state sex anywhere (structured, free text, supplement)? *Falsified if* the gap is small (<15%) — then the audit headline weakens (evidence so far: 0/10 in compact fields; eLife mouse-literature data says the gap will be large).
- **RQ-subtype:** What % of human-HF datasets are HFpEF/HFrEF-resolvable (term or stated EF)? *Falsified if* <10% are resolvable — then cross-study subtype synthesis (CS2) is impossible and the paper pivots to "the archive cannot currently support subtype meta-analysis," itself publishable.
- **RQ-trust:** Does deterministic-first + abstention dominate LLM-only extraction on the risk–coverage curve? *Falsified if* a frontier LLM matches 0-false-assertion at equal coverage — then the contribution narrows to the benchmark + derivation layer (still novel).
- **RQ-corroboration:** For datasets with deposited matrices, what fraction of recovered sex/chamber/donor claims are molecularly corroborated (RPS4Y1/DDX3Y; NPPA/MYL4 vs MYL2/MYL3; NPPB)? 

## 3. /GroundTruth — what "truth" is, in three independent layers

1. **Expert-adjudicated human labels:** dual independent student annotation → Bagchi-lab/Dhusia adjudication; per-field Cohen's κ (2 raters) with κ ≥ 0.75 release gates; frozen holdout before any rule tuning; annotator provenance (`curator:<id>`) on every label. Size for the trust claim: **≥300 record-field pairs** in the gated set (0/300 → 95% upper bound ≈ 1.2% false-assertion rate; 0/12 proves nothing).
2. **Molecular ground truth (self-validating, no human in the loop):** Y-chromosome proteins (RPS4Y1/DDX3Y/EIF1AY) vs recovered sex; atrial (NPPA, MYL4) vs ventricular (MYL2, MYL3) markers vs claimed chamber; natriuretic-peptide program vs claimed failing status — *with technical evaluability modeled* (was the marker observable at that depth?), the pxEnrich Aim-2 pattern.
3. **Publication cross-check:** linked papers (PubMed IDs are in the records) as a third source whose *disagreement with repository metadata is a result*, not noise — the conflict classes D4/D5 already found one real case (PXD047728) in a 10-record probe.

## 4. /PubMedSweep — what the literature said this morning (all via PubMed)

**The 2026 wave (closest adjacent work — none was in the earlier landscape scan):**
- **Hutton & Meyer (Cedars-Sinai), arXiv/PMC 2026, PMID 42539124** — *Omics Data Discovery Agents*: LLM agents **with MCP servers** that retrieve, re-quantify (DDA/DIA proteomics, RNA-seq) and meta-analyze published omics; five end-to-end reanalyses, correlations 0.85–0.997; self-described as a **feasibility demo, "rather than a validated benchmark."** The closest new competitor in spirit — agentic, MCP, proteomics — and the strongest proof the field is sprinting at this problem.
- **Rogic, …, Pavlidis, *Database* 2026, PMID 42483875 · [DOI](https://doi.org/10.1093/database/baag041)** — GPT-4o entity-to-ontology annotation of GEO (9,000+ Gemma-curated experiments): 77% (mouse strain) / 59% (cell line) accuracy; outputs **verbatim supporting quotes**; conclusion: human-in-the-loop, LLMs "not ready to fully replace curators." ⚠ Their regex baseline scored only **6%** — see /NoveltyCheck for why that number must be pre-empted, not ignored.
- **Sundaram, Gonçalves, Musen, *GigaScience* 2026, PMID 41773962 · [DOI](https://doi.org/10.1093/gigascience/giag019)** — GPT-4 + CEDAR templates standardizing BioSample/GEO metadata: retrieval recall 17.65% → 62.87%. Symbolic-constrained LLM = validated direction.
- **Kaier et al., *BMC Res Notes* 2026, PMID 41527010 · [DOI](https://doi.org/10.1186/s13104-026-07632-w)** — search-augmented LLM multi-repository dataset annotation; repository-grounded extraction beat article-grounded; Gemini 2.5 Pro 97.1% precision on a small validated set.

**Biology timing:** HFpEF myocardial proteomics is an active 2025–26 literature (18 PubMed hits on the focused query) — the CS2 synthesis question is live, not stale.

**Previously verified anchors retained:** SDRF (PMID 34615866), PRIDE 2025 (PMID 39494541), MetaSRA (PMID 28535296), sex-reporting bias (PMID 26939790), Universal Definition (PMID 33663906), Li 2020 (PMID 32487995), Doll 2017 (PMID 29133944), LLM-in-health evaluation (PMIDs 39405325, 37438534), Bagchi-orbit methods (PMIDs 40035765, 40258050). DOIs in the reviewer report.

## 5. /StateOfTheArt — synthesis (as of today)

The 2026 state of the art in repository-metadata recovery is: **LLM-assisted, human-in-the-loop, quote-grounded annotation** (Rogic; Kaier), **symbolically constrained LLM standardization** (Sundaram/CEDAR), **agentic end-to-end reuse feasibility demos over MCP** (Hutton & Meyer), **prospective community formats** (SDRF; PRIDE's crowd/HAMLET push, with PRIDE itself warning HAMLET outputs "should be evaluated carefully for possible incorrect values"), and **manually curated phenotype databases at partial coverage** (ProMetaDB: phenotypes/conditions over 5 repositories; 195 of 2,000 MassIVE projects re-annotated; **no assertion states, no conflict handling** — verified on its site today).
What **no one** in this set has: epistemic status on every claim (asserted/unknown/mixed/conflicting/abstained + study_focus scope), abstention as a **CI release gate**, clinical-physiology **derivation** (EF→Universal-Definition band with the preserved-EF guard; definitional-only propagation), or a cardiovascular phenotype layer at all.

## 6. /ResearchGap — final statement (pxEnrich-safe, sweep-aware)

> Public cardiovascular multi-omics archives lack harmonized physiological and cellular metadata — ejection-fraction-resolved HF subtype, failing vs non-failing donor status, biological sex, etiology, and fibroblast activation state. Existing recovery approaches either index submitted keywords without phenotype recovery (OmicsDI; repository search), curate phenotypes manually at partial coverage without epistemic grading (ProMetaDB; Expression Atlas), standardize prospectively (SDRF, CEDAR), or extract with LLMs under human review while reporting accuracy but no machine-enforced abstention (GEO/GPT-4o annotation; agentic reuse demos). None assigns assertion states with verbatim provenance, none derives clinical physiology (stated LVEF → guideline-banded subtype) under definitional-propagation discipline, and none gates releases on a measured false-assertion rate — leaving sex-dimorphic and subtype-resolved cardiovascular meta-analysis unsupported by the archive despite the data existing.

## 7. /NoveltyCheck — what survived today's sweep, what didn't

**Survives (the four defensible claims):** (1) assertion-state semantics + study_focus scope over repository metadata; (2) CI-gated false-assertion benchmark as an engineering invariant; (3) cardiovascular phenotype-derivation layer (D1–D5, definitional-only propagation); (4) the *combination* delivered as a read-only, assertion-graded evidence index.
**Narrowed/retired claims:**
- ~~"First/novel LLM-free or LLM-assisted metadata extraction over omics repositories"~~ — taken (Rogic, Sundaram, Kaier, HAMLET). Never lead with this.
- "MCP interface" — Hutton & Meyer already expose omics tooling via MCP; qualify to *"the first assertion-graded, read-only cardiovascular evidence index served over MCP,"* and cite them.
- Quote-grounding alone — Rogic's pipeline also emits verbatim supporting quotes; cardioEnrich's differentiator is that provenance is *mandatory and gated*, not advisory.
**The 6% regex problem (pre-empt it):** Rogic's regex baseline (6% on mouse strains) will be quoted against any "deterministic-first" pitch. The answer: that was *open-vocabulary entity linking* (thousands of strain names → ontology IDs); cardioEnrich's deterministic tier does *bounded clinical field extraction* (11 closed fields with abstention), where pxEnrich's own 18-dataset preliminary comparison showed the regex tier competitive with gpt-4o-mini under abstention-aware scoring. Put that contrast in one paragraph of Related Work before a reviewer writes it for you.
**Crowding risk: HIGH and rising.** Four relevant papers in one year. Mitigation = speed (P1 submitted ≤ mid-2027) + the niche nobody is in (cardio physiology + epistemic gating) + benchmarking *their* systems (HAMLET and a Rogic-style GPT-4o pipeline as compared baselines turns competitors into table rows).

## 8. /DataAvailability — measured today (ProteomeCentral PROXI compact search, the exact endpoint pxEnrich ingests from)

| Keyword | n_available_rows (2026-10-30) |
|---|---|
| breast cancer *(calibration)* | **308** (pxEnrich seed recorded 307 on 2026-10-11 — endpoint behavior confirmed stable) |
| heart | **193** |
| heart failure | **36** |
| cardiac | **24** |
| myocardium | **24** |
| cardiomyopathy | **22** |
| **myocardial** | **0** ⚠ |

Findings: (1) **PROXI keyword search has no stemming and narrow field coverage** — "myocardial" returns zero while "myocardium" returns 24; single-keyword discovery is badly lossy, so ingest must union a full vocabulary *and* add PRIDE's own full-text search (which indexes descriptions). (2) The PROXI-visible cardio corpus is the **same order of magnitude as pxEnrich's breast-cancer corpus** (union plausibly ~250–450 pre-dedup; PRIDE full-text likely pushes the true cardio-vocabulary corpus into the high hundreds) — big enough to matter, small enough to benchmark and student-curate. The exact deduplicated count stays the known ~1-hour `pridepy` task on a network-enabled machine, but these are hard, quotable lower bounds. (3) GEO expansion remains staged — don't let its (much larger) counts into year-1 commitments.

## 9. /DataRealityCheck — the uncomfortable specifics

1. **Processed-matrix availability is the single biggest unmeasured dependency.** CS1/CS3 molecular corroboration needs deposited abundance tables; a large share of PRIDE submissions are raw-files-only ("partial" submissions). **Kill-criterion test (≤2 weeks, on her machine):** for the cardiac corpus, count datasets with parseable processed matrices. If <20%, corroboration becomes a sub-study and re-quantification (heavy; cf. Hutton & Meyer's containerized pipelines) moves to a later aim — plan text should already say so.
2. **Compact fields ≠ the archive.** Today's "sex stated in 0/10" is a *compact-field* number; descriptions and supplements will raise recovery. The audit must therefore report the gap **per evidence stratum** (structured field / description / supplement / publication) — which is also the more interesting figure.
3. **Supplementary PDFs are where sex and EF hide** — PDF table extraction is its own error source; scope it as Tier-2 (LLM-candidate + abstention gate), never Tier-1.
4. **API fragility observed today:** EBI PRIDE API rate-limited quickly; PROXI per-dataset JSON truncates on file-heavy records (two records unreadable this way). Ingest needs retry/backoff and the bulk routes pxEnrich already has; snapshot-and-version everything (already the design).
5. **Student throughput math (don't hand-wave it):** 500 studies × 11 fields × 2 annotators ≈ 11,000 judgments; at ~3 min each ≈ **550 person-hours**. A 10-student cohort at 3 h/week covers ~450 h/semester → **scope the gold set to ~300 studies or plan two semesters**; the κ-per-round curve doubles as the training-outcome metric.
6. **Repository drift:** counts, records, and even keyword semantics change (308 vs 307 in 19 days); every published number must carry its retrieval date (already the seed-file convention).

## 10. /RealityCheck — brutal mode

- **Single-maintainer risk is the project's biggest structural weakness.** Kalyani is the architecture; her bandwidth spans many active projects. Mitigations that reviewers accept: student-maintainable rule files (YAML-ish lexicons), CI that strangers can run, a named co-maintainer in the PUI team, and the SDRF-emission path so value persists even if the service stops.
- **"PRIDE will eat this":** partially true and fine — PRIDE's own 2025 position is prospective SDRF + crowd + beta HAMLET with an accuracy caveat. The durable position is *complementary and upstream-feeding*: benchmark HAMLET, emit validator-passing SDRF back, and the worst case (PRIDE adopts the approach) is the best case for impact.
- **"A frontier LLM makes this trivial":** then it becomes cardioEnrich's Tier-2 engine and must beat the risk–coverage curve on the frozen benchmark — the benchmark and derivation rules are the moat, not the extractor. This is also why the benchmark paper must come out before the moat is generic.
- **AHA IPA discipline:** everything measured today (counts, 0/10 sex, the PXD047728 conflict) is usable in the pre-proposal only as *corpus description*, never as analyzed preliminary results; it is, however, exactly the preliminary data NLM PAR-25-131 wants.
- **The two decisions still gating v0.2 are human, not technical:** Bagchi's primary subtype axis and the student cohort. Until the first is settled, CS2 vs fibroblast-state work can't be prioritized.
- **Two-week kill-criteria list:** (i) processed-matrix fraction in the cardiac corpus; (ii) deduplicated cardio-vocabulary corpus count via PRIDE full-text; (iii) sex-recovery rate on 50 full records (descriptions included) — if sex is actually stated in >85% of full records, retire the SABV headline before a reviewer does.

---
**Net:** GO. The idea survived contact with the evidence, but 2026 changed the battlefield: the generic claim is gone, the specific claim (assertion-graded, physiology-deriving, CI-gated cardiovascular evidence) is intact and empty of competitors, and the clock is now part of the strategy.

*PubMed attribution: literature facts above are based on articles retrieved from PubMed; DOIs linked inline here or in the companion reviewer report. Web sources: [ProMetaDB](https://prometadb.igib.res.in/prometadb), [OmicsDI docs](https://omicsdi.readthedocs.io/en/latest/introduction.html), [PRIDE/ProteomeCentral PROXI API](https://proteomecentral.proteomexchange.org/api/proxi/v0.1/ui/).*
