"""La sorveglianza deve scoprire anche tool mai presenti nella fixture."""
import json
from types import SimpleNamespace

import pytest

import estrai_schema


def simula(monkeypatch, riferimenti, definizioni):
    raccolta = []
    chiamate = []
    server = SimpleNamespace(server_address=("127.0.0.1", 1), shutdown=lambda: None)
    monkeypatch.setattr(estrai_schema, "_crea_proxy", lambda dest: (raccolta.append(dest) or server))
    monkeypatch.setattr(estrai_schema, "ATTESI", ["noto"])

    def run(cmd, **kwargs):
        chiamate.append(cmd)
        raccolta[0].append([{"name": estrai_schema.PREFIX + n, "input_schema": {"type": "object"}}
                            for n in definizioni])
        events = [{"type": "user", "message": {"content": [{"type": "tool_result", "content": [
            {"type": "tool_reference", "tool_name": estrai_schema.PREFIX + n}
            for n in riferimenti]}]}}]
        return SimpleNamespace(returncode=0, stderr="", stdout="\n".join(map(json.dumps, events)))

    monkeypatch.setattr(estrai_schema.subprocess, "run", run)
    return chiamate


def test_tool_nuovo_non_noto_viene_estratto(monkeypatch):
    calls = simula(monkeypatch, ["noto", "nuovo"], ["noto", "nuovo"])
    tools, refs = estrai_schema.lancia()
    assert {t["name"] for t in tools} == {estrai_schema.PREFIX + n for n in ("noto", "nuovo")}
    assert refs == {"noto", "nuovo"}
    assert len(calls) == 1
    assert '"+BuddaLaw"' in calls[0][2]
    assert "select:" not in calls[0][2]


def test_schema_completo_non_richiede_seconda_chiamata(monkeypatch):
    calls = simula(monkeypatch, ["noto"], ["noto"])
    tools, _ = estrai_schema.lancia()
    assert len(tools) == 1
    assert len(calls) == 1


def test_senza_inventario_live_non_si_dichiara_completo(monkeypatch):
    simula(monkeypatch, [], ["noto"])
    with pytest.raises(RuntimeError, match="inventario.*non verificabile"):
        estrai_schema.lancia()


def test_definizione_nuova_non_espansa_blocca_salvataggio(monkeypatch):
    simula(monkeypatch, ["noto", "nuovo"], ["noto"])
    with pytest.raises(RuntimeError, match="schema incompleto.*nuovo"):
        estrai_schema.lancia()


def test_catalogo_al_limite_non_e_prova_di_completezza(monkeypatch):
    simula(monkeypatch, ["noto"], ["noto"])
    monkeypatch.setattr(estrai_schema, "LIMITE_SCOPERTA", 1)
    with pytest.raises(RuntimeError, match="limite dei risultati"):
        estrai_schema.lancia()
