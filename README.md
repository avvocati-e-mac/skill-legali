# Skill legali per Claude, Codex e assistenti AI

Raccolta di **skill** per Claude, Codex e altri assistenti AI utili nella pratica e nello studio dell'avvocato italiano.  
Ogni skill insegna all'assistente comportamenti specifici — come generare automaticamente link alle norme, cercare giurisprudenza, fare ricerche sul web in modo riservato, trascrivere registrazioni o confrontare e valutare le risposte di diverse IA su una domanda di diritto — pensati per il lavoro quotidiano di chi fa l'avvocato.

> **A chi è rivolto questo repository**  
> Queste istruzioni sono scritte per avvocati che non hanno familiarità con la programmazione. Niente paura: installare una skill richiede solo pochi clic.

---

## Skill disponibili

| Skill | Descrizione | Scarica |
|-------|-------------|---------|
| [**normattiva**](./normattiva/) | Genera link ipertestuali cliccabili verso [Normattiva.it](https://www.normattiva.it) per ogni riferimento normativo italiano citato nel testo (art. X c.c., d.lgs., legge n., r.d., ecc.), usando il formato standard URN-NIR. L'assistente non produce riferimenti normativi "nudi": ogni citazione diventa automaticamente un link verificabile. | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/normattiva/normattiva.skill) |
| [**BuddaLaw**](./buddalaw/) | Ricerca live di sentenze (Cassazione, merito, TAR, CGT, Garante Privacy), normativa e prassi tributaria tramite il server MCP [BuddaLaw](https://buddalaw.it) *(banca dati a pagamento, con sistema a crediti)*. L'assistente non cita mai sentenze dalla memoria interna: ogni riferimento giurisprudenziale proviene da ricerca live con link verificabile. Include workflow per contratti (3 step) e atti processuali (2 step), con ordine obbligatorio per la prassi tributaria. | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/buddalaw/buddalaw.skill) |
| [**GestioLex Corpus**](./Gestiolex%20Corpus/) | Ricerca testi normativi e massime giurisprudenziali italiane tramite il server MCP GestioLex Corpus, sviluppato e messo a disposizione da [GestioLex](https://www.gestiolex.it/). Sceglie lo strumento piu adatto tra lettura esatta di articoli, ricerca normativa e orientamento giurisprudenziale. La [guida](./Gestiolex%20Corpus/README.md) spiega anche come configurare l'MCP in Claude Code e Codex. | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/Gestiolex%20Corpus/gestiolex-corpus.skill) |
| [**migliora chiarezza testi legali**](./migliora-chiarezza-testi-legali/) | Aiuta a rendere più chiari, leggibili e meno ambigui contratti, clausole, pareri e atti giudiziari italiani. Applica una checklist di revisione basata sul plain language legale di Bryan Garner, adattato alla tradizione giuridica italiana, e produce riscritture PRIMA/DOPO con motivazione. | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/migliora-chiarezza-testi-legali/migliora-chiarezza-testi-legali.skill) |
| [**ricerca web (SearXNG)**](./ricerca%20con%20SearXNG%20e%20test/) | Ricerca su internet **gratuita e privata** tramite un motore [SearXNG](https://docs.searxng.org) che installi sul tuo computer — l'alternativa per chi **non ha un abbonamento Perplexity**. Cura particolarmente le ricerche in italiano e quelle legali, con instradamento automatico verso Normattiva (norme), BuddaLaw (sentenze) e fonti di dottrina. La [guida passo-passo](./ricerca%20con%20SearXNG%20e%20test/README.md) spiega come creare il server SearXNG (Docker/OrbStack) e collegarlo all'assistente. | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/ricerca%20con%20SearXNG%20e%20test/ricerca-web-searXNG.skill) |
| [**trascrizione audio**](./trascrizione%20audio/) | Trasforma un file audio in **testo e sottotitoli** (SRT/VTT/TXT), lavorando **interamente sul tuo computer** quando l'ambiente lo consente (l'audio non viene mai caricato online). Adatta a registrazioni di udienze, colloqui col cliente e note vocali coperte da segreto professionale. Sceglie da sola lo strumento giusto in base all'hardware (Mac Apple Silicon, Mac Intel, Windows, Linux). | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/trascrizione%20audio/audio-transcription.skill) |
| [**Concilio di LLM (valutazione risposta legale)**](./concilio-llm-prompt-legale/) | Mette a confronto e dà un voto alle risposte di un'IA su una **stessa domanda di diritto italiano** (civile, penale, tributario, amministrativo). Caso d'uso principale: confrontare la **risposta "base" di un'IA con quella ottenuta usando un miglioratore di prompt**, per capire quanto migliora davvero. Supporta anche il confronto tra più IA (A/B/C) e la valutazione di una singola risposta. Estrae il testo dei pareri da Word/PDF/testo, li fa giudicare da un "concilio" di più modelli e controlla i punti critici: **citazioni** delle norme e delle sentenze, **privacy/GDPR** e affidabilità della giurisprudenza, producendo infine un report leggibile. È pensata come **controllo di qualità: non sostituisce mai la verifica dell'avvocato**. Lavora con i soli strumenti del tuo computer finché non sei tu ad autorizzare una verifica online. | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/concilio-llm-prompt-legale/concilio-llm-prompt-legale.skill) |
| [**miglioratore di prompt legale**](./miglioratore-prompt-legale/) | Trasforma una **domanda di diritto italiano scritta "alla buona"** in un **prompt ben strutturato e completo**, pensato per ottenere dall'IA una ricerca legale affidabile e direttamente utilizzabile. Funziona per qualsiasi materia (civile, penale, tributario, lavoro, amministrativo, crisi d'impresa). Se la domanda è ambigua ti fa prima qualche domanda di chiarimento; se serve un dato aggiornato (una riforma recente, l'orientamento attuale) ti **propone** una breve ricerca online — non la fa di nascosto. Il risultato è **solo il prompt migliorato**, pronto da incollare: non risponde al quesito e non inventa mai norme o sentenze. **Conviene richiamarla esplicitamente** (basta scrivere "usa il miglioratore di prompt legale"): non sempre si attiva da sola. Usa un po' più di "carburante" (consuma più risorse) rispetto a una risposta diretta, ma in cambio ottieni un prompt migliore e quindi una ricerca più affidabile. | [⬇️ `.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/miglioratore-prompt-legale/miglioratore-prompt-legale.skill) |

---

## Cronologia degli aggiornamenti

| Data | Skill | Aggiornamento |
|------|-------|---------------|
| 7 luglio 2026 | **migliora chiarezza testi legali** | Primo rilascio: revisione di contratti, clausole, pareri e atti giudiziari per migliorare chiarezza, leggibilità e riduzione dell'ambiguità |
| 17 giugno 2026 | **BuddaLaw** v8.4 | Risposte più curate, da parere d'avvocato: quando emerge un contrasto tra sentenze o una pronuncia delle Sezioni Unite (o dell'Adunanza Plenaria), l'assistente espone sempre i diversi orientamenti e il principio risolutivo, in tutti gli ambiti del diritto. Smesso di scartare le sentenze in base al solo "punteggio di rilevanza" — una sentenza importante può avere punteggio basso. Aggiunto un controllo che evita di accostare a una sentenza un link sbagliato e una regola per le pronunce più vecchie (precedenti al 2019) che non si possono aprire per intero |
| 17 giugno 2026 | **miglioratore di prompt legale** | Primo rilascio: trasforma un quesito giuridico italiano in un prompt ottimizzato e strutturato (restituisce solo il prompt, sotto le 750 parole); domande di chiarimento se la richiesta è ambigua, ricerca online opzionale "su conferma" e compatibilità Claude Code/Codex |
| 16 giugno 2026 | **Concilio di LLM** | Migliorie dopo prova reale: comando dedicato `prompt-eval` per il confronto base-vs-prompt-migliorato (ID neutri A/B); timeout per giudice e fallback automatico della singola cella in caso di modello bloccato; verifica fonti delegata a un subagente; riconoscimento confidenzialità basato su dati personali reali (non sulle parole-tema); estrazione del quesito più robusta |
| 16 giugno 2026 | **Concilio di LLM** | Rifocalizzata e rinominata (`concilio-llm-prompt-legale`): scopo principale = confronto risposta base vs versione da miglioratore di prompt; esempi generali sui quattro rami del diritto italiano (civile, penale, tributario, amministrativo) con preset dedicati |
| 16 giugno 2026 | **italian-legal-llm-panel** | Primo rilascio: giuria di IA per valutare e confrontare risposte legali italiane (punteggio su 39, confronto A/B/C, verifica delle fonti, report leggibile) |
| 10 giugno 2026 | **GestioLex Corpus** | Primo rilascio: ricerca normativa e massime italiane tramite MCP GestioLex Corpus, con routing tra articoli esatti, norme e giurisprudenza |
| 2 giugno 2026 | *(tutte)* | Aggiunta compatibilità esplicita con Codex/OpenAI, file `AGENTS.md` gemelli di `CLAUDE.md` e metadati `agents/openai.yaml` nelle skill |
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

Se usi Claude, scarica il file `.skill`. Se usi Codex o un ambiente OpenAI, usa la cartella interna della skill, quella che contiene `SKILL.md`.

### Compatibilità in breve

- **Claude Desktop, Claude for Work/Cowork e Claude Code:** usa i file `.skill` scaricabili dalla tabella.
- **Codex e ambienti OpenAI:** usa le cartelle sorgente con `SKILL.md`; ogni skill include anche `agents/openai.yaml` con metadati utili per l'interfaccia OpenAI.
- Quando una procedura cambia in base all'ambiente, la skill contiene istruzioni separate per Claude e per OpenAI/Codex.

Scegli il prodotto che usi:

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

### Codex / ambienti OpenAI

> Questa modalità è per utenti più avanzati.

Le skill sono compatibili anche con ambienti che leggono cartelle contenenti `SKILL.md`.

1. Apri la cartella della skill che ti interessa, ad esempio `normattiva/normattiva/`
2. Usa o installa quella cartella nel tuo ambiente Codex/OpenAI secondo la configurazione locale
3. Il file `agents/openai.yaml`, quando presente, fornisce nome, descrizione e metadati per l'interfaccia OpenAI

I file `.skill` restano pensati soprattutto per l'installazione comoda in Claude.

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
│   ├── SKILL.md          ← istruzioni principali della skill
│   ├── agents/           ← metadati per ambienti OpenAI/Codex (se presenti)
│   │   └── openai.yaml
│   └── references/       ← tabelle e riferimenti di supporto (se presenti)
└── nome-skill.skill      ← file preconfezionato, pronto per l'installazione Claude
```

Il file `.skill` è quello che serve per installare comodamente la skill in Claude. La cartella interna contiene i dettagli tecnici e il file `SKILL.md`, utili per capire come funziona la skill, modificarla o usarla in ambienti compatibili con Codex/OpenAI.

---

## Per chi contribuisce

Se modifichi questo repository:

1. Mantieni allineati `CLAUDE.md` e `AGENTS.md`: sono file gemelli.
2. Se aggiorni una skill, rigenera anche il relativo file `.skill`.
3. Fai commit piccoli, atomici e descrittivi: ogni commit deve contenere una sola modifica logica completa.
4. Dopo ogni commit, fai subito anche il push su GitHub.

---

## Suggerimenti e richieste

Hai bisogno di una skill per un'altra area del diritto?  
Apri una [Issue](../../issues) su questa pagina descrivendo cosa ti servirebbe — o scrivi direttamente a Filippo.

---

## Licenza

Rilasciato sotto licenza [MIT](LICENSE). Puoi usare, condividere e modificare liberamente queste skill, anche in ambito professionale.
