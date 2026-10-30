"""Data models for the cardioEnrich evidence index.

Structurally identical to pxEnrich ``pxenrich/models.py`` — the assertion
semantics, scopes, provenance fields, and dataclasses are deliberately
UNCHANGED so that the two systems share one benchmark harness, one MCP tool
contract, and one mental model. Only the domain layer differs:
``EVIDENCE_FIELDS`` is the cardiovascular field set (see docs/RULES_DIFF.md).

Plain dataclasses (stdlib-only) so the core engine runs anywhere.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class AssertionStatus(str, Enum):
    """Status of an evidence assertion. Abstention states are first-class values.

    UNCHANGED from pxEnrich rule:v0.1 — this is the trust contract.
    """

    ASSERTED = "asserted"            # evidence supports this value
    UNKNOWN = "unknown"              # no evidence found either way (default)
    MIXED = "mixed"                  # cohort contains more than one value
    CONFLICTING = "conflicting"      # sources disagree (e.g. stated EF vs stated subtype)
    ABSTAINED = "abstained"          # evidence exists but is insufficient to assert
    NOT_EVALUABLE = "not_evaluable"  # field does not apply to this record


class SourceType(str, Enum):
    """Where a piece of evidence came from. UNCHANGED from pxEnrich."""

    TITLE = "title"
    DESCRIPTION = "description"
    KEYWORDS = "keywords"
    SPECIES_FIELD = "species_field"
    SDRF = "sdrf"
    PUBLICATION = "publication"
    CURATOR = "curator"
    REPOSITORY_FIELD = "repository_field"


class Scope(str, Enum):
    """What an assertion applies to. UNCHANGED from pxEnrich.

    'The study is about cardiac fibrosis' (study_focus) is never conflated
    with 'the cohort has cardiac fibrosis' (dataset scope).
    """

    DATASET = "dataset"
    COHORT_SUBSET = "cohort_subset"
    SAMPLE = "sample"
    STUDY_FOCUS = "study_focus"


# ---------------------------------------------------------------------------
# THE DOMAIN DIFF: cardiovascular evidence fields (rule:cardio-v0.1)
# pxEnrich fields removed:  er_status, pr_status, her2_status, subtype
# pxEnrich fields kept:     sample_type, organism_context, disease_context
# pxEnrich field renamed:   treatment_context -> perturbation_context
# New cardio fields:        hf_subtype, donor_status, etiology, cardiac_region,
#                           model_system, cell_state_context, sex_context
# Rationale per field: docs/RULES_DIFF.md §3
# ---------------------------------------------------------------------------
EVIDENCE_FIELDS = [
    "disease_context",      # which cardiovascular disease, vs keyword-only mention
    "hf_subtype",           # HFrEF / HFmrEF / HFpEF — stated term or DERIVED from stated LVEF
    "donor_status",         # failing / non-failing donor tissue (explicit terms only — see D2)
    "etiology",             # ischemic / dilated / hypertrophic / arrhythmogenic / ...
    "cardiac_region",       # LV / RV / atria / septum / myocardium / epicardial adipose
    "sample_type",          # tissue, plasma, iPSC-CMs, cardiac fibroblasts, EVs, ... (extended)
    "organism_context",     # human / animal model / mixed / conflicting (keyword-vs-species check)
    "model_system",         # TAC, MI/LAD, I/R, AngII, ISO, PE, iPSC-CM, cardioid, microtissue
    "cell_state_context",   # stimulus-defined cell state: TGF-beta activation, myofibroblast, hypertrophic stimulus
    "sex_context",          # male / female / both — SABV; usually UNKNOWN = the metadata gap itself
    "perturbation_context", # drug / treatment exposure incl. dose+route capture; LVAD unloading
]


@dataclass
class EvidenceAssertion:
    """One evidence-backed claim about one field of one dataset.

    A confident value with no evidence_text and no source is a DEFECT, not an
    answer. UNCHANGED from pxEnrich.
    """

    dataset_accession: str
    field: str                       # one of EVIDENCE_FIELDS
    value: Optional[str]             # None when status is an abstention state
    status: AssertionStatus
    scope: Scope = Scope.DATASET
    confidence: float = 0.0
    evidence_text: Optional[str] = None
    source_type: Optional[SourceType] = None
    source_url: Optional[str] = None
    extracted_by: str = "rule:cardio-v0.1"   # rule:vX | llm:<model> | curator:<name>
    note: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        d["scope"] = self.scope.value
        d["source_type"] = self.source_type.value if self.source_type else None
        return d


@dataclass
class DatasetRecord:
    """Normalized dataset record in the local evidence index. UNCHANGED shape."""

    accession: str                   # ProteomeXchange accession (PXD...) or labeled synthetic id
    title: str
    repository: str                  # PRIDE | MassIVE | iProX | jPOST | ...
    species: Optional[str] = None
    instrument: Optional[str] = None
    announce_date: Optional[str] = None
    keywords: Optional[str] = None
    description: Optional[str] = None
    lab_head: Optional[str] = None
    pubmed_ids: Optional[str] = None
    dois: Optional[str] = None
    repo_link: Optional[str] = None
    px_link: Optional[str] = None
    source: str = "proteomecentral"
    source_retrieved: Optional[str] = None
    record_status: str = "metadata_only"     # metadata_only | detailed | curated
    synthetic: bool = False                  # True only for labeled demo records
    assertions: list[EvidenceAssertion] = field(default_factory=list)

    def __post_init__(self):
        if not self.px_link and not self.synthetic:
            self.px_link = (
                "https://proteomecentral.proteomexchange.org/"
                f"cgi/GetDataset?ID={self.accession}"
            )

    def to_dict(self, include_assertions: bool = True) -> dict:
        d = {k: v for k, v in asdict(self).items() if k != "assertions"}
        if include_assertions:
            d["assertions"] = [a.to_dict() for a in self.assertions]
        return d
