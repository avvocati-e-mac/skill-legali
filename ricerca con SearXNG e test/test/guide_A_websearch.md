# Guida A — Installazione SearXNG su macOS ARM (ricerca via WebSearch)

> Guida generata dai risultati del tool **WebSearch** (Claude built-in).
> Topic: installare il server SearXNG via Docker e via OrbStack su macOS Apple Silicon,
> con JSON API abilitata per il server MCP `mcp-searxng`.

## Prerequisiti

- macOS su Apple Silicon (ARM64).
- Un runtime container: **Docker Desktop** *oppure* **OrbStack**. OrbStack è
  drop-in compatibile con la CLI `docker`/`docker compose`, quindi i comandi sotto
  sono identici per entrambi.
- `git` e `openssl` (preinstallati su macOS).

## 1. Installazione via Docker / docker-compose

```bash
# 1. Clona il repo ufficiale searxng-docker
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker

# 2. Copia il file .env di esempio e impostane i valori
cp .env.example .env   # se presente nella tua versione del repo
# Modifica SEARXNG_HOSTNAME (default http://localhost) nel .env

# 3. Genera il secret key (sostituisce il placeholder "ultrasecretkey")
sed -i "" "s|ultrasecretkey|$(openssl rand -hex 32)|g" searxng/settings.yml
# NB: su macOS sed richiede l'argomento "" dopo -i
```

### Abilitare la JSON API (obbligatorio per mcp-searxng)

Di default SearXNG espone solo l'output HTML. Il server MCP `mcp-searxng` interroga la
**JSON API**, quindi va abilitata. In `searxng/settings.yml`:

```yaml
search:
  safe_search: 0
  formats:
    - html
    - json        # ← necessario per l'API JSON
server:
  limiter: false  # ← evita che il rate-limiter blocchi le richieste API
```

### Porta 8100

Il `docker-compose.yaml` mappa di default `127.0.0.1:8080:8080`. Per usare la porta
**8100** (quella attesa dalla skill), modifica il mapping del servizio `searxng`:

```yaml
services:
  searxng:
    ports:
      - "127.0.0.1:8100:8080"
```

### Avvio

```bash
docker compose up -d
```

I servizi del compose sono tre: **searxng** (l'app), **redis/valkey** (cache in memoria),
**caddy** (reverse proxy / TLS, usa la host network per le porte 80/443).

## 2. Installazione via OrbStack (macOS ARM)

OrbStack è un'alternativa nativa Apple Silicon a Docker Desktop. **Non serve cambiare nulla**
nei comandi: la CLI `docker` e `docker compose` funziona identica, i Dockerfile e i compose
file non vanno modificati.

1. Installa OrbStack (`brew install orbstack` o dal sito) e avvialo.
2. Esegui gli stessi comandi della sezione Docker:
   ```bash
   cd searxng-docker
   docker compose up -d
   ```

### Note ARM64

- OrbStack esegue immagini `linux/arm64`, `linux/amd64`, `linux/arm`, `linux/386` sia su
  Apple Silicon che su Intel.
- L'immagine ufficiale `searxng/searxng` è multi-arch, quindi su ARM gira nativa.
- Se un'immagine fosse solo x86_64, OrbStack usa **Rosetta** per eseguirla con buone
  performance; puoi forzare l'architettura con `--platform`.

## 3. Verifica della JSON API

```bash
curl 'http://localhost:8100/search?q=test&format=json'
```

Una risposta sana è un JSON con una chiave `results` popolata. Se ricevi HTML o un errore
403/429, la JSON API non è abilitata o il limiter sta bloccando (vedi pitfall).

## 4. Pitfall comuni su macOS ARM

| Sintomo | Causa | Fix |
|---|---|---|
| `curl ...format=json` ritorna HTML | `json` non è in `search.formats` | aggiungi `- json` e riavvia |
| 403 / 429 sulla JSON API | `limiter: true` blocca le richieste programmatiche | `server.limiter: false` |
| porta occupata | 8080/8100 già in uso | cambia il mapping nel compose |
| `sed -i` errore | macOS `sed` richiede `-i ""` | usa `sed -i "" ...` |

## Fonti (WebSearch)

- [searxng-docker/settings.yml (master)](https://github.com/searxng/searxng-docker/blob/master/searxng/settings.yml)
- [searxng-docker/docker-compose.yaml](https://github.com/searxng/searxng-docker/blob/master/docker-compose.yaml)
- [SearXNG Docs — Installation container](https://docs.searxng.org/admin/installation-docker.html)
- [SearXNG Docs — Search API](https://docs.searxng.org/dev/search_api.html)
- [mcp-searxng (MCP Server)](https://github.com/ihor-sokoliuk/MCP-searxng)
- [OrbStack Docs — Docker containers](https://docs.orbstack.dev/docker/)
- [SearXNG / Open WebUI provider](https://docs.openwebui.com/features/chat-conversations/web-search/providers/searxng/)
