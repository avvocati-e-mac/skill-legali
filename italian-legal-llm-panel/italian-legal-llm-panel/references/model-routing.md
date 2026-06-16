# Model Routing

Choose the best available judges dynamically. Do not spend live calls or upload confidential material unless the user has approved that route or the current task explicitly authorizes it.

## Doctor First

Run:

```bash
python3 italian-legal-llm-panel/scripts/legal_panel.py doctor
```

Use its `routing.selected_primary_judges` and `routing.fallback_order`. Treat model names as route targets, not proof that the account can use them; the first live call still confirms authentication, subscription, and quota.

## Priority Order

Use at least two independent top judges when available:

1. Claude Opus recent route, currently `claude-opus-4-8`.
2. Codex GPT-5.5 or GPT-5.x with `high` or `xhigh` reasoning, currently `gpt-5.5` with `xhigh`.
3. Claude Sonnet recent route.
4. Perplexity single-model routes, in this order when the plan and quota permit: `gpt55`, `gpt54`, `gemini_pro`, `kimi_k26`.
5. NotebookLM only for approved source-grounded review of uploaded materials, not blind legal authority verification.

For the current A/B/C workflow, use:

- Primary judge 1: `claude_opus_4_8` (`claude --model claude-opus-4-8`).
- Primary judge 2: `codex_gpt_5_5_xhigh` (`codex exec -m gpt-5.5` with xhigh reasoning).
- Spare/tie-breaker: one Perplexity `pwm ask --json --source none` call per candidate only when needed.

## Perplexity Policy

Use Perplexity only after confirming:

- `pwm` is installed.
- Login is valid.
- Subscription is Pro or Max.
- Quota is adequate.
- The user approves the live calls if approval is not already explicit.

Do not use `pwm council` as the default. It is allowed only when two better judges are unavailable and the user explicitly approves that council route. Prefer separate `pwm ask --json --source none --model <model>` calls so raw output remains isolated per model and candidate.

## Fallback Triggers

Run a Perplexity spare judge only when:

- one primary judge fails or returns malformed/unusable JSON;
- the same candidate's primary judge scores diverge by more than 8 points;
- the first two ranked candidates are within 3 points after primary aggregation.

If Perplexity authentication or quota is unavailable, disclose that no Perplexity fallback was run.

## Local/Offline

Use `mock`, `extract`, `single`, `compare`, `prepare-live`, `normalize-live`, and `report` for local validation and deterministic screening. Offline scores are not legal conclusions; they catch missing topics, citation risk, stale-law traps, and aggregation regressions.
