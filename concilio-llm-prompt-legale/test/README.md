# Harness di test — concilio-llm-prompt-legale

Questi test **non** sono un deliverable per l'utente finale: sono lo **strumento di sviluppo** per ottimizzare la skill trattandola come un programma. Servono a far emergere, a costo zero, *cosa la skill fa davvero, se lo fa bene, e dove no* — così ogni problematica diventa un test rosso e l'ottimizzazione è iterativa, senza rieseguire l'intera pipeline live (costosa in token e tempo).

La cartella vive **fuori** dalla skill installabile (`concilio-llm-prompt-legale/test/`, non dentro `concilio-llm-prompt-legale/concilio-llm-prompt-legale/`).

## Come eseguire

```bash
cd concilio-llm-prompt-legale/test
./run_tests.sh
# oppure
python3 -m pytest -v
```

Tutto gira **offline, gratis, senza chiamare modelli**. Richiede solo `pytest` (stdlib per il resto).

## Struttura

| File | Livello | Cosa verifica |
| --- | --- | --- |
| `test_unit_core.py` | 1 — Correttezza | Funzioni deterministiche di `legal_panel.py`: scoring (range/bucket/monotonia), estrazione e classificazione citazioni, alias norme, confidenzialità (email reale/CF vs placeholder), trappole di rischio, mock trap. |
| `test_caselaw_formcheck.py` | 1 — Correttezza | `caselaw_formcheck.py`: parser forma citazioni, mappatura stati, invariante "mai `verified`", merge nel report. |
| `test_statute_verifier.py` | 1 — Correttezza | `verify_statutes.py` offline su HTML in cache: `verified` a zero rete, gate di rete rispettato. |
| `test_invariants.py` | 2 — Comportamento | Promesse della skill: `verify-sources` solo routing (mai `verified`), cite false emergono, `legal_final_assessment` resta `non_determinato`, blocco allucinazioni deterministico, `CLAUDE.md ≡ AGENTS.md`, logica `source_gate`. |
| `test_pipeline_fixtures.py` | 3 — Macchina | normalize→aggregate→report su **giudici finti** (`fixtures/fake_judges/`): JSON valido, raw malformato preservato, merge multi-`--sources`. |

## Profiler

`profile_skill.py` misura **dove la skill spende** (citazioni risolte in Python vs delegate all'LLM/MCP, dimensione prompt giudice in token-proxy, confronto monolitico-vs-segmentato). `test_profiler_budgets.py` trasforma le metriche in asserzioni di budget: una regressione di efficienza diventa un test rosso.

```bash
python3 profile_skill.py --cases fixtures/cases_smoke.json
```

La stima token è un **proxy deterministico** (caratteri/4): numeri indicativi, ottimi per confronti relativi prima/dopo un'ottimizzazione, senza dipendenze esterne.

## Tier-2 live (opzionale)

`test_e2e_live.py` è saltato di default. Si attiva con:

```bash
RUN_LIVE_E2E=1 ANTHROPIC_API_KEY=... ./run_tests.sh
```

Manda un prompt giudice a un modello reale e verifica che il verdetto rispetti lo schema. Costa token: si lancia di rado.

## Fixture

I fixture in `fixtures/` codificano comportamenti **reali** osservati (non aspettative teoriche). Se cambi il parser o lo scoring, aggiorna i fixture insieme al codice. `fixtures/normattiva_articles/` contiene solo gli HTML di partenza (il `.txt` pulito è generato a runtime in `tmp`, non versionato).
