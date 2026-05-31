# Query set — confronto SearXNG-skill vs Perplexity

Pre-registrato (ipotesi dichiarate *prima* della raccolta dati, per evitare razionalizzazione post-hoc).
Data esecuzione: 2026-05-30. Giudice: Claude (stesso modello → bias correlato dichiarato).

Per ogni query: ID, testo, dominio skill atteso, tipo, tier Perplexity (`quick`/`standard`, mai `research`),
ipotesi di vantaggio (chi dovrebbe vincere e perché). Le ipotesi NON influenzano la valutazione cieca:
servono solo a misurare quanto il risultato conferma/smentisce le attese.

## Convenzione tier Perplexity (parità con la logica della skill pwm)
- `fact` → `quick` (Sonar 2)
- `news` / `comparison` / `deep` / ambiguo → `standard` (1 Pro Search)
- mai `research` (Deep Research) in autonomia

---

## A. Query storiche (continuità col benchmark a 4 modalità)

| ID | Query | Dominio | Tipo | Tier pplx | Ipotesi vantaggio |
|---|---|---|---|---|---|
| T01 | In che anno è stata fondata OpenAI? | general | fact | quick | Pari (fatto stabile; entrambi corretti) |
| T03 | Quali sono gli annunci e le novità di OpenAI di maggio 2026? | ai-generativa | news | standard | Perplexity (recency/sintesi) vs skill (recency IT con time_range) |
| T04 | Ricetta originale della pasta cacio e pepe romana | cucina | recipe | standard | SearXNG-skill (lingua IT forzata + progressive disclosure) |
| T06 | Differenze tra interfaces e types in TypeScript, quando usare quale | informatica | comparison | standard | Pari (dominio EN, entrambi forti) |
| T07 | Chi è l'attuale CEO di Google nel 2026? | general | fact | quick | Pari (fatto verificabile) |
| T11 | Cosa prevede la normativa italiana sui cookie e il GDPR per i siti web? | legale-it/dottrina | deep | standard | SearXNG-skill (fonti IT autorevoli) |
| T12 | zzxqpfm blorgatron quantum spaghetti del futuro 2099 | general | failure | standard | SearXNG-skill ("0 risultati" onesto vs allucinazione attesa pplx) |

## B. Query nuove (mirate ai punti deboli/forti sospetti, un dominio skill ciascuna)

| ID | Query | Dominio | Tipo | Tier pplx | Ipotesi vantaggio |
|---|---|---|---|---|---|
| N01 | Commenti dottrinali sull'abuso di dipendenza economica nel diritto italiano | legale-it/dottrina | deep | standard | SearXNG-skill (dottrina IT: Altalex/Diritto.it; pplx rischia fonti EN o generiche) |
| N02 | Procedimento della carbonara di Giallozafferano | cucina | recipe | standard | SearXNG-skill (S12: heading sinonimo, lettura mirata 1 URL IT) |
| N03 | Confronto aggiornato tra Claude Opus 4.x e GPT-5.x per task di reasoning | ai-generativa | comparison | standard | Perplexity (recency + sintesi multi-fonte su topic in rapida evoluzione) |
| N04 | Come usare async/await in Python 3.12 e differenze rispetto a 3.10 | informatica | deep | standard | Pari (docs ufficiali EN; vantaggio a chi cita docs.python.org) |
| N05 | Sentenza Cassazione n. 999999/2099 sul danno da spaghetti quantistici | legale-it/giurisprudenza | failure | standard | SearXNG-skill ("non esiste" onesto; pplx rischia di confabulare una sentenza) |

---

## Note metodologiche per la raccolta

- **Stessa data** per entrambi i lati (recency comparabile).
- **Lato Perplexity**: `pwm ask "<query>" --intent <tier> --json` → `test/perplexity_raw/<ID>.json`.
- **Lato SearXNG-skill**: eseguo la query *applicando la SKILL.md v3 attuale* (header, classificazione,
  progressive disclosure reali) → `test/searxng_raw/<ID>.md` con: header `[...]`, fonti ordinate,
  risposta, chars ingeriti (search output + letture), n. tool call.
- **Failure cases (T12, N05)**: il criterio è binario e verificabile — il sistema dichiara l'assenza
  di risultati / l'inesistenza, oppure confabula? Nessun giudizio soggettivo.
