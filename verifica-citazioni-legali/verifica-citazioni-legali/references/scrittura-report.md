# Scrittura del report: chiaro al primo colpo, azionabile in modo puntuale

Chi legge è un avvocato con poco tempo, spesso a ridosso di una scadenza. Deve capire **in 30 secondi**:
- se l'atto ha problemi seri;
- quali sono;
- dove si trovano;
- che cosa fare.

Il dettaglio serve a chi vuole controllare, non a chi deve decidere.

## Struttura a strati (modello: `assets/modello_report.md`)
1. **Esito in breve**, al massimo 8 righe:
   - conteggi per gravità;
   - una frase sul rischio complessivo;
   - che cosa non è stato verificato e perché.

   Deve stare in piedi da solo.
2. **Tabella delle azioni**, ordinata: prima i bloccanti, poi i gravi, poi i formali. Una riga per ogni intervento.
3. **Schede**, una per ID, tutte con lo stesso schema.
4. **Appendici**: norme, rilievi non di citazione, limiti degli strumenti, rinvio al registro.

## Regole
- **Prima il verdetto, poi il perché.** «Da eliminare: le Sezioni Unite escludono questo termine per il direttore dei lavori», non il contrario.
- **Una frase, un'idea.** Frasi brevi, soggetto e verbo vicini, nessun inciso lungo.
- **Azioni con un solo verbo**, da questo elenco chiuso:
  - **ELIMINA**: togli la citazione o il passo;
  - **CORREGGI**: estremi, comma, link, refuso;
  - **SOSTITUISCI**: un'altra pronuncia o un altro passo, verificati;
  - **RIFORMULA**: il periodo, perché il principio è diverso da quello scritto;
  - **VERIFICA SUL PDF**: riscontro manuale necessario (OCR, pagina);
  - **DECIDE L'AVVOCATO**: la correzione cambia un argomento o una strategia.
- **Dove**: la **stringa da cercare** dell'inventario, univoca e corta, da incollare in Trova; tra parentesi la posizione (riga, paragrafo, nota o pagina), solo indicativa. La stringa contiene sempre estremi **interi**: mai un numero o una parola tagliati, che sembrerebbero un altro errore.
- **Intervento in tabella**: quando la correzione sta in 12 parole circa, scrivila direttamente come `prima` → `dopo`. Per ELIMINA, indica l'inizio e la fine del passo da togliere. Solo le riformulazioni lunghe rinviano alla scheda. Chi legge la tabella deve poter correggere senza aprire nient'altro.
- **Ciò che non è verificato** (fuori ambito, non reperito, strumento mancante) va dichiarato come **ancora da controllare**, mai lasciato ambiguo, ed **elencato per ID**: chi legge deve sapere quali voci restano aperte senza aprire l'inventario.
- La stringa da cercare è testo semplice, senza `*`, `\textit{}`, `~` né virgolette spaiate: deve trovarsi sia nel sorgente sia nel documento impaginato. Lo script la sceglie così; se la scrivi a mano, rispetta la stessa regola.
- **ID stabili** (C01…) in inventario, tabella, schede e registro. Non rinumerare dopo la consegna.
- **Testo da incollare** nel formato sorgente, pronto all'uso (vedi `formati/<formato>.md`). Ogni virgolettato al suo interno è verificato (IDENTICA) e ogni estremo è quello accertato.
- **Niente gergo degli strumenti** nel corpo: punteggi di somiglianza, nomi di tool, id interni e query vanno in appendice o nel registro. Nel corpo bastano estremi e fonte («testo integrale», «massima ufficiale»).
- **Linguaggio calibrato**: «non reperita con gli strumenti usati» non è «inesistente»; «verificata sulla massima» non è «verificata sul testo».
- **Le citazioni corrette** finiscono in un elenco compatto («Verificate senza rilievi: C03, C05, C08»), non in schede.
- I **rilievi non di citazione** (refusi, date incoerenti, numerazione dei documenti, nomi non anonimizzati) vanno solo elencati in appendice: non sono il compito principale.

## Autocontrollo prima della consegna
1. Leggi solo l'esito in breve e la tabella: sapresti dire le 3 azioni più urgenti e dove farle? Se no, riscrivi.
2. Ogni riga della tabella ha una stringa da cercare intera, un verbo dell'elenco e, se la correzione è breve, il `prima → dopo`?
3. Ogni scheda ha un «testo da incollare» o il motivo per cui manca (es. ELIMINA)?
4. Hai passato `confronta_verbatim.py` sui virgolettati proposti?
5. Nel report ci sono nomi da escludere?
