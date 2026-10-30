# cardioEnrich — Study-Section-Style Evaluation
**Reviewer stance:** Senior bioinformatician / cardiovascular data scientist / NIH peer-review perspective (BDMA-type panel)
**Date:** 2026-10-30 · **Prepared for:** K. Dhusia (computational lead) & R. Bagchi (PI)
**Grounding:** Citations below were verified against PubMed (PMIDs + DOIs); funding-mechanism claims checked against NIH Guide notices. Where a claim is my reviewer judgment rather than a verified fact, it is labeled as such.

> ⚠ **Correction before anything else:** the proposal summary names "Dr. *Paramita* Bagchi"; every project document names **Dr. *Rushita* Bagchi (UAMS)**. Fix before this text seeds any grant or manuscript draft.

---

## 0. Overall impression (what a study section would say in the first two minutes)

**Strengths:** a genuinely under-occupied niche (assertion-state, provenance-first metadata recovery over cardiovascular repositories); a working predecessor (pxEnrich) that de-risks Approach; a benchmark design where *false assertions block releases* — reviewers reward teams that engineer against their method's failure mode; a training arm with a real PUI pipeline; direct alignment with SABV and data-reuse mandates.

**Weaknesses to fix in the writing:** (1) the phrase **"zero-hallucination constraints" is an overclaim** — no reviewer believes "zero"; claim instead *"a measured false-assertion rate, CI-gated at 0 on a frozen expert benchmark, with 95% Wilson intervals reported"*; (2) "RAG" is the wrong label for Aim 2 (see §1.1) and invites comparison to generic chatbots — the architecture is *deterministic extraction with selective prediction*, which is stronger; (3) GEO expansion in Aim 1 is scope creep for a first award — stage it; (4) the biological payoff must headline, or the panel scores it as infrastructure (see §3, §6).

**Reviewer-style scores (1 = exceptional, 9 = poor), my judgment:** Significance 3 · Innovation 2–3 · Approach 3 (2 with the fixes below) · Investigators 2 (working prior system) · Environment 2.

---

## 1. Scientific soundness & methodological rigor

### 1.1 Rule-based NLP vs hybrid LLM/symbolic — the right framing
- **Tiered hybrid is both feasible and the defensible design**, and it is what pxEnrich's own Aim 1 already benchmarks (regex baseline vs open-weight and commercial LLMs with abstention-aware metrics). Keep that three-way comparison as a *result*, not a design dilemma: Tier 1 = deterministic lexicon/regex + derivation rules over titles/descriptions/SDRF (versioned `rule:cardio-vX`, fully reproducible); Tier 2 = constrained LLM extraction over long free text and supplementary files, **emitting candidates only**, every one of which must carry a verbatim source span and pass the same assertion-state gate before indexing; Tier 3 = human adjudication queue for `conflicting`.
- **Why this beats "just use an LLM":** unverified LLM output in health contexts measurably fabricates; the current best systematic evidence base for LLM evaluation in health care (Bedi et al., *JAMA* 2025, PMID 39405325, [DOI](https://doi.org/10.1001/jama.2024.21700)) shows most evaluations don't even use real patient/record data, and foundational work (Singhal et al., *Nature* 2023, PMID 37438534, [DOI](https://doi.org/10.1038/s41586-023-06291-2)) documents the gap between fluent answers and clinician-grade reliability. Your architecture makes the LLM *optional and auditable* — say so explicitly in Approach.
- **Rename Aim 2.** It is not retrieval-augmented *generation*; it is **provenance-enforced extraction with selective prediction** (the abstention literature's framing: a risk–coverage trade-off, cf. El-Yaniv & Wiener, *JMLR* 11:1605–1641, 2010 — ML literature, not PubMed). Reviewers who know selective classification will instantly recognize the rigor; "RAG" invites "so it's a chatbot" dismissals.

### 1.2 Clinical-harmonization failure modes (name these in the Approach; each needs a rule or an abstention)
1. **Compartment confusion** — LV tissue biopsy vs explant vs isolated cardiomyocytes vs cardiac fibroblasts vs plasma/serum vs EV fractions are *different proteomes*; a single `sample_type` label on a mixed-design study is a category error. Mitigation: multi-valued sample assertions at `cohort_subset`/`sample` scope; EV-fraction flagged as a modifier (already in rule:cardio-v0.1). Chamber claims can be **quantitatively audited** where matrices are deposited (atrial markers NPPA/MYL4 vs ventricular MYL2/MYL3) — turn a failure mode into a validation experiment (§6, CS3).
2. **EF provenance and drift** — echo vs CMR vs catheterization EFs differ; EF changes over a disease course; "mean LVEF 45±12%" spans all three bands. Mitigation: band only point values; abstain on ranges/means with SDs crossing a boundary; record modality when stated; version the banding to the Universal Definition (Bozkurt et al., *J Card Fail* 2021, PMID 33663906, [DOI](https://doi.org/10.1016/j.cardfail.2021.01.022)) as a **named simplification** — reviewers accept named simplifications and punish silent ones. Note HFmrEF (41–49%) definitions churned across guideline eras; pre-2016 datasets won't use the term.
3. **"Non-failing donor" ≠ healthy** — donor hearts declined for transplant carry downtime, catecholamine storm, and comorbidity; say "non-failing" only as the field's term of art, never "normal."
4. **Study-focus vs cohort-status conflation** — "TGF-β" or "MYBPC3" as a *topic* is not a cohort phenotype; the `study_focus` scope (inherited from pxEnrich) is your defense — keep the HCM-gene→etiology inference banned (v0.1 already defers it).
5. **Definitional vs epidemiological propagation** — the single most important design rule, already encoded: HFpEF⟹HF is definitional (safe); "cardiomyopathy study ⟹ failing cohort" is epidemiological and *demonstrably false* (PXD018678 contains donor controls; Li et al., *Nat Commun* 2020, PMID 32487995, [DOI](https://doi.org/10.1038/s41467-020-16584-z)). Make this contrast a figure — it is the clearest articulation of why the method is trustworthy.
6. **Species/keyword sloppiness** — real, observed on day one (PXD047728: species = *Mus musculus*, keyword "human") → `conflicting`, curator queue. Quantify this conflict class archive-wide; it's a publishable number.
7. **Unit/dose traps** — the µg vs mg class (the Eggertsen PNAS Methods-vs-Results AngII discrepancy; PMID 40035765, [DOI](https://doi.org/10.1073/pnas.2420499122)): capture doses **verbatim**, never normalize units in v0.x.

### 1.3 Undergraduate-curated gold standard — valid *only* with this protocol
A panel will not accept "undergraduates curated it" at face value; it will accept a **measured annotation process**:
- **Dual independent annotation** of every record-field pair by ≥2 trained students, against a written codebook with decision rules and worked examples; **expert adjudication** (Bagchi lab + Dhusia) of all disagreements; adjudicated labels = gold.
- **Report chance-corrected agreement per field**: Cohen's κ (2 raters) or Fleiss' κ (>2), with targets κ ≥ 0.75 ("excellent" by conventional bands) for release-gating fields and κ reported per field (sex and sample_type will be high; etiology and hf_subtype lower — report honestly, they measure task hardness, which is itself a result).
- **Freeze a holdout split before any rule tuning** (your harness already enforces `set: holdout`), annotator-level provenance (`curator:<id>`) on every gold label, and a drift audit: expert re-adjudicates a random 10% blind.
- **Pedagogical bonus for the grant:** the κ curve across training rounds is a *learning-outcome measurement* — it serves the NSF-IUSE/AR INBRE arm as evidence, not decoration.

---

## 2. Innovation & competitive landscape (/NoveltyCheck)

| Tool / resource | What it does | What it does **not** do (cardioEnrich's gap) |
|---|---|---|
| **OmicsDI** | cross-repository dataset indexing/search | no phenotype recovery, no assertion states, no evidence spans |
| **Expression Atlas** | expert-curated, reprocessed expression sets | curation is manual and selective; transcriptome-centric; no abstention semantics |
| **PRIDE Inspector / PRIDE web** | QC + browse of individual submissions | per-dataset, not corpus-level evidence synthesis; PRIDE's own 2025 strategy is *prospective* SDRF adoption and crowd annotation (PRIDE 2025 update, *NAR*, PMID 39494541, [DOI](https://doi.org/10.1093/nar/gkae1011)) — it concedes the retrospective problem cardioEnrich attacks |
| **MassIVE** | repository + reanalysis (MSV) | same: storage/reanalysis, not phenotype evidence extraction |
| **BioDataome / recount-style resources** | uniformly processed public omics | uniform *processing*, not metadata truth; no conflict/abstention model |
| **MetaSRA** (Bernstein et al., *Bioinformatics* 2017, PMID 28535296, [DOI](https://doi.org/10.1093/bioinformatics/btx334)) | **closest prior art**: ontology-normalized SRA sample metadata via an automated pipeline | normalization without *epistemic status*: no asserted/unknown/mixed/conflicting/abstained, no verbatim evidence spans, no CI-gated false-assertion benchmark, transcriptomic |
| **SDRF-Proteomics** (Dai/Füllgrabe et al., *Nat Commun* 2021, PMID 34615866, [DOI](https://doi.org/10.1038/s41467-021-26111-3)) | the community metadata *format* | a format, prospectively adopted; cardioEnrich is the retrospective recovery engine that can *emit* validated SDRF — position as complementary, SDRF-emitting (your Aim-3 pattern) |
| Generic biomedical RAG / PRIDE's docs chatbot | fluent answers over documentation/literature | no deterministic layer, no provenance-to-snippet guarantee, no abstention gate, answers are not regression-testable |

**The four claims to put verbatim in the Introduction (the defensible novelty):**
1. First **assertion-state semantics** (asserted/unknown/mixed/conflicting/abstained, with `study_focus` scope) over repository metadata.
2. First **CI-gated false-assertion benchmark**: any confident claim without support fails the build — trustworthiness as an *engineering invariant*, not a promise.
3. First **cardiovascular phenotype-derivation layer** with definitional-only propagation (stated LVEF → Universal-Definition band, with the preserved-EF-≠-HFpEF guard).
4. A **machine-readable (MCP) read-only interface**, making the evidence index consumable by any agent while the index itself stays deterministic.

**Verify before submission** (gaps the earlier landscape scan flagged): current OmicsDI capabilities, ProMetaDB scope, and a 2025–26 bioRxiv/arXiv sweep for "LLM + PRIDE/ProteomeXchange metadata" preprints.

---

## 3. Biological & translational impact (/ResearchGap)

- **Sex-dimorphic cardiac remodeling.** The evidence that sex restructures the failing-heart proteome is direct — Li et al. found sex-specific pathway architecture in ICM/DCM myocardium (PMID 32487995, [DOI](https://doi.org/10.1038/s41467-020-16584-z)); sex-specific proteomic correlates are documented in HFpEF/coronary microvascular dysfunction (Sabbatini et al./*Eur J Heart Fail* 2022, PMID 35060248, [DOI](https://doi.org/10.1002/ejhf.2435)) and in post-MI remodeling biology (PMID 31483157, [DOI](https://doi.org/10.1080/14789450.2019.1664293)). Yet sex is unrecoverable at query time across most of the archive — in our 10-record compact-metadata probe, sex was stated in **0/10** records. No existing tool can even *count* this, let alone stratify reanalysis by it.
- **SABV compliance, quantified.** NIH's SABV policy (NOT-OD-15-102, effective 2016) requires sex as a biological variable; text-mining of 15,311 mouse studies found only ~50% reported sex/age, with **the strongest male-bias in cardiovascular disease models** (Flórez-Vargas et al., *eLife* 2016, PMID 26939790, [DOI](https://doi.org/10.7554/eLife.13615)). cardioEnrich's audit extends exactly this measurement to the proteomics archive and — unlike a one-off audit — leaves behind the index that fixes it. That sentence belongs in Significance.
- **HFpEF vs HFrEF molecular synthesis.** Subtype lives in free text (pxEnrich's measured analogue: subtype recoverable from free text in 32.4% of breast-cancer datasets vs 0.3% structured); until it is structured, cross-study HFpEF/HFrEF proteomic comparison is anecdotal. The field has deep single-study maps (the 16-region human heart atlas, Doll et al., *Nat Commun* 2017, PMID 29133944, [DOI](https://doi.org/10.1038/s41467-017-01747-2)) but no apparatus for *corpus-level, phenotype-resolved* synthesis.
- **Fibroblast-state biology.** The Bagchi-orbit papers (Eggertsen PNAS 2025; Travers et al., *Circulation* 2025, PMID 40258050, [DOI](https://doi.org/10.1161/CIRCULATIONAHA.124.071956)) make activation state and failing/non-failing donor status first-class phenotypes — cardioEnrich is the only proposed tool with those as extraction fields.

---

## 4. Target journal & publication strategy

**Realism check (reviewer judgment):** *Circulation* and *EHJ* do not publish metadata tools; they publish the *biology the tool finds*. Plan a **two-paper arc**:

| Paper | Target (in order) | Why |
|---|---|---|
| **P1 — Tool + archive audit** ("cardioEnrich: assertion-graded recovery of cardiovascular phenotypes from public proteomics, and a quantitative audit of the SABV/subtype metadata gap") | *Bioinformatics* (MetaSRA precedent, PMID 28535296), *Briefings in Bioinformatics*, *NAR* (Database/Web Server issue — requires a stable public instance + sustainability statement), *J Proteome Res* (community fit) | benchmark-forward, reproducible, resource |
| **P2 — Biology** (sex-stratified / HFpEF-vs-HFrEF cross-study findings enabled by P1) | *Nature Communications*, *Cardiovascular Research*, *Circulation: Heart Failure* | the discovery paper; cite P1 |

**Figures/metrics top-tier reviewers will require for P1:**
1. PRISMA-style corpus flow (archive → cardio-vocabulary corpus → extractable → benchmarked), with the exact N.
2. The **gap figure**: per field, % recoverable from free text vs % present in structured fields (the cardio twin of pxEnrich's 32.4%/0.3%), sex and subtype highlighted.
3. **Benchmark table**: regex tier vs open-weight LLM vs commercial LLM, per field — precision/recall/F1 *on asserted*, false-assertion rate (with 95% Wilson CI), missed-value rate, correct-abstention rate, scope-error rate; expert gold standard with per-field κ.
4. **Risk–coverage curves** (selective-prediction standard): accuracy vs fraction answered, per tier — the figure that *proves* abstention buys trust.
5. One **conflict gallery** (real D4/D5 cases) and one **corroboration case study** (metadata claim vs deposited matrix — §6).
6. For NAR specifically: live URL, API/MCP docs, versioning + sustainability plan.

---

## 5. Grant eligibility & funding strategy

| Mechanism | Fit | Key facts / cautions |
|---|---|---|
| **AHA Innovative Project Award** (pre-proposal **Dec 9, 2026**) | the live shot | already scoped in the project's AHA report; no preliminary data allowed — keep corpus counts as *descriptions* |
| **NLM PAR-25-131** "Computational Approaches to Curation at Scale" (R01, final new-app date **Jan 15, 2027**) | best-matched federal NOFO | preliminary data *welcome* — the pxEnrich benchmark + this demo are its core |
| **NLM PAR-26-040** (bioinformatics R01) | strong | allows MPI (a formal role for Dhusia); non-responsive to single-disease framing — write "cardiovascular disease broadly" |
| **NIH R15 (AREA)** | **via the PUI, not UAMS** | R15 eligibility is institution-limited (components below the NIH-funding cap; AREA = undergraduate-focused institutions). UAMS will not qualify; **a Harding-led R15 with Dhusia/Bagchi as collaborators** turns the student-curation arm into its own fundable project — confirm the active AREA PAR and the cap with Harding's grants office. |
| **NIH R21 to NHLBI** | ⚠ **check before planning** | NHLBI has long not participated in the parent R21 ([NHLBI withdrawal notice, AASM summary](https://aasm.org/nhlbi-will-no-longer-participate-in-the-innovative-research-grant-r21-program/); cf. historical scope notices [NOT-HL-09-124](https://grants.nih.gov/grants/guide/notice-files/NOT-HL-09-124.html)). Verify the current parent-R21 participating-IC list; NLM is the natural IC for this project anyway. |
| **NHLBI R01** | the destination | after P1 + a biological preliminary result; pair the tool with a cardiovascular question (sex-dimorphic HF proteome) so NHLBI, not just NLM, owns it |
| **NSF IUSE** | training arm | the Bio Arcade + benchmark-curation pedagogy loop, with κ-across-training-rounds as the assessment instrument |

**Feasibility objections a panel will raise — and the pre-emptive answers:**
1. *"Regex won't generalize."* → It isn't claimed to; the tiered design measures exactly where deterministic rules stop and constrained LLM extraction (still abstention-gated) takes over; the benchmark separates silence/error/over-call.
2. *"An undergraduate gold standard isn't a gold standard."* → Dual annotation, expert adjudication, per-field κ ≥ 0.75 gates, frozen holdout (§1.3).
3. *"This is engineering, not science."* → Lead with the quantified SABV/subtype gap and the two biology case studies; the index is the method, the gap and the stratified reanalysis are the science.
4. *"PRIDE/SDRF will solve this."* → SDRF is prospective format adoption; the ~60k-dataset backlog is retrospective, and PRIDE's own 2025 update leans on crowd annotation (PMID 39494541) — cardioEnrich automates and *grades* that recovery, and emits validator-passing SDRF back.
5. *"LLMs make this trivial."* → The health-LLM evaluation literature (PMIDs 39405325, 37438534) is precisely why provenance + abstention + a false-assertion CI gate are the contribution.
6. *Sustainability* (NAR and NIH both ask) → GitHub-versioned rules, seed-snapshot reproducibility, CI, institutional hosting plan.
7. *Scope* → stage GEO/imaging expansion to a later aim/renewal; ProteomeXchange first.

---

## 6. Technical & biological enhancement plan (/ExperimentDesign)

**CS1 — Sex recovery with built-in molecular ground truth (the flagship).**
Recover `sex_context` from free text across the cardiac corpus; for every dataset with a deposited protein matrix, corroborate against sex-specific proteins (RPS4Y1/DDX3Y/EIF1AY detected ⇒ male samples present; absence with adequate depth + XIST-pathway context ⇒ female), explicitly modeling *technical evaluability* (was the marker observable at that depth?) exactly as pxEnrich Aim 2 does for ESR1/PGR/ERBB2. Deliverables: % of archive where sex is (a) stated, (b) silently recoverable from the data itself, (c) truly unknowable — then a **sex-stratified cross-study differential-abundance reanalysis** in HF vs non-failing tissue (candidate replication targets from PMID 32487995's sex-specific pathways). This is P2's spine.

**CS2 — HFpEF vs HFrEF cross-study evidence synthesis.**
Build the first phenotype-resolved cardiac proteomics slice (term- and D1-EF-derived subtypes, conflicts quarantined); test whether metabolic/OXPHOS signatures reported in single HFpEF myocardium studies (e.g., the PXD060431-class datasets) replicate across independent cohorts; quantify how many "HF" datasets are *unsubtypeable* — itself the headline gap number.

**CS3 — Metadata-claim vs matrix contradiction audit (the cardio ERβ analogue).**
For datasets claiming a chamber or donor status, audit deposited matrices: atrial (NPPA, MYL4) vs ventricular (MYL2, MYL3) marker ratios vs claimed `cardiac_region`; NPPB/NT-proBNP-pathway abundance vs claimed "non-failing." Output per claim: **corroborated / contradicted / evidentially insufficient** — the before/after reified-evidence-graph figure, cardio edition.

**Metrics that prove the abstention mechanism (define in the SAP, pre-registered thresholds):**
- Per-field **precision / recall / F1** on `asserted` vs adjudicated gold.
- **False-assertion rate** (the "hallucination-free" claim, measured): asserted-when-gold-is-non-asserted, with 95% Wilson CI; release gate = 0 observed on the frozen benchmark (state the CI honestly: 0/N bounds, not "zero hallucination").
- **Risk–coverage curves + AURC** per tier (selective prediction, El-Yaniv & Wiener 2010): the coverage-vs-accuracy trade-off the abstention buys.
- **Correct-abstention rate** and **scope-error rate** (study_focus-vs-dataset confusions).
- **Inter-annotator κ** per field (gold-standard quality), **calibration (ECE)** if confidence scores are surfaced to users.
- Power note: size the expert benchmark so the false-assertion CI is informative (e.g., 0/300 gives an upper 95% bound ≈ 1.2% — 12 records cannot support the claim; ~300+ record-field pairs per release gate can).

---

## 7. Verified literature anchors (all via PubMed unless noted)

**Metadata completeness & reuse in public archives**
- Dai C, Füllgrabe A, et al. *A proteomics sample metadata representation for multiomics integration and big data analysis.* Nat Commun 2021. PMID 34615866 · [DOI](https://doi.org/10.1038/s41467-021-26111-3) — the SDRF-Proteomics standard cardioEnrich emits back.
- Perez-Riverol Y, et al. *The PRIDE database at 20 years: 2025 update.* Nucleic Acids Res 2025. PMID 39494541 · [DOI](https://doi.org/10.1093/nar/gkae1011) — scale (42k+ datasets), SDRF/crowd-annotation strategy = the retrospective gap conceded.
- Bernstein MN, Doan A, Dewey CN. *MetaSRA: normalized human sample-specific metadata for the Sequence Read Archive.* Bioinformatics 2017. PMID 28535296 · [DOI](https://doi.org/10.1093/bioinformatics/btx334) — closest prior art; cite and differentiate on assertion semantics.
- Flórez-Vargas O, et al. *Bias in the reporting of sex and age in biomedical research on mouse models.* eLife 2016. PMID 26939790 · [DOI](https://doi.org/10.7554/eLife.13615) — ~50% sex/age reporting; strongest male-bias in CVD models.

**Clinical phenotype granularity in cardiac proteomics**
- Bozkurt B, et al. *Universal Definition and Classification of Heart Failure…* J Card Fail 2021. PMID 33663906 · [DOI](https://doi.org/10.1016/j.cardfail.2021.01.022) — the EF bands behind rule D1.
- Li M, Parker BL, et al. *Core functional nodes and sex-specific pathways in human ischaemic and dilated cardiomyopathy.* Nat Commun 2020. PMID 32487995 · [DOI](https://doi.org/10.1038/s41467-020-16584-z) — PXD018678; sex-specific HF proteome; the donor-control counter-example behind rule D2.
- Doll S, et al. *Region and cell-type resolved quantitative proteomic map of the human heart.* Nat Commun 2017. PMID 29133944 · [DOI](https://doi.org/10.1038/s41467-017-01747-2) — chamber-resolved biology motivating `cardiac_region`.
- Sex-dimorphic HF proteomics: PMID 35060248 · [DOI](https://doi.org/10.1002/ejhf.2435) (HFpEF/CMD, Eur J Heart Fail 2022); PMID 31483157 · [DOI](https://doi.org/10.1080/14789450.2019.1664293) (post-MI remodeling review).
- Bagchi-orbit methods anchors: Eggertsen et al., PNAS 2025, PMID 40035765 · [DOI](https://doi.org/10.1073/pnas.2420499122); Travers et al., Circulation 2025, PMID 40258050 · [DOI](https://doi.org/10.1161/CIRCULATIONAHA.124.071956).

**Trustworthy AI / abstention / benchmark curation**
- Bedi S, et al. *Testing and Evaluation of Health Care Applications of Large Language Models: A Systematic Review.* JAMA 2025. PMID 39405325 · [DOI](https://doi.org/10.1001/jama.2024.21700).
- Singhal K, et al. *Large language models encode clinical knowledge.* Nature 2023. PMID 37438534 · [DOI](https://doi.org/10.1038/s41586-023-06291-2).
- El-Yaniv R, Wiener Y. *On the foundations of noise-free selective classification.* JMLR 11:1605–1641, 2010 (ML literature; not PubMed) — the risk–coverage framework for the abstention metrics.

---

## Bottom line

Fundable and publishable as designed, **if** the writing (a) replaces "zero-hallucination" with the measured, CI-gated false-assertion claim, (b) drops "RAG" for "provenance-enforced extraction with selective prediction," (c) leads every Significance paragraph with the biology (SABV gap, sex-dimorphic HF, HFpEF/HFrEF synthesis) and treats the index as the method, and (d) sizes the expert benchmark (~300+ record-field pairs) so the trust claim is statistically meaningful. The two-paper arc (Bioinformatics/NAR tool+audit → Nat Commun/Cardiovasc Res biology) and the funder ladder (AHA IPA → NLM PAR-25-131 → Harding-led R15 + NSF IUSE for training → NHLBI R01) give four shots whose materials reinforce rather than cannibalize each other.
