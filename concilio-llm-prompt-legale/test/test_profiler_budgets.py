"""Asserzioni di budget: una regressione di efficienza diventa un test rosso.

Trasforma le metriche del profiler in invarianti. Se un'ottimizzazione futura
peggiora la quota di citazioni risolte in Python o gonfia i prompt giudice,
questi test falliscono.
"""

from __future__ import annotations

import profile_skill as ps
from _paths import FIXTURES

CASES = FIXTURES / "cases_smoke.json"


def test_profiler_runs():
    report = ps.run(CASES)
    assert report["n_candidates"] == 2
    assert report["citations"]["total"] >= 4


def test_python_resolution_budget():
    report = ps.run(CASES)
    cit = report["citations"]
    # su questo caso (norme + una cite falsa) tutto è risolvibile in Python: nessuna delega all'MCP
    assert cit["python_resolution_ratio"] >= 0.8, cit
    assert cit["caselaw_filtered_offline"] >= 1, "la cite 99999 deve essere scartata offline"


def test_compact_prompt_saves_tokens():
    report = ps.run(CASES)
    j = report["judge_prompts"]
    assert j["prompt_tokens_compact_compressed_per_judge"] < j["prompt_tokens_monolithic_per_judge"]
    assert j["savings_compact_vs_monolithic_ratio"] >= 0.15, j


def test_token_proxy_monotonic():
    assert ps.token_proxy("a" * 400) > ps.token_proxy("a" * 40)
    assert ps.token_proxy("") >= 1
