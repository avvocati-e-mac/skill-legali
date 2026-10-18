"""Collaudi indipendenti devono fermarsi insieme al primo guasto."""
import json
import sys
import threading

import pytest

from test_e2e_runner import runner


def test_arresto_preesistente_non_avvia_processi(runner, monkeypatch, tmp_path):
    flag = tmp_path / 'STOP'
    flag.touch()
    monkeypatch.setenv('BUDDALAW_STOP_FILE', str(flag))
    marker = tmp_path / 'non-avviato'
    with pytest.raises(runner.Blocco, match='arresto condiviso'):
        runner._stdout_su_file([sys.executable, '-c',
                               f'from pathlib import Path;Path({str(marker)!r}).touch()'],
                              timeout=5, salva=tmp_path / 'trace.jsonl')
    assert not marker.exists()


def test_guasto_live_pubblica_arresto(runner, monkeypatch, tmp_path):
    flag = tmp_path / 'STOP'
    monkeypatch.setenv('BUDDALAW_STOP_FILE', str(flag))
    ev = {'type': 'tool_use', 'part': {'tool': 'buddalaw_search_case_law',
          'state': {'status': 'completed', 'input': {}, 'output': '{"error":"HTTP 500"}'}}}
    script = f'import time;print({json.dumps(ev)!r},flush=True);time.sleep(5)'
    with pytest.raises(runner.Blocco):
        runner._stdout_su_file([sys.executable, '-u', '-c', script], timeout=5,
                              salva=tmp_path / 'trace.jsonl', controlla=True)
    assert flag.exists()


def test_arresto_esterno_ferma_processo_gia_attivo(runner, monkeypatch, tmp_path):
    flag = tmp_path / 'STOP'
    started = tmp_path / 'started'
    marker = tmp_path / 'azione-successiva'
    monkeypatch.setenv('BUDDALAW_STOP_FILE', str(flag))
    def stop():
        import time
        for _ in range(100):
            if started.exists():
                flag.touch()
                return
            time.sleep(0.01)
    thread = threading.Thread(target=stop)
    thread.start()
    script = (f'import time;from pathlib import Path;Path({str(started)!r}).touch();'
              f'time.sleep(1);Path({str(marker)!r}).touch()')
    try:
        with pytest.raises(runner.Blocco, match='arresto condiviso'):
            runner._stdout_su_file([sys.executable, '-u', '-c', script], timeout=5,
                                  salva=tmp_path / 'trace.jsonl', controlla=True)
    finally:
        thread.join(timeout=2)
    assert started.exists()
    assert not marker.exists()


def test_arresto_claude_prima_di_stdout_conserva_classificazione(runner, monkeypatch, tmp_path):
    flag = tmp_path / 'STOP'
    flag.touch()
    monkeypatch.setenv('BUDDALAW_STOP_FILE', str(flag))
    with pytest.raises(runner.Blocco) as exc:
        runner.esegui_claude(['quesito'], 'v9', 'haiku', .1, tmp_path / 'trace.jsonl')
    assert exc.value.esecuzione.costo == 0
    assert 'arresto condiviso' in exc.value.esecuzione.errore


def test_timeout_mcp_in_preflight_e_guasto(runner, monkeypatch):
    import subprocess
    def run(cmd, **kwargs):
        if cmd[1:] == ['mcp', 'list']:
            raise subprocess.TimeoutExpired(cmd, 120)
        return subprocess.CompletedProcess(cmd, 0,
            '{"mcp":{"buddalaw":{"enabled":true}}}' if cmd[1:] == ['debug','config'] else 'OpenRouter authenticated')
    monkeypatch.setattr(runner.subprocess, 'run', run)
    with pytest.raises(runner.Blocco, match='timeout del controllo MCP'):
        runner.preflight_opencode('opencode')
