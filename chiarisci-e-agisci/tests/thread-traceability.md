# Tracciabilità con il thread Perplexity

Thread sorgente: `6e5c8432-ff95-4730-a72f-994b520a15d5` — “Prima analisi ed utilizzo meta del sistema”.

Questa matrice riassume le decisioni, senza ripubblicare la conversazione personale completa.

| Turno | Decisione consolidata | Implementazione nella skill | Test |
|---:|---|---|---|
| 2 | Usare l'IA per verificare e far lavorare l'utente, non per sostituirlo; scomporre e chiarire | Contratto maieutico e modalità organizzazione | C001–C003 |
| 4–5 | L'IA interroga l'utente con maieutica vincolata; target principale avvocati | Domande durante il chiarimento e workflow professionali/legali | C001, C004, C007 |
| 5 | La presenza esterna serve come accountability; l'evidenza sul body doubling resta non conclusiva | Accountability tramite impegni e checkpoint, senza affermazioni cliniche | C011 |
| 6 | Valutare forma e contenuto; segnalare risposte errate o incomplete | Segnalazione di contraddizioni, presupposti non verificati e lacune | C006, C009 |
| 6 | La conversazione deve “mettere in movimento” l'utente | Primo passo minimo e verifica dell'esito | C001, C002 |
| 6 | Nessuna memoria dei dati del cliente e attenzione alla riservatezza | Divieto di memorizzazione e minimizzazione dei dati | C005 |
| 6 | Funzionare in chat, Cowork e ambienti code con checkpoint | Rami runtime e fallback testuale; approvazione prima di file/esecuzione | C012, C014 |
| 6 | Supportare organizzazione, prodromi redazionali e priorità | Tre reference caricate condizionatamente | C001, C004, C007 |
| 7 | Urgenza basata su termini oggettivi; importanza su valore e rilevanza del cliente | Tre dimensioni separate e regole di prevalenza | C006–C009, C013 |
| 7 | Usare progressive disclosure con un file per ogni subtask | SKILL principale più reference di modalità | Test statici e C001/C004/C007/C014–C016 |
| 7–8 | A fine sessione proporre nuovi workflow; niente `LEARNINGS.md` | Reference di integrazione con checkpoint e divieto di archivio conversazioni | C015, C016 |
| 8 | Anonimator appartiene alla narrazione del podcast, non alla skill | Nessun riferimento ad Anonimator nei sorgenti o nell'archivio | Test statico dedicato |

## Esito della verifica

La baseline rappresentava tutte le decisioni sostanziali del thread, ma lasciava ambigue sufficienza del chiarimento, separazione dei checkpoint, minimizzazione dei dati già ricevuti e condizionalità della reference di integrazione. La versione ottimizzata rende questi vincoli espliciti e li collega ai test statici e comportamentali indicati nella matrice.
