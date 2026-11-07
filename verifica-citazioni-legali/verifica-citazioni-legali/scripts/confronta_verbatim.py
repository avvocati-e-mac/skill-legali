#!/usr/bin/env python3
"""Confronto deterministico tra un virgolettato dell'atto e il testo della fonte.

Normalizza apostrofi, virgolette, trattini, spazi, sillabazione a fine riga e
legature OCR; tratta le ellissi («[…]», «(…)», «...», «…») come separatori di
segmenti, che devono comparire nella fonte nell'ordine dato.

Esiti:
  IDENTICA   tutti i segmenti presenti alla lettera (dopo normalizzazione)
  VARIANTE   segmento simile ma diverso: mostra le parole tolte/aggiunte
  ASSENTE    nessun passo abbastanza simile nel testo letto
  (ASSENTE vale per QUEL testo: non prova che la frase non esista altrove.)

Uso singolo:
  python3 confronta_verbatim.py --fonte SENTENZA.(txt|md|pdf|docx|odt) \
          --citazione "testo tra virgolette"
Uso a lotti (JSON: lista di {"id", "citazione", "fonte"}):
  python3 confronta_verbatim.py --lotto citazioni.json [--out esito.md]

Codice d'uscita: 0 se tutte IDENTICHE, 1 se c'è almeno una VARIANTE o ASSENTE.
"""
import argparse
import difflib
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estrai_citazioni import carica_testo  # noqa: E402

SOGLIA_VARIANTE = 0.72

SOSTITUZIONI = {
    "\u2019": "'", "\u2018": "'", "\u02bc": "'", "`": "'", "\u00b4": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u00ab": '"', "\u00bb": '"',
    "\u2013": "-", "\u2014": "-", "\u2212": "-", "\u2010": "-", "\u2011": "-",
    "\ufb01": "fi", "\ufb02": "fl", "\u00a0": " ", "\u00ad": "", "~": " ",
}
ELLISSI = r"\[\s*(?:\.\.\.|…)\s*\]|\(\s*(?:\.\.\.|…)\s*\)|\.\.\.|…"


def normalizza(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in SOSTITUZIONI.items():
        s = s.replace(a, b)
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)          # sillabazione a fine riga
    s = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", s)        # comandi LaTeX
    s = re.sub(r"\s*'\s*", "'", s)                          # "l' attività" -> "l'attività"
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def parole(s):
    return re.findall(r"\w+(?:'\w+)?|[^\w\s]", s.lower())


def cerca_segmento(seg, fonte_norm, fonte_tok, da_tok):
    """Restituisce (esito, rapporto, inizio_tok, fine_tok, diff)."""
    st = parole(seg)
    if not st:
        return ("IDENTICA", 1.0, da_tok, da_tok, [])
    n = len(st)
    # 1) ricerca esatta sui token, a partire da da_tok
    for i in range(da_tok, len(fonte_tok) - n + 1):
        if fonte_tok[i:i + n] == st:
            return ("IDENTICA", 1.0, i, i + n, [])
    # 2) ricerca approssimata: candidati ancorati alle parole più lunghe
    chiavi = sorted(set(w for w in st if len(w) > 4), key=len, reverse=True)[:6]
    candidati = set()
    for k in chiavi:
        idx_seg = st.index(k)
        for j, w in enumerate(fonte_tok[da_tok:], start=da_tok):
            if w == k:
                candidati.add(max(da_tok, j - idx_seg))
    migliore = (0.0, None, None)
    for c in candidati:
        # la fonte può avere parole in più (inserzioni) o in meno: finestre variabili
        for delta in range(-max(3, n // 4), max(4, int(n * 0.5)) + 1):
            fin = min(len(fonte_tok), c + n + delta)
            fin = max(fin, c + 1)
            r = difflib.SequenceMatcher(None, st, fonte_tok[c:fin], autojunk=False).ratio()
            if r > migliore[0]:
                migliore = (r, c, fin)
    r, c, fin = migliore
    if (c is None or r < SOGLIA_VARIANTE) and n >= 12:
        # 3) inciso omesso senza ellissi: cerca le due metà vicine e in ordine
        meta = n // 2
        a = cerca_segmento(" ".join(st[:meta]), fonte_norm, fonte_tok, da_tok)
        if a[0] != "ASSENTE":
            b = cerca_segmento(" ".join(st[meta:]), fonte_norm, fonte_tok, a[3])
            if b[0] != "ASSENTE" and 0 < b[2] - a[3] <= 60:
                omesso = " ".join(fonte_tok[a[3]:b[2]])
                diff = a[4] + [{"atto": "(nulla: inciso omesso senza ellissi)", "fonte": omesso}] + b[4]
                return ("VARIANTE", min(a[1], b[1]), a[2], b[3], diff)
    if c is None or r < SOGLIA_VARIANTE:
        return ("ASSENTE", r, None, None, [])
    diff = []
    for op in difflib.SequenceMatcher(None, st, fonte_tok[c:fin], autojunk=False).get_opcodes():
        tag, i1, i2, j1, j2 = op
        if tag == "equal":
            continue
        diff.append({"atto": " ".join(st[i1:i2]), "fonte": " ".join(fonte_tok[c + j1:c + j2])})
    return ("VARIANTE", r, c, fin, diff)


def togli_intestazioni(testo):
    """Toglie righe ripetute ≥ 3 volte (intestazioni, firme digitali, piè di
    pagina) e numeri di pagina isolati: spezzano le frasi a cavallo di pagina."""
    righe = testo.splitlines()
    conta = {}
    for r in righe:
        k = r.strip()
        if len(k) > 12:
            conta[k] = conta.get(k, 0) + 1
    ripetute = {k for k, c in conta.items() if c >= 3}
    tenute = [r for r in righe
              if r.strip() not in ripetute and not re.fullmatch(r"\s*(?:pag\.?\s*)?\d{1,3}\s*", r)]
    return "\n".join(tenute)


def confronta(citazione, testo_fonte):
    fonte_norm = normalizza(togli_intestazioni(testo_fonte))
    fonte_tok = parole(fonte_norm)
    segmenti = [s.strip(" ,;:\"'") for s in re.split(ELLISSI, normalizza(citazione))]
    segmenti = [s for s in segmenti if parole(s)]
    esiti, da, peggiore = [], 0, "IDENTICA"
    ordine = {"IDENTICA": 0, "VARIANTE": 1, "ASSENTE": 2}
    for seg in segmenti:
        e, r, i, f, diff = cerca_segmento(seg, fonte_norm, fonte_tok, da)
        if e == "ASSENTE" and da > 0:      # forse fuori ordine: riprova dall'inizio
            e2 = cerca_segmento(seg, fonte_norm, fonte_tok, 0)
            if e2[0] != "ASSENTE":
                e, r, i, f, diff = e2
                diff = diff + [{"atto": "(segmento fuori ordine)", "fonte": ""}]
                e = "VARIANTE"
        ctx = " ".join(fonte_tok[max(0, (i or 0) - 15):(f or 0) + 15]) if i is not None else ""
        esiti.append({"segmento": seg, "esito": e, "somiglianza": round(r, 3),
                      "diff": diff, "contesto_fonte": ctx})
        if f is not None:
            da = f
        if ordine[e] > ordine[peggiore]:
            peggiore = e
    return {"esito": peggiore, "segmenti": esiti}


def stampa(idc, citazione, ris):
    righe = ["### %s — %s" % (idc, ris["esito"]), "", "Atto: «%s»" % citazione.strip(), ""]
    for s in ris["segmenti"]:
        seg = s["segmento"] if len(s["segmento"]) <= 200 else s["segmento"][:200] + "…"
        righe.append("- Segmento «%s»: **%s** (somiglianza %.2f)" % (seg, s["esito"], s["somiglianza"]))
        for d in s["diff"]:
            righe.append("  - atto: «%s» → fonte: «%s»" % (d["atto"], d["fonte"]))
        if s["contesto_fonte"]:
            righe.append("  - contesto nella fonte: …%s…" % s["contesto_fonte"][:400])
    return "\n".join(righe)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fonte")
    ap.add_argument("--citazione")
    ap.add_argument("--lotto", help="JSON: lista di {id, citazione, fonte}")
    ap.add_argument("--out", help="scrive il resoconto Markdown qui")
    ap.add_argument("--json", action="store_true", help="stampa anche il JSON")
    args = ap.parse_args()

    if args.lotto:
        with open(args.lotto, encoding="utf-8") as f:
            voci = json.load(f)
    elif args.fonte and args.citazione:
        voci = [{"id": "Q1", "citazione": args.citazione, "fonte": args.fonte}]
    else:
        ap.error("servono --fonte e --citazione, oppure --lotto")

    cache, blocchi, risultati, tutto_ok = {}, [], [], True
    for v in voci:
        if v["fonte"] not in cache:
            cache[v["fonte"]] = carica_testo(v["fonte"])[0]
        ris = confronta(v["citazione"], cache[v["fonte"]])
        tutto_ok &= ris["esito"] == "IDENTICA"
        risultati.append({"id": v.get("id"), **ris})
        blocchi.append(stampa(v.get("id", "Q"), v["citazione"], ris))
    rapporto = "# Confronto verbatim\n\n" + "\n\n".join(blocchi) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(rapporto)
    print(rapporto)
    if args.json:
        print(json.dumps(risultati, ensure_ascii=False, indent=2))
    sys.exit(0 if tutto_ok else 1)


if __name__ == "__main__":
    main()
