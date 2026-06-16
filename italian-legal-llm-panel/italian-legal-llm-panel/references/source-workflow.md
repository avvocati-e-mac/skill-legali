# Source Workflow

Source verification is separate from LLM judging. A judge can assess plausibility, but official or paid legal sources must verify existence, currency, and holdings. In reports, explain `source_verification: not_performed` as: "le citazioni non sono state controllate su fonti ufficiali".

## Route And Confidentiality Gate

Before live search or cloud upload:

1. Determine whether the material contains client facts, personal data, employee data, mailbox contents, litigation strategy, or confidential business facts.
2. If the user has not already specified the route, ask whether they want only local/offline processing or also online/live processing.
3. Disclose the intended provider/tool before any cloud/live route.
4. Do not choose local/offline or online/live silently based only on the confidentiality label.

## Verification Order

1. Italian legislation:
   - Use the local Normattiva skill from `avvocati-e-mac/skill-legali` when installed.
   - Read the article text, verify vigency, record the official URL, relevant excerpt, `vigente_al`, finding, and score impact.
   - If the Normattiva skill is missing, stop the official Normattiva check, mark the record `unavailable`, and ask the user before installing it.
2. GDPR and EU law:
   - Use EUR-Lex or another official EU source.
   - Do not use Normattiva as the authority for GDPR text or EU-law currency.
3. Case law and measures:
   - Use BuddaLaw MCP or another approved legal database first for Cassation, ordinary courts, TAR/CGT, Garante, and similar citations.
   - If BuddaLaw is unavailable, use SearXNG when installed/configured.
   - If SearXNG is unavailable, use Perplexity only when authenticated and explicitly approved.
   - If Perplexity is unavailable/expired/not approved, use base web search only as discovery and confirm against official or authorized sources.
4. Fallback:
   - If no live/official source is available, leave `source_verification` as `not_performed` and state this clearly in the report.

Use the script entrypoint for repeatable citation routing:

```bash
python3 italian-legal-llm-panel/scripts/legal_panel.py verify-sources --cases panel-input.json --output source-verification.json
```

Each record must include `citation`, `source_type`, `preferred_tool`, `tool_used`, `official_url`, `status`, `vigente_al`, `article_text_excerpt`, `finding`, and `score_impact`.

## Overrides

Apply these flags even if LLM judges score highly:

- Cited statute not found or cited in an obsolete version: set or recommend `aggiornamento = 0` and human review.
- Case-law citation not verifiable: set or recommend `assenza_allucinazioni = 0-1` and human review.
- Privacy or employment-law advice lacks proportionality, minimization, employee-monitoring, or notice analysis: flag human review.
- The answer recommends automatic forwarding of employee or role mailbox content without minimization or notice analysis: flag high GDPR/employment-law risk.

## Reporting

State whether source checks were:

- `not_performed`: no official-source or live-source check was performed; citations remain unchecked.
- `partial`: web search but no official or paid legal database confirmation.
- `verified`: official source or approved legal database confirmed core citations.

Never present an unverified citation as verified.
