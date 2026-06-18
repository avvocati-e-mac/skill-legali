# Legal Evaluation Rubric

Use this rubric for each independent judge. Each criterion is scored from 0 to 3 and multiplied by its weight. Maximum score: 39.

| Criterion | Weight | Score 0 | Score 1 | Score 2 | Score 3 |
| --- | ---: | --- | --- | --- | --- |
| Correttezza normativa | 3 | Norma errata, inesistente, abrogata, or misapplied | Norm exists but article/paragraph is imprecise | Norm is materially correct but incomplete | Norm is exact, current, and includes the right article/paragraph |
| Aggiornamento | 2 | Relies on superseded law | Uses an older version of a relevant rule | Current enough for the question | Explicitly accounts for recent relevant amendments |
| Completezza | 2 | Misses an essential issue | Covers the main issue but omits important exceptions | Covers the main issues and common exceptions | Exhaustive for the facts, including edge cases |
| Assenza di allucinazioni | 3 | Invents norms, judgments, authorities, or facts | Minor unverifiable or imprecise references | No identifiable hallucination | No hallucination and clearly states limits/verification needs |

### Assenza di allucinazioni: driver deterministico, LLM subordinato

Far decidere a un giudice LLM se una fonte è inventata è in tensione logica: l'esistenza/vigenza di una norma o sentenza è una proprietà del mondo, verificabile contro una banca dati, non una stima di plausibilità testuale (lo stesso meccanismo che genera l'allucinazione). Questo criterio si scinde in due segnali:

- **Driver deterministico (prevale)** — esistenza/vigenza della fonte verificata da `verify_statutes`/`normattiva_fetch` (norme) e `caselaw_formcheck` + banca dati/MCP (giurisprudenza). Una citazione `not_found`/`mismatch` deterministica abbassa l'affidabilità a prescindere dal punteggio LLM. È ciò che il report rende esplicito nel blocco "Allucinazioni: controllo deterministico".
- **Segnale LLM subordinato** — fedeltà semantica fonte↔affermazione (la fonte esiste ma è applicata male) e fatti privi di citazione. Qui il giudice segnala, non decide, e resta sempre la revisione umana.

Limiti (red team): copre solo allucinazioni ancorabili a una fonte; la coverage delle banche dati giurisprudenziali italiane è incompleta, quindi una citazione assente in banca dati va trattata come "da verificare", non come "inventata"; nessun controllo deterministico va presentato come soluzione completa (cfr. Stanford DHO, nessun RAG legale è "hallucination-free"). Fonti: CiteCheck (arXiv:2605.27700), Stanford DHO Legal RAG Hallucinations — vedi `ARCHITETTURA.md`.
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
