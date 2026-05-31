# Architettura dei test — Benchmark SearXNG-skill vs Perplexity

> Questo documento è strutturato per **progressive disclosure**: ogni livello è autosufficiente.
> Leggi solo fino alla profondità che ti serve.
> - **Livello 0** (30 secondi): cosa fa e com'è organizzato.
> - **Livello 1** (5 minuti): i tre layer dell'architettura e il flusso dei dati.
> - **Livello 2** (15 minuti): ogni componente, file per file.
> - **Livello 3** (approfondito): la base scientifica, spiegata in modo semplice.
> - **Livello 4** (riferimento): la documentazione scientifica completa.

---

## LIVELLO 0 — In una frase

Misuriamo **quanto è buona la ricerca web della skill SearXNG** confrontandola con Perplexity Pro,
usando un metodo che separa *qualità delle fonti trovate* da *qualità della risposta scritta*, con
**5 giudici AI indipendenti** e **codice statistico testato**. Tutto è riproducibile e ogni numero
è ancorato a un paper scientifico o a un test automatico.

```
DATI GREZZI  →  VALUTAZIONE 2 LAYER  →  GIUDIZIO MULTI-MODELLO  →  RED TEAMING  →  REPORT
(cosa cerca   (fonti vs risposta,     (5 AI di vendor diversi,    (auto-critica   (V1→V2→V3)
 ogni sistema) metriche oggettive)     accordo misurato)           dei difetti)
```

---

## LIVELLO 1 — I tre layer dell'architettura

L'architettura segue una regola della letteratura RAG (Es et al. 2023; Thakur et al. 2024):
**non mischiare la valutazione del "cosa trova" con quella del "cosa scrive"**. Da qui tre layer.

### Layer A — Raccolta dati (cosa fa ogni sistema)
Per 12 query reali, registriamo *esattamente* cosa produce ogni sistema:
- **Perplexity**: `perplexity_raw/*.json` (risposta + fonti citate, ordinate).
- **SearXNG-skill**: `searxng_raw/*.md` (header, fonti, risposta, chars ingeriti, tool call).

### Layer B — Valutazione su due piani
1. **Retrieval** (`retrieval_eval.md`, `compute_ndcg.py`): le *fonti* sono buone e ben ordinate?
   Metrica: **nDCG** su un *pool* di fonti, con etichette di rilevanza 0–3.
2. **Generazione** (`blind_pplx/`, `multijudge/`): la *risposta* è corretta, attuale, ben supportata?
   Metrica: **criteri booleani** (sì/no verificabili), giudicati da 5 AI.

### Layer C — Affidabilità del giudizio
Poiché i giudici sono AI, ne misuriamo l'accordo e i bias:
- **Krippendorff α** (`metrics.py`): quanto concordano i 5 giudici, criterio per criterio.
- **Sensitivity analysis** (`sensitivity_analysis.md`): i risultati reggono se le etichette cambiano?
- **Varianza** (A3) e **bias dei giudici** (verbosity, self-preference, outlier): `multijudge/RESULT_V3.md`.

### Sopra a tutto: Red teaming
Ogni versione del report viene **attaccata da noi stessi** per trovarne i difetti prima dell'utente
(`RED_TEAM.md` → `RED_TEAM_V2.md` → `RED_TEAM_V3.md`). I difetti trovati guidano la versione successiva.

```
                       ┌─────────────────────────────────────────────┐
   12 query reali ───► │ Layer A: raccolta (perplexity_raw, searxng_raw)
                       └───────────────┬─────────────────────────────┘
                    ┌──────────────────┴───────────────────┐
                    ▼                                       ▼
        ┌───────────────────────┐              ┌────────────────────────┐
        │ Layer B1: RETRIEVAL    │              │ Layer B2: GENERAZIONE  │
        │ nDCG su pool TREC      │              │ booleani × 5 giudici   │
        │ compute_ndcg.py        │              │ multijudge/            │
        └───────────┬───────────┘              └───────────┬────────────┘
                    └──────────────────┬───────────────────┘
                                       ▼
                       ┌───────────────────────────────────┐
                       │ Layer C: affidabilità             │
                       │ α (metrics.py, testato),          │
                       │ sensitivity, varianza, bias       │
                       └───────────────┬───────────────────┘
                                       ▼
                       ┌───────────────────────────────────┐
                       │ RED TEAMING → REPORT (V1→V2→V3)    │
                       └───────────────────────────────────┘
```

---

## LIVELLO 2 — I componenti, file per file

### Codice (logica pura e testata)
| File | Ruolo | Note |
|---|---|---|
| `metrics.py` | **Cuore statistico**: `krippendorff_alpha_nominal`, `dcg`, `ndcg`, `majority` | Logica separata dai dati; convenzioni documentate nel docstring |
| `test_compute.py` | **Test suite** (15 test): known-answer, oracolo differenziale, edge case, property | `python3 test_compute.py` → 15/15 PASS |
| `compute_ndcg.py` | Layer B1: nDCG dei due ranking sul pool | importa da `metrics.py` |
| `multijudge/compute_alpha.py` | Layer C: α dei 5 giudici per criterio | importa da `metrics.py` |
| `multijudge/build_prompts.py` / `build_prompts_A6.py` | Costruzione prompt-giudice **anonimi** (cecità) | mappa A/B da `_KEY.md` |
| `multijudge/analyze_a6.py` | A6/A3/RT10: contaminazione, varianza, outlier | importa da `metrics.py` |

### Dati grezzi (mai mescolati col codice)
| Cartella/file | Contenuto |
|---|---|
| `perplexity_raw/*.json` (12) | output Perplexity: risposta + citazioni ordinate |
| `searxng_raw/*.md` (12) | output skill: header, fonti, risposta, chars, tool call |
| `multijudge/raw/*.json` (5) | giudizi 4 modelli, query contestabili |
| `multijudge/raw_a6/*.json` (10) | giudizi 4 modelli, query non contestabili × 2 run |
| `blind_pplx/_KEY.md` | **chiave sigillata** della mappatura A/B (cecità) |

### Definizioni congelate (decise *prima* di guardare i dati)
| File | Contenuto |
|---|---|
| `test_cases_pplx.md` | le 12 query + ipotesi pre-registrate (anti-razionalizzazione) |
| `rubric.md` | la rubrica booleana congelata (eredità del benchmark precedente) |
| `references_literature.md` | la bibliografia: ogni scelta di metodo è ancorata qui |

### Risultati e auto-critica (versionati)
| File | Versione | Contenuto |
|---|---|---|
| `retrieval_eval.md`, `blind_pplx/evaluation.md` | base | layer B grezzo |
| `benchmark_pplx_vs_searxng.md`, `REPORT_COMPLETO.md` | V1 | primo report (1 giudice) |
| `multijudge/RESULT.md`, `REPORT_COMPLETO_V2.md` | V2 | multi-giudice |
| `multijudge/RESULT_V3.md`, `REPORT_COMPLETO_V3.md` | V3 | codice testato + bias caratterizzato |
| `RED_TEAM.md` → `_V2` → `_V3` | tutte | i difetti trovati a ogni giro |
| `sensitivity_analysis.md`, `token_efficiency_pplx.md` | — | robustezza ed efficienza (assi separati) |

> Nota di manutenzione: esistono due file `* copia.md` (duplicati, probabilmente creati da macOS/Finder).
> Non sono parte dell'architettura e possono essere rimossi.

### Come rieseguire tutto (riproducibilità)
```bash
cd test/
python3 test_compute.py            # 1. valida le metriche (deve dare 15/15 OK)
python3 compute_ndcg.py            # 2. layer retrieval → nDCG 0.732 = 0.732
python3 multijudge/compute_alpha.py   # 3. α per criterio
python3 multijudge/analyze_a6.py      # 4. contaminazione, varianza, outlier
# I giudizi LLM si rigenerano con pwm council (vedi build_prompts*.py); raw già salvati.
```

---

## LIVELLO 3 — La base scientifica, spiegata in modo semplice

Ogni scelta dell'architettura risponde a un problema noto in letteratura. Qui il *perché*, in parole semplici.

### 3.1 Perché separare "fonti" da "risposta" (two-layer)
**Problema**: se valuti solo la risposta finale, non sai se un errore viene da fonti scadenti o da
cattiva scrittura. **Soluzione** (RAGAS, Es et al. 2023; Thakur et al. 2024): valuta i due piani
separatamente. *Analogia*: come giudicare un tema scolastico distinguendo "ha consultato libri buoni?"
da "ha scritto bene?". Da qui Layer B1 (fonti) e B2 (risposta).

### 3.2 Perché nDCG per le fonti
**Problema**: una lista di fonti è buona non solo se contiene quelle giuste, ma se le mette *in alto*.
**Soluzione** (Järvelin & Kekäläinen 2002): **nDCG** premia le fonti rilevanti vicino alla cima e
"sconta" quelle in fondo (logaritmicamente). *Analogia*: su Google, il primo risultato conta più del
decimo. nDCG = 1.0 significa ordine perfetto.

### 3.3 Perché il "pool" e le etichette 0–3
**Problema**: non possiamo etichettare *tutte* le fonti del web. **Soluzione** (pooling TREC, Manning
et al. 2008): prendi il top-K di *entrambi* i sistemi, unisci, ed etichetta solo quelle. Le etichette
0–3 (3=ufficiale, 0=irrilevante) seguono una regola *esplicita e scritta prima*, per non barare a posteriori.

### 3.4 Perché criteri booleani (sì/no) invece di voti 1–10
**Problema**: i voti soggettivi ("dai 7 o 8?") fanno litigare i giudici. **Soluzione** (arXiv:2408.09235):
domande **booleane verificabili** ("cita una fonte ufficiale? sì/no") danno molto più accordo. *Analogia*:
"ha passato l'esame?" è più oggettivo di "che voto merita la sua simpatia?".

### 3.5 Perché 5 giudici e Krippendorff α
**Problema**: un solo giudice AI può avere pregiudizi. **Soluzione**: 5 giudici di **aziende diverse**
(Anthropic, OpenAI, Google, Moonshot, NVIDIA) → i loro errori non sono correlati. **Krippendorff's α**
misura quanto concordano: α=1.0 accordo perfetto, α=0 come il caso, α<0 peggio del caso. *Analogia*: una
giuria internazionale è più affidabile di un singolo arbitro tifoso. Scegliamo α (non altri indici) perché
gestisce ≥3 giudici, dati mancanti e categorie nominali.

### 3.6 Perché Perplexity NON è il "metro di verità" (gold standard)
**Problema**: sembrerebbe comodo dire "ha ragione Perplexity". **Soluzione/scoperta** (Liu, Zhan, Liang,
NeurIPS 2023): hanno misurato che nei motori generativi *come Perplexity* solo ~51% delle frasi è davvero
supportato dalle fonti citate. Quindi Perplexity è un **avversario da confrontare**, non un giudice di
verità. La verità la fissiamo con una *fact-key* indipendente. La nostra misura lo conferma: il criterio
"la citazione supporta la frase?" ha l'accordo più basso (α=0.323), proprio come prevede quel paper.

### 3.7 Perché ci preoccupiamo dei bias dei giudici
Tre bias noti dei giudici-AI, e come li neutralizziamo:
- **Verbosity bias** (Dubois et al. 2024): premiano le risposte *lunghe*. → **Escludiamo la lunghezza**
  dai criteri di qualità; l'efficienza-token è un asse separato.
- **Position bias** (Wang et al. 2024): preferiscono la risposta presentata per prima. → **Swap-and-average**:
  alterniamo l'ordine A/B e mediamo.
- **Self-preference** (survey LLM-as-a-Judge, 2024): un modello favorisce il proprio stile. → Usiamo giudici
  di vendor diversi *e* abbiamo misurato il bias di Claude (V3): risultava *indulgente*, ma — sorpresa —
  semmai verso Perplexity, non verso la skill. Confronto quindi conservativo per SearXNG.

### 3.8 Perché testiamo il codice con un "known-answer test"
**Problema**: una metrica statistica scritta a mano può essere sbagliata e nessuno se ne accorge.
**Soluzione** (best practice di calcolo scientifico): la confrontiamo con un caso a *risposta nota*.
**Lezione appresa (V3)**: abbiamo chiesto il valore atteso a un LLM e ce l'ha dato **sbagliato due volte**.
Da lì la regola: il valore di riferimento deve venire da *calcolo deterministico* o da una *seconda
implementazione indipendente*, mai da un LLM. Così `test_compute.py` protegge tutti gli α del report.

### 3.9 Perché il "red teaming" è parte dell'architettura
**Problema**: è facile innamorarsi dei propri risultati. **Soluzione**: a ogni versione *attacchiamo*
il nostro stesso lavoro, classificando i difetti per gravità (🔴🟡🟢) e distinguendo "fatti osservati
sui tool" (robusti) da "punteggi di giudizio" (fragili). È così che V1 è diventato V2 (multi-giudice) e
V2 è diventato V3 (codice testato). I difetti non sono nascosti: sono il motore del miglioramento.

---

## LIVELLO 4 — Documentazione scientifica (riferimento completo)

Bibliografia completa e link in **`references_literature.md`**. Sintesi per uso:

| Tema | Riferimento | Cosa ci dà |
|---|---|---|
| nDCG / ranking | Järvelin & Kekäläinen, *Cumulated Gain-based Evaluation of IR Techniques*, ACM TOIS 2002 | la metrica del Layer B1 |
| Pooling | Manning, Raghavan, Schütze, *Introduction to IR*, 2008 (cap. Evaluation) | come etichettare senza giudizi esaustivi |
| Eval RAG two-layer | Es et al., *RAGAS*, 2023 (arXiv:2309.15217); Thakur et al., *Evaluating Retrieval Quality in RAG*, 2024 | separare retrieval da generazione |
| Verifiability gen. search | Liu, Zhan, Liang, *Evaluating Verifiability in Generative Search Engines*, NeurIPS 2023 (arXiv:2304.09848) | perché Perplexity ≠ gold standard (~51% supportato) |
| Citation faithfulness | Gao, Yen, Yu, Chen, *ALCE*, 2023 (arXiv:2305.14627); Rashkin et al., *AIS*, Google 2022 (arXiv:2112.12870) | definizione di "la fonte supporta il claim" |
| Rubrica booleana | *Reference-Guided Verdict: LLMs-as-Judges*, arXiv:2408.09235 | booleani > Likert per l'accordo |
| Accordo tra giudici | Krippendorff, *Computing Krippendorff's Alpha-Reliability*, 2011 | la metrica del Layer C (α) |
| Verbosity bias | Dubois et al. (AlpacaFarm/length-controlled), 2024 | escludere la lunghezza dai criteri |
| Position bias | Wang et al., 2024 | swap-and-average |
| Self-preference | *Survey on LLM-as-a-Judge* (Li/Fu et al.), 2024 | giudici di vendor diversi |
| Valutazione fonti | CRAAP test, CSU Chico 2004 | Currency/Authority come assi distinti |
| Corroborazione fonti | Dong, Berti-Équille, Srivastava, *Truth Discovery / Source Dependence*, VLDB 2009 | corroborazione solo tra fonti indipendenti |

### Convenzioni implementative dichiarate (per evitare ambiguità)
- **Krippendorff α**: variante *nominale* (binaria). Do = (Σ off-diagonal della coincidence matrix)/n;
  De = (n² − Σ n_c²)/(n(n−1)); α = 1 − Do/De. Unità con <2 valutatori escluse. *Valore canonico di
  verifica = 0.6914* (calcolato deterministicamente, NON da LLM). Vedi `metrics.py` + `test_compute.py`.
- **nDCG@k**: DCG = Σ rel_i / log₂(i+2) (rank 0-based → +2); nDCG = DCG/IDCG; rilevanza graduata 0–3.
- **Giudizio cieco**: prompt anonimi A/B senza marker del metodo (verificato via `grep`); chiave in `_KEY.md`.
- **Isolamento giudici**: `pwm council ... --no-synthesis -s none` → i giudici valutano solo i testi forniti
  + fact-key, senza fare ricerca propria.

---

*Documento vivo. Aggiornare quando cambiano metriche (`metrics.py`), criteri (`rubric.md`) o si aggiunge
una versione di report. La regola d'oro resta: ogni numero o è ancorato a un paper, o è coperto da un test.*
