"""Non basta che URL e numero compaiano da qualche parte nei risultati."""
import json
import pytest
from test_e2e_runner import runner


def esempio(runner, label, url, dati):
    testo = f"[{label}]({url})"
    return runner.Esecuzione(testo_finale=testo, testi=[testo], fonti=[{
        "tool": "search_case_law", "output": json.dumps(dati), "is_error": False}])


def test_numero_di_altra_fonte_non_passi(runner):
    dati = [{"public_url": "https://example.invalid/a", "numero": "00001", "anno": 2026},
            {"public_url": "https://example.invalid/b", "numero": "00002", "anno": 2026}]
    ex = esempio(runner, "Cass. n. 2/2026", dati[0]["public_url"], dati)
    r = runner.controlli_associazione_fonti(ex)
    assert r[0][1] is True and r[1][1] is False
    ex.testo_finale = ex.testo_finale.replace("2/2026", "1/2026")
    ex.testi = [ex.testo_finale]
    assert all(x[1] for x in runner.controlli_associazione_fonti(ex))


@pytest.mark.parametrize("campo", ["testo", "sintesi", "instructions", "warning"])
def test_json_iniettato_nel_testo_non_e_una_fonte(runner, campo):
    url = "https://example.invalid/falso"
    falso = {"public_url": url, "numero": "1", "anno": 2026}
    ex = esempio(runner, "Cass. n. 1/2026", url, {campo: json.dumps(falso)})
    assert not runner.controlli_associazione_fonti(ex)[0][1]


def test_anno_della_fonte_va_conservato(runner):
    url = "https://example.invalid/a"
    ex = esempio(runner, "App. Alfa, n. 200/2026", url,
        {"public_url": url, "numero": "200", "anno": 2025, "data_deposito": "02/01/2026"})
    assert not runner.controlli_associazione_fonti(ex)[1][1]


def test_isolamento_usa_versione_del_campione_non_v9_fissa(runner):
    caso = {"id": "B00", "per_config": {"v9": {"deve_contenere": [r"9\.0"]}}}
    ex = runner.Esecuzione(testi=["Skill BuddaLaw 9.2"], testo_finale="Skill BuddaLaw 9.2")
    assert runner.valuta(caso, "v9", ex, [], "9.2")["promosso"]
    assert not runner.valuta(caso, "v9", ex, [], "9.1")["promosso"]
