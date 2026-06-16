# Live Judging

Use live judging only after the user has chosen the online/live route. Always keep prompts and raw outputs separate by candidate and judge.

## Prompt Preparation

Prepare prompts with:

```bash
python3 italian-legal-llm-panel/scripts/legal_panel.py prepare-live \
  "A.docx" "B.docx" "C.docx" \
  --preset cda-resignation-mailbox \
  --output-dir panel-results-raw \
  --cases-output panel-input.json
```

The command writes:

- `metadata.json`: selected judges, supervisor route, routing notes, and command hints.
- `case-<candidate>.json`: normalized extracted case.
- `<candidate>__<judge>.prompt.md`: one prompt per candidate and judge.

## Three Judges

Use these routes when available:

```bash
codex exec --skip-git-repo-check --ephemeral -m gpt-5.5 -c model_reasoning_effort=\"xhigh\" "<prompt>"
pwm ask --json --source none --model gemini_pro "<prompt>"
pwm ask --json --source none --model kimi_k26 "<prompt>"
```

For the default A/B/C workflow, reserve Claude Opus 4.8 for the supervisor/meta-judge. The three first-pass judges should be Codex GPT-5.5 xhigh, Perplexity Gemini Pro, and Perplexity Kimi K2.6 where available. Do not use Perplexity GPT-5.5 as a default first-pass judge when Codex GPT-5.5 is already present.

Save each response as:

```text
<candidate>__<judge>.raw.txt
```

If a CLI can write JSON or a final message file, saving that output as `.raw.json` or `.raw.txt` is acceptable. Do not combine multiple candidates or judges in one raw file.

## Perplexity Spare Judge

Use Perplexity as two independent first-pass judges from different model families when authenticated and approved. Use an additional Perplexity route only when a fallback trigger in `model-routing.md` fires:

```bash
pwm ask --json --source none --model nemotron "<prompt>"
```

Fallback order after the primary routes is `nemotron`, then `gpt55`, then `gpt54`. Record quota/auth notes in the report appendix, and disclose when fallback reduces model-family diversity.

## Normalization

Normalize after collecting raw files:

```bash
python3 italian-legal-llm-panel/scripts/legal_panel.py normalize-live \
  --cases panel-input.json \
  --raw-dir panel-results-raw \
  --output panel-results-normalized.json
```

Malformed outputs must remain in the raw folder and appear under `raw_errors` in the normalized JSON. Do not silently discard a failed judge.

## Supervisor

Prepare the supervisor prompt after normalization. The supervisor must be the strongest available model and must not duplicate one of the three first-pass judges; the default is Claude Opus 4.8.

```bash
python3 italian-legal-llm-panel/scripts/legal_panel.py prepare-supervisor \
  --input panel-results-normalized.json \
  --output-dir panel-results-supervisor
```

Run the generated `run-supervisor.sh` only after confirming the online/live route. Save the supervisor raw output separately; it reviews disagreement, ranking, override flags, and report notes, but does not verify sources.

Default supervisor route:

```bash
claude --model claude-opus-4-8 --effort xhigh --print --output-format text "<prompt>"
```
