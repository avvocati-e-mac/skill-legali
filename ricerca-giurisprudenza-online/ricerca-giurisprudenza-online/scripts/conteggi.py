#!/usr/bin/env python3
"""Conteggi e tabelle per la bozza, calcolati dalle schede (nessun modello, nessun calcolo a mano).

Uso:  python3 conteggi.py <cartella_lavoro>

Scrive <cartella_lavoro>/conteggi.txt (conteggi per esito, ruolo_del_tema,
conseguenze_legate_al_tema come scritte, chi + numeri della ricerca) e <cartella_lavoro>/tabelle.md
(tabella degli estremi e tabella cronologica in Markdown). I file "scaricati" sono
solo quelli presenti davvero nella cartella ../pdf accanto a <cartella_lavoro>.
Solo libreria standard di Python 3.
"""
import csv
import json
import os
import re
import sys
from collections import Counter

ESITI = ["accoglie", "rigetta", "inammissibile", "improcedibile", "altro"]
RUOLI = ["decisivo", "concorrente", "obiter", "marginale"]
CHI = ["avvocato", "parte", "giudice", "ctu", "altro"]
RE_DATA = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def leggi_csv(percorso):
    if not os.path.isfile(percorso):
        return []
    with open(percorso, encoding="utf-8-sig", newline="") as f:
        testo = f.read()
    if not testo.strip():
        return []
    prima = testo.splitlines()[0]
    delim = ";" if prima.count(";") > prima.count(",") else ","
    return [{(k or "").strip(): (v or "").strip() for k, v in r.items()}
            for r in csv.DictReader(testo.splitlines(), delimiter=delim)]


def data_it(s):
    m = RE_DATA.match(s or "")
    return "%s/%s/%s" % (m.group(3), m.group(2), m.group(1)) if m else (s or "non indicato")


def chiave_data(s):
    return s if RE_DATA.match(s or "") else "9999-99-99"


def cella(s):
    s = str(s if s not in (None, "") else "non indicato")
    return s.replace("|", "/").replace("\n", " ").strip()


def tabella(intestazioni, righe):
    out = ["| " + " | ".join(intestazioni) + " |",
           "|" + "|".join(["---"] * len(intestazioni)) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in righe]
    return "\n".join(out)


def conta(titolo, valori_attesi, valori):
    c = Counter(valori)
    righe = [titolo]
    for v in valori_attesi:
        righe.append("  %-34s %d" % (v, c.pop(v, 0)))
    for v, n in sorted(c.items(), key=lambda x: str(x[0])):
        righe.append("  %-34s %d   <- valore non ammesso" % (v, n))
    return righe


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    lav = os.path.abspath(os.path.expanduser(argv[1]))
    if not os.path.isdir(lav):
        print("Cartella di lavoro non trovata: %s" % lav)
        return 2

    elenco = leggi_csv(os.path.join(lav, "elenco.csv"))
    scartati = {r.get("id") for r in leggi_csv(os.path.join(lav, "scartati.csv"))}
    ids_elenco = [r.get("id", "") for r in elenco]

    schede, illeggibili = [], []
    dir_schede = os.path.join(lav, "schede")
    if os.path.isdir(dir_schede):
        for nome in sorted(os.listdir(dir_schede)):
            if not nome.endswith(".json"):
                continue
            i = nome[:-5]
            try:
                with open(os.path.join(dir_schede, nome), encoding="utf-8-sig") as f:
                    d = json.load(f)
                if not isinstance(d, dict):
                    raise ValueError("non è un oggetto")
                d["_id"] = i
                schede.append(d)
            except Exception as e:
                illeggibili.append("%s (%s)" % (nome, e))

    # file davvero presenti in ../pdf
    dir_pdf = os.path.join(os.path.dirname(lav), "pdf")
    presenti = {}
    if os.path.isdir(dir_pdf):
        for nome in os.listdir(dir_pdf):
            p = os.path.join(dir_pdf, nome)
            base, ext = os.path.splitext(nome)
            if ext.lower() in (".pdf", ".html", ".htm") and os.path.getsize(p) > 0:
                presenti[base.rsplit("_", 1)[-1]] = nome
    scaricati = sorted(i for i in set(ids_elenco) if i in presenti)

    def est(s, k):
        e = s.get("estremi")
        return e.get(k) if isinstance(e, dict) else None

    out = []
    out.append("CONTEGGI (da %d schede)" % len(schede))
    out.append("")
    out.append("Numeri della ricerca")
    out.append("  Candidati in elenco.csv:             %d" % len(ids_elenco))
    out.append("  Scartati (scartati.csv):             %d" % len(scartati))
    out.append("  Schede compilate (letti):            %d" % len(schede))
    out.append("  Scaricati (file presenti in pdf/):   %d" % len(scaricati))
    if illeggibili:
        out.append("  Schede illeggibili (escluse):        %d -> %s" % (len(illeggibili), "; ".join(illeggibili)))
    mancano = [i for i in ids_elenco if i not in presenti and i not in scartati]
    if mancano and os.path.isdir(dir_pdf):
        out.append("  In elenco ma senza file in pdf/:     %s" % ", ".join(mancano))
    out.append("")
    out += conta("Per esito", ESITI, [s.get("esito") for s in schede])
    out.append("")
    out += conta("Per ruolo_del_tema", RUOLI, [s.get("ruolo_del_tema") for s in schede])
    out.append("")
    cons = []
    for s in schede:
        v = s.get("conseguenze_legate_al_tema")
        v = v if isinstance(v, list) else [v]
        cons += [" ".join(x.replace("’", "'").replace("‘", "'").lower().split()) if isinstance(x, str) else x
                 for x in v]
    # conseguenze libere: contate come scritte (normalizzate), dalla più frequente
    freq = Counter(cons).most_common()
    freq.sort(key=lambda x: (-x[1], str(x[0])))
    out.append("Per conseguenze_legate_al_tema (frasi libere; una scheda può averne più d'una)")
    out += ["  %-50s %d" % (v, n) for v, n in freq] or ["  (nessuna scheda)"]
    out.append("")
    out += conta("Per chi (chi usa o solleva il tema)", CHI, [s.get("chi") for s in schede])
    out.append("")
    out += conta("Per tema_causa_dell_esito", ["si", "no", "non chiaro"],
                 [s.get("tema_causa_dell_esito") for s in schede])
    out.append("")
    out += conta("Per testo_letto", ["integrale", "parziale", "no"], [s.get("testo_letto") for s in schede])
    testo = "\n".join(out) + "\n"

    ordinate = sorted(schede, key=lambda s: (chiave_data(est(s, "data_decisione")), s["_id"]))
    t1 = tabella(
        ["id", "Ufficio", "Sezione", "Tipo", "Data decisione", "Data deposito", "Numero", "R.G.",
         "Giudice o collegio"],
        [[cella(s["_id"]), cella(est(s, "ufficio")), cella(est(s, "sezione")), cella(est(s, "tipo")),
          data_it(est(s, "data_decisione")), data_it(est(s, "data_deposito")), cella(est(s, "numero")),
          cella(est(s, "rg")), cella(est(s, "giudice"))] for s in ordinate])
    t2 = tabella(
        ["Data decisione", "id", "Ufficio", "Numero", "Peso del tema", "Esito",
         "Conseguenze legate al tema"],
        [[data_it(est(s, "data_decisione")), cella(s["_id"]), cella(est(s, "ufficio")),
          cella(est(s, "numero")), cella(s.get("ruolo_del_tema")), cella(s.get("esito")),
          cella("; ".join(s["conseguenze_legate_al_tema"]) if isinstance(s.get("conseguenze_legate_al_tema"), list)
                else s.get("conseguenze_legate_al_tema"))] for s in ordinate])
    md = "## Tabella degli estremi\n\n%s\n\n## Tabella cronologica\n\n%s\n" % (t1, t2)

    with open(os.path.join(lav, "conteggi.txt"), "w", encoding="utf-8") as f:
        f.write(testo)
    with open(os.path.join(lav, "tabelle.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print(testo)
    print("Scritti: %s e %s" % (os.path.join(lav, "conteggi.txt"), os.path.join(lav, "tabelle.md")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
