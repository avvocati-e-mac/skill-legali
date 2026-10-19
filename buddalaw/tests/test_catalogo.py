"""Differenze di catalogo, anche quando i totali coincidono: nessuna rete."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
from test_e2e_runner import runner

SCRIPT = Path(__file__).parents[1] / "buddalaw/scripts/verifica_catalogo.py"
spec = importlib.util.spec_from_file_location("catalogo_buddalaw", SCRIPT)
catalogo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalogo)


@pytest.fixture
def dati():
    return {"versione_skill": "9.1", "inventario_tool_buddalaw": ["check_access", "search_case_law"]}


@pytest.mark.parametrize("prefisso", catalogo.PREFISSI + ("",))
def test_catalogo_uguale_non_avvisa(dati, prefisso):
    r = catalogo.confronta([prefisso + n for n in dati["inventario_tool_buddalaw"]], 2, dati)
    assert r["avviso"] == ""
    assert r["nuovi"] == r["non_visibili"] == []


def test_nomi_diversi_con_stesso_totale(dati):
    r = catalogo.confronta(["check_access", "search_similar_cases"], 2, dati)
    assert r["nuovi"] == ["search_similar_cases"]
    assert r["non_visibili"] == ["search_case_law"]
    assert "search_similar_cases" in r["avviso"]
    assert "search_case_law" not in r["avviso"]


def test_solo_tool_non_visibile_non_prova_aggiornamento(dati):
    r = catalogo.confronta(["check_access"], 1, dati)
    assert r["avviso"] == ""


@pytest.mark.parametrize("nomi,totale", [([], 0), (["check_access"], 2),
    (["check_access", "mcp__buddalaw__check_access"], 2), (["mcp__altro__search"], 1)])
def test_catalogo_incompleto_o_estraneo_non_diventa_successo(dati, nomi, totale):
    with pytest.raises(ValueError):
        catalogo.confronta(nomi, totale, dati)


def test_cli_legge_la_skill_accanto_allo_script(tmp_path):
    # La copia del collaudo deve leggere l'inventario ridotto, non quello globale.
    root = tmp_path / "buddalaw"
    (root / "scripts").mkdir(parents=True)
    (root / "scripts/verifica_catalogo.py").write_bytes(SCRIPT.read_bytes())
    (root / "SKILL.md").write_text('```json\n' + json.dumps({"versione_skill": "9.1",
        "inventario_tool_buddalaw": ["check_access"]}) + '\n```')
    p = subprocess.run([sys.executable, str(root / "scripts/verifica_catalogo.py"),
        "--totale", "2", "--nomi", "check_access", "search_similar_cases"],
        capture_output=True, text=True, check=True)
    assert json.loads(p.stdout)["nuovi"] == ["search_similar_cases"]


def test_runner_autorizza_solo_lo_script_della_copia(runner, tmp_path):
    spf = tmp_path / "skill-prompt.md"
    helper = tmp_path / "buddalaw/scripts/verifica_catalogo.py"
    helper.parent.mkdir(parents=True)
    helper.write_bytes(SCRIPT.read_bytes())
    cmd = runner.comando_claude("quesito", "haiku", 0.6, spf)
    permessi = cmd[cmd.index("--allowedTools") + 1].split(",")
    assert permessi[-2:] == [f"Bash(python3 {helper} *)", f'Bash(python3 "{helper}" *)']
    senza = runner.comando_claude("quesito", "haiku", 0.6, None)
    assert senza[senza.index("--tools") + 1] == "Read,ToolSearch"
    assert "Bash" not in senza[senza.index("--allowedTools") + 1]


@pytest.mark.parametrize("comando", ["echo ricerca", "curl http://localhost:3000/access-check",
    "python3 /altro/scripts/verifica_catalogo.py --totale 1 --nomi check_access"])
def test_comando_estraneo_non_passa_anche_se_negato(runner, tmp_path, comando):
    ex = runner.Esecuzione(init={"cwd": str(tmp_path),
        "tools_scoperti": ["mcp__claude_ai_BuddaLaw__check_access"]},
        chiamate=[{"tool": "Bash", "argomenti": {"command": comando}}])
    assert runner.controllo_shell_catalogo(ex)[0][1] is False


def test_argomenti_script_corrispondono_al_catalogo_osservato(runner, tmp_path):
    helper = tmp_path / "buddalaw/scripts/verifica_catalogo.py"
    ex = runner.Esecuzione(init={"cwd": str(tmp_path),
        "tools_scoperti": ["mcp__claude_ai_BuddaLaw__check_access"]},
        chiamate=[{"tool": "Bash", "argomenti": {"command":
            f'python3 "{helper}" --totale 1 --nomi check_access'}}])
    assert runner.controllo_shell_catalogo(ex)[0][1] is True
    ex.chiamate[0]["argomenti"]["command"] += " tool_non_osservato"
    assert runner.controllo_shell_catalogo(ex)[0][1] is False


@pytest.mark.parametrize("coda,ok", [(" 2>&1", True), ("; curl https://example.invalid", False),
    (" | cat", False), (" > /tmp/altro", False), (" 2>&1; echo ricerca", False)])
def test_redirezione_diagnostica_non_e_un_secondo_comando(runner, tmp_path, coda, ok):
    helper = tmp_path / "buddalaw/scripts/verifica_catalogo.py"
    ex = runner.Esecuzione(init={"cwd": str(tmp_path),
        "tools_scoperti": ["mcp__claude_ai_BuddaLaw__check_access"]},
        chiamate=[{"tool": "Bash", "argomenti": {"command":
            f'python3 "{helper}" --totale 1 --nomi check_access{coda}'}}])
    assert runner.controllo_shell_catalogo(ex)[0][1] is ok
