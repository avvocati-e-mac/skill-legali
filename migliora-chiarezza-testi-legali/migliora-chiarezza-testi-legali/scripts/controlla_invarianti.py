#!/usr/bin/env python3
"""Controllo meccanico di una riscrittura: confronta il testo originale con il DOPO.

Uso (serve solo Python 3, nessuna libreria esterna):

    python3 scripts/controlla_invarianti.py bozza.txt
    python3 scripts/controlla_invarianti.py --prima originale.txt --dopo riscritto.txt

Nel primo caso il file contiene la risposta con i blocchi PRIMA:, DOPO:,
Motivo: ed eventualmente TESTO RISCRITTO:. Il controllo segnala cio' che
compare nel DOPO (o nel TESTO RISCRITTO) e non nel PRIMA: numeri, date,
esimenti, intensificatori, frasi da IA, fonti; e cio' che sparisce: garanzie,
eccezioni, "si obbliga a". Non giudica lo stile: se segnala qualcosa,
correggi oppure spiega nel Motivo perche' la modifica e' voluta.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEADER = re.compile(
    r"^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*)?(PRIMA|DOPO|Motivo|TESTO RISCRITTO|Sommario|Scheda|Controllo|PROPOSTA)"
    r"(?:\s*\([^:\n]*\))?(?::(?:\*\*)?|\*\*|[ \t]*$)[ \t]*",
    re.IGNORECASE | re.MULTILINE,
)

AGGIUNTE = {
    "esimente": r"\bcaso fortuito\b|\bforza maggiore\b|\bnon (?:a lui |a lei |loro )?imputabil\w*",
    "intensificatore": r"\b(?:interamente|totalmente|assolutamente|palese(?:mente)?|evidente(?:mente)?|chiaramente|macroscopic\w*|gravissim\w*|del tutto|pienamente|pacificamente|indubbiamente|radicalmente|esclusivamente)\b",
    "fatto di comodo": r"\binvano\b|\b(?:priv[ao]|senza) (?:di )?(?:alcun )?riscontro\b",
    "frase da IA": r"\b(?:è|e') (?:importante|fondamentale|cruciale|essenziale) (?:sottolineare|notare|evidenziare|ricordare)\b"
    r"|\bvale la pena\b|\bgioca(?:no)? un ruolo\b|\bin (?:conclusione|sintesi|definitiva),|\bspero (?:che )?(?:questo|sia)\b"
    r"|\bversione (?:riscritta|migliorata|più chiara)\b|\bpotrebber?o? (?:eventualmente|potenzialmente)\b|" "\u2014",
    "fonte": r"\bartt?\.\s*\d+[^\n;,.]*|\bCass(?:azione|\.)[^\n;]{0,40}?\d{2,}|\bd\.\s?lgs\.?\s*(?:n\.\s*)?\d+|\bD\.M\.\s*(?:n\.\s*)?\d+",
}

CONSERVARE = {
    "garanzia ('garantisce')": r"\bgarantisc\w*",
    "eccezione ('salvo', 'tranne', 'eccetto')": r"\b(?:salvo|salva|tranne|eccetto|ad eccezione)\b",
    "'a pena di'": r"\ba pena di\b",
    "'si obbliga a' (effetto obbligatorio)": r"\bsi obblig\w* a (?:vend|trasfer|ced|costitu|don)\w*",
}

NUMERI = re.compile(
    r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b|\b\d{1,3}(?:\.\d{3})+(?:,\d+)?\b"
    r"|\b\d+(?:,\d+)?\s*(?:%|euro|€|giorni|gg|mesi|anni|ore)\b|\b\d{2,}\b",
    re.IGNORECASE,
)
PERSONE = {"nostro": r"\bnostr[aoie]\b", "Vostro": r"\bvostr[aoie]\b"}


def sezione(testo: str, nome: str) -> str:
    trovate = list(HEADER.finditer(testo))
    blocchi = []
    for i, m in enumerate(trovate):
        if m.group(1).lower() == nome.lower():
            fine = trovate[i + 1].start() if i + 1 < len(trovate) else len(testo)
            blocchi.append(togli_virgolette_esterne(testo[m.end():fine].strip()))
    return "\n".join(blocchi)


def togli_virgolette_esterne(blocco: str) -> str:
    """Il DOPO scritto tutto tra virgolette non va trattato come una citazione."""
    m = re.match(r'^\s*(?:\*\*)?["“«](.*)["”»](?:\*\*)?\s*$', blocco, re.DOTALL)
    if m and not re.search(r'["“”«»]', m.group(1)):
        return m.group(1).strip()
    return blocco


def senza_virgolettati(testo: str) -> str:
    return re.sub(r"[\"“«][^\"”»]{0,400}[\"”»]", " ", testo)


def controlla(prima: str, dopo: str) -> list[str]:
    avvisi: list[str] = []
    p, d = senza_virgolettati(prima), senza_virgolettati(dopo)
    cifre_prima = set(re.findall(r"\d+", prima))
    nuovi = sorted({n.group(0) for n in NUMERI.finditer(dopo)} - {n.group(0) for n in NUMERI.finditer(prima)})
    nuovi = [n for n in nuovi if re.sub(r"\D", "", n) not in cifre_prima]
    if nuovi:
        avvisi.append("Numeri, date o termini che nel testo originale non ci sono: " + ", ".join(nuovi))
    for etichetta, schema in AGGIUNTE.items():
        prima_n = len(re.findall(schema, p, re.IGNORECASE))
        dopo_n = len(re.findall(schema, d, re.IGNORECASE))
        if dopo_n > prima_n:
            esempi = sorted({m.group(0).strip() for m in re.finditer(schema, d, re.IGNORECASE)})[:3]
            avvisi.append(f"Aggiunto nel DOPO ({etichetta}): " + ", ".join(esempi))
    for etichetta, schema in CONSERVARE.items():
        if re.search(schema, p, re.IGNORECASE) and not re.search(schema, d, re.IGNORECASE):
            avvisi.append(f"Sparito nel DOPO: {etichetta}")
    if re.search(r"\b(?:vende|trasferisce|cede)\b", d, re.IGNORECASE) and re.search(CONSERVARE["'si obbliga a' (effetto obbligatorio)"], p, re.IGNORECASE):
        avvisi.append("Attenzione: il DOPO usa 'vende/trasferisce/cede' dove il PRIMA diceva 'si obbliga a'.")
    for persona, schema in PERSONE.items():
        if re.search(schema, d, re.IGNORECASE) and not re.search(schema, p, re.IGNORECASE):
            avvisi.append(f"Compare '{persona}' nel DOPO ma non nel PRIMA: verifica chi scrive e a chi.")
    return avvisi


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("risposta", nargs="?", type=Path, help="file con i blocchi PRIMA:/DOPO:")
    parser.add_argument("--prima", type=Path)
    parser.add_argument("--dopo", type=Path)
    args = parser.parse_args(argv)
    if args.prima and args.dopo:
        prima = togli_virgolette_esterne(args.prima.read_text(encoding="utf-8"))
        dopo = togli_virgolette_esterne(args.dopo.read_text(encoding="utf-8"))
    elif args.risposta:
        testo = args.risposta.read_text(encoding="utf-8")
        prima = sezione(testo, "PRIMA")
        dopo = "\n".join(x for x in (sezione(testo, "DOPO"), sezione(testo, "TESTO RISCRITTO")) if x)
    else:
        testo = sys.stdin.read()
        prima = sezione(testo, "PRIMA")
        dopo = "\n".join(x for x in (sezione(testo, "DOPO"), sezione(testo, "TESTO RISCRITTO")) if x)
    if not prima or not dopo:
        print("Non trovo i blocchi PRIMA: e DOPO: (oppure usa --prima e --dopo).")
        return 2
    avvisi = controlla(prima, dopo)
    if not avvisi:
        print("Controllo: nessuna violazione meccanica trovata. Restano da verificare a occhio senso e registro.")
        return 0
    print("Controllo: da verificare prima di consegnare")
    for avviso in avvisi:
        print(f"- {avviso}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
