# cardioEnrich domain-layer diff — `rule:cardio-v0.1` vs pxEnrich `rule:v0.1`

**Status:** draft for the Dhusia–Bagchi kickoff · 2026-10-30
**Diffed against:** `kalyanidhusia/pxenrich_AIagent` @ `pxenrich/extraction.py` (`RULE_VERSION = "rule:v0.1"`) and `pxenrich/models.py`
**Implemented in:** `cardioenrich/extraction.py` + `cardioenrich/models.py` in this repo (runnable demo, 12-record seed, benchmark green at `false_assertion_rate = 0.0`)
**Purpose:** this document doubles as the **Approach skeleton** for the AHA IPA pre-proposal (Dec 9) and the NLM PAR-25-131 application (Jan 15).

---

## 1. The one-sentence diff

Everything that makes pxEnrich trustworthy is kept byte-for-byte — assertion states, scopes, provenance dataclasses, benchmark metrics, the CI gate — and only the **domain layer** is swapped: breast-cancer receptor/subtype fields become a cardiovascular field set whose central derivation is **stated LVEF → HF subtype**, guarded by one hard lesson: *the only safe propagations are definitional ones.*

## 2. UNCHANGED (the architecture contract)

| Component | pxEnrich `rule:v0.1` | cardioEnrich `rule:cardio-v0.1` |
|---|---|---|
| `AssertionStatus` | asserted / unknown / mixed / conflicting / abstained / not_evaluable | **identical** |
| `Scope` | dataset / cohort_subset / sample / **study_focus** | **identical** (studying fibrosis ≠ having fibrosis) |
| `SourceType`, source ordering | title (0.85) > description (0.80) > keywords (0.60) | **identical** |
| `EvidenceAssertion`, `DatasetRecord` dataclasses | stdlib dataclasses, provenance on every claim | **identical shape** (+ one `synthetic: bool` flag for labeled demo records) |
| Keyword-only disease rule | "breast cancer" in keywords only → ABSTAINED, study_focus | same rule, cardio vocabulary |
| Benchmark schema + metrics | accuracy, **false_assertion_rate**, missed_value_rate, correct_abstention_rate, scope_error_rate | **identical**; CI exits non-zero on any false assertion |
| Deterministic-first, LLM optional | regex rules; LLM explains retrieved evidence only | **identical** |
| Ingest connectors | ProteomeCentral PROXI, PRIDE v3, MassIVE | reused as-is; only the query vocabulary changes |

## 3. Field map (the diff itself)

| pxEnrich field | Action | cardioEnrich field | Rationale |
|---|---|---|---|
| `er_status` | **removed** | — | receptor axes have no cardio meaning |
| `pr_status` | **removed** | — | " |
| `her2_status` | **removed** | — | " |
| `subtype` | **replaced** | `hf_subtype` (HFrEF / HFmrEF / HFpEF) | the cardio analogue of molecular subtype; term-stated or **derived from stated LVEF** (rule D1) |
| — | **new** | `donor_status` (failing / non-failing / mixed) | the field Bagchi's world pivots on (failing-vs-nonfailing donor hearts); explicit-terms-only (rule D2) |
| — | **new** | `etiology` (ICM / DCM / HCM / ARVC / diabetic / chemo-induced / peripartum) | cause is orthogonal to syndrome; PXD018678 is MIXED here while `disease_context` stays specific |
| — | **new** | `cardiac_region` (LV / RV / LA / RA / septum / myocardium / epicardial adipose / pericardial) | chamber-resolved biology is first-class in cardiac proteomics (regional atlases, LV-vs-RV remodeling) |
| `sample_type` | **extended** | `sample_type` | adds: iPSC-CMs, cardioids, engineered microtissues/EHTs, cardiac fibroblasts, primary cardiomyocytes, pericardial fluid, epicardial adipose; keeps plasma/serum/EV/FFPE logic |
| `organism_context` | **extended** | `organism_context` | adds pig/zebrafish/macaque; adds **D5** species-field-vs-keyword conflict check (live example: PXD047728, species=Mus, keyword="human"); iPSC-"human" exempted from D5 |
| `disease_context` | **re-vocabularied** | `disease_context` | HF, DCM/HCM/ICM/ARVC, MI, I/R, AF, hypertrophy, cardiac fibrosis, cardiotoxicity, myocarditis, aortic stenosis, pressure overload; umbrella terms de-duplicated when a specific form matches |
| — | **new** | `model_system` (TAC, coronary ligation/MI, I/R, AngII, ISO, PE, iPSC model, engineered tissue, sham) | the stimulus/injury ontology the Eggertsen & Travers papers demand; **dose/route captured verbatim** (`\d+ (mg|µg|ng)/kg(/d|/h)?`) — no unit normalization in v0.1 (named simplification: the PNAS 2025 µg-vs-mg discrepancy is exactly why captured text stays verbatim) |
| — | **new** | `cell_state_context` (myofibroblast, TGF-β-stimulated, fibroblast activation, hypertrophic-stimulus-treated CMs, failing-vs-nonfailing comparison) | Bagchi-papers signal: **fibroblast activation state as a phenotype**; TGF-β *mentioned* without a stimulation verb → ABSTAINED at study_focus scope |
| — | **new** | `sex_context` (male / female / both-or-sex-stratified) | SABV; both flagged papers stratify by sex. Mostly UNKNOWN in repository metadata — **that gap is itself the reportable finding** |
| `treatment_context` | **renamed + extended** | `perturbation_context` | keeps pre/post, resistance, drug-exposure logic; adds LVAD / mechanical unloading and the cardio drug lexicon (SGLT2i, sacubitril/valsartan, beta-blockers, anthracyclines, trastuzumab, escitalopram) |

Net: pxEnrich 8 fields → cardioEnrich **11 fields** (3 removed, 1 replaced, 4 kept/extended, 7 new-or-renamed).

## 4. New lexicons (seed vocabulary; grow via student curation)

- **Disease:** heart failure (HF/HFpEF/HFrEF/HFmrEF), cardiomyopathy (dilated, hypertrophic, ischemic, arrhythmogenic, diabetic, peripartum, chemo-induced), myocardial infarction, ischemia–reperfusion, atrial fibrillation, cardiac hypertrophy, cardiac fibrosis, cardiotoxicity, myocarditis, aortic stenosis, pressure overload; umbrella fallbacks "heart disease/CVD", bare "fibrosis (organ unspecified)".
- **Model/stimulus:** TAC, LAD/coronary ligation, I/R, AngII infusion, isoproterenol, phenylephrine, sham; engineered: iPSC-CM/hiPSC-CM, cardioid, EHT/microtissue. Dose-with-units regex attached.
- **Region:** LV, RV, LA, RA/atrial, septum, apex (v0.2), myocardium-unspecified, whole heart, epicardial adipose, pericardial.
- **Sample:** cardiac tissue/biopsy/FFPE/explant, iPSC-CMs, cardioids, microtissues, cardiac fibroblasts, primary cardiomyocytes (NRVM/ARVM), endothelial cells, plasma, serum, pericardial fluid, blood/PBMC, EVs/exosomes, cell line.
- **Cell state:** myofibroblast, TGF-β-(treated|stimulated|induced|activated), fibroblast activation, (AngII|PE|ISO)-treated cardiomyocytes, failing-vs-nonfailing comparison.
- **Species:** + Sus scrofa (pig), Danio rerio (zebrafish), Macaca, rabbit, dog.
- **Drugs (perturbation):** SGLT2 inhibitors (empagliflozin, dapagliflozin), sacubitril/valsartan, metoprolol, carvedilol, doxorubicin/anthracyclines, trastuzumab, escitalopram (the LogiRx finding), + pxEnrich's generic exposure/resistance patterns.

## 5. Derivation rules (the TNBC analogues) — D1–D5

pxEnrich's signature derivation is definitional: **TNBC ⟹ ER−/PR−/HER2−** (true by definition of the label). The cardio port's central design question was *which cardio propagations are definitional and which are merely epidemiological* — and only definitional ones are allowed.

| # | Rule | Status | Why |
|---|---|---|---|
| **D1** | Stated LVEF % → `hf_subtype` by **2021 Universal Definition bands: HFrEF ≤40 %, HFmrEF 41–49 %, HFpEF ≥50 %** (named simplification; ESC 2021 uses the same bands). Comparators mapped conservatively: `<40`→HFrEF, `≥50`→preserved-range, band-straddling comparators (e.g. `<50`, `>40`) → **no claim**. **Guard:** a preserved EF *without* an HF context term → ABSTAINED — a normal ejection fraction alone is NOT HFpEF. | implemented + unit-tested | definitional given the bands, which are named and versioned |
| **D2** | `donor_status` asserted **only from explicit language** ("failing hearts", "end-stage heart failure", "explanted hearts", "transplant recipients" / "non-failing donor", "unused donor hearts", "donor controls"). A non-failing comparator named inside an HF cohort → MIXED. **Banned propagation:** "cardiomyopathy study" ⟹ failing cohort — such studies routinely include donor controls (live counter-example: **PXD018678**, ICM + DCM + age-matched donors; even "pre-mortem hearts" is not failing evidence, because donor hearts are pre-mortem too). | implemented + benchmarked | the epidemiological-vs-definitional line, stated as a rule |
| **D3** | `hf_subtype` ASSERTED ⟹ `disease_context` = heart failure. | implemented | definitional: HFpEF/HFmrEF/HFrEF *are* heart failure. The only airtight cardio propagation found so far. Never fires from MIXED/CONFLICTING subtype. |
| **D4** | Term-derived and EF-derived subtype disagree ("preserved ejection fraction" beside "LVEF 34 %") → **CONFLICTING**, both evidences attached, never silently resolved. | implemented + unit-tested | the same inconsistency class as the Methods-vs-Results AngII dose discrepancy (1.5 µg/kg/d vs 1.5 mg/kg/d) in Eggertsen et al., PNAS 2025 — the class an assertion-state system exists to surface |
| **D5** | Species field lists only non-human organisms while title/keywords say "human" → `organism_context` **CONFLICTING**, curator-review note. Exemption: "human iPSC-…" is not a conflict. Live example: **PXD047728** (species = Mus musculus; keywords "… heart disease, human"). | implemented + benchmarked | extends pxEnrich's species-vs-SDRF conflict rule to a conflict class we actually observed in the wild on day one |

### Candidate rules deliberately **deferred to v0.2** (decide with Dr. Bagchi)
- LVAD/mechanical unloading ⟹ advanced HF (clinically near-certain, but *stated nowhere* in metadata → currently ABSTAINED; see PXD082534).
- Fibroblast activation ⟸ αSMA/POSTN/ACTA2 marker mentions (needs her call on marker list — this is Aim-2-style quantitative corroboration, not metadata extraction).
- HCM gene names (MYBPC3, MYH7, TTN-truncating → DCM) ⟹ etiology. Gene-mention ≠ cohort genotype; likely study_focus ABSTAIN like pxEnrich's HER2-focus rule.
- "and"-coordination ("Myocardial Hypertrophy **and** Fibrosis") currently yields `cardiac hypertrophy; fibrosis (organ unspecified)` — a shared-modifier parse would upgrade the second term (PXD076291).

## 6. What compact metadata alone proved on day one (12-record demo seed)

10 real ProteomeXchange records (fetched 2026-10-30) + 2 labeled synthetic records; full output in `out/evidence_report.md`:

- **asserted 38 · mixed 3 · conflicting 2 · abstained 5 · unknown 84** (12 records × 11 fields)
- `sex_context` is UNKNOWN for **10/10 real records** → the SABV metadata gap, quantified — the cardio twin of pxEnrich's 32.4 %-free-text / 0.3 %-structured subtype-gap figure, and the natural first "N" for the pre-proposal's Significance paragraph.
- One **real** organism conflict (PXD047728) found without trying — conflicts are not hypothetical.
- Benchmark: 32 curated expectations, accuracy 1.0, **false_assertion_rate 0.0** (CI-gating), correct_abstention_rate 1.0; 17 unit tests on D1–D5.

**Named limitation:** this snapshot carries title/keywords/species/instrument only (the assembly environment could not fetch long description fields verbatim, and paraphrased text must never enter a deterministic corpus). Descriptions — where EF values, donor counts, doses, and sex usually live — arrive via the existing pxEnrich live-ingest path (`pridepy` / PROXI) on a network-enabled machine. The corpus-scoping count (the quotable "N datasets match the cardio vocabulary") is the known ~1-hour task.

## 7. Open questions for Dr. Bagchi (these change v0.2, not v0.1)

1. **What is "subtype" in her world?** v0.1 implements all three candidates — EF-banded HFpEF/HFrEF (D1), failing/non-failing donor status (D2), and fibroblast activation state (`cell_state_context`). Which is the *primary* axis her questions pivot on?
2. **Priority disease terms** beyond the seed vocabulary (hypertrophy / HF / fibrosis per the Eggertsen & Travers signal) — e.g., does cardio-oncology (anthracycline/trastuzumab cardiotoxicity, SGLT2 repurposing) get first-class treatment in v0.2?
3. **Marker list for fibroblast activation** (αSMA/ACTA2, POSTN, FAP?) — needed only for the Aim-2-style quantitative corroboration layer, her analogue of pxEnrich's ESR1/PGR/ERBB2 matrix check.
4. **Student team**: which PUI cohort curates the cardio benchmark (the pxEnrich assignment adapts directly — same schema, cardio accessions)?
5. **Compute target** for the full ingest + index (her lab's reality: HPC/Slurm vs Apple Silicon)?
