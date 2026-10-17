# BuddaLaw — filtri di ricerca e uffici

Valori osservati nel sondaggio del 17 ottobre 2026 (server MCP 1.30.0). Valgono per `search_case_law` e, dove indicato, per `search_similar_cases`.

## Regola generale

I filtri si sommano: ogni filtro in più restringe. Zero risultati con più filtri non significa che il tema non abbia giurisprudenza: togli un filtro alla volta e dillo all'utente.

## Ufficio: `list_uffici` → `codiceufficio`

Il filtro per ufficio si chiama `codiceufficio` e vale **solo** per `merito`, `amministrativo` e `tributari`. Su `civile`, `penale` e le altre banche dati non dà errore ma azzera i risultati: omettilo.

1. Chiama `list_uffici` con il dominio corrispondente:

   | Ricerca su | `dominio` di `list_uffici` | Voci osservate |
   |---|---|---|
   | `merito` | `merito` | 170 |
   | `amministrativo` | `amministrativo` | 32 |
   | `tributari` | `tributario` | 125 |

2. Scegli la voce dalla `label` (nome leggibile). La prima voce («Tutte le …») ha `codice` null e non filtra.
3. Passa il campo `codice` come `codiceufficio`, **come stringa**, con gli zeri iniziali.

```json
{"tool": "list_uffici", "arguments": {"dominio": "merito"}}
```

```json
{"tool": "search_case_law", "arguments": {"query": "licenziamento per superamento del periodo di comporto", "search_category": "merito", "codiceufficio": "0151460094", "anno": 2025}}
```

Esempi di codici visti nelle risposte: Tribunale di Milano `0151460094`; Corte d'appello di Caltanissetta `0850040065`; TAR Lazio, Roma `tar_rm`; Consiglio di Stato `cds`; CGA Sicilia `cgagiur`; una Corte di giustizia tributaria `U24`. Prendi comunque il codice da `list_uffici`, non da questo elenco.

Dati non sempre puliti: alcune etichette hanno caratteri sbagliati (es. «ForlÃ¬») e qualche ufficio compare due volte (Trentino con `V75` e `V76`). Se due voci sembrano lo stesso ufficio, prova la prima e, se torna vuota, la seconda.

## Giudice: `giudice`

Solo per `merito` (anche in `search_similar_cases`). Basta il cognome: la ricerca è parziale («Rossi» trova «MARIO ROSSI»). I nomi dei giudici nelle risposte sono in chiaro: prima di riportarli in un documento per altri, avvisa l'utente.

## Date: `data_deposito` e `anno`

- `data_deposito` filtra **un solo giorno esatto**, non «da quella data in poi». Un giorno festivo dà zero risultati.
- Il formato dipende dalla banca dati:

  | Formato | Banche dati |
  |---|---|
  | AAAA-MM-GG | `civile`, `penale`, `privacy` |
  | GG/MM/AAAA | `tributari`, `prassi`, `merito`, `amministrativo`, `costituzionale`, `eu-case-law` |

  Il formato sbagliato provoca un `RetryError`: una sola prova nell'altro formato, poi fermati.
- Per un periodo («sentenze recenti», «dopo la riforma Cartabia») usa `anno`, intero, con una ricerca per anno, nel tetto delle chiamate. Calcola gli anni solo se la data di oggi è nel contesto; altrimenti chiedila.
- Nel merito `anno` può differire dall'anno di deposito (anno 2025, deposito 02/01/2026): cita con la data di deposito.

## Numero: `numero`

- In `search_case_law` è una **stringa a confronto esatto**. Cassazione: 5 cifre con zeri (`"03285"`; `"3285"` dà zero risultati).
- Per una sentenza di Cassazione nota è più semplice `get_judgement` con `dominio`, `numero` e `anno` (gli zeri vengono normalizzati), senza `ufficio`.

## Peso semantico: `semantic_weight`

Cambia molto l'ordine dei risultati (fra 0,2 e 0,9 solo un risultato su quattro in comune).

| Valore | Quando |
|---|---|
| 0,2–0,3 | formule testuali, nomi di istituti, numero di una circolare |
| 0,7 | predefinito, ricerche miste |
| 0,9 | descrizione di un fatto o di un principio a parole proprie |

## Numero di risultati: `max_results`

- `search_case_law`: da 1 a 20, predefinito 5. Usa 3 per una sentenza mirata, 5 di norma, 10 per una panoramica.
- `search_similar_cases`: da 1 a 20, predefinito 10.
- `search_articles`: il valore viene ignorato; tieni solo i risultati pertinenti.
