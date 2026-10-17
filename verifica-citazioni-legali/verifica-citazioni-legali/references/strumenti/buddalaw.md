# BuddaLaw (MCP)

Banca dati commerciale: Cassazione civile e penale, merito, Corte costituzionale, amministrativo, tributario, UE. Per i dettagli operativi carica la skill `buddalaw`.

## Che cosa dà
- `search_case_law` con `numero` e `anno` (e una `query` tematica): restituisce passi di **testo** con ECLI, data di deposito, sezione e `public_url`. Utile per verificare l'esistenza e trovare i passi.
- `get_judgement` con `dominio` e `idatto` (ECLI): **testo integrale**. Per la Cassazione il dominio è solo `civile` o `penale`.
- Il numero può essere registrato con zeri iniziali (es. `00619`): se `619` dà zero, riprova con 5 cifre.

## Limiti e cautele
- Il campo **«sintesi» è un riassunto automatico**: può attribuire alla sentenza articoli o principi che il testo non contiene. Non è mai una prova; si cita il testo.
- **Copertura incompleta**: alcune pronunce (anche di Cassazione) mancano. Un «not found» vuol dire NON REPERITA: prova Italgiure.
- I testi sono pseudonimizzati («A___»), quindi i nomi propri non sono verificabili.
- Le risposte di `get_judgement` possono essere molto lunghe.
  - Oltre una certa soglia il sistema le salva da solo in un file temporaneo: copialo in `fonti/`.
  - Sotto soglia arrivano in conversazione: scrivi tu il campo `text` in `fonti/<numero>_<anno>.txt`.
  - Poi usa `confronta_verbatim.py` e `grep` invece di rileggerle per intero.
- In un'intestazione troncata la sezione si ricava dalla formula di chiusura o dalle citazioni incrociate.
