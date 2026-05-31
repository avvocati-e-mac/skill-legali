# Guida B — Installazione SearXNG su macOS ARM (ricerca via SearXNG MCP + skill)

> Guida generata dai risultati del MCP **SearXNG** seguendo la disciplina di progressive
> disclosure della skill `ricerca-web-searXNG` (search → readHeadings → section, con
> fallback e skip su pagine inutili).
> Topic: installare il server SearXNG via Docker e via OrbStack su macOS Apple Silicon,
> con JSON API abilitata per il server MCP `mcp-searxng`.

## Prerequisiti

- macOS su Apple Silicon (ARM64).
- **Docker Desktop** oppure **OrbStack** (CLI `docker compose` identica per entrambi).
- `git` e `openssl`.

## 1. Installazione via Docker / docker-compose

Il metodo raccomandato dalla documentazione ufficiale è il **compose instancing** dal repo
`searxng-docker`.

```bash
# 1. Clona il repository ufficiale
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker

# 2. Modifica il file .env: decommenta SEARXNG_HOSTNAME e impostalo
#    (default: http://localhost). LETSENCRYPT_EMAIL solo se vuoi TLS pubblico.

# 3. Genera il secret key
sed -i "" "s|ultrasecretkey|$(openssl rand -hex 32)|g" searxng/settings.yml
```

### Abilitare la JSON API (richiesto da mcp-searxng)

La documentazione e più fonti confermano: di default è attivo **solo HTML**, va attivato
il formato JSON. In `searxng/settings.yml`:

```yaml
search:
  formats:
    - html
    - json        # abilita l'API JSON consumata da mcp-searxng
server:
  limiter: false  # il limiter blocca le chiamate API programmatiche
```

### Porta 8100

Il compose mappa di default la 8080 su localhost. Per la porta **8100** usata dalla skill,
nel servizio `searxng`:

```yaml
services:
  searxng:
    ports:
      - "127.0.0.1:8100:8080"
```

### Avvio e gestione

```bash
docker compose up -d      # avvia lo stack (searxng + redis/valkey + caddy)
docker compose logs -f    # log
docker compose down       # stop
```

## 2. Installazione via OrbStack (macOS ARM)

OrbStack inoltra il socket del proprio engine a macOS: **piena compatibilità** con i
workflow Docker esistenti, Docker Compose incluso. La CLI `docker compose` funziona
as-is, i file compose non vanno toccati.

```bash
# Dopo aver installato e avviato OrbStack:
cd searxng-docker
docker compose up -d
```

### Note ARM64

- OrbStack esegue immagini `linux/arm` (32-bit), `linux/arm64` (64-bit), `linux/386`,
  `linux/amd64` su Apple Silicon e Intel.
- `searxng/searxng` è multi-arch → su ARM gira nativa.
- Immagini solo x86_64: OrbStack usa **Rosetta** automaticamente; con `--platform` puoi
  forzare l'architettura per singolo servizio.

## 3. Verifica della JSON API

```bash
curl 'http://localhost:8100/search?q=test&format=json'
```

Risposta sana: JSON con chiave `results` non vuota. HTML o 403/429 → JSON non abilitato o
limiter attivo.

## 4. Pitfall comuni su macOS ARM

| Sintomo | Causa | Fix |
|---|---|---|
| la query JSON ritorna HTML | manca `- json` in `search.formats` | aggiungi e riavvia |
| 403 / 429 sull'API | `limiter` attivo | `server.limiter: false` |
| conflitto di porta | 8080/8100 occupata | cambia mapping nel compose |
| `sed -i` fallisce su macOS | sintassi BSD | `sed -i "" ...` |

## Fonti (SearXNG MCP)

- [SearXNG Docs — Installation container](https://docs.searxng.org/admin/installation-docker.html)
- [SearXNG / Open WebUI provider (step-by-step clone/.env/compose)](https://docs.openwebui.com/features/chat-conversations/web-search/providers/searxng/)
- [Reddit r/Searx — JSON non abilitato di default](https://www.reddit.com/r/Searx/comments/1ed34ml/)
- conferme incrociate: Msty AI guide, OpenClaw SearXNG setup

## Nota sul processo di ricerca (token efficiency)

- **1** `searxng_web_search` (~1.100 char di lista risultati)
- **5** `web_url_read`: 2 `readHeadings` + 3 letture mirate (`section`/`paragraphRange`)
- Una `section` è risultata povera → fallback a `paragraphRange`; una pagina era nav/JS →
  **skip alla fonte successiva** (regola di resilienza della skill).
- **Totale contenuto ingerito ≈ 6.400 caratteri.**
