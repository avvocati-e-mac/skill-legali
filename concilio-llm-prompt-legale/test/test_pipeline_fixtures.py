"""LIVELLO 3 — La 'macchina' della skill su raw finti, senza chiamare modelli.

Simula i giudici LLM con fixture raw (fake_judges/) e verifica che normalize →
aggregate → report funzionino: JSON ben formato, raw malformato preservato,
divergenza propagata, merge fonti corretto.
"""

from __future__ import annotations

import json
import subprocess
import sys

from _paths import FIXTURES, LEGAL_PANEL

CASES = FIXTURES / "cases_smoke.json"
RAW_DIR = FIXTURES / "fake_judges"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(LEGAL_PANEL), *args],
        capture_output=True, text=True,
    )


def _normalize(tmp_path):
    out = tmp_path / "normalized.json"
    res = _run("normalize-live", "--cases", str(CASES), "--raw-dir", str(RAW_DIR), "--output", str(out))
    assert res.returncode == 0, res.stderr
    return json.loads(out.read_text(encoding="utf-8")), out


def test_normalize_valid_verdicts(tmp_path):
    data, _ = _normalize(tmp_path)
    by_id = {c["candidate_id"]: c for c in data["candidates"]}
    # A ha due giudici validi
    assert len(by_id["A"]["verdetti_individuali"]) == 2
    for verdict in by_id["A"]["verdetti_individuali"]:
        assert verdict["score_massimo"] == 39
        assert len(verdict["criteria"]) == 6


def test_malformed_raw_preserved_not_invented(tmp_path):
    data, _ = _normalize(tmp_path)
    raw_errors = data.get("raw_errors", [])
    assert any("B__perplexity" in e.get("raw_file", "") for e in raw_errors), "raw malformato deve essere registrato"
    # B mantiene solo il verdetto valido, non ne inventa
    by_id = {c["candidate_id"]: c for c in data["candidates"]}
    assert len(by_id["B"]["verdetti_individuali"]) == 1


def test_report_merges_multiple_sources(tmp_path):
    _, normalized = _normalize(tmp_path)
    # due source file: routing + form-check
    sv = tmp_path / "sv.json"
    _run("verify-sources", "--cases", str(CASES), "--output", str(sv))
    fc = tmp_path / "fc.json"
    res_fc = subprocess.run(
        [sys.executable, str(LEGAL_PANEL.parent / "caselaw_formcheck.py"),
         "--cases", str(CASES), "--output", str(fc)],
        capture_output=True, text=True,
    )
    assert res_fc.returncode == 0, res_fc.stderr
    report = tmp_path / "report.md"
    res = _run("report", "--input", str(normalized), "--sources", str(sv), "--sources", str(fc), "--output", str(report))
    assert res.returncode == 0, res.stderr
    text = report.read_text(encoding="utf-8")
    assert "Report finale" in text
    # la cite 99999 del caso A emerge nel blocco deterministico
    assert "99999" in text
