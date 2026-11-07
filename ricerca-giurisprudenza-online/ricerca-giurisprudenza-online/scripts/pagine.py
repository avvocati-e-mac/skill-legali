#!/usr/bin/env python3
"""Pagina fisica delle citazioni nei provvedimenti scaricati come PDF (nessun modello, 0 token).

Uso:  python3 pagine.py <cartella_lavoro> [--skill-docling <cartella della skill docling-citazioni-pdf>]

Per ogni scheda il cui file in ../pdf e' un PDF, cerca ogni citazione (citazioni[].testo,
NON il campo pagina) nel testo del PDF e scrive <cartella_lavoro>/pagine.jsonl, riscritto
per intero a ogni esecuzione. Una riga per citazione, chiave (id, i):
  id, i, file_pdf, sha256_pdf, metodo, stato, pagina_fisica, note
Stati: trovata | ambigua | non_ritrovata_nel_pdf | non_verificabile.
"non_ritrovata_nel_pdf" NON significa che la citazione sia falsa o errata: solo che il testo
estratto dal PDF non la contiene cosi' com'e' (impaginazione, firme, anonimizzazione, scansione).
Metodi, in ordine: (a) check_pdf_quote.py della skill docling-citazioni-pdf (richiede pypdfium2),
(b) pdftotext (pagine dai salti pagina), (c) nessuno -> non_verificabile.
La skill docling-citazioni-pdf non e' presumibile: se non e' in una cartella nota, il percorso
va scoperto dall'assistente e passato con --skill-docling. Dei suoi file si usa solo lo script
check_pdf_quote.py. Solo libreria standard di Python 3.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import unicodedata

NOME_B = "docling-citazioni-pdf"
CITAZIONI_MIN = 8  # sotto questa lunghezza (normalizzata) la ricerca darebbe troppi falsi riscontri


def cartelle_note():
    home = os.path.expanduser("~")
    codex = os.environ.get("CODEX_HOME") or os.path.join(home, ".codex")
    return [os.path.join(home, ".claude", "skills", NOME_B),
            os.path.join(codex, "skills", NOME_B),
            os.path.join(home, ".agents", "skills", NOME_B)]


def trova_script_b(esplicita):
    """Percorso di check_pdf_quote.py o None."""
    candidate = [esplicita] if esplicita else cartelle_note()
    for c in candidate:
        if not c:
            continue
        c = os.path.abspath(os.path.expanduser(c))
        for rel in (("scripts", "check_pdf_quote.py"), (NOME_B, "scripts", "check_pdf_quote.py"),
                    ("check_pdf_quote.py",)):
            p = os.path.join(c, *rel)
            if os.path.isfile(p):
                return p
    return None


def sha256(percorso):
    h = hashlib.sha256()
    with open(percorso, "rb") as f:
        for blocco in iter(lambda: f.read(1 << 20), b""):
            h.update(blocco)
    return h.hexdigest()


# ---------- metodo (b): pdftotext ----------
_QUOTE = {"’": "'", "‘": "'", "´": "'", "`": "'", "ʼ": "'",
          "“": '"', "”": '"', "«": '"', "»": '"', "„": '"'}
_TRATTINI = set("-‐‑‒–—−­")


def normalizza(testo, pagina=None):
    """Lista di (carattere, pagina): minuscolo, apostrofi/virgolette unificati, senza spazi
    ne' trattini (cosi' la sillabazione a fine riga e gli a capo non contano)."""
    out = []
    for ch in unicodedata.normalize("NFC", testo):
        ch = _QUOTE.get(ch, ch)
        if ch.isspace() or ch in _TRATTINI:
            continue
        out.append((ch.lower(), pagina))
    return out


def pagine_pdftotext(percorso):
    """Testo per pagina fisica (lista) oppure None se pdftotext manca o fallisce."""
    exe = shutil.which("pdftotext")
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "-enc", "UTF-8", percorso, "-"], capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    pagine = r.stdout.decode("utf-8", "replace").split("\f")
    if pagine and not pagine[-1].strip():
        pagine.pop()
    return pagine


def cerca_in_pagine(pagine, citazione):
    """-> (stato, pagina_fisica, note) cercando la citazione nel testo normalizzato."""
    q = "".join(c for c, _ in normalizza(citazione))
    if len(q) < CITAZIONI_MIN:
        return "non_verificabile", None, "citazione troppo breve per un riscontro affidabile"
    testo, mappa = [], []
    for n, t in enumerate(pagine, 1):
        for c, _ in normalizza(t):
            testo.append(c)
            mappa.append(n)
    testo = "".join(testo)
    inizi, pos = [], testo.find(q)
    while pos != -1:
        inizi.append(pos)
        pos = testo.find(q, pos + 1)
    if not inizi:
        return ("non_ritrovata_nel_pdf", None,
                "non ritrovata nel testo del PDF (non e' un giudizio sulla citazione)")
    spans = [(mappa[i], mappa[i + len(q) - 1]) for i in inizi]
    if len(spans) > 1:
        elenco = ", ".join(str(a) if a == b else "%d-%d" % (a, b) for a, b in spans)
        return "ambigua", None, "testo presente piu' volte, pagine %s" % elenco
    a, b = spans[0]
    return "trovata", a, ("" if a == b else "a cavallo delle pagine %d-%d" % (a, b))


# ---------- metodo (a): check_pdf_quote.py di B ----------
def esegui_b(script_b, percorso, pagine, citazione):
    try:
        r = subprocess.run([sys.executable, "-B", script_b, "--pdf", percorso, "--pages"]
                           + [str(p) for p in pagine] + ["--quote", citazione],
                           capture_output=True, text=True, timeout=180)
        d = json.loads(r.stdout or r.stderr)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    if r.returncode != 0 or not isinstance(d, dict) or d.get("status") == "check_unavailable":
        return None
    return d


def pagine_di_b(script_b, percorso):
    d = esegui_b(script_b, percorso, [1], "prova di conteggio pagine")
    n = d.get("physical_page_count") if d else None
    return n if isinstance(n, int) and n > 0 else 0


def cerca_con_b(script_b, percorso, citazione, n_pagine):
    """-> (stato, pagina, note) oppure None se B non e' utilizzabile."""
    d = esegui_b(script_b, percorso, range(1, n_pagine + 1), citazione)
    if d is None:
        return None
    st = d.get("status")
    if st == "text_match_found":
        fis = d.get("selected_physical_pages") or []
        if not fis:
            return None
        nota = "" if len(fis) == 1 else "a cavallo delle pagine %d-%d" % (fis[0], fis[-1])
        return "trovata", int(fis[0]), nota
    if st == "ambiguous_text_match":
        pp = sorted({p for m in d.get("matches", []) for p in m.get("physical_pages", [])})
        return "ambigua", None, "testo presente piu' volte, pagine %s" % ", ".join(map(str, pp))
    if st == "unverified_text_boundaries":
        return "ambigua", None, "confini del testo nella pagina non verificati"
    if st == "text_not_found":
        return ("non_ritrovata_nel_pdf", None,
                "non ritrovata nel testo del PDF (non e' un giudizio sulla citazione)")
    return None


def main(argv):
    args = argv[1:]
    skill_b = None
    if "--skill-docling" in args:
        k = args.index("--skill-docling")
        if k + 1 >= len(args):
            print(__doc__)
            return 2
        skill_b = args[k + 1]
        del args[k:k + 2]
    if len(args) != 1 or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    lav = os.path.abspath(os.path.expanduser(args[0]))
    if not os.path.isdir(lav):
        print("Cartella di lavoro non trovata: %s" % lav)
        return 2
    dir_pdf = os.path.join(os.path.dirname(lav), "pdf")
    dir_schede = os.path.join(lav, "schede")

    pdf_per_id = {}
    if os.path.isdir(dir_pdf):
        for nome in sorted(os.listdir(dir_pdf)):
            base, ext = os.path.splitext(nome)
            p = os.path.join(dir_pdf, nome)
            if ext.lower() == ".pdf" and os.path.isfile(p) and os.path.getsize(p) > 0:
                pdf_per_id[base.rsplit("_", 1)[-1]] = p

    script_b = trova_script_b(skill_b)
    b_ok = script_b is not None
    pdftotext_ok = shutil.which("pdftotext") is not None

    righe, n_b = [], {}
    if os.path.isdir(dir_schede):
        for nome in sorted(os.listdir(dir_schede)):
            if not nome.endswith(".json"):
                continue
            ident = nome[:-5]
            percorso = pdf_per_id.get(ident)
            if not percorso:
                continue  # HTML o file assente: nessuna pagina PDF
            try:
                with open(os.path.join(dir_schede, nome), encoding="utf-8-sig") as f:
                    scheda = json.load(f)
                citazioni = scheda.get("citazioni") if isinstance(scheda, dict) else None
                if not isinstance(citazioni, list):
                    continue
            except Exception:
                continue
            digest = sha256(percorso)
            nome_pdf = os.path.basename(percorso)
            testo_pagine = pagine_pdftotext(percorso) if pdftotext_ok else None
            n_pag = len(testo_pagine) if testo_pagine else 0
            senza_testo = testo_pagine is not None and not "".join(testo_pagine).strip()
            for i, c in enumerate(citazioni):
                testo = c.get("testo") if isinstance(c, dict) else None
                base = {"id": ident, "i": i, "file_pdf": nome_pdf, "sha256_pdf": digest}
                if not isinstance(testo, str) or not testo.strip():
                    righe.append(dict(base, metodo="nessuno", stato="non_verificabile",
                                      pagina_fisica=None, note="citazione senza testo"))
                    continue
                risultato, metodo = None, "nessuno"
                if b_ok:
                    if not n_b.get(percorso):
                        n_b[percorso] = pagine_di_b(script_b, percorso)
                    risultato = (cerca_con_b(script_b, percorso, testo, n_b[percorso])
                                 if n_b[percorso] else None)
                    if risultato is None:
                        b_ok = False  # pypdfium2 assente o B inutilizzabile: si passa a pdftotext
                    else:
                        metodo = "check_pdf_quote"
                if risultato is None and testo_pagine is not None:
                    metodo = "pdftotext"
                    if senza_testo:
                        risultato = ("non_verificabile", None,
                                     "il PDF non ha testo estraibile (scansione?); nessun OCR")
                    else:
                        risultato = cerca_in_pagine(testo_pagine, testo)
                if risultato is None:
                    metodo = "nessuno"
                    risultato = ("non_verificabile", None,
                                 "nessuno strumento disponibile per leggere il PDF")
                stato, pagina, note = risultato
                righe.append(dict(base, metodo=metodo, stato=stato, pagina_fisica=pagina, note=note))

    dest = os.path.join(lav, "pagine.jsonl")
    tmp = dest + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in righe:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, dest)

    tot = len(righe)
    trovate = sum(1 for r in righe if r["stato"] == "trovata")
    metodi = sorted({r["metodo"] for r in righe})
    print("Pagine PDF: citazioni con pagina trovata %d/%d (metodi: %s)" % (trovate, tot, ", ".join(metodi) or "nessuno"))
    print("check_pdf_quote.py di %s: %s; pdftotext: %s" % (
        NOME_B, "trovato" if script_b else "non trovato",
        "presente" if pdftotext_ok else "assente"))
    print("Scritto: %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
