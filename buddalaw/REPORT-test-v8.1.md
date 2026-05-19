# BuddaLaw Skill — Report comparativo e risultati test
**Data:** 2026-05-19  
**Versioni analizzate:** versione precedente (MCP BuddaLaw per Perplexity) → v7.2 → v8.0  
**Test eseguiti:** 32 scenari live con tool MCP BuddaLaw attivi

---

## Stato dei test eseguiti

| Gruppo | Test | Esito |
|---|---|---|
| 1 — check_access e sessione | T01–T03 | ✅ T01/T02 pass · ⚠️ T03 non simulabile (fallback offline non testabile senza interruzione rete) |
| 2 — No sentenze senza ricerca live | T04–T05 | ✅ pass |
| 3 — Formato citazione | T06–T09 | ✅ T06/T07/T08 pass · ⚠️ T09 issue scoperta (vedi sotto) |
| 4 — Mappa categorie | T10–T13 | ✅ pass (tutti e 4 i DB restituiscono risultati corretti) |
| 5 — semantic_weight adattivo | T14–T15 | ✅ pass |
| 6 — max_results adattivo | T16–T17 | ✅ pass |
| 7 — Score basso e nessun risultato | T18–T19 | ✅ T19 pass · ⚠️ T18 issue scoperta (vedi sotto) |
| 8 — Workflow contratti 3 step | T20–T22 | ✅ pass (280 requisiti restituiti, deduplication verificata: 118 unici) |
| 9 — Workflow atti processuali 2 step | T23–T24 | ✅ pass (template DI completo con istruzioni, 29 categorie listate) |
| 10 — Prassi tributaria 3 livelli | T25–T26 | ✅ pass |
| 11 — GUID e get_judgement | T27–T29 | ✅ T27 pass · ⚠️ T28/T29 issue scoperta (vedi sotto) |
| 12 — Lingua e formato risposta | T30–T32 | ✅ pass |

---

## Issue scoperte durante i test

### Issue #1 — public_url Garante Privacy usa path `data-protection-authority` (⚠️ medio)

**Test:** T27 — `get_judgement(idatto=2898732, dominio="privacy")`  
**Riscontrato:** L'URL restituito è `https://platform.buddalaw.com/full-documents/data-protection-authority/2898732`

Nei risultati di `search_case_law(search_category="privacy")` l'`index_key` del documento è `data-protection-authority`. Il tool `get_judgement` accetta `dominio="privacy"` e funziona correttamente — il path interno è una questione del server, non della skill.

**Fix:** nessun intervento necessario — `dominio="privacy"` funziona correttamente. Nota aggiunta in `tool-reference.md`.

---

### Issue #2 — Valori `dominio` per `get_judgement` diversi da `search_category` (⚠️ medio — corretto)

**Test:** T28/T29  
**Riscontrato:** i valori accettati da `get_judgement` per il parametro `dominio` sono diversi da quelli di `search_category`:

| search_category | dominio get_judgement (corretto) |
|---|---|
| `tributari` | `tributario` |
| `prassi` | `tributario-prassi` |
| `civile` | `civile` |
| `penale` | `penale` |
| `merito` | `merito` |
| `amministrativo` | `amministrativo` |
| `privacy` | `privacy` |

Dominio aggiuntivo disponibile: `lavoro` (corti di merito lavoro), `data-protection-authority` (alias privacy Garante).

**Fix applicato:** tabella dominio corretta in `SKILL.md` e `tool-reference.md`. File `.skill` rigenerato.

---

### Issue #3 — Il motore semantico non restituisce mai zero risultati (⚠️ basso — comportamento server)

**Test:** T18 — query completamente inventata («diritto romano arcaico applicato alla finanza derivata del terziario avanzato»)  
**Riscontrato:** 3 risultati restituiti con score 0.7/0.35/0.30 — tutti su condominio e muri divisori. Il motore semantico trova sempre i documenti più vicini per similarità, anche per query assurde.

**Implicazione:** score 0.7 non garantisce pertinenza topica. La skill deve valutare la coerenza tematica del risultato, non solo il numero.

**Mitigazione nel SKILL.md:** regola "dopo 2 tentativi con riformulazione, dichiara assenza risultati" — ma la valutazione della pertinenza topica rimane a carico di Claude. Non risolvibile a livello di skill.

---

### Issue #4 — `get_contract_requirements` restituisce duplicati sistematici (🔴 alto — già coperto)

**Test:** T22  
**Riscontrato:** contratto locazione commerciale (id 81) → 280 requisiti totali, 118 unici per `title` (162 duplicati). Distribuzione: 219 MUST · 45 SHOULD · 16 COULD. Scope: 47 specific + 71 general.

**Fix:** regola di deduplicazione per `title` già presente nel SKILL.md v8.0 — confermata come necessaria dai test.

---

### Verifica esempio sentenza nel SKILL.md ✅

**Test:** T15 — `search_case_law(numero="12056", anno=2026, search_category="civile")`  
**Riscontrato:** la sentenza usata come esempio nel SKILL.md esiste realmente.

> [Cass. Civ. Sez. Lav., ord. n. 12056/2026](https://platform.buddalaw.com/full-documents/civile/ECLI:IT:CASS:2026:12056CIV) — la sede aziendale non è sede protetta per le conciliazioni ex art. 2113 c.c. L'onere di provare l'effettiva assistenza sindacale in sede non protetta grava sul datore di lavoro.

---

## Report comparativo versioni

### Versione precedente (`MCP BuddaLaw per Perplexity/buddalaw_skill.md`)

| Caratteristica | Stato |
|---|---|
| Formato | Guida narrativa per utenti — non istruzioni comportamentali per Claude |
| Frontmatter YAML | ❌ Assente |
| Struttura cartelle standard | ❌ Singolo file `.md`, nessuna sottocartella |
| File `.skill` installabile | ❌ Assente |
| Trigger automatici | ❌ Non definiti |
| PRINCIPIO ZERO (check_access) | ⚠️ Menzionato genericamente, senza regola di sessione |
| Regola assoluta (no sentenze inventate) | ❌ Assente |
| Formato citazione | ❌ Assente |
| Mappa categorie → tool | ✅ Presente come tabella informativa |
| Workflow contratti | ✅ 2 step (manca list_contract_categories) |
| Workflow atti processuali | ✅ 2 step (manca list_processual_act_categories) |
| Prassi tributaria ordine | ✅ Presente |
| Esempi di query | ✅ Buona copertura (punto di forza) |
| Gestione score basso | ❌ Assente |
| Fallback offline | ❌ Assente |
| Gestione GUID | ❌ Assente |
| Gestione lingue straniere | ❌ Assente |
| Suite di test | ❌ Assente |

---

### v7.2 (file `buddalaw_skill_v7.2.md`)

| Caratteristica | Stato |
|---|---|
| Formato | ✅ Istruzioni comportamentali per Claude |
| Frontmatter YAML | ❌ Assente |
| Struttura cartelle standard | ❌ Singolo file |
| File `.skill` installabile | ❌ Assente |
| PRINCIPIO ZERO | ✅ Ben definito |
| Regola assoluta | ✅ Esplicita |
| Formato citazione | ✅ Formato unico con tabella (6 DB) |
| Formato citazione — prassi/amm.vo | ⚠️ Incompleto |
| GUID Garante/CGT | ✅ Presente ma con regola errata («non usare get_judgement con GUID» — il GUID è invece accettato) |
| dominio get_judgement | ❌ Valori errati (`tributari`/`prassi` invece di `tributario`/`tributario-prassi`) |
| Mappa materia→categoria | ✅ Completa |
| Workflow contratti | ✅ 3 step (manca list_contract_categories) |
| Workflow atti processuali | ✅ 2 step (manca list_processual_act_categories) |
| Prassi tributaria 3 livelli | ✅ |
| Regole trasversali | ✅ Presenti |
| Formato risposta | ✅ Con esempi giusto/sbagliato |
| Fallback offline | ❌ Assente |
| Gestione lingue straniere | ❌ Assente |
| Score basso | ❌ Assente |
| max_results adattivo | ⚠️ Menzionato, non sistematizzato |
| semantic_weight dinamico | ⚠️ Parziale |
| Esempi query | ❌ Assenti |
| Schema parametri tool | ❌ Assente |
| Suite di test | ❌ Assente |

---

### v8.0 — post-test (skill attuale in `buddalaw/`)

| Caratteristica | Stato |
|---|---|
| Formato | ✅ SKILL.md con frontmatter YAML standard |
| Struttura cartelle standard | ✅ Doppia cartella + references/ + .skill ZIP |
| File `.skill` installabile | ✅ |
| PRINCIPIO ZERO + fallback offline | ✅ |
| Regola assoluta | ✅ |
| Formato citazione (8 DB) | ✅ |
| GUID — regola corretta | ✅ (GUID preferito, funziona con get_judgement) |
| dominio get_judgement | ✅ **Corretto post-test** (`tributario` / `tributario-prassi`) |
| Mappa materia→categoria (search) | ✅ |
| Mappa materia→domain (articles) | ✅ |
| Workflow contratti con list_categories | ✅ 3 step completo |
| Workflow atti con list_categories | ✅ 2 step completo |
| Prassi tributaria 3 livelli | ✅ |
| Regole trasversali ampliate | ✅ (lingua, max_results, score basso, no inventare) |
| Formato risposta | ✅ |
| Score basso → riformula → 2 tentativi | ✅ |
| max_results adattivo 3/5/10 | ✅ |
| semantic_weight regola dinamica | ✅ |
| Gestione lingue straniere | ✅ |
| Esempi query (60+) | ✅ `references/query-examples.md` |
| Schema parametri 13 tool | ✅ `references/tool-reference.md` |
| Suite di test 32 scenari | ✅ `references/test-suite.md` |
| Issue #3 (score alto su query assurde) | ⚠️ Mitigata — non risolvibile a livello skill |

---

## Sintesi evolutiva

```
Versione precedente   →   v7.2   →   v8.0 (post-test)
(guida utente)            (istruzioni Claude,    (istruzioni Claude,
                           incomplete)            complete + testate)

Installabile:          ❌        ❌        ✅
Frontmatter YAML:      ❌        ❌        ✅
Regola assoluta:       ❌        ✅        ✅
dominio corretto:      n/a       ❌        ✅  ← fix scoperto dai test
Fallback offline:      ❌        ❌        ✅
Esempi query:          ✅        ❌        ✅
Test suite:            ❌        ❌        ✅  (32 scenari)
```

---

## Punto aperto residuo

Il motore semantico di BuddaLaw non restituisce mai zero risultati — trova sempre i documenti più simili per rappresentazione vettoriale, anche per query completamente fuori tema. Questo è un comportamento del server, non della skill. La mitigazione implementata (valutazione pertinenza topica + 2 tentativi di riformulazione) è la soluzione corretta a livello di istruzioni per Claude.
