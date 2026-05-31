# Red teaming V2 — dopo la validazione multi-giudice

Aggiorna `RED_TEAM.md` (V1) con l'esito dei 5 rater. Due difetti V1 chiusi/mitigati, **due nuovi scoperti**.

## Stato difetti V1

| ID | Difetto | Stato V2 |
|---|---|---|
| RT1 | "delta E5 +15%" su pool diversi | **corretto** (numero rimosso) |
| **RT2** | **1 solo giudice (Claude)** | ✅ **CHIUSO** — 5 rater (Claude+4 esterni), Krippendorff α per criterio |
| RT3 | circolarità label nDCG | mitigato (sensitivity analysis, delta robusto) |
| RT4 | "pplx non confabula" troppo netto | corretto |
| RT5 | 12 query, 0 ripetizioni | **ancora aperto** — anzi rafforzato: 5 query → α su 8–10 unità è indicativo, non forte |
| RT6 | routing legale (Normattiva/BuddaLaw) non testato | ancora aperto |
| RT7 | asimmetria misura token | dichiarato |
| RT8 | citation-precision su campione minimo | **parzialmente chiuso** — ora misurata su 5 query × 5 rater; risultato: α=0.323 (criterio intrinsecamente poco affidabile, non colpa del campione) |

## Nuovi difetti scoperti DAL multi-giudice

### 🔴 RT9 — Self-preference / leniency bias di Claude (CONFERMATO su N03)
Il multi-giudice ha trovato la prova concreta di ciò che RT2 temeva in astratto: su **N03, risposta Perplexity,
Q1_corretto**, io (Claude) avevo detto ✅ mentre **GPT, Gemini, Kimi e Nemotron dicono ❌ all'unanimità (4/4)**.
La risposta Perplexity era datata (Opus 4.7 vs GPT-5.5, fonti 2025, conclusione invertita rispetto ai dati 2026).
- **Implicazione**: alcuni giudizi single-rater di V1 erano contaminati dal mio bias. Non posso sapere quanti senza
  rivalutare tutto a 5 rater. I criteri con α basso (Q1 0.564, Q3 0.562, Q5 0.323) sono i più a rischio.
- **Mitigazione**: per i criteri α<0.80, usare la **maggioranza dei 5 rater**, non il mio voto. Fatto in `RESULT.md §4`.
- **Limite**: 4 dei 5 giudici (incluso me) sono comunque LLM; potrebbero condividere bias non visibili. Ma sono di
  4 vendor diversi → la convergenza 4/4 contro Claude è un segnale forte di bias *mio*, non loro.

### 🟡 RT10 — Nemotron è un outlier sistematico
Nemotron 3 Super è in minoranza in 5 degli 8 disaccordi (T11-B-Q1, N01-A-Q5, N02-A-Q3, N03-A-Q3 + concorda con
minoranza su N03-B-Q5). È più severo/idiosincratico degli altri.
- **Rischio**: includerlo a peso pieno sposta la maggioranza su criteri al limite.
- **Gestione**: dove il booleano è verificabile sui file, il suo voto discorde è **scartato** (regola utente); dove
  è soggettivo, è riportato ma non decide da solo. NON lo elimino dai dati grezzi (sarebbe cherry-picking).
- **Da indagare**: con più query si potrebbe stabilire se Nemotron è semplicemente "severo calibrato" o "rumoroso".

### 🟢 RT11 — `-s none` impedisce ai giudici di verificare fatti nuovi
I giudici valutano i testi + la mia fact-key, ma non possono controllare se ENTRAMBE le risposte condividono un
errore che la fact-key non cattura. La fact-key l'ho scritta io → eredita il mio eventuale errore.
- **Mitigazione possibile (futura)**: una passata aggiuntiva con `-s web` su 1–2 query per cross-check, accettando
  che introduce la variabile "ricerca del giudice". Non fatto qui per non confondere i due regimi.

### 🟢 RT12 — La fact-key di N03 era costruita da dati SearXNG (potenziale circolarità pro-SearXNG)
La fact-key di N03 ("Opus 4.8 in testa su HLE") viene dai dati che SearXNG aveva letto (System Card via vellum).
Quindi giudicare Perplexity "datato" contro quella fact-key **favorisce strutturalmente SearXNG** su quella query.
- **Difesa**: la fact-key è verificabile indipendentemente (Opus 4.8 > 4.7 è un fatto pubblico di maggio 2026, non
  un'opinione di SearXNG). Ma la formulazione andava marcata come potenzialmente di parte. **Lo dichiaro ora.**
- **Effetto**: il "punto a SearXNG su N03" va preso con questa cautela. Non annulla il reperto del self-preference
  (resta vero che 4 giudici hanno visto la datazione e io no), ma ridimensiona il "SearXNG vince N03" come vittoria netta.

## Cosa regge dopo V2
- α=1.0 su lingua/recency → quei giudizi sono solidi a prescindere dal rater.
- Il pareggio nDCG (retrieval) non è toccato dal multi-giudice (riguarda la generazione).
- Il declassamento di Perplexity da gold-standard è ora **doppiamente supportato**: letteratura (Liu et al.) +
  misura diretta (Q5 α=0.323, e Perplexity datato su N03).

## Azioni ancora aperte (priorità)
- **A3 (alta ora)**: ripetizioni per dare varianza ad α e ai punteggi (RT5). 5 query × 3 run × 4 giudici = 60 Pro
  Search (quota 65 → al limite; oppure 3 query × 3 run = 36).
- **A4 (media)**: estendere a routing legale / multi-dominio (RT6).
- **A6 (nuova, media)**: rivalutare a 5 rater anche le 7 query NON contestabili, per stimare quante celle V1 il mio
  self-preference aveva alterato (RT9 generalizzato).
- **A7 (nuova, bassa)**: fact-key scritte da una fonte terza/neutra, non derivate da un lato (RT12).
