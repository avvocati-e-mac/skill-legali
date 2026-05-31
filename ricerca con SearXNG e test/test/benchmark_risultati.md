# Benchmark Rigoroso — Risultati Reali
## Ha senso usare skill+MCP SearXNG rispetto ai tool base di Claude?

Data: 2026-05-29 | Metodologia: test eseguiti live con misure reali di caratteri

---

## 1. Dati misurati (non stimati)

### Overhead fisso MCP SearXNG
Ogni chiamata `searxng_web_search` produce ~**3.000 chars** nel contesto,
indipendentemente da qualsiasi skill. Questo è il costo irriducibile e invariabile.
In token (~4 chars/token): **~750 token per ricerca**.

| Test | Query | chars_mcp_out | Note |
|---|---|---|---|
| T01 | Anno fondazione OpenAI | 3.193 | Risposta già in snippet top-2 |
| T03b | News OpenAI (senza time_range) | 2.590 | 3/10 risultati recenti |
| T03c | News OpenAI (con time_range:month) | 2.386 | 8/10 risultati recenti |
| T04 | Ricetta cacio e pepe | 3.380 | Top: GialloZafferano, 100% IT |
| T06 | TS interfaces vs types | 3.150 | Top: Reddit/LogRocket, 100% EN |
| T07 | CEO di Google 2026 | 3.050 | Risposta in snippet top-1 |
| T11 | GDPR cookies 2026 | 3.200 | Top: myagileprivacy.com (IT) |
| **Media** | | **~3.000** | |

### Costo lettura URL: differenza reale skill vs grezzo

| Modalità | URL letto | chars output | Contenuto utile? |
|---|---|---|---|
| B grezzo (nessun limite) | GialloZafferano cacio e pepe | **9.200** | ~30% utile (menu nav, commenti, footer = rumore) |
| C skill (paragraphRange+maxLength:1500) | GialloZafferano cacio e pepe | **1.500** | ~95% utile (ingredienti + procedura) |
| **Risparmio lettura URL** | | **-7.700 chars (-84%)** | |

### Test failure (T12)
Query: `"zzxqpfm blorgatron quantum spaghetti 2099"`
→ SearXNG restituisce **0 risultati** con messaggio esplicito (non risultati irrilevanti come ipotizzato nel piano — il bug era sbagliato). Il fallback funziona correttamente.

### Test recency (T03)
Senza `time_range`: **3/10** risultati di maggio 2026.
Con `time_range:month`: **8/10** risultati di maggio 2026.
→ Il parametro `time_range` è il beneficio più concreto e misurabile della skill.

---

## 2. Risposta alle 3 domande chiave

### Domanda 1: Ha senso usare MCP SearXNG vs WebSearch Claude?

**Risposta: SÌ, in casi specifici. NO come soluzione universale.**

| Scenario | Vantaggio SearXNG | WebSearch Claude |
|---|---|---|
| Query con risposta nota (fact su knowledge base) | ❌ Nessuno (+750 token di overhead) | ✅ Risposta diretta, 0 token MCP |
| Notizie recenti IT (lingua controllata) | ✅ `language:it` forza fonti italiane | ⚠️ Nessun controllo lingua |
| Notizie recenti con `time_range` | ✅ +166% risultati rilevanti (3→8/10) | ⚠️ Nessun controllo temporale |
| Documentazione tecnica EN | ✅ `language:en` garantisce fonti EN | ⚠️ Nessun controllo |
| Privacy / disponibilità | ✅ Istanza locale, nessun rate limit | ⚠️ Solo USA, servizio esterno |
| Query semplice non recente | ❌ 750 token di overhead inutili | ✅ Più efficiente |

**Conclusione**: SearXNG è superiore per **query che richiedono lingua specifica o recency**. Per tutto il resto (facts, knowledge base) è più costoso senza beneficio.

---

### Domanda 2: La skill migliora rispetto al grezzo?

**Risposta: SÌ in modo significativo, ma solo sul `web_url_read`.**

Il risparmio è concentrato su un punto solo ma potente:

| Componente | Grezzo | Con Skill | Risparmio reale |
|---|---|---|---|
| `searxng_web_search` output | ~3.000 chars | ~3.000 chars | **0%** — invariabile |
| `web_url_read` output (recipe/deep) | ~9.200 chars (pagina intera) | ~1.500 chars (estratto) | **-84%** |
| `web_url_read` output (fact) | 0-9.200 chars (a caso) | **0** (skip sistematico) | **0-100%** |
| Qualità risultati news | 3/10 recenti | 8/10 recenti | **+166%** rilevanza |
| Lingua IT legale | non garantita | garantita | qualitativa |

**Il vero valore della skill non è comprimere il search output** (impossibile) **ma:**
1. **Parametri corretti** per dominio → qualità risultati (recency, lingua)
2. **Skip `web_url_read`** su query fact → 0-9.200 chars risparmiati
3. **`maxLength:1500`** su letture → -84% per pagine con molto rumore (nav, footer, commenti)
4. **Routing legale** → 0 SearXNG per normativa (→Normattiva) e giurisprudenza (→BuddaLaw)

---

### Domanda 3: La skill è ulteriormente migliorabile?

**Risposta: SÌ, con 4 interventi prioritari.**

#### Miglioramento 1 — `readHeadings` prima di leggere (ALTO IMPATTO)
Il costo di 9.200 chars su GialloZafferano è dovuto principalmente a navigazione, footer, commenti. Il tool supporta `readHeadings:true` che restituisce solo i titoli (~200-300 chars). Usarlo come primo passo per individuare la sezione esatta da leggere con `section`, riducendo ulteriormente il costo.

```
Attuale:  paragraphRange:1-8 + maxLength:1500 → 1.500 chars
Proposta: readHeadings → trova sezione "Ingredienti" → section:"Ingredienti" + maxLength:800 → ~800 chars
Risparmio aggiuntivo: -47%
```

#### Miglioramento 2 — NOT-TRIGGER più aggressivo per query fact (ALTO IMPATTO)
Attualmente la skill non ha un meccanismo esplicito per decidere se una query è risolvibile dalla knowledge base interna senza ricerca. Ogni query passa per SearXNG (+750 token fissi). Aggiungere uno step 0 esplicito:

> "Se la risposta è un fatto stabile (fondazione azienda, definizione, persona nota) e la mia knowledge base lo copre con certezza → rispondi direttamente, 0 tool call."

Risparmio: **750 token fissi per ogni query fact** (T01, T07 nei test = 2 × 750 = 1.500 token evitabili).

#### Miglioramento 3 — Cache query in sessione (MEDIO IMPATTO)
Se l'utente fa due query correlate nella stessa sessione (es. "notizie OpenAI" poi "GPT-5.5 cosa fa"), la seconda può riusare i risultati della prima. Attualmente non c'è questo controllo nella skill. Aggiungere in Step 0: controlla se esiste già un `tool_result` di `searxng_web_search` con query simile nel contesto corrente.

#### Miglioramento 4 — Fallback esplicito su WebSearch Claude se SearXNG offline (BASSO IMPATTO, ALTA ROBUSTEZZA)
Il test ha dimostrato che quando SearXNG è offline la skill si blocca. Aggiungere nella SKILL.md: "Se `searxng_web_search` restituisce errore di rete, informa l'utente e proponi di continuare con WebSearch Claude se disponibile."

---

## 3. Raccomandazione finale

```
┌─────────────────────────────────────────────────────────────────┐
│ USA MCP SearXNG + Skill quando:                                 │
│  • Query legali IT (lingua:it garantita)                        │
│  • Notizie recenti (time_range critico)                         │
│  • Ricette/documentazione (evita lettura pagina intera)         │
│  • Privacy (istanza locale, no servizi US)                      │
│                                                                 │
│ NON usare MCP SearXNG quando:                                   │
│  • Risposta è un fatto nella knowledge base                     │
│  • Query non richiede aggiornamento recente                     │
│  • SearXNG server è offline                                     │
│                                                                 │
│ Risparmio reale confermato:                                     │
│  • Lettura URL: -84% chars (da 9.200 a 1.500)                   │
│  • Recency news: +166% risultati rilevanti                      │
│  • Overhead fisso irriducibile: ~750 token/ricerca              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Prossimi miglioramenti alla skill (priorità)

| # | Intervento | Impatto | Complessità |
|---|---|---|---|
| 1 | `readHeadings` prima di leggere URL | -47% chars lettura | Bassa |
| 2 | NOT-TRIGGER esplicito per fact KB | -750 token/query | Bassa |
| 3 | Cache query in sessione | variabile | Media |
| 4 | Fallback su WebSearch Claude se offline | robustezza | Bassa |
