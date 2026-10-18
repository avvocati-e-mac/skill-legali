"""Controlli offline sull'isolamento del runner OpenCode, senza usare credenziali."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def runner(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location(
        "buddalaw_e2e_test", Path(__file__).parent / "e2e" / "run.py")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "SANDBOX", tmp_path)
    (tmp_path / "opencode.json").write_text("{}")
    return module


def test_server_estraneo_blocca_prima_delle_connessioni(runner, monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, json.dumps({
            "mcp": {"buddalaw": {"enabled": True}, "altro": {"type": "remote"}}
        }))

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    with pytest.raises(runner.Salta, match="server MCP estranei abilitati: altro"):
        runner.preflight_opencode("opencode")
    assert calls == [["opencode", "debug", "config"]]


def test_server_disabilitato_non_contamina(runner, monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if cmd[1:] == ["debug", "config"]:
            out = json.dumps({"mcp": {
                "buddalaw": {"enabled": True}, "altro": {"enabled": False}}})
        elif cmd[1:] == ["auth", "list"]:
            out = "OpenRouter authenticated"
        else:
            out = "✓ buddalaw connected"
        return subprocess.CompletedProcess(cmd, 0, out)

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    runner.preflight_opencode("opencode")
    assert calls[-1] == ["opencode", "mcp", "list"]


@pytest.mark.parametrize("code,output", [(1, ""), (0, "non-json")])
def test_config_non_verificabile_ferma_il_test(runner, monkeypatch, code, output):
    monkeypatch.setattr(runner.subprocess, "run", lambda cmd, **kw:
                        subprocess.CompletedProcess(cmd, code, output))
    with pytest.raises(runner.Salta, match="configurazione risolta"):
        runner.preflight_opencode("opencode")


def test_skill_globale_non_avvia_il_modello(runner, monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "verifica_skill_opencode", lambda *a: ["skill globale"])

    def no_model(*args, **kwargs):
        pytest.fail("Il modello non deve partire con la skill sbagliata")

    monkeypatch.setattr(runner, "_stdout_su_file", no_model)
    ex, problems = runner.esegui_opencode(
        "opencode", ["quesito"], "v9", "provider/model", tmp_path / "trace.jsonl")
    assert problems == ["skill globale"]
    assert ex.costo == 0
    assert ex.errore == "isolamento della skill non verificato"


@pytest.mark.parametrize("message", ["HTTP 500: Internal server error", "Circuit breaker aperto"])
def test_guasto_server_ferma_senza_ritento(runner, message):
    with pytest.raises(runner.Blocco):
        runner.controlla_blocco(message, True)


def test_numero_articolo_non_e_errore_http(runner):
    runner.controlla_blocco("La sentenza richiama l'art. 500 c.p.c.", False)


def test_guasto_connessione_non_viene_chiamato_login_mancante(runner, monkeypatch):
    def fake_run(cmd, **kwargs):
        if cmd[1:] == ["debug", "config"]:
            out = '{"mcp":{"buddalaw":{"enabled":true}}}'
        elif cmd[1:] == ["auth", "list"]:
            out = "OpenRouter authenticated"
        else:
            out = "✗ buddalaw failed\nMCP error -32000: Connection closed\nhttps://mcp.buddalaw.com/mcp"
        return subprocess.CompletedProcess(cmd, 0, out)

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    with pytest.raises(runner.Blocco, match="collegamento BuddaLaw non riuscito.*Connection closed"):
        runner.preflight_opencode("opencode")
