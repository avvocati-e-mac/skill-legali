# Reporting

Write reports for non-specialist Italian lawyers first, with technical details moved to an appendix.
The final file (`report-finale.md`) must be generated with `legal_panel.py report` whenever normalized
JSON is available; do not hand-write a short final summary from `report-live.md` or intermediate notes.

## Required Structure

1. `Risposta breve`
   - say in plain Italian whether the report is provisional or source-gate-passed;
   - name the best candidate as panel outcome, not as a final legal conclusion;
   - state practical reliability;
   - state `legal_final_assessment: non_determinato` unless a human lawyer has explicitly reviewed and approved a final assessment;
   - state what a lawyer must verify before reuse.
2. `Cosa fare adesso`
   - give 2-4 practical next steps: which draft to inspect first, which citations to remove/verify, and when to rerun the report;
   - if source problems exist, name the problem class (`non coerente`, `non trovata`, `da verificare`) in ordinary language.
3. `Mappa candidati` when a randomization map exists
   - reveal A/B/C only after judging;
   - explain that judges worked on anonymous IDs.
4. `A colpo d'occhio`
   - table rows: correctness, currency, completeness, no hallucinations, source citation, uncertainty, total `/39`, ranking;
   - columns: candidates A, B, C, or the candidate IDs in the case file;
   - values: mean judge score per criterion and final aggregate score.
5. `Come leggere il risultato`
   - explain that `source_verification: not_performed` means the citations were not checked against official sources.
6. `Verifica fonti ufficiali`
   - keep this separate from the LLM judgment;
   - explain the order Normattiva for Italian legislation, EUR-Lex for GDPR/EU law, then BuddaLaw -> SearXNG -> Perplexity -> base web for case law and measures;
   - state `source_gate` and whether unresolved/mismatch/not_found records remain;
   - render citations and official/public URLs as Markdown links whenever a URL is present;
   - table for statutes: candidate, linked article, plain-language status, linked official source, verified content, score impact;
   - table for case law/measures: candidate, linked citation when available, plain-language status, linked tool/source, finding, score impact;
   - warn that a norm may exist and still not support the candidate's legal use.
7. Candidate notes and lawyer review flags.
8. Appendix:
   - models and routes used;
   - raw files directory;
   - malformed JSON or missing raw files;
   - Perplexity auth/quota notes and whether fallback was run;
   - se una cella giudice è andata in timeout/errore ed è stata sostituita con un fallback di famiglia diversa, indicarlo;
   - limitations.

Se la verifica fonti è stata eseguita con `normattiva_fetch.py` o dal subagente, riportare l'esito
**verificato** per citazione (`verified`/`mismatch`/`not_found`), non lo stato grezzo
`not_performed`/`unsupported` del solo wrapper di routing.

For older run artifacts that contain `candidate_summary` instead of `candidates`/`ranking`, still
produce a full final report by deriving candidates, ranking, criterion averages, and judge notes
from `candidate_summary` plus `verdicts`.

## Tone

Use plain Italian. Do not present unverified citations as true. Say "citazione non verificata" or "da controllare su fonte ufficiale/banca dati autorizzata" whenever the panel has not performed source checks.

Avoid unexplained internal labels in the main body. If a technical label is useful, keep it in
backticks and immediately explain its practical meaning. Prefer "Relazione provvisoria" to "report
tecnico" for lawyer-facing documents.

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
