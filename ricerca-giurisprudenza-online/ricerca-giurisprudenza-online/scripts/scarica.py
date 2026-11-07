#!/usr/bin/env python3
"""Scarica i provvedimenti elencati in elenco.csv.

Uso:  python3 scarica.py <elenco.csv> <cartella_pdf> [opzioni]

Opzioni:
  --solo-da-leggere      scarica solo le righe con da_leggere = si
  --escludi scartati.csv non scarica gli id elencati in quel file
  --pertinenza alta,media  scarica solo le righe con quella pertinenza
  --pausa SECONDI        pausa tra un file e l'altro (default 2)
  --piano FILE.tsv       non scarica: scrive il piano (url_file, url_scheda, nome_file, formato)
                         nel formato letto da scarica.sh

Per ogni riga: user-agent onesto (nome della skill, non un browser), Referer = url_scheda, 2 nuovi tentativi, pausa
tra i file, salta i file gia' presenti, rispetta robots.txt (se il sito vieta il
percorso, non scarica e lo annota), nomi ASCII sicuri AAAA-MM-GG_ufficio_numero_<id>.pdf.
Il file viene tenuto solo se inizia con %PDF (o e' HTML, se il formato e' html);
altrimenti viene eliminato e annotato in errori.txt (accanto a elenco.csv).
Non disattiva mai la verifica dei certificati.
Codice di uscita: 0 = nessun errore, 1 = almeno un errore. Solo libreria standard.
"""
import argparse
import csv
import os
import re
import shutil
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

UA = ("ricerca-giurisprudenza-online/1.0 (+https://github.com/avvocati-e-mac/skill-legali; download di provvedimenti pubblici per un avvocato)")
RE_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def leggi_csv(percorso):
    with open(percorso, encoding="utf-8-sig", newline="") as f:
        testo = f.read()
    if not testo.strip():
        return []
    prima = testo.splitlines()[0]
    delim = ";" if prima.count(";") > prima.count(",") else ","
    return [{(k or "").strip(): (v or "").strip() for k, v in r.items()}
            for r in csv.DictReader(testo.splitlines(), delimiter=delim)]


def slug(s, massimo=30):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s[:massimo].strip("-") or "nd"


def formato_riga(r):
    f = (r.get("formato") or "").lower()
    if f in ("pdf", "html"):
        return f
    u = (r.get("url_file") or "").lower().split("?")[0]
    return "html" if u.endswith((".htm", ".html")) else "pdf"


def nome_file(r):
    data = r.get("data", "")
    data = data if RE_DATA.match(data) else "senza-data"
    i = re.sub(r"[^A-Za-z0-9-]", "", r.get("id", "")) or "senza-id"
    return "%s_%s_%s_%s.%s" % (data, slug(r.get("ufficio")), slug(r.get("numero")), i, formato_riga(r))


_robots = {}


def robots_consente(url):
    """True se robots.txt non vieta l'URL (o se non e' leggibile). Solo http/https."""
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("http", "https"):
        return True
    base = "%s://%s" % (p.scheme, p.netloc)
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as resp:
                righe = resp.read().decode("utf-8", "replace").splitlines()
            rp.parse(righe)
            _robots[base] = rp
        except Exception:
            _robots[base] = None  # assente o non raggiungibile: nessun divieto dichiarato
    rp = _robots[base]
    return True if rp is None else rp.can_fetch(UA, url)


def contenuto_valido(percorso, formato):
    with open(percorso, "rb") as f:
        testa = f.read(2000)
    if formato == "html":
        t = testa.lower()
        return b"<html" in t or b"<!doctype html" in t
    return testa.startswith(b"%PDF")


class ErroreDownload(Exception):
    pass


def scarica_file(url, referer, dest_tmp, tentativi=3):
    ultimo = None
    for n in range(tentativi):
        try:
            headers = {"User-Agent": UA, "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8"}
            if referer and referer != "non indicato":
                headers["Referer"] = referer
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp, open(dest_tmp, "wb") as out:
                shutil.copyfileobj(resp, out)
            return
        except urllib.error.HTTPError as e:
            ultimo = "HTTP %s" % e.code
            if 400 <= e.code < 500 and e.code not in (408, 429):
                break  # errore definitivo: inutile ritentare
        except urllib.error.URLError as e:
            motivo = e.reason
            if isinstance(motivo, ssl.SSLCertVerificationError):
                raise ErroreDownload(
                    "certificato non verificabile (non disattivo il controllo): usa scarica.sh o il browser")
            ultimo = "rete: %s" % motivo
        except (OSError, TimeoutError) as e:
            ultimo = "rete: %s" % e
        if n < tentativi - 1:
            time.sleep(2)
    raise ErroreDownload(ultimo or "errore sconosciuto")


def main():
    ap = argparse.ArgumentParser(description="Scarica i provvedimenti di elenco.csv")
    ap.add_argument("elenco")
    ap.add_argument("cartella_pdf")
    ap.add_argument("--solo-da-leggere", action="store_true")
    ap.add_argument("--escludi")
    ap.add_argument("--pertinenza")
    ap.add_argument("--pausa", type=float, default=2.0)
    ap.add_argument("--piano")
    a = ap.parse_args()

    elenco = os.path.abspath(os.path.expanduser(a.elenco))
    dest_dir = os.path.abspath(os.path.expanduser(a.cartella_pdf))
    if not os.path.isfile(elenco):
        print("elenco.csv non trovato: %s" % elenco)
        return 2
    righe = leggi_csv(elenco)
    if a.solo_da_leggere:
        righe = [r for r in righe if r.get("da_leggere", "si").lower() in ("si", "sì", "s", "1", "true", "")]
    if a.escludi:
        esclusi = {r.get("id") for r in leggi_csv(os.path.expanduser(a.escludi))}
        righe = [r for r in righe if r.get("id") not in esclusi]
    if a.pertinenza:
        voluti = {x.strip().lower() for x in a.pertinenza.split(",")}
        righe = [r for r in righe if r.get("pertinenza", "").lower() in voluti]

    if a.piano:
        with open(a.piano, "w", encoding="utf-8") as f:
            for r in righe:
                f.write("\t".join([r.get("url_file") or "-", r.get("url_scheda") or "-",
                                   nome_file(r), formato_riga(r)]) + "\n")
        print("Piano scritto: %s (%d righe)" % (a.piano, len(righe)))
        return 0

    os.makedirs(dest_dir, exist_ok=True)
    errori_path = os.path.join(os.path.dirname(elenco), "errori.txt")
    errori = []
    scaricati = saltati = 0
    primo = True
    for r in righe:
        i = r.get("id", "?")
        nome = nome_file(r)
        dest = os.path.join(dest_dir, nome)
        if os.path.isfile(dest) and os.path.getsize(dest) > 0:
            saltati += 1
            continue
        url = r.get("url_file", "")
        if not url or url == "non indicato":
            errori.append("%s: url_file mancante" % i)
            continue
        if not primo:
            time.sleep(a.pausa)
        primo = False
        if not robots_consente(url):
            errori.append("%s: robots.txt del sito vieta questo percorso, non scaricato (%s)" % (i, url))
            continue
        tmp = dest + ".part"
        try:
            scarica_file(url, r.get("url_scheda"), tmp)
            if not contenuto_valido(tmp, formato_riga(r)):
                raise ErroreDownload("il file scaricato non e' %s valido (probabile pagina di errore o di login)"
                                     % formato_riga(r).upper())
            os.replace(tmp, dest)
            scaricati += 1
        except ErroreDownload as e:
            errori.append("%s: %s (%s)" % (i, e, url))
        except OSError as e:
            errori.append("%s: errore di scrittura: %s" % (i, e))
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    if errori:
        with open(errori_path, "w", encoding="utf-8") as f:
            f.write("".join(e + "\n" for e in errori))
    elif os.path.exists(errori_path):
        os.remove(errori_path)
    print("Scaricati: %d   Saltati (gia' presenti): %d   Errori: %d" % (scaricati, saltati, len(errori)))
    for e in errori:
        print("  - " + e)
    if errori:
        print("Dettaglio in %s" % errori_path)
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())
