"""Tier-1 — Form check deterministico delle citazioni giurisprudenziali.

Verifica il parser e la mappatura su stati ammessi del nuovo script
caselaw_formcheck.py. Garantisce l'invariante: forma valida != verified.
"""

from __future__ import annotations

import json

import pytest

import caselaw_formcheck as cf
import legal_panel as lp
from _paths import FIXTURES

CASES = json.loads((FIXTURES / "caselaw_citations.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_form_check_status(case):
    record = cf.form_check_record(
        {"citation": case["citation"], "candidate_id": "A", "raw_match": case["citation"]},
        reference_year=2026,
    )
    assert record["status"] == case["expect_status"], record["form_check"]
    if "expect_flag" in case:
        assert case["expect_flag"] in record["form_check"]["flags"]
    if "expect_plausibility" in case:
        assert record["form_check"]["plausibility"] == case["expect_plausibility"]


def test_never_emits_verified():
    for case in CASES:
        record = cf.form_check_record(
            {"citation": case["citation"], "candidate_id": "A"}, reference_year=2026
        )
        assert record["status"] != "verified"
        assert record["status"] in lp.SOURCE_STATUSES


def test_output_envelope_merges_into_report(tmp_path):
    sources = {
        "records": [
            {"candidate_id": "A", "citation": "Cass. civ. Sez. II n. 99999/2024", "source_type": "case_law_or_authority"},
            {"candidate_id": "A", "citation": "Cass. civ. sez. III n. 12567/2019", "source_type": "case_law_or_authority"},
        ]
    }
    src = tmp_path / "sv.json"
    src.write_text(json.dumps(sources), encoding="utf-8")
    result = cf.run(sources_path=src, cases_path=None, reference_year=2026)
    # envelope shape compatibile con merge_source_payloads
    merged = lp.merge_source_payloads([result])
    keys = {lp.source_record_merge_key(r) for r in merged["records"]}
    assert len(keys) == 2  # una riga per citazione
    statuses = {lp.source_record_status(r) for r in merged["records"]}
    assert "not_found" in statuses  # il placeholder 99999 emerge come problema


def test_reference_year_gate():
    # con anno di riferimento futuro la cite 2030 diventa plausibile
    future_ok = cf.form_check_record(
        {"citation": "Cons. Stato sez. IV n. 1234/2030", "candidate_id": "A"}, reference_year=2031
    )
    assert future_ok["status"] != "mismatch"
    past = cf.form_check_record(
        {"citation": "Cons. Stato sez. IV n. 1234/2030", "candidate_id": "A"}, reference_year=2026
    )
    assert past["status"] == "mismatch"
