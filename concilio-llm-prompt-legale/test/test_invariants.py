"""LIVELLO 2 — Invarianti/promesse della skill (comportamento), a costo zero.

Asserzioni eseguibili su ciò che SKILL.md/ARCHITETTURA.md promettono. Ogni
invariante rossa è una problematica concreta da correggere nella skill.
"""

from __future__ import annotations

import json
import subprocess
import sys

import caselaw_formcheck as cf
import legal_panel as lp
from _paths import FIXTURES, LEGAL_PANEL, SKILL_ROOT

CASES_SMOKE = FIXTURES / "cases_smoke.json"


def _run(*args, **kw):
    return subprocess.run(
        [sys.executable, str(LEGAL_PANEL), *args],
        capture_output=True, text=True, **kw,
    )


# --- verify-sources è solo routing: mai 'verified' --------------------------

def test_verify_sources_is_routing_only(tmp_path):
    out = tmp_path / "sv.json"
    res = _run("verify-sources", "--cases", str(CASES_SMOKE), "--output", str(out))
    assert res.returncode == 0, res.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    for record in data["records"]:
        status = lp.source_record_status(record)
        assert status != "verified", "verify-sources non deve confermare nulla"
        assert status in lp.SOURCE_STATUSES | {"not_performed"}


# --- citazione palesemente falsa emerge come problema -----------------------

def test_fake_citation_surfaces():
    record = cf.form_check_record(
        {"citation": "Cass. civ. Sez. II n. 99999/2024", "candidate_id": "A"}, reference_year=2026
    )
    assert record["status"] in {"not_found", "mismatch"}, "una cite falsa non deve passare silenziosa"


# --- panel_ranking != legal_final_assessment --------------------------------

def test_legal_final_assessment_non_determinato(tmp_path):
    mock_out = tmp_path / "mock.json"
    _run("mock", "--output", str(mock_out))
    report = tmp_path / "report.md"
    res = _run("report", "--input", str(mock_out), "--output", str(report))
    assert res.returncode == 0, res.stderr
    text = report.read_text(encoding="utf-8")
    assert "legal_final_assessment" in text.lower()
    assert "non_determinato" in text


# --- il report non spaccia not_performed per verifica -----------------------

def test_report_does_not_present_not_performed_as_verified(tmp_path):
    mock_out = tmp_path / "mock.json"
    _run("mock", "--output", str(mock_out))
    report = tmp_path / "r.md"
    _run("report", "--input", str(mock_out), "--output", str(report))
    text = report.read_text(encoding="utf-8")
    # se compare not_performed, non deve essere accostato a 'verificate'/'confermate'
    assert "source_verification: verified" not in text


# --- driver deterministico delle allucinazioni prevale ----------------------

def test_deterministic_hallucination_block_present(tmp_path):
    mock_out = tmp_path / "mock.json"
    _run("mock", "--output", str(mock_out))
    sources = {"records": [
        {"candidate_id": "correct", "citation": "Cass. civ. Sez. II n. 99999/2024",
         "source_type": "case_law_or_authority", "status": "not_found", "finding": "placeholder"},
    ]}
    src = tmp_path / "sv.json"
    src.write_text(json.dumps(sources), encoding="utf-8")
    report = tmp_path / "r.md"
    _run("report", "--input", str(mock_out), "--sources", str(src), "--output", str(report))
    text = report.read_text(encoding="utf-8")
    assert "controllo deterministico" in text.lower()
    assert "99999" in text


# --- CLAUDE.md ≡ AGENTS.md byte-per-byte ------------------------------------

def test_claude_agents_identical():
    claude = (SKILL_ROOT / "CLAUDE.md").read_bytes()
    agents = (SKILL_ROOT / "AGENTS.md").read_bytes()
    assert claude == agents, "CLAUDE.md e AGENTS.md devono restare byte-identici"


# --- source_gate coerente con gli stati dei record --------------------------

def test_source_gate_logic():
    verified = [{"candidate_id": "A", "citation": "art. 2946 c.c.", "source_type": "italian_statute", "status": "verified"}]
    assert lp.source_gate_from_records(verified)["status"] == "passed"
    none = [{"candidate_id": "A", "citation": "x", "source_type": "unknown", "status": "unavailable"}]
    assert lp.source_gate_from_records(none)["status"] == "not_performed"
    mixed = verified + [{"candidate_id": "A", "citation": "y", "source_type": "case_law_or_authority", "status": "not_found"}]
    assert lp.source_gate_from_records(mixed)["status"] in {"passed_with_findings", "failed"}
