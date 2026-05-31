# Skill legali per Claude

Raccolta di **skill** per Claude utili nella pratica e nello studio dell'avvocato italiano.  
Ogni skill insegna a Claude comportamenti specifici — come generare automaticamente link alle norme, cercare giurisprudenza, fare ricerche sul web in modo riservato o trascrivere registrazioni — pensati per il lavoro quotidiano di chi fa l'avvocato.

> **A chi è rivolto questo repository**  
> Queste istruzioni sono scritte per avvocati che non hanno familiarità con la programmazione. Niente paura: installare una skill richiede solo pochi clic.

---

## Skill disponibili

| Skill | Descrizione | Scarica |
|-------|-------------|---------|
| [**normattiva**](./normattiva/) | Genera link ipertestuali cliccabili verso [Normattiva.it](https://www.normattiva.it) per ogni riferimento normativo italiano citato nel testo (art. X c.c., d.lgs., legge n., r.d., ecc.), usando il formato standard URN-NIR. Claude non produce mai riferimenti normativi "nudi": ogni citazione diventa automaticamente un link verificabile. | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/normattiva/normattiva.skill) |
| [**BuddaLaw**](./buddalaw/) | Ricerca live di sentenze (Cassazione, merito, TAR, CGT, Garante Privacy), normativa e prassi tributaria tramite il server MCP [BuddaLaw](https://buddalaw.it) *(banca dati a pagamento, con sistema a crediti)*. Claude non cita mai sentenze dalla memoria interna: ogni riferimento giurisprudenziale proviene da ricerca live con link verificabile. Include workflow per contratti (3 step) e atti processuali (2 step), con ordine obbligatorio per la prassi tributaria. | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/buddalaw/buddalaw.skill) |
| [**ricerca web (SearXNG)**](./ricerca%20con%20SearXNG%20e%20test/) | Ricerca su internet **gratuita e privata** per Claude, tramite un motore [SearXNG](https://docs.searxng.org) che installi sul tuo computer — l'alternativa per chi **non ha un abbonamento Perplexity**. Cura particolarmente le ricerche in italiano e quelle legali, con instradamento automatico verso Normattiva (norme), BuddaLaw (sentenze) e fonti di dottrina. La [guida passo-passo](./ricerca%20con%20SearXNG%20e%20test/README.md) spiega come creare il server SearXNG (Docker/OrbStack) e collegarlo a Claude. | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/ricerca%20con%20SearXNG%20e%20test/ricerca-web-searXNG.skill) |
| [**trascrizione audio**](./trascrizione%20audio/) | Trasforma un file audio in **testo e sottotitoli** (SRT/VTT/TXT) direttamente in Claude Code e Claude Desktop, lavorando **interamente sul tuo computer** (l'audio non viene mai caricato online). Adatta a registrazioni di udienze, colloqui col cliente e note vocali coperte da segreto professionale. Sceglie da sola lo strumento giusto in base all'hardware (Mac Apple Silicon, Mac Intel, Windows, Linux). | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/trascrizione%20audio/audio-transcription.skill) |

---

## Cronologia degli aggiornamenti

| Data | Skill | Aggiornamento |
|------|-------|---------------|
| 31 maggio 2026 | *(tutte)* | Aggiunti link di download diretti ai file `.skill` nelle guide e una colonna "Scarica" nella tabella delle skill |
| 31 maggio 2026 | **trascrizione audio** | Primo rilascio: trascrizione audio→testo in locale (SRT/VTT/TXT), multi-piattaforma, con guida per avvocati |
| 31 maggio 2026 | **ricerca web (SearXNG)** | Primo rilascio: ricerca web gratuita e privata via SearXNG, con guida all'installazione del server e routing legale |
| 19 maggio 2026 | **BuddaLaw** v8.3 | Migliorata la gestione dei risultati duplicati nella ricerca articoli |
| 19 maggio 2026 | **BuddaLaw** v8.2 | Aggiunta suite di test automatici per verificare la qualità delle ricerche |
| 19 maggio 2026 | **normattiva** | Aggiunto supporto per versioni storiche delle norme e testi abrogati |
| 23 aprile 2026 | **BuddaLaw** | Primo rilascio: ricerca live di sentenze, normativa e prassi tributaria tramite MCP |
| 10 aprile 2026 | **normattiva** | Primo rilascio: generazione automatica di link a Normattiva.it per ogni citazione normativa |

---

## Approfondimenti

Articoli, video e podcast su [avvocati-e-mac.it](https://avvocati-e-mac.it) che spiegano come funzionano queste skill e come sono state costruite:

- **[Una skill per linkare le norme italiane con Normattiva.it](https://avvocati-e-mac.it/blog/2026/4/13/skill-link-norme-italiane-perplexity-claude)** — Articolo che racconta come è nata la skill normattiva e perché è utile per ottenere la liquidazione delle spese processuali
- **[Ricerche giuridiche online con IA? Iniziano ad essere possibili](https://avvocati-e-mac.it/blog/2025/4/2/ricerche-giuridiche-online-con-ia-iniziano-ad-essere-possibili)** — Articolo introduttivo sulla ricerca giurisprudenziale con l'IA e sulla scoperta di SearXNG per cercare sul web (alla base della skill di ricerca web)
- **[Video: MCP BuddaLaw per Perplexity](https://www.youtube.com/watch?v=Tu1ZDFstDsY)** — Video su YouTube che mostra come usare il server MCP di BuddaLaw con Perplexity
- **[Podcast ep. 79 — MCP di BuddaLaw, Skill Normattiva ed altri esperimenti](https://avvocati-e-mac.it/podcast/79)** — Episodio podcast che tratta entrambe le skill

---

## Come installare una skill

Scegli il prodotto Claude che usi:

### Claude Desktop (app per Mac e Windows)

1. Scarica il file `.skill` della skill che ti interessa (ad esempio `normattiva.skill`) cliccando su di esso in questa pagina GitHub e poi su **Download raw file**
2. Apri **Claude Desktop**
3. Vai su **Impostazioni** → **Skill** (o trascina il file `.skill` direttamente nella finestra di Claude)
4. Clicca su **Installa** quando compare la finestra di conferma
5. La skill è attiva: Claude la userà automaticamente quando pertinente

### Claude.ai / Claude for Work (Cowork)

1. Scarica il file `.skill` come descritto sopra
2. Apri [claude.ai](https://claude.ai) nel browser
3. Clicca sull'icona del tuo profilo in alto a destra → **Impostazioni** → **Skill**
4. Trascina il file `.skill` nell'area di caricamento, oppure clicca **Sfoglia** e selezionalo
5. Conferma l'installazione: la skill sarà disponibile in tutte le tue conversazioni

### Claude Code (terminale / riga di comando)

> Questa modalità è per utenti più avanzati che usano Claude Code dal terminale o dall'estensione per VS Code.

**Metodo 1 — Installa tramite file `.skill`:**
```
Apri Claude Code e scrivi:
/install normattiva.skill
```
oppure trascina il file `.skill` direttamente nella finestra di Claude Code.

**Metodo 2 — Installazione manuale della cartella:**

1. Scarica l'intera cartella della skill (ad esempio la cartella `normattiva/normattiva/`)
2. Copiala in:
   - **Mac/Linux:** `~/.claude/skills/`
   - **Windows:** `%APPDATA%\Claude\skills\`
3. Riavvia Claude Code

---

## Come aggiornare una skill

Quando viene pubblicata una nuova versione di una skill:

1. Torna su questa pagina GitHub
2. Scarica il nuovo file `.skill` (o la cartella aggiornata)
3. Installala seguendo gli stessi passi di sopra: la vecchia versione verrà sostituita automaticamente

Per ricevere notifiche sugli aggiornamenti, clicca su **Watch** → **Releases only** in alto a destra su questa pagina GitHub.

---

## Struttura del repository

Ogni skill è organizzata in una propria cartella:

```
nome-skill/
├── nome-skill/
│   ├── SKILL.md          ← istruzioni per Claude (non modificare)
│   └── references/       ← tabelle e riferimenti di supporto (se presenti)
└── nome-skill.skill      ← file preconfezionato, pronto per l'installazione
```

Il file `.skill` è quello che serve per installare la skill. La cartella interna contiene i dettagli tecnici, utili solo se vuoi capire come funziona la skill o modificarla.

---

## Suggerimenti e richieste

Hai bisogno di una skill per un'altra area del diritto?  
Apri una [Issue](../../issues) su questa pagina descrivendo cosa ti servirebbe — o scrivi direttamente a Filippo.

---

## Licenza

Rilasciato sotto licenza [MIT](LICENSE). Puoi usare, condividere e modificare liberamente queste skill, anche in ambito professionale.
