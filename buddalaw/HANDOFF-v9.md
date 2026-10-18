# BuddaLaw v9.0 — Passaggio di consegne

**Data:** 2026-10-18
**Branch:** `feat/buddalaw-v9` · **PR in bozza:** https://github.com/avvocati-e-mac/skill-legali/pull/1 (non unire a `main` senza l'ok del maintainer)
**Piano di riferimento:** il piano «BuddaLaw v9.0: skill allineata al server reale, avviso di obsolescenza, test a tre livelli» (riassunto qui sotto)

## Vincolo del maintainer: solo abbonamento Claude

Il 18 ottobre il maintainer ha precisato: «usa l'abbonamento di claude non
sprecare i miei soldi su openrouter». Questa istruzione prevale sui comandi
storici qui sotto: **non riprendere OpenRouter né i verificatori con proxy API**.
Le tornate OpenRouter incomplete restano tali e non vanno presentate come
verifica conclusa dei relativi modelli. Il passaggio a `main` è già autorizzato
al termine del collaudo; non serve richiederlo.

- Accesso della CLI verificato: `claude.ai`, `firstParty`, abbonamento `pro`;
  nessuna chiave API nell'ambiente. Il programma ora offre
  `--runtime claude --solo-abbonamento --modello <modello Claude esplicito>`:
  se non verifica l'abbonamento o trova variabili API, non avvia il modello.
  Il manifest conserva solo questi tre dati, senza identificativi personali.
- Controlli offline aggiornati: **114/114**, più 12 live saltati.
- I valori USD dei test Claude sono stime dei token riportate dalla CLI,
  **non addebiti attestati**. Non sommarli ai costi OpenRouter come se fossero
  fatturazione aggiuntiva. Riferimento: [Anthropic](https://code.claude.com/docs/en/costs).
- Dopo «autorizzo», un controllo OpenCode nella sandbox originale è riuscito;
  il successivo preflight è fallito ancora con SSE 400, prima dei modelli
  (`20261018-121903-721116`). Claude accoppiato è stato fermato, zero prove
  valide (`20261018-121904-779603`). OpenCode resta escluso.
- La candidata C2 omette B12 anche su Claude Pro indipendente: Haiku **0/3**
  (`20261018-122434-829842`). Sonnet 4.6 omette l'avviso nella prima prova
  valida (`20261018-123248-635574`); tornata fermata manualmente nella seconda,
  senza guasto BuddaLaw. Due avvii precedenti nella sandbox senza rete non
  hanno prodotto risposte né chiamate BuddaLaw: non sono fallimenti della skill
  (`20261018-122852-523710`, `20261018-123032-869731`).
- Nuova candidata C3, commit `bcc34e6`: inventario JSON una voce per riga;
  confronto tra insiemi e numero di nomi, considerando solo l'array, distinto
  dai nomi negli esempi. Sorgenti e archivio rigenerati, offline superato.
  B12 Haiku concluso in `20261018-123513-403307`: **0/3**, avviso ancora
  omesso. Hash C3:
  `1ce58fd6d54a617eb7bd176df5a9b304e4f89a012c2646a6d2f2f46897f0647f`.
- Completamento in corso, solo Claude Pro: altri 25 casi v9, 59 esecuzioni
  previste (`20261018-123724-623063`); confronto v8.4/nessuna, 34 esecuzioni
  (`20261018-123806-605934`). B13 v9 passa 3/3. Arresto condiviso separato in
  `results/20261018-c3-claude-pro/STOP`, da conservare se creato.
- Protezione dell'abbonamento pubblicata nel commit `ac05b18`.
  Le copie installate non sono state aggiornate.

## Ripresa del 18 ottobre — verifica interrotta sul collegamento

Il maintainer ha chiesto «riparti da handoff per finire test skill e passare a
main»: il passaggio a `main` è quindi autorizzato al termine della verifica.
Questa sezione prevale sul precedente passaggio di consegne. La PR resta
in bozza: il collaudo della candidata seguente è stato interrotto dal nuovo
guasto descritto qui sotto. Non è una promozione stabile.

- Controlli offline: **104/104**, più 12 live saltati nel comando ordinario.
- Il server espone **48 tool**, non più 16: 32 nuovi calcolatori/cataloghi;
  i 16 di ricerca e lettura hanno parametri e descrizioni invariati.
- T74 selezionava soltanto i nomi già noti e dava un falso verde. Ora scopre
  l'intero server con `+BuddaLaw`: rosso con la vecchia fixture, verde dopo
  l'aggiornamento a 48. I nomi coincidono anche con il MCP nativo Codex.
- Inventario e `.skill` aggiornati. La candidata con hash
  `87bde6f179b716b8fd748c0678860478abf3a0b4edb94ecd0a6a380ecc9205a3`
  omette l'avviso B12 in 3/3 prove Qwen e 3/3 Haiku; Haiku omette anche B23.
  B13 passa 3/3 e B24 passa dopo la correzione del valutatore descritta sotto.
- Il valutatore scartava i file MCP persistiti da Claude. Ora ammette soltanto
  il percorso esatto restituito dalla fonte e letto con successo; non legge
  file aggiuntivi dietro le quinte. La rivalutazione di B24 non cambia la
  risposta originale e rimuove il falso errore sui link.
- Candidata attuale: hash
  `5b470efdd3587b8e4107a0b8e23bf9dd3fb71ea956392eec88d2eee440872c3d`.
  Scoperta esplicita del catalogo differito in Claude; inventario vicino alla
  procedura. Sorgente e archivio coerenti; verifica live non conclusa.
- I collaudi possono ora usare sandbox separate con `BUDDALAW_SANDBOX` e un
  unico `BUDDALAW_STOP_FILE`: al primo guasto si fermano tutti. Il file resta
  presente e non autorizza ritenti. Cinque prove offline proteggono lo stop.
- Test positivo B12 della candidata attuale, tre prove previste per modello, in
  `tests/e2e/results/20261018-112344-442115/` (Haiku),
  `20261018-112345-576791/` (Qwen), `20261018-112345-939757/` (DeepSeek).
  Sandbox sotto `.opencode-sandbox/validation-c2/`; stop condiviso in
  `results/20261018-c2-validation/STOP`.
- **Nuovo fermo:** entrambe le nuove sandbox OpenCode falliscono il preflight
  con `SSE error: Non-200 status code (400)`, prima dei modelli (0/3 per
  modello). Haiku è fermato dallo stop condiviso nella prima prova: 1/3
  registrata, **zero prove valide**. La scoperta `+BuddaLaw` compare nella
  traccia parziale, ma non dimostra che l'avviso corretto arrivi nella risposta.
- Le configurazioni MCP delle nuove sandbox coincidono con quella precedente;
  anche configurazione isolata e percorso degli output coincidono. Non sono
  stati letti file di credenziali e non è provata la necessità di un nuovo login.
- Nessun ritento dopo il fermo. Il file `STOP` è preservato. Per nuove chiamate
  serve una nuova autorizzazione del maintainer secondo la regola di arresto
  dell'handoff. Prima prova suggerita: un solo controllo del collegamento nella
  sandbox originale già autorizzata; poi confronto con le nuove cartelle,
  conservando il vecchio arresto e aprendo una nuova tornata solo se autorizzata.
- Nessuna copia installata aggiornata; cartelle e risposte precedenti preservate.

Commit pubblicati nella ripresa: `5353983` (schema e inventario), `6f7f28e`
(isolamento Claude), `e851335` (fonti persistite), `78f92c2` (stop condiviso),
`d1815d7` (catalogo differito e inventario vicino alla procedura).
Attendere il completamento del test positivo prima di promuovere la candidata.

## Da leggere per riprendere

**Handoff richiesto dal maintainer il 18 ottobre.** Questa sezione riassume
lo stato finale e prevale sui dati storici riportati più sotto. Per prepararla
non sono stati avviati nuovi test a pagamento.

| Punto | Stato al passaggio di consegne |
|---|---|
| Rilascio | Beta; PR ancora in bozza, nessuna promozione stabile |
| Controlli offline | **89/89 superati** |
| Livello C | **12/12 superati**, in due tornate: 11 comportamenti e T74 schema |
| Suite OpenCode completa | **13/124 registrate, 11 valide, 2 non valutabili**; interrotta durante Qwen |
| Blocco da risolvere | Collegamento MCP intermittente nell'avvio effettivo di OpenCode |
| Nuovo arresto automatico | Implementato e testato offline; manca la verifica live dopo la correzione |
| Skill installabile | Sorgenti e `.skill` invariati durante il red teaming; copie installate non aggiornate |
| Caso del chirurgo | Quattro risposte originali conservate; confronto concluso, distinto dalla suite generale |

**Prima azione utile:** leggere `tests/README.md` e diagnosticare l'avvio MCP
di OpenCode. Non attribuire a Qwen il fallimento B03 r2: la prova del guasto è
in `tests/e2e/results/20261018-074418-850333/opencode__openrouter_qwen_qwen3.8-flash__v9/B03__r2.mcp.json`.
Un precedente `mcp list` riuscito non dimostra che il processo successivo
disponga dei tool. Non presumere che occorra rifare il login: OAuth era stato
rinnovato con successo.

Dopo aver risolto il collegamento, eseguire prima un controllo breve del
runner aggiornato. Dalla root del repository:

```bash
bash buddalaw/tests/e2e/prepara_opencode.sh
python3.14 buddalaw/tests/e2e/run.py --runtime opencode --config v9 --casi B00 --runs 1 --budget 0.10
```

Il controllo usa entrambi i modelli OpenRouter e resta una tornata separata.
Se compare un nuovo guasto, fermarsi e conservarne le prove. Quando l'avvio
è verificato, completare le tornate descritte in «Cosa resta da fare», dando
priorità agli avvisi B12/B13/B23/B24. Non ripetere il livello C già superato
senza nuove modifiche o indizi di cambiamento del servizio.

**Materiali da preservare:**

- Caso del chirurgo: `tests/e2e/results/20261017-caso-chirurgo/` e
  `~/Downloads/Test_BuddaLaw_v9_Chirurgo_2026-10-17/`.
- Red teaming e nuove risposte: le tre cartelle di risultati elencate nella
  sezione del 18 ottobre e `~/Downloads/Test_BuddaLaw_v9_RedTeam_2026-10-18/`.
  Quest'ultima contiene **16 nuove risposte**, indice con impronte, audit,
  report, piano e copia di questo handoff. Le prove non valutabili sono indicate.
- Non riscrivere gli originali; non pubblicare i trace grezzi ignorati da git.
- Cartelle non tracciate preesistenti da lasciare intatte: `.claude/`, `logs/`,
  `migliora-chiarezza-testi-legali/tests/blind/` e
  `migliora-chiarezza-testi-legali/tests/runs/`.

**Commit pubblicati da cui ripartire:**

| Commit | Contenuto |
|---|---|
| `1ffb567` | Copertura, provenienza delle fonti e attacchi al valutatore |
| `5e53e7d` | Configurazione OpenCode separata dalle skill globali |
| `cc003ae` | ToolSearch esplicito per il controllo dello schema live |
| `8f5ca78` | Riconoscimento delle citazioni con data completa |
| `2e18c63` | Arresto sul guasto MCP all'avvio e classificazione delle prove |
| `365ad68` | Piano di red teaming, report e stato del collaudo parziale |

## Dove siamo

| Fatto | Commit |
|---|---|
| Sondaggio del server MCP 1.30.0 (16 tool, enum, formati, 37 comportamenti) | `f4c48ea` |
| Skill v9.0: 187 righe, procedura in 7 passi, tabella di instradamento, inventario dei tool per l'avviso di aggiornamento | `6dca99e` |
| Suite di test a tre livelli (A offline, B end-to-end, C live) e `tests/CHECKLIST.md` (T01–T84) | `83a33c9` |
| Report di collaudo con Haiku | `9659b35` |
| README e CLAUDE.md/AGENTS.md allineati | `a0c39ee`, `aa6e9ca` |

Prima tornata (dati storici): livello A 52/52; Haiku v9 24/26 casi, ⚡ 17/18,
zero link inventati su 114 esecuzioni, ≈ 0,94 $. Non sommare questi dati alle
coorti successive. Dettagli in `REPORT-test-v9.0.md`.

## Aggiornamento dopo la ripresa del 17 ottobre

- Il maintainer ha autorizzato la ripresa e chiesto un confronto mirato sullo
  stesso quesito con **subagenti GPT Astra e Luna**, più **DeepSeek V4.1 Flash e
  Qwen 3.8 Flash-Next tramite OpenCode/OpenRouter**. Quattro risposte concluse,
  conservate integralmente in `tests/e2e/results/20261017-caso-chirurgo/` (ignorata
  da git) e copiate in Downloads con il confronto e gli audit.
- BuddaLaw è autenticato in OpenCode; non occorre presumere un nuovo login.
  Qwen Flash-Next usa l'ID `openrouter/qwen/qwen3.8-flash`. Versione CLI: 1.18.19.
- Esiti mirati: Astra 4 ricerche e 1 integrale ottenuto su 2 richieste; Luna
  3 ricerche e 2 integrali dichiarati nell'audit; DeepSeek **10 ricerche** e
  nessun integrale ottenuto; Qwen **7 ricerche**, nessun integrale ottenuto,
  **4 chiamate non conformi e 1 URL giurisprudenziale alterato**. Dati completi
  nel report; questo singolo caso non sostituisce la suite né prova soglie
  percentuali di affidabilità.
- Costo OpenCode delle due risposte concluse: **0,05780 $**, esclusi
  preparazione e tentativo incompleto. Costi GPT non disponibili.
- La suite generale è stata interrotta per il quesito richiesto: Qwen aveva
  passato B00–B02. Le prove preparatorie con isolamento errato sono escluse.
- Il runner ora esclude tutti gli MCP estranei ereditati, non avvia il modello
  se la skill viene caricata dalla posizione sbagliata e ferma anche HTTP 500.
  La sandbox nega `task` e `question`: una delega interna `explore` aveva lasciato
  aperto il primo tentativo DeepSeek. Il tentativo è conservato separatamente.
  Per il quesito mirato sono stati usati 16 passi; il runner ordinario resta a 8.
- Offline: **61/61** (52 strutturali più 9 sul runner). La skill e il `.skill`
  non sono cambiati. Non sono state aggiornate copie installate.
- Il canale C via Claude ha rifiutato `claude-haiku-5-5` come modello non
  riconosciuto, senza chiamare BuddaLaw: risolvere questo ID prima di rilanciarlo.

La lista qui sotto descrive il lavoro generale ancora aperto, con le
precisazioni dell'aggiornamento sopra. Non unire la PR senza l'ok del maintainer.

## Revisione critica e stato al 18 ottobre

Il maintainer ha chiesto di procedere con gli ulteriori test e di sottoporre
anche il piano a red teaming. Piano ed esiti sono in
`PIANO-collaudo-v9-red-team.md` e nell'ultima sezione del report.

- **89/89 offline**, compresi gli attacchi al valutatore. Le correzioni hanno
  rimosso falsi verdi (suite vuote, fonti prese dagli esempi, URL come prefissi)
  e falsi rossi (virgolette e date complete), controllano schema, budget per
  quesito, copertura e prove di isolamento nelle rivalutazioni.
- **Livello C completato: 12/12.** Gli 11 test di comportamento sono passati
  con 13 chiamate, 0,4923 $. T74 è passato separatamente dopo aver attivato
  `ENABLE_TOOL_SEARCH=true` nel proxy. La fixture non è cambiata.
- Claude Code 2.1.289 non riconosce Haiku 5.5. Il default dei test è ora
  **`claude-haiku-4-5-20251001`**, modificabile con `BUDDALAW_CLAUDE_MODEL`.
  Nessun aggiornamento software; la nuova coorte non equivale alla vecchia.
- OAuth OpenCode rinnovato con successo. Una configurazione separata con
  `XDG_CONFIG_HOME` esclude le skill globali omonime senza leggere o copiare
  credenziali. Usare i comandi di autorizzazione stampati dallo script.
- **Suite OpenCode interrotta: 13/124 registrate, 11 valide.** Qwen: B00 3/3,
  B01 2/3 (avvertenze finali), B02 3/3; B03 ha due successi e una prova non
  valutabile; B04 interrotto. DeepSeek non era ancora stato raggiunto dalla
  nuova suite completa. Il controllo breve separato B00 ha invece usato
  entrambi i modelli; DeepSeek senza skill fallisce soltanto la lingua.
- Per **B03 r2**, Qwen dichiarava tool assenti: il log della stessa sessione
  conferma `server unavailable`, `key=buddalaw`, `status=failed`. È un guasto
  del collegamento, non della skill o del modello. Il vecchio `mcp list` di
  preflight non garantiva gli avvii successivi. La tornata è stata fermata
  dopo la diagnosi, senza nuovi tentativi di ricerca.
- Il runner ora sorveglia anche stderr di OpenCode e ferma il processo su
  questo errore di avvio. Testato offline che non parta l'azione successiva;
  **non è ancora seguito da un nuovo collaudo live completo**. Il modello
  ausiliario dei titoli viene impostato su quello scelto, evitando altri
  modelli ereditati. OpenCode usa ora **16 passi** per tutti i profili.
- Tracce: `tests/e2e/results/redteam-20261017/`,
  `20261018-074007-371138/` (controllo breve) e
  `20261018-074418-850333/` (suite interrotta). Quest'ultima conserva la prova
  del guasto, la valutazione iniziale e quella corretta, senza cambiare testi.
  Costi step noti: 0,01102 $ e 0,07019 $, esclusi diagnostica e ausiliari.
- Nuove risposte in `Downloads/Test_BuddaLaw_v9_RedTeam_2026-10-18/`;
  i quattro originali del chirurgo restano invariati nella cartella precedente.
- Skill e `.skill` **invariati**; nessuna copia installata aggiornata. Stato
  **beta, non promossa al rilascio stabile**. Non cambiare attese o istruzioni
  per compensare guasti del canale.

## Cosa resta da fare

Nella prima tornata il server era andato fuori servizio a metà collaudo
(«Circuit breaker aperto — backend temporaneamente non disponibile», HTTP 500).
Il maintainer ha poi autorizzato la ripresa e `check_access` è riuscito, come
registrato sopra. Per completare il lavoro generale rimangono questi passi;
resta lo stop senza ritenti automatici al primo nuovo blocco o guasto:

1. **Collegamento OpenCode:** prima di nuove ricerche verificare il guasto
   intermittente nell'avvio effettivo del processo, non soltanto con un
   `mcp list` separato. Il nuovo controllo ferma la tornata al primo avvio
   MCP fallito. Non avviare due collaudi sulla stessa sandbox.
2. **Livello B, Haiku:**
   - nuova coorte esplicitamente identificata: `python3.14 buddalaw/tests/e2e/run.py --runtime claude --config v9 --runs 1 --runs-lampo 3`, guardando soprattutto B12/B23 (avviso presente) e B13/B24 (avviso assente);
   - `--config v8.4,nessuna --solo-lampo` per il confronto (oggi non conclusivo: 3 casi validi, pari);
   - `--modello default --solo-lampo`.
3. **opencode (Qwen 3.8 Flash-Next, DeepSeek V4.1 Flash):** dopo aver risolto il
   collegamento, preparare la sandbox e completare `--runtime opencode --config
   v9 --runs 1 --runs-lampo 3`. Sono tre ripetizioni **complessive** dei critici,
   non una più altre tre. Le risposte originali e le tornate interrotte restano
   separate. Confrontare v8.4/nessuna con gli stessi modelli e limiti.
4. Aggiornare `REPORT-test-v9.0.md` con i nuovi esiti, poi commit e push.
5. Facoltativo: verificare con `normattiva/normattiva/scripts/verifica.py` le due discrepanze URN di `get_law_article` (S1: allegato `;262` invece di `;262:2` per i codici; S2: URN diverso per il D.M. 55/2014).
6. Togliere la bozza dalla PR e unire solo dopo l'ok.

## Avvertenze per chi riprende

- **pytest:** usare la cache già presente, senza modificare Python installato:
  `UV_CACHE_DIR=/private/tmp/buddalaw-uv-cache uv run --offline --no-project --with pytest --python /opt/homebrew/bin/python3.14 python -m pytest buddalaw/tests/test_struttura.py buddalaw/tests/test_e2e_runner.py buddalaw/tests/test_e2e_redteam.py`.
- **Isolamento:** in `~/.claude/skills/buddalaw` (e probabilmente `~/.codex/skills/buddalaw`) c'è una vecchia v8.3 con lo stesso nome. I runner la escludono (`--disable-slash-commands`; in opencode `OPENCODE_DISABLE_EXTERNAL_SKILLS=1`, `OPENCODE_DISABLE_CLAUDE_CODE=1`). Non aggiornare quelle copie senza consenso.
- **Spesa:** tetto predefinito 5 $ per modello e invocazione; la nuova suite
  aveva tetto 3 $. I costi già maturati non sono sommati automaticamente tra
  invocazioni. I costi parziali e degli ausiliari non sono un totale di fattura.
- **Server:** fermarsi al primo 403/429, circuit breaker o HTTP 500, senza ritentare (`tools/chiama_mcp.py` lo fa già).
- **Riservatezza:** non leggere file di credenziali (es. `auth.json` di opencode); nessuna chiave nel repo; fixture pseudonimizzate.
- **Schema:** rigenerare la fixture soltanto dopo aver verificato un cambio
  reale. Un'estrazione vuota è un errore del canale, non uno schema da salvare.
- **GPT / Codex:** Astra e Luna collaudati come subagenti con MCP nativi in questa sessione. Non equivale a un collaudo della CLI Codex né a un aggiornamento della sua configurazione locale.
