# Profilo: agcm.it (Autorita garante della concorrenza e del mercato) - da terminale, ricognizione 2026-11-07

Tipo di sito: pubblico

robots.txt: vieta solo i bollettini 1991-2000 e le relazioni oscurate.

## Campi
- Pagina d'ingresso: www.agcm.it
- Come si cerca: WebSearch con allowed_domains ["agcm.it"] (comunicati, es. PS12962). La pagina /ricerca-avanzata-provvedimenti: da verificare (probabile JavaScript).
- URL della scheda: comunicato HTML, con il link al provvedimento
- URL del file: PDF in /dotcmsdoc/allegati-news/, da trovare partendo dal comunicato
- Formato: PDF testuale
- Strumento che funziona: curl, poi pdftotext
- id consigliato: agcm-<codice>
- Provvedimento di prova: PS12962 (Trustpilot): PDF di 2,2 MB, HTTP 200, circa 125.000 caratteri.
- Da verificare al primo uso: provvedimenti piu vecchi (stanno nei bollettini), ricerca avanzata.
