"""Unit tests for rule:cardio-v0.1 — focused on the derivation rules D1–D5.

Run:  python -m pytest tests/ -q     (or)     python tests/test_cardioenrich.py
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cardioenrich.extraction import classify_ef, extract_assertions  # noqa: E402
from cardioenrich.models import AssertionStatus, DatasetRecord  # noqa: E402


def rec(title="", desc="", keyw="", species="Homo sapiens", acc="TEST-0001"):
    return DatasetRecord(accession=acc, title=title, repository="demo",
                         species=species, keywords=keyw, description=desc,
                         synthetic=True)


def get(assertions, field):
    return next(a for a in assertions if a.field == field)


class TestD1EfDerivation(unittest.TestCase):
    """D1: LVEF % -> Universal-Definition band (HFrEF ≤40, HFmrEF 41–49, HFpEF ≥50)."""

    def test_bands(self):
        self.assertEqual(classify_ef(32, None), "HFrEF")
        self.assertEqual(classify_ef(40, None), "HFrEF")
        self.assertEqual(classify_ef(41, None), "HFmrEF")
        self.assertEqual(classify_ef(49, None), "HFmrEF")
        self.assertEqual(classify_ef(50, None), "HFpEF-range (EF preserved)")
        self.assertEqual(classify_ef(62, None), "HFpEF-range (EF preserved)")

    def test_comparators_conservative(self):
        self.assertEqual(classify_ef(40, "<"), "HFrEF")       # <40 is reduced
        self.assertEqual(classify_ef(35, "<="), "HFrEF")
        self.assertIsNone(classify_ef(50, "<"))                # <50 straddles bands: no claim
        self.assertEqual(classify_ef(50, ">="), "HFpEF-range (EF preserved)")
        self.assertIsNone(classify_ef(40, ">"))                # >40 straddles bands: no claim

    def test_ef_with_hf_context_asserts(self):
        a = get(extract_assertions(rec(
            title="Myocardial proteomics in heart failure patients with LVEF 32%")),
            "hf_subtype")
        self.assertEqual(a.status, AssertionStatus.ASSERTED)
        self.assertEqual(a.value, "HFrEF")
        self.assertIn("Universal Definition", a.note)

    def test_normal_ef_without_hf_context_abstains(self):
        """A preserved EF alone is NOT HFpEF — the D1 guard."""
        a = get(extract_assertions(rec(
            title="Plasma proteome of marathon runners with ejection fraction 62%")),
            "hf_subtype")
        self.assertEqual(a.status, AssertionStatus.ABSTAINED)


class TestD2DonorStatus(unittest.TestCase):
    """D2: donor_status only from explicit language — never from disease terms."""

    def test_cardiomyopathy_study_does_not_imply_failing(self):
        a = get(extract_assertions(rec(
            title="Proteomics of dilated cardiomyopathy myocardium")), "donor_status")
        self.assertEqual(a.status, AssertionStatus.UNKNOWN)

    def test_explicit_failing(self):
        a = get(extract_assertions(rec(
            title="Phosphoproteome of explanted hearts at transplantation")),
            "donor_status")
        self.assertEqual(a.status, AssertionStatus.ASSERTED)
        self.assertEqual(a.value, "failing")

    def test_failing_vs_nonfailing_is_mixed(self):
        a = get(extract_assertions(rec(
            title="Heart failure myocardium versus non-failing donor hearts")),
            "donor_status")
        self.assertEqual(a.status, AssertionStatus.MIXED)


class TestD3Propagation(unittest.TestCase):
    """D3: hf_subtype asserted -> disease_context = heart failure (definitional)."""

    def test_hfpef_implies_heart_failure(self):
        out = extract_assertions(rec(title="Proteome in HFpEF myocardium"))
        dc = get(out, "disease_context")
        self.assertEqual(dc.status, AssertionStatus.ASSERTED)
        self.assertIn("heart failure", dc.value)

    def test_conflicting_subtype_does_not_propagate(self):
        out = extract_assertions(rec(
            title="Preserved ejection fraction cohort with LVEF 34%"))
        self.assertEqual(get(out, "hf_subtype").status, AssertionStatus.CONFLICTING)
        # disease_context must not be asserted as HF via D3 from a conflict.
        dc = get(out, "disease_context")
        self.assertNotEqual((dc.status, dc.value),
                            (AssertionStatus.ASSERTED, "heart failure"))


class TestD4Conflict(unittest.TestCase):
    def test_term_vs_ef_conflict(self):
        a = get(extract_assertions(rec(
            title="Heart failure with preserved ejection fraction (mean LVEF 34%)")),
            "hf_subtype")
        self.assertEqual(a.status, AssertionStatus.CONFLICTING)
        self.assertIn("LVEF 34%", a.evidence_text)

    def test_term_and_ef_agree(self):
        a = get(extract_assertions(rec(
            title="HFrEF myocardium, LVEF 30%")), "hf_subtype")
        self.assertEqual(a.status, AssertionStatus.ASSERTED)
        self.assertEqual(a.value, "HFrEF")


class TestD5OrganismConflict(unittest.TestCase):
    def test_species_vs_keyword_conflict(self):
        a = get(extract_assertions(rec(
            title="Proteomics of myosin-binding protein C",
            keyw="myocardium, heart disease, human",
            species="Mus musculus")), "organism_context")
        self.assertEqual(a.status, AssertionStatus.CONFLICTING)

    def test_ipsc_human_word_is_not_a_conflict(self):
        a = get(extract_assertions(rec(
            title="Human iPSC-derived cardiomyocyte proteome",
            species="Homo sapiens")), "organism_context")
        self.assertEqual(a.status, AssertionStatus.ASSERTED)
        self.assertIn("iPSC", a.value)


class TestAbstentionSemantics(unittest.TestCase):
    def test_cardiac_without_disease_abstains(self):
        a = get(extract_assertions(rec(title="Rat heart tissue iTRAQ proteomics",
                                       species="Rattus norvegicus")), "disease_context")
        self.assertEqual(a.status, AssertionStatus.ABSTAINED)

    def test_keyword_only_disease_abstains(self):
        a = get(extract_assertions(rec(title="Proteomics of a sarcomeric protein",
                                       keyw="heart disease")), "disease_context")
        self.assertEqual(a.status, AssertionStatus.ABSTAINED)

    def test_every_field_always_answered(self):
        out = extract_assertions(rec(title="x"))
        from cardioenrich.models import EVIDENCE_FIELDS
        self.assertEqual({a.field for a in out}, set(EVIDENCE_FIELDS))

    def test_provenance_on_every_asserted_value(self):
        out = extract_assertions(rec(
            title="Heart failure left ventricular tissue, male and female, LVEF 30%"))
        for a in out:
            if a.status == AssertionStatus.ASSERTED:
                self.assertTrue(a.evidence_text, f"{a.field} asserted without evidence")


if __name__ == "__main__":
    unittest.main(verbosity=2)
