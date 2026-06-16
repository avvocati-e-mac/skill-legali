# Reporting

Write reports for non-specialist readers first, with technical details moved to an appendix.

## Required Structure

1. `Risposta breve`
   - name the best candidate;
   - state practical reliability;
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

Se la verifica fonti è stata eseguita (dal subagente), riportare l'esito **verificato** per citazione
(`verified`/`mismatch`/`not_found`), non lo stato grezzo `not_performed` del solo wrapper di routing.

## Tone

Use plain Italian. Do not present unverified citations as true. Say "citazione non verificata" or "da controllare su fonte ufficiale/banca dati autorizzata" whenever the panel has not performed source checks.

## Reliability Labels

- `>= 27/39` with verified sources: usable for drafting under lawyer review.
- `>= 27/39` with `source_verification: not_performed`: useful internal draft, but sources and current law must be checked.
- `20-26/39`: screening signal only; substantive lawyer revision required.
- `< 20/39`: high-risk answer; use only to identify issues to rewrite.

Always flag human review when sources are not verified, candidate scores diverge by more than 8 points, suspected hallucinated citations appear, or confidential material was sent through a cloud route.
