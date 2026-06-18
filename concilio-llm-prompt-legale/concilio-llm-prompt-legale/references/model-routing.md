# Model Routing

Choose three independent live judges dynamically, then run a separate supervisor/meta-judge after normalization. Do not spend live calls or upload material unless the user has chosen the online/live route or the current task explicitly authorizes it.

## Doctor First

Run:

```bash
python3 concilio-llm-prompt-legale/scripts/legal_panel.py doctor
```

Use its `routing.selected_primary_judges`, aiming for three judges. Treat model names as route targets, not proof that the account can use them; the first live call still confirms authentication, subscription, and quota. If sandboxed checks say Perplexity is unavailable but the user expects it, verify `pwm login --check` and `pwm usage` outside the sandbox after approval.

## Priority Order

Use three independent non-supervisor judges when available. Reserve the strongest available model for supervision.

1. Codex GPT-5.5 or GPT-5.x with `high` or `xhigh` reasoning, currently `gpt-5.5` with `xhigh`.
2. Perplexity single-model route `gemini_pro`.
3. Perplexity single-model route `kimi_k26`; use `nemotron` as the first diverse fallback if Kimi or Gemini fails.
4. Claude Opus recent route, currently `claude-opus-4-8`, reserved for supervisor/meta-judge.
5. Claude Sonnet recent route as fallback judge only when a judge route fails.
6. Perplexity `gpt55` only as fallback/tie-breaker when a diverse non-GPT route is unavailable; do not use it as a default primary judge together with Codex GPT-5.5.
7. NotebookLM only for approved source-grounded review of uploaded materials, not blind legal authority verification.

For the current A/B/C workflow, use:

- Judge 1: `codex_gpt_5_5_xhigh` (`codex exec -m gpt-5.5` with xhigh reasoning).
- Judge 2: `perplexity_gemini_pro` (`pwm ask --json --source none --model gemini_pro`) when authenticated and approved.
- Judge 3: `perplexity_kimi_k26` (`pwm ask --json --source none --model kimi_k26`) when authenticated and approved.
- Supervisor/meta-judge: default `claude_opus_4_8` (`claude --model claude-opus-4-8`) after `normalize-live`.

Rationale: avoid two GPT-family primary judges in the same panel. When Codex GPT-5.5 is selected, Perplexity GPT-5.5 may still be useful as fallback or tie-breaker, but the default first-pass panel must include a non-GPT route such as Gemini, Kimi, or Nemotron.

## Perplexity Policy

Use Perplexity only after confirming:

- `pwm` is installed.
- Login is valid.
- Subscription is Pro or Max.
- Quota is adequate.
- The user approves the live calls if approval is not already explicit.

Do not use `pwm council` as the default. Prefer separate `pwm ask --json --source none --model <model>` calls so raw output remains isolated per model and candidate.

## Fallback Triggers

Run an extra spare judge only when:

- one of the three judges fails or returns malformed/unusable JSON;
- the same candidate's judge scores diverge by more than 8 points;
- the first two ranked candidates are within 3 points after primary aggregation.

If Perplexity authentication or quota is unavailable, disclose that the Perplexity judge was not run and which fallback judge replaced it.

## Local/Offline

Use `mock`, `extract`, `single`, `compare`, `prepare-live`, `normalize-live`, and `report` for local validation and deterministic screening. Offline scores are not legal conclusions; they catch missing topics, citation risk, stale-law traps, and aggregation regressions.

## Risparmio token (flag sperimentali off-default)

Tutti off-default; l'utente decide e misura l'effetto col profiler (`test/profile_skill.py`):

- `prepare-live --judges 2`: due giudici di famiglia diversa invece di tre per lo screening (≈ -1/3 dei round-trip). Indebolisce la calibrazione kappa: solo screening, non set pilota.
- `prepare-live --compact-prompts`: prompt giudice compatto (rubrica per riferimento). Riduce i token di input ma va misurato il tasso di parse JSON.
- `prepare-live --compress-answer`: compressione estrattiva deterministica della risposta prima del giudizio (tiene le frasi con segnale legale). Riduce token e attenua lo style bias.
- `prepare-supervisor --skip-if-agreement 5`: salta il meta-giudice se la divergenza massima tra giudici è ≤ 5 punti; il salto è registrato per audit.
- `prepare-live --verdict-cache DIR`: registra una chiave `(sha256 risposta, giudice, model_route)` per non rigiudicare testo identico. La chiave include `model_route` così un aggiornamento del modello invalida la cache.

**Modelli leggeri per screening**: per un primo passaggio a basso rischio si possono usare giudici di classe più leggera (es. Claude Sonnet/Haiku, route Perplexity meno costose) ed escalare ai modelli forti solo su ambiguità (divergenza alta o top-2 ravvicinati). Cautela: giudici più deboli hanno più bias — vale solo per screening, mai per la valutazione definitiva.

## Sandbox e autorizzazioni (Codex)

In Codex, i comandi con login/rete (chiamate live ai giudici `pwm`/`codex exec`/`claude`, BuddaLaw/GestioLex MCP, `verify_statutes.py --allow-network`) vanno eseguiti **fuori dal sandbox**; nel sandbox falliscono (login non riusciti). I comandi deterministici/offline girano nel sandbox. Chiedi **una sola autorizzazione a monte** che enumeri route, provider/tool, login ed esecuzione fuori sandbox, invece di lanciare e poi chiedere a metà. Se usi Claude per BuddaLaw, carica prima la skill `buddalaw` se presente.
