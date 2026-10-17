#!/usr/bin/env python3
"""Inventario delle citazioni di un atto: giurisprudenza, norme, virgolettati,
documenti di causa, link e affermazioni senza fonte.

Formati: .tex .md .markdown .txt (lettura diretta, posizione = riga),
.docx .odt (via pandoc, posizione = paragrafo o nota), .pdf (via pdftotext,
posizione = pagina). Nessun accesso alla rete.

Uso:
  python3 estrai_citazioni.py ATTO --out CARTELLA [--pattern FILE.json]
                              [--solo-giurisprudenza | --solo-norme]

Scrive CARTELLA/inventario.md e CARTELLA/inventario.json. L'inventario è un
punto di partenza: le regex non vedono tutto (rinvii come «conf.», «ivi»,
dottrina). La skill prevede una seconda lettura integrale dell'atto.
"""
import argparse
import bisect
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata

QUI = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- caricamento

def carica_testo(percorso):
    """Restituisce (testo, tipo_posizione, mappa) dove mappa serve a tradurre
    un offset in posizione leggibile."""
    est = os.path.splitext(percorso)[1].lower()
    if est in (".tex", ".md", ".markdown", ".txt"):
        with open(percorso, encoding="utf-8", errors="replace") as f:
            return f.read(), "riga", est
    if est in (".docx", ".odt"):
        if not shutil.which("pandoc"):
            sys.exit("pandoc non trovato: serve per leggere .docx e .odt "
                     "(https://pandoc.org). In alternativa esporta l'atto in .md.")
        cmd = ["pandoc", percorso, "-t", "plain", "--wrap=none"]
        if est == ".docx":
            cmd.insert(2, "--track-changes=accept")
        out = subprocess.run(cmd, capture_output=True, text=True)
        if out.returncode != 0:
            sys.exit("pandoc ha restituito un errore: " + out.stderr.strip())
        return out.stdout, "paragrafo", est
    if est == ".pdf":
        if not shutil.which("pdftotext"):
            sys.exit("pdftotext non trovato: serve per leggere i PDF (poppler).")
        out = subprocess.run(["pdftotext", "-enc", "UTF-8", percorso, "-"],
                             capture_output=True, text=True)
        if not out.stdout.strip():
            sys.exit("Il PDF non contiene testo (scansione?): serve un OCR, "
                     "per esempio ocrmypdf, prima dell'estrazione.")
        return out.stdout, "pagina", est
    if est == ".doc":
        sys.exit("Il formato .doc non è supportato: salvalo come .docx o .odt.")
    sys.exit("Formato non supportato: " + est)


class Posizioni:
    """Traduce offset in riga / paragrafo / nota / pagina."""

    def __init__(self, testo, tipo):
        self.tipo = tipo
        self.inizi_riga = [0] + [m.end() for m in re.finditer(r"\n", testo)]
        if tipo == "paragrafo":
            # paragrafi = blocchi separati da righe vuote; le note di pandoc
            # plain stanno in fondo come "[1] testo"
            self.blocchi = [0] + [m.end() for m in re.finditer(r"\n[ \t]*\n+", testo)]
            self.note = {}
            for m in re.finditer(r"(?m)^\[(\d+)\][ \t]", testo):
                self.note[m.start()] = m.group(1)
            self.inizio_note = min(self.note) if self.note else None
        if tipo == "pagina":
            self.pagine = [0] + [m.end() for m in re.finditer(r"\f", testo)]

    def di(self, offset):
        if self.tipo == "riga":
            return "riga %d" % bisect.bisect_right(self.inizi_riga, offset)
        if self.tipo == "paragrafo":
            if self.inizio_note is not None and offset >= self.inizio_note:
                inizi = sorted(self.note)
                k = inizi[bisect.bisect_right(inizi, offset) - 1]
                return "nota %s" % self.note[k]
            return "par. %d" % bisect.bisect_right(self.blocchi, offset)
        return "pag. %d" % bisect.bisect_right(self.pagine, offset)


# --------------------------------------------------------- pulizia del testo

def maschera_commenti_tex(testo):
    """Restituisce l'insieme degli intervalli commentati (% non preceduto da \\)."""
    intervalli = []
    for m in re.finditer(r"(?m)(?<!\\)%.*$", testo):
        intervalli.append((m.start(), m.end()))
    return intervalli


def in_intervalli(pos, intervalli):
    for a, b in intervalli:
        if a <= pos < b:
            return True
    return False


def pulisci(s):
    """Rende leggibile un frammento LaTeX/Markdown per il report."""
    s = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\(?:textbf|textit|emph|textsc|underline|texttt)\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)
    s = s.replace("~", " ").replace("{", "").replace("}", "")
    s = re.sub(r"\*\*|__|(?<!\w)[*_](?!\w)", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def contesto(testo, a, b, ampiezza=160):
    ini = max(0, a - ampiezza)
    fin = min(len(testo), b + ampiezza)
    # allarga ai confini di frase se vicini
    pre = testo[ini:a]
    k = max(pre.rfind(". "), pre.rfind("\n\n"))
    if k != -1:
        ini = ini + k + 2
    post = testo[b:fin]
    k = re.search(r"\.(\s|$)|\n\n", post)
    if k:
        fin = b + k.end()
    return pulisci(testo[ini:fin])


def stringa_da_cercare(testo, a, b):
    """Frammento originale univoco (≤ 60 caratteri) da usare con Trova."""
    frammento = testo[a:b]
    candidati = []
    righe = [r for r in re.split(r"\n", frammento) if r.strip()]
    for r in righe:
        r = r.strip()
        for lung in (40, 60, len(r)):
            c = r[:lung]
            # non tagliare a metà parola o numero: «n. 1639» sembrerebbe un errore
            m = re.match(r"[\w'’.-]*", r[lung:])
            candidati.append(c + (m.group(0) if m else ""))
    candidati.append(frammento[:60])
    # preferisci stringhe senza segni di formattazione né virgolette spaiate:
    # chi usa Trova sul documento impaginato non vede *, \textit, ~
    markup = re.compile(r"[*_\\{}«»“”\"`]")
    # la tilde LaTeX è uno spazio non divisibile: nel documento impaginato è uno spazio
    testo_vis = testo.replace("~", " ")
    puliti = []
    # 1) pezzi interi della citazione (fino a 80 caratteri), senza tagli
    for pezzo in markup.split(frammento.replace("\n", " ").replace("~", " ")):
        pezzo = re.sub(r"\s+", " ", pezzo).strip(" ,;:")
        if 12 <= len(pezzo) <= 80:
            puliti.append(pezzo)
    # 2) tronconi: mai finire su «n.», «art.», «Rv.», «sez.» senza il seguito
    tronco = re.compile(r"(?:\b(?:n|nn|art|artt|Rv|sez|co|comma)\.?)\s*$", re.I)
    for i, c in enumerate(candidati):
        if tronco.search(c):
            resto = frammento[frammento.find(c) + len(c):]
            m = re.match(r"\s*[\w'’./-]+", resto)
            if m:
                candidati[i] = c + m.group(0)
    for c in candidati:
        for pezzo in markup.split(c):
            pezzo = pezzo.strip(" ,;:")
            if len(pezzo) >= 12:
                puliti.append(pezzo)
    for c in puliti:
        if testo_vis.count(c) == 1:
            return c
    for c in candidati:
        c = c.strip()
        if len(c) >= 8 and testo.count(c) == 1:
            return c
    return frammento.strip()[:60]


# ----------------------------------------------------------------- estrazione

def unisci(trovati):
    """Unisce intervalli sovrapposti dello stesso tipo."""
    trovati.sort(key=lambda x: (x["tipo"], x["a"]))
    uniti = []
    for t in trovati:
        if uniti and uniti[-1]["tipo"] == t["tipo"] and t["a"] <= uniti[-1]["b"]:
            uniti[-1]["b"] = max(uniti[-1]["b"], t["b"])
        else:
            uniti.append(dict(t))
    return uniti


def estremi_di(frammento, P):
    e = {}
    E = P["estremi"]
    m = re.search(E["ecli"], frammento)
    if m:
        e["ecli"] = m.group(1)
    m = re.search(E["rv"], frammento)
    if m:
        e["rv"] = m.group(1) + ("-" + m.group(2) if m.group(2) else "")
    m = re.search(E["rg"], frammento)
    if m:
        e["rg"] = "%s/%s" % (m.group(1), m.group(2))
    resto = re.sub(E["rv"], " ", frammento)
    resto = re.sub(E["rg"], " ", resto)
    m = re.search(E["numero_anno_barra"], resto)
    if m:
        e["numero"], e["anno"] = m.group(1), m.group(2)
    else:
        m = re.search(E["numero"], resto)
        if m:
            e["numero"] = m.group(1)
            m2 = re.search(E["anno_del"], resto[m.end():m.end() + 30])
            if m2:
                e["anno"] = m2.group(1)
    m = re.search(E["data"], resto)
    if m:
        e["data"] = "%02d.%02d.%s" % (int(m.group(1)), int(m.group(2)), m.group(3))
    else:
        m = re.search(E["data_estesa"], resto, re.I)
        if m:
            e["data"] = " ".join(m.groups())
    m = re.search(E["sezione"], frammento)
    if m:
        e["sezione"] = m.group(1)
    if re.search(r"Sez(?:ioni)?\.?[\s~]*U(?:n|nite)?\.?|SS\.?[\s~]*UU", frammento):
        e["sezione"] = "Un."
    m = re.search(E["tipo"], frammento, re.I)
    if m:
        e["tipo"] = m.group(1).lower()
    if "anno" not in e and "data" in e:
        e["anno"] = e["data"][-4:]
    return e


def estrai(testo, P, est, solo=None):
    trovati = []
    commenti = maschera_commenti_tex(testo) if est == ".tex" else []
    fine = re.compile(P["fine_citazione"])
    maxlen = P["lunghezza_massima_citazione"]

    if solo in (None, "giurisprudenza"):
        for anc in P["ancore_giurisprudenza"]:
            for m in re.finditer(anc, testo):
                a = m.start()
                coda = testo[m.end():m.end() + maxlen]
                f = fine.search(coda)
                b = m.end() + (f.start() if f else len(coda))
                fr = testo[a:b]
                # tieni solo se ci sono estremi (numero, anno, data, Rv, ECLI)
                # e taglia dopo l'ultimo estremo, per non trascinare testo
                ultimi = list(re.finditer(P["ultimo_estremo"], fr))
                ultimi = [u for u in ultimi if re.search(r"\d{2,}", u.group(0))]
                if ultimi:
                    trovati.append({"tipo": "giurisprudenza", "a": a, "b": a + ultimi[-1].end()})

    if solo in (None, "norme"):
        N = P["norme"]
        for m in re.finditer(N["ancora"], testo):
            fin = min(len(testo), m.end() + N["finestra_fonte"])
            finestra = testo[m.start():fin]
            # la fonte deve venire prima della citazione successiva
            altra = re.search(N["ancora"], finestra[m.end() - m.start():])
            if altra:
                finestra = finestra[:m.end() - m.start() + altra.start()]
            f = re.search(N["fonti"], finestra, re.I)
            if f:
                b = m.start() + f.end()
                trovati.append({"tipo": "norma", "a": m.start(), "b": b})
            else:
                trovati.append({"tipo": "norma_senza_fonte", "a": m.start(), "b": m.end()})

    if solo is None:
        for pat in P["virgolettati"]:
            for m in re.finditer(pat, testo, re.S):
                if len(m.group(1)) > 1500:
                    continue
                trovati.append({"tipo": "virgolettato", "a": m.start(), "b": m.end()})
        for pat in P["link"]:
            for m in re.finditer(pat, testo):
                trovati.append({"tipo": "link", "a": m.start(), "b": m.end()})
        for m in re.finditer(P["documenti"], testo):
            trovati.append({"tipo": "documento", "a": m.start(), "b": m.end()})
        for m in re.finditer(P["affermazioni_senza_fonte"], testo, re.I):
            trovati.append({"tipo": "affermazione_senza_fonte", "a": m.start(), "b": m.end()})

    voci = unisci(trovati)
    for v in voci:
        v["commentato"] = in_intervalli(v["a"], commenti)
    return voci


ORDINE = ["giurisprudenza", "norma", "norma_senza_fonte", "virgolettato",
          "documento", "affermazione_senza_fonte", "link"]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("atto")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pattern", default=os.path.join(QUI, "pattern_it.json"))
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--solo-giurisprudenza", action="store_true")
    g.add_argument("--solo-norme", action="store_true")
    args = ap.parse_args()

    with open(args.pattern, encoding="utf-8") as f:
        P = json.load(f)
    testo, tipo_pos, est = carica_testo(args.atto)
    testo = unicodedata.normalize("NFC", testo)
    solo = "giurisprudenza" if args.solo_giurisprudenza else ("norme" if args.solo_norme else None)
    voci = estrai(testo, P, est, solo)
    pos = Posizioni(testo, tipo_pos)

    voci.sort(key=lambda v: (v["commentato"], v["a"]))
    risultato = []
    n = 0
    for v in voci:
        n += 1
        fr = testo[v["a"]:v["b"]]
        r = {
            "id": "C%02d" % n,
            "tipo": v["tipo"],
            "posizione": pos.di(v["a"]),
            "testo": pulisci(fr),
            "contesto": contesto(testo, v["a"], v["b"]),
            "stringa_da_cercare": stringa_da_cercare(testo, v["a"], v["b"]),
            "commentato": v["commentato"],
            "verdetto": None,
            "gravita": None,
            "stato": "da fare",
        }
        if v["tipo"] == "giurisprudenza":
            r["estremi"] = estremi_di(fr, P)
        risultato.append(r)

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "inventario.json"), "w", encoding="utf-8") as f:
        json.dump({"atto": os.path.abspath(args.atto), "posizione": tipo_pos,
                   "voci": risultato}, f, ensure_ascii=False, indent=2)

    conta = {}
    for r in risultato:
        conta[r["tipo"]] = conta.get(r["tipo"], 0) + 1
    righe = ["# Inventario delle citazioni", "",
             "Atto: `%s` — posizione espressa come %s." % (os.path.basename(args.atto), tipo_pos),
             "Estrazione automatica: va riconciliata con una lettura integrale dell'atto.", "",
             "| Tipo | Voci |", "|---|---|"]
    for t in ORDINE:
        if t in conta:
            righe.append("| %s | %d |" % (t, conta[t]))
    commentate = sum(1 for r in risultato if r["commentato"])
    if commentate:
        righe += ["", "%d voci sono in parti commentate (non stampate): sono elencate in fondo." % commentate]
    for t in ORDINE:
        sel = [r for r in risultato if r["tipo"] == t and not r["commentato"]]
        if not sel:
            continue
        righe += ["", "## " + t, "", "| ID | Posizione | Citazione | Estremi letti | Da cercare |", "|---|---|---|---|---|"]
        for r in sel:
            est_txt = ", ".join("%s %s" % (k, v) for k, v in r.get("estremi", {}).items())
            righe.append("| %s | %s | %s | %s | `%s` |" % (
                r["id"], r["posizione"], r["testo"].replace("|", "/")[:180],
                est_txt, r["stringa_da_cercare"].replace("|", "/").replace("`", "'")))
    sel = [r for r in risultato if r["commentato"]]
    if sel:
        righe += ["", "## Nelle parti commentate", "", "| ID | Posizione | Tipo | Citazione |", "|---|---|---|---|"]
        for r in sel:
            righe.append("| %s | %s | %s | %s |" % (r["id"], r["posizione"], r["tipo"],
                                                     r["testo"].replace("|", "/")[:160]))
    if est == ".tex" and re.search(r"\\(?:input|include)\{", testo):
        righe += ["", "**Attenzione**: l'atto usa `\\input`/`\\include`; i file inclusi vanno estratti a parte."]
    with open(os.path.join(args.out, "inventario.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(righe) + "\n")
    print("Voci: %d (%s). Scritti inventario.md e inventario.json in %s" % (
        len(risultato), ", ".join("%s %d" % (t, conta[t]) for t in ORDINE if t in conta), args.out))


if __name__ == "__main__":
    main()
