# Profilo: giustizia tributaria (Corti di giustizia tributaria) - verificato con Claude in Chrome il 2026-11-07, lettura solo tramite download

Tipo di sito: pubblico

Da terminale il sito risponde 403 "Access Denied" (Akamai) a curl, anche su robots.txt: è un blocco anti-robot, non aggirarlo (niente cambio di user-agent). Nel browser invece si apre normalmente, senza captcha, login o banner: usare il browser non è un aggiramento.

## Campi
- Pagina d'ingresso: https://bancadatigiurisprudenza.giustiziatributaria.gov.it/ → modulo su `/ricerca`
- Contenuto: sentenze delle Corti di giustizia tributaria di I e II grado, pseudonimizzate, gratuite.
- robots.txt: non leggibile da terminale (403); trattandosi di sito pubblico vale la regola di `ambienti.md` (lettura mirata ammessa).
- Come si cerca: SOLO dal modulo nel browser (parole + anno e altri filtri). L'URL resta `/ricerca` senza parametri: la ricerca non si ricostruisce da URL. Risultati ordinati per data, non per pertinenza; il filtro per parole è poco selettivo (prova: "notifica avviso di accertamento PEC" + 2024 → 17.789 risultati): restringere con anno, grado, sede e parole più tecniche.
- URL della scheda: `/ricerca/dettaglio/<due id numerici>` (opachi, non costruibili).
- URL del file: nessun link diretto al PDF.
- Formato: PDF mostrato in un riquadro Adobe PDF Embed su altro dominio: `get_page_text` e `javascript_tool` vedono solo il guscio (~840 caratteri); pdf.js non applicabile.
- Strumento che funziona: browser (Claude in Chrome verificato; un subagente alla volta). Lettura: pulsante "Scarica provvedimento" → il file arriva nella cartella Download dell'utente → testo con `pdftotext`. Lo scaricamento dal browser richiede il SÌ dell'utente: chiedilo una volta sola per l'elenco dei provvedimenti da leggere (estremi e numero), poi procedi. Non leggere a colpi di schermate (lento e costoso) salvo pochissime pagine.
- Nota tecnica: `javascript_tool` non restituisce risultati che contengono link (href): estrarre solo testo.
- id consigliato: `cgt<grado>-<sede>-<anno>-<numero>` (es. `cgt1-roma-2024-16159`)
- Provvedimento di prova: CGT di primo grado di Roma, sentenza n. 16159/2024, depositata il 31/12/2024 (aperta; testo non estratto perché il download non era autorizzato nel test).
- Da verificare al primo uso: nome e posizione del file scaricato; se il PDF scaricato ha testo o è una scansione; limiti di frequenza.
- Alternative: l'utente scarica i PDF e li passa alla skill; oppure una banca dati con licenza (es. BuddaLaw, sentenze tributarie).
