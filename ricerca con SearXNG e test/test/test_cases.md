# Test Cases — Skill ricerca-web

Ogni scenario descrive: input utente, comportamento atteso (dominio, parametri, tool call), e criteri di pass/fail.

---

## Scenario 1 — Legale IT: normativa

**Input**: `"Cosa prevede l'art. 1341 c.c. sulle clausole vessatorie?"`

**Comportamento atteso**:
- Dominio: `legale-it/normativa`
- Intestazione: `[legale-it/normativa · deep · it · nessun filtro]`
- Se Normattiva installata: invoca skill Normattiva → 0 chiamate SearXNG
- Se Normattiva NON installata: SearXNG IT, deep read, avviso installazione Normattiva mostrato

**Tool call attesi**:
- Con Normattiva: 0 `searxng_web_search`, 0 `web_url_read`
- Senza Normattiva: 1 `searxng_web_search` (lingua `it`), 1 `web_url_read` (Brocardi o Normattiva.it)

**Pass**: risposta spiega il contenuto dell'art. 1341; nessuna fonte EN; se Normattiva installata → link URN nella risposta

---

## Scenario 2 — Legale IT: giurisprudenza

**Input**: `"Ultime sentenze della Cassazione sul licenziamento per giusta causa 2025"`

**Comportamento atteso**:
- Dominio: `legale-it/giurisprudenza`
- Intestazione: `[legale-it/giurisprudenza · news · it · time_range: year]`
- Se BuddaLaw disponibile: chiede all'utente BuddaLaw vs SearXNG
- Se BuddaLaw NON disponibile: SearXNG IT automaticamente, nessun messaggio

**Tool call attesi (se BuddaLaw scelto)**: `search_case_law` con query pertinente, 0 SearXNG
**Tool call attesi (se SearXNG scelto o BuddaLaw assente)**: 1 `searxng_web_search` (`language: it`, `time_range: year`), 1-2 `web_url_read`

**Pass**: risposta cita sentenze rilevanti; se BuddaLaw → nessuna chiamata SearXNG

---

## Scenario 3 — Legale IT: dottrina

**Input**: `"Commenti dottrinali sull'abuso di dipendenza economica nel diritto italiano"`

**Comportamento atteso**:
- Dominio: `legale-it/dottrina`
- Intestazione: `[legale-it/dottrina · deep · 5 fonti · it · nessun filtro]`
- SearXNG IT sempre (indipendente da BuddaLaw o Normattiva)

**Tool call attesi**: 1 `searxng_web_search` (`language: it`), 1-3 `web_url_read`

**Pass**: risposta da fonti IT; almeno 1 fonte di dottrina (Altalex, Diritto.it, Il Sole 24 Ore); nessuna chiamata BuddaLaw

---

## Scenario 4 — AI/IA generativa

**Input**: `"Differenze principali tra Claude 3.5 Sonnet e GPT-4o per task di reasoning"`

**Comportamento atteso**:
- Dominio: `ai-generativa`
- Tipo: `comparison`
- Intestazione: `[ai-generativa · comparison · 5 fonti · multilingual · time_range: month]`
- `time_range: month` (il campo AI evolve rapidamente, default per dominio)

**Tool call attesi**: 1 `searxng_web_search` (multilingual, `time_range: month`), 2-3 `web_url_read`

**Pass**: risposta cita blog Anthropic e/o OpenAI o benchmark recenti; fonti EN+IT; `time_range: month` applicato

---

## Scenario 5 — Informatica/docs

**Input**: `"Come usare async/await in Python 3.12, differenze rispetto a 3.10"`

**Comportamento atteso**:
- Dominio: `informatica`
- Tipo: `deep`
- Intestazione: `[informatica · deep · 5 fonti · en · nessun filtro]`
- Lingua EN (query mista ma dominio tecnico)

**Tool call attesi**: 1 `searxng_web_search` (`language: en`), 1-2 `web_url_read` con `section` su docs ufficiali Python

**Pass**: risposta con esempi di codice; fonte docs.python.org o Real Python; lingua EN prioritaria

---

## Scenario 6 — Cucina IT

**Input**: `"Ricetta originale della pasta alla gricia romana"`

**Comportamento atteso**:
- Dominio: `cucina`
- Tipo: `recipe`
- Intestazione: `[cucina · recipe · 3 fonti · it · nessun filtro]`

**Tool call attesi**: 1 `searxng_web_search` (`language: it`), 1 `web_url_read` (`paragraphRange: "1-10"`, `maxLength: 2000`)

**Pass**: risposta contiene ingredienti + procedura; fonte IT (Giallozafferano, Misya, ecc.); 1 sola lettura URL

---

## Scenario 7 — Cucina internazionale EN

**Input**: `"Best tonkotsu ramen broth recipe from scratch"`

**Comportamento atteso**:
- Dominio: `cucina` (internazionale, query in EN)
- Tipo: `recipe`
- Intestazione: `[cucina · recipe · 3 fonti · en · nessun filtro]`

**Tool call attesi**: 1 `searxng_web_search` (`language: en`), 1 `web_url_read`

**Pass**: risposta con ricetta completa; fonte EN (Serious Eats, NYT Cooking, ecc.); 0 fonti IT

---

## Scenario 8 — Failure: 0 risultati con retry

**Input**: `"xkj93qpz spaghetti quantistici alla curcuma del futuro 2099"`

**Comportamento atteso**:
- Tentativo 1: SearXNG con parametri originali → 0 risultati
- Tentativo 2: rimuovi time_range + multilingual + query semplificata → 0 risultati
- Messaggio utente: "Non ho trovato risultati per [query]. Prova a riformulare..."
- Stop — nessuna risposta inventata

**Tool call attesi**: 2 `searxng_web_search`, 0 `web_url_read`

**Pass**: nessuna risposta fabricata; messaggio di fallback chiaro; 2 tentativi eseguiti

---

## Scenario 9 — Verifica conteggio tool call (fact semplice)

**Input**: `"In che anno è stato fondato Anthropic?"`

**Comportamento atteso**:
- Dominio: `general`
- Tipo: `fact`
- Intestazione: `[general · fact · 3 fonti · multilingual · nessun filtro]`
- Risposta dagli snippet — nessuna lettura URL

**Tool call attesi**: 1 `searxng_web_search`, **0** `web_url_read`

**Pass critico**: 0 chiamate `web_url_read`; risposta corretta (2021); ≤2 tool call totali

---

# Scenari edge case (inusuali ma possibili)

Questi 8 scenari (S10–S17) coprono input atipici e fallimenti parziali del progressive
disclosure. Ognuno mappa 1:1 con un intervento della skill v3.

---

## S10 — URL incollato direttamente (intervento #1)

**Input**: `"Riassumi questo: https://www.giallozafferano.it/ricette/cacio-e-pepe.html"`

**Comportamento atteso**:
- Riconosce che l'input È un URL → **0 chiamate `searxng_web_search`**
- `web_url_read(url, readHeadings=true)` → identifica sezione → `section` + `maxLength:1200`
- Intestazione: `[url-direct · 0 search]`

**Tool call attesi**: 0 `searxng_web_search`, 1-2 `web_url_read`

**Pass**: nessuna ricerca eseguita; risposta sintetizza il contenuto dell'URL fornito

---

## S11 — Query multi-dominio (intervento #2)

**Input**: `"Implicazioni legali del GDPR nell'uso di LLM in azienda"`

**Comportamento atteso**:
- Rileva due domini paritari (legale-it + ai-generativa)
- Se l'intento primario NON è chiaro → chiede all'utente con pattern A/B
- Dopo la scelta → 1 sola ricerca sul dominio scelto

**Tool call attesi**: 0 ricerche prima della risposta dell'utente; poi 1 `searxng_web_search`

**Pass**: chiede quale ambito prioritizzare prima di cercare; NON esegue due ricerche separate
**Pass alternativo**: se l'intento primario è chiaro dal verbo, procede senza chiedere (documentando il dominio scelto nell'intestazione)

---

## S12 — Heading con sinonimo, non match esatto (intervento #3)

**Input**: `"Procedimento della carbonara di Giallozafferano"` (la pagina usa "Come si prepara", non "Preparazione")

**Comportamento atteso**:
- `readHeadings` restituisce "Come si prepara la carbonara" (non "Preparazione")
- Match **semantico**: riconosce "Come si prepara" ≈ "Procedimento" e legge quella sezione

**Tool call attesi**: 1 `searxng_web_search`, 2 `web_url_read` (headings + section)

**Pass**: la sezione letta è quella della procedura, anche se il titolo differisce dalla parola cercata; NO fallback a paragraphRange per mancato match testuale

---

## S13 — Pagina con 40+ heading (intervento #4)

**Input**: `"Spiegami la storia del diritto romano"` (top result = pagina Wikipedia lunga)

**Comportamento atteso**:
- `readHeadings` restituisce una lista molto lunga (>20 titoli)
- NON scorre tutta la lista: considera i primi 20 + filtra per keyword dell'intento
- Legge solo la/le sezione/i pertinente/i

**Tool call attesi**: 1 `searxng_web_search`, 2 `web_url_read`

**Pass**: non esplode il budget chars sulla lista heading; sezione selezionata pertinente all'intento

---

## S14 — Primo URL paywall/consent banner (intervento #5)

**Input**: `"Analisi dottrinale sull'abuso del diritto"` dove il top URL restituisce solo banner cookie/paywall

**Comportamento atteso**:
- `web_url_read` su URL#1 → <200 chars utili / solo consenso cookie
- **Passa a URL#2** dagli snippet già in mano (0 nuove `searxng_web_search`)

**Tool call attesi**: 1 `searxng_web_search`, ≤4 `web_url_read` totali (URL#1 fallito + URL#2)

**Pass**: non si ferma al primo URL inutile; prova il successivo senza nuova ricerca; resta entro 4 `web_url_read`

---

## S15 — time_range troppo stretto su topic di nicchia (intervento #6)

**Input**: `"Novità nelle ultime ore su [framework di nicchia]"` → `time_range:day` dà 0 risultati pertinenti

**Comportamento atteso**:
- Tentativo 1: `time_range:day` → irrilevante
- Tentativo 2: **allarga time_range** (day→month→year) PRIMA di toccare la query
- Solo se ancora nulla → semplifica la query

**Tool call attesi**: 2-3 `searxng_web_search` (allargamenti progressivi del time_range)

**Pass**: il primo fallback allarga il filtro temporale, NON la query; la query originale resta intatta finché possibile

---

## S16 — Cache + news: niente riuso (intervento #7)

**Input**: prima `"Ultime notizie su OpenAI"`, poi più avanti in sessione `"Aggiornamenti OpenAI di oggi"`

**Comportamento atteso**:
- La seconda query è `news` → **NON riusa la cache** della prima, anche se stesso dominio
- Esegue una ricerca nuova

**Tool call attesi**: 1 `searxng_web_search` nuova per la seconda query (no `[CACHE]`)

**Pass**: nessuna intestazione `[CACHE]` per la news; ricerca rieseguita per garantire freschezza

---

## S17 — Risultato PDF (intervento #8)

**Input**: `"Linee guida AgID sull'accessibilità dei PDF"` dove il top result è un file `.pdf`

**Comportamento atteso**:
- Riconosce che l'URL è un PDF → **salta `readHeadings`**
- Usa direttamente `paragraphRange:"1-8"` + `maxLength:1200`
- Se illeggibile → URL successivo (intervento #5)

**Tool call attesi**: 1 `searxng_web_search`, 1 `web_url_read` (no headings pass)

**Pass**: nessuna chiamata `readHeadings` sul PDF; lettura con paragraphRange; fallback a URL successivo se illeggibile

---

## Checklist verifica post-installazione

- [ ] La skill compare nella lista skills disponibili nella sessione
- [ ] L'intestazione `[dominio · tipo · N fonti · lingua · filtro]` appare in ogni risposta
- [ ] Scenario 1: 0 SearXNG se Normattiva installata
- [ ] Scenario 2: chiede BuddaLaw vs SearXNG se BuddaLaw disponibile
- [ ] Scenario 3: SearXNG IT anche con BuddaLaw disponibile
- [ ] Scenario 9: 0 `web_url_read` per query fact
- [ ] Scenario 8: 2 tentativi poi messaggio, nessuna risposta inventata

### Edge case (v3)

- [ ] S10: URL incollato → 0 `searxng_web_search`, va diretto a `web_url_read`
- [ ] S11: multi-dominio → chiede A/B (o procede sul primario se chiaro), mai 2 ricerche
- [ ] S12: heading sinonimo → match semantico, no fallback per mancato match testuale
- [ ] S13: pagina con 40+ heading → cap 20 + keyword, budget non esplode
- [ ] S14: primo URL paywall → passa a URL#2 senza nuova ricerca, ≤4 `web_url_read`
- [ ] S15: time_range stretto → allarga prima il filtro temporale, poi la query
- [ ] S16: seconda news in sessione → nessun `[CACHE]`, ricerca rieseguita
- [ ] S17: risultato PDF → niente `readHeadings`, usa paragraphRange
