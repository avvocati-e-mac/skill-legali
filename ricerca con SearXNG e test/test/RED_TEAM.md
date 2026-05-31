# Red teaming dell'attività svolta — confronto SearXNG vs Perplexity

Autocritica avversariale del benchmark `benchmark_pplx_vs_searxng.md`. Obiettivo: trovare i punti
in cui le MIE conclusioni sono fragili, prima che lo faccia l'utente. Standard di riferimento:
[[metodologia-valutazione-cieca]] (3 giudici, Krippendorff α≥0.80, booleani verificabili, fonti corroborate).

## Difetti trovati (ordinati per gravità)

### 🔴 RT1 — Il "delta E5 +15% che supera Perplexity" era calcolato su pool diversi (INVALIDO)
Nella verifica di N04 avevo scritto: v3 0.805 → v4 0.923 (+15%, supera pplx 0.799). **Sbagliato**: lo
0.805 di partenza usava un pool ridotto, mentre il run completo (`compute_ndcg.py`) dà nDCG_sx N04 = **0.572**
perché il pool reale include molti `docs.python.org` label-3 di Perplexity che alzano l'IDCG. Ho confrontato
due numeri non commensurabili e li ho presentati come "prima/dopo".
- **Cosa resta vero**: la *direzione* è corretta — promuovere docs.python.org sopra il SEO-blog migliora il
  ranking SearXNG su N04 (il caso col gap più ampio a sfavore). E5 è giustificata.
- **Cosa NON posso affermare**: un numero preciso di miglioramento, né che "supera Perplexity". Una verifica
  pulita richiede di ricalcolare nDCG_sx con il ranking ri-ordinato **sullo stesso pool** del run completo.
- **Correzione applicata**: claim rimosso/declassato in README e report.

### 🔴 RT2 — Un solo giudice (io), non 3 + Krippendorff α (viola lo standard dell'utente)
La metodologia congelata chiede **3 giudici indipendenti** e **α≥0.80**. Qui tutti i punteggi qualità (95%=95%,
i booleani Q1–Q6) provengono da **un singolo rater = Claude**, lo stesso modello del generatore di un lato →
self-preference + bias correlato non eliminabile. Non c'è inter-rater agreement perché non c'è un secondo rater.
- **Impatto**: il "95%=95%" è single-rater, indicativo. Non ha la robustezza statistica che l'utente pretende.
- **Mitigazione parziale**: molti booleani sono verificabili sui file (lingua fonte, recency, failure onesto,
  citazione presente) → per quelli un controllo oggettivo decide. Ma "completezza/utilità" resta soggettiva.
- **Rimedio proposto**: rieseguire la valutazione con ≥2 giudici aggiuntivi (anche di famiglia diversa, es.
  un modello non-Claude via pwm) sui soli booleani contestabili, e riportare α. → vedi "Cosa manca", azione A1.

### 🟡 RT3 — Circolarità delle label di rilevanza (mitigata, non azzerata)
Le label 0–3 le ho messe io conoscendo le scelte di Perplexity → possibile bias pro-pplx nel nDCG.
- **Mitigazione fatta**: sensitivity analysis (`sensitivity_analysis.md`) — perturbando le label ±1 su 300 trial,
  delta nDCG media −0.001, sd 0.039, pareggio nel 53% dei casi. **Il pareggio è robusto al rumore casuale.**
- **Limite residuo**: non simula un errore *sistematico* (sovrastimare sempre gli ufficiali). Un secondo
  annotatore cieco resta lo standard.

### 🟡 RT4 — "Perplexity non confabula sui failure" era troppo netto
Red teaming sulle citazioni T12: Perplexity cita Marvel 2099, un repo GitHub casuale, profili Steam — **inventa
pertinenza** aggrappandosi a "2099"/"quantum", pur concludendo correttamente "non esiste". Non confabula una
*risposta*, ma non è la "robustezza piena" che avevo scritto. SearXNG ("0 risultati") è più sobrio.
- **Correzione applicata** in `blind_pplx/evaluation.md`.

### 🟡 RT5 — Potenza statistica nulla: 12 query, 0 ripetizioni
12 query, 1 esecuzione ciascuna, 1 sessione, 1 giorno. Nessuna ripetizione per misurare la varianza
(es. il ranking SearXNG può cambiare tra run; le risposte pplx pure). I numeri sono **istantanee**, non stime.
- **Impatto**: differenze <~0.05 di nDCG o ±1 query su 12 non sono distinguibili dal rumore.
- **Rimedio**: 3 ripetizioni per query con riporto di media±sd (costa ~36 Pro Search, fattibile: ne restano 96).

### 🟡 RT6 — Copertura domini incompleta vs i trigger della skill
Il set copre: general/fact, ai-generativa, informatica, cucina (IT+implicito EN), legale-it (dottrina+failure giurisprudenza).
**Non testati**: legale-it/normativa con Normattiva attiva (routing → 0 SearXNG), giurisprudenza con BuddaLaw attivo
(routing → search_case_law), query multi-dominio S11 (A/B), URL-diretto S10, cucina EN reale (S07 tonkotsu), lingue terze.
Il routing legale (il pezzo più "intelligente" della skill) **non è stato confrontato con Perplexity affatto**.
- **Impatto**: le euristiche E1–E6 toccano solo la lettura/ranking generici; il valore del routing resta non quantificato qui.

### 🟢 RT7 — Asimmetria di misura mai chiusa
Confronto "chars ingeriti da SearXNG" (contesto Claude) vs "lunghezza risposta pplx" (output). Sono cose diverse;
l'ho dichiarato in `token_efficiency_pplx.md` ma il README sintetizza come se fosse un vantaggio netto. È un
vantaggio *per uso agentico*, non in assoluto. Formulazione da tenere prudente.

### 🟢 RT8 — Q5 (citation-precision) verificata su un campione minuscolo
Ho ispezionato verifiability su ~4-5 risposte, non sistematicamente su tutte le frasi (la replica "ridotta" di
Liu et al. è molto ridotta). La conclusione "pplx non gold standard" regge perché poggia sul paper, non sul mio
campione; ma non posso vantare una misura mia di citation-precision. Onestà: è citazione di letteratura + spot-check.

## Cosa NON è un difetto (regge al red teaming)
- Il **pareggio nDCG** sopravvive alla sensitivity analysis (RT3) → conclusione "ranking equivalente" solida.
- Le **euristiche E1–E4** non dipendono dai punteggi: sono **fatti osservati direttamente** sui tool (chrome nel
  paragraphRange, PDF binari non parsati, `section` parziale>esatto). Riproducibili, non opinioni.
- Il **declassamento di Perplexity da gold standard** poggia su letteratura peer-reviewed (Liu et al. NeurIPS 2023),
  non sul mio giudizio → robusto anche con 1 giudice.

## Azioni correttive proposte (priorità)
- **A1 (alta)**: ri-valutazione con ≥2 giudici extra sui booleani contestabili + Krippendorff α. (RT2)
- **A2 (alta)**: ricalcolo pulito del delta E5 sullo stesso pool, o rimozione del numero. (RT1) — *fatto: numero rimosso.*
- **A3 (media)**: 3 ripetizioni/query con media±sd per dare varianza. (RT5)
- **A4 (media)**: estendere il set a routing legale (Normattiva/BuddaLaw), multi-dominio, URL-diretto. (RT6)
- **A5 (bassa)**: secondo annotatore cieco per le label nDCG. (RT3)
