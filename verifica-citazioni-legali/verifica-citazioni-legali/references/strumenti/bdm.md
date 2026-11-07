# Banca Dati di Merito (BDM, Ministero della Giustizia): CLI `bdm` e MCP

Tribunali e corti d'appello, civile, dal 2016 circa. Non contiene la Cassazione. Per i dettagli carica la skill `banca-dati-merito`.

## Che cosa dà
- Estremi ufficiali: ufficio, tipo, R.G. con anno, data, materia, parole chiave, gradi collegati presenti nella banca dati.
- Testo integrale pseudonimizzato. Il PDF si scarica in due passi, previo consenso.

## Limiti e cautele
- **Sessione** con identità digitale, scadenza breve (circa 2 ore). Se `bdm_auth_status` dice «scaduta», il login lo fa l'utente (`! bdm login`).
- **Al primo rifiuto (403/429) fermati** e riferisci: i retry hanno causato in passato l'inibizione dell'utenza.
- I valori di `ufficio` e `materia` vanno presi **esatti** da `bdm_elenca_valori`: un valore scritto a memoria dà zero senza errore.
- Due parole nella ricerca libera **allargano** i risultati. Per verificare una citazione usa `modalita=esatta` con una frase del provvedimento, più ufficio e `anno_ruolo`.
- Fissa un tetto di richieste prima di iniziare (es. 5 per provvedimento).
- I nomi di giudici e difensori restano in chiaro: non riportarli nel report.

## Uso tipico per una verifica
1. `bdm_elenca_valori(uffici)` → valore esatto.
2. `bdm_cerca(testo="<frase esatta>", modalita="esatta", ufficio=…, anno_ruolo=…)`.
3. `bdm_apri(id)`: estremi e gradi collegati.
