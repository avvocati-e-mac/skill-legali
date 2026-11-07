# Profilo: ilcaso.it (verificato)

Le schede (www.ilcaso.it/sentenze/ultime/<numero>) sono bloccate per WebFetch (robots). Il testo integrale è un PDF in www.ilcaso.it/giurisprudenza/archivio/<numero>.pdf, leggibile con il browser integrato: nel pannello il PDF appare vuoto, quindi si estrae il testo con pdf.js caricato da cdnjs tramite javascript_tool. La ricerca interna del sito non filtra i risultati: cercare con WebSearch e parametro allowed_domains ["ilcaso.it"] (l'operatore site: viene ignorato). WebFetch accetta di solito solo URL comparsi nei risultati di ricerca; un rifiuto robots_disallowed è una politica del sito: non riprovare.

## Campi (stessi di ricognizione.md)
- Pagina d'ingresso: www.ilcaso.it
- Come si cerca: WebSearch con allowed_domains ["ilcaso.it"]; la ricerca interna non filtra.
- URL della scheda: www.ilcaso.it/sentenze/ultime/<numero>
- URL del file: www.ilcaso.it/giurisprudenza/archivio/<numero>.pdf (PDF con testo)
- Formato: PDF testuale
- Strumento che funziona: browser integrato + pdf.js (cdnjs) via javascript_tool
- `id` consigliato: il <numero> dell'URL
- Provvedimento di prova: non indicato nel profilo
- Da verificare al primo uso: se `scripts/scarica.py` riesce a scaricare direttamente i PDF dell'archivio (il percorso potrebbe non essere consentito da robots.txt: in tal caso lo script non scarica e lo segnala; non aggirare, apri i PDF dal browser integrato).
