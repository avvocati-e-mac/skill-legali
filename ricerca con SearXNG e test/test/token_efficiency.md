# Efficienza token — misura oggettiva (separata dal giudizio cieco)

> Conteggio dei **caratteri reali** degli output dei tool ricevuti in sessione per ciascun
> metodo di ricerca, sullo stesso task (installazione SearXNG macOS ARM).
> Questa misura è **fuori** dal giudizio cieco di qualità: i giudici non la vedono, perché
> indicava il metodo. È un dato oggettivo, non un punteggio.

## Caratteri ingeriti per metodo

| Metodo | Dettaglio | Char |
|---|---|---|
| **WebSearch** | 4 query × (link list + prosa sintetizzata) | **~6.690** |
| **MCP + skill** | 1 search + 2 readHeadings + 2 section + 1 paragraphRange (con 1 fallback e 1 skip) | **~5.200** |
| **MCP grezzo** | 1 search + 1 lettura full-page (didof.dev) | **~14.580** |

Rapporti: WebSearch / skill = **1,29×** · grezzo / skill = **2,80×** · grezzo / WebSearch = **2,18×**.

## Lettura del dato

- Il **MCP grezzo** è di gran lunga il più costoso: una sola pagina full-page (~13.500 char,
  per la maggior parte off-topic: setup n8n/Postgres/Gemini, nav, footer) costa **quasi 3×**
  l'intera ricerca della skill, e coprirebbe meno argomenti (servirebbero altre letture
  full-page per OrbStack/ARM).
- La **skill** è la più frugale (~5.200 char) grazie a readHeadings→section, fallback mirati e
  allo skip della pagina nav/JS.
- **WebSearch** (~6.690 char, **prima non misurato**) è intermedio: leggermente più costoso
  della skill perché ha richiesto 4 query per coprire il topic, ma molto più economico del
  grezzo perché restituisce sintesi compatte invece di pagine intere.

## Nota metodologica

- I valori sono conteggi dei tool_result effettivi di questa sessione (vedi `_KEY.md` per la
  corrispondenza con le guide blind). Sono stime al ~±5% sulla lunghezza dei blocchi prosa di
  WebSearch (non perfettamente deterministici tra run), esatti sui read MCP.
- L'efficienza token **non** misura la qualità del contenuto: per quella vedi
  `guide_comparison_report.md` (giudizio cieco a rubrica).
