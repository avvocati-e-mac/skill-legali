# Installare un server SearXNG su macOS (Apple Silicon) con JSON API

## Prerequisiti
- macOS su Apple Silicon (ARM64).
- Un runtime container: Docker Desktop *oppure* OrbStack (CLI `docker compose` identica).
- `git` e `openssl` (preinstallati su macOS).

## 1. Clonare il repository e avviare
```bash
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker
```

## 2. Configurazione `.env`
```bash
cp .env.example .env    # se presente nella tua versione del repo
```
Imposta `SEARXNG_HOSTNAME` (default `http://localhost`).

## 3. Secret key
Sostituisci il placeholder `ultrasecretkey` con una chiave casuale. Su macOS `sed` è la
variante BSD, quindi richiede l'argomento `""` dopo `-i`:

```bash
sed -i "" "s|ultrasecretkey|$(openssl rand -hex 32)|g" searxng/settings.yml
```

## 4. Abilitare la JSON API
Di default SearXNG espone solo HTML; per l'uso programmatico serve il formato JSON. In
`searxng/settings.yml`:

```yaml
search:
  formats:
    - html
    - json
```

## 5. Rate limiter
Il limiter blocca le richieste programmatiche (403/429). Disattivalo:

```yaml
server:
  limiter: false
```

## 6. Impostare la porta 8100
Il compose mappa di default `127.0.0.1:8080:8080`. Per esporre la porta 8100, nel servizio
`searxng`:

```yaml
services:
  searxng:
    ports:
      - "127.0.0.1:8100:8080"
```

## 7. Gestione del servizio
```bash
docker compose up -d
```
Lo stack comprende `searxng` (app), `redis`/`valkey` (cache), `caddy` (reverse proxy / TLS,
usa la host network per le porte 80/443).

## 8. OrbStack
OrbStack è un'alternativa nativa Apple Silicon a Docker Desktop. **Non serve cambiare nulla**:
la CLI `docker` e `docker compose` funziona identica, i file compose non vanno modificati.

```bash
cd searxng-docker
docker compose up -d
```

## 9. Note ARM64 / Apple Silicon
- OrbStack esegue immagini `linux/arm`, `linux/arm64`, `linux/386`, `linux/amd64` su Apple
  Silicon e Intel.
- L'immagine ufficiale `searxng/searxng` è multi-arch → su ARM gira nativa.
- Per immagini solo x86_64, OrbStack usa Rosetta automaticamente; con `--platform` puoi forzare
  l'architettura.

## 10. Verifica della JSON API
```bash
curl 'http://localhost:8100/search?q=test&format=json'
```
Una risposta sana è un JSON con chiave `results` popolata. HTML o 403/429 → JSON non abilitato
o limiter attivo.

## 11. Pitfall comuni
| Sintomo | Causa | Fix |
|---|---|---|
| `...format=json` ritorna HTML | manca `- json` in `search.formats` | aggiungi e riavvia |
| 403 / 429 sull'API | `limiter` attivo | `server.limiter: false` |
| porta occupata | 8080/8100 in uso | cambia il mapping nel compose |
| `sed -i` errore | macOS usa BSD sed | usa `sed -i "" ...` |

## Fonti
- searxng-docker (repo ufficiale): https://github.com/searxng/searxng-docker
- settings.yml ufficiale: https://github.com/searxng/searxng-docker/blob/master/searxng/settings.yml
- SearXNG Docs — Installation container: https://docs.searxng.org/admin/installation-docker.html
- SearXNG Docs — Search API: https://docs.searxng.org/dev/search_api.html
- OrbStack Docs — Docker: https://docs.orbstack.dev/docker/
