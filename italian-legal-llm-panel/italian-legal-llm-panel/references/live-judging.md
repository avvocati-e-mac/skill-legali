# Live Judging

Use live judging only after the privacy gate. Always keep prompts and raw outputs separate by candidate and judge.

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

- `metadata.json`: selected judges, routing notes, and command hints.
- `case-<candidate>.json`: normalized extracted case.
- `<candidate>__<judge>.prompt.md`: one prompt per candidate and judge.

## Primary Judges

Use these routes when available:

```bash
claude --model claude-opus-4-8 --effort xhigh --print --output-format text "<prompt>"
codex exec --skip-git-repo-check --ephemeral -m gpt-5.5 -c model_reasoning_effort=\"xhigh\" "<prompt>"
```

Save each response as:

```text
<candidate>__<judge>.raw.txt
```

If a CLI can write JSON or a final message file, saving that output as `.raw.json` or `.raw.txt` is acceptable. Do not combine multiple candidates or judges in one raw file.

## Perplexity Spare Judge

Use Perplexity only when a fallback trigger in `model-routing.md` fires:

```bash
pwm ask --json --source none --model gpt55 "<prompt>"
```

Downgrade in order to `gpt54`, `gemini_pro`, then `kimi_k26` if plan or quota blocks the preferred model. Record quota/auth notes in the report appendix.

## Normalization

Normalize after collecting raw files:

```bash
python3 italian-legal-llm-panel/scripts/legal_panel.py normalize-live \
  --cases panel-input.json \
  --raw-dir panel-results-raw \
  --output panel-results-normalized.json
```

Malformed outputs must remain in the raw folder and appear under `raw_errors` in the normalized JSON. Do not silently discard a failed judge.
