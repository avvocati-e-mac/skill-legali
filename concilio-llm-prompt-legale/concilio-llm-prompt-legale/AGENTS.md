# Concilio di LLM per valutazione risposta legale

Follow `SKILL.md` for quick operating instructions. Read `ARCHITETTURA.md` for architecture, scoring, bias controls, source verification, kappa calibration, supervisor flow, and scientific references.

Use this skill to screen and rank Italian legal AI answers across civil, criminal, tax, and administrative law. Its primary use case is comparing an LLM's baseline answer with the version produced after a prompt improver, on the same legal question. It is not legal advice and never substitutes review by an Italian lawyer. Keep LLM judging separate from official source verification.

Core CLI commands:

```bash
python3 concilio-llm-prompt-legale/scripts/legal_panel.py doctor
python3 concilio-llm-prompt-legale/scripts/legal_panel.py extract "answer.docx" --preset civile
python3 concilio-llm-prompt-legale/scripts/legal_panel.py single "answer.docx" --ground-truth ground_truth.md
python3 concilio-llm-prompt-legale/scripts/legal_panel.py compare "base.md" "migliorato.md" --preset civile --candidate-id A --candidate-id B
python3 concilio-llm-prompt-legale/scripts/legal_panel.py prepare-live "A.md" "B.md" --output-dir panel-results-raw --cases-output panel-input.json
python3 concilio-llm-prompt-legale/scripts/legal_panel.py normalize-live --cases panel-input.json --raw-dir panel-results-raw --output panel-results-normalized.json
python3 concilio-llm-prompt-legale/scripts/legal_panel.py prepare-supervisor --input panel-results-normalized.json --output-dir panel-results-supervisor
python3 concilio-llm-prompt-legale/scripts/legal_panel.py verify-sources --cases panel-input.json --output source-verification.json
python3 concilio-llm-prompt-legale/scripts/legal_panel.py report panel-results-normalized.json --output panel-report.md
python3 concilio-llm-prompt-legale/scripts/legal_panel.py mock
```

Available presets: `civile`, `penale`, `tributario`, `amministrativo`. When comparing a baseline answer with a prompt-improved one, use neutral candidate IDs (A/B) so no judge is biased toward the "improved" label.

Route and privacy gate: do not decide local/offline or online/live silently. If the user has not already specified the route, ask whether they want only local/offline processing or also online/live model calls, naming the intended providers/tools. Do not install tools, authenticate accounts, upload documents, run live Perplexity/NotebookLM/BuddaLaw/GestioLex/cloud-model workflows, or spend live model calls unless the user has explicitly approved that route.

Maintenance rule: `CLAUDE.md` and `AGENTS.md` must remain byte-for-byte identical. Every edit to one file requires the same edit to the other file.
