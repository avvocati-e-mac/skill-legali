# Script Test Riproducibile
## Come rieseguire il benchmark delle 4 modalità

Data creazione: 2026-05-29 | Versione skill: ricerca-web v1.0

---

## Prerequisiti

```
- Claude Code CLI attivo
- MCP SearXNG configurato in ~/.mcp.json con SEARXNG_URL=http://[host]:8100
- Server SearXNG online e raggiungibile
- WebSearch Claude disponibile nella sessione
```

Verifica connessione prima di iniziare:
```bash
curl -s "http://[SEARXNG_HOST]:8100/search?q=test&format=json" | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK, risultati:', len(d['results']))"
```

---

## Query fisse (NON modificare per garantire riproducibilità)

```
T01: "In che anno è stata fondata OpenAI?"
T02: "Cosa prevede l'art. 2043 c.c.?"          [legale IT normativa]
T03: "Ultimi annunci OpenAI maggio 2026"         [news con recency]
T04: "Ricetta cacio e pepe originale romana"     [cucina IT recipe]
T05: "Dottrina italiana sull'abuso del diritto contrattuale" [legale deep]
T06: "Differences between TypeScript interfaces and types 2025" [info EN comparison]
T07: "Who is the CEO of Google in 2026?"         [fact EN]
T08: "Best butter chicken recipe authentic Indian" [cucina EN]
T09: "Novità Claude AI maggio 2026"              [ai/news IT]
T10: "How to use Python dataclasses with inheritance" [info EN deep]
T11: "normativa GDPR cookies 2026"               [ambiguo legale+tech]
T12: "zzxqpfm blorgatron quantum spaghetti 2099" [failure]
```

### Query edge case (v3) — corrispondono a S10–S17 in test_cases.md

```
T13: "Riassumi questo: https://www.giallozafferano.it/ricette/cacio-e-pepe.html" [S10 url-direct]
T14: "Implicazioni legali del GDPR nell'uso di LLM in azienda" [S11 multi-dominio]
T15: "Procedimento della carbonara di Giallozafferano"        [S12 heading sinonimo]
T16: "Spiegami la storia del diritto romano"                  [S13 pagina 40+ heading]
T17: "Analisi dottrinale sull'abuso del diritto"              [S14 paywall → URL successivo]
T18: "Novità nelle ultime ore su HTMX"                        [S15 time_range stretto]
T19: "Aggiornamenti OpenAI di oggi" (2ª news in sessione)     [S16 cache+news, no riuso]
T20: "Linee guida AgID sull'accessibilità dei PDF"            [S17 risultato PDF]
```

> Nota S14/S16: questi due dipendono dallo stato live (quale URL è in paywall, cosa c'è già
> in cache). Eseguirli verificando il *comportamento* (tool call) più che il contenuto.

---

## Procedura per ogni test

### MODALITÀ A — Knowledge Base (0 tool call)
Esegui la query senza alcun tool. Registra:
- Risposta (testo breve)
- Qualità 1-5
- Note su cosa sa/non sa

### MODALITÀ B — WebSearch Claude
```
Usa il tool WebSearch con la query esatta.
Registra:
- chars_output = len(risposta_sintetizzata) + len(links_json)
- Qualità 1-5
- Lingua delle fonti (IT/EN/misto)
- Il tool ha inventato qualcosa? (sì/no)
```

### MODALITÀ C — MCP SearXNG grezzo
```python
# Parametri: NESSUNA ottimizzazione, usa solo query grezza
mcp__searxng__searxng_web_search(
    query="[QUERY ESATTA]"
    # nessun language, nessun time_range, nessun safesearch
)
# Se query richiede deep: leggi il primo URL senza limiti
mcp__searxng__web_url_read(url="[TOP URL]")  # nessun maxLength

# Misura:
chars_search = len(output_search_tool)
chars_read = len(output_read_tool) if letto else 0
```

### MODALITÀ D — MCP + Skill ricerca-web
```python
# Step 0: classifica dominio e tipo (vedi SKILL.md)
# → determina: dominio, tipo, lingua, time_range, n_risultati

# Step 1: ricerca con parametri corretti
mcp__searxng__searxng_web_search(
    query="[QUERY EVENTUALMENTE NORMALIZZATA]",
    language="it"|"en"|"all",
    time_range="month"|"year"|None,
    safesearch="1"
)

# Step 2: progressive disclosure
# - fact → STOP (0 web_url_read)
# - recipe/deep → leggi 1-3 URL con:
mcp__searxng__web_url_read(
    url="[URL SELEZIONATO]",
    paragraphRange="1-8",
    maxLength=1500
)

# Misura:
chars_search = len(output_search_tool)  # identico a C se stessa query
chars_read = len(output_read_tool) if letto else 0
delta_vs_C = chars_read_C - chars_read_D
```

---

## Scheda di registrazione per ogni test

```
═══════════════════════════════════════════════
TEST T0X — [query esatta]
Data: YYYY-MM-DD | Modello: claude-sonnet-X.X
═══════════════════════════════════════════════

MODALITÀ A (Knowledge Base):
  Risposta breve: [...]
  Qualità (1-5): [ ]
  Tool call: 0
  Note: [sa / non sa / parziale]

MODALITÀ B (WebSearch Claude):
  chars_links: [ ] (conta i caratteri del JSON links)
  chars_risposta: [ ] (conta i caratteri della risposta sintetizzata)
  chars_totale: [ ]
  Qualità (1-5): [ ]
  Lingua fonti: [IT/EN/misto]
  Allucinazione?: [sì/no]
  Tool call: 1

MODALITÀ C (MCP SearXNG grezzo):
  Params: query=[...] language=none time_range=none
  chars_search_out: [ ]  ← MISURARE REALMENTE
  URL letti: [ ] → [URL]
  chars_read_out: [ ]    ← MISURARE REALMENTE
  chars_totale: [ ]
  Qualità (1-5): [ ]
  Lingua fonti: [IT/EN/misto]
  Tool call: [ ]

MODALITÀ D (MCP + Skill):
  Step 0 — dominio classificato: [dominio/tipo]
  Params: query=[...] language=[...] time_range=[...]
  chars_search_out: [ ]  ← identico a C se query uguale
  URL letti: [ ] → [URL con maxLength]
  chars_read_out: [ ]    ← MISURARE REALMENTE
  chars_totale: [ ]
  Qualità (1-5): [ ]
  Lingua fonti: [IT/EN/misto]
  Tool call: [ ]
  Delta chars vs C: [ ] (positivo = skill costa di più, negativo = skill risparmia)

VERDETTO T0X:
  Migliore qualità: [A/B/C/D]
  Minore overhead: [A/B/C/D]
  Caso d'uso: [quando usare quale]
═══════════════════════════════════════════════
```

---

## Come misurare i chars realmente

Dopo ogni tool call, esegui questo snippet per misurare l'output ricevuto:

```python
# Incolla l'output del tool in una variabile e misura
output = """[INCOLLA QUI L'OUTPUT COMPLETO DEL TOOL]"""
print(f"chars: {len(output)}")
print(f"token approssimati (~4 chars/token): {len(output)//4}")
```

Oppure usa lo script bash:
```bash
echo -n "[OUTPUT]" | wc -c
```

---

## Metriche da raccogliere per l'analisi finale

Per ogni test, compila questa riga nella tabella aggregata:

```
| Test | KB_q | WS_q | WS_chars | MCP-B_q | MCP-B_chars | MCP-C_q | MCP-C_chars | Lingua_ok | Migliore |
```

Dove:
- `_q` = qualità 1-5
- `_chars` = chars totali nel contesto (search + read)
- `Lingua_ok` = sì se la lingua attesa era quella ricevuta
- `Migliore` = modalità con il miglior rapporto qualità/overhead

---

## Risultati del benchmark originale (2026-05-29) per confronto

| Test | KB | WS_chars | WS_q | MCP-B_chars | MCP-B_q | MCP-C_chars | MCP-C_q | Migliore |
|---|---|---|---|---|---|---|---|---|
| T01 Fact OpenAI | 5 | ~900 | 5 | ~3.200 | 5 | ~3.200 | 5 | KB |
| T03 News maggio | 1 | ~1.200 | 5 | ~2.600 | 3 | ~2.400 | 5 | WS/MCP-C |
| T04 Recipe IT | 3 | ~1.100 | 4 | ~12.200 | 4 | ~4.900 | 5 | MCP-C |
| T07 Fact CEO | 5 | ~700 | 5 | ~3.050 | 5 | ~3.050 | 5 | KB |
| T11 GDPR IT | 2 | ~1.000 | 3 | ~3.200 | 4 | ~3.200 | 4 | MCP-C |
| T06 TS comp EN | 4 | ~1.100 | 5 | ~3.150 | 4 | ~4.650 | 5 | WS |
| T12 Failure | 4 | ~900 | 2 | ~100 | 5 | ~200 | 5 | KB/MCP |

---

## Changelog

| Versione | Data | Note |
|---|---|---|
| 1.0 | 2026-05-29 | Prima versione, 7 test eseguiti su 12 pianificati |
| — | — | T02, T05, T08, T09, T10 da completare in sessioni successive |
