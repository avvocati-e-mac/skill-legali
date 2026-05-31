# Report completo V3 — SearXNG-skill (v4) vs Perplexity Pro, validato e con codice testato

**Data**: 2026-05-31 · **Giudici**: 5 rater (Claude + GPT-5.4 + Gemini 3.1 Pro + Kimi K2.6 + Nemotron 3 Super)
**Budget totale sessioni**: ~75 Pro Search (quota 35 rimanente) · **Skill**: v4

> **Cosa aggiunge V3 rispetto a V2**: (1) **codice statistico testato** (known-answer test, 15/15 PASS — prima
> nessuna metrica era validata); (2) **contaminazione del giudizio Claude quantificata** (A6); (3) **varianza
> misurata** (A3, ripetizioni); (4) **Nemotron riabilitato** (RT10); (5) red teaming del codice e dei nuovi
> risultati. Fonti: `multijudge/RESULT_V3.md`, `metrics.py`, `test_compute.py`, `multijudge/analyze_a6.py`.

---

## 1. Il fix più importante: il codice ora è testato

V1/V2 calcolavano Krippendorff α con un'implementazione **hand-rolled mai validata**. Red teaming:
- Costruito known-answer test (caso canonico Wikipedia). **Trappola evitata**: Perplexity, interrogato per il
  valore atteso, ha dato due numeri **entrambi sbagliati** (0.7477, poi 0.9231); il vero è **0.6914** (calcolo
  deterministico). → **Un LLM non è ground-truth per test numerici.**
- Ancorato il test a: aritmetica esplicita + **seconda implementazione indipendente** (oracolo differenziale) + casi degeneri.
- **`test_compute.py`: 15/15 PASS.** La mia α era già corretta → **i valori α di V2 sono confermati**.
- Refactoring best-practice: `metrics.py` condiviso e validato, dati separati dalla logica, convenzioni documentate,
  nDCG e α non più duplicati. `compute_ndcg.py` ancora 0.732=0.732, `compute_alpha.py` α invariati.

## 2. Risultati consolidati

### 2.1 Ranking fonti (retrieval) — nDCG 0.732 = 0.732
Invariato, ora con `ndcg` testato. Robusto a sensitivity ±1 (delta −0.001). SearXNG vince cucina/news IT;
Perplexity informatica (docs ufficiali) → euristica E5.

### 2.2 Qualità (generazione) — 5 rater + α testato
α per criterio: lingua/recency **1.0** (oggettivi), Q1 0.564, Q3 0.562, **Q5 citation-precision 0.323** (basso →
criterio intrinsecamente difficile, conferma Liu et al.). Stabilità tra run: **97%** (solo 3/102 flip).

### 2.3 Il bias di Claude V1: misurato e RIBALTATO
- **Contaminazione 11%** (3/26 celle facili, stabile su 2 run): Claude V1 era **più indulgente** di una giuria di 4 modelli.
- **NON è self-preference**: delle ~4 celle contaminate (A6+V2), **~3 favoriscono Perplexity, 1 SearXNG**. Claude
  tende a dare credito alle risposte lunghe/ben scritte (stile Perplexity), **non a sé/SearXNG**.
- **Conseguenza**: il confronto V1/V2 era *conservativo per SearXNG*, non gonfiato a suo favore. La conclusione
  "pari" resta valida e, se sbilanciata, lo era **contro** SearXNG.

### 2.4 Nemotron riabilitato (RT10 chiuso)
Su set ampio (5 query × 2 run) Nemotron ha **0% voti di minoranza** — il più consensuale, non un outlier.
L'idiosincrasia vista in V2 era artefatto del campione piccolo. Nessun giudice è sistematicamente rumoroso.

## 3. Skill v4 — euristiche invariate, una rafforzata
E1–E6 (vedi `references/search_strategy.md`). La rivalutazione conferma **E3** (fonte ufficiale non letta penalizzata
dai giudici, N01/T01) e **E5/E6** (docs ufficiali contano: T01-B SearXNG bocciato da 4/4 per non aver citato openai.com).

## 4. Stato red teaming completo
| ID | Difetto | Stato V3 |
|---|---|---|
| RT1 | delta E5 su pool diversi | corretto |
| RT2 | 1 solo giudice | ✅ chiuso (5 rater) |
| RT3 | circolarità label nDCG | mitigato (sensitivity) |
| RT4 | "pplx non confabula" netto | corretto |
| RT5 | varianza non misurata | ✅ **chiuso** (A3: 3% instabilità, giudizi riproducibili) |
| RT6 | routing legale non testato | aperto (fuori scope) |
| RT9 | self-preference di Claude | ✅ **ribaltato** — è leniency, semmai pro-Perplexity, non pro-SearXNG |
| RT10 | Nemotron outlier | ✅ **chiuso** — artefatto campione, Nemotron è il più consensuale |
| **RT-CODE (nuovo)** | **α non validata** | ✅ **chiuso** — known-answer test 15/15, metrics.py condiviso |
| **RT-V3-LLM-truth (nuovo)** | **ground-truth da LLM inaffidabile** | documentato (Perplexity sbagliò il valore α 2 volte) |

## 5. Verdetto finale (V3)
- **La skill SearXNG v4 è competitiva con Perplexity Pro** su ranking (nDCG pari, testato) e qualità (pari con
  difetti speculari). Il confronto è ora **difendibile**: 5 giudici di famiglie diverse, codice testato, varianza
  misurata, bias del giudice caratterizzato e risultato **conservativo per SearXNG** (Claude semmai favoriva Perplexity).
- **Perplexity NON è gold standard** — tripla evidenza: letteratura (Liu et al.), Q5 α=0.323, e risposta datata su N03.
- **Onestà sui limiti residui**: campione query piccolo (potenza statistica limitata, RT6 routing non testato); il
  verbosity bias dei giudici è plausibile ma **non isolato** (lungo correla con corretto su questo set); i 5 giudici
  restano LLM (possibili bias comuni non osservabili, ma decorrelati tra 5 vendor).
- **Qualità del lavoro**: i numeri ora poggiano su codice con test suite, non su implementazioni ad-hoc. Questo è il
  miglioramento di maggior valore di V3 — senza, tutti gli α erano a rischio.
