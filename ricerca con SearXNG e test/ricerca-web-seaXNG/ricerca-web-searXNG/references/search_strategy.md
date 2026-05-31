# Search Strategy — Ricerca Web

## Tabella parametri per dominio

| Dominio | `language` | `time_range` default | `safesearch` | Fonti prioritarie |
|---|---|---|---|---|
| `legale-it/dottrina` | `it` | nessuno | `1` | Altalex, Il Sole 24 Ore Diritto, Studio Cataldi, Diritto.it, Brocardi |
| `legale-it/giurisprudenza` | `it` | `year` se "ultime/recenti" | `1` | → routing BuddaLaw (vedi legal_routing.md) |
| `legale-it/normativa` | `it` | nessuno | `1` | → routing Normattiva (vedi legal_routing.md) |
| `ai-generativa` | multilingual | `month` (default) | `1` | arXiv, Anthropic blog, OpenAI blog, Google DeepMind, HuggingFace, The Verge AI, Ars Technica AI |
| `informatica` | `en` (o `it` se query in IT) | nessuno | `1` | Docs ufficiali, GitHub, MDN, Stack Overflow, Dev.to, CSS-Tricks |
| `cucina` (IT) | `it` | nessuno | `1` | Giallozafferano, Cookaround, Misya, La Cucina Italiana, Cucchiaio d'Argento |
| `cucina` (EN/internazionale) | `en` | nessuno | `1` | Serious Eats, NYT Cooking, BBC Good Food, AllRecipes, Bon Appétit |
| `general` | autodetect dalla query | nessuno | `1` | ampio spettro |

### Lingua di terze parti (FR/ES/DE/altre)

Le regole IT/EN sopra coprono i due casi dominanti. Per query scritte in una **terza
lingua** (francese, spagnolo, tedesco, ecc.):
- `language` = la lingua della query (autodetect)
- Fonti: autodetect, nessun elenco prioritario forzato
- Non forzare `it` o `en` su una query che non è in quelle lingue — degraderebbe la pertinenza

---

## Numero risultati per tipo query

| Tipo | `n_risultati` | Call URL totali | Metodo lettura (v2) |
|---|---|---|---|
| `fact` | 3 | 0 | — (risponde da snippet) |
| `recipe` | 3 | 2 (1 headings + 1 section) | `readHeadings:true` → `section:"Ingredienti/Preparazione"` + `maxLength:800` |
| `news` | 7 | 1-2 | `paragraphRange:"1-6"` + `maxLength:1500` |
| `deep` | 5 | 2 per URL (1 headings + 1 section) | `readHeadings:true` → `section` rilevante + `maxLength:1200` |
| `comparison` | 5 | 2 per URL | `readHeadings:true` → `section` + `maxLength:1000` per URL |
| qualunque `legale-it` | 5 | 1-3 | `paragraphRange:"1-10"` + `maxLength:1500` (no readHeadings) |

### Stima costo v1 vs v2 per tipo

| Tipo | v1 chars lettura | v2 chars lettura | Delta |
|---|---|---|---|
| `fact` | 0 | 0 | = |
| `recipe` | 1.500-2.000 | ~150 (headings) + ~800 (section) = ~950 | **-40%** |
| `news` | 1.500 | 1.500 | = |
| `deep` (1 URL) | 1.500 | ~150 + ~1.200 = ~1.350 | **-10%** |
| `comparison` (2 URL) | 3.000 | 2×(~150+~1.000) = ~2.300 | **-23%** |
| `legale-it` | 1.500 | 1.500 | = |

---

## Template output Step 1 (JSON a righe)

Dopo ogni chiamata `searxng_web_search`, emetti **solo** questa struttura per ogni risultato:

```
{"t":"Titolo della pagina","u":"https://url-completo.it/pagina","s":"Testo del snippet troncato a massimo ottanta parole, tagliando esattamente qui se più lungo"}
{"t":"Secondo risultato","u":"https://secondo-url.com","s":"Snippet secondo risultato..."}
```

Regole:
- Nessun altro testo prima/dopo il blocco JSON
- Snippet: max 80 parole, tronca con `...` se più lungo
- Titolo: esattamente come da risultato, senza modifica
- URL: completo, nessun accorciamento
- Nessun campo aggiuntivo oltre `t`, `u`, `s`

---

## Criteri selezione URL da leggere

Per scegliere quali URL approfondire in Step 2, valuta in ordine:

1. **Rilevanza snippet** — lo snippet risponde direttamente alla query?
2. **Autorevolezza fonte** — fonte ufficiale/istituzionale > testata specializzata > blog > forum
3. **Recency** — per query `news` o `ai-generativa`, preferisci date più recenti
4. **Lingua** — preferisci nella lingua del dominio (IT per legale/cucina, EN per informatica)
5. **Evita** — Wikipedia come unica fonte per deep read; forum per query legali; siti con paywall noto

### Re-rank per autorevolezza PRIMA di leggere (v4 — euristica E5/E6)

> Misurato (benchmark vs Perplexity, `test/retrieval_eval.md`): il relevance score grezzo di SearXNG
> a volte mette un **SEO-blog sopra la fonte ufficiale** (es. un blog dev.to sopra docs.python.org).
> Perplexity, a parità di ranking medio, privilegia gli ufficiali. Correzione 100% interna alla skill.

Prima di scegliere quale URL leggere, **ri-ordina i candidati per tipo-fonte secondo il dominio**, NON
fidarti del solo relevance score. Ordine di preferenza per dominio:

| Dominio | Ordine di preferenza per la LETTURA |
|---|---|
| `informatica` | **docs ufficiali** (docs.python.org, developer.mozilla.org, `*.readthedocs.io`, doc ufficiale del framework) > blog tecnici noti (LogRocket, Real Python) > Stack Overflow > forum/SEO-blog |
| `legale-it/dottrina` | enciclopedie giuridiche (Treccani Diritto) > riviste aperte (Altalex, Diritto.it, Il Sole 24 Ore Diritto) > **poi** PDF accademici / paywall (spesso non leggibili → vedi E3) |
| `cucina` | siti ricette affermati (Giallozafferano, Cookaround) > food blog > **mai** social/video (YouTube/FB/TikTok) come fonte di procedura |
| `ai-generativa` | blog/vendor ufficiali + System Card/paper > testate tech (Ars, The Verge) > aggregatori/SEO-blog |

Se la fonte ufficiale è presente ma più in basso nei risultati, **promuovila** come primo URL da leggere.

---

## Lettura resiliente del contenuto (v4 — euristiche E1–E4)

> Il MCP `web_url_read` ha limiti reali emersi dal benchmark (`test/benchmark_pplx_vs_searxng.md`).
> Queste regole evitano di sprecare letture su chrome/PDF e di mancare la sezione giusta.

- **E1 — Il primo `paragraphRange:"1-N"` cade spesso nel chrome/menu** su siti news e istituzionali
  (header, navigazione, social link occupano i primi paragrafi). Se la lettura `1-N` restituisce
  prevalentemente link/voci di menu (<200 chars di prosa utile), **NON arrenderti**: rileggi con un
  **offset più avanti** (es. `paragraphRange:"9-25"`) prima di passare all'URL successivo.
- **E2 — Siti istituzionali a chrome pesante** (es. garanteprivacy.it) sono spesso **inestraibili** dal
  MCP (restituiscono solo menu). Citali come **riferimento autorevole** nella risposta, ma **leggi il
  contenuto da una fonte secondaria ben strutturata** (es. Iubenda, Altalex) presente negli snippet.
- **E3 — PDF accademici e riviste a paywall** (tipici della dottrina legale-it) **non vengono parsati**
  dal MCP (restituiscono byte binari `%PDF...` o solo menu+paywall). Per `legale-it/dottrina`:
  **declassa PDF/paywall nella scelta di lettura**, privilegia fonti HTML aperte; se restano solo
  PDF/paywall, **rispondi dagli snippet** (spesso già ricchi) e dichiaralo. Non insistere oltre 2 letture fallite.
- **E4 — `section:` funziona meglio con match PARZIALE**: passa la **keyword centrale** dell'heading,
  non la stringa completa. Es. `section:"Hard reasoning"` trova "3. Hard reasoning: Humanity's Last Exam";
  `section:"Come preparare"` trova "Come preparare gli Spaghetti alla Carbonara". Il match esatto della
  stringa intera spesso fallisce con "not found".

**Dove `readHeadings`→`section` funziona benissimo** (confermato): siti ricette (Giallozafferano), blog
tecnici strutturati (LogRocket), docs ufficiali (Python). Lì il progressive disclosure rende ~1.200 chars
di contenuto puro invece della pagina intera. Usalo con fiducia su questi domini.

---

## Segnali per `time_range`

Usa `time_range` **solo** se la query contiene esplicitamente:
- `day`: "oggi", "nelle ultime ore", "stamattina"
- `month`: "questo mese", "ultime settimane", "recente"
- `year`: "quest'anno", "2025", "ultime novità", "aggiornamento"

Non impostare `time_range` per query senza riferimenti temporali.

---

## Fallback su risultati irrilevanti

SearXNG non restituisce mai davvero 0 risultati — trova sempre qualcosa di correlato per parole chiave.
Il criterio di fallback è la **pertinenza**: i risultati sono irrilevanti se nessuno dei primi 3 snippet contiene almeno 1 termine chiave della query originale.

L'ordine dei tentativi è ottimizzato: **prima si allarga il filtro temporale** (causa più
frequente di 0 risultati su topic reali ma di nicchia), poi la lingua, e solo da ultimo si
tocca la query — perché semplificare la query troppo presto cambia ciò che si sta cercando.

```
Tentativo 1: parametri originali
  → risultati irrilevanti (nessun termine query negli snippet)?
Tentativo 2: allarga time_range (day→month→year→nessuno) mantenendo query e lingua
  → ancora irrilevanti?
Tentativo 3: lingua → multilingual + query semplificata
  → ancora irrilevanti?
→ Messaggio utente: "Non ho trovato risultati pertinenti per '[query]'.
  Prova a riformulare la ricerca o verifica i termini usati."
```

---

## Composizione con skill Normattiva (post-risposta)

Dopo aver sintetizzato la risposta in Step 3, se nel testo compaiono riferimenti normativi italiani (pattern: `art. N sigla`, `d.lgs. N/AAAA`, `legge N/AAAA`, `r.d. N/AAAA`, `D.P.R. N/AAAA`) **e** la skill Normattiva è installata:

1. Estrai tutti i riferimenti normativi dalla bozza di risposta
2. Invoca la skill Normattiva passando la lista dei riferimenti
3. Sostituisci i riferimenti nudi con i link Normattiva.it generati
4. Presenta la risposta finale linkificata

Se Normattiva non è installata, lascia i riferimenti come testo semplice e aggiungi (una volta per sessione):
> `ℹ️ Installa la skill Normattiva per avere link cliccabili alle norme: https://github.com/filippostrozzi/skill-legali/blob/main/normattiva`
