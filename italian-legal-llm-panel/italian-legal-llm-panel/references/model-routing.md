# Model Routing

Choose three independent live judges dynamically, then run a separate supervisor/meta-judge after normalization. Do not spend live calls or upload material unless the user has chosen the online/live route or the current task explicitly authorizes it.

## Doctor First

Run:

```bash
python3 italian-legal-llm-panel/scripts/legal_panel.py doctor
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
