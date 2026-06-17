# Reporting

Write reports for non-specialist readers first, with technical details moved to an appendix.

## Required Structure

1. `Risposta breve`
   - state whether this is a technical provisional report or a report with source gate passed;
   - name the best candidate as `panel_ranking`, not as a final legal conclusion;
   - state practical reliability;
   - state `legal_final_assessment: non_determinato` unless a human lawyer has explicitly reviewed and approved a final assessment;
   - state what a lawyer must verify before reuse.
2. `A colpo d'occhio`
   - table rows: correctness, currency, completeness, no hallucinations, source citation, uncertainty, total `/39`, ranking;
   - columns: candidates A, B, C, or the candidate IDs in the case file;
   - values: mean judge score per criterion and final aggregate score.
3. `Come leggere il risultato`
   - explain that `source_verification: not_performed` means the citations were not checked against official sources.
4. `Verifica fonti ufficiali`
   - keep this separate from the LLM judgment;
   - explain the order Normattiva for Italian legislation, EUR-Lex for GDPR/EU law, then BuddaLaw -> SearXNG -> Perplexity -> base web for case law and measures;
   - state `source_gate` and whether unresolved/mismatch/not_found records remain;
   - table for statutes: article, official source, verified content, vigency, score impact;
   - table for case law/measures: citation, tool used, status, finding, score impact;
   - warn that a norm may exist and still not support the candidate's legal use.
5. Candidate notes and lawyer review flags.
6. Appendix:
   - models and routes used;
   - raw files directory;
   - malformed JSON or missing raw files;
   - Perplexity auth/quota notes and whether fallback was run;
   - se una cella giudice è andata in timeout/errore ed è stata sostituita con un fallback di famiglia diversa, indicarlo;
   - limitations.

Se la verifica fonti è stata eseguita con `normattiva_fetch.py` o dal subagente, riportare l'esito
**verificato** per citazione (`verified`/`mismatch`/`not_found`), non lo stato grezzo
`not_performed`/`unsupported` del solo wrapper di routing.

## Tone

Use plain Italian. Do not present unverified citations as true. Say "citazione non verificata" or "da controllare su fonte ufficiale/banca dati autorizzata" whenever the panel has not performed source checks.

## Reliability Labels

- `>= 27/39` with verified sources: usable for drafting under lawyer review.
- `>= 27/39` with `source_verification: not_performed`: useful internal draft, but sources and current law must be checked.
- `20-26/39`: screening signal only; substantive lawyer revision required.
- `< 20/39`: high-risk answer; use only to identify issues to rewrite.

Always flag human review when sources are not verified, candidate scores diverge by more than 8 points, suspected hallucinated citations appear, or confidential material was sent through a cloud route.

## Source Gate

- `passed`: all attached source records are verified and no mismatch/not_found/unresolved records remain.
- `passed_with_findings`: at least one source is verified, but unresolved or problematic records remain.
- `failed`: mismatch/not_found records exist and no verified source offsets the problem.
- `not_performed`: no official-source or approved-database check has been performed.

Generate the Markdown report even when the gate is not passed, but label it as a technical
provisional report. Do not turn `panel_ranking` into `legal_final_assessment`.
