# Installare un server SearXNG su macOS (Apple Silicon) con JSON API

## Prerequisiti
- macOS su Apple Silicon (ARM64).
- Docker Desktop oppure OrbStack (CLI `docker compose` identica per entrambi).
- `git` e `openssl`.

## 1. Clonare il repository e avviare
Il metodo raccomandato dalla documentazione ufficiale è il compose instancing dal repo
`searxng-docker`.

```bash
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker
```

## 2. Configurazione `.env`
Nel file `.env`: decommenta e imposta `SEARXNG_HOSTNAME` (default `http://localhost`).
`LETSENCRYPT_EMAIL` serve solo se vuoi un certificato TLS pubblico.

## 3. Secret key
Su macOS `sed` è la variante BSD e richiede l'argomento `""` dopo `-i`:

```bash
sed -i "" "s|ultrasecretkey|$(openssl rand -hex 32)|g" searxng/settings.yml
```

## 4. Abilitare la JSON API
La documentazione conferma che di default è attivo solo HTML; va attivato JSON. In
`searxng/settings.yml`:

```yaml
search:
  formats:
    - html
    - json
```

## 5. Rate limiter
```yaml
server:
  limiter: false   # il limiter blocca le chiamate API programmatiche
```

## 6. Impostare la porta 8100
Il compose mappa di default la 8080 su localhost. Per la porta 8100, nel servizio `searxng`:

```yaml
services:
  searxng:
    ports:
      - "127.0.0.1:8100:8080"
```

## 7. Gestione del servizio
```bash
docker compose up -d      # avvia (searxng + redis/valkey + caddy)
docker compose ps         # stato
docker compose logs -f    # log
docker compose down       # stop
```

## 8. OrbStack
OrbStack inoltra il socket del proprio engine a macOS: piena compatibilità con i workflow
Docker, Compose incluso. La CLI `docker compose` funziona as-is, i file compose non vanno
toccati.

```bash
cd searxng-docker
docker compose up -d
```

## 9. Note ARM64 / Apple Silicon
- OrbStack esegue immagini `linux/arm` (32-bit), `linux/arm64` (64-bit), `linux/386`,
  `linux/amd64` su Apple Silicon e Intel.
- `searxng/searxng` è multi-arch → su ARM gira nativa.
- Immagini solo x86_64: OrbStack usa Rosetta automaticamente; con `--platform` si forza
  l'architettura per singolo servizio.

## 10. Verifica della JSON API
```bash
curl 'http://localhost:8100/search?q=test&format=json'
```
Risposta sana: JSON con chiave `results` non vuota. HTML o 403/429 → JSON non abilitato o
limiter attivo.

## 11. Pitfall comuni
| Sintomo | Causa | Fix |
|---|---|---|
| la query JSON ritorna HTML | manca `- json` in `search.formats` | aggiungi e riavvia |
| 403 / 429 sull'API | `limiter` attivo | `server.limiter: false` |
| conflitto di porta | 8080/8100 occupata | cambia mapping nel compose |
| `sed -i` fallisce su macOS | sintassi BSD | `sed -i "" ...` |

## Fonti
- SearXNG Docs — Installation container: https://docs.searxng.org/admin/installation-docker.html
- Guida provider SearXNG (passi clone/.env/compose): https://docs.openwebui.com/features/chat-conversations/web-search/providers/searxng/
- Discussione community: JSON non abilitato di default (r/Searx)
- Conferme incrociate da guide di terzi (Msty, OpenClaw)
