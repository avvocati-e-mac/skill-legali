# Guida C — Installazione SearXNG su macOS ARM (ricerca via MCP SearXNG GREZZO, senza skill)

> Guida generata usando il MCP SearXNG **senza** la disciplina della skill: cioè
> `searxng_web_search` seguito da `web_url_read` **sull'intera pagina** (nessun
> `readHeadings`, nessun `section`, nessun `maxLength`). È il comportamento "di default"
> del MCP nudo. Stesso topic delle guide A e B.

## Prerequisiti

- macOS Apple Silicon (ARM64).
- Docker Desktop oppure OrbStack.
- `git`, `openssl`.

## 1. Installazione via Docker / docker-compose

Dal repo ufficiale `searxng/searxng-docker` (estratto dalla pagina letta):

```bash
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker
docker compose up        # avvia lo stack; il servizio risponde su http://localhost:8080
```

Lo stack include i servizi `searxng`, `caddy` (reverse proxy) e `redis`/`valkey` (cache).
Il servizio `searxng` espone la porta `8080`:

```yaml
searxng:
  container_name: searxng
  image: docker.io/searxng/searxng:latest
  ports:
    - '8080:8080'
  volumes:
    - ./searxng:/etc/searxng:rw
```

### Abilitare la JSON API

Dopo il primo avvio compare la cartella `searxng/` con `settings.yml`. Per l'uso da parte di
agenti AI serve il formato JSON (di default SearXNG restituisce solo HTML). Modifica
`searxng/settings.yml`:

```yaml
# formats: [html, csv, json, rss]
formats:
  - html
  - json   # <-- aggiungi questo
```

Poi `docker restart searxng`. Verifica aggiungendo `&format=json` alla query.

### Porta 8100

(La pagina letta usa la 8080; per la 8100 va cambiato il mapping `ports` — non esplicitato
nella fonte.)

## 2. OrbStack

(La pagina letta non tratta OrbStack né le note ARM64; "funziona indipendentemente dal
sistema operativo" è l'unico riferimento generico alla portabilità.)

## 3. Verifica

```
GET http://localhost:8080/search?q=<query>&format=json
```
Supporta i parametri `time_range` (day/month/year), `language`, `safesearch`.

## 4. Pitfall

- Se l'agente non riesce a usare SearXNG: probabile JSON non abilitato (vedi sopra).

## Fonti (MCP grezzo)

- [Run n8n and SearXNG Locally with Docker — didof.dev](https://didof.dev/en/blog/setup-n8n-and-searxng-locally/) (pagina letta integralmente)

## Nota sul processo di ricerca (token economy)

- **1** `searxng_web_search` (~1.100 char)
- **1** `web_url_read` **sull'intera pagina** = **~13.500 caratteri** ingeriti, di cui la
  maggior parte irrilevante al topic (setup n8n/Postgres/Gemini, nav, footer, share, promo).
- Il contenuto utile su macOS/OrbStack è **assente** nella pagina letta; per coprirlo
  servirebbero altre letture full-page (ulteriori ~10k char ciascuna).
- **Totale ingerito per questa singola lettura ≈ 13.500 caratteri** — più del doppio
  dell'intera ricerca della Guida B (~6.400 char) per un risultato meno completo.
