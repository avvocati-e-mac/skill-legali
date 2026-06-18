---
name: concilio-llm-prompt-legale
description: Concilio di LLM per valutazione risposta legale. Confronta e valuta risposte di IA su quesiti di diritto italiano (civile, penale, tributario, amministrativo) con un concilio di giudici source-aware; caso d'uso principale = risposta base di un LLM vs versione da miglioratore di prompt sullo stesso quesito (supporta anche A/B/C e valutazione singola). MANDATORY TRIGGERS: confrontare/valutare risposte legali base-vs-migliorato o di piu' IA; estrarre risposte da DOCX/PDF/Markdown/testo; punteggio su rubrica /39; controllare citazioni, GDPR/privacy o affidabilita' della giurisprudenza; preparare giudizi e verifica fonti (Normattiva, BuddaLaw, GestioLex, SearXNG, Perplexity); produrre report legali per non tecnici.
---

# Concilio di LLM per valutazione risposta legale

Use this skill to screen and rank Italian legal AI answers across civil, criminal, administrative,
and tax law. Treat the panel as quality-control only: it never substitutes review by an Italian
lawyer, and any source used in a filing, client advice, or professional opinion must be verified by
the professional.

## Caso d'uso principale: risposta base vs prompt migliorato

Lo scopo primario è valutare **la stessa domanda legale risposta da un LLM in due versioni**: quella
generata dal prompt base e quella generata dopo un miglioratore di prompt. Usa il comando dedicato
`prompt-eval`, che assegna da solo ID neutri (A=base, B=migliorato) per evitare bias a favore della
versione "migliorata", impone lo stesso quesito e aggiunge una checklist orientata al *delta*:

```bash
python3 concilio-llm-prompt-legale/scripts/legal_panel.py prompt-eval \
  --baseline "risposta-base.md" --improved "risposta-prompt-migliorato.md" \
  --preset civile --quesito "<quesito di diritto>"
```

La skill resta generica: `compare` serve per confronto A/B/C di più IA e `single` per la valutazione
di una singola risposta. Per casi tipici usa un preset tematico: `civile`, `penale`, `tributario`,
`amministrativo`. Se il quesito non è nel documento né passato con `--quesito`, lo script avvisa
(campo `warnings`): chiedilo all'utente invece di valutare senza domanda di riferimento.

## Core Workflow

1. Extract and normalize the candidates with `scripts/legal_panel.py`.
2. Apply the route gate before any live/cloud route: if the user has not already chosen, ask whether to run only locally/offline or also online/live.
3. Choose three independent judges dynamically with `doctor`, then run a separate supervisor/meta-judge after normalization.
4. Run separate prompts per candidate and per judge; save raw outputs separately.
5. Normalize raw JSON, preserve malformed outputs, aggregate scores out of 39, prepare supervisor review, and generate `report-finale.md` with `legal_panel.py report`. Do not hand-write the final report from partial notes: the command adds candidate explanations, source links, and lawyer-facing next steps.
6. Keep `panel_ranking` separate from `legal_final_assessment`: without explicit human review, the final legal assessment remains `non_determinato`.
7. State clearly whether source verification was `not_performed`, `partial`, or `verified`, and whether `source_gate` is `passed`, `passed_with_findings`, `failed`, or `not_performed`.

## Route And Privacy Gate

Use `confidential` as a risk label, not as an automatic route decision. Default `confidential` to `true` when material includes client, employee, mailbox, personal-data, company, or litigation facts, but do not silently choose local/offline or online/live. If the user has not already specified the route, ask whether they want only local/offline processing or also online/live model calls, naming the intended providers/tools. Do not install tools, authenticate accounts, upload documents, or spend live model calls unless the user has approved that route or the current request explicitly authorizes it.

## Script

Prefer the bundled script for repeatable work. Use `--preset civile|penale|tributario|amministrativo`
to load a generic checklist for that branch of Italian law:

```bash
python3 concilio-llm-prompt-legale/scripts/legal_panel.py doctor
python3 concilio-llm-prompt-legale/scripts/legal_panel.py extract "answer.docx" --preset civile
python3 concilio-llm-prompt-legale/scripts/legal_panel.py single "answer.docx" --ground-truth checklist.md
python3 concilio-llm-prompt-legale/scripts/legal_panel.py compare "A.md" "B.md" --preset penale
python3 concilio-llm-prompt-legale/scripts/legal_panel.py prepare-live "A.md" "B.md" --preset tributario --output-dir panel-results-raw --cases-output panel-input.json
python3 concilio-llm-prompt-legale/scripts/legal_panel.py normalize-live --cases panel-input.json --raw-dir panel-results-raw --output panel-results-normalized.json
python3 concilio-llm-prompt-legale/scripts/legal_panel.py prepare-supervisor --input panel-results-normalized.json --output-dir panel-results-supervisor
python3 concilio-llm-prompt-legale/scripts/legal_panel.py verify-sources --cases panel-input.json --output source-verification.json
python3 concilio-llm-prompt-legale/scripts/verify_statutes.py --sources source-verification.json --articles-dir normattiva-articles --output statutes-verification.json   # offline di default; aggiungi --allow-network solo dopo l'OK route fonti
python3 concilio-llm-prompt-legale/scripts/caselaw_formcheck.py --sources source-verification.json --output caselaw-formcheck.json   # offline, form-check deterministico delle citazioni giurisprudenziali
python3 concilio-llm-prompt-legale/scripts/legal_panel.py report --input panel-results-normalized.json --candidate-map candidate-map.json --sources source-verification.json --sources statutes-verification.json --sources caselaw-formcheck.json --output report-finale.md
python3 concilio-llm-prompt-legale/scripts/legal_panel.py mock
```

`verify_statutes.py` è un wrapper deterministico su `normattiva_fetch.py`: **offline di default** (legge solo HTML in cache), esegue il fetch live a Normattiva solo con `--allow-network` dopo l'approvazione della route fonti. `caselaw_formcheck.py` valida **solo la forma** delle citazioni giurisprudenziali (corte/sezione/numero/anno) e scarta placeholder/anni futuri/incoerenze: forma valida ≠ esistenza ≠ massima, non emette mai `verified`. Le citazioni plausibili restano da verificare con BuddaLaw/MCP o controllo umano. Per le allucinazioni di fonte il driver è deterministico (questi due script), il giudizio LLM è subordinato: vedi `references/rubric.md` e `ARCHITETTURA.md`.

The script is local/offline unless you run the prompts with external CLIs yourself. It validates extraction, scoring, prompt preparation, aggregation, malformed raw preservation, and report generation.

For randomizzato A/B/C runs, pass `--candidate-map` only at the report stage, after live judging is complete. The report must be understandable to an Italian lawyer who is not familiar with LLM evaluation: start from the practical outcome, explain what remains unverified, and render source URLs as Markdown links instead of plain text.

`verify-sources` only classifies/routs citations. `normattiva_fetch.py` performs the official
Normattiva web fetch for Italian statutes and stores HTML/TXT article files. Run it only after the
user has approved the source-verification route. It verifies existence/text/vigency signals, not
whether the statute legally supports the candidate's argument.

`doctor` also checks whether `normattiva`, `buddalaw`, `gestiolex`, and `searxng` skills/MCP routes are present. If `normattiva` is missing, ask the user before installing it from `avvocati-e-mac/skill-legali` with path `normattiva/normattiva`. Do not silently configure BuddaLaw, GestioLex Corpus, SearXNG, Perplexity, or any paid/cloud route.

## Reference Routing

- Read `references/rubric.md` before judging or editing scoring.
- Read `references/model-routing.md` before choosing Claude, Codex, Perplexity, NotebookLM, or `pwm council`.
- Read `references/live-judging.md` before preparing or running live judge calls.
- Read `references/reporting.md` before writing user-facing reports.
- Read `references/source-workflow.md` before verifying citations: `verify-sources` routes citations, `normattiva_fetch.py` fetches Italian statutes from Normattiva when approved, and case-law/provvedimenti go to BuddaLaw/GestioLex or the documented fallback. For broad live searches, delegate to a subagent so the main thread receives only verdict records.
- Read `references/case-schema.md` when producing or consuming case/result JSON.

## Live Judges

Default: three independent judges + a separate stronger supervisor. Anonymize candidates with neutral IDs (A/B/C) so no judge is biased toward a "base" or "improved" label. See `references/model-routing.md` and `references/live-judging.md` for the exact routes, fallbacks, and supervisor flow before running any live call.

## Efficienza dei token

- **Non ri-estrarre le citazioni a mano**: usa l'output deterministico di `detect_source_citations`/`verify-sources`. Rileggere il testo per estrarre le citazioni spreca contesto e introduce errori.
- **Progressive disclosure**: leggi ogni file di `references/` solo quando arrivi alla fase relativa (rubric prima del giudizio, source-workflow prima della verifica fonti, ecc.), non tutti in anticipo.
- Flag sperimentali **off-default** per ridurre i token (l'utente decide se attivarli, misura l'effetto col profiler in `test/profile_skill.py`): `prepare-live --compact-prompts` (prompt giudice compatto), `--compress-answer` (compressione estrattiva della risposta), `--judges 2` (due giudici invece di tre per lo screening), `--verdict-cache DIR` (evita di rigiudicare testo identico); `prepare-supervisor --skip-if-agreement 5` (salta il supervisore se i giudici concordano). Modelli più leggeri per lo screening: vedi `references/model-routing.md`.

## Runtime: Codex e sandbox

Se stai operando in **Codex / ambiente OpenAI**:

- **Comandi nel sandbox** (sicuri, deterministici, offline): `doctor`, `extract`, `single`, `compare`, `prompt-eval`, `verify-sources` (senza `--allow-cloud/--allow-web`), `prepare-live`, `normalize-live`, `prepare-supervisor`, `report`, `mock`, `caselaw_formcheck.py`, `verify_statutes.py` **senza** `--allow-network`, e l'harness in `test/`.
- **Comandi FUORI dal sandbox** (login/rete: nel sandbox falliscono — login Perplexity/Claude non riusciti, ecc.): tutte le chiamate live ai giudici (`pwm`, `codex exec`, `claude`), BuddaLaw/GestioLex MCP, e `verify_statutes.py --allow-network` (fetch Normattiva). Eseguili fuori dal sandbox.
- **Autorizzazione unica a monte**: prima di partire, NON lanciare comandi live e poi chiedere a metà. Enumera in un solo passaggio TUTTO il necessario — route (locale/offline vs online/live), provider/tool coinvolti, login richiesti, esecuzione fuori sandbox — e chiedi l'approvazione una volta sola. Autorizza esattamente ciò che serve, senza estendere il consenso oltre.
- **BuddaLaw via Claude**: se in Codex usi Claude per accedere a BuddaLaw e la skill `buddalaw` è presente (repo/ambiente), **caricala prima** di interrogare BuddaLaw, così Claude ha le istruzioni corrette della banca dati.

Se stai operando in **Claude Desktop / Claude for Work / Claude Code**: usa i tool, i subagenti e i fallback dell'ambiente Claude; per ricerche live ampie delega a un subagente così il thread principale riceve solo i record-verdetto.
