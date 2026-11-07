# Profilo: giustizia-amministrativa.it (TAR, Consiglio di Stato) - verificato il 2026-11-07

Tipo di sito: pubblico

Ricognizione fatta da terminale; il browser NON serve. robots.txt assente (404) su www. e mdp.: nessun percorso vietato.

## Campi (stessi di ricognizione.md)
- Pagina d'ingresso: www.giustizia-amministrativa.it
- Come si cerca: WebSearch con allowed_domains ["giustizia-amministrativa.it"]. Consiglio dalla valutazione: fare interrogazioni distinte per Consiglio di Stato e per TAR. Avvertenza: i riassunti della ricerca web possono datare male le notizie (2018/2019 presentate come nuovo codice); fidarsi solo del testo del provvedimento.
- URL della scheda: non c'e una scheda separata; si apre direttamente il provvedimento.
- URL del file: https://mdp.giustizia-amministrativa.it/visualizza/?nodeRef=&schema=<ufficio>&nrg=<anno+num ricorso>&nomeFile=<anno+num provv>_<tipo>.<html|xml|pdf>&subDir=Provvedimenti (schema: cds, tar_na, tar_rm, ...; tipo 01 sentenza TAR, 11 sentenza CdS, 20 sentenza breve). Pulire i "&amp=" degli URL dei risultati.
- Formato: varia (la maggior parte .html, alcuni .xml, alcuni .pdf). L'estensione NON e intercambiabile: un'estensione sbagliata risponde 200 con la pagina "404 - Pagina non trovata". Controllare SEMPRE il testo ricevuto. Provare l'estensione del risultato; se fallisce, le altre due.
- Strumento che funziona: shell. `curl -sS -L -m 30 -A "ricerca-giurisprudenza-online/1.0" -o f "<URL>"`; PDF con `pdftotext -layout f out.txt`; HTML/XML togliendo i tag (python3, re e html.unescape). Browser non necessario.
- id consigliato: <ufficio>-<anno>-<numero> (es. cds-2026-3008)
- Provvedimento di prova: Cons. Stato, Sez. III, n. 3008/2026, R.G. 8682/2025, pubbl. 16/04/2026 (PDF, 25.711 caratteri estratti).
- Da verificare al primo uso: ricerca interna con filtri (sede, sezione, anno) via URL: da verificare; limiti di frequenza: da verificare (usare pause).
