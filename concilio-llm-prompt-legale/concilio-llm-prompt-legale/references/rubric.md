# Legal Evaluation Rubric

Use this rubric for each independent judge. Each criterion is scored from 0 to 3 and multiplied by its weight. Maximum score: 39.

| Criterion | Weight | Score 0 | Score 1 | Score 2 | Score 3 |
| --- | ---: | --- | --- | --- | --- |
| Correttezza normativa | 3 | Norma errata, inesistente, abrogata, or misapplied | Norm exists but article/paragraph is imprecise | Norm is materially correct but incomplete | Norm is exact, current, and includes the right article/paragraph |
| Aggiornamento | 2 | Relies on superseded law | Uses an older version of a relevant rule | Current enough for the question | Explicitly accounts for recent relevant amendments |
| Completezza | 2 | Misses an essential issue | Covers the main issue but omits important exceptions | Covers the main issues and common exceptions | Exhaustive for the facts, including edge cases |
| Assenza di allucinazioni | 3 | Invents norms, judgments, authorities, or facts | Minor unverifiable or imprecise references | No identifiable hallucination | No hallucination and clearly states limits/verification needs |
| Citazione fonti | 2 | No source | Generic source only | Specific article, act, or authority | Article/paragraph plus verifiable case-law or official-source coordinates |
| Segnalazione incertezza | 1 | States certainty on a disputed point | Does not mention uncertainty | Notes uncertainty or alternative views | Identifies competing views and their practical significance |

## Thresholds

- `>= 27/39`: usable for internal screening if sources are verified.
- `20-26/39`: lawyer review required before relying on it.
- `< 20/39`: high-risk answer; use only to identify issues to rework.
- Always flag human review for max judge divergence above 8 points, suspected hallucinated citations, stale-law traps, or confidential material routed through unapproved cloud systems.

## Judge Prompt Requirements

The judge must:

- Ignore markdown polish, length, and presentation unless they affect legal clarity.
- Reason criterion-by-criterion before scoring.
- Quote or summarize the answer portion that supports each score.
- Return strict JSON only.
- Include `score_ponderato`, `score_massimo: 39`, `percentuale`, `flag_revisione_umana`, and `punti_critici_per_avvocato`.

## Calibration

For a pilot set of 30-50 cases, compute inter-rater agreement:

- Use Fleiss' kappa for 3+ judges on discrete 0-3 scores.
- Use Cohen's kappa for pairwise checks.
- Treat `kappa < 0.40` as a rubric problem, not a model problem.
- Target `kappa >= 0.60` for operational screening.

## Red-Team Traps

Include traps in at least 20% of benchmark cases:

- Stale law, such as treating pre-2012 article 18 Workers' Statute rules as current without distinction.
- Invented case law, such as implausible Cassation numbers or unverifiable holdings.
- False certainty where case law is divided.
- Correct but operationally useless answers that omit sources, exceptions, or facts.
- Long but empty answers that test verbosity bias.
- Markdown-vs-prose pairs with identical legal content to detect style bias.
