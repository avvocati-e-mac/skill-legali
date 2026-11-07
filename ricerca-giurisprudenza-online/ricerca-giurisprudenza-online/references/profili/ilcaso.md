# Profilo: ilcaso.it (verificato con il browser integrato)

Le schede (www.ilcaso.it/sentenze/ultime/<numero>) sono rifiutate da WebFetch per una politica dello strumento: il `robots.txt` del sito (controllato il 2026-11-07) non vieta alcun percorso (`User-agent: *` con `Disallow:` vuoto), quindi la lettura nel browser è ammessa. Il testo integrale è un PDF in www.ilcaso.it/giurisprudenza/archivio/<numero>.pdf, leggibile con il browser integrato: nel pannello il PDF appare vuoto, quindi si estrae il testo con pdf.js caricato da cdnjs tramite javascript_tool. La ricerca interna del sito non filtra i risultati: cercare con WebSearch e parametro allowed_domains ["ilcaso.it"] (l'operatore site: viene ignorato). WebFetch accetta di solito solo URL comparsi nei risultati di ricerca.

Il sito ha anche contenuti in abbonamento: con Claude in Chrome, se l'utente è collegato e la pagina mostra contenuti riservati, fermati e chiedi (`arresto.md`).

## Campi (stessi di ricognizione.md)
- Pagina d'ingresso: www.ilcaso.it
- Come si cerca: WebSearch con allowed_domains ["ilcaso.it"]; la ricerca interna non filtra.
- URL della scheda: www.ilcaso.it/sentenze/ultime/<numero>
- URL del file: www.ilcaso.it/giurisprudenza/archivio/<numero>.pdf (PDF con testo)
- Formato: PDF testuale
- Strumento che funziona: browser integrato + pdf.js (cdnjs) via javascript_tool (verificato). Claude in Chrome: da verificare al primo uso (prima `get_page_text`, poi pdf.js); annota qui l'esito.
- `id` consigliato: il <numero> dell'URL
- Provvedimento di prova: non indicato nel profilo
- Da verificare al primo uso: se `scripts/scarica.py` riesce a scaricare direttamente i PDF dell'archivio (robots.txt lo consente; se il sito risponde con una pagina di login o di errore, lo script non tiene il file e lo segnala; non aggirare).
