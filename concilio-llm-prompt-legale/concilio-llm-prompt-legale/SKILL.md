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
5. Normalize raw JSON, preserve malformed outputs, aggregate scores out of 39, prepare supervisor review, and generate a readable Markdown report.
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
python3 concilio-llm-prompt-legale/scripts/normattiva_fetch.py --sources source-verification.json --output-json normattiva-verification.json --output-md normattiva-verification.md --articles-dir normattiva-articles
python3 concilio-llm-prompt-legale/scripts/legal_panel.py report --input panel-results-normalized.json --sources source-verification.json --sources normattiva-verification.json --output panel-results-report.md
python3 concilio-llm-prompt-legale/scripts/legal_panel.py mock
```

The script is local/offline unless you run the prompts with external CLIs yourself. It validates extraction, scoring, prompt preparation, aggregation, malformed raw preservation, and report generation.

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
