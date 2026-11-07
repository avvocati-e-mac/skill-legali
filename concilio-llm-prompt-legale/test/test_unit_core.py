"""LIVELLO 1 — Correttezza deterministica delle funzioni Python di legal_panel.py.

Importa legal_panel come modulo (scripts/ è su sys.path via conftest) e verifica
che ogni funzione faccia ciò che dichiara. Gratis, offline, nessun modello.
"""

from __future__ import annotations

import json

import pytest

import legal_panel as lp
from _paths import FIXTURES


def _load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


CITATIONS = _load("citations.json")
ANSWERS = _load("answers.json")


# --- scoring ----------------------------------------------------------------

@pytest.mark.parametrize(
    "score,bucket",
    [(0, 0), (19, 0), (20, 1), (26, 1), (27, 2), (33, 2), (34, 3), (39, 3)],
)
def test_score_to_discrete_buckets(score, bucket):
    assert lp.score_to_discrete(score) == bucket


def test_clamp_score_bounds():
    assert lp.clamp_score(-3) == 0
    assert lp.clamp_score(9) == 3
    assert lp.clamp_score(2) == 2


def test_base_scores_in_range():
    for ans in ANSWERS:
        case = {"risposta": ans["text"], "ground_truth": "art. 2946 c.c.", "required_topics": []}
        result = lp.base_scores(case)
        total = 0
        for name, score in result["scores"].items():
            assert 0 <= score <= 3, f"{ans['id']}:{name} fuori range"
            total += score * lp.WEIGHTS[name]
        assert 0 <= total <= lp.MAX_SCORE == 39


def test_scoring_monotonicity_citations():
    base = {"risposta": "Il termine è decennale.", "ground_truth": "", "required_topics": []}
    cited = {"risposta": "Il termine è decennale ai sensi dell'art. 2946 c.c.", "ground_truth": "", "required_topics": []}
    s_base = lp.base_scores(base)["scores"]["citazione_fonti"]
    s_cited = lp.base_scores(cited)["scores"]["citazione_fonti"]
    assert s_cited >= s_base


def test_scoring_hallucination_drops_score():
    clean = {"risposta": "L'art. 2946 c.c. fissa la prescrizione decennale.", "ground_truth": "", "required_topics": []}
    halluc = {"risposta": "La Cass. civ. n. 99999/2024 lo conferma.", "ground_truth": "", "required_topics": []}
    assert lp.base_scores(halluc)["scores"]["assenza_allucinazioni"] == 0
    assert lp.base_scores(clean)["scores"]["assenza_allucinazioni"] >= 2


# --- citation detection & classification ------------------------------------

@pytest.mark.parametrize("case", CITATIONS, ids=[c["id"] for c in CITATIONS])
def test_detect_citation(case):
    detected = lp.detect_source_citations({"risposta": case["raw"], "fonti": []})
    citations = [d["citation"] for d in detected]
    if case.get("expect_dropped"):
        assert case["raw"].split()[0] not in " ".join(citations) or not citations or "250" not in " ".join(citations)
        return
    if "expect_citation" in case:
        assert case["expect_citation"] in citations, f"{case['id']}: {citations}"
    for expected in case.get("expect_contains", []):
        assert expected in citations, f"{case['id']}: manca {expected} in {citations}"
    if "expect_source_type" in case:
        types = {d["source_type"] for d in detected}
        assert case["expect_source_type"] in types, f"{case['id']}: {types}"


def test_gdpr_out_of_range_dropped():
    detected = lp.detect_source_citations({"risposta": "GDPR art. 250", "fonti": []})
    assert not any("250" in d["citation"] for d in detected)
    kept = lp.detect_source_citations({"risposta": "GDPR art. 5", "fonti": []})
    assert any(d["source_type"] == "eu_law" for d in kept)


@pytest.mark.parametrize(
    "act,expected",
    [
        ("CCII", "d.lgs. 14/2019"),
        ("codice civile", "c.c."),
        ("Statuto dei lavoratori", "l. 300/1970"),
        ("cod. civ.", "c.c."),
    ],
)
def test_norm_act_aliases(act, expected):
    assert lp.norm_act(act) == expected


def test_expand_article_numbers():
    assert lp.expand_article_numbers("2946 e 2947") == ["2946", "2947"]
    assert lp.expand_article_numbers("5-7") == ["5", "6", "7"]
    # range oversize: scartato
    assert lp.expand_article_numbers("5-40") == []


# --- confidentiality --------------------------------------------------------

@pytest.mark.parametrize(
    "case", [a for a in ANSWERS if "expect_confidential" in a], ids=[a["id"] for a in ANSWERS if "expect_confidential" in a]
)
def test_confidentiality(case):
    confidential, reasons = lp.infer_confidential_detail(case["text"])
    assert confidential is case["expect_confidential"], f"{case['id']}: {reasons}"


# --- risk traps -------------------------------------------------------------

@pytest.mark.parametrize(
    "case", [a for a in ANSWERS if "expect_hallucination" in a], ids=[a["id"] for a in ANSWERS if "expect_hallucination" in a]
)
def test_find_risks(case):
    risks = lp.find_risks(case["text"])
    assert bool(risks["hallucinations"]) is case["expect_hallucination"], case["id"]
    assert bool(risks["stale"]) is case["expect_stale"], case["id"]
    assert bool(risks["privacy"]) is case["expect_privacy"], case["id"]


# --- mock traps replicated as a pytest invariant ----------------------------

def test_mock_traps_pass():
    evaluated = [lp.evaluate_case(c) for c in lp.mock_cases()]
    by_id = {item["candidate_id"]: item for item in evaluated}
    assert "possible_hallucinated_citation" in by_id["hallucinated_citation"]["human_review_flags"]
    assert "possible_stale_law" in by_id["stale_law"]["human_review_flags"]
    plain = by_id["style_bias_plain"]["score_medio"]
    markdown = by_id["style_bias_markdown"]["score_medio"]
    assert abs(plain - markdown) <= 4
