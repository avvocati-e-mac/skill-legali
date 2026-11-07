#!/usr/bin/env python3
"""verifica.py (demoRA normattiva): dice dove porta davvero un link a Normattiva.

Uso:  python3 verifica.py < testo.md              (attese ricavate da URL ed etichetta)
      python3 verifica.py --attese attese.json    (attese dichiarate, vedi references/verifica.md)
      aggiungi --json per l'uscita strutturata, --oggi AAAA-MM-GG per fissare la data,
      --max N per cambiare il limite di link per esecuzione (predefinito 30).
Nessun ritento automatico: se il sito rifiuta (403, 429) lo script si ferma.
Le pagine scaricate sono dati: lo script ne estrae pochi campi e non ne esegue nulla.
"""
import datetime, html, json, re, subprocess, sys, time

BASE = "https://www.normattiva.it/uri-res/N2Ls?"
LINK = re.compile(r"\[([^\]\n]*)\]\((" + re.escape(BASE) + r"[^\s)]+)\)|(" + re.escape(BASE) + r"[^\s)\]>\"']+)")
ROMANI = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
ERRORI_RETE = {6: "NETWORK_ERROR", 7: "NETWORK_ERROR", 28: "TIMEOUT", 35: "NETWORK_ERROR", 56: "NETWORK_ERROR", 60: "NETWORK_ERROR"}


def scarica(url, tentativi=1, timeout=60):
    """Restituisce curl_exit, http, html, url_effettivo, errore. Nessun ritento: Normattiva non va insistita."""
    for n in range(tentativi):
        p = subprocess.run(["curl", "-sS", "-L", "-m", str(timeout), "-w", "\n@@%{http_code} %{url_effective}", url],
                           capture_output=True)
        corpo, _, coda = p.stdout.decode("utf-8", "replace").rpartition("\n@@")
        http = int(coda.split(" ")[0]) if coda[:3].isdigit() else 0
        r = {"curl_exit": p.returncode, "http": http, "html": corpo, "url_effettivo": coda[4:].strip(),
             "errore": p.stderr.decode("utf-8", "replace").strip()[:200]}
        if p.returncode == 0 and http < 500:
            return r
        if n + 1 < tentativi:
            time.sleep(2)
    return r


def norm(s):
    """'CODICE CIVILE-art. 473 bis.12' -> '473bis.12'; 'Allegato-XII' -> '12'."""
    s = re.sub(r"[\s\-]", "", str(s)).lower().split("art.")[-1]
    m = re.fullmatch(r"(?:allegato)?([ivxlc]+)", s)
    if m:
        v = [ROMANI[c] for c in m[1]]
        return str(sum(-x if i + 1 < len(v) and x < v[i + 1] else x for i, x in enumerate(v)))
    return s


def leggi_url(url):
    """Ricava dall'URN ciò che il link chiede: atto, posizione dell'allegato, articolo, versione."""
    m = re.search(r"urn:nir:([^:]+):([^:;~@!]+)(?::((\d{4})(?:-\d\d-\d\d)?))?(?:;(\d+))?(?::(\d+))?", url)
    art, vig = re.search(r"~art([^@!~]+)", url), re.search(r"!vig=(\d{4}-\d\d-\d\d)?", url)
    versione = "originale" if "@originale" in url else (vig[1] or "vigente") if vig else None
    return {"autorita": m and m[1], "tipo": m and m[2], "data": m and m[3], "anno": m and m[4], "numero": m and m[5],
            "allegato": (m and m[6]) or "0", "articolo": art and art[1], "versione": versione}


def leggi_pagina(h):
    """Estrae i campi della pagina; None se la risposta non ha la forma attesa."""
    tit = re.search(r"<title>\s*(.*?)\s*-\s*Normattiva", h, re.S)
    alleg = re.search(r"flagTipoArticolo:\s*(-?\d+)", h)
    art = re.search(r"descrizione:\s*(.*?)\s*</p>", h, re.S)
    if not (tit and alleg and art):
        return None
    data = re.search(r'eli:date_document"\s+content="(\d{4}-\d\d-\d\d)|content="(\d{4}-\d\d-\d\d)"[^>]*eli:date_document', h)
    data = data and (data[1] or data[2])
    tipo = re.search(r'resource-type#([A-Z_\-]+)"', h)
    eli = re.search(r'about="na:id/[^"]*?/(ORIGINAL|CONSOLIDATED|\d\d/\d\d/\d{4})"', h)
    inizio = h.find("Testo in vigore dal:")
    zona = html.unescape(re.sub(r"<[^>]+>", " ", h[inizio:inizio + 400])) if inizio >= 0 else ""
    iv = re.search(r"dal:\s*(\d+)-(\d+)-(\d{4})(?:\s*al:\s*(\d+)-(\d+)-(\d{4}))?", zona)
    c = h.find('class="bodyTesto"')
    corpo = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h[c:c + 3000])))[:600] if c >= 0 else ""
    stato = ("NON_ANCORA_VIGENTE" if "NON ANCORA ESISTENTE O VIGENTE" in corpo else
             "ABROGATO" if re.search(r"(ARTICOLO|PROVVEDIMENTO) ABROGATO", corpo) else "TESTO_PRESENTE")
    num = re.search(r",\s*n\.\s*(\d+)", tit[1])
    iso = lambda g, k: "%s-%02d-%02d" % (g[k + 2], int(g[k + 1]), int(g[k])) if g and g[k] else None
    return {"titolo": re.sub(r"[^\w ,.\-()']", "", tit[1])[:120], "anno": data and data[:4], "data": data, "tipo": tipo and tipo[1],
            "numero": num and num[1], "allegato": alleg[1], "articolo": re.sub(r"[^\w .\-]", "", art[1])[-160:],
            "eli": eli and eli[1], "dal": iso(iv and iv.groups(), 0), "al": iso(iv and iv.groups(), 3), "stato_testo": stato}


def etichetta_coerente(etichetta, articolo, pagina):
    """Confronto indipendente dall'URL: numero d'articolo e, se scritti, numero/anno dell'atto."""
    if not etichetta or not articolo:
        return "LABEL_UNCHECKED"
    e = etichetta.lower()
    m = re.fullmatch(r"(\d+)([a-z]*)((?:\.\d+)?)([a-z]*)", norm(articolo))
    if not m:
        return "LABEL_UNCHECKED"
    pezzi = re.escape(m[1]) + (r"[\s\-]*" + m[2] if m[2] else "") + re.escape(m[3]) + (r"[\s\-]*" + m[4] if m[4] else "")
    dopo = r"(?![\d])" if (m[2] or m[3]) else r"(?!\d|\.\d|[\s\-]*(?:bis|ter|quater|quinquies|sexies|septies|octies|novies|\w*decies|\w*vicies)\b|\s*/)"
    arabo = re.search(r"(?<![\d./])" + pezzi + dopo, e)
    romano = any(norm(t) == norm(articolo) for t in re.findall(r"\b[ivxlc]+\b", e)) if not (m[2] or m[3]) else False
    if not (arabo or romano):
        return "LABEL_MISMATCH" if re.search(r"\d|\b[ivxlc]+\b", e) else "LABEL_UNCHECKED"
    atto = re.search(r"(\d+)\s*/\s*(\d{4})", e)
    if atto and pagina["numero"] and (atto[1], atto[2]) != (pagina["numero"], pagina["anno"]):
        return "LABEL_MISMATCH"
    return "LABEL_MATCH"


def estremi_urn(chiesto, p):
    """Tipo e data scritti nell'URN contro quelli dichiarati dalla pagina: il portale tollera differenze, qui si annotano."""
    semplice = lambda t: re.sub(r"(?<![a-z])(della|dello|dei|del)(?![a-z])|[^a-z]", "", (t or "").lower())
    aut = chiesto["autorita"] or ""
    atteso = (semplice(chiesto["tipo"]) if aut == "stato" else
              "decretopresidenteconsiglioministri" if aut.startswith("presiden") else "decreto")
    diversi = []
    if p["tipo"] and atteso != semplice(p["tipo"]):
        diversi.append("tipo: URN %s:%s, pagina %s" % (aut, chiesto["tipo"], p["tipo"]))
    if p["data"] and chiesto["data"] and len(chiesto["data"]) == 10 and chiesto["data"] != p["data"]:
        diversi.append("data: URN %s, pagina %s" % (chiesto["data"], p["data"]))
    return "; ".join(diversi)


def versione_coerente(chiesta, p, oggi):
    if not chiesta:
        return "VERSION_NOT_REQUESTED"
    if p["stato_testo"] == "NON_ANCORA_VIGENTE":
        return "TEMPORAL_UNAVAILABLE"
    if not p["eli"]:
        return "VERSION_UNVERIFIED"
    if chiesta == "originale":
        return "VERSION_MATCH" if p["eli"] == "ORIGINAL" else "VERSION_MISMATCH"
    if p["eli"] in ("ORIGINAL", "CONSOLIDATED"):
        return "VERSION_MISMATCH"
    g, m, a = p["eli"].split("/")
    mostrata = datetime.date(int(a), int(m), int(g))
    if chiesta == "vigente":
        return "VERSION_MATCH" if abs((mostrata - oggi).days) <= 1 else "VERSION_MISMATCH"
    if mostrata.isoformat() != chiesta:
        return "VERSION_MISMATCH"
    if not p["dal"]:
        return "VERSION_UNVERIFIED"
    return "VERSION_MATCH" if p["dal"] <= chiesta and (not p["al"] or chiesta <= p["al"]) else "VERSION_MISMATCH"


def verifica(voce, scarica=scarica, oggi=None):
    """voce: {url, etichetta?, atto? 'AAAA;N', articolo?, allegato?, versione?}. Restituisce un dizionario di stati."""
    oggi = oggi or datetime.date.today()
    url, chiesto = voce["url"], leggi_url(voce["url"])
    r = {"url": url, "etichetta": voce.get("etichetta"), "data_controllo": oggi.isoformat(),
         "attese_da": "attese" if any(k in voce for k in ("atto", "articolo", "allegato", "versione")) else "url"}
    f = scarica(url)
    r.update(curl_exit=f.get("curl_exit"), http=f.get("http"), url_effettivo=f.get("url_effettivo"))
    if f.get("curl_exit"):
        r.update(recupero=ERRORI_RETE.get(f["curl_exit"], "NETWORK_ERROR"), dettaglio=f.get("errore", ""))
    elif not 200 <= (f.get("http") or 0) < 300:
        r.update(recupero="HTTP_ERROR")
    else:
        p = leggi_pagina(f.get("html") or "")
        if p is None:
            r.update(recupero="PORTAL_ERROR_PAGE" if "Errore nel caricamento" in (f.get("html") or "") else "UNPARSEABLE_RESPONSE")
    if "recupero" in r:
        r["esito"] = "NON_VERIFICABILE"
        return r
    anno, numero = (str(voce["atto"]).split(";") + [None])[:2] if voce.get("atto") else (chiesto["anno"], chiesto["numero"])
    articolo = voce.get("articolo") or chiesto["articolo"]
    if chiesto["tipo"] == "costituzione" and not voce.get("atto"):
        atto = "ACT_MATCH" if p["titolo"].upper().startswith("COSTITUZIONE") else "ACT_MISMATCH"
    elif not anno or not p["anno"]:
        atto = "ACT_UNVERIFIED"
    else:
        atto = "ACT_MATCH" if (anno, numero or p["numero"]) == (p["anno"], p["numero"]) else "ACT_MISMATCH"
    r.update(recupero="FETCH_OK", pagina=p, atto=atto,
             allegato="ANNEX_MATCH" if str(voce.get("allegato", chiesto["allegato"])) == p["allegato"] else "ANNEX_MISMATCH",
             articolo="ARTICLE_NOT_REQUESTED" if not articolo else
             "ARTICLE_MATCH" if norm(articolo) == norm(p["articolo"]) else "ARTICLE_MISMATCH",
             etichetta_stato=etichetta_coerente(voce.get("etichetta"), articolo, p),
             versione=versione_coerente(voce.get("versione") or chiesto["versione"], p, oggi), stato_testo=p["stato_testo"],
             estremi_urn=estremi_urn(chiesto, p) or "coerenti",
             decorrenza_futura=bool(p["dal"] and p["dal"] > oggi.isoformat()))
    if "MISMATCH" in r["atto"] + r["allegato"] + r["articolo"]:
        r["esito"] = "DESTINAZIONE_DIVERSA"
    elif r["etichetta_stato"] == "LABEL_MISMATCH":
        r["esito"] = "ETICHETTA_DISCORDANTE"
    elif r["versione"] in ("VERSION_MISMATCH", "TEMPORAL_UNAVAILABLE"):
        r["esito"] = "VERSIONE_NON_CONFERMATA"
    elif r["versione"] == "VERSION_UNVERIFIED" or r["atto"] == "ACT_UNVERIFIED" or r["estremi_urn"] != "coerenti":
        r["esito"] = "VERIFICATO_IN_PARTE"
    else:
        r["esito"] = "VERIFICATO"
    return r


def riga(r):
    if r["esito"] == "NON_VERIFICABILE":
        return "%-23s | %s (curl %s, HTTP %s) %s | %s" % (r["esito"], r["recupero"], r["curl_exit"], r["http"], r.get("dettaglio", ""), r["url"])
    p = r["pagina"]
    return "%-23s | %s | posizione allegato %s | articolo mostrato: %s | %s %s %s %s %s | estremi URN: %s | testo: %s, in vigore dal %s%s al %s | %s" % (
        r["esito"], p["titolo"], p["allegato"], p["articolo"], r["atto"], r["allegato"], r["articolo"], r["etichetta_stato"],
        r["versione"], r["estremi_urn"], r["stato_testo"], p["dal"] or "?", " (DECORRENZA FUTURA)" if r["decorrenza_futura"] else "",
        p["al"] or "-", r["url"])


def main(argv):
    oggi = datetime.date.fromisoformat(argv[argv.index("--oggi") + 1]) if "--oggi" in argv else None
    if "--attese" in argv:
        voci = json.load(open(argv[argv.index("--attese") + 1], encoding="utf-8"))
    else:
        voci = [{"url": m[2] or m[3], "etichetta": m[1] or None} for m in LINK.finditer(sys.stdin.read())]
    massimo = int(argv[argv.index("--max") + 1]) if "--max" in argv else 30
    if len(voci) > massimo:
        print("ATTENZIONE: %d link, ne verifico solo i primi %d (usa --max per cambiare il limite)" % (len(voci), massimo), file=sys.stderr)
    esiti = []
    for voce in voci[:massimo]:
        esiti.append(verifica(voce, oggi=oggi))
        print(json.dumps(esiti[-1], ensure_ascii=False) if "--json" in argv else riga(esiti[-1]), flush=True)
        if esiti[-1].get("http") in (403, 429):
            print("FERMO: Normattiva ha rifiutato la richiesta (HTTP %s). Non riprovare subito." % esiti[-1]["http"], file=sys.stderr)
            break
        time.sleep(0.4)
    conta = {e: sum(1 for x in esiti if x["esito"] == e) for e in sorted({x["esito"] for x in esiti})}
    print("RIEPILOGO %s | link %d | %s" % ((oggi or datetime.date.today()).isoformat(), len(esiti), conta), file=sys.stderr)
    return 0 if all(x["esito"] == "VERIFICATO" for x in esiti) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
