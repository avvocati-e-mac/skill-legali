---
name: gestiolex-corpus
description: >
  Use the `gestiolex_corpus` MCP server for Italian legal research when the
  assistant, including Claude Code or Codex/OpenAI environments, needs the
  exact text of an article from a major Italian code, a quick
  statutory lookup without exact citations, or jurisprudential orientation
  through massime and principles of law. Trigger this skill for lawyer-facing
  research tasks about Italian statutes, code articles, procedural provisions,
  civil liability, labor, family, enforcement, consumer law, privacy, or other
  Italian-law topics where the answer should come from the GestioLex corpus
  instead of broad web browsing. Prefer the most precise low-token path:
  `leggi_articolo` when article and code are known, `cerca_norma` for
  exploratory statutory search, and `cerca_giurisprudenza` for case-law
  orientation.
---

# GestioLex Corpus

## What this MCP is

- GestioLex Corpus is a remote MCP server developed and provided by GestioLex at `https://corpus.gestiolex.it/mcp`.
- It gives the assistant access to Italian legal research tools for code articles, statutory lookup, and jurisprudential massime.
- This repository ships only the skill instructions; it does not include or run the GestioLex Corpus MCP server.

## Runtime compatibility

- In Claude Code, Claude Desktop, or Claude for Work/Cowork, use the available MCP tools exposed by the configured `gestiolex_corpus` server.
- In Codex or OpenAI environments, use the available `gestiolex_corpus` MCP tools with the same routing rules.
- If the runtime does not expose the required MCP tools, say that GestioLex Corpus is not available in the current environment and ask whether to use another documented source or workflow.
- Do not invent equivalent tool results from memory.

## Quick routing

- Use `leggi_articolo` when the user already gives both article and code.
- Use `cerca_norma` when the user needs a statutory basis but does not know the exact citation.
- Use `cerca_giurisprudenza` when the user asks for orientamenti, precedenti, massime, principi di diritto, or case-law support.
- Treat bare patterns like `111 c.c.`, `360 c.p.c.`, `24 Cost.`, `3 codice del consumo`, or `24 Carta costituzionale` as exact article requests when the user asks to read, retrieve, or quote the text.
- Resolve longer code abbreviations before shorter ones: `c.p.p.` before `c.p.`, and `c.p.c.` before `c.p.` or `c.c.`.

## Operating rules

- Prefer one tool call first, not parallel search by default.
- Keep the first query short, technical, and low-ambiguity.
- Use `k=1` for a single precise hook, `k=3` for normal legal research, `k=5` only for panoramiche or contrastive orientation.
- Let narrow markers override broad-looking words: `solo`, `un solo`, `molto mirate`, `piu vicino`, `riferimento preciso`, and `gancio piu utile` mean `k=1`.
- If the first result set is off-topic, reformulate once with fewer words and stronger legal nouns.
- If the second attempt is still weak, say so explicitly and avoid overstating confidence.

## Query construction

- Reduce narrative prompts to `istituto + problema`.
- For smaller or less reliable models, extract the legal topic after `su`, `di`, `in materia di`, or `relativo a`, then remove procedural filler.
- Preserve article numbers only when they disambiguate the search.
- For `cerca_giurisprudenza`, avoid mixing too many facts and too many provisions in one query.
- For `cerca_norma`, prefer legal nouns over full natural-language questions.
- If the prompt says `disciplina`, `norma`, `base normativa`, or `articolo`, prefer `cerca_norma` even if it also uses a generic word like `orientamento`.
- If the query matches a high-confidence known anchor in the reference file, use `leggi_articolo` directly.

## Response style

- Answer the legal point first.
- Then cite the article or the massima source briefly.
- Flag partial relevance inline when the returned result is useful but not exact.
- Avoid long quotations unless the exact wording is the point of the request.

Read [references/query-patterns.md](references/query-patterns.md) only when you need normalization rules, examples, or red-team failure handling.
