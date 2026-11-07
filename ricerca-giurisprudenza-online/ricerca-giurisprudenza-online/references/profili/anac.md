# Profilo: anticorruzione.it (ANAC: pareri precontenzioso, delibere) - da terminale, ricognizione 2026-11-07

Tipo di sito: pubblico

robots.txt: Allow: /.

## Campi
- Pagina d'ingresso: www.anticorruzione.it
- Come si cerca: WebSearch con allowed_domains ["anticorruzione.it"] (pareri per numero e data). La pagina "consulta-i-documenti" con filtri: da verificare.
- URL della scheda: pagina HTML con la massima. Gli URL contengono un GUID: vanno presi dai risultati, non indovinati; alcune pagine hanno il prefisso /en/.
- URL del file: PDF scaricabile dal link della scheda
- Formato: PDF testuale
- Strumento che funziona: curl, poi pdftotext
- id consigliato: anac-<tipo>-<numero>-<anno>
- Provvedimento di prova: Parere n. 345 del 9/9/2025: HTTP 200, 6 pagine, circa 12.500 caratteri, testo pulito.
- Da verificare al primo uso: filtri della pagina documenti, limiti di frequenza.
