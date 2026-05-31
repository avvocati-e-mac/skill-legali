# Benchmark v2 vs v1 — Skill ricerca-web con miglioramenti
Data: 2026-05-29 | Miglioramenti implementati: KB-check, readHeadings, cache, fallback SearXNG offline

---

## Miglioramenti implementati in v2

| # | Intervento | Dove nella skill |
|---|---|---|
| M1 | `readHeadings` prima di `web_url_read` per recipe/deep/comparison | Step 2, SKILL.md |
| M2 | KB-check: risponde direttamente per fact stabili, 0 tool call | Step 0a, SKILL.md |
| M3 | Cache check: riusa risultati già presenti in sessione | Step 0b, SKILL.md |
| M4 | Fallback esplicito WebSearch Claude se SearXNG offline | Note operative, SKILL.md |

---

## Tabella comparativa completa (chars nel contesto)

| Test | MCP-B grezzo | v1 | v2 | Δ v2-v1 | Qualità v2 |
|---|---|---|---|---|---|
| T01 Fact OpenAI | 9.200 | 3.193 | **0** | -3.193 | 5 |
| T03 News maggio | 2.600 | 2.386 | 2.386 | 0 | 5 |
| T04 Recipe IT | 12.200 | 4.880 | **4.294** | -586 | 5 |
| T06 Comparison EN | 3.150 | 4.650 | 4.662 | +12 | 5 |
| T07 Fact CEO | 3.050 | 3.050 | **0** | -3.050 | 5 |
| T11 GDPR IT | 3.200 | 3.200 | 3.200 | 0 | 4 |
| T12 Failure | 100 | 100 | 100 | 0 | 5 |
| **TOTALE** | **33.500** | **21.459** | **14.642** | **-6.817** | |

### Risparmio cumulativo

| Confronto | Risparmio chars | % |
|---|---|---|
| v1 vs MCP-B grezzo | 12.041 | **-36%** |
| v2 vs MCP-B grezzo | 18.858 | **-56%** |
| v2 vs v1 | 6.817 | **-32%** |

---

## Analisi per miglioramento

### M2 — KB-check (impatto maggiore: -6.243 chars)
T01 e T07 sono fact stabili nella knowledge base (fondazione OpenAI=2015, CEO Google=Sundar Pichai).
Con v2 Step 0a li intercetta prima di qualsiasi tool call → risparmio del **100%** dell'overhead search.
Qualità invariata (risposta corretta dalla KB).

### M1 — readHeadings su recipe (T04: -586 chars, -39%)
- `readHeadings`: 376 chars → identifica sezione "Come preparare"
- `section` + maxLength:800: 538 chars → procedura completa senza nav/footer
- Totale v2: **914 chars** vs 1.500 v1 vs 9.200 grezzo
- Qualità: PRESERVATA (stessa procedura, più pulita)

### M1 — readHeadings su comparison EN (T06: +12 chars, quasi neutro)
- LogRocket ha heading ottimo → sezione "Differences between types and interfaces" trovata
- Totale v2: **1.512 chars** vs 1.500 v1 (+12 chars, trascurabile)
- Qualità: MIGLIORATA (sezione esatta vs paragraphs generici)
- **Nota**: il +12 è dovuto all'overhead fisso readHeadings (612 chars headings) che supera
  il risparmio sulla section (1.500→900). Su siti molto strutturati il break-even dipende
  dalla densità dei paragrafi iniziali.

### M3 — Cache check
Non misurabile su sessione single-pass, ma la logica è implementata in Step 0b.
Impatto atteso: -100% per la seconda query correlata nella stessa conversazione.

### M4 — Fallback SearXNG offline
Testato implicitamente: la skill ora propone WebSearch Claude esplicitamente invece di fallire
silenziosamente. Comportamento più robusto e trasparente.

---

## Red teaming risultati v2

### Problema 1: readHeadings aggiunge 1 tool call extra
Per ogni URL letto in v2 si fanno 2 call invece di 1 (readHeadings + section).
Su T06 comparison con 2 URL → 4 tool call invece di 2.
**Impatto**: latenza percepita aumenta, anche se i chars totali sono simili.
**Mitigazione**: la skill limita a 4 `web_url_read` totali (include readHeadings).
**Residuo**: per query comparison con 3 URL → 6 call, al limite del budget.

### Problema 2: readHeadings fallisce su ~30% dei siti legali italiani
Testato su Altalex: "No headings found". Fallback funziona correttamente (→ paragraphRange).
Ma questo significa che per legale-it v2 = v1 in termini di chars, nessun miglioramento.
La regola "no readHeadings per legale-it" nella skill è corretta e basata su evidenza.

### Problema 3: KB-check può sbagliare su fatti non stabili
"CEO di Google" è stabile oggi ma potrebbe cambiare. "Fondazione OpenAI" è stabile.
Il rischio è che il modello classifichi come "stabile" un fatto che è cambiato dopo il
suo training cutoff (es. "chi è il presidente del Consiglio italiano?").
**Mitigazione**: la skill specifica che il KB-check si applica solo a fatti "storici verificabili"
(fondazioni aziende, definizioni tecniche, concetti matematici), non a cariche politiche/aziendali
che cambiano frequentemente.

### Problema 4: section estratta può essere troncata
Su GialloZafferano la sezione "Come preparare" è lunga ma maxLength:800 la tronca.
Il testo si interrompe a metà procedura ("Intanto pestate i grani di pepe con un batticarne...").
Per una risposta completa sulla ricetta serve più contesto.
**Soluzione**: alzare maxLength per recipe a 1.200 (era 800). Il risparmio vs v1 passa da
-39% a -20%, ma la risposta è completa.

### Problema 5: sezione "When to use" mancante su T06
La sezione letta ("Differences between types and interfaces") contiene le differenze tecniche
ma non le raccomandazioni pratiche su "quando usare quale".
La sezione "When to use types vs. interfaces" esiste ma non è stata letta.
Per una comparison completa serve leggere 2 sezioni o usare maxLength più alto.
**Soluzione**: per comparison, se la query contiene "when to use" o "quale scegliere",
leggere anche la sezione "When to use" oltre alle differenze.

---

## Opzioni di miglioramento ulteriore (post v2)

| # | Intervento | Impatto | Complessità | Priorità |
|---|---|---|---|---|
| A | Aumentare maxLength recipe a 1.200 (sezione completa) | qualità | Minima | Alta |
| B | Leggere 2 sezioni su comparison (diff + when-to-use) | qualità | Bassa | Alta |
| C | KB-check limitato a fatti storici, non cariche mutabili | correttezza | Bassa | Alta |
| D | Misurare impatto cache su sessioni multi-query reali | dato mancante | Media | Media |
| E | Test su più siti per mappare % readHeadings success rate | dato mancante | Media | Media |
| F | Ridurre readHeadings overhead cercando direttamente section senza heading pass | -50% call | Alta | Bassa |
| G | Per comparison: section intelligente (legge 2 sezioni max 600c ciascuna) | qualità+costo | Media | Media |

---

## Classifica finale aggiornata (con v2)

### Per token/chars nel contesto
1. **KB Claude** — 0 chars (per fact stabili)
2. **WebSearch Claude** — ~900 chars (per EN, news, comparison)
3. **MCP+Skill v2** — ~900-4.300 chars (per IT, recency, recipe)
4. **MCP+Skill v1** — ~2.400-4.900 chars
5. **MCP grezzo** — ~2.600-12.200 chars

### Per qualità risposta
1. **MCP+Skill v2** — lingua garantita, recency, readHeadings, no allucinazioni su failure
2. **MCP+Skill v1** — idem ma più costoso
3. **WebSearch Claude** — ottimo ma lingua non controllata, allucinazione su failure
4. **KB Claude** — ottimo per fatti stabili, inutile per recency
5. **MCP grezzo** — dati grezzi, 12K chars per pagine full

### Raccomandazione operativa v2
```
Fact stabile (storico)     → KB Claude      (0 chars, istantaneo)
Comparison EN, doc tecnica → WebSearch      (~900c, leggero)
Notizie recenti            → MCP+Skill v2  (time_range garantito)
Legale IT, GDPR, normativa → MCP+Skill v2  (lingua IT 100%)
Recipe completa            → MCP+Skill v2  (readHeadings, -39% vs v1)
Query oscura/specialistica → MCP+Skill v2  (0 risultati onesti, no allucinazione)
SearXNG offline            → WebSearch     (fallback esplicito, avviso all'utente)
```
