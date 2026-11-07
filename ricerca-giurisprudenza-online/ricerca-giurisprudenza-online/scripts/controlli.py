#!/usr/bin/env python3
"""Controlli meccanici sulla cartella di lavoro di una ricerca giurisprudenziale.

Uso:  python3 controlli.py <cartella_lavoro>

Verifica che i file attesi esistano e non siano vuoti, valida le schede JSON
(campi obbligatori, campi non ammessi, valori ammessi), cerca ogni citazione nel
relativo testi/<id>.txt dopo normalizzazione, scrive <cartella_lavoro>/controlli.txt.
Codice di uscita: 0 = tutto in regola, 1 = ci sono problemi, 2 = uso errato.
Solo libreria standard di Python 3.
"""
import csv
import datetime
import json
import os
import re
import sys
import unicodedata

ESITI = ["accoglie", "rigetta", "inammissibile", "improcedibile", "altro"]
DEFINITIVO = ["si", "no", "non indicato"]
FONTE_TESTO = ["provvedimento", "massima_sito"]
TESTO_LETTO = ["integrale", "parziale", "no"]
CHI = ["avvocato", "parte", "giudice", "ctu", "altro"]
TEMA_CAUSA = ["si", "no", "non chiaro"]
RUOLO = ["decisivo", "concorrente", "obiter", "marginale"]
CONSEGUENZE = [
    "condanna art. 96 co. 3",
    "condanna art. 96 co. 4",
    "trasmissione atti all'Ordine",
    "spese",
    "nessuna",
    "altro",
]
ESTREMI = ["ufficio", "sezione", "grado", "tipo", "data_decisione",
           "data_deposito", "numero", "rg", "giudice"]
CAMPI_STRINGA = ["url_scheda", "url_file", "come_emerge", "fatti",
                 "parte_rilevante", "motivo_reale_dell_esito"]
CAMPI_LISTA = ["norme_applicate", "importi", "precedenti_citati", "dubbi"]
CAMPI = (["estremi", "fonte_testo", "testo_letto", "chi", "esito", "definitivo",
          "tema_causa_dell_esito", "ruolo_del_tema",
          "conseguenze_legate_al_tema", "citazioni"]
         + CAMPI_STRINGA + CAMPI_LISTA)
CAMPI_AMMESSI = set(CAMPI) | {"id"}
LIMITI_PAROLE = {"fatti": 60, "parte_rilevante": 150, "motivo_reale_dell_esito": 30}
RE_ID = re.compile(r"^[A-Za-z0-9-]+$")
RE_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------- utilità
def leggi_csv(percorso):
    """Legge un CSV (virgola o punto e virgola, anche con BOM) come lista di dict."""
    with open(percorso, encoding="utf-8-sig", newline="") as f:
        testo = f.read()
    if not testo.strip():
        return []
    prima = testo.splitlines()[0]
    delim = ";" if prima.count(";") > prima.count(",") else ","
    righe = csv.DictReader(testo.splitlines(), delimiter=delim)
    out = []
    for r in righe:
        out.append({(k or "").strip(): (v or "").strip() for k, v in r.items()})
    return out


def norm(s):
    """Normalizza virgolette, apostrofi, trattini, spazi speciali, forma Unicode."""
    s = unicodedata.normalize("NFC", s)
    s = s.replace("­", "").replace("​", "")
    for c in "“”«»„‟″":
        s = s.replace(c, '"')
    for c in "‘’‚‛′`´":
        s = s.replace(c, "'")
    for c in "‐‑‒–—―−":
        s = s.replace(c, "-")
    return s.replace(" ", " ")


def compatta(s):
    """Toglie ogni spazio: rende irrilevanti spazi multipli e spazi spuri
    dentro le parole (tipici dell'estrazione PDF, es. 'ChatGP T')."""
    return re.sub(r"\s+", "", norm(s))


def pagliai(testo):
    """Due versioni compatte del testo: normale e con le sillabazioni a fine riga ricomposte."""
    return [compatta(testo), compatta(re.sub(r"-[ \t]*\r?\n\s*", "", norm(testo)))]


def trovata(citazione, covoni):
    c = norm(citazione).strip().strip('"\'').strip()
    if not c:
        return False
    for h in covoni:
        if compatta(c) in h:
            return True
    # omissioni: [...] (...) … ...  -> ogni frammento deve comparire, nell'ordine
    frammenti = [compatta(x) for x in re.split(r"\[\s*\.{3}\s*\]|\(\s*\.{3}\s*\)|…|\.{3}", c)]
    frammenti = [x for x in frammenti if x]
    if len(frammenti) > 1:
        for h in covoni:
            pos = 0
            ok = True
            for fr in frammenti:
                i = h.find(fr, pos)
                if i < 0:
                    ok = False
                    break
                pos = i + len(fr)
            if ok:
                return True
    return False


def non_vuota(s):
    return isinstance(s, str) and s.strip() != ""


def parole(s):
    return len(s.split())


def norm_valore(s):
    return norm(s).strip() if isinstance(s, str) else s


# ---------------------------------------------------------------- validazione
def valida_scheda(d, id_file):
    """Restituisce (errori, avvisi) per una scheda già caricata da JSON."""
    err, avv = [], []
    if not isinstance(d, dict):
        return ["la scheda non è un oggetto JSON"], avv
    for k in d:
        if k not in CAMPI_AMMESSI:
            err.append("campo non ammesso: %s" % k)
    if "id" in d and d["id"] != id_file:
        err.append("id nella scheda (%r) diverso dal nome del file (%r)" % (d["id"], id_file))
    for k in CAMPI:
        if k not in d:
            err.append("campo mancante: %s" % k)

    est = d.get("estremi")
    if "estremi" in d:
        if not isinstance(est, dict):
            err.append("estremi non è un oggetto")
        else:
            for k in est:
                if k not in ESTREMI:
                    err.append("estremi: campo non ammesso: %s" % k)
            for k in ESTREMI:
                if k not in est:
                    err.append("estremi: campo mancante: %s" % k)
                elif not non_vuota(est[k]):
                    err.append("estremi.%s vuoto (scrivi 'non indicato')" % k)
            for k in ("data_decisione", "data_deposito"):
                v = est.get(k)
                if non_vuota(v) and v != "non indicato" and not RE_DATA.match(v):
                    err.append("estremi.%s: formato data non valido %r (atteso AAAA-MM-GG)" % (k, v))

    for k in CAMPI_STRINGA:
        if k in d and not non_vuota(d[k]):
            err.append("%s vuoto o non testuale (scrivi 'non indicato')" % k)
    for k, lim in LIMITI_PAROLE.items():
        if non_vuota(d.get(k)) and parole(d[k]) > lim:
            avv.append("%s: %d parole (limite %d)" % (k, parole(d[k]), lim))

    for k, ammessi in (("fonte_testo", FONTE_TESTO), ("testo_letto", TESTO_LETTO),
                       ("chi", CHI), ("esito", ESITI), ("definitivo", DEFINITIVO),
                       ("tema_causa_dell_esito", TEMA_CAUSA), ("ruolo_del_tema", RUOLO)):
        if k in d and d[k] not in ammessi:
            err.append("%s: valore non ammesso %r (ammessi: %s)" % (k, d[k], " | ".join(ammessi)))

    for k in CAMPI_LISTA:
        if k in d:
            if not isinstance(d[k], list):
                err.append("%s deve essere una lista" % k)
            elif not all(isinstance(x, str) for x in d[k]):
                err.append("%s: gli elementi devono essere testo" % k)

    if "conseguenze_legate_al_tema" in d:
        c = d["conseguenze_legate_al_tema"]
        ammessi_norm = {norm(x): x for x in CONSEGUENZE}
        if not isinstance(c, list) or not c:
            err.append("conseguenze_legate_al_tema deve essere una lista non vuota")
        else:
            for x in c:
                if not isinstance(x, str) or norm(x) not in ammessi_norm:
                    err.append("conseguenze_legate_al_tema: valore non ammesso %r (ammessi: %s)"
                               % (x, " | ".join(CONSEGUENZE)))
            if "nessuna" in c and len(c) > 1:
                err.append("conseguenze_legate_al_tema: 'nessuna' non può stare con altri valori")

    if "citazioni" in d:
        cz = d["citazioni"]
        if not isinstance(cz, list):
            err.append("citazioni deve essere una lista")
        else:
            for i, x in enumerate(cz, 1):
                if not isinstance(x, dict):
                    err.append("citazioni[%d] non è un oggetto" % i)
                    continue
                for k in x:
                    if k not in ("testo", "pagina"):
                        err.append("citazioni[%d]: campo non ammesso: %s" % (i, k))
                if not non_vuota(x.get("testo")):
                    err.append("citazioni[%d]: testo mancante o vuoto" % i)
                elif parole(x["testo"]) > 25:
                    avv.append("citazioni[%d]: %d parole (limite 25)" % (i, parole(x["testo"])))
                p = x.get("pagina")
                if not (isinstance(p, (int, str)) and not isinstance(p, bool) and str(p).strip()):
                    err.append("citazioni[%d]: pagina mancante" % i)

    # coerenza (solo avvisi)
    ruolo = d.get("ruolo_del_tema")
    if ruolo in ("obiter", "marginale"):
        if d.get("tema_causa_dell_esito") == "si":
            avv.append("incoerenza: tema_causa_dell_esito = si ma ruolo_del_tema = %s" % ruolo)
        forti = [x for x in (d.get("conseguenze_legate_al_tema") or [])
                 if isinstance(x, str) and x.startswith(("condanna", "trasmissione"))]
        if forti:
            avv.append("incoerenza: conseguenze %s ma ruolo_del_tema = %s" % (forti, ruolo))
    if d.get("testo_letto") == "no" and d.get("citazioni"):
        avv.append("testo_letto = no ma ci sono citazioni")
    return err, avv


# ---------------------------------------------------------------- principale
def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    lav = os.path.abspath(os.path.expanduser(argv[1]))
    if not os.path.isdir(lav):
        print("Cartella di lavoro non trovata: %s" % lav)
        return 2

    mancanti, problemi_file = [], []
    righe = []

    def esiste_non_vuoto(rel, cartella=False):
        p = os.path.join(lav, rel)
        if cartella:
            if not os.path.isdir(p):
                mancanti.append(rel + "/ (cartella assente)")
                return False
            return True
        if not os.path.isfile(p):
            mancanti.append(rel + " (assente)")
            return False
        if os.path.getsize(p) == 0:
            mancanti.append(rel + " (vuoto)")
            return False
        return True

    ok_elenco = esiste_non_vuoto("elenco.csv")
    ok_scartati = esiste_non_vuoto("scartati.csv")
    esiste_non_vuoto("ricognizione.md")
    esiste_non_vuoto("testi", cartella=True)
    esiste_non_vuoto("schede", cartella=True)

    elenco, scartati = [], set()
    if ok_elenco:
        try:
            elenco = leggi_csv(os.path.join(lav, "elenco.csv"))
        except Exception as e:  # file illeggibile
            problemi_file.append("elenco.csv non leggibile: %s" % e)
        if ok_elenco and not elenco and not problemi_file:
            problemi_file.append("elenco.csv non contiene alcuna riga")
        if elenco and "id" not in elenco[0]:
            problemi_file.append("elenco.csv: manca la colonna 'id'")
            elenco = []
    if ok_scartati:
        try:
            scartati = {r.get("id", "") for r in leggi_csv(os.path.join(lav, "scartati.csv"))}
        except Exception as e:
            problemi_file.append("scartati.csv non leggibile: %s" % e)

    da_leggere = []
    for r in elenco:
        i = r.get("id", "")
        if not i:
            problemi_file.append("elenco.csv: riga senza id")
            continue
        if not RE_ID.match(i):
            problemi_file.append("elenco.csv: id non valido %r (solo lettere, cifre e trattino)" % i)
        if r.get("da_leggere", "si").lower() in ("si", "sì", "s", "1", "true", "") and i not in scartati:
            da_leggere.append(i)

    dir_schede = os.path.join(lav, "schede")
    dir_testi = os.path.join(lav, "testi")
    schede_presenti = sorted(f[:-5] for f in os.listdir(dir_schede) if f.endswith(".json")) \
        if os.path.isdir(dir_schede) else []

    valide = 0
    errori_schede = []   # (id, [messaggi])
    avvisi_schede = []
    citazioni_tot = citazioni_ok = 0
    da_verificare = []   # (id, testo, pagina, motivo)

    for i in da_leggere:
        p = os.path.join(dir_schede, i + ".json")
        if not os.path.isfile(p):
            mancanti.append("schede/%s.json (assente)" % i)
            continue
        if os.path.getsize(p) == 0:
            mancanti.append("schede/%s.json (vuoto)" % i)
            continue
        try:
            with open(p, encoding="utf-8-sig") as f:
                d = json.load(f)
        except Exception as e:
            errori_schede.append((i, ["JSON non valido: %s" % e]))
            continue
        err, avv = valida_scheda(d, i)
        if err:
            errori_schede.append((i, err))
        else:
            valide += 1
        if avv:
            avvisi_schede.append((i, avv))

        # file di testo e citazioni (anche se la scheda ha altri errori)
        pt = os.path.join(dir_testi, i + ".txt")
        testo_letto = d.get("testo_letto") if isinstance(d, dict) else None
        ha_testo = os.path.isfile(pt) and os.path.getsize(pt) > 0
        if testo_letto != "no" and not ha_testo:
            mancanti.append("testi/%s.txt (%s)" % (i, "vuoto" if os.path.isfile(pt) else "assente"))
        covoni = None
        if ha_testo:
            with open(pt, encoding="utf-8", errors="replace") as f:
                covoni = pagliai(f.read())
        cz = d.get("citazioni") if isinstance(d, dict) else None
        if isinstance(cz, list):
            for x in cz:
                if not isinstance(x, dict) or not non_vuota(x.get("testo")):
                    continue
                citazioni_tot += 1
                pag = x.get("pagina", "")
                if covoni is None:
                    da_verificare.append((i, x["testo"], pag, "testo estratto non disponibile"))
                elif trovata(x["testo"], covoni):
                    citazioni_ok += 1
                else:
                    da_verificare.append((i, x["testo"], pag, "non trovata nell'estratto"))

    senza_riga = [s for s in schede_presenti if s not in {r.get("id") for r in elenco}]

    # ------------------------------------------------------------ rapporto
    Y = len(da_leggere)
    righe.append("CONTROLLI - %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    righe.append("Cartella: %s" % lav)
    righe.append("")
    righe.append("Schede valide: %d/%d" % (valide, Y))
    righe.append("Citazioni trovate: %d/%d" % (citazioni_ok, citazioni_tot))
    righe.append("File mancanti: %d" % len(mancanti))
    righe.append("Candidati scartati (non conteggiati): %d" % len(scartati & {r.get('id') for r in elenco}))
    righe.append("")
    righe.append("== File mancanti o vuoti ==")
    righe += ["- " + m for m in mancanti] or ["nessuno"]
    if problemi_file:
        righe.append("")
        righe.append("== Problemi negli elenchi ==")
        righe += ["- " + m for m in problemi_file]
    righe.append("")
    righe.append("== Schede con errori ==")
    if errori_schede:
        for i, msgs in errori_schede:
            righe.append("- %s" % i)
            righe += ["    " + m for m in msgs]
    else:
        righe.append("nessuna")
    righe.append("")
    righe.append('== Citazioni "da verificare" (da ricontrollare sul testo completo; non significa che siano inesistenti) ==')
    if da_verificare:
        for i, t, pag, motivo in da_verificare:
            righe.append('- %s, pag. %s: "%s" [%s]' % (i, pag, t, motivo))
    else:
        righe.append("nessuna")
    righe.append("")
    righe.append("== Avvisi (non bloccanti, da rivedere) ==")
    avvisi = []
    for i, msgs in avvisi_schede:
        avvisi += ["%s: %s" % (i, m) for m in msgs]
    avvisi += ["scheda %s presente ma senza riga in elenco.csv" % s for s in senza_riga]
    righe += ["- " + a for a in avvisi] or ["nessuno"]

    ok = (not mancanti and not problemi_file and not errori_schede and not da_verificare
          and valide == Y and Y > 0)
    righe.append("")
    righe.append("ESITO: %s" % ("TUTTO IN REGOLA" if ok else "CI SONO PROBLEMI DA RISOLVERE"))
    out = "\n".join(righe) + "\n"
    with open(os.path.join(lav, "controlli.txt"), "w", encoding="utf-8") as f:
        f.write(out)
    print(out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
