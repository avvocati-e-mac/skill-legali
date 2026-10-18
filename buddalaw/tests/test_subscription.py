"""Il vincolo solo abbonamento ferma i canali a consumo prima dei modelli."""
import json
import subprocess

import pytest

from test_e2e_runner import runner


@pytest.fixture(autouse=True)
def ambiente_senza_api(monkeypatch):
    for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
                "CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CODE_USE_BEDROCK",
                "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY"):
        monkeypatch.delenv(key, raising=False)


def test_openrouter_escluso_prima_di_qualsiasi_processo(runner, monkeypatch):
    monkeypatch.setattr(runner.subprocess, 'run', lambda *a, **k: pytest.fail('processo inatteso'))
    with pytest.raises(ValueError, match='soltanto --runtime claude'):
        runner.verifica_abbonamento_claude(['claude', 'opencode'], 'haiku')


@pytest.mark.parametrize('key', ['ANTHROPIC_API_KEY', 'ANTHROPIC_BASE_URL', 'CLAUDE_CODE_USE_BEDROCK'])
def test_variabili_api_escluse_senza_leggerne_il_valore(runner, monkeypatch, key):
    monkeypatch.setenv(key, 'valore-da-non-mostrare')
    monkeypatch.setattr(runner.subprocess, 'run', lambda *a, **k: pytest.fail('processo inatteso'))
    with pytest.raises(ValueError) as exc:
        runner.verifica_abbonamento_claude(['claude'], 'haiku')
    assert 'valore-da-non-mostrare' not in str(exc.value)


@pytest.mark.parametrize('auth', [
    {'loggedIn': True, 'authMethod': 'apiKey', 'apiProvider': 'firstParty', 'subscriptionType': 'pro'},
    {'loggedIn': False},
    {'loggedIn': True, 'authMethod': 'claude.ai', 'apiProvider': 'firstParty', 'subscriptionType': None},
])
def test_accesso_non_verificato_ferma_i_modelli(runner, monkeypatch, auth):
    monkeypatch.setattr(runner.subprocess, 'run', lambda cmd, **kw:
                        subprocess.CompletedProcess(cmd, 0, json.dumps(auth)))
    with pytest.raises(ValueError, match='non verificato'):
        runner.verifica_abbonamento_claude(['claude'], 'haiku')


def test_pro_conserva_solo_tipo_di_accesso(runner, monkeypatch):
    calls = []
    def auth(cmd, **kw):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, json.dumps({
            'loggedIn': True, 'authMethod': 'claude.ai', 'apiProvider': 'firstParty',
            'subscriptionType': 'pro', 'email': 'privata', 'orgId': 'privato'}))
    monkeypatch.setattr(runner.subprocess, 'run', auth)
    proof = runner.verifica_abbonamento_claude(['claude'], 'claude-haiku-4-5-20251001')
    assert calls == [['claude', 'auth', 'status', '--json']]
    assert proof == {'authMethod': 'claude.ai', 'apiProvider': 'firstParty', 'subscriptionType': 'pro'}


def test_modello_globale_non_determinato_vietato(runner):
    with pytest.raises(ValueError, match='modello Claude esplicito'):
        runner.verifica_abbonamento_claude(['claude'], None)


def test_errore_auth_non_espone_output(runner, monkeypatch):
    def fail(*a, **k):
        raise subprocess.CalledProcessError(1, 'claude', stderr='dettagli privati')
    monkeypatch.setattr(runner.subprocess, 'run', fail)
    with pytest.raises(ValueError) as exc:
        runner.verifica_abbonamento_claude(['claude'], 'haiku')
    assert 'dettagli privati' not in str(exc.value)
