# Installare un server SearXNG su macOS (Apple Silicon) con JSON API

## Prerequisiti
- macOS su Apple Silicon (ARM64).
- Docker installato.

## 1. Clonare il repository e avviare
SearXNG fornisce un repository con un `docker-compose.yml` pronto.

```bash
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker
docker compose up        # il servizio risponde su http://localhost:8080
```

Lo stack comprende i servizi `searxng`, `caddy` (reverse proxy) e `redis`/`valkey` (cache).
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

## 2. Configurazione `.env`
Lo stack legge alcune variabili (es. `SEARXNG_HOSTNAME`, con default `http://localhost:8080`)
dal file di ambiente / dal compose. Personalizzale secondo necessità.

## 3. Secret key
Non presente nel materiale reperito.

## 4. Abilitare la JSON API
Dopo il primo avvio compare la cartella `searxng/` con `settings.yml`. Di default SearXNG
restituisce solo HTML; per l'uso programmatico serve il formato JSON. Modifica
`searxng/settings.yml`:

```yaml
# formats: [html, csv, json, rss]
formats:
  - html
  - json   # <-- aggiungi questo
```

Poi riavvia: `docker restart searxng`.

## 5. Rate limiter
Non presente nel materiale reperito.

## 6. Impostare la porta 8100
Non presente nel materiale reperito (il setup usa la porta 8080).

## 7. Gestione del servizio
- Avvio: `docker compose up`
- Spegnimento: `docker compose down`

## 8. OrbStack
Non presente nel materiale reperito.

## 9. Note ARM64 / Apple Silicon
Non presenti nel materiale reperito (la guida indica genericamente che "funziona
indipendentemente dal sistema operativo").

## 10. Verifica della JSON API
L'endpoint di ricerca è `GET /search` con parametro `q`. Aggiungendo `&format=json` la
risposta è in JSON. Sono supportati anche `time_range` (day/month/year), `language`,
`safesearch`.

```
http://localhost:8080/search?q=test&format=json
```

## 11. Pitfall comuni
- Se un client non riesce a usare SearXNG, la causa più probabile è il formato JSON non
  abilitato (vedi punto 4).

## Fonti
- Tutorial "Run n8n and SearXNG Locally with Docker" (blog di terzi, focalizzato su un setup
  n8n + SearXNG): https://didof.dev/en/blog/setup-n8n-and-searxng-locally/
