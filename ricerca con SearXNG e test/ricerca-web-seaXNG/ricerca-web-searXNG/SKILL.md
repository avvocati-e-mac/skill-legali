---
name: ricerca-web-searXNG
description: >
  Esegue ricerche web ottimizzate tramite il MCP SearXNG con consumo minimo di token.
  Classifica automaticamente il dominio della query (legale IT, AI/generativa, informatica,
  cucina, generale) e adatta lingua, parametri e profondità di lettura. Usa progressive
  disclosure: risponde dagli snippet per query semplici, legge le pagine solo quando serve.
  Per query legali italiane integra il routing verso BuddaLaw (giurisprudenza) e la skill
  Normattiva (articoli di legge) quando disponibili, usando SearXNG solo per dottrina e
  commenti. Emette sempre un'intestazione con i parametri usati per trasparenza.

  TRIGGER — usare questa skill quando l'utente chiede di:
  cercare su internet, trovare informazioni aggiornate, cercare notizie recenti, cercare
  documentazione tecnica, cercare ricette, cercare sentenze o dottrina giuridica,
  trovare fonti web, fare una ricerca, "cerca online", "cerca sul web", "cosa dice
  internet su", "ultime notizie su", "trova informazioni su", ricerche su AI e modelli
  linguistici, ricerche su framework e librerie, ricerche su cucina e gastronomia,
  trovare commenti dottrinali o prassi su argomenti legali.

  NOT-TRIGGER — NON usare questa skill quando:
  la query riguarda file o codice nel progetto locale; la risposta è derivabile dalla
  knowledge base interna senza ricerca esterna; la query è solo una citazione normativa
  (art. X c.c. ecc.) e la skill Normattiva è installata; la query è solo una ricerca
  di sentenze specifiche e il MCP BuddaLaw è disponibile.
---

# Skill: Ricerca Web (SearXNG)

Ricerca web ottimizzata per token, con routing intelligente tra SearXNG, BuddaLaw e Normattiva.

## Compatibilità runtime

Questa skill deve funzionare sia in ambienti Claude sia in ambienti OpenAI/Codex.

- **Se stai operando in Claude Desktop, Claude for Work/Cowork o Claude Code:** usa i tool MCP SearXNG esposti con i nomi logici `searxng_web_search` e `web_url_read`; se SearXNG non è disponibile, applica il fallback Claude descritto in fondo.
- **Se stai operando in Codex o in un ambiente OpenAI:** usa i tool MCP SearXNG disponibili nell'ambiente corrente (es. namespace `mcp__searxng` in Codex) mantenendo gli stessi parametri logici; se SearXNG non è disponibile, applica il fallback OpenAI/Codex descritto in fondo.
- Non usare un fallback web in modo silenzioso: il cambio di strumento va sempre dichiarato all'utente.

## Step 0 — Intent parsing (0 tool call)

Prima di qualsiasi ricerca, esegui questi controlli nell'ordine indicato:

### 0a-bis. URL diretto — la fonte è già fornita?

Se l'input dell'utente **è già un URL** (o "riassumi/leggi/cosa dice questo: <url>"):
- **0 chiamate `searxng_web_search`** — la fonte è data, non serve cercare
- Vai diretto a `web_url_read(url, readHeadings=true)` → identifica la sezione rilevante all'intento → `web_url_read(url, section="[sezione]", maxLength=1200)`
- Se non c'è un intento specifico ("riassumi" generico) → `paragraphRange:"1-10"` + `maxLength:1800`
- Emetti: `[url-direct · 0 search]` come intestazione

Questo è il massimo del progressive disclosure: nessuna ricerca quando l'URL è già noto.

### 0a. KB check — la ricerca è necessaria?

Valuta se la risposta è derivabile dalla knowledge base interna **senza ricerca**:
- È un fatto stabile e verificabile (anno fondazione, CEO attuale di azienda nota, definizione standard, persona pubblica nota)?
- Non richiede aggiornamenti recenti (nessun segnale temporale nella query)?
- Non richiede lingua specifica IT per fonti italiane?

**Se tutte e tre le condizioni sono vere → rispondi direttamente, 0 tool call.**
Emetti: `[KB · fact · 0 call]` come intestazione.

Esempi di query che NON richiedono ricerca: "chi ha fondato Apple", "cosa è un algoritmo", "capitale della Francia", "cos'è il TCP/IP", "anno fondazione OpenAI".
Esempi che RICHIEDONO ricerca: "ultime notizie su X", "sentenza recente su Y", "ricetta di Z", "normativa italiana su W".

**ATTENZIONE — non applicare KB-check a:**
- Cariche politiche o aziendali (presidente, CEO, ministro) → cambiano frequentemente
- Prezzi, valutazioni, statistiche → cambiano continuamente  
- Normative con possibili aggiornamenti recenti
- Qualsiasi query con segnale temporale ("attuale", "oggi", "2026", "ora")

### 0b. Cache check — risultati già presenti in sessione?

Prima di fare una nuova ricerca, controlla se nella conversazione corrente esistono già risultati SearXNG pertinenti:
- Cerca tool_result di `searxng_web_search` con query simile o stesso dominio
- Se trovati e recenti (stessa sessione, stessa area tematica) → riusali, **0 nuove tool call**
- Emetti: `[CACHE · {dominio} · 0 nuove call]` come intestazione

**Eccezione — MAI riusare la cache per `news`:** per query di tipo `news` la freschezza
conta anche entro la stessa sessione (potrebbero esserci aggiornamenti tra una domanda e
l'altra). Esegui sempre una ricerca nuova per le news, ignora la cache.

### 0c. Classificazione query

Determina:

**1. Dominio**
- `legale-it` — diritto italiano, norme, sentenze, dottrina, prassi
- `ai-generativa` — intelligenza artificiale, LLM, modelli, paper AI
- `informatica` — programmazione, documentazione tecnica, framework, librerie
- `cucina` — ricette, ingredienti, tecniche culinarie
- `general` — tutto il resto

**2. Sotto-tipo (solo per legale-it)**
- `giurisprudenza` — sentenze, Cassazione, TAR, Corte d'Appello, pronunce
- `normativa` — articoli di legge, decreti, codici, disposizioni
- `dottrina` — commenti, prassi, circolari, interpretazioni

**3. Tipo query**
- `fact` — risposta atomica: nome, data, numero, definizione breve → 3 risultati, 0 letture URL
- `deep` — spiegazione, guida, analisi → 5 risultati, 1-3 letture URL
- `comparison` — confronto tra due o più cose → 5 risultati, 1-3 letture URL
- `news` — ultime notizie, aggiornamenti recenti → 7 risultati, 1-2 letture URL
- `recipe` — ricetta completa → 3 risultati, 1 lettura URL con `readHeadings` poi `section`

**4. Parametri**
- `lingua`: `it` per legale-it e cucina IT; multilingual EN+IT per ai-generativa; EN per informatica (IT se query in italiano); autodetect per general
- `time_range`: solo se la query contiene parole come "ultime", "recenti", "oggi", "2025", "2026", "novità" → `day`/`month`/`year`
- `n_risultati`: come da tipo query sopra

**5. Query multi-dominio** — se la query tocca due domini distinti (es. legale-it +
ai-generativa: "implicazioni legali GDPR degli LLM in azienda"):
- Se l'**intento primario è chiaro dal verbo/oggetto** della richiesta → usa quel dominio,
  non chiedere nulla (es. "spiegami la *normativa* sull'AI" → primario = legale-it).
- Se i due domini sono **paritari e non risolvibili** → chiedi all'utente, riusando il
  pattern A/B già definito in `legal_routing.md`:
  ```
  La tua domanda tocca due ambiti. Su cosa vuoi che mi concentri?
   A) {dominio 1} — {cosa troverò}
   B) {dominio 2} — {cosa troverò}
  ```
  Dopo la scelta → **1 sola ricerca** sul dominio scelto. Non eseguire due ricerche
  separate (raddoppierebbe l'overhead) salvo richiesta esplicita dell'utente.

**6. Routing legale** (solo se dominio = `legale-it`): vedi `references/legal_routing.md`

**Output Step 0** — emetti sempre questa intestazione prima di procedere:
```
[{dominio} · {tipo} · {n} fonti · {lingua} · {time_range o "nessun filtro"}]
```
Esempio: `[legale-it/dottrina · deep · 5 fonti · it · nessun filtro]`

---

## Step 1 — Ricerca

Chiama `searxng_web_search` con i parametri determinati in Step 0.

Dopo la risposta, estrai **solo** questi campi per ogni risultato e scarta tutto il resto:
```
{"t":"Titolo risultato","u":"https://url.risultato","s":"snippet max 80 parole troncato qui"}
```
Una riga JSON per risultato. Non aggiungere altro testo.

**Fallback su risultati irrilevanti o errore** (ordine ottimizzato):
SearXNG restituisce sempre qualcosa — valuta la pertinenza: se nessuno dei primi 3 snippet contiene termini chiave della query, considera i risultati irrilevanti.
1. **Prima allarga `time_range`** se presente e stretto: `day`→`month`→`year`→nessuno. Spesso 0 risultati pertinenti dipende solo da un filtro temporale troppo restrittivo su un topic reale ma di nicchia. Riprova prima di toccare la query.
2. Allarga lingua a multilingual
3. Semplifica la query (rimuovi termini specifici) — **solo** dopo aver provato i punti 1-2
4. Riprova una volta. Se ancora irrilevante → informa l'utente: "Non ho trovato risultati pertinenti per '[query]'. Prova a riformulare." e fermati.

---

## Step 2 — Progressive disclosure con readHeadings

Sulla base del tipo query determinato in Step 0:

| Tipo | Azione |
|---|---|
| `fact` | Risponde dagli snippet. **Stop — 0 letture URL.** |
| `recipe` | **Prima** chiama `web_url_read` con `readHeadings: true` sul top URL → identifica la sezione "Ingredienti" o "Preparazione" → **poi** rileggi con `section: "[sezione]"` + `maxLength: 1200` |
| `news` | Legge **1-2 URL** più recenti con `paragraphRange: "1-6"` e `maxLength: 1500` |
| `deep` | **Prima** chiama `web_url_read` con `readHeadings: true` → identifica la sezione più rilevante → **poi** rileggi con `section: "[sezione]"` + `maxLength: 900`. Se `readHeadings` non restituisce sezioni utili, usa `paragraphRange: "1-8"` + `maxLength: 1500` |
| `comparison` | Legge **2-3 URL** bilanciati. Per ciascuno: `readHeadings: true` → leggi **2 sezioni** se la query contiene "quando usare/when to use/quale scegliere" (sezione differenze + sezione raccomandazione), altrimenti 1 sezione. `maxLength: 900` per sezione |
| `legale-it` qualunque tipo | `paragraphRange: "1-10"` + `maxLength: 1500` (testi legali non hanno heading standard, readHeadings non utile) |

**Procedura readHeadings (per recipe/deep/comparison):**
1. `web_url_read(url=URL, readHeadings=true)` → ottieni lista titoli (~100-200 chars)
2. **Se la lista supera ~20 titoli** (es. pagine Wikipedia lunghe): NON scorrerla tutta — considera solo i primi 20 + filtra per le keyword dell'intento. La lista heading non deve diventare essa stessa un costo.
3. Identifica il titolo per **corrispondenza semantica**, non testuale esatta: scegli l'heading il cui *significato* corrisponde all'intento, anche se le parole differiscono. Sinonimi comuni:
   - recipe → "Ingredienti" ≈ "Cosa serve" / "Occorrente"; "Preparazione" ≈ "Come si prepara" ≈ "Procedimento" ≈ "Come fare"
   - comparison → "Differenze" ≈ "Differences" ≈ "Comparison"; "Quando usare" ≈ "When to use" ≈ "Which to choose"
   - deep → l'heading che nomina il concetto chiave della query
4. `web_url_read(url=URL, section="[keyword centrale del titolo]", maxLength=800)` → solo quella sezione.
   **Passa la keyword centrale, NON l'heading completo** (E4): `section:"Hard reasoning"` trova
   "3. Hard reasoning: Humanity's Last Exam"; il match della stringa intera spesso dà "not found".
5. Se step 4 restituisce <200 chars (sezione vuota/non trovata) → fallback a `paragraphRange: "1-8"` + `maxLength: 1500`

**readHeadings→section è affidabile su siti ricette, blog tecnici strutturati e docs ufficiali.**
Su siti news/istituzionali con molto chrome può fallire → vedi "lettura resiliente" nelle Note operative.

**Costo readHeadings:** ~100-200 chars aggiuntivi per URL (1 extra call). Break-even: se la sezione estratta è <1.300 chars vs 1.500 di paragraphRange, il costo netto è negativo.

Scegli gli URL da leggere in base alla rilevanza dello snippet e all'autorevolezza della fonte (fonti ufficiali > blog > forum).

---

## Step 3 — Risposta finale

1. Sintetizza il contenuto con le fonti caricate
2. Cita le fonti nel formato `[Titolo](URL)`
3. Per ogni riferimento normativo italiano presente nella risposta (art. X c.c., d.lgs. ecc.): se la skill **Normattiva** è installata, applica il suo workflow per trasformare ogni citazione in link cliccabile Normattiva.it
4. Ripeti l'intestazione di Step 0 all'inizio della risposta

---

## Note operative

- Non leggere mai una pagina intera senza `maxLength` esplicito
- Non fare più di 4 chiamate `web_url_read` per singola query utente (include readHeadings e gli URL alternativi sotto)
- **Lettura resiliente (prova-il-successivo):** se `web_url_read` su un URL restituisce <200 chars utili, solo un banner di consenso cookie / paywall, oppure errore → **passa all'URL successivo** dagli snippet già in mano (0 nuove `searxng_web_search`). Prova al massimo 2 URL alternativi; se anche questi falliscono, rispondi dagli snippet disponibili e segnalalo.
- **Chrome/menu invece del contenuto (E1):** su siti news e istituzionali il primo `paragraphRange:"1-N"` cade spesso nel chrome (header, menu, social link). Se la lettura `1-N` è prevalentemente voci di menu/link (<200 chars di prosa), **rileggi con offset più avanti** (es. `paragraphRange:"9-25"`) PRIMA di scartare l'URL.
- **Siti istituzionali a chrome pesante (E2):** alcune fonti ufficiali (es. garanteprivacy.it) restituiscono solo menu, inestraibili dal MCP. **Citale come riferimento** ma **leggi il contenuto da una fonte secondaria strutturata** (Iubenda, Altalex) presente negli snippet.
- **Risultato PDF / non-HTML (E3):** il MCP spesso **non parsa i PDF** (restituisce byte binari `%PDF...`). Per `legale-it/dottrina` (dove la fonte è tipicamente un PDF accademico o una rivista a paywall): **declassa PDF/paywall nella scelta di lettura**, privilegia HTML aperto; se restano solo PDF/paywall, **rispondi dagli snippet** (spesso già ricchi) e dichiaralo. Non insistere oltre 2 letture fallite.
- **Re-rank per autorevolezza prima di leggere (E5/E6):** non fidarti del solo relevance score per scegliere l'URL. Per `informatica` promuovi i **docs ufficiali** (docs.python.org, MDN) sopra blog/SEO; per `cucina` evita social/video come fonte di procedura. Tabella completa in `references/search_strategy.md`.
- La riga di intestazione `[...]` è sempre visibile all'utente — aiuta a correggere la classificazione se sbagliata
- Consulta `references/search_strategy.md` per tabelle parametri e template
- Consulta `references/legal_routing.md` per il routing completo delle query legali

## Fallback se SearXNG non disponibile

Se `searxng_web_search` restituisce errore di rete o timeout:
1. Informa l'utente: `⚠️ Il server SearXNG non è raggiungibile.`
2. **Se stai operando in Claude Desktop, Claude for Work/Cowork o Claude Code:** proponi `WebSearch Claude` se disponibile: `Posso continuare con WebSearch Claude (disponibile ma con meno controllo su lingua e recency). Procedo?` Se l'utente conferma, usa `WebSearch` con la stessa query e prefissa la risposta con `[WebSearch Claude fallback · parametri lingua/recency non garantiti]`.
3. **Se stai operando in Codex o in un ambiente OpenAI:** usa il tool web/search disponibile nell'ambiente solo se le regole della sessione lo consentono; prefissa la risposta con `[OpenAI/Codex web fallback · parametri SearXNG non disponibili]`. Se il runtime non offre ricerca web, chiedi conferma all'utente per procedere senza fonti live o per configurare SearXNG.

Non usare mai un fallback web come sostituto silenzioso di SearXNG.
