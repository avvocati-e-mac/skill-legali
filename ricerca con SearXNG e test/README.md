# Ricerca web con SearXNG — Guida per avvocati

Questa skill dà a Claude la capacità di **cercare su internet** in modo **gratuito e privato**,
usando un piccolo motore di ricerca che installi tu sul tuo Mac: **SearXNG**.

> **Perché esiste questa skill**
> È pensata per chi **non ha un abbonamento a Perplexity** (o non vuole pagarne uno).
> Ti dà la stessa cosa essenziale — far cercare Claude su internet e farti rispondere con le
> fonti — senza costi mensili e senza che le tue ricerche finiscano tracciate da servizi esterni.
> Funziona particolarmente bene sulle ricerche in **italiano** e su quelle **legali**.

> **A chi è rivolta questa guida**
> A colleghi avvocati che non si occupano di informatica. I passaggi sono spiegati uno per uno.
> Se un termine tecnico compare per la prima volta, lo trovi spiegato lì accanto. Servono circa
> 20–30 minuti la prima volta; dopo, tutto parte da solo.

> Cerchi i dettagli tecnici, i numeri dei benchmark e le scelte di progetto? Sono nel
> [README tecnico](./ricerca-web-seaXNG/README.md). Questa pagina è la guida pratica.

---

## 1. Come funziona, a grandi linee

Quando fai una domanda a Claude, dietro le quinte succede questo:

![Schema a blocchi: tu chiedi, Claude cerca su SearXNG, ti risponde con le fonti](immagini/01-schema.png)

```
  Tu chiedi  ──▶  Claude  ──▶  server MCP  ──▶  SearXNG  ──▶  internet
                                                                  │
  Risposta con le fonti  ◀───────────────────────────────────────┘
```

Due parole tecniche, spiegate semplici:

- **SearXNG** è un *metamotore di ricerca*: invece di avere un suo indice, interroga
  contemporaneamente Google, Bing, DuckDuckGo e altri, e ti mette insieme i risultati — **senza
  tracciarti** e senza pubblicità. È gratuito e open source. Lo fai girare sul tuo Mac, quindi
  le ricerche restano tue.
- Un **server MCP** è un piccolo "ponte" che permette a Claude di parlare con un programma
  esterno. Qui il ponte collega Claude al tuo SearXNG. (MCP sta per *Model Context Protocol*:
  è lo standard che Claude usa per collegarsi a strumenti esterni.)

In pratica installerai **tre cose**: il motore SearXNG, il ponte MCP, e la skill (le istruzioni
che insegnano a Claude *come* cercare bene). Le vediamo una alla volta.

---

## 2. Cosa ti serve (prerequisiti)

Prima di iniziare, assicurati di avere:

- [ ] Un **Mac con chip Apple Silicon** (M1, M2, M3, M4…). La guida è pensata per questi.
- [ ] Un **"runtime container"** — un programma che fa girare SearXNG in modo isolato e pulito.
      Puoi usare **Docker Desktop** *oppure* **OrbStack** (ne basta uno: lo installiamo al Passo 1).
      *Un "container" è come una scatola che contiene un programma con tutto ciò che gli serve:
      lo avvii e lo spegni senza sporcare il resto del Mac.*
- [ ] **Node.js** installato (serve al ponte MCP). Si scarica da [nodejs.org](https://nodejs.org) —
      scegli la versione "LTS" e installa con doppio clic.
- [ ] **Claude Code** installato e funzionante (l'app da terminale di Claude).

Tutti i comandi di questa guida si scrivono nel **Terminale** del Mac (lo trovi in
*Applicazioni → Utility → Terminale*, oppure cercalo con Spotlight ⌘+Spazio scrivendo "Terminale").

---

## 3. Passo 1 — Installa il runtime container

Scegli **uno** dei due. Su Apple Silicon **OrbStack** è consigliato: è più leggero e nativo.

### Opzione A — OrbStack (consigliata)

1. Vai su [orbstack.dev](https://orbstack.dev) e scarica l'app (oppure, se usi Homebrew, da
   Terminale: `brew install orbstack`).
2. Apri OrbStack e lascialo avviato.

![OrbStack avviato](immagini/03-orbstack.png)

### Opzione B — Docker Desktop

1. Vai su [docker.com](https://www.docker.com/products/docker-desktop/) e scarica Docker Desktop
   per **Apple Silicon**.
2. Installa con doppio clic, apri l'app e attendi che l'icona della balena indichi "running".

![Docker Desktop avviato](immagini/02-docker.png)

> **Da qui in poi i comandi sono identici** per OrbStack e per Docker Desktop. Useremo sempre
> `docker compose`: funziona allo stesso modo con entrambi, non devi cambiare nulla.

---

## 4. Passo 2 — Crea il server SearXNG

### 4.1 Crea la cartella e il file di avvio

Nel Terminale, crea una cartella che ospiterà SearXNG:

```bash
mkdir -p ~/searxng
cd ~/searxng
```

Dentro questa cartella crea un file chiamato `docker-compose.yml` (è il file che dice al Mac
*cosa* avviare). Per crearlo e aprirlo con l'editor TextEdit:

```bash
touch docker-compose.yml
open -e docker-compose.yml
```

Incolla dentro **esattamente** questo contenuto, poi salva (⌘+S) e chiudi:

```yaml
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    ports:
      - "8080:8080"
    volumes:
      - ./searxng:/etc/searxng
    environment:
      - BASE_URL=http://localhost:8080/
    restart: always
```

Cosa dice, in breve: «avvia SearXNG, rendilo raggiungibile sul tuo Mac all'indirizzo
`localhost:8080`, salva la sua configurazione nella sottocartella `searxng`, e riavvialo da solo
se si spegne».

> **Perché la porta 8080?** È quella standard di SearXNG. Se la 8080 fosse già occupata da un
> altro tuo programma, cambia **entrambi** i numeri a sinistra dei due punti (es. `"8100:8080"`)
> e ricordati questo numero: dovrai usarlo anche al Passo 3.

### 4.2 Primo avvio (genera la configurazione)

Sempre dalla cartella `~/searxng`, avvia:

```bash
docker compose up -d
```

Il primo avvio scarica SearXNG e crea il file di configurazione
`~/searxng/searxng/settings.yml`. Aspetta una decina di secondi.

### 4.3 Modifica chiave: attiva la lettura per Claude

Questo è il passaggio **più importante** e quello che di solito manca nelle guide. Di default
SearXNG mostra i risultati solo come pagina web, che Claude non sa leggere. Dobbiamo dirgli di
fornire i risultati anche in **formato JSON** (un formato che i programmi capiscono).

Apri il file di configurazione:

```bash
open -e ~/searxng/searxng/settings.yml
```

Trova la sezione `search:` e fai in modo che includa `json` tra i formati. Trova poi la sezione
`server:` e imposta `limiter: false`. Le due parti devono risultare così:

```yaml
search:
  formats:
    - html
    - json        # ← senza questa riga, Claude non può leggere i risultati

server:
  limiter: false  # ← il "limiter" blocca le richieste automatiche: va spento
```

*Perché:* la riga `json` permette a Claude di leggere i risultati; `limiter: false` evita che
SearXNG scambi le richieste di Claude per traffico sospetto e le blocchi.

![Il file settings.yml con le righe json e limiter evidenziate](immagini/04-settings-json.png)

Salva (⌘+S) e riavvia SearXNG perché prenda le modifiche:

```bash
docker compose restart
```

### 4.4 Verifica che funzioni

Apri nel browser **[http://localhost:8080](http://localhost:8080)**: deve comparire la pagina di
ricerca di SearXNG.

![SearXNG aperto nel browser](immagini/05-searxng-browser.png)

Poi, dal Terminale, controlla che il formato JSON sia attivo:

```bash
curl -s 'http://localhost:8080/search?q=test&format=json' | head -c 200
```

Se vedi del testo che inizia con `{` e contiene `results`, è tutto a posto. Se invece compare
codice di una pagina web (`<!DOCTYPE html>`) o un errore, rivedi il Passo 4.3 (la riga `json`)
— vedi anche la sezione **Problemi frequenti**.

### 4.5 Comandi utili (da `~/searxng`)

| Comando | Cosa fa |
|---|---|
| `docker compose up -d` | avvia SearXNG (in sottofondo) |
| `docker compose down` | lo ferma |
| `docker compose restart` | lo riavvia (dopo aver cambiato la configurazione) |
| `docker compose logs -f` | mostra cosa sta facendo (premi `Ctrl+C` per uscire) |

> **Per chi vuole di più (avanzato):** se ti serve un'installazione "da produzione" con HTTPS e
> nome di dominio, esiste il repository ufficiale
> [searxng-docker](https://github.com/searxng/searxng-docker). I dettagli sono nella sezione 9
> del [README tecnico](./ricerca-web-seaXNG/README.md). Per l'uso con Claude sul tuo Mac, la
> configurazione semplice qui sopra è sufficiente.

---

## 5. Passo 3 — Installa la skill e il ponte MCP

Ora colleghiamo Claude al SearXNG appena avviato.

### Metodo automatico (consigliato)

Dalla cartella di questo progetto, esegui:

```bash
bash "ricerca con SearXNG e test/ricerca-web-seaXNG/install.sh"
```

Lo script fa tutto da solo: copia la skill al posto giusto e aggiunge il ponte MCP `searxng` al
file `~/.mcp.json` **senza cancellare** le tue altre configurazioni. Puoi rilanciarlo senza
rischi: non duplica nulla.

### Metodo manuale

Se preferisci farlo a mano:

1. Copia la cartella della skill:
   ```bash
   mkdir -p ~/.claude/skills
   cp -R "ricerca con SearXNG e test/ricerca-web-seaXNG/ricerca-web-searXNG" ~/.claude/skills/ricerca-web-searXNG
   ```
2. Apri (o crea) il file `~/.mcp.json` e aggiungi il blocco `searxng` sotto `mcpServers`:
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

![Il file ~/.mcp.json con il blocco searxng](immagini/06-mcpjson.png)

> **Importante:** il numero di porta in `SEARXNG_URL` deve **combaciare** con quello scelto al
> Passo 2 (di default `8080`). Se al Passo 2 hai cambiato porta, cambiala anche qui.

### Claude Desktop / claude.ai (solo la skill)

Se usi **Claude Desktop** o **claude.ai**, puoi installare la sola skill scaricando il file
**[`ricerca-web-searXNG.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/ricerca%20con%20SearXNG%20e%20test/ricerca-web-searXNG.skill)**
e trascinandolo nella finestra di Claude.

> **Attenzione:** la skill da sola insegna a Claude *come* cercare, ma per cercare davvero
> servono comunque il **motore SearXNG** (Passo 2) e il **ponte MCP** già avviati. Su Claude
> Desktop il ponte MCP va configurato a parte.

---

## 6. Passo 4 — Verifica dentro Claude

1. Riavvia Claude Code (oppure scrivi `/mcp` per far partire il ponte SearXNG).
2. Scrivi `/doctor`: tra le skill caricate deve comparire `ricerca-web-searXNG`.
3. Fai una ricerca di prova, ad esempio: *«cerca le ultime notizie sul processo telematico»*.
   In testa alla risposta deve apparire una riga tra parentesi quadre come
   `[legale-it/dottrina · news · 7 fonti · it · …]`: è il "biglietto da visita" della skill, ti
   dice come ha cercato.

![Claude esegue una ricerca con l'intestazione tra parentesi quadre](immagini/07-claude-ricerca.png)

Se vedi quella riga e le fonti cliccabili, **funziona tutto**.

---

## 7. Come si usa, in pratica

Non devi imparare comandi: scrivi a Claude in italiano normale. Esempi:

- *«cerca la dottrina recente sulla responsabilità medica»* → cerca su fonti giuridiche italiane
  (Altalex, Il Sole 24 Ore Diritto, Diritto.it…) e cita i link.
- *«ultime notizie sul codice degli appalti»* → cerca solo tra i risultati recenti.
- *«riassumi questa pagina: <indirizzo del sito>»* → legge direttamente quel sito, senza cercare.

**Routing legale automatico** — per le domande di diritto italiano la skill sceglie da sola lo
strumento migliore:

| Tipo di domanda | Strumento usato |
|---|---|
| Articoli di legge (art. X c.c., d.lgs. …) | la skill **Normattiva** (se installata) → link cliccabili |
| Sentenze (Cassazione, TAR…) | il servizio **BuddaLaw** (se disponibile) |
| Dottrina, commenti, prassi | **SearXNG** (questa skill) |

### SearXNG o Perplexity?

| | **SearXNG** (questa skill) | **Perplexity** |
|---|---|---|
| Costo | **gratuito** | abbonamento a pagamento |
| Privacy | ricerche sul tuo Mac, non tracciate | servizio esterno |
| Italiano e diritto IT | molto curato | buono |
| Setup | una volta sola (questa guida) | immediato |

SearXNG è nata proprio per darti la ricerca web **senza pagare un abbonamento**. Se però hai già
Perplexity e vuoi usarlo con Claude, esiste una skill separata (**non** fa parte di questo
progetto): la trovi nel repository
[perplexity-web-mcp](https://github.com/jacob-bd/perplexity-web-mcp). Non è necessaria: la skill
SearXNG funziona da sola, senza dipendere da Perplexity.

---

## 8. Problemi frequenti

| Sintomo | Causa probabile | Soluzione |
|---|---|---|
| `format=json` restituisce una pagina web | manca la riga `json` nei formati | aggiungila in `settings.yml` (Passo 4.3) e `docker compose restart` |
| Errore `403` o `429` sulle ricerche | il `limiter` è attivo | metti `limiter: false` in `settings.yml` e riavvia |
| `localhost:8080` non si apre | la porta 8080 è già occupata | cambia porta nel `docker-compose.yml` **e** in `~/.mcp.json` |
| Comandi `docker` "non trovati" | Docker/OrbStack non è avviato | apri l'app del runtime e riprova |
| Il ponte MCP non parte | manca **Node.js** | installalo da [nodejs.org](https://nodejs.org) e riavvia Claude |
| La skill non compare in `/doctor` | non è stata copiata in `~/.claude/skills` | rilancia `install.sh` o rifai il Metodo manuale |

---

## 9. La cartella `test/` (solo per sviluppatori)

> **Questa parte non serve all'avvocato che vuole solo usare la skill.** È per chi sviluppa o
> vuole verificare la qualità della skill. Puoi saltarla tranquillamente.

La cartella `test/` contiene il "lavoro dietro le quinte" che dimostra che la skill funziona bene:

- una **suite di prove riproducibili** (17 scenari di ricerca con il risultato atteso);
- i **benchmark** che confrontano questa skill con la ricerca "grezza" e con Perplexity, valutati
  alla cieca da più giudici indipendenti su una griglia di criteri;
- i **dati grezzi** delle prove (cartelle `searxng_raw/`, `perplexity_raw/`) e alcuni **script
  Python** che calcolano i punteggi.

In sintesi serve a documentare, con numeri verificabili, che la skill ottiene risultati di
qualità pari o superiore consumando molte meno risorse. I risultati completi sono commentati nel
[README tecnico](./ricerca-web-seaXNG/README.md).

---

## 10. Approfondimenti

- [Ricerche giuridiche online con IA? Iniziano ad essere possibili](https://avvocati-e-mac.it/blog/2025/4/2/ricerche-giuridiche-online-con-ia-iniziano-ad-essere-possibili)
  — l'articolo su *Avvocati e Mac* che racconta la scoperta di SearXNG per le ricerche legali con l'IA.
- [README tecnico della skill](./ricerca-web-seaXNG/README.md) — architettura, benchmark e scelte di progetto.
- [Documentazione ufficiale di SearXNG](https://docs.searxng.org) e repository
  [searxng-docker](https://github.com/searxng/searxng-docker) (installazione avanzata con HTTPS).
- [Ponte MCP per SearXNG (`mcp-searxng`)](https://github.com/ihor-sokoliuk/MCP-searxng).
- [OrbStack](https://orbstack.dev) · [Docker Desktop](https://www.docker.com/products/docker-desktop/).
