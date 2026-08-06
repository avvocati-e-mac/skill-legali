"""
Livello C — verifica di conformità contro l'API Normattiva (richiede rete).

Perché esiste
-------------
`test_normattiva.py` verifica che `build_urn_link()` riproduca l'URL scritto a
mano in `cases.json`. Funzione e fixture codificano la stessa convinzione:
è una tautologia. Nessuno dei suoi 1.400 assert poteva scoprire che la legge
fallimentare aveva la data sbagliata, perché
`regio.decreto:1942-01-16;267:1~art67` è un URN **formalmente perfetto** che
punta al nulla.

E non lo si poteva scoprire nemmeno cliccando: il portale Normattiva risponde
con una pagina praticamente sempre, anche a URN inventati.

**L'unico oracolo è l'API.** Questo file interroga davvero Normattiva e verifica
che il numero d'articolo restituito coincida con quello richiesto.

Esecuzione
----------
    NORMATTIVA_LIVE=1 pytest test_api_live.py -v

Senza la variabile d'ambiente i test vengono saltati: **non va nel gate**.
L'endpoint è un servizio interno del portale, non un'API pubblica versionata:
può cambiare senza preavviso, e un rosso qui non significa che la skill sia
sbagliata. Eseguirlo a mano, o al massimo una volta a settimana.

Cosa NON viene verificato, e perché
-----------------------------------
- **Lunghezza o hash del testo**: cambiano a ogni novella. L'art. 51 T.U.I.R. è
  passato da 23.681 a 69 caratteri quando è stato abrogato.
- **Il portale**: risponde 200 a tutto.
- **L'uguaglianza fra due URN**: `~art9999` restituisce la stessa pagina di
  `~art1` e `262:9` la stessa di `262`. Trovarli uguali non prova nulla.
"""

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

API = ("https://api.normattiva.it/t/normattiva.api/bff-opendata"
       "/v1/api/v1/atto/dettaglio-atto-urn")
PAUSA = 0.2   # cortesia verso un servizio pubblico gratuito
TIMEOUT = 30

live = pytest.mark.skipif(
    not os.environ.get("NORMATTIVA_LIVE"),
    reason="serve rete: esegui con NORMATTIVA_LIVE=1",
)


def interroga(urn: str) -> tuple[int, str]:
    """Restituisce (codice HTTP, testo dell'articolo ripulito dai tag).

    Gestisce le DUE forme di risposta dell'API: per alcuni atti (d.lgs.
    36/2023, TUEL, T.U. Edilizia) `data.atto` è `null` e il contenuto sta in
    `data.lista`. Chi legge solo `data.atto` classifica come rotte tre voci
    perfettamente corrette.
    """
    richiesta = urllib.request.Request(
        API,
        data=json.dumps({"urn": urn}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        grezzo = urllib.request.urlopen(richiesta, timeout=TIMEOUT).read()
        stato = 200
    except urllib.error.HTTPError as e:
        grezzo, stato = e.read(), e.code
    finally:
        time.sleep(PAUSA)

    try:
        corpo = json.loads(grezzo)
    except json.JSONDecodeError:
        return stato, ""

    dati = corpo.get("data") or {}
    atto = dati.get("atto") or {}
    html = atto.get("articoloHtml") or ""
    if not html and dati.get("lista"):
        html = (dati["lista"][0] or {}).get("articoloHtml") or ""

    return stato, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


ORDINALI = ("bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|"
            "undecies|duodecies|terdecies|quaterdecies")

# «Art. 2645-ter», «Art. 17 Obblighi…», «CODICE CIVILE Art. 1. (Capacità…)»
_INTESTAZIONE = re.compile(
    rf"\bArt\.?\s*(\d+)\s*-?\s*({ORDINALI})?\b", re.IGNORECASE)

# Incipit che tradiscono un preambolo restituito al posto dell'articolo.
_PREAMBOLO = re.compile(
    r"IL PRESIDENTE DELLA REPUBBLICA|Visti gli articoli|Visto l'\s*art"
    r"|La Camera dei deputati|VITTORIO EMANUELE|PROMULGA", re.IGNORECASE)


def numero_articolo(testo: str) -> str | None:
    """Estrae il numero d'articolo dall'intestazione, o None.

    - tollera «Art. 416-bis» e «Art. 416bis»: Normattiva usa il trattino nel
      testo ma non nell'URN, quindi si normalizza togliendolo;
    - tollera un titolo che precede («CODICE DI PROCEDURA CIVILE Art. 1.»);
    - il suffisso è riconosciuto solo fra gli ordinali reali, altrimenti
      «Art. 17 Obblighi del datore» diventerebbe l'articolo «17obblighi».

    Restituisce None se nei primi 200 caratteri non c'è un'intestazione, o se
    il testo è chiaramente un preambolo (vedi `e_preambolo`).
    """
    m = _INTESTAZIONE.search(testo[:200])
    if not m:
        return None
    return (m.group(1) + (m.group(2) or "")).lower()


def e_preambolo(testo: str) -> bool:
    """Vero se la risposta è la formula di promulgazione, non l'articolo.

    Su molti atti moderni `~art1` restituisce il preambolo con HTTP 200 e un
    testo plausibile: è la trappola più silenziosa dell'API.
    """
    return bool(_PREAMBOLO.search(testo[:300]))


def carica_casi():
    return json.loads((Path(__file__).parent / "cases.json").read_text(encoding="utf-8"))


# Alcuni articoli sono stati abrogati: la risposta e' corretta ma corta.
ABROGATO = re.compile(r"\bABROGAT", re.IGNORECASE)


@live
@pytest.mark.parametrize(
    "caso", [c for c in carica_casi() if c.get("articolo")],
    ids=lambda c: c["id"],
)
def test_l_articolo_restituito_e_quello_richiesto(caso):
    """L'assert che avrebbe scoperto entrambi gli errori della lookup.

    Non basta che l'API risponda 200: deve restituire **l'articolo chiesto**.
    Con l'allegato sbagliato risponde 200 e restituisce il preambolo del regio
    decreto, che sembra un successo.
    """
    urn = caso["url_atteso"].split("N2Ls?", 1)[1]
    stato, testo = interroga(urn)

    assert stato == 200, f"{caso['id']} {caso['desc']}: HTTP {stato} per {urn}"
    assert testo, f"{caso['id']}: risposta senza testo per {urn}"

    if ABROGATO.search(testo) and len(testo) < 400:
        pytest.skip(f"{caso['id']}: articolo abrogato — serve !vig= per il testo")

    assert not e_preambolo(testo), (
        f"{caso['id']} {caso['desc']}: ricevuto il PREAMBOLO invece dell'articolo. "
        f"Di solito significa allegato mancante o `~art1` su un atto moderno. "
        f"Inizio: {testo[:90]!r}"
    )

    atteso = f"{caso['articolo']}{(caso.get('art_suffix') or '')}".lower()
    ottenuto = numero_articolo(testo)

    assert ottenuto is not None, (
        f"{caso['id']}: nessuna intestazione «Art. N» nei primi 200 caratteri. "
        f"Inizio: {testo[:90]!r}"
    )
    assert ottenuto == atteso, (
        f"{caso['id']} {caso['desc']}: chiesto art. {atteso}, ricevuto art. {ottenuto}. "
        f"URN: {urn}"
    )


# ── Casi negativi: se questi PASSANO, il controllo non funziona ───────────────

NEGATIVI = [
    ("c.c. senza l'allegato :2",
     "urn:nir:stato:regio.decreto:1942-03-16;262~art2043"),
    ("cod. navigazione senza l'allegato :1",
     "urn:nir:stato:regio.decreto:1942-03-30;327~art422"),
    ("c.p.a. senza l'allegato :2",
     "urn:nir:stato:decreto.legislativo:2010-07-02;104~art29"),
    ("l.fall. con la vecchia data sbagliata",
     "urn:nir:stato:regio.decreto:1942-01-16;267:1~art67"),
    ("articolo inesistente",
     "urn:nir:stato:legge:1970-05-20;300~art9999"),
    ("atto inesistente",
     "urn:nir:stato:legge:1999-01-01;9999~art1"),
]


@live
@pytest.mark.parametrize("descrizione,urn", NEGATIVI, ids=[n for n, _ in NEGATIVI])
def test_gli_urn_sbagliati_devono_fallire(descrizione, urn):
    """Un controllo che non sa dire di no non è un controllo."""
    stato, testo = interroga(urn)
    ok_articolo = stato == 200 and numero_articolo(testo) is not None
    assert not ok_articolo, (
        f"{descrizione}: l'API ha restituito un articolo per un URN sbagliato. "
        f"Il controllo non discrimina. URN: {urn}"
    )


SINTASSI_INVALIDA = [
    ("comma nell'URN", "urn:nir:stato:legge:1970-05-20;300~art7-com1"),
    ("lettera nell'URN", "urn:nir:stato:legge:1970-05-20;300~art7-com1-letb"),
    ("suffisso col trattino", "urn:nir:stato:regio.decreto:1942-03-16;262:2~art2645-ter"),
    ("partizione ~all", "urn:nir:stato:regio.decreto:1942-03-16;262~all1"),
    ("partizione ~pre", "urn:nir:stato:regio.decreto:1940-10-28;1443:1~pre"),
]


@live
@pytest.mark.parametrize("descrizione,urn", SINTASSI_INVALIDA,
                         ids=[n for n, _ in SINTASSI_INVALIDA])
def test_le_sintassi_che_la_skill_non_deve_generare(descrizione, urn):
    """Documenta perché comma, lettera e partizioni sono fuori dalla skill.

    Se un giorno Normattiva le implementasse, questo test diventerebbe rosso:
    sarebbe il momento di rimetterle in `lookup-extended.md`.
    """
    stato, _ = interroga(urn)
    assert stato != 200, (
        f"{descrizione}: ora l'API accetta questa sintassi ({urn}). "
        f"Rivedere la sezione «Partizioni sotto-articolo» di lookup-extended.md."
    )


@live
def test_il_suffisso_attaccato_funziona():
    """Controprova positiva del test precedente: senza trattino va."""
    stato, testo = interroga("urn:nir:stato:regio.decreto:1942-03-16;262:2~art2645ter")
    assert stato == 200 and numero_articolo(testo) == "2645ter", (
        f"~art2645ter dovrebbe funzionare: HTTP {stato}, testo {testo[:80]!r}"
    )
