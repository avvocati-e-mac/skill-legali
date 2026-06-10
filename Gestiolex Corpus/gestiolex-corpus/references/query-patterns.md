# Query Patterns

## Tool selection

- `leggi_articolo(codice, articolo)`
  Use for exact article retrieval.
- `cerca_norma(query, k)`
  Use for statutory exploration.
- `cerca_giurisprudenza(query, k)`
  Use for massime and orientation.

## Normalization

- Normalize common code mentions before calling `leggi_articolo`.
- Match longer abbreviations first.
- Treat `c.c.`, `codice civile`, `cc` as the same target.
- Treat `c.p.c.`, `codice di procedura civile`, `cpc` as the same target.
- Treat `c.p.`, `codice penale`, `cp` as the same target.
- Treat `c.p.p.`, `codice di procedura penale`, `cpp` as the same target.
- Preserve article suffixes like `bis`, `ter`, `quater`, `sexies`.
- Treat `111 c.c.`, `360 c.p.c.`, `24 Cost.`, `3 codice del consumo`, `24 Carta costituzionale`, and similar bare number + code patterns as article requests when the prompt asks to read, retrieve, quote, or show the text.

## Routing precedence

- Exact article beats search.
- Explicit jurisprudence words beat generic research words: `massime`, `precedenti`, `Cassazione`, `sentenze`, `orientamenti giurisprudenziali`.
- Normative words beat generic `orientamento`: `disciplina`, `norma`, `base normativa`, `articolo`, `testo`, `codice`.
- When the prompt asks for both statute and cases, do the narrowest first unless the user explicitly asks for both in the same answer.

## Low-token patterns

- Exact article:
  `leggi_articolo(codice="c.c.", articolo="2947")`
- Statutory basis:
  `cerca_norma(query="prescrizione risarcimento danno", k=3)`
- Case-law orientation:
  `cerca_giurisprudenza(query="notifica cartella pec indirizzo non registrato", k=3)`

## Known anchors

- `clausole vessatorie consumatore`, `contratto professionista consumatore`
  Prefer `leggi_articolo(codice="codice del consumo", articolo="33")`.
- `accertamento vessatorieta clausole`
  Prefer `leggi_articolo(codice="codice del consumo", articolo="34")`.
- `definizione consumatore professionista`
  Prefer `leggi_articolo(codice="codice del consumo", articolo="3")`.

Use known anchors only when the match is clear. Otherwise keep the normal search workflow.

## Choosing k

- `k=1`
  Use when the user asks for one precise anchor, one article, one strongest precedent, `solo il riferimento`, `molto mirate`, `piu vicino`, or `gancio piu utile`.
- `k=3`
  Default for ordinary lawyer research.
- `k=5`
  Use only for panoramiche, contrasts, or when the user explicitly asks for multiple bases or multiple orientations.
- Narrow markers override broad words. Example: `cerca solo il gancio piu utile` remains `k=1` even though it contains `piu`.
- If the prompt is contradictory, prefer the narrower call first; it costs less and can be followed by a broader search only if needed.

## One-step reformulation

- Narrative to technical:
  `quando si prescrive il danno da fatto illecito`
  -> `prescrizione risarcimento danno fatto illecito`
- Broad to focused:
  `domicilio digitale notificazioni`
  -> `art 16-sexies notificazioni domicilio digitale`
- Mixed facts to legal core:
  `licenziamento perché ha scritto un post offensivo`
  -> `licenziamento giusta causa social network`
- Prompt with procedural filler:
  `Per la difesa mi serve una sola massima buona su notifica cartella pec indirizzo non registrato`
  -> `notifica cartella pec indirizzo non registrato`
- Normative request with generic orientation word:
  `disciplina di clausole vessatorie consumatore mi serve l'orientamento`
  -> use `cerca_norma`, query `clausole vessatorie consumatore`

## Failure modes

- `cerca_norma` can return noisy ranking on specific prompts.
- `cerca_giurisprudenza` is useful for orientation, not guaranteed exact match on the first try.
- If an exact article is known, using search instead of `leggi_articolo` is usually wasteful.
- Smaller models may over-include narrative words; compress the query before searching.
- Smaller models may confuse `c.p.p.` with `c.p.` if they match abbreviations left to right; use longest match first.

## Red-team checks

- Do not call `leggi_articolo` unless both code and article are identifiable.
- Do not use `k=5` by habit.
- Do not stack `cerca_norma` and `cerca_giurisprudenza` unless the user clearly needs both.
- Do not invent an exact source when the returned result is only partially aligned.
