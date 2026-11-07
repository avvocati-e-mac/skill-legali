"""
Livello C — contratto con il server BuddaLaw reale (richiede rete e abbonamento).

Esecuzione (dalla radice del repository):

    BUDDALAW_LIVE=1 pytest buddalaw/tests/test_mcp_live.py -v

Senza la variabile d'ambiente i test sono saltati: **non va nel gate**.

Perché esiste
-------------
Le regole della skill v9.0 vengono dal sondaggio del 17 ottobre 2026
(`REPORT-sondaggio-v9.md`). Qui quelle regole sono scritte come contratti: se
il server cambia comportamento, il test diventa rosso e va rivista la skill
(non il test). Il primo test confronta lo schema reale con la fixture: è il
controllo di obsolescenza per il maintainer.

Come chiama il server
---------------------
Il connettore BuddaLaw di claude.ai usa OAuth: non c'è un token locale. Ogni
chiamata passa da `claude -p` (Haiku, al massimo 3 turni, budget 0,20 $) con
`tools/chiama_mcp.py`, che legge il `tool_result` grezzo dallo stream e scarta
la chiamata se il modello ha cambiato gli argomenti. Costo tipico: meno di un
centesimo a chiamata.

Al primo 403, 429 o messaggio di blocco la sessione si ferma (`pytest.exit`):
nessun ritento.
"""
from __future__ import annotations

import difflib
import json
import os
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
FIXTURE = TESTS / "fixtures" / "tool_schema.json"

pytestmark = pytest.mark.skipif(
    os.environ.get("BUDDALAW_LIVE") != "1",
    reason="livello C: imposta BUDDALAW_LIVE=1 per interrogare BuddaLaw",
)

# Messaggio fisso di not_found osservato il 2026-10-17.
FRASE_NOT_FOUND = "non è un errore tecnico"


def chiama(tool: str, argomenti: dict):
    """Una chiamata; al primo blocco ferma tutta la sessione."""
    import chiama_mcp

    try:
        return chiama_mcp.chiama(tool, argomenti)
    except chiama_mcp.Bloccato as e:
        pytest.exit(f"BuddaLaw ha rifiutato o limitato la richiesta: mi fermo, nessun ritento. {e}",
                    returncode=3)


def json_di(esito) -> dict:
    assert isinstance(esito.dati, dict), f"risposta non JSON: {esito.grezzo[:300]!r}"
    return esito.dati


def risultati(esito) -> list[dict]:
    d = json_di(esito)
    assert "error" not in d, f"errore del server: {d['error']}"
    return d.get("results") or []


# ---------------------------------------------------------------------------
# T74 — obsolescenza dello schema
# ---------------------------------------------------------------------------

def _differenze_schema(vecchio: dict, nuovo: dict) -> list[str]:
    v = {t["name"]: t for t in vecchio.get("tools", [])}
    n = {t["name"]: t for t in nuovo.get("tools", [])}
    righe = []
    for nome in sorted(set(n) - set(v)):
        righe.append(f"tool NUOVO: {nome}")
    for nome in sorted(set(v) - set(n)):
        righe.append(f"tool SPARITO: {nome}")
    for nome in sorted(set(v) & set(n)):
        pv, pn = v[nome]["parameters"], n[nome]["parameters"]
        av, an = set(pv.get("properties", {})), set(pn.get("properties", {}))
        for p in sorted(an - av):
            righe.append(f"{nome}: parametro nuovo {p!r}")
        for p in sorted(av - an):
            righe.append(f"{nome}: parametro tolto {p!r}")
        for p in sorted(av & an):
            if pv["properties"][p] != pn["properties"][p]:
                righe.append(f"{nome}.{p}: definizione cambiata")
        if pv.get("required") != pn.get("required"):
            righe.append(f"{nome}: obbligatori {pv.get('required')} → {pn.get('required')}")
        if v[nome].get("description") != n[nome].get("description"):
            righe.append(f"{nome}: descrizione cambiata")
    return righe


def test_T74_schema_live_uguale_alla_fixture():
    """T74 — se BuddaLaw aggiunge, toglie o cambia un tool, questo test diventa rosso."""
    import estrai_schema

    try:
        nuovo = estrai_schema.costruisci()
    except RuntimeError as e:
        pytest.fail(f"estrazione dello schema non riuscita: {e}")
    vecchio = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if nuovo == vecchio:
        return
    sintesi = _differenze_schema(vecchio, nuovo) or ["differenze fuori dai tool (metadati)"]
    diff = "".join(difflib.unified_diff(
        json.dumps(vecchio, ensure_ascii=False, indent=2).splitlines(True),
        json.dumps(nuovo, ensure_ascii=False, indent=2).splitlines(True),
        "fixture", "server", n=1))
    pytest.fail(
        "BuddaLaw è cambiato: tool nuovi, spariti o con parametri cambiati.\n  - "
        + "\n  - ".join(sintesi)
        + "\nAggiornare la skill (SKILL.md, references, inventario) e poi la fixture con\n"
          "  python3 buddalaw/tests/tools/estrai_schema.py\n\n"
        + diff[:6000])


# ---------------------------------------------------------------------------
# get_judgement
# ---------------------------------------------------------------------------

def test_T75_cassazione_per_numero_e_anno():
    """T75 — Cassazione: dominio + numero + anno interi, senza ufficio, dà il testo."""
    d = json_di(chiama("get_judgement", {"dominio": "civile", "numero": 3285, "anno": 2022}))
    assert not d.get("not_found"), f"3285/2022 non trovata: {d}"
    assert d.get("idatto") == "ECLI:IT:CASS:2022:3285CIV", d.get("idatto")
    assert len(d.get("text") or "") > 1000, "testo assente o troppo corto"
    assert str(d.get("public_url", "")).startswith("https://platform.buddalaw.com/full-documents/civile/")


def test_T76_T45_not_found_con_messaggio_fisso():
    """T76 T45 — Sez. Un. 577/2008 non è in BuddaLaw: not_found con il messaggio fisso."""
    d = json_di(chiama("get_judgement", {"dominio": "civile", "numero": 577, "anno": 2008}))
    assert d.get("not_found") is True, (
        f"577/2008 ora risponde diversamente: rivedere T45 e la regola not_found. {str(d)[:300]}")
    assert FRASE_NOT_FOUND in (d.get("message") or "").lower(), f"messaggio cambiato: {d.get('message')!r}"


@pytest.mark.sorveglianza
def test_T77_ufficio_senza_dominio_da_falso_not_found():
    """T77 — 30201/2008 con ufficio="Cassazione civile" e senza dominio: falso not_found.

    Con dominio="civile" la stessa decisione si trova (anche se si aggiunge
    ufficio: verificato il 2026-10-17). La regola della skill «Cassazione:
    dominio, numero e anno, mai ufficio» evita entrambe le trappole. Se il primo
    controllo diventa rosso, il server ha corretto il falso not_found.
    """
    con = json_di(chiama("get_judgement", {"numero": 30201, "anno": 2008, "ufficio": "Cassazione civile"}))
    senza = json_di(chiama("get_judgement", {"dominio": "civile", "numero": 30201, "anno": 2008}))
    assert not senza.get("not_found") and senza.get("text"), f"30201/2008 con dominio: {str(senza)[:300]}"
    assert con.get("not_found") is True, "con ufficio e senza dominio ora la trova: rivedere T57"


# ---------------------------------------------------------------------------
# Date
# ---------------------------------------------------------------------------

def test_T78_data_esatta_iso_su_civile():
    """T78 — civile: data_deposito AAAA-MM-GG filtra quel solo giorno."""
    res = risultati(chiama("search_case_law", {
        "query": "responsabilità contrattuale inadempimento", "search_category": "civile",
        "data_deposito": "2022-09-23", "max_results": 3}))
    assert res, "nessun risultato per il 23/09/2022 su civile"
    date = {r.get("data_deposito") for r in res}
    assert date == {"2022-09-23"}, f"data_deposito non è un filtro esatto: {date}"


def test_T79_data_italiana_su_merito():
    """T79 — merito: data_deposito GG/MM/AAAA funziona ed è esatta."""
    res = risultati(chiama("search_case_law", {
        "query": "licenziamento", "search_category": "merito",
        "data_deposito": "06/07/2026", "max_results": 3}))
    assert res, "nessun risultato per il 06/07/2026 sul merito"
    date = {r.get("data_deposito") for r in res}
    assert date == {"06/07/2026"}, f"date restituite: {date}"


@pytest.mark.sorveglianza
def test_T79_formato_sbagliato_su_civile_da_errore():
    """T79 — civile con GG/MM/AAAA dà RetryError (regola «una sola prova nell'altro formato»)."""
    e = chiama("search_case_law", {
        "query": "responsabilità contrattuale inadempimento", "search_category": "civile",
        "data_deposito": "23/09/2022", "max_results": 3})
    assert e.is_error or "RetryError" in e.grezzo or "error" in (e.dati or {}), (
        f"il formato italiano ora è accettato su civile: rivedere la tabella delle date. {e.grezzo[:200]!r}")


# ---------------------------------------------------------------------------
# Uffici
# ---------------------------------------------------------------------------

def test_T80_T52_codiceufficio_da_list_uffici():
    """T80 T52 — list_uffici merito → codice → search_case_law con codiceufficio."""
    d = json_di(chiama("list_uffici", {"dominio": "merito"}))
    uffici = d.get("uffici") or []
    assert len(uffici) >= 100, f"solo {len(uffici)} uffici di merito"
    assert uffici[0].get("codice") is None, "la prima voce («Tutti…») non ha più codice null"
    milano = [u for u in uffici if "tribunale" in str(u.get("label", "")).lower()
              and "milano" in str(u.get("label", "")).lower() and u.get("codice")]
    assert milano, "Tribunale di Milano assente da list_uffici"
    codice = milano[0]["codice"]
    assert isinstance(codice, str) and codice.startswith("0"), f"codice non è una stringa con zeri: {codice!r}"
    res = risultati(chiama("search_case_law", {
        "query": "licenziamento per superamento del periodo di comporto", "search_category": "merito",
        "codiceufficio": codice, "max_results": 3}))
    assert res, f"codiceufficio {codice} non dà risultati"
    assert {r.get("codiceufficio") for r in res} == {codice}, "il filtro codiceufficio non è esatto"


# ---------------------------------------------------------------------------
# get_law_article
# ---------------------------------------------------------------------------

def test_T81_articolo_2043_cc():
    """T81 — art. 2043 c.c.: trovato, rubrica e URN del codice civile."""
    d = json_di(chiama("get_law_article", {"act": "codice_civile", "article": "2043"}))
    assert d.get("found") is True, str(d)[:300]
    assert d.get("heading") == "Risarcimento per fatto illecito", d.get("heading")
    assert "danno ingiusto" in (d.get("text") or "")
    assert "regio.decreto:1942-03-16;262" in (d.get("returned_urn") or ""), d.get("returned_urn")
    url = d.get("normattiva_url") or ""
    assert url.endswith("~art2043"), url
    # Sorpresa S1: oggi manca l'allegato «:2». Se compare, i link di BuddaLaw
    # tornano utilizzabili: aggiornare la sezione «Norme» della skill.
    assert ";262:2" not in url, "il normattiva_url ora contiene l'allegato: rivedere la regola sui link"


def test_T82_T54_articolo_abrogato():
    """T82 T54 — art. 594 c.p.: found con testo vuoto o rubrica ABROGATO."""
    d = json_di(chiama("get_law_article", {"act": "codice_penale", "article": "594"}))
    assert d.get("found") is True, str(d)[:300]
    assert not (d.get("text") or "").strip() or "ABROGAT" in (d.get("heading") or "").upper(), (
        f"il 594 c.p. non risulta più abrogato nel modo atteso: {d.get('heading')!r}")


# ---------------------------------------------------------------------------
# Valori di search_category
# ---------------------------------------------------------------------------

def test_T83_search_category_non_ammessa():
    """T83 — «lavoro» non esiste: errore con l'elenco dei valori."""
    d = json_di(chiama("search_case_law", {"query": "licenziamento", "search_category": "lavoro",
                                           "max_results": 1}))
    assert "error" in d, f"«lavoro» ora è accettato: aggiornare tabella e schema. {str(d)[:200]}"
    assert "tributari" in d["error"] and "eu-case-law" in d["error"], d["error"]


@pytest.mark.sorveglianza
def test_T84_T63_tributario_accettato_in_silenzio():
    """T84 T63 — «tributario» (valore non documentato) oggi non dà errore.

    Se diventa rosso il server ha cambiato comportamento: ricontrollare la
    trappola tributari/tributario nella skill.
    """
    d = json_di(chiama("search_case_law", {"query": "operazioni soggettivamente inesistenti IVA",
                                           "search_category": "tributario", "max_results": 1}))
    assert "error" not in d, f"«tributario» ora dà errore: {d['error']}"
