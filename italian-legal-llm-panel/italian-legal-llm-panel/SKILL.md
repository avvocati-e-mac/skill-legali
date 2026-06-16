---
name: italian-legal-llm-panel
description: Evaluate and compare Italian legal AI answers with a source-aware Panel of Judges. Use when Codex needs to extract legal answers from DOCX, PDF, Markdown, or plain text; normalize answer cases; score Italian law responses against a ground truth; compare A/B/C candidate answers; check citation, GDPR/privacy, employment-law, company-law, or case-law reliability risks; prepare Claude, Codex, Perplexity, NotebookLM, Normattiva, BuddaLaw, or SearXNG judging and source-verification workflows; or produce non-technical legal-panel reports.
---

# Italian Legal LLM Panel

Use this skill to screen and rank Italian legal AI answers. Treat the panel as quality-control only: it never substitutes review by an Italian lawyer, and any source used in a filing, client advice, or professional opinion must be verified by the professional.

## Core Workflow

1. Extract and normalize the candidates with `scripts/legal_panel.py`.
2. Apply the privacy gate before any live/cloud route.
3. Choose judges dynamically with `doctor`; prefer the best two available top models over fixed Perplexity routes.
4. Run separate prompts per candidate and per judge; save raw outputs separately.
5. Normalize raw JSON, preserve malformed outputs, aggregate scores out of 39, and generate a readable Markdown report.
6. State clearly whether source verification was `not_performed`, `partial`, or `verified`.

## Privacy Gate

Default `confidential` to `true` when material includes client, employee, mailbox, personal-data, company, or litigation facts. Do not install tools, authenticate accounts, upload documents, or spend live model calls unless the user has approved that route or the current request explicitly authorizes it.

## Script

Prefer the bundled script for repeatable work:

```bash
python3 italian-legal-llm-panel/scripts/legal_panel.py doctor
python3 italian-legal-llm-panel/scripts/legal_panel.py extract "answer.docx" --preset cda-resignation-mailbox
python3 italian-legal-llm-panel/scripts/legal_panel.py compare "A.docx" "B.docx" "C.docx" --preset cda-resignation-mailbox
python3 italian-legal-llm-panel/scripts/legal_panel.py prepare-live "A.docx" "B.docx" "C.docx" --preset cda-resignation-mailbox --output-dir panel-results-raw --cases-output panel-input.json
python3 italian-legal-llm-panel/scripts/legal_panel.py normalize-live --cases panel-input.json --raw-dir panel-results-raw --output panel-results-normalized.json
python3 italian-legal-llm-panel/scripts/legal_panel.py verify-sources --cases panel-input.json --output source-verification.json
python3 italian-legal-llm-panel/scripts/legal_panel.py report --input panel-results-normalized.json --sources source-verification.json --output panel-results-report.md
python3 italian-legal-llm-panel/scripts/legal_panel.py mock
```

The script is local/offline unless you run the prompts with external CLIs yourself. It validates extraction, scoring, prompt preparation, aggregation, malformed raw preservation, and report generation.

`doctor` also checks whether `normattiva`, `buddalaw`, and `searxng` skills/MCP routes are present. If `normattiva` is missing, ask the user before installing it from `avvocati-e-mac/skill-legali` with path `normattiva/normattiva`. Do not silently configure BuddaLaw, SearXNG, Perplexity, or any paid/cloud route.

## Reference Routing

- Read `references/rubric.md` before judging or editing scoring.
- Read `references/model-routing.md` before choosing Claude, Codex, Perplexity, NotebookLM, or `pwm council`.
- Read `references/live-judging.md` before preparing or running live judge calls.
- Read `references/reporting.md` before writing user-facing reports.
- Read `references/source-workflow.md` before verifying citations or configuring MCP tools.
- Read `references/case-schema.md` when producing or consuming case/result JSON.

## Initial A/B/C Case

For the supplied DOCX files about board resignation, possible employment-law spillover, mailbox forwarding, autoresponder handling, GDPR/privacy, and case-law reliability:

```bash
python3 italian-legal-llm-panel/scripts/legal_panel.py prepare-live \
  "research-eaa30475a1d37986- A.docx" \
  "research-617fc5f5a987e7f4 - B.docx" \
  "research-1e81aa59dead131a - C.docx" \
  --preset cda-resignation-mailbox \
  --output-dir panel-results-abc-live-bestmodels-raw \
  --cases-output panel-input-abc-live.json
```

Use Claude Opus 4.8 and Codex GPT-5.5 xhigh when available. Use Perplexity `pwm ask --json --source none` only as a single fallback or tie-breaker when a primary judge fails, judge divergence exceeds 8 points, or the top two candidates are within 3 points. Do not use `pwm council` by default; use it only when two better judges are unavailable and the user explicitly approves.
