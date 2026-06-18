"""Tier-2 — e2e live opzionale. Saltato di default.

Attivazione:
    RUN_LIVE_E2E=1 ANTHROPIC_API_KEY=... python3 -m pytest test_e2e_live.py

Manda UN prompt giudice a un modello reale e verifica che il verdetto rispetti
lo schema (6 criteri, score_massimo 39). Volutamente minimale: nessun panel,
nessun retry. Costa token, si lancia di rado.
"""

from __future__ import annotations

import json
import os

import pytest

import legal_panel as lp

RUN_LIVE = os.environ.get("RUN_LIVE_E2E") == "1" and bool(os.environ.get("ANTHROPIC_API_KEY"))

pytestmark = pytest.mark.skipif(not RUN_LIVE, reason="live e2e disabilitato (set RUN_LIVE_E2E=1 e ANTHROPIC_API_KEY)")


def test_single_judge_schema():
    anthropic = pytest.importorskip("anthropic")
    case = {
        "candidate_id": "A",
        "quesito": "Qual è il termine di prescrizione ordinario nel codice civile?",
        "ground_truth": "Prescrizione ordinaria decennale art. 2946 c.c.",
        "risposta": "Il termine ordinario è decennale ai sensi dell'art. 2946 c.c.",
        "fonti": ["art. 2946 c.c."],
        "source_file": "live",
        "data_riferimento": lp.today_iso(),
    }
    profile = lp.LIVE_JUDGE_PROFILES[lp.PRIMARY_LIVE_JUDGES[0]]
    prompt = lp.build_judge_prompt(case, profile)

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text
    payload, error = lp.parse_json_from_text(text)
    assert payload is not None, f"{error}: {text[:200]}"
    assert "criteria" in payload
    assert len(payload["criteria"]) == 6
