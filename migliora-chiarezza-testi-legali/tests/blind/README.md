# Cartella `blind/`

Qui `blind_review.py` crea una sottocartella per ogni sessione di revisione
umana **cieca A/B** (`tests/blind/<nome-sessione>/`), con tre file:

- `coppie.json` — le coppie anonime mostrate all'avvocato (testo originale,
  contesto del caso, "Testo 1" e "Testo 2" ripuliti). Non contiene mai il
  nome del modello, la versione della skill o l'esito del harness.
- `mappa_segreta.json` — la mappa che rivela quale braccio (versione/variante
  della skill) corrisponde a "Testo 1" e "Testo 2" per ciascuna coppia. Va
  aperta solo dopo aver completato la revisione, con
  `python3 blind_review.py unblind --session <nome-sessione>`.
- `risposte.json` — le valutazioni salvate automaticamente dall'interfaccia
  web mentre l'avvocato revisiona le coppie.

Il contenuto di ogni sessione (compresa la mappa segreta) non va mai
committato: il file `.gitignore` di `tests/` esclude tutta la cartella
`blind/` tranne questo README, per evitare di versionare per sbaglio
risultati intermedi o la chiave che disvela l'anonimizzazione.
