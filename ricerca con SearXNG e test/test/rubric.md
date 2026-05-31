# Rubrica di valutazione v3 — Guide installazione SearXNG (macOS ARM)

> Versione 3 = v2 + **regola di disambiguazione "corretto sì/no" in M2** (test di eseguibilità
> letterale), aggiunta per alzare l'accordo tra giudici su M2 (in v2 α=0.43, unico disaccordo).
>
> Parametri **booleani** (conteggio sì/no, poi normalizzato 0–10) anziché Likert
> soggettivo, fondati sulla letteratura (vedi `references_literature.md`):
> - scala booleana > Likert per l'inter-rater agreement (arXiv:2408.09235);
> - fonti valutate con **CRAAP** (Currency/Authority distinti) + **truth discovery** per la
>   corroborazione dependence-aware (Dong/Berti-Équille/Srivastava, VLDB 2009);
> - accordo tra giudici riportato con **Krippendorff's α** (soglia 0.80).
>
> Documento congelato prima della valutazione. Usato dai giudici ciechi. NON contiene
> riferimenti al metodo di ricerca con cui ogni guida è stata prodotta.

Task: *"Guida per installare un server SearXNG self-hosted su macOS Apple Silicon (ARM64) via
Docker e via OrbStack, con la JSON API abilitata per un client programmatico (MCP)."*

3 metriche di qualità (M1–M3), ciascuna 0–10. L'efficienza token è valutata SEPARATAMENTE.

---

## M1 — Completezza pesata (boolean checklist)

Per ogni item: **presente e azionabile in sequenza? sì/no.** (Un item dichiarato "non presente"
o solo nominato senza renderlo eseguibile = NO.) Ogni item ha un **peso per impatto funzionale**.

### Regola di classificazione dei pesi (test oggettivo: "se ometti l'item, server/API funziona?")
- **peso 2 — BLOCCANTE**: senza, il server non parte o l'API MCP non risponde.
- **peso 1 — IMPORTANTE**: richiesto dal task ma con workaround / non blocca l'avvio.
- **peso 0.5 — COSMETICO**: qualità di vita.

### Checklist
| # | Item | Peso | Perché |
|---|---|---|---|
| 1 | `git clone` repo `searxng-docker` | 1 | punto di partenza, ma reperibile |
| 2 | `.env` / `SEARXNG_HOSTNAME` | 1 | configurabile, default esiste |
| 3 | Secret key (sostituzione `ultrasecretkey`) | 2 | senza, instanza insicura/non valida |
| 4 | sed BSD macOS `sed -i ""` | 1 | workaround manuale possibile |
| 5 | `formats:` con `html` + `json` | 2 | senza JSON, l'API MCP non risponde |
| 6 | `server.limiter: false` | 2 | senza, l'API è bloccata (403/429) |
| 7 | Remap porta 8100 (`127.0.0.1:8100:8080`) | 1 | richiesto dal task; workaround = altra porta |
| 8 | Avvio `docker compose up -d` | 2 | senza, niente server |
| 9 | Gestione (`ps`/`logs`/`down`, almeno uno) | 0.5 | qualità di vita |
| 10 | OrbStack utilizzabile (CLI drop-in) | 1 | il task lo chiede; Docker è alternativa |
| 11 | Note ARM64 corrette (multi-arch/Rosetta/`--platform`) | 1 | il task lo chiede; spesso "just works" |
| 12 | Verifica JSON con `curl ...&format=json` | 2 | senza, non sai se l'API funziona davvero |

Σ pesi totali = 16.5. **Punteggio M1 = round( (Σ pesi presenti / 16.5) × 10 )**.

> L'eseguibilità end-to-end NON è una metrica separata: è incorporata nel "azionabile in
> sequenza" di ciascun item (evita il doppio conteggio con la completezza).

---

## M2 — Accuratezza (boolean vs fact-key = ground truth)

Per **ogni fatto della fact-key che la guida menziona**: **affermato correttamente? sì/no.**
**Punteggio M2 = round( (fatti corretti / fatti menzionati) × 10 ).**
(Niente gravità −2/−1: è binario. Le omissioni non contano qui — sono in M1.)

### Regola di disambiguazione "corretto sì/no" (v3 — toglie il giudizio)

Un fatto menzionato conta **NO (errato)** se e solo se, eseguito **alla lettera così come
scritto nella guida**, produce un risultato **diverso** da quello della fact-key. Test operativo
(eseguibilità letterale), non "spirito" o "intenzione":

- **Valore/sintassi/posizione sbagliati che cambiano il comportamento → NO.**
  Esempio risolutivo del disaccordo v2: `formats:` messo a **livello radice** invece che sotto
  `search:` → SearXNG **non** abilita la JSON API (la chiave radice è ignorata) → comportamento
  diverso dalla fact-key → **NO (errato)**, anche se l'intento era giusto.
- **Valore/sintassi/posizione corretti ma formulazione incompleta** (manca un dettaglio non
  necessario all'esecuzione) → **SÌ** (l'omissione del dettaglio è materia di M1, non di M2).
- **Fatto menzionato solo parzialmente** (es. cita la porta di default 8080 ma non il remap):
  la *parte affermata* è valutata per ciò che è; se la parte affermata è corretta → **SÌ**; il
  remap mancante è un'omissione → M1.

Regola pratica per il giudice: chiediti *"se copio-incollo esattamente questo, ottengo il
risultato della fact-key?"*. Sì → corretto. No → errato. Niente vie di mezzo.

### Fact-key (assunzione di riferimento, contestabile — base: requisiti reali server+API)
1. Repo ufficiale: `https://github.com/searxng/searxng-docker`
2. macOS = BSD sed → `sed -i "" '...'` (NON `sed -i '...'`)
3. Secret key: `openssl rand -hex 32` sostituisce `ultrasecretkey` in `searxng/settings.yml`
4. JSON API: sotto `search:`, `formats:` include `- json` (oltre a `html`)
5. Client programmatici: `server.limiter: false` evita 403/429
6. Porta: default 8080; per 8100 → `"127.0.0.1:8100:8080"` nel servizio `searxng`
7. OrbStack: CLI `docker`/`docker compose` as-is; compose non va modificato
8. ARM64: `searxng/searxng` multi-arch (nativa su Apple Silicon); x86 → Rosetta; `--platform` per forzare
9. Verifica: `curl 'http://localhost:8100/search?q=test&format=json'` → JSON con `results`

---

## M3 — Supporto & corroborazione delle fonti (CRAAP-derivata, dependence-aware)

NON conta se la fonte è "ufficiale". Per ogni **fatto-chiave** (= un fatto della fact-key) che
la guida presenta, valuta tre booleani:

- **(a) Supportato** — la guida cita almeno una fonte che afferma quel fatto e non lo
  contraddice. (sì/no)
- **(b) Corroborato** — il fatto è confermato da **≥2 fonti indipendenti**, cioè che non
  derivano visibilmente l'una dall'altra. (sì/no)
- **(c) Attuale (Currency)** — la/le fonte/i si riferiscono a versione/contesto corrente, non a
  materiale palesemente datato o relativo ad altro stack. (sì/no)

**Punteggio M3 = round( media( %a, %b, %c ) × 10 )** sui fatti-chiave presenti.

### Regole dependence-aware (dalla letteratura truth-discovery)
- **Circular reporting**: 5 pagine che ripetono lo stesso `settings.yml` copiandolo dalla stessa
  origine = **1** fonte indipendente → NON conta come "corroborato".
- **Minoranza-corretta ammessa**: una guida con **una sola** fonte corretta prende comunque (a)
  Supportato e (c) Attuale se applicabili; semplicemente non prende il bonus (b) Corroborato.
  Non penalizzare la singola fonte giusta — la maggioranza non è prova di verità.
- Indipendenza giudicata leggendo le fonti citate; in dubbio, considera **dipendenti** (prudenza).

---

## Efficienza (NON entra nei punteggi M — classifica separata)
Misurata oggettivamente in `token_efficiency.md` (caratteri ingeriti). Riportata come classifica
a sé + indice qualità/token descrittivo.

---

## Output richiesto a ciascun giudice
Per ogni guida (guide_1/2/3) e metrica:
- **M1**: tabella item × (sì/no) con i pesi, somma pesi presenti / 16.5, punteggio.
- **M2**: per ogni fatto-key menzionato, corretto sì/no; rapporto e punteggio.
- **M3**: per ogni fatto-key presente, i tre booleani (a/b/c); le tre percentuali e il punteggio;
  segnala esplicitamente i casi di sospetto circular reporting.
- Tabella riepilogo (guida × M1/M2/M3), **totale /30**, e classifica con 2-3 frasi.
- **Non** speculare su come la guida sia stata prodotta: valuta solo il testo.
