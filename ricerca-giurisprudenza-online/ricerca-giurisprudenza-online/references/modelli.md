# Scelta del modello per fase

## Principio
- Usa il modello più economico che sa risolvere il compito. Mai partire dal più alto "per sicurezza".
- Ciò che è meccanico e verificabile (conteggi, controlli, formati) lo fanno gli script: 0 token.
- Il modello principale (orchestratore) decide e controlla; non esegue lavoro ripetitivo.

## Tabella compito -> livello
Codex/OpenAI: scegli tra i modelli disponibili nel runtime; non inventare nomi.

| Compito | Claude | Codex/OpenAI |
|---|---|---|
| Ricognizione di un sito con profilo | haiku (o tu, se bastano 2-3 chiamate) | modello piccolo/economico |
| Ricognizione di un sito nuovo | sonnet (deve capire struttura e blocchi) | modello intermedio |
| Interrogazioni di ricerca con profilo | haiku, con elenco deciso da te | modello piccolo/economico |
| Estrazione meccanica (scarico, testo, citazioni, estremi) | haiku | modello piccolo/economico |
| Qualificazione giuridica (ruolo del tema, ratio/obiter, causa dell'esito) | haiku + verifica sonnet solo sulle schede "decisivo" o `tema_causa=si` | piccolo + verifica intermedio, stesse schede |
| Bozza | sonnet | modello intermedio |
| Red team | sonnet | modello intermedio |
| Pagine dei PDF (Fase 5b, `pagine.py`) | script: 0 token, nessun modello | uguale |
| Report finale | sonnet (l'orchestratore controlla e applica le correzioni del red team) | intermedio |
| Profilo di un sito nuovo | sonnet | modello intermedio |

Perché (misure 7 nov 2026, appalti, 8+1 provvedimenti): haiku ha estratto 31/31 citazioni e tutti gli estremi giusti (circa 150k token per 4 provvedimenti), ma ha sovrastimato "decisivo" in 7 schede su 8 (realisticamente 5), ha preso un obiter per ratio e un'indicazione parziale per omissione. Sonnet diretto sulle schede costerebbe di più su tutte; la verifica sonnet sulle sole schede "decisivo" corregge l'errore a costo contenuto. Il red team sonnet ha trovato 10 rilievi reali (106k); la bozza sonnet (74k) eredita le sovrastime, quindi la verifica va fatta prima.

## Risalita
Sali di un solo livello, e solo per quel compito, se:
- `controlli.py` fallisce due volte sulla stessa scheda;
- il subagente supera il tetto di chiamate senza risultato;
- il testo è molto lungo o confuso (soglia indicativa: oltre 60.000 caratteri; da tarare con le prossime ricerche) o lo scarico dà testo illeggibile;
- il tema ha un contrasto dichiarato tra orientamenti (qualificazione: sempre sonnet).
Opus solo se sonnet fallisce due volte e l'utente conferma.

## Tetti e risposte brevi
Ogni subagente ha un tetto di chiamate (indicato nella fase) e risponde in max 150 parole; il materiale va su file. È la leva principale di costo.

## Misura
Nel report, sezione limiti, una riga: modelli usati per fase (es. "estrazione haiku, verifica sonnet su 5 schede, bozza e red team sonnet").
