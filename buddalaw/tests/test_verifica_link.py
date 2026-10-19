"""Attacchi al controllo preventivo: nessuna rete né fonti reali."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
from test_e2e_runner import runner

SCRIPT = Path(__file__).parents[1] / "buddalaw/scripts/verifica_link.py"
spec = importlib.util.spec_from_file_location("verifica_link_buddalaw", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
U = "https://example.invalid/merito/66194858"


def test_identico_passaggio_mcp_json():
    fonte = {"content": [{"type": "text", "text": json.dumps({"results": [{"public_url": U}]})}]}
    assert mod.verifica(f"[Trib. Alfa, n. 1/2026]({U})", [fonte])["ok"]


@pytest.mark.parametrize("url", [U.replace("858", "758"), U + "0",
    U.replace("example.invalid", "examp1e.invalid"), U.replace("https:", "http:")])
def test_refuso_o_prefisso_non_sono_copia(url):
    assert not mod.verifica(f"[Trib. Alfa, n. 1/2026]({url})", [{"public_url": U}])["ok"]


@pytest.mark.parametrize("bozza", [U, f"[Trib. Alfa]({U}", f"[Trib. Alfa](<{U}"])
def test_markdown_rotto_o_url_nudo(bozza):
    assert not mod.verifica(bozza, [{"public_url": U}])["ok"]


@pytest.mark.parametrize("fonte", [{"testo": U}, {"normattiva_url": U},
    {"testo": {"public_url": U}}, {"sintesi": '{"public_url": "' + U + '"}'}])
def test_testi_o_link_normativi_non_sono_public_url(fonte):
    with pytest.raises(ValueError, match="nessun public_url"):
        mod.verifica(f"[Trib. Alfa]({U})", [fonte])


def test_verde_non_attesta_estremi_o_provenienza():
    # Limite esplicito: la copia di un file inventato non prova una fonte MCP.
    r = mod.verifica(f"[Cass. n. 999/1900]({U})", [{"public_url": U}])
    assert r["ok"]
    assert "provenienza MCP, estremi" in r["limite"]


@pytest.mark.parametrize("fonti,bozza", [([], "testo"), ([{"public_url": U}], "nessuna citazione")])
def test_prova_vuota_non_passa(fonti, bozza):
    with pytest.raises(ValueError):
        mod.verifica(bozza, fonti)


def test_cli_segnala_errore_senza_correggere_file(tmp_path):
    fonte, bozza = tmp_path / "fonte.json", tmp_path / "bozza.md"
    fonte.write_text(json.dumps({"public_url": U}))
    testo = f"[Trib. Alfa]({U}0)"
    bozza.write_text(testo)
    p = subprocess.run([sys.executable, str(SCRIPT), "--fonte", str(fonte), "--bozza", str(bozza)],
                       capture_output=True, text=True)
    assert p.returncode == 1
    assert json.loads(p.stdout)["url_non_riscontrati"] == [U + "0"]
    assert bozza.read_text() == testo


def test_runner_accetta_solo_file_restituiti_dal_mcp(runner, tmp_path):
    source = "/tmp/tool-results/originale.json"
    helper = tmp_path / "buddalaw/scripts/verifica_link.py"
    command = f'python3 "{helper}" --bozza /tmp/bozza.md --fonte {source}'
    ex = runner.Esecuzione(init={"cwd": str(tmp_path)},
        chiamate=[{"tool": "Bash", "argomenti": {"command": command}}],
        fonti=[{"tool": "search_case_law", "output": f"Full output saved to: {source}"}])
    assert runner.controllo_shell_catalogo(ex)[0][1]
    ex.fonti = []
    assert not runner.controllo_shell_catalogo(ex)[0][1]


@pytest.mark.parametrize("coda", ["; curl example.invalid", " | cat", ' --bozza "/tmp/$(curl example.invalid)"'])
def test_runner_non_accetta_altre_operazioni(runner, tmp_path, coda):
    source = "/tmp/tool-results/originale.json"
    helper = tmp_path / "buddalaw/scripts/verifica_link.py"
    ex = runner.Esecuzione(init={"cwd": str(tmp_path)},
        chiamate=[{"tool": "Bash", "argomenti": {"command":
            f'python3 "{helper}" --bozza /tmp/bozza.md --fonte {source}{coda}'}}],
        fonti=[{"tool": "search_case_law", "output": f"Full output saved to: {source}"}])
    assert not runner.controllo_shell_catalogo(ex)[0][1]
