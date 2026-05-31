# Benchmark Finale — 4 Modalità a Confronto
## Knowledge Base Claude · WebSearch Claude · MCP SearXNG grezzo · MCP + Skill ricerca-web

Data: 2026-05-29 | Dati: misurati live, non stimati

---

## Come leggere questo report

**4 modalità testate su 7 query reali:**
- **KB** = Solo knowledge base Claude (0 tool call)
- **WS** = WebSearch Claude built-in (risposta sintetizzata)
- **MCP-B** = MCP SearXNG grezzo (nessuna logica skill)
- **MCP-C** = MCP SearXNG + logica skill ricerca-web

**Qualità 1-5:** 5=corretta+fonte+aggiornata+lingua giusta · 4=corretta ma fonte parziale · 3=corretta ma generica · 2=parziale · 1=sbagliata

---

## Overhead nel contesto (chars misurati realmente)

| Componente | KB | WebSearch | MCP-B | MCP-C |
|---|---|---|---|---|
| Tool output (search) | 0 | ~550 (links JSON) | **~3.000** | **~3.000** |
| Risposta sintetizzata WS | — | ~150-900 | — | — |
| Lettura URL (fact) | — | — | 0 | 0 |
| Lettura URL (recipe/deep) | — | — | **~9.200** | **~1.500** |
| **TOTALE fact** | **0** | **~900** | **~3.200** | **~3.200** |
| **TOTALE deep/recipe** | **0** | **~900** | **~12.200** | **~4.900** |

> Il search output MCP (~3.000 chars) è **irriducibile** dalla skill: entra sempre nel contesto prima di qualsiasi elaborazione. La skill agisce solo su `web_url_read` (-84%) e parametri di ricerca (qualità risultati).

---

## Tabella comparativa completa

| Test | KB | WS | MCP-B | MCP-C |
|---|---|---|---|---|
| **T01 Fact: anno fondazione OpenAI** | | | | |
| Qualità | 5 | 5 | 5 | 5 |
| Lingua risultati | — | misto | IT | IT |
| Chars nel contesto | 0 | ~900 | ~3.200 | ~3.200 |
| Tool call | 0 | 1 | 1 | 1 |
| **Verdetto** | ✅ Migliore | ✅ OK | ❌ Overkill | ❌ Overkill |
| | | | | |
| **T03 News: annunci OpenAI maggio 2026** | | | | |
| Qualità | 1 | 5 | 3 | 5 |
| Recency risultati | n/a | buona* | 3/10 recenti | 8/10 recenti |
| Chars nel contesto | 0 | ~1.200 | ~2.600 | ~2.400 |
| Tool call | 0 | 1 | 1 | 1 |
| **Verdetto** | ❌ Non sa | ✅ Buona | ⚠️ Recency bassa | ✅ Migliore |
| | | | | |
| **T04 Recipe: cacio e pepe romana** | | | | |
| Qualità | 3 | 4 | 4 | 5 |
| Lingua fonti | — | misto EN+IT | IT 100% | IT 100% |
| Chars nel contesto | 0 | ~1.100 | ~12.200 | ~4.900 |
| Tool call | 0 | 1 | 2 | 2 |
| **Verdetto** | ⚠️ Generico | ✅ OK | ❌ 12K chars! | ✅ Migliore |
| | | | | |
| **T07 Fact: CEO Google 2026** | | | | |
| Qualità | 5 | 5 | 5 | 5 |
| Chars nel contesto | 0 | ~700 | ~3.050 | ~3.050 |
| Tool call | 0 | 1 | 1 | 1 |
| **Verdetto** | ✅ Migliore | ✅ OK | ❌ Overkill | ❌ Overkill |
| | | | | |
| **T11 Ambiguo: GDPR cookies IT** | | | | |
| Qualità | 2 | 3 | 4 | 4 |
| Lingua fonti | — | misto EN+IT | IT 100% | IT 100% |
| Chars nel contesto | 0 | ~1.000 | ~3.200 | ~3.200 |
| Tool call | 0 | 1 | 1 | 1 |
| **Verdetto** | ❌ Datato | ⚠️ Lingua mista | ✅ OK | ✅ OK |
| | | | | |
| **T06 Comparison: TS interfaces vs types** | | | | |
| Qualità | 4 | 5 | 4 | 5 |
| Lingua fonti | — | EN 100% | EN 100% | EN 100% |
| Chars nel contesto | 0 | ~1.100 | ~3.150 | ~4.650 |
| Tool call | 0 | 1 | 1 | 2 |
| **Verdetto** | ⚠️ Datato | ✅ Ottimo | ✅ OK | ✅ Migliore |
| | | | | |
| **T12 Failure: query assurda** | | | | |
| Qualità risposta | 4 | 2 | 5 | 5 |
| Comportamento | Non inventa | **Inventa** contesto | 0 risultati pulito | 0 risultati + fallback |
| Chars nel contesto | 0 | ~900 | ~100 | ~200 |
| Tool call | 0 | 1 | 1 | 2 |
| **Verdetto** | ✅ Corretto | ❌ Allucinazione | ✅ Corretto | ✅ Corretto |

*WS = WebSearch Claude usa un meccanismo interno non trasparente; probabilmente ha accesso a notizie recenti indipendentemente dal parametro time_range.

---

## Le 3 domande — risposta definitiva

### 1. Ha senso usare MCP SearXNG rispetto ai tool base?

**Dipende dal tipo di query. Non è una risposta universale.**

| Scenario | Migliore scelta | Motivazione |
|---|---|---|
| Fact stabile (fondazioni, persone, definizioni) | **KB Claude** | 0 token, risposta corretta |
| Notizie recenti, qualsiasi lingua | **WebSearch Claude** o **MCP+Skill** | WS più leggero; MCP+Skill migliore su recency IT |
| Ricette IT, legale IT, dottrina IT | **MCP+Skill** | Lingua IT garantita, WS restituisce fonti EN |
| Documentazione tecnica EN | **WebSearch Claude** | Qualità equivalente, overhead 3x inferiore |
| Query con rischio allucinazione (topic oscuro) | **MCP grezzo** o **MCP+Skill** | "0 risultati" onesto vs WS che inventa contesto |
| Privacy / no servizi esterni US | **MCP+Skill** | Istanza locale SearXNG |

### 2. La skill migliora rispetto al MCP grezzo?

**Sì, ma il guadagno è concentrato su un punto:**

L'unico risparmio token significativo è sulla **lettura URL** (`web_url_read`):
- Senza skill: pagina intera → **9.200 chars** (70% navigazione/footer/rumore)
- Con skill (`paragraphRange+maxLength:1500`): **1.500 chars** (-84%)

Il search output (~3.000 chars) è invariabile. La skill aggiunge valore attraverso:
- **Parametri corretti**: `time_range:month` → 8/10 risultati recenti vs 3/10 (T03)
- **Lingua forzata**: `language:it` → 100% fonti IT per query legali/cucina (T04, T11)
- **Skip lettura** su query fact: 0 `web_url_read` invece di potenziale lettura inutile

### 3. La skill è ulteriormente migliorabile?

**Sì. 4 interventi identificati, 2 ad alto impatto:**

| # | Intervento | Risparmio stimato | Complessità |
|---|---|---|---|
| 1 | `readHeadings` prima di `web_url_read` → trova sezione esatta | ulteriore -47% chars lettura | Bassa |
| 2 | NOT-TRIGGER esplicito per fact da KB | -3.200 chars (tutta la search) per query fact | Bassa |
| 3 | Cache query in sessione | -100% per query correlate | Media |
| 4 | Fallback su WebSearch Claude se SearXNG offline | robustezza | Bassa |

---

## Scoperta inattesa: WebSearch Claude allucinazione su failure

T12 rivela un problema importante di WebSearch Claude: su query senza risultati pertinenti
(**"zzxqpfm blorgatron quantum spaghetti 2099"**) ha restituito una risposta costruita
attorno ai termini parzialmente coincidenti trovati ("quantum spaghetti", "2099"),
presentandola come se fosse una risposta valida.

MCP SearXNG ha restituito correttamente **0 risultati** con messaggio esplicito.

**Implicazione**: per ricerche specialistiche dove la mancanza di risultati è un segnale
importante (es. giurisprudenza su un caso specifico, normativa di nicchia), MCP SearXNG
è più affidabile di WebSearch Claude.

---

## Raccomandazione operativa

```
Query fact stabile               → KB Claude (0 tool call)
Notizie recenti, doc EN          → WebSearch Claude (overhead 3x minore)
Legale IT, cucina IT, GDPR IT    → MCP + Skill (lingua garantita)
Ricerche dove "non trovato" è    → MCP + Skill (comportamento onesto)
  informazione utile
Privacy/air-gapped               → MCP + Skill (istanza locale)
```

---

## Nota metodologica

Tutti i valori di chars sono misurati contando i caratteri dell'output reale ricevuto dai tool,
non stimati. I confronti sono su sessione singola, stessa data (2026-05-29), stesso modello.
Il test è riproducibile eseguendo le stesse query con gli stessi parametri.
Script di test completo: `test_script_riproducibile.md` in questa stessa cartella.
