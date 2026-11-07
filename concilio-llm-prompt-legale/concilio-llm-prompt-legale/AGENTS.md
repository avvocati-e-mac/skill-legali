# Concilio di LLM per valutazione risposta legale

Follow `SKILL.md` for quick operating instructions. Read `ARCHITETTURA.md` for architecture, scoring, bias controls, source verification, kappa calibration, supervisor flow, and scientific references.

Use this skill to screen and rank Italian legal AI answers across civil, criminal, administrative, and tax law. Its primary use case is comparing an LLM's baseline answer with the version produced after a prompt improver, on the same legal question. It is not legal advice and never substitutes review by an Italian lawyer. Keep LLM judging separate from official source verification.

Core CLI commands:

```bash
python3 concilio-llm-prompt-legale/scripts/legal_panel.py doctor
python3 concilio-llm-prompt-legale/scripts/legal_panel.py extract "answer.docx" --preset civile
python3 concilio-llm-prompt-legale/scripts/legal_panel.py single "answer.docx" --ground-truth ground_truth.md
python3 concilio-llm-prompt-legale/scripts/legal_panel.py prompt-eval --baseline base.md --improved migliorato.md --preset civile
python3 concilio-llm-prompt-legale/scripts/legal_panel.py compare "A.md" "B.md" "C.md" --preset civile
python3 concilio-llm-prompt-legale/scripts/legal_panel.py prepare-live "A.md" "B.md" --judge-timeout 240 --output-dir panel-results-raw --cases-output panel-input.json
python3 concilio-llm-prompt-legale/scripts/legal_panel.py normalize-live --cases panel-input.json --raw-dir panel-results-raw --output panel-results-normalized.json
python3 concilio-llm-prompt-legale/scripts/legal_panel.py prepare-supervisor --input panel-results-normalized.json --output-dir panel-results-supervisor
python3 concilio-llm-prompt-legale/scripts/legal_panel.py verify-sources --cases panel-input.json --output source-verification.json
python3 concilio-llm-prompt-legale/scripts/verify_statutes.py --sources source-verification.json --articles-dir normattiva-articles --output statutes-verification.json
python3 concilio-llm-prompt-legale/scripts/caselaw_formcheck.py --sources source-verification.json --output caselaw-formcheck.json
python3 concilio-llm-prompt-legale/scripts/normattiva_fetch.py --sources source-verification.json --output-json normattiva-verification.json --output-md normattiva-verification.md --articles-dir normattiva-articles
python3 concilio-llm-prompt-legale/scripts/legal_panel.py report --input panel-results-normalized.json --sources source-verification.json --sources statutes-verification.json --sources caselaw-formcheck.json --output panel-report.md
python3 concilio-llm-prompt-legale/scripts/legal_panel.py mock
```

Available presets: `civile`, `penale`, `tributario`, `amministrativo`. Per il caso primario (base vs prompt migliorato) usa `prompt-eval`: assegna da solo ID neutri A/B per evitare bias. In `run-live.sh` ogni giudice ha un timeout (`--judge-timeout`, default 240s); se una cella va in timeout, sostituisci solo quella con un fallback di famiglia diversa, non rifare il panel. `verify-sources` instrada le citazioni; `verify_statutes.py` (wrapper deterministico offline-di-default su `normattiva_fetch.py`, `--allow-network` per il fetch live dopo OK route fonti) verifica esistenza/vigenza delle norme; `caselaw_formcheck.py` (offline) valida solo la forma delle citazioni giurisprudenziali e non emette mai `verified`; giurisprudenza e provvedimenti restano da verificare con BuddaLaw/GestioLex o fallback documentato (vedi `references/source-workflow.md`). Per le allucinazioni di fonte il driver è deterministico (questi script), il giudizio LLM è subordinato. `panel_ranking` non è `legal_final_assessment`: senza revisione umana esplicita resta `non_determinato`. `confidential` si basa su dati personali reali, non sulle parole-tema: leggi `confidential_reason` prima di attivare il gate.

Risparmio token (flag off-default, l'utente decide e misura col profiler `test/profile_skill.py`): `prepare-live --judges 2|--compact-prompts|--compress-answer|--verdict-cache DIR`, `prepare-supervisor --skip-if-agreement N`. Non ri-estrarre citazioni a mano (usa l'output deterministico); leggi i `references/` con progressive disclosure. Test/harness in `concilio-llm-prompt-legale/test/` (fuori dalla skill): `python3 -m pytest concilio-llm-prompt-legale/test` gira offline e gratis.

Runtime Codex e sandbox: i comandi con login/rete (chiamate live ai giudici `pwm`/`codex exec`/`claude`, BuddaLaw/GestioLex MCP, `verify_statutes.py --allow-network`) vanno eseguiti FUORI dal sandbox; i comandi deterministici/offline girano nel sandbox. Chiedi una sola autorizzazione a monte che enumeri route, provider/tool, login ed esecuzione fuori sandbox, invece di lanciare e poi chiedere a metà. Se in Codex usi Claude per accedere a BuddaLaw e la skill `buddalaw` è presente, caricala prima di interrogare BuddaLaw.

Route and privacy gate: do not decide local/offline or online/live silently. If the user has not already specified the route, ask whether they want only local/offline processing or also online/live model calls, naming the intended providers/tools. Do not install tools, authenticate accounts, upload documents, run live Perplexity/NotebookLM/BuddaLaw/GestioLex/cloud-model workflows, or spend live model calls unless the user has explicitly approved that route.

Maintenance rule: `CLAUDE.md` and `AGENTS.md` must remain byte-for-byte identical. Every edit to one file requires the same edit to the other file.
