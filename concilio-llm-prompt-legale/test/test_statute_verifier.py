"""Tier-1 — verify_statutes.py in modalità OFFLINE su fixture HTML in cache.

Conferma che la verifica deterministica delle norme funziona a zero rete e zero
token, e che il gate di rete è rispettato (offline di default).
"""

from __future__ import annotations

import json
import shutil

import verify_statutes as vs
from _paths import FIXTURES

ARTICLES_DIR = FIXTURES / "normattiva_articles"


def _cases_file(tmp_path):
    cases = {"cases": [{"candidate_id": "A", "risposta": "art. 2946 c.c.", "fonti": []}]}
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(cases), encoding="utf-8")
    return path


def _articles_copy(tmp_path):
    """Copia i fixture HTML in tmp così il .txt generato non sporca il repo."""
    dest = tmp_path / "normattiva_articles"
    shutil.copytree(ARTICLES_DIR, dest)
    return dest


def test_offline_verified_from_cache(tmp_path):
    result = vs.verify_statutes(
        sources_path=None,
        cases_path=_cases_file(tmp_path),
        articles_dir=_articles_copy(tmp_path),
        allow_network=False,
    )
    statuses = {r["citation"]: r["status"] for r in result["records"]}
    assert statuses.get("art. 2946 c.c.") == "verified"


def test_offline_missing_cache_is_unavailable(tmp_path):
    cases = {"cases": [{"candidate_id": "Z", "risposta": "art. 1453 c.c.", "fonti": []}]}
    path = tmp_path / "c.json"
    path.write_text(json.dumps(cases), encoding="utf-8")
    result = vs.verify_statutes(
        sources_path=None,
        cases_path=path,
        articles_dir=_articles_copy(tmp_path),
        allow_network=False,
    )
    # nessun file in cache per questa citazione -> non verificata, ma NON crasha
    statuses = {r["status"] for r in result["records"]}
    assert "verified" not in statuses
    assert statuses <= {"unavailable", "unsupported", "not_found", "mismatch"}


def test_offline_never_hits_network(monkeypatch, tmp_path):
    import normattiva_fetch as nf

    def _boom(*args, **kwargs):
        raise AssertionError("Network call attempted in offline mode!")

    monkeypatch.setattr(nf, "request_with_headers", _boom)
    # non deve sollevare: in offline non chiama request_with_headers
    vs.verify_statutes(
        sources_path=None,
        cases_path=_cases_file(tmp_path),
        articles_dir=_articles_copy(tmp_path),
        allow_network=False,
    )
