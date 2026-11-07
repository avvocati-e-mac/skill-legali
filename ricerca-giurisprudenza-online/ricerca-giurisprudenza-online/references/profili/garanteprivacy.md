# Profilo: garanteprivacy.it (docweb) - da terminale, ricognizione 2026-11-07

Tipo di sito: pubblico

robots.txt vieta i PDF (/*pdf*, /*.pdf$) e c/portal; le pagine docweb-display sono permesse. Poiche e un sito pubblico, la lettura MIRATA dei PDF e ammessa (da dichiarare nei limiti del report); il download automatico dei PDF NO. In pratica conviene usare la pagina HTML.

## Campi
- Pagina d'ingresso: www.garanteprivacy.it
- Come si cerca: WebSearch con allowed_domains ["garanteprivacy.it"] (ottimo: restituisce i docweb con data e numero). Ricerca interna del sito: da verificare.
- URL della scheda e del file: https://www.garanteprivacy.it/web/guest/home/docweb/-/docweb-display/docweb/<n> (HTML)
- Formato: HTML
- Strumento che funziona: curl sulla pagina HTML, poi rimozione dei tag; togliere menu e navigazione.
- id consigliato: docweb-<n>
- Provvedimento di prova: docweb 9870832 (ChatGPT, 30/3/2023): HTTP 200, circa 10.200 caratteri di testo.
- Da verificare al primo uso: limiti di frequenza.
