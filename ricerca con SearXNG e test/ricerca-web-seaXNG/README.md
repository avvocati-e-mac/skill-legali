# ricerca-web-searXNG — Skill di ricerca web ottimizzata per Claude Code

Ricerca web a **consumo minimo di token** tramite il MCP SearXNG, con routing intelligente
verso BuddaLaw (giurisprudenza IT) e la skill Normattiva (articoli di legge IT).
Classifica automaticamente il dominio della query e adatta lingua, parametri e profondità di
lettura usando **progressive disclosure**: risponde dagli snippet quando basta, legge le
pagine solo quando serve, e legge solo la sezione rilevante invece dell'intera pagina.

**Verdetto benchmark** (7 query reali, misurato live 2026-05-29):
**−56% di caratteri nel contesto** rispetto al MCP SearXNG grezzo, qualità pari o superiore.

---

## 1. Cos'è

Il MCP SearXNG da solo restituisce dati grezzi: una pagina letta può occupare 9.000–12.000
caratteri di navigazione, footer e rumore. Questa skill aggiunge un layer di *decisione*
sopra il MCP che:

- decide **se** cercare (alcune risposte vengono dalla knowledge base, 0 tool call);
- decide **come** cercare (lingua, recency, numero risultati per dominio);
- decide **quanto leggere** (snippet → sezione mirata → pagina, mai più del necessario).

---

## 2. Architettura

```
            ┌──────────────────────────────────────────────────────────┐
  Query ───▶│ STEP 0 — Intent parsing                       (0 tool call)│
            │  0a-bis  È un URL?        → salta la ricerca, leggi diretto │
            │  0a      KB-check         → fatto stabile? rispondi da KB   │
            │  0b      Cache-check      → già in sessione? riusa (no news)│
            │  0c      Classificazione  → dominio · tipo · lingua · range │
            └───────────────┬──────────────────────────────────────────-┘
                            │ (se serve cercare)
            ┌───────────────▼──────────────────────────────────────────-┐
  STEP 1 ──▶│ searxng_web_search → estrai solo {t,u,s} per risultato     │
            │ Fallback: allarga time_range → lingua → query (in quest'ord)│
            └───────────────┬──────────────────────────────────────────-┘
                            │
            ┌───────────────▼──────────────────────────────────────────-┐
  STEP 2 ──▶│ Progressive disclosure (web_url_read)                      │
            │  fact       → 0 letture (rispondi dagli snippet)            │
            │  recipe/    → readHeadings → section mirata (match semant.) │
            │  deep/comp.   con fallback a paragraphRange se serve        │
            │  news       → paragraphRange 1-6                            │
            │  legale-it  → paragraphRange 1-10 (no headings)             │
            │  resilienza → URL inutile/paywall/PDF? prova il successivo  │
            └───────────────┬──────────────────────────────────────────-┘
                            │
            ┌───────────────▼──────────────────────────────────────────-┐
  STEP 3 ──▶│ Sintesi + citazioni [Titolo](URL) + linkify Normattiva     │
            │ Ripeti l'intestazione [...] in testa alla risposta         │
            └──────────────────────────────────────────────────────────-┘
```

### I tre layer di file

| File | Quando è caricato | Contenuto |
|---|---|---|
| `ricerca-web-searXNG/SKILL.md` | **sempre** (entry point) | workflow Step 0–3, regole, note operative |
| `ricerca-web-searXNG/references/search_strategy.md` | **on-demand** | tabelle parametri per dominio, template output, fallback, lingue terze |
| `ricerca-web-searXNG/references/legal_routing.md` | **on-demand** | albero decisionale legale, routing BuddaLaw/Normattiva, multi-dominio |

I `references/` sono essi stessi **progressive disclosure**: non occupano contesto finché la
skill non li consulta per una query che li richiede (legale, parametri di dettaglio).

### Routing esterno

- **MCP BuddaLaw** — banca dati giuridica strutturata: per giurisprudenza IT, se disponibile.
- **Skill Normattiva** — trasforma le citazioni normative (`art. X c.c.`) in link cliccabili.
- **WebSearch Claude** — fallback esplicito (con conferma utente) se SearXNG è offline.

---

## 3. I controlli di Step 0 (e il perché)

| Controllo | Cosa fa | Perché |
|---|---|---|
| **0a-bis URL-direct** | se l'input è un URL, salta la ricerca | la fonte è già data: cercare è spreco puro |
| **0a KB-check** | fatti stabili (fondazioni, definizioni) → risponde da KB | 0 tool call, 0 caratteri: il risparmio più grande |
| **0b Cache-check** | riusa risultati già in sessione | evita ricerche duplicate — **tranne per le news** (freschezza) |
| **0c Classificazione** | dominio · tipo · lingua · time_range | imposta i parametri giusti: lingua IT garantita, recency controllata |

> Il KB-check **non** si applica a cariche mutabili (CEO, presidente, ministro), prezzi,
> statistiche, o query con segnali temporali: lì serve sempre la ricerca.

---

## 4. Progressive disclosure — il cuore dell'ottimizzazione

La pagina intera è quasi sempre sovradimensionata. La skill legge a livelli crescenti e si
ferma appena ha abbastanza:

| Tipo query | Metodo lettura | Caratteri tipici |
|---|---|---|
| `fact` | nessuna lettura, solo snippet | 0 |
| `recipe` | `readHeadings` → `section` ("Preparazione"…) | ~950 |
| `deep` | `readHeadings` → `section` rilevante | ~1.350 |
| `comparison` | `readHeadings` → 1–2 sezioni | ~2.300 (2 URL) |
| `news` | `paragraphRange:"1-6"` | ~1.500 |
| `legale-it` | `paragraphRange:"1-10"` (no headings) | ~1.500 |

**Perché `readHeadings` → `section` batte la lettura full-page:** la lettura di una pagina
intera è ~9.200 caratteri (70% navigazione/footer); estrarre solo la sezione pertinente la
riduce a ~950–1.350 caratteri → **−84% sul singolo `web_url_read`**.

---

## 5. Routing legale

```
legale-it
├── NORMATIVA (art. X, d.lgs., codici)
│     └── skill Normattiva installata? → usa Normattiva (0 SearXNG)
│         altrimenti → SearXNG IT (Brocardi/Normattiva.it) + avviso installazione
├── GIURISPRUDENZA (sentenze, Cassazione, TAR)
│     └── MCP BuddaLaw disponibile? → chiede all'utente BuddaLaw vs SearXNG
│         altrimenti → SearXNG IT (time_range:year se "ultime")
└── DOTTRINA (commenti, prassi, circolari)
      └── sempre SearXNG IT (Altalex, Diritto.it, Il Sole 24 Ore…)
```

---

## 6. Edge case gestiti (v3)

| # | Caso inusuale | Comportamento |
|---|---|---|
| 1 | URL incollato | salta la ricerca, legge diretto |
| 2 | query multi-dominio (legale + tech) | chiede quale ambito (o usa il primario se chiaro) |
| 3 | heading con sinonimo ("Come si prepara") | match **semantico**, non testuale |
| 4 | pagina con 40+ heading | cap a 20 + filtro keyword |
| 5 | primo URL paywall/consent/vuoto | passa all'URL successivo, 0 nuove ricerche |
| 6 | time_range troppo stretto | allarga prima il filtro temporale, poi la query |
| 7 | seconda news in sessione | niente cache: rifà la ricerca per freschezza |
| 8 | risultato PDF | salta `readHeadings`, usa `paragraphRange` |
| 9 | query in lingua terza (FR/ES/DE) | lingua = quella della query, fonti autodetect |

## 6-bis. Miglioramenti v4 (dal benchmark vs Perplexity Pro)

Estratti misurando la skill contro Perplexity Pro su 12 query (`test/benchmark_pplx_vs_searxng.md`).
Risultato: qualità e ranking **alla pari** con Perplexity (nDCG 0.732 = 0.732, qualità 95% = 95%);
Perplexity **non** è gold standard (Liu et al. 2023: ~51% claim supportati dalle sue citazioni). Le 6
euristiche sotto sono regole statiche interne — **nessuna dipendenza da Perplexity a runtime**.

| # | Euristica | Caso | Comportamento v4 |
|---|---|---|---|
| E1 | chrome al posto del contenuto | news/istituzionali: `1-N` cade nel menu | rileggi con offset (`9-25`) prima di scartare l'URL |
| E2 | sito istituzionale chrome-heavy | garanteprivacy & simili inestraibili | citalo come riferimento, leggi da fonte secondaria (Iubenda, Altalex) |
| E3 | PDF non parsato / paywall | dottrina legale-it | declassa PDF/paywall in lettura, rispondi dagli snippet, max 2 tentativi |
| E4 | `section` match esatto fallisce | heading lungo | passa la **keyword centrale**, non la stringa intera |
| E5 | SEO-blog sopra docs ufficiali | informatica | **boost docs ufficiali** (docs.python.org, MDN) nella lettura — su N04 era il gap più ampio (nDCG_sx 0.572 vs pplx 0.799) |
| E6 | ranking grezzo non autorevole | tutti i domini | **re-rank per autorevolezza** prima di scegliere l'URL (tabella in `search_strategy.md`) |

Punti di forza confermati dal benchmark: cucina IT e news IT (SearXNG batte Perplexity, che usa social/video);
failure onesto (entrambi corretti — Perplexity Pro **non** confabula, ipotesi iniziale smentita);
efficienza-token per uso agentico (output controllabile vs risposte Perplexity 6–9k chars).

---

## 7. Dipendenze

| Dipendenza | Obbligatoria? | Se manca |
|---|---|---|
| MCP **searxng** | ✅ sì | la skill propone WebSearch Claude come fallback (con conferma) |
| MCP **buddalaw** | ⬜ opzionale | giurisprudenza via SearXNG IT, nessun avviso |
| Skill **Normattiva** | ⬜ opzionale | citazioni normative come testo + avviso installazione (1×/sessione) |

Degradazione graziosa: senza gli opzionali la skill funziona comunque, solo con meno
arricchimenti.

---

## 8. Installazione della skill (Claude Code)

> Questa sezione installa **la skill**. Per il **server SearXNG** (prerequisito obbligatorio)
> vedi la sezione 9.

### Metodo 1 — script automatico (consigliato)

```bash
bash ricerca-web-seaXNG/install.sh
```

Lo script: copia la skill in `~/.claude/skills/ricerca-web-searXNG/`, aggiunge **in modo non
distruttivo** il server `searxng` a `~/.mcp.json` (se assente), e stampa i passi finali.
È idempotente: rilanciarlo non duplica nulla.

### Metodo 2 — manuale

1. Copia la cartella della skill:
   ```bash
   mkdir -p ~/.claude/skills
   cp -R ricerca-web-seaXNG/ricerca-web-searXNG ~/.claude/skills/ricerca-web-searXNG
   ```
2. Aggiungi il server MCP SearXNG in `~/.mcp.json` (sotto `mcpServers`):
   ```json
   {
     "mcpServers": {
       "searxng": {
         "command": "npx",
         "args": ["-y", "mcp-searxng"],
         "env": { "SEARXNG_URL": "http://localhost:8080" }
       }
     }
   }
   ```
   Sostituisci `SEARXNG_URL` con l'indirizzo della **tua** istanza SearXNG (vedi sezione 9).
   (Opzionale) per la giurisprudenza aggiungi anche un server `buddalaw` di tipo `http`.

### Metodo 3 — bundle `.skill`

`ricerca-web-searXNG.skill` è uno **zip** della cartella skill, utile per distribuzione:
```bash
unzip ricerca-web-searXNG.skill -d ~/.claude/skills/ricerca-web-searXNG
```

### Verifica

- Riavvia Claude Code (o esegui `/mcp` per far partire il server SearXNG).
- `/doctor` → la skill `ricerca-web-searXNG` deve comparire tra quelle caricate.
- Fai una ricerca: in testa alla risposta deve apparire l'intestazione `[dominio · tipo · …]`.

### Disinstallazione

```bash
rm -rf ~/.claude/skills/ricerca-web-searXNG
```
(e rimuovi il blocco `searxng` da `~/.mcp.json` se non ti serve altrove).

---

## 9. Installare il server SearXNG (macOS Apple Silicon)

La skill richiede un'istanza SearXNG raggiungibile con la **JSON API attiva** (il server MCP
`mcp-searxng` interroga l'endpoint JSON). Di seguito l'installazione via Docker e via OrbStack
su macOS ARM.

> Questa guida è il risultato di un test pratico: due ricerche indipendenti sullo stesso
> argomento (una con WebSearch, una con questa stessa skill) sono state confrontate da un
> terzo agente valutatore su 6 metriche. La versione qui sotto unisce l'efficienza di processo
> della skill con le fonti ufficiali. Dettagli in `test/guide_comparison_report.md`.

### Prerequisiti

- macOS su Apple Silicon (ARM64).
- Un runtime container: **Docker Desktop** *oppure* **OrbStack**. La CLI `docker compose` è
  identica per entrambi — i comandi sotto non cambiano.
- `git` e `openssl` (preinstallati su macOS).

### 9.1 — Via Docker / docker-compose

```bash
# 1. Clona il repository ufficiale
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker

# 2. Prepara il file .env e impostane i valori
cp .env.example .env          # se presente nella tua versione del repo
# Decommenta/imposta SEARXNG_HOSTNAME (default: http://localhost)

# 3. Genera il secret key (sostituisce il placeholder "ultrasecretkey")
#    NB: su macOS sed richiede l'argomento "" dopo -i
sed -i "" "s|ultrasecretkey|$(openssl rand -hex 32)|g" searxng/settings.yml
```

**Abilita la JSON API (obbligatorio per `mcp-searxng`)** — di default SearXNG espone solo
HTML. In `searxng/settings.yml`:

```yaml
search:
  formats:
    - html
    - json        # ← necessario per l'API JSON consumata da mcp-searxng
server:
  limiter: false  # ← il limiter blocca le chiamate API programmatiche (403/429)
```

**Porta 8080** — è quella attesa dalla config di default della skill ed è anche il default del
compose ufficiale (`127.0.0.1:8080:8080`): non serve modificarla. Se la 8080 è già occupata da
un altro servizio, cambia il mapping del servizio `searxng` (es. `"127.0.0.1:8100:8080"`) e
aggiorna di conseguenza `SEARXNG_URL` in `~/.mcp.json`.

**Avvio e gestione** — lo stack comprende tre servizi: `searxng` (l'app), `redis`/`valkey`
(cache in memoria), `caddy` (reverse proxy/TLS, usa la host network per le porte 80/443).

```bash
docker compose up -d      # avvia
docker compose ps         # stato dei servizi
docker compose logs -f    # log
docker compose down       # stop
```

### 9.2 — Via OrbStack (alternativa nativa Apple Silicon)

OrbStack inoltra il socket del proprio engine a macOS: **piena compatibilità** con i workflow
Docker, Compose incluso. La CLI `docker compose` funziona as-is e i file compose **non vanno
modificati**.

```bash
# Dopo aver installato e avviato OrbStack (brew install orbstack):
cd searxng-docker
docker compose up -d
```

Note ARM64:
- OrbStack esegue immagini `linux/arm`, `linux/arm64`, `linux/386`, `linux/amd64` su Apple
  Silicon e Intel.
- L'immagine ufficiale `searxng/searxng` è multi-arch → su ARM gira **nativa**.
- Per immagini solo x86_64, OrbStack usa **Rosetta** automaticamente; con `--platform` puoi
  forzare l'architettura per singolo servizio.

### 9.3 — Verifica della JSON API

```bash
curl 'http://localhost:8080/search?q=test&format=json'
# con jq, controllo rapido che ci siano risultati:
curl -s 'http://localhost:8080/search?q=test&format=json' | jq '.results | length'
```

Risposta sana: JSON con chiave `results` non vuota (il secondo comando stampa un numero > 0).
Se ricevi HTML o un errore 403/429 → la JSON API non è abilitata o il limiter sta bloccando.

### 9.4 — Pitfall comuni su macOS ARM

| Sintomo | Causa | Fix |
|---|---|---|
| `...format=json` ritorna HTML | manca `- json` in `search.formats` | aggiungi e `docker compose restart` |
| 403 / 429 sull'API | `limiter` attivo | `server.limiter: false` |
| conflitto di porta | 8080 già in uso | cambia il mapping nel compose e `SEARXNG_URL` |
| `sed -i` fallisce | macOS usa BSD sed | usa `sed -i "" ...` |

### 9.5 — Collega la skill al tuo server

Assicurati che `SEARXNG_URL` in `~/.mcp.json` punti all'istanza appena avviata
(`http://localhost:8080`, oppure l'IP LAN se il server gira su un'altra macchina).

**Fonti** (documentazione ufficiale):
[searxng-docker repo](https://github.com/searxng/searxng-docker) ·
[settings.yml ufficiale](https://github.com/searxng/searxng-docker/blob/master/searxng/settings.yml) ·
[SearXNG — Installation container](https://docs.searxng.org/admin/installation-docker.html) ·
[SearXNG — Search API](https://docs.searxng.org/dev/search_api.html) ·
[mcp-searxng](https://github.com/ihor-sokoliuk/MCP-searxng) ·
[OrbStack — Docker](https://docs.orbstack.dev/docker/)

---

## 10. Testing

Suite completa: **17 scenari** in [`test/test_cases.md`](../test/test_cases.md)
(9 happy-path S1–S9 + 8 edge case S10–S17). Query fisse riproducibili e procedura in
[`test/test_script_riproducibile.md`](../test/test_script_riproducibile.md).

Ogni scenario specifica: input, comportamento atteso, tool call attesi, criterio pass/fail.

### Test pratico a 3 vie — giudizio cieco, rubrica booleana fondata sulla letteratura

La guida della sezione 9 è stata prodotta confrontando **tre** ricerche reali sullo stesso topic
e valutandole alla **cieca** (guide anonime, ordine randomizzato) con **3 giudici indipendenti**
su una **rubrica booleana** (`test/rubric.md`) ancorata alla letteratura (CRAAP per le fonti;
truth-discovery per la corroborazione dependence-aware; rubriche booleane > Likert; Krippendorff α
per l'accordo — bibliografia in `test/references_literature.md`). Token misurati a parte.

| Metrica (0–10) | MCP grezzo | WebSearch | MCP + skill | α giudici |
|---|---|---|---|---|
| M1 Completezza pesata | 5.0 | **10.0** | **10.0** | 1.000 |
| M2 Accuratezza (v3, validata sui file) | 7.0 | 10.0 | 10.0 | 1.000† |
| M3 Supporto & corroborazione fonti | 7.0 | 6.7 | 4.7 | 0.80 |
| **Totale qualità /30** | 19.0 | **26.7** | 24.7 | |
| Char ingeriti | ~14.580 | ~6.690 | **~5.200** | |
| Qualità / 1000 char | 1.3 | 4.0 | **4.7** | |

**Esito.** *Qualità*: WebSearch e skill **pari** su completezza e accuratezza; WebSearch vince di
poco **solo** su M3 perché citava fonti **indipendenti**, mentre le fonti di terzi della skill
sono state segnalate (dai 3 giudici) come *circular reporting* → fattore correggibile, indipendente
dal tool. *Efficienza*: la skill è la più frugale → **miglior rapporto qualità/token (4.7)**.
*Risultato più solido*: la skill batte il **MCP grezzo** di +5.7 punti con **~1/3 dei token** —
*mai usare il MCP grezzo senza la skill*. <br>*†In v3 M2 ha una regola di eseguibilità letterale:
2 giudici su 3 concordano (α=1.000) e il loro giudizio è confermato dal `grep` sui file; il 3°
giudice ha invertito le etichette ed è stato scartato col controllo oggettivo — il design
multi-giudice ha catturato l'outlier.* Metodologia, α e limiti nel
[report completo](../test/guide_comparison_report.md).

---

## 11. Benchmark — quale strumento per quale query

| Scenario | Strumento migliore | Perché |
|---|---|---|
| Fact stabile (storico) | **KB Claude** | 0 token, istantaneo |
| Comparison EN, doc tecnica | **WebSearch Claude** | leggero (~900c), qualità pari |
| Notizie recenti | **questa skill** | `time_range` garantito (8/10 recenti) |
| Legale IT, GDPR, cucina IT | **questa skill** | lingua IT 100% (WebSearch dà fonti EN) |
| Recipe completa | **questa skill** | `readHeadings`→`section`, −39% vs v1 |
| Query oscura / "0 risultati" | **questa skill** | risposta onesta, niente allucinazioni |
| SearXNG offline | **WebSearch Claude** | fallback esplicito con avviso |

---

*Versione skill: v4 · v3 (progressive disclosure + edge case) + 6 euristiche di lettura/ranking
estratte dal benchmark contro Perplexity Pro (vedi `test/benchmark_pplx_vs_searxng.md`).*
