# Profilo: ilcaso.it (verificato con il browser integrato e con Claude in Chrome)
Tipo di sito: privato (rivista/editore: se robots.txt vietasse un percorso, prima controlla i termini d'uso)

Le schede (www.ilcaso.it/sentenze/ultime/<numero>) sono rifiutate da WebFetch per una politica dello strumento: il `robots.txt` del sito (controllato il 2026-11-07) non vieta alcun percorso (`User-agent: *` con `Disallow:` vuoto), quindi la lettura nel browser è ammessa (e lo scaricamento automatico anche). Il testo integrale è un PDF in www.ilcaso.it/giurisprudenza/archivio/<numero>.pdf, leggibile con il browser integrato: nel pannello il PDF appare vuoto, quindi si estrae il testo con pdf.js caricato da cdnjs tramite javascript_tool. La ricerca interna del sito non filtra i risultati: cercare con WebSearch e parametro allowed_domains ["ilcaso.it"] (l'operatore site: viene ignorato). WebFetch accetta di solito solo URL comparsi nei risultati di ricerca.

Il sito ha anche contenuti in abbonamento: con Claude in Chrome, se l'utente è collegato e la pagina mostra contenuti riservati, fermati e chiedi (`arresto.md`). Attenzione al falso allarme: il menu "SCOPRI ED ENTRA IN PREMIUM" compare su TUTTE le pagine, anche pubbliche; non è un segnale di contenuto riservato. Le schede delle sentenze e i PDF dell'archivio sono pubblici.

## Campi (stessi di ricognizione.md)
- Pagina d'ingresso: www.ilcaso.it
- Come si cerca: WebSearch con allowed_domains ["ilcaso.it"]; la ricerca interna non filtra.
- URL della scheda: www.ilcaso.it/sentenze/ultime/<numero>
- URL del file: www.ilcaso.it/giurisprudenza/archivio/<numero>.pdf (PDF con testo)
- Formato: PDF testuale
- Strumento che funziona: browser integrato + pdf.js (cdnjs) via javascript_tool (verificato). Claude in Chrome (verificato il 2026-11-07 con l'estensione in Brave): `get_page_text` sul PDF NON funziona ("No text content found"); pdf.js 3.11.174 da cdnjs via `javascript_tool` sì (13 pagine, testo completo, con spazi spuri dentro le parole da togliere). La scheda HTML si legge con `javascript_tool` (`document.body.innerText`).
- `id` consigliato: il <numero> dell'URL
- Provvedimento di prova: 32960 (Tribunale Firenze, Sez. Imprese, 14 marzo 2025, R.G. 11053/2024), letto nel browser e scaricato con `scarica.py` e `scarica.sh`
- Download: `scripts/scarica.py` e `scarica.sh` scaricano i PDF dell'archivio con lo user-agent onesto della skill (verificato il 2026-11-07). Se un giorno il sito rispondesse con una pagina di login o di errore, lo script non tiene il file e lo segnala: non aggirare.
