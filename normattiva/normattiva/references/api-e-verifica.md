# Normattiva – API, verifica degli URN e trappole note

Documento tecnico. **Non serve per scrivere un link**: per quello bastano
`SKILL.md` e `lookup-extended.md`. Serve quando devi **verificare** un URN,
recuperare il **testo** di un articolo, o capire perché qualcosa non torna.

Tutte le misure sono state prese il **2026-08-06** con ~500 richieste reali.

---

## 1. L'URN non è un link: è un identificatore con due consumatori

```
                    ┌─→  https://www.normattiva.it/uri-res/N2Ls?<urn>   →  pagina per l'utente
URN ────────────────┤
                    └─→  API dettaglio-atto-urn                          →  testo dell'articolo
```

La skill costruisce **l'URN**. Il link è l'URN con un prefisso davanti. Lo stesso
identificatore alimenta anche l'API, se serve il testo.

**I due consumatori si comportano in modo opposto di fronte a un errore:**

| | Portale (link) | API (testo) |
|---|---|---|
| URN corretto | pagina dell'atto | testo dell'articolo |
| Sintassi non valida (comma, lettera, `~all1`, `~pre`) | 200, pagina **identica** a quella senza | **errore 400** |
| Allegato sbagliato o mancante | 200, mostra il preambolo o una pagina di ripiego | **errore 404** |
| Tipo di atto sbagliato | 200, **la pagina giusta** | 404 |
| Giorno/mese sbagliato | 200, **la pagina giusta** | 404 |
| **Anno sbagliato** | 200, **un atto completamente diverso** | 404 |
| Atto inesistente | 200, pagina «Normattiva - Errore» | 404 «atto non trovato» |
| Stringa senza senso | 200, pagina di errore | — |

### Le due conseguenze che contano

**1. Un URN non si valida cliccandoci sopra.** Il portale risponde con una pagina
praticamente sempre. Due errori sono rimasti nella lookup di questa skill per
mesi proprio per questo: dal browser sembravano funzionare.

**2. L'anno è l'unica parte che non puoi sbagliare.** Il portale risolve per
**anno + numero** e ignora tipo e data:

| URN richiesto | Atto mostrato |
|---|---|
| `legge:1970-05-20;300~art18` | Legge 300/1970 — 121.033 byte |
| `legge:1970-01-01;300~art18` (giorno sbagliato) | la stessa, byte per byte |
| `decreto.legislativo:1970-05-20;300~art18` (tipo sbagliato) | la stessa, byte per byte |
| `legge:1971-05-20;300~art18` (**anno** sbagliato) | **D.P.R. 300/1971** — atto diverso, pagina plausibile, HTTP 200 |

Sbagliare tipo o giorno è invisibile e innocuo. Sbagliare anno produce un link a
una norma diversa che nessuno noterà. In un parere è il danno peggiore possibile.

---

## 2. Recuperare il testo di un articolo

```
POST https://api.normattiva.it/t/normattiva.api/bff-opendata/v1/api/v1/atto/dettaglio-atto-urn
Content-Type: application/json

{"urn": "urn:nir:stato:regio.decreto:1942-03-16;262:2~art1414"}
```

Nessuna chiave, nessuna registrazione. Dati in **CC BY 4.0**. Risposta in ~0,26 s.

Il testo sta in `data.atto.articoloHtml`, in HTML semantico Akoma Ntoso
(`article-num-akn`, `art-comma-div-akn`, `comma-num-akn`).

### Perché non scaricare la pagina del portale

Stesso articolo, art. 2043 c.c.:

| Via | Byte | Testo utile |
|---|---:|---|
| **API** | **1.287** | 180 caratteri: l'articolo |
| Pagina del portale | 2.591.983 | 69.289 caratteri = **tutto il codice civile**, in un blocco unico non segmentabile |

**Fattore 2.013×.** La pagina di un codice non marca i singoli articoli: non c'è
modo affidabile di ritagliarne uno.

---

## 3. Le quattro trappole dell'API

### 3.1 Due forme di risposta

Per alcuni atti `data.atto` è `null` e il contenuto sta in **`data.lista`** (due
elementi: testo originario e ripubblicazione con note). Succede su atti centrali
— **D.Lgs. 36/2023, TUEL, T.U. Edilizia**.

Chi legge solo `data.atto` conclude che quelle voci siano rotte. Non lo sono.

### 3.2 `~art1` restituisce il preambolo

Su almeno 13 atti moderni. La risposta è formalmente valida e il testo è
plausibile: **nessuna avvisaglia.**

| URN | Cosa torna |
|---|---|
| `legge:1970-05-20;300~art1` | «La Camera dei deputati ed il Senato hanno approvato» |
| `decreto.legislativo:2001-06-08;231~art1` | **18.308 caratteri** di «IL PRESIDENTE DELLA REPUBBLICA, Visti…» |
| `decreto.legislativo:2000-08-18;267~art1` | preambolo del TUEL |

**Controllo:** se il testo non comincia con `Art. <numero richiesto>`, non è
l'articolo.

### 3.3 Gli articoli abrogati tornano quasi vuoti

| URN | Caratteri | Con `!vig=` |
|---|---:|---:|
| `917~art51` (T.U.I.R.) | **69** | 23.681 |
| `633~art19` (IVA) | **64** | 11.174 |
| `196~art13` (Privacy) | 64 | 4.771 |

Meno di 200 caratteri con la parola «ABROGATO» **non è una risposta vuota**: è
un'informazione. Rilancia con `!vig=` alla data dei fatti.

### 3.4 Due tipi di 404, distinguibili

| Risposta | Significato | Cosa fare |
|---|---|---|
| ~43 byte, «atto non trovato» | l'atto non esiste | fermarsi |
| ~168 byte con dettagli di debug (`codiceRedazionale`, `idArticolo`) | **l'atto esiste, le coordinate sono sbagliate** | riprovare con un altro allegato |

---

## 4. Grammatica dell'URN accettata dall'API

```
urn:nir:stato:<tipo>:<data>;<numero>[:<allegato>]~art<N>[!vig=AAAA-MM-GG]
```

| Regola | Verifica |
|---|---|
| Solo `~art<N>` e `~art<N>bis` | comma, lettera, `~all`, `~pre`, `~dis` → errore |
| `bis`/`ter` **attaccati** | `~art2645ter` ✅ · `~art2645-ter` ❌ |
| Allegato obbligatorio per i codici storici, vietato per il c.p.p. | c.c. senza `:2` → preambolo; c.p.p. con `:1` → 404 |
| `!vig=AAAA-MM-GG` funziona su tutti i tipi di atto | verificato su Cost., r.d., legge, d.lgs., d.l., d.p.r. |
| `!vig=` **senza data** | errore: per il testo vigente si **omette** il parametro |
| `@originale` | l'API lo **ignora** (risposta identica a senza) |
| Data corta `1942;262:2` | accettata |

---

## 5. La ricerca per parole non serve a trovare articoli

`POST …/ricerca/semplice` con
`{"testoRicerca":"…","orderType":"recente","paginazione":{"paginaCorrente":1,"numeroElementiPerPagina":3}}`

**La paginazione deve essere annidata:** con i campi al livello superiore l'API
risponde con un errore del server, non con un errore di validazione.

Tre limiti che la rendono poco utile:

1. **È a livello di atto, non di articolo.** Non esiste modo di chiedere «l'articolo che parla di X».
2. **La pertinenza è debole.** Su «responsabilità extracontrattuale» il primo risultato è la legge sulla Costituzione europea; su «art. 2043 codice civile» **il codice civile non compare**.
3. **Non restituisce mai l'URN.** Va ricostruito dai campi, e per i **codici è impossibile**: il numero di allegato non compare da nessuna parte.

Nota: `orderType` **non è validato**. Qualunque valore diverso da `"recente"`
cade sul default; scrivere `"rilevanza"` non produce errore e non cambia nulla.

Una cosa buona: quando non trova nulla **lo dice** (`numeroAttiTrovati: 0`).

**Conclusione: per i codici la lookup di questa skill non è una scorciatoia, è
l'unica strada.**

---

## 6. Le note di aggiornamento vanno separate

`articoloHtml` include i blocchi storici di aggiornamento: sull'art. 18 L.
300/1970 sono **3.342 caratteri su 14.503, il 23%** («La L. 11 maggio 1990, n.
108 ha disposto che…»).

Sono cronologia delle modifiche, non norma vigente. Si isolano su
`class="art_aggiornamento-akn"`. **Preziosi da conservare, mai da mescolare al
testo dell'articolo:** un modello che li legge come testo cita come vigente ciò
che è storia.

---

## 7. Affidabilità

| Prova | Esito |
|---|---|
| 30 richieste sequenziali (pausa 200 ms) | 30 × OK, mediana 0,263 s |
| 10 richieste senza pausa | 10 × OK |
| 10 richieste concorrenti | 10 × OK, 0,39 s totali |
| ~500 richieste in un'ora | zero errori, nessun degrado |

Nessun rate limiting osservato. *Ma* `dati.normattiva.it/robots.txt` risponde con
un blocco del sistema di protezione del Poligrafico: un firewall applicativo
esiste nel perimetro anche se non ci ha mai colpiti. Chi costruisce un client
metta comunque backoff e limiti.

---

## 8. Come si verifica una voce della lookup

L'unico controllo che funziona:

1. Interroga `dettaglio-atto-urn` con l'URN da verificare più un **articolo noto**
   (non l'art. 1: vedi §3.2).
2. Estrai il numero d'articolo dall'intestazione del testo restituito.
3. **Confronta con quello richiesto.** Se non coincide, la voce è sbagliata.

Aggiungi sempre dei **casi negativi**: `262~art2043` (senza allegato) e
`327~art409` (senza allegato) *devono* fallire. Se passano, il controllo non
funziona.

**Cosa non usare come controllo:** la lunghezza del testo (cambia a ogni
novella), l'hash della pagina del portale (cambia con l'URN richiesto), il codice
HTTP del portale (è sempre 200), il confronto fra due URN (`~art9999` restituisce
la stessa pagina di `~art1`).

Lo script `tests/test_api_live.py` implementa esattamente questo.

---

## Limiti dichiarati

- L'endpoint è un servizio interno del portale, non un'API pubblica versionata
  con un contratto: **può cambiare senza preavviso**.
- Le prove di carico vengono da un solo indirizzo IP in un'ora: non dicono nulla
  su quote giornaliere o uso continuativo.
- I 13 atti con `~art1` → preambolo sono un campione, non un censimento.
- L'assenza di GDPR, CEDU e codice deontologico forense da Normattiva è
  **dedotta**, non misurata.
