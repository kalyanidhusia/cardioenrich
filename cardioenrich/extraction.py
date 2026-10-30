"""Deterministic evidence extraction for cardiovascular proteomics metadata.

cardioEnrich rule set ``rule:cardio-v0.1`` — the domain-layer diff against
pxEnrich ``rule:v0.1`` (see docs/RULES_DIFF.md for the full diff and the
rationale behind every derivation rule).

Design rules carried over UNCHANGED from pxEnrich:
  * The LLM is not the database — these rules are deterministic and reproducible.
  * Every assertion carries evidence_text, source, scope, and confidence.
  * "unknown", "mixed", "conflicting", and "abstained" are valid outputs.
  * A study ABOUT a process (study_focus) is NOT a claim that the cohort
    HAS that phenotype (dataset scope).

Cardio-specific derivation rules (the TNBC-analogues; D-numbers match
docs/RULES_DIFF.md §5):
  D1  Stated LVEF %  ->  hf_subtype, by the 2021 Universal Definition of HF
      bands (HFrEF <=40%, HFmrEF 41-49%, HFpEF >=50%).  NAMED SIMPLIFICATION:
      HFpEF additionally requires a heart-failure context term — a normal EF
      alone is NOT HFpEF.
  D2  donor_status is asserted ONLY from explicit explant/failing/non-failing
      donor language. "Cardiomyopathy study" does NOT imply a failing cohort
      (such studies routinely include donor controls) — unlike TNBC->ER-,
      that propagation is epidemiological, not definitional, so it is banned.
  D3  hf_subtype asserted  ->  disease_context = heart failure (definitional:
      HFpEF/HFmrEF/HFrEF ARE heart failure). The only cardio propagation that
      is airtight the way TNBC -> ER-/PR-/HER2- is.
  D4  Term-derived and EF-derived hf_subtype disagree  ->  CONFLICTING, with
      both pieces of evidence attached (e.g. "preserved ejection fraction"
      stated next to "LVEF 34%").
  D5  Species field lists only non-human organisms but title/keywords say
      "human"  ->  organism_context CONFLICTING, flagged for curator review.

Extend RULE_VERSION when rules change so regression tests can pin behavior.
"""

from __future__ import annotations

import re
from typing import Optional

from .models import (
    AssertionStatus,
    DatasetRecord,
    EvidenceAssertion,
    Scope,
    SourceType,
)

RULE_VERSION = "rule:cardio-v0.1"

# ---------------------------------------------------------------------------
# Lexicons (docs/RULES_DIFF.md §4)
# ---------------------------------------------------------------------------

# Cardiovascular disease vocabulary: (pattern, canonical value).
DISEASE_PATTERNS = [
    (r"heart failure|\bHF\b(?![\s-]?X)|HFpEF|HFrEF|HFmrEF|cardiac failure", "heart failure"),
    (r"dilated cardiomyopath\w*|\bDCM\b", "cardiomyopathy — dilated (DCM)"),
    (r"hypertrophic cardiomyopath\w*|\bHCM\b", "cardiomyopathy — hypertrophic (HCM)"),
    (r"ischa?emic cardiomyopath\w*|\bICM\b", "cardiomyopathy — ischemic (ICM)"),
    (r"arrhythmogenic (?:right ventricular )?cardiomyopath\w*|\bARVC\b", "cardiomyopathy — arrhythmogenic (ARVC)"),
    (r"cardiomyopath\w*", "cardiomyopathy (type unspecified)"),
    (r"myocardial infarct\w*|\bAMI\b|\bMI\b(?![\w-])", "myocardial infarction"),
    (r"heart disease|cardiovascular disease|\bCVD\b", "cardiovascular disease (unspecified)"),
    (r"ischa?emia[\s/–-]*reperfusion|\bI/R\b|\bIRI\b", "ischemia–reperfusion injury"),
    (r"atrial fibrillation|\bAFib\b|\bAF\b(?![\w-])", "atrial fibrillation"),
    (r"(?:cardiac|myocardial|ventricular) hypertroph\w*|hypertroph\w* (?:and|,)? ?fibrosis", "cardiac hypertrophy"),
    (r"(?:cardiac|myocardial|ventricular) fibrosis", "cardiac fibrosis"),
    (r"\bfibrosis\b", "fibrosis (organ unspecified)"),
    (r"cardiotox\w*", "cardiotoxicity (cardio-oncology)"),
    (r"myocarditis", "myocarditis"),
    (r"aortic stenosis", "aortic stenosis"),
    (r"pressure[\s-]?overload", "pressure-overload remodeling"),
]
# Generic cardiac terms that justify ABSTAIN (cardiac study, disease unstated)
# rather than UNKNOWN when no disease pattern fires.
CARDIAC_FOCUS = r"\bcardiac\b|\bheart\b|myocard\w*|cardiomyocyte|cardiovascular|aort\w*|coronar\w*|vascul\w*"

# hf_subtype direct terms.
HF_SUBTYPE_TERMS = [
    (r"HFpEF|heart failure with (?:a )?preserved ejection fraction|preserved ejection[\s-]?fraction", "HFpEF"),
    (r"HFrEF|heart failure with (?:a )?reduced ejection fraction|reduced ejection[\s-]?fraction", "HFrEF"),
    (r"HFmrEF|mildly reduced ejection fraction|mid[\s-]?range ejection fraction", "HFmrEF"),
]
# Stated LVEF values, with optional comparator. Captures: (comparator, number).
EF_RE = re.compile(
    r"(?:\bLV\s?EF\b|\bEF\b|ejection[\s-]fraction)[\s:]*(?:of|was|is|at|=|~|≈)?\s*"
    r"(<|≤|<=|>|≥|>=)?\s*(\d{1,2}(?:\.\d)?)\s*%",
    re.I,
)

# donor_status — explicit terms ONLY (rule D2). NOTE: "pre-mortem hearts" is
# deliberately NOT failing evidence — donor-control hearts are pre-mortem too
# (PXD018678 is the live counter-example: ICM + DCM + donor controls).
FAILING_PATTERNS = [
    (r"failing (?:human )?hearts?|end[\s-]?stage heart failure|explanted hearts?|"
     r"heart (?:transplant(?:ation)? recipients?|explants?)",
     "failing"),
]
NONFAILING_PATTERNS = [
    (r"non[\s-]?failing(?: donor)?s?|unused donor hearts?|donor controls?|healthy donor hearts?",
     "non-failing donor"),
]

# Etiology (cause), distinct from disease_context (what).
ETIOLOGY_PATTERNS = [
    (r"ischa?emic cardiomyopath\w*|\bICM\b", "ischemic (ICM)"),
    (r"dilated cardiomyopath\w*|\bDCM\b", "dilated (DCM)"),
    (r"hypertrophic cardiomyopath\w*|\bHCM\b", "hypertrophic (HCM)"),
    (r"arrhythmogenic|\bARVC\b", "arrhythmogenic (ARVC)"),
    (r"diabetic cardiomyopath\w*", "diabetic"),
    (r"(?:anthracycline|doxorubicin|chemotherapy)[\s-]?(?:induced|associated)", "chemotherapy-induced"),
    (r"peripartum cardiomyopath\w*", "peripartum"),
]

# Cardiac region / compartment.
REGION_PATTERNS = [
    (r"left ventric\w*|\bLV\b(?![\w])", "left ventricle (LV)"),
    (r"right ventric\w*|\bRV\b(?![\w])", "right ventricle (RV)"),
    (r"left atri\w*|\bLA\b(?![\w])", "left atrium (LA)"),
    (r"right atri\w*|atri(?:um|al)", "atrium / atrial"),
    (r"interventricular septum|septal", "septum"),
    (r"epicardial (?:adipose|fat)", "epicardial adipose tissue"),
    (r"pericardi\w*", "pericardium / pericardial"),
    (r"myocardi(?:um|al)", "myocardium (chamber unspecified)"),
    (r"whole heart", "whole heart"),
]

# Sample-type vocabulary, ordered by specificity (extends pxEnrich list).
SAMPLE_PATTERNS = [
    (r"iPSC[\s-]?(?:derived[\s-]?)?(?:cardiomyocytes?|CMs?)|hiPSC[\s-]?CMs?", "iPSC-derived cardiomyocytes"),
    (r"cardioids?", "cardioid (iPSC-derived organoid)"),
    (r"engineered heart tissues?|\bEHTs?\b|cardiac microtissues?", "engineered cardiac microtissue"),
    (r"(?:primary )?cardiac fibroblasts?|\bCFs?\b(?![\w])", "cardiac fibroblasts"),
    (r"(?:primary |adult |neonatal )?(?:rat |mouse |human )?cardiomyocytes?|\bNRVMs?\b|\bARVMs?\b", "cardiomyocytes (primary)"),
    (r"endothelial cells?", "endothelial cells"),
    (r"patient[\s-]?derived xenograft|\bPDX\b", "patient-derived xenograft (PDX)"),
    (r"\bFFPE\b|(?:heart|cardiac|ventricular|myocardial|atrial) (?:tissues?|biops\w+|samples?)|"
     r"hearts? tissues?|heart tissue|biops\w+|explanted hearts?|pre[\s-]?mortem .{0,20}hearts?", "cardiac tissue"),
    (r"\bplasma\b", "plasma"),
    (r"\bserum\b", "serum"),
    (r"pericardial fluid", "pericardial fluid"),
    (r"epicardial (?:adipose|fat)", "epicardial adipose tissue"),
    (r"peripheral blood|\bPBMCs?\b|\bblood\b", "blood / immune cells"),
    (r"extracellular vesicles?|exosomes?|\bEVs?\b(?![\w])", "extracellular vesicles"),
    (r"cell lines?|co[\s-]?culture", "cell line / in vitro"),
]

ANIMAL_SPECIES = {
    "mus musculus": "mouse",
    "rattus norvegicus": "rat",
    "sus scrofa": "pig",
    "oryctolagus": "rabbit",
    "canis": "dog",
    "danio rerio": "zebrafish",
    "macaca": "macaque",
}
NON_DISEASE_SPECIES = ["escherichia coli", "saccharomyces", "bacillus"]

# Model systems / injury models (with dose/route capture for infusion models).
MODEL_PATTERNS = [
    (r"transverse aortic constriction|\bTAC\b", "pressure overload (TAC)"),
    (r"\bLAD\b (?:ligation|occlusion)|coronary (?:artery )?(?:ligation|occlusion)", "myocardial infarction (coronary ligation)"),
    (r"ischa?emia[\s/–-]*reperfusion|\bI/R\b", "ischemia–reperfusion"),
    (r"angiotensin[\s-]?II|\bAngII\b|\bAng II\b", "angiotensin II infusion"),
    (r"isoproterenol|\bISO\b(?![\w])", "isoproterenol"),
    (r"phenylephrine|\bPE\b(?![\w])", "phenylephrine"),
    (r"myocardial infarct\w* model|\bMI\b model", "myocardial infarction model"),
    (r"iPSC|hiPSC|cardioids?", "iPSC-derived model"),
    (r"microtissues?|engineered heart", "engineered-tissue model"),
    (r"\bsham\b", "sham-operated control arm"),
]
DOSE_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mg|µg|ug|ng)\s*/\s*kg\s*(?:/\s*(?:d(?:ay)?|h(?:r|our)?))?",
    re.I,
)

# Stimulus-defined cell states (the Bagchi-papers signal: fibroblast
# activation state as a first-class phenotype).
CELL_STATE_PATTERNS = [
    (r"myofibroblasts?", "myofibroblast (activated fibroblast)"),
    (r"TGF[\s-]?(?:β|beta)[\s-]?(?:1)?[\s-]?(?:treated|stimulated|induced|activated)",
     "TGF-β-stimulated"),
    (r"fibroblast activation", "fibroblast activation"),
    (r"(?:AngII|angiotensin[\s-]?II|phenylephrine|PE|isoproterenol|ISO)[\s-]?(?:treated|stimulated|induced) cardiomyocytes?",
     "hypertrophic-stimulus-treated cardiomyocytes"),
    (r"failing (?:vs\.?|versus) non[\s-]?failing", "failing vs non-failing comparison"),
]
# TGF-β mention without a treatment verb = study focus, not cell state.
TGFB_FOCUS = r"TGF[\s-]?(?:β|beta)"

# Sex as a biological variable.
SEX_PATTERNS = [
    (r"male and female|female and male|both sexes|men and women|women and men|sex[\s-]?specific", "both / sex-stratified"),
    (r"\bfemale\b|\bwomen\b", "female"),
    (r"\bmale\b|\bmen\b", "male"),
]

# Perturbation / treatment context (pxEnrich treatment_context, extended).
PERTURBATION_PATTERNS = [
    (r"mechanical unloading|\bLVAD\b|ventricular assist device", "mechanical unloading (LVAD)"),
    (r"pre[\s-]?and post[\s-]?|before and after (?:surgery|treatment)|neoadjuvant", "pre/post treatment comparison"),
    (r"resistan(?:t|ce)|persist(?:er|ence)", "therapy resistance / persistence"),
    (r"treated with|treatment response|exposed to|inhibitor|inhibition|agonist|"
     r"doxorubicin|anthracycline|trastuzumab|SGLT2|empagliflozin|dapagliflozin|"
     r"sacubitril|valsartan|metoprolol|carvedilol|escitalopram|drug repurposing",
     "drug / treatment exposure"),
]

HF_CONTEXT_RE = re.compile(r"heart failure|\bHF\b(?![\s-]?X)|HFpEF|HFrEF|HFmrEF|cardiac failure", re.I)
HUMAN_WORD_RE = re.compile(r"\bhumans?\b(?![\s-]?ized)", re.I)


# ---------------------------------------------------------------------------
# Helpers (identical mechanics to pxEnrich)
# ---------------------------------------------------------------------------

def _search(patterns, text: str):
    for pat, value in patterns:
        m = re.search(pat, text, re.I)
        if m:
            return value, m.group(0)
    return None, None


def _snippet(text: str, match: str, width: int = 120) -> str:
    idx = text.lower().find(match.lower())
    if idx < 0:
        return match
    start = max(0, idx - width // 2)
    end = min(len(text), idx + len(match) + width // 2)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"


def _unknown(acc: str, fieldname: str, rec: DatasetRecord, note: str) -> EvidenceAssertion:
    return EvidenceAssertion(
        acc, fieldname, None, AssertionStatus.UNKNOWN, Scope.DATASET, 0.0,
        source_url=rec.repo_link, extracted_by=RULE_VERSION, note=note,
    )


def classify_ef(value: float, comparator: Optional[str]) -> Optional[str]:
    """D1: map a stated LVEF % to a Universal-Definition band.

    NAMED SIMPLIFICATION: 2021 Universal Definition bands
    (HFrEF <=40 %, HFmrEF 41-49 %, HFpEF >=50 %). Comparators are mapped
    conservatively; a band-straddling comparator returns None (no claim).
    """
    if comparator in ("<", "<=", "≤"):
        return "HFrEF" if value <= 41 else None
    if comparator in (">", ">=", "≥"):
        return "HFpEF-range (EF preserved)" if value >= 49 else None
    if value <= 40:
        return "HFrEF"
    if value <= 49:
        return "HFmrEF"
    return "HFpEF-range (EF preserved)"


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_assertions(rec: DatasetRecord) -> list[EvidenceAssertion]:
    """Run all deterministic rule:cardio-v0.1 rules over one dataset record.

    Returns one assertion per evidence field. Fields with no evidence get an
    UNKNOWN assertion so downstream consumers never confuse "we did not look"
    with "we looked and found nothing".
    """
    out: list[EvidenceAssertion] = []
    acc = rec.accession
    title = rec.title or ""
    desc = rec.description or ""
    keyw = rec.keywords or ""
    species = (rec.species or "").lower()
    sources = [
        (title, SourceType.TITLE, 0.85),
        (desc, SourceType.DESCRIPTION, 0.80),
        (keyw, SourceType.KEYWORDS, 0.60),
    ]
    all_text = f"{title}\n{desc}\n{keyw}"
    strong_text = f"{title}\n{desc}"

    # --- organism context (incl. D5 keyword-vs-species conflict) -----------
    out.append(_organism(rec, species, all_text, title, desc, keyw))

    # --- disease context -----------------------------------------------------
    disease_hits = []
    for text, stype, conf in sources:
        if not text:
            continue
        for pat, value in DISEASE_PATTERNS:
            m = re.search(pat, text, re.I)
            if m and value not in [v for v, *_ in disease_hits]:
                disease_hits.append((value, m.group(0), text, stype, conf))
    strong = [h for h in disease_hits if h[3] in (SourceType.TITLE, SourceType.DESCRIPTION)]
    if strong:
        values = sorted({v for v, *_ in strong})
        # De-duplicate umbrella terms when a specific form matched:
        if len(values) > 1 and any("cardiomyopathy — " in v for v in values):
            values = [v for v in values if v != "cardiomyopathy (type unspecified)"]
        if len(values) > 1:
            values = [v for v in values if v != "cardiovascular disease (unspecified)"]
        if len(values) > 1 and "cardiac fibrosis" in values:
            values = [v for v in values if v != "fibrosis (organ unspecified)"]
        first = strong[0]
        out.append(EvidenceAssertion(
            acc, "disease_context", "; ".join(values), AssertionStatus.ASSERTED,
            Scope.DATASET, first[4], evidence_text=_snippet(first[2], first[1]),
            source_type=first[3], source_url=rec.repo_link, extracted_by=RULE_VERSION,
            note=None if len(values) == 1 else "Multiple disease terms — possibly a comparative cohort.",
        ))
    elif disease_hits:  # keyword-only — same abstention logic as pxEnrich bc_kw_only
        first = disease_hits[0]
        out.append(EvidenceAssertion(
            acc, "disease_context", None, AssertionStatus.ABSTAINED, Scope.STUDY_FOCUS,
            0.0, evidence_text=_snippet(first[2], first[1]), source_type=first[3],
            source_url=rec.repo_link, extracted_by=RULE_VERSION,
            note=(f"'{first[1]}' appears only in submitter keywords, not in the title "
                  "or description. The study may be related to cardiovascular disease "
                  "without being a study OF that disease; not confidently labeled."),
        ))
    elif re.search(CARDIAC_FOCUS, strong_text, re.I):
        m = re.search(CARDIAC_FOCUS, strong_text, re.I)
        out.append(EvidenceAssertion(
            acc, "disease_context", None, AssertionStatus.ABSTAINED, Scope.STUDY_FOCUS,
            0.0, evidence_text=_snippet(strong_text, m.group(0)),
            source_type=SourceType.TITLE, source_url=rec.repo_link,
            extracted_by=RULE_VERSION,
            note="Cardiac material/focus is stated, but no disease is named — "
                 "a cardiac study is not automatically a disease study.",
        ))
    else:
        out.append(_unknown(acc, "disease_context", rec,
                            "No cardiovascular disease terms found in available metadata."))

    # --- hf_subtype: direct terms + D1 EF derivation + D4 conflict ----------
    term_val, term_match, term_src = None, None, None
    for text, stype, conf in sources:
        if not text:
            continue
        v, m = _search(HF_SUBTYPE_TERMS, text)
        if v:
            term_val, term_match, term_src = v, m, (text, stype, conf)
            break
    ef_val, ef_match = None, None
    m = EF_RE.search(all_text)
    if m:
        ef_band = classify_ef(float(m.group(2)), m.group(1))
        if ef_band:
            ef_val, ef_match = ef_band, m.group(0)

    def _norm(v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return "HFpEF" if v.startswith("HFpEF") else v

    if term_val and ef_val and _norm(term_val) != _norm(ef_val):
        # D4 — the assertion-state system's reason to exist.
        out.append(EvidenceAssertion(
            acc, "hf_subtype", None, AssertionStatus.CONFLICTING, Scope.DATASET, 0.0,
            evidence_text=(f"Stated subtype term '{term_match}' vs stated "
                           f"ejection fraction '{ef_match}' "
                           f"(EF-derived band: {_norm(ef_val)})."),
            source_type=term_src[1], source_url=rec.repo_link, extracted_by=RULE_VERSION,
            note="The named subtype and the stated LVEF disagree (D4); "
                 "flagged for curator review rather than silently resolved.",
        ))
    elif term_val:
        out.append(EvidenceAssertion(
            acc, "hf_subtype", term_val, AssertionStatus.ASSERTED, Scope.DATASET,
            term_src[2], evidence_text=_snippet(term_src[0], term_match),
            source_type=term_src[1], source_url=rec.repo_link, extracted_by=RULE_VERSION,
        ))
    elif ef_val:
        banded = _norm(ef_val)
        if banded == "HFpEF" and not HF_CONTEXT_RE.search(all_text):
            out.append(EvidenceAssertion(
                acc, "hf_subtype", None, AssertionStatus.ABSTAINED, Scope.DATASET, 0.0,
                evidence_text=_snippet(all_text, ef_match),
                source_type=SourceType.DESCRIPTION, source_url=rec.repo_link,
                extracted_by=RULE_VERSION,
                note="A preserved EF was stated but no heart-failure context: "
                     "a normal ejection fraction alone is NOT HFpEF (D1 guard).",
            ))
        else:
            out.append(EvidenceAssertion(
                acc, "hf_subtype", banded, AssertionStatus.ASSERTED, Scope.DATASET, 0.75,
                evidence_text=_snippet(all_text, ef_match),
                source_type=SourceType.DESCRIPTION, source_url=rec.repo_link,
                extracted_by=RULE_VERSION,
                note=("Derived from stated LVEF by 2021 Universal Definition bands "
                      "(HFrEF ≤40 %, HFmrEF 41–49 %, HFpEF ≥50 %) — rule D1."),
            ))
    else:
        out.append(_unknown(acc, "hf_subtype", rec,
                            "No HF-subtype term and no stated ejection fraction found."))

    # D3: hf_subtype asserted -> disease_context = heart failure (definitional).
    hf_assert = next((a for a in out if a.field == "hf_subtype"
                      and a.status == AssertionStatus.ASSERTED), None)
    if hf_assert:
        dc = next(a for a in out if a.field == "disease_context")
        if dc.status != AssertionStatus.ASSERTED:
            out[out.index(dc)] = EvidenceAssertion(
                acc, "disease_context", "heart failure", AssertionStatus.ASSERTED,
                Scope.DATASET, 0.7,
                evidence_text=f"Implied by asserted HF subtype ({hf_assert.value}).",
                source_type=SourceType.DESCRIPTION, source_url=rec.repo_link,
                extracted_by=RULE_VERSION,
                note="Derived (D3): HFpEF/HFmrEF/HFrEF are heart failure by definition.",
            )

    # --- donor_status (D2: explicit terms only) ------------------------------
    f_val, f_match = _search(FAILING_PATTERNS, all_text)
    nf_val, nf_match = _search(NONFAILING_PATTERNS, all_text)
    # A non-failing comparator named inside a heart-failure cohort is a
    # failing-vs-non-failing comparison even without the word "failing hearts".
    if nf_val and not f_val and HF_CONTEXT_RE.search(all_text):
        f_val, f_match = "failing", HF_CONTEXT_RE.search(all_text).group(0)
    if f_val and nf_val:
        out.append(EvidenceAssertion(
            acc, "donor_status", "failing and non-failing (comparison cohort)",
            AssertionStatus.MIXED, Scope.DATASET, 0.75,
            evidence_text=f"'{f_match}' and '{nf_match}'",
            source_type=SourceType.DESCRIPTION, source_url=rec.repo_link,
            extracted_by=RULE_VERSION,
            note="Cohort spans failing and non-failing donor tissue; interpret per-sample.",
        ))
    elif f_val or nf_val:
        value = f_val or nf_val
        match = f_match or nf_match
        out.append(EvidenceAssertion(
            acc, "donor_status", value, AssertionStatus.ASSERTED, Scope.DATASET, 0.8,
            evidence_text=_snippet(all_text, match), source_type=SourceType.DESCRIPTION,
            source_url=rec.repo_link, extracted_by=RULE_VERSION,
        ))
    else:
        note = ("No explicit failing / non-failing donor language. NOT derived from "
                "disease terms: a cardiomyopathy study routinely includes donor "
                "controls, so that propagation is banned (D2).")
        out.append(_unknown(acc, "donor_status", rec, note))

    # --- etiology -------------------------------------------------------------
    etio_hits = []
    for text, stype, conf in sources:
        if not text:
            continue
        for pat, value in ETIOLOGY_PATTERNS:
            m = re.search(pat, text, re.I)
            if m and value not in [v for v, *_ in etio_hits]:
                etio_hits.append((value, m.group(0), text, stype, conf))
    if len({v for v, *_ in etio_hits}) > 1:
        values = ", ".join(sorted({v for v, *_ in etio_hits}))
        out.append(EvidenceAssertion(
            acc, "etiology", values, AssertionStatus.MIXED, Scope.DATASET, 0.75,
            evidence_text="; ".join(sorted({f"'{m}'" for _, m, *_ in etio_hits})),
            source_type=etio_hits[0][3], source_url=rec.repo_link, extracted_by=RULE_VERSION,
            note="Multiple etiologies mentioned — likely a comparative cohort.",
        ))
    elif etio_hits:
        v, m_, text, stype, conf = etio_hits[0]
        out.append(EvidenceAssertion(
            acc, "etiology", v, AssertionStatus.ASSERTED, Scope.DATASET, conf,
            evidence_text=_snippet(text, m_), source_type=stype,
            source_url=rec.repo_link, extracted_by=RULE_VERSION,
        ))
    else:
        out.append(_unknown(acc, "etiology", rec,
                            "No etiology terms found in available metadata."))

    # --- cardiac region --------------------------------------------------------
    rvalue, rmatch = _search(REGION_PATTERNS, all_text)
    if rvalue:
        out.append(EvidenceAssertion(
            acc, "cardiac_region", rvalue, AssertionStatus.ASSERTED, Scope.DATASET, 0.7,
            evidence_text=_snippet(all_text, rmatch), source_type=SourceType.DESCRIPTION,
            source_url=rec.repo_link, extracted_by=RULE_VERSION,
        ))
    else:
        out.append(_unknown(acc, "cardiac_region", rec,
                            "No cardiac region/compartment terms found."))

    # --- sample type -------------------------------------------------------------
    sample_hits = []
    for text, stype, conf in sources:
        if not text:
            continue
        for pat, value in SAMPLE_PATTERNS:
            m = re.search(pat, text, re.I)
            if m and value not in [v for v, *_ in sample_hits]:
                sample_hits.append((value, m.group(0), text, stype, conf))
    if not sample_hits:
        out.append(_unknown(acc, "sample_type", rec,
                            "No sample-type terms found in available metadata."))
    else:
        seen_vals = [v for v, *_ in sample_hits]
        primary = [v for v in seen_vals if v != "extracellular vesicles"] or seen_vals
        value = "; ".join(dict.fromkeys(primary))[:200]
        if "extracellular vesicles" in seen_vals and primary != seen_vals:
            value += " (extracellular-vesicle fraction)"
        first = next(h for h in sample_hits if h[0] == primary[0])
        out.append(EvidenceAssertion(
            acc, "sample_type", value, AssertionStatus.ASSERTED, Scope.DATASET,
            first[4], evidence_text=_snippet(first[2], first[1]),
            source_type=first[3], source_url=rec.repo_link, extracted_by=RULE_VERSION,
        ))

    # --- model system ---------------------------------------------------------
    mvalue, mmatch = _search(MODEL_PATTERNS, all_text)
    if mvalue:
        dose = DOSE_RE.search(all_text)
        note = None
        value = mvalue
        if dose:
            value = f"{mvalue} ({dose.group(0)})"
            note = "Dose/route captured verbatim where stated (no unit normalization in v0.1)."
        out.append(EvidenceAssertion(
            acc, "model_system", value, AssertionStatus.ASSERTED, Scope.DATASET, 0.75,
            evidence_text=_snippet(all_text, mmatch), source_type=SourceType.DESCRIPTION,
            source_url=rec.repo_link, extracted_by=RULE_VERSION, note=note,
        ))
    else:
        out.append(_unknown(acc, "model_system", rec,
                            "No injury/perturbation model or engineered-model terms found."))

    # --- cell state context ------------------------------------------------------
    cvalue, cmatch = _search(CELL_STATE_PATTERNS, all_text)
    if cvalue:
        out.append(EvidenceAssertion(
            acc, "cell_state_context", cvalue, AssertionStatus.ASSERTED, Scope.DATASET,
            0.7, evidence_text=_snippet(all_text, cmatch),
            source_type=SourceType.DESCRIPTION, source_url=rec.repo_link,
            extracted_by=RULE_VERSION,
        ))
    elif re.search(TGFB_FOCUS, all_text, re.I):
        m = re.search(TGFB_FOCUS, all_text, re.I)
        out.append(EvidenceAssertion(
            acc, "cell_state_context", None, AssertionStatus.ABSTAINED, Scope.STUDY_FOCUS,
            0.0, evidence_text=_snippet(all_text, m.group(0)),
            source_type=SourceType.DESCRIPTION, source_url=rec.repo_link,
            extracted_by=RULE_VERSION,
            note="TGF-β is mentioned as a topic; no stimulation/activation of the "
                 "profiled cells is stated. Studying a pathway is not the same as "
                 "the samples being pathway-activated.",
        ))
    else:
        out.append(_unknown(acc, "cell_state_context", rec,
                            "No stimulus-defined cell-state terms found."))

    # --- sex context ---------------------------------------------------------------
    svalue, smatch = _search(SEX_PATTERNS, all_text)
    if svalue:
        out.append(EvidenceAssertion(
            acc, "sex_context", svalue, AssertionStatus.ASSERTED, Scope.DATASET, 0.7,
            evidence_text=_snippet(all_text, smatch), source_type=SourceType.DESCRIPTION,
            source_url=rec.repo_link, extracted_by=RULE_VERSION,
        ))
    else:
        out.append(_unknown(acc, "sex_context", rec,
                            "Sex not stated in available metadata — itself a reportable "
                            "SABV metadata gap."))

    # --- perturbation context ---------------------------------------------------
    pvalue, pmatch = _search(PERTURBATION_PATTERNS, all_text)
    if pvalue:
        out.append(EvidenceAssertion(
            acc, "perturbation_context", pvalue, AssertionStatus.ASSERTED,
            Scope.DATASET, 0.65, evidence_text=_snippet(all_text, pmatch),
            source_type=SourceType.DESCRIPTION, source_url=rec.repo_link,
            extracted_by=RULE_VERSION,
        ))
    else:
        out.append(_unknown(acc, "perturbation_context", rec,
                            "No treatment / intervention terms found."))

    return out


def _organism(rec, species, all_text, title, desc, keyw) -> EvidenceAssertion:
    """Organism context with the D5 keyword-vs-species conflict check."""
    acc = rec.accession
    species_list = [s.strip() for s in re.split(r"[,;]", species) if s.strip()]
    kinds = set()
    for s in species_list:
        if "homo sapiens" in s or s == "human":
            kinds.add("human")
        elif any(k in s for k in ANIMAL_SPECIES):
            kinds.add("animal")
        elif any(k in s for k in NON_DISEASE_SPECIES):
            kinds.add("non_disease_system")
        elif s:
            kinds.add("other")

    human_word = HUMAN_WORD_RE.search(f"{title}\n{keyw}")
    ipsc = re.search(r"iPSC|hiPSC", all_text, re.I)

    # D5: species field is non-human only, but metadata text says "human".
    if kinds and "human" not in kinds and human_word and not ipsc:
        return EvidenceAssertion(
            acc, "organism_context", None, AssertionStatus.CONFLICTING, Scope.DATASET,
            0.0,
            evidence_text=(f"Species field: {rec.species}; but title/keywords contain "
                           f"'{human_word.group(0)}'."),
            source_type=SourceType.SPECIES_FIELD, source_url=rec.repo_link,
            extracted_by=RULE_VERSION,
            note="Sources disagree about the organism (D5) — possibly a human-relevance "
                 "keyword on an animal study, or a missing species entry; flagged for "
                 "curator review rather than silently resolved.",
        )
    if kinds == {"human"}:
        patienty = re.search(
            r"patients?\b|clinical samples?|cohort|donor|biops\w+|pre[\s-]?mortem|explant",
            all_text, re.I)
        if ipsc:
            value, note = "human — iPSC-derived model", \
                "Human-derived but an engineered model, not patient tissue."
        elif patienty:
            value, note = "human — patient/donor-derived samples", None
        else:
            value, note = "human (sample source not detailed)", None
        ev = (patienty.group(0) if patienty else (ipsc.group(0) if ipsc else rec.species))
        return EvidenceAssertion(
            acc, "organism_context", value, AssertionStatus.ASSERTED, Scope.DATASET,
            0.85, evidence_text=_snippet(all_text, ev) if ev else rec.species,
            source_type=SourceType.SPECIES_FIELD, source_url=rec.repo_link,
            extracted_by=RULE_VERSION, note=note,
        )
    if "human" in kinds and "animal" in kinds:
        return EvidenceAssertion(
            acc, "organism_context", "mixed: human and animal model",
            AssertionStatus.MIXED, Scope.DATASET, 0.8,
            evidence_text=f"Species field: {rec.species}",
            source_type=SourceType.SPECIES_FIELD, source_url=rec.repo_link,
            extracted_by=RULE_VERSION,
            note="Contains both human and animal-model material; interpret per-sample.",
        )
    if "animal" in kinds:
        animal = next((v for k, v in ANIMAL_SPECIES.items() if k in species), "animal")
        return EvidenceAssertion(
            acc, "organism_context", f"animal model ({animal})",
            AssertionStatus.ASSERTED, Scope.DATASET, 0.9,
            evidence_text=f"Species field: {rec.species}",
            source_type=SourceType.SPECIES_FIELD, source_url=rec.repo_link,
            extracted_by=RULE_VERSION,
            note="Animal-model study: informative for biology, not direct evidence in humans.",
        )
    if "non_disease_system" in kinds:
        return EvidenceAssertion(
            acc, "organism_context", f"non-disease experimental system ({rec.species})",
            AssertionStatus.ASSERTED, Scope.DATASET, 0.9,
            evidence_text=f"Species field: {rec.species}",
            source_type=SourceType.SPECIES_FIELD, source_url=rec.repo_link,
            extracted_by=RULE_VERSION,
            note="e.g. recombinant protein work; not a study of patients or hearts.",
        )
    return _unknown(acc, "organism_context", rec, "Species field missing or unrecognized.")


def enrich_record(rec: DatasetRecord) -> DatasetRecord:
    """Attach extracted assertions to a record (idempotent)."""
    rec.assertions = extract_assertions(rec)
    return rec
