# CLAUDE.md / AGENTS.md — Contesto del progetto skill-legali

Questo file contiene informazioni di contesto per gli agenti AI che lavorano su questo repository. Leggilo all'inizio di ogni sessione.

---

## Regola di reciprocità CLAUDE.md / AGENTS.md

`CLAUDE.md` e `AGENTS.md` sono file gemelli e devono restare allineati.

- Se modifichi `CLAUDE.md`, applica la stessa modifica anche ad `AGENTS.md`.
- Se modifichi `AGENTS.md`, applica la stessa modifica anche a `CLAUDE.md`.
- La regola vale anche per i file annidati con gli stessi nomi nelle sottocartelle.
- Prima di concludere un lavoro che tocca uno dei due file, verifica che i file gemelli abbiano contenuto equivalente.

---

## Cos'è questo progetto

`skill-legali` è un repository pubblico GitHub che raccoglie **skill per assistenti AI** dedicate alla pratica legale italiana. Le skill sono istruzioni comportamentali che insegnano all'assistente come agire in specifici contesti legali o professionali.

**Repository GitHub:** `avvocati-e-mac/skill-legali`  
**Maintainer:** Filippo Strozzi (avvocato)  
**Target utenti finali:** avvocati italiani, **non tecnici** — le istruzioni devono sempre essere semplici e prive di gergo tecnico

Le skill devono restare compatibili con:

- Claude Desktop
- Claude for Work / Cowork
- Claude Code
- Codex e ambienti OpenAI che leggono skill `SKILL.md`

Quando una procedura dipende dal runtime, differenzia sempre in modo esplicito:

- **Modelli Claude:** usa i tool, i subagenti e i fallback disponibili nell'ambiente Claude.
- **Modelli OpenAI/Codex:** usa i tool MCP, shell, browser o subagenti disponibili nell'ambiente OpenAI/Codex.
- Se un tool non è disponibile nel runtime corrente, non inventare un equivalente: usa il fallback documentato nella skill oppure chiedi conferma all'utente.

---

## Skill presenti

### normattiva

- **Cartella:** `normattiva/`
- **Scopo:** genera link cliccabili verso [Normattiva.it](https://www.normattiva.it) per ogni riferimento normativo italiano nel testo, usando il formato URN-NIR
- **Trigger:** qualsiasi risposta che contiene citazioni normative (art. X c.c., d.lgs., legge n., r.d., d.p.r., Cost., ecc.)
- **Comportamento:** l'assistente non produce riferimenti normativi "nudi": ogni citazione diventa un link inline
- **File chiave:** `normattiva/normattiva/SKILL.md`, `normattiva/normattiva/references/atti.md` (tabella di 167 atti), `references/versioni-e-portale.md`, `references/verifica.md`, `references/api-e-verifica.md`, `scripts/verifica.py`
- **File installazione Claude:** `normattiva/normattiva.skill`
- **Versione 3 (convegno di Ravenna, 7 ottobre 2026)**, sviluppata in Cowork come `demora-normattiva` e adottata qui il 2026-10-17. Il 2026-10-17 tutte le righe di `atti.md` sono state verificate: le 157 righe `urn:nir:stato:` con l'API, i 10 d.m./D.P.C.M. e 4 casi che l'API non sa leggere sul portale con `scripts/verifica.py`.
- **L'API non è l'unico oracolo:** rifiuta d.m. e D.P.C.M. (`urn:nir:ministero...`, codice 1003) anche quando il link è giusto. Per quelli vale solo `scripts/verifica.py`, che apre il portale e confronta atto, allegato, articolo e versione.
- **Prima di modificare `atti.md`**, esegui il livello C dei test:
  `NORMATTIVA_LIVE=1 pytest normattiva/tests/test_api_live.py` (si ferma su 403/429,
  nessun ritento) e, per le righe non `stato`, lo script sul portale. I test
  strutturali da soli non possono accorgersi di un URN formalmente perfetto che
  punta al nulla: e' cosi' che due errori sono sopravvissuti fino al 2026-08-06.

### buddalaw

- **Cartella:** `buddalaw/`
- **Scopo:** ricerca live di sentenze, normativa, contratti e atti processuali italiani tramite MCP BuddaLaw
- **Trigger:** quesiti che richiedono sentenze italiane, verifica giurisprudenziale, contratti, atti processuali, prassi tributaria o provvedimenti del Garante Privacy
- **Comportamento:** l'assistente non cita sentenze specifiche dalla memoria interna; ogni riferimento deve provenire da ricerca live
- **File chiave:** `buddalaw/buddalaw/SKILL.md`, `buddalaw/buddalaw/references/`, `buddalaw/REPORT-sondaggio-v9.md` (comportamenti reali del server), `buddalaw/tests/` (README, CHECKLIST, fixture dello schema)
- **File installazione Claude:** `buddalaw/buddalaw.skill`
- **Versione 9.1 beta (2026-10-18):** mantiene l’inventario dei 48 tool del server BuddaLaw MCP 1.30.0 (16 per ricerca e lettura, 32 calcolatori/cataloghi non collaudati). Aggiunge `scripts/verifica_catalogo.py` per confrontare i nomi osservati con l’inventario della propria copia della skill, senza rete o credenziali; richiede shell e Python, con confronto manuale negli altri ambienti. Rafforza copia dei link, avviso immediato, gestione delle norme e lingua italiana. Gli esiti della nuova candidata sono in `buddalaw/REPORT-test-v9.1.md`; la campagna v9.0 resta congelata nel suo rapporto. Nessuna promozione stabile implicita.
- **Test:** livello A offline (gate) `python3 -m pytest buddalaw/tests` (144 controlli offline; i live sono saltati senza `BUDDALAW_LIVE`); livello C `BUDDALAW_LIVE=1 python3 -m pytest buddalaw/tests/test_mcp_live.py`, il cui primo test cerca l’intero catalogo (`+BuddaLaw`, non una selezione dei soli tool già noti) e diventa rosso quando lo schema live di BuddaLaw cambia (controllo di obsolescenza per il maintainer); livello B `python3 buddalaw/tests/e2e/run.py` (Claude Code isolato e opencode + OpenRouter, con tetto di spesa).
- **Runner v9.1:** 16 turni Claude per tutti i profili, registrati nel manifest. La nuova skill dispone di Bash per lo script locale; il valutatore boccia anche i tentativi di comandi estranei rifiutati dal runtime e controlla che i nomi passati allo script coincidano con quelli osservati. Non confrontare direttamente le nuove prove con le vecchie a otto turni.
- **Vincolo della ripresa del 18 ottobre:** il maintainer richiede esclusivamente l'abbonamento Claude. Per i test B usare `--runtime claude --solo-abbonamento` con un modello Claude esplicito; non riprendere OpenRouter o i proxy API senza una nuova istruzione esplicita. I valori USD della CLI sono stime dei token, non fatturazione attestata.
- **Prima di modificare la skill:** se il livello C segnala un cambio di schema, rigenera la fixture con `python3 buddalaw/tests/tools/estrai_schema.py` e aggiorna l'inventario di `SKILL.md`. Dopo ogni modifica rigenera `buddalaw.skill`, altrimenti il livello A resta rosso.

### GestioLex Corpus

- **Cartella:** `Gestiolex Corpus/`
- **Scopo:** ricerca testi normativi italiani e massime giurisprudenziali tramite MCP GestioLex Corpus
- **Trigger:** richieste su articoli di codice, basi normative, orientamenti giurisprudenziali, massime o principi di diritto italiani
- **Comportamento:** l'assistente sceglie il percorso piu preciso tra lettura esatta dell'articolo, ricerca normativa e ricerca giurisprudenziale, evitando ricerche parallele non necessarie
- **File chiave:** `Gestiolex Corpus/gestiolex-corpus/SKILL.md`, `Gestiolex Corpus/gestiolex-corpus/references/query-patterns.md`
- **File installazione Claude:** `Gestiolex Corpus/gestiolex-corpus.skill`

### memo-legale-strutturato

- **Cartella:** `memo-legale-strutturato/`
- **Scopo:** redige memo legali italiani chiari, sintetici e operativi per uso interno dell'avvocato o dello studio
- **Trigger:** memo legale, memorandum, parere interno, nota per avvocato, case assessment, legal risk assessment, strategia precontenziosa/processuale o trasformazione di ricerche/fonti in memo operativo
- **Comportamento:** usa progressive disclosure per consumare pochi token, sceglie tra memo rapido/standard/complesso, adatta i modelli di legal memo al diritto italiano e verifica BuddaLaw/Perplexity quando disponibili
- **File chiave:** `memo-legale-strutturato/memo-legale-strutturato/SKILL.md`, `memo-legale-strutturato/memo-legale-strutturato/references/`
- **File installazione Claude:** `memo-legale-strutturato/memo-legale-strutturato.skill`

### chiarisci-e-agisci

- **Cartella:** `chiarisci-e-agisci/`
- **Scopo:** accompagna l'avvocato dall'incertezza alla prima azione concreta mediante domande maieutiche, scomposizione e checkpoint
- **Trigger:** difficoltà a iniziare o organizzare un lavoro, preparazione dei prodromi alla redazione, scelta delle priorità per urgenza e importanza
- **Comportamento:** durante il chiarimento pone domande mirate, segnala lacune e contraddizioni, distingue dati forniti/inferiti/mancanti e non modifica file o workflow senza approvazione
- **File chiave:** `chiarisci-e-agisci/chiarisci-e-agisci/SKILL.md`, `chiarisci-e-agisci/chiarisci-e-agisci/references/`
- **File installazione Claude:** `chiarisci-e-agisci/chiarisci-e-agisci.skill`

### ricerca-web-searXNG

- **Cartella:** `ricerca con SearXNG e test/ricerca-web-seaXNG/`
- **Scopo:** ricerca web privata e ottimizzata tramite MCP SearXNG, con routing verso BuddaLaw e Normattiva per il diritto italiano
- **Trigger:** richieste di cercare online, trovare informazioni aggiornate, documentazione tecnica, news, ricette, dottrina o fonti web
- **Comportamento:** usa progressive disclosure, legge pagine solo quando serve e dichiara i parametri usati
- **File chiave:** `ricerca con SearXNG e test/ricerca-web-seaXNG/ricerca-web-searXNG/SKILL.md`, `references/`
- **File installazione Claude:** `ricerca con SearXNG e test/ricerca-web-seaXNG/ricerca-web-searXNG.skill`

### audio-transcription

- **Cartella:** `trascrizione audio/`
- **Scopo:** trascrive file audio o video in SRT/VTT/TXT in locale, scegliendo lo strumento in base all'hardware
- **Trigger:** richieste di trascrizione audio/video, sottotitoli, installazione o configurazione di parakeet, whisper o faster-whisper
- **Comportamento:** lavora in locale quando possibile e carica solo il reference della piattaforma rilevata
- **File chiave:** `trascrizione audio/audio-transcription/SKILL.md`, `trascrizione audio/audio-transcription/references/`
- **File installazione Claude:** `trascrizione audio/audio-transcription.skill`

### concilio-llm-prompt-legale (Concilio di LLM per valutazione risposta legale)

- **Cartella:** `concilio-llm-prompt-legale/`
- **Scopo:** valuta e confronta risposte di IA su quesiti di diritto italiano (civile, penale, tributario, amministrativo) con un "concilio" di giudici LLM; caso d'uso primario = confronto risposta base vs versione da miglioratore di prompt sullo stesso quesito (estrazione da DOCX/PDF/testo, confronto A/B/C, scoring su rubrica /39, verifica fonti, report leggibile)
- **Trigger:** richieste di confrontare/valutare la risposta di un'IA prima e dopo un miglioratore di prompt, confrontare più IA (A/B/C), controllare citazioni, GDPR/privacy o affidabilità della giurisprudenza, preparare workflow di giudizio e verifica fonti
- **Comportamento:** è controllo di qualità e non sostituisce mai la verifica dell'avvocato; nel confronto base-vs-migliorato usa ID neutri (A/B) per evitare bias; lavora in locale/offline finché l'utente non autorizza esplicitamente una verifica online; non installa tool né spende chiamate live senza approvazione
- **File chiave:** `concilio-llm-prompt-legale/concilio-llm-prompt-legale/SKILL.md`, `concilio-llm-prompt-legale/concilio-llm-prompt-legale/references/`, `concilio-llm-prompt-legale/concilio-llm-prompt-legale/scripts/legal_panel.py`
- **File installazione Claude:** `concilio-llm-prompt-legale/concilio-llm-prompt-legale.skill`

### miglioratore-prompt-legale (Miglioratore di prompt legale)

- **Cartella:** `miglioratore-prompt-legale/`
- **Scopo:** trasforma un quesito giuridico italiano (anche abbozzato) in un prompt ottimizzato e strutturato per ricerche legali affidabili; vale per qualsiasi ramo del diritto italiano (civile, penale, tributario, lavoro, amministrativo, crisi d'impresa)
- **Trigger:** quesiti giuridici su cui l'utente vuole una ricerca/parere affidabile; richieste tipo "migliora questo prompt legale", "scrivimi un prompt per un parere su…"; domande di diritto vaghe o incomplete che migliorerebbero con un prompt strutturato
- **Comportamento:** restituisce SOLO il prompt migliorato (meno di 750 parole), eventualmente dopo domande di chiarimento; non risponde al quesito e non inventa norme o sentenze; lavora offline di default e propone la ricerca online (ricerca-web-searXNG → perplexity-web-mcp → web nativo) solo per colmare lacune utili al prompt e dopo conferma dell'utente
- **File chiave:** `miglioratore-prompt-legale/miglioratore-prompt-legale/SKILL.md`, `miglioratore-prompt-legale/miglioratore-prompt-legale/references/`
- **File installazione Claude:** `miglioratore-prompt-legale/miglioratore-prompt-legale.skill`

### verifica-citazioni-legali

- **Cartella:** `verifica-citazioni-legali/`
- **Scopo:** verifica le citazioni di un atto, parere, memoria o contratto già scritto (specie se generato o rivisto con IA): esistenza ed estremi delle pronunce, verbatim, natura e pertinenza del passo, passi contrari, norme e vigenza
- **Trigger:** richieste di verificare, controllare o revisionare citazioni, sentenze, massime, riferimenti normativi o virgolettati; «esiste questa sentenza?», «controlla l'atto prima del deposito», ricerca di allucinazioni in testi scritti con IA
- **Comportamento:** verifica solo sulla fonte letta, mai a memoria; non dichiara «inesistente» senza prova positiva; chiede all'utente quali banche dati usare; produce un report con tabella delle azioni e testo da incollare; non modifica mai l'atto originale e applica solo le correzioni scelte, su una copia
- **File chiave:** `verifica-citazioni-legali/verifica-citazioni-legali/SKILL.md`, `references/`, `scripts/estrai_citazioni.py`, `scripts/confronta_verbatim.py`, `assets/test/` (atto di collaudo con verdetti attesi)
- **File installazione Claude:** `verifica-citazioni-legali/verifica-citazioni-legali.skill`
- **Riservatezza:** gli esempi e l'atto di collaudo non contengono dati di parti o pratiche reali; mantenerli così

---

## Struttura standard di una skill

Ogni skill segue questa struttura di cartelle:

```text
nome-skill/
├── nome-skill/
│   ├── SKILL.md                    ← frontmatter YAML + istruzioni comportamentali
│   ├── agents/                     ← (opzionale) metadati per ambienti OpenAI/Codex
│   │   └── openai.yaml
│   └── references/                 ← (opzionale) tabelle, lookup, documenti di supporto
│       └── nome-riferimento.md
└── nome-skill.skill                ← file ZIP preconfezionato per installazione Claude
```

Il file `.skill` è un archivio ZIP che contiene la cartella interna `nome-skill/` con `SKILL.md`, `references/` ed eventuale `agents/`. Viene generato comprimendo la cartella interna.

### Frontmatter SKILL.md

Ogni `SKILL.md` inizia con un frontmatter YAML obbligatorio:

```yaml
---
name: nome-skill
description: >
  Descrizione concisa di cosa fa la skill e quando si attiva.
  MANDATORY TRIGGERS: condizioni che devono far scattare la skill.
---
```

Il frontmatter deve restare compatibile con Claude e Codex: non usare campi proprietari che rendano il file illeggibile da uno dei due ambienti.

> ⚠️ **Limite description: massimo 1024 caratteri.** Il campo `description` non può superare i 1024 caratteri, altrimenti Claude Cowork rifiuta l'installazione con l'errore `field 'description' in SKILL.md must be at most 1024 characters`. Il limite vale sul valore "appiattito" dallo YAML (con `description: >` le righe non vuote vengono unite da spazi singoli). Tieni la description concisa e, in caso di dubbio, verifica la lunghezza prima di rigenerare il `.skill`.

---

## Come aggiungere una nuova skill

1. Crea la cartella `nome-skill/` nella root del repository.
2. Al suo interno, crea la sottocartella `nome-skill/nome-skill/` con il file `SKILL.md`.
3. Se la skill usa tabelle di riferimento, aggiungile in `nome-skill/nome-skill/references/`.
4. Se serve metadata per Codex/OpenAI, aggiungi `nome-skill/nome-skill/agents/openai.yaml` senza rendere obbligatorio quel file per Claude.
5. Crea il file `.skill` comprimendo la cartella interna:

   ```bash
   cd nome-skill
   zip -r nome-skill.skill nome-skill/
   ```

6. Aggiorna la tabella "Skill disponibili" nel `README.md` se cambia l'elenco o la descrizione pubblica.
7. Fai un commit atomico e descrittivo, poi push.

---

## Compatibilità Claude / OpenAI

Quando aggiorni una skill:

- Mantieni `SKILL.md` come entry point principale.
- Mantieni il frontmatter YAML semplice: `name`, `description` e, se già presenti, metadati non bloccanti come `version` o `metadata`.
- Non sostituire istruzioni Claude con istruzioni solo Codex. Se il comportamento cambia per runtime, scrivi due rami:
  - **Se stai operando in Claude Desktop, Claude for Work/Cowork o Claude Code:** usa il comportamento Claude.
  - **Se stai operando in Codex o in un ambiente OpenAI:** usa il comportamento OpenAI/Codex.
- Non rimuovere i file `.skill`: servono a Claude Desktop, Cowork e Claude Code.
- Se modifichi sorgenti dentro una skill, rigenera anche il relativo `.skill`.
- Evita riferimenti esclusivi a "Claude" quando la regola vale per ogni assistente; usa "assistente" o "agent". Usa "Claude" o "Codex/OpenAI" solo nei rami runtime-specifici.

---

## Regola: commit atomici, descrittivi e push automatico

I commit devono essere **atomici e descrittivi**.

- Ogni commit deve contenere una sola modifica logica coerente: non mescolare cambi di skill, README, test e packaging se possono essere separati.
- Il commit deve includere tutti i file necessari a rendere completa quella modifica logica: se aggiorni una skill, includi anche il relativo `.skill` rigenerato; se tocchi `CLAUDE.md`, includi anche `AGENTS.md`.
- Il messaggio deve descrivere chiaramente cosa cambia, usando preferibilmente il formato `tipo(scope): descrizione`.
- Evita messaggi generici come `update`, `fix`, `varie`, `misc`.

Esempi:

```bash
git commit -m "docs(repo): aggiungi regole per compatibilità codex"
git commit -m "feat(normattiva): aggiungi metadata openai"
git commit -m "chore(skills): rigenera archivi installabili"
```

In questo repository, **ogni volta che fai un commit devi fare subito anche il `git push`** verso `origin` (`avvocati-e-mac/skill-legali`), senza chiederlo all'utente. Il repo è pubblico e va mantenuto allineato al remote: non lasciare commit solo in locale.

```bash
git commit -m "tipo(scope): descrizione"
git push
```

Unica eccezione: se sei su un branch diverso da `main` creato per una specifica revisione, pusha comunque quel branch (`git push -u origin <branch>`) salvo diversa indicazione dell'utente.

### Autenticazione per il push

Sul Mac di Filippo ci sono **due account GitHub** autenticati via `gh`. L'account di default `a2podcast` **non ha permessi di scrittura** su questo repo: un `git push` diretto fallisce con errore **403**. Il push va fatto con l'account proprietario **`avvocati-e-mac`**.

Quando il push dà 403 (o prima di pushare), usa `gh` per impostare l'account giusto:

```bash
gh auth switch --user avvocati-e-mac
gh auth setup-git
git push
```

In generale, **usa `gh` per gestire autenticazione e push**: è il modo affidabile per evitare il 403.

---

## Note tecniche

### MCP BuddaLaw

- Il server MCP `buddalaw` può essere configurato localmente negli ambienti che lo supportano.
- BuddaLaw è un servizio di ricerca giurisprudenziale e normativa italiana.
- Le skill non devono presumere che il tool sia sempre disponibile: se manca, dichiararlo e usare il fallback previsto.

### MCP GestioLex Corpus

- Il server MCP `gestiolex_corpus` è sviluppato e messo a disposizione da GestioLex.
- Endpoint remoto: `https://corpus.gestiolex.it/mcp`.
- Serve a interrogare corpus normativi italiani e massime giurisprudenziali tramite strumenti MCP come `leggi_articolo`, `cerca_norma` e `cerca_giurisprudenza`.
- Per Codex si configura in `~/.codex/config.toml`; per Claude Code e Claude Desktop si configura nelle impostazioni MCP o con il comando MCP remoto supportato dalla versione in uso.
- La skill non contiene il server MCP: contiene solo le istruzioni per usarlo correttamente.

### File da non committare

- `.DS_Store` e artefatti `__MACOSX`
- file di impostazioni locali con credenziali o preferenze personali
- output temporanei generati da test o benchmark, salvo siano report intenzionali

---

## Workflow di release

Per pubblicare una nuova versione di una skill:

1. Modifica `SKILL.md` e/o i file in `references/` o `agents/`.
2. Rigenera il file `.skill`:

   ```bash
   cd nome-skill && zip -r nome-skill.skill nome-skill/ && cd ..
   ```

3. Aggiorna `README.md` se necessario.
4. Commit atomico e push:

   ```bash
   git add .
   git commit -m "feat(normattiva): descrizione della modifica"
   git push
   ```

5. Opzionale: crea un tag di versione:

   ```bash
   git tag v1.1.0 && git push --tags
   ```

---

## Tono e comunicazione

- Gli utenti finali sono avvocati italiani, non programmatori.
- Il README deve sempre usare linguaggio semplice, istruzioni passo-passo, niente abbreviazioni tecniche non spiegate.
- Se si aggiungono nuove sezioni al README, mantieni lo stesso tono accessibile.
- Le skill sono scritte in italiano, con linguaggio tecnico-giuridico appropriato quando serve.
