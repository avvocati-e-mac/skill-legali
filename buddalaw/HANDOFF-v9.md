# BuddaLaw v9.2 — revisione conclusa con limiti

**Aggiornato:** 19 ottobre 2026. **Branch di revisione:** `fix/buddalaw-v9-completamento`.
La richiesta «riparti da handoff … arrivare alla versione stabile … test con
Luna usando questo abbonamento» è stata eseguita. Questa apertura prevale
su tutta la cronologia sottostante.

## Stato conclusivo

- **Versione 9.2 definitiva con limiti documentati. Non promossa a stabile sui
  modelli leggeri.** Nessun test in corso, nessuna attesa di quota, nessun
  lavoro da riprendere automaticamente per questa campagna.
- [Rapporto completo](REPORT-test-v9.2.md): piano, due candidate C7/C8,
  risultati avversariali, motivazione dell'arresto e limiti per modello.
- Migliorie: selezione esplicita dei tool dopo il confronto del catalogo;
  estremi normativi prima degli alias; controllo di link su file originali
  già disponibili. Il verificatore rileva l'errore reale C6 senza correggere
  o sostituire la vecchia risposta.
- **177 controlli offline superati**, 12 live saltati. Nessuna nuova
  certificazione completa dello schema o dei 32 calcolatori.
- Haiku C7: **6 valide, 5 promosse** (B12 3/3, B13 2/3). Rimane un tentativo
  di usare la shell per preparare una ricerca.
- Haiku C8: **4/26 avviate, 3 valide**. B00 promosso dopo correzione
  dell'attesa di versione; B01/B02 bocciati, B03 interrotta e non valutabile.
  B02 non effettua alcuna ricerca MCP. Due critici bocciati su 17 rendono
  impossibile il 90% nella tornata (massimo 15/17): stop deciso dal coordinatore,
  non guasto del servizio. Suite incompleta dichiarata, senza ritenti.
- Luna `gpt-6-luna`, `high`, subagenti nativi di questo abbonamento su richiesta
  esplicita: **sei risposte**, 17 chiamate MCP, **13 link fedeli**. Non è una
  promozione completa: confronto catalogo manuale anziché script, data di
  deposito fuori dai link di merito e conteggio avvisi non attestabile da
  una traccia nativa. Un ulteriore test locale del verificatore rileva l'URL
  sbagliato nella risposta C6. Audit e limiti nel rapporto.
- Solo Claude Pro nei test CLI, nessun OpenRouter o proxy API. I 21 eventi
  nativi controllati indicano consumo extra disabilitato. Costi stimati noti
  1,51547 USD, escluso B03 interrotto; non sono fatturazione aggiuntiva.

## Pacchetto finale e controlli

- SHA-256 `SKILL.md` finale:
  `6be2bea52b49b84cdd7828941d1cb59cacf327b79e562d17255acaca90c80b2f`.
- SHA-256 archivio `buddalaw.skill`:
  `1c1e664910c729879601b8dddfc7881115d4bc7ae5d5fc69a4bda8100b6f51e7`.
- Rispetto alla C8 provata cambia soltanto l'etichetta di stato nel changelog
  del frontmatter; corpo delle istruzioni e tutte le risorse sono identici.
- Il valutatore ammette il solo suffisso diagnostico `2>&1`, senza comandi
  aggiuntivi; controlla `public_url` e numero/anno dello stesso oggetto e la
  versione della skill congelata in B00. Rivalutazioni senza nuove chiamate.
- Le copie installate in Claude/Codex non sono state aggiornate.

```bash
UV_CACHE_DIR=/private/tmp/buddalaw-uv-cache uv run --offline --no-project --with pytest --python /opt/homebrew/bin/python3.14 python -m pytest -q buddalaw/tests
```

## Prove da preservare e limiti aperti

Sotto `tests/e2e/results/` (ignorato da Git):

| Cartella | Contenuto |
|---|---|
| `20261019-071357-946829` | C7 Haiku, sei prove, esiti rivalutati |
| `20261019-072050-161495` | C8 Haiku, tornata fermata per soglia irraggiungibile |
| `20261019-luna-c7` | Audit Luna, note d'ambiente, copie C7/C8 e confronto locale |
| `20261019-c7/STOP` | Arresto conclusivo; conservarlo senza cancellarlo |

Non dichiarare impossibile qualsiasi miglioramento futuro: i test mostrano
che queste due candidate non raggiungono la soglia richiesta. Ulteriore
robustezza richiede soprattutto controlli nel programma che esegue il modello,
non altre promesse nelle istruzioni. Il controllo dei link è facoltativo e
condizionato alla disponibilità dei file; non assicura la provenienza MCP,
la pertinenza o l'identità del messaggio dopo l'invio. Nessuna nuova promozione
per Sonnet, calcolatori, modelli OpenRouter o ambienti senza shell.

Una nuova richiesta può aprire una campagna distinta; non rilanciare questa
per cancellare gli esiti negativi. Lasciare intatti risultati storici e cartelle
preesistenti `.claude/`, `logs/`, `migliora-chiarezza-testi-legali/tests/blind/`
e `migliora-chiarezza-testi-legali/tests/runs/`. Non pubblicare audit grezzi.

## Cronologia conservata

<details>
<summary>Handoff v9.1 e cronologia v9.0, superati dall'apertura v9.2</summary>

# BuddaLaw — ripresa e candidata v9.1 beta

**Handoff aggiornato:** 19 ottobre 2026. **Collaudo concluso:** 18 ottobre 2026.
**Branch:** `fix/buddalaw-v9-completamento`, pubblicato su `origin`.
**Stato:** revisione beta e collaudo mirato conclusi. Nessuna promozione stabile.
Questa apertura prevale sulle note storiche della v9.0 archiviate sotto.

## Pubblicazione e stato verificato il 19 ottobre

- Commit della revisione: [`1805a46`](https://github.com/avvocati-e-mac/skill-legali/commit/1805a462b3ab1dcc3ac69447966fc47f8dc23744).
- [PR #2](https://github.com/avvocati-e-mac/skill-legali/pull/2): **aperta, in bozza**, base `main`, non unita. La verifica del 19 ottobre conferma questi dati.
- La v9.1 è disponibile nel branch e nell'archivio locale
  `buddalaw/buddalaw.skill`; `main` conserva la precedente v9.0 beta.
- La richiesta corrente è soltanto preparare questo handoff: non sono stati
  avviati nuovi test, modifiche della skill, installazioni o operazioni di merge.

La richiesta «riparti da handoff per ultimare la skill» ha avviato una nuova
candidata, perché il lavoro precedente era già concluso e unito a main.
La v9.0 C3 e le sue risposte restano congelate; non sono state ripetute per
alzare il punteggio. Le copie installate non sono state aggiornate.

Leggere prima [REPORT-test-v9.1.md](REPORT-test-v9.1.md), che contiene hash,
prove, limiti e differenze dell'ambiente di test. Il file `SKILL.md` della candidata C6 ha hash:
`f55712536f17d3c809c6b1632bdaa6c7a59db1ed331e344468e39814e794fed5`.
Le impronte delle altre risorse sono nei manifest delle tornate: il solo hash
di `SKILL.md` non identifica tutti i file del pacchetto.
SHA-256 dell'archivio installabile, verificato il 19 ottobre:
`ff795e0836fcc0ea69411fcc82c1e7b402126d1e39d26fa3b9d6d74ee95bcc39`.

- **144 controlli offline superati**, 12 live saltati; sorgenti e `.skill`
  coerenti. Nuovo script `buddalaw/scripts/verifica_catalogo.py`, senza rete
  o credenziali, per confrontare il catalogo osservato con l'inventario locale.
- Nuove istruzioni su avviso immediato, copia dei link, norme, lingua e anno
  delle pronunce recenti. Il confronto manuale resta il fallback senza shell.
- Solo abbonamento **Claude Pro**, nessuna API/OpenRouter. Nei nuovi eventi
  osservati il consumo extra è disabilitato. Il limite Claude è 16 turni per
  tutti i profili; non confrontare le percentuali con la vecchia C3 a otto.
- C6 Haiku: **6/6 valide, 0/6 promosse**, B12 e B13 bocciati per comandi shell
  estranei, anche se negati dal runtime. Gli avvisi risultano corretti.
- C6 Sonnet: primo gruppo **4/4 valide, 3/4 promosse**. B12/B13/B24 passano;
  B23 emette l'avviso una sola volta ma altera una cifra di un URL. **Non è
  risolto il requisito di assenza di link alterati.**
- Secondo gruppo Sonnet: **8/8 valide, 6/8 promosse**. Passano B07/B11/B15/
  B19/B21/B22; B01 aggiunge un box finale e B20 salta la verifica degli estremi
  nel formato prescritto. Totale Sonnet **9/12**. I risultati negativi sono
  conservati e non sostituiti con nuovi tentativi.

La revisione beta è chiusa con archivio rigenerato, report e controlli locali.
Non restano test in corso né attese della quota. Le ulteriori correzioni per
una versione stabile sono lavoro successivo su una nuova candidata: priorità
alla verifica dei collegamenti prima dell'invio e all'uso esclusivo dei tool
MCP per le ricerche. Non ripetere i casi bocciati di C6 per alzare il punteggio.

## Prima azione alla prossima ripresa

Leggere il rapporto v9.1 e questa apertura, prima della cronologia archiviata.
La domanda facoltativa «proseguire verso una stabile oppure chiudere la beta?»
non ha ricevuto risposta nella sessione precedente; l'assistente ha dichiarato
di chiudere la revisione beta, coerentemente con l'handoff. Non trasformare
questa scelta operativa in una richiesta dell'utente di promozione stabile.

Se viene richiesto di arrivare alla stabile, partire da una **nuova candidata**
senza alterare le risposte C6. Priorità concrete:

1. B23 Sonnet: la fonte restituisce un URL che termina in `66194858`, mentre
   la risposta termina in `66194758`. Valutare un controllo automatico della
   bozza contro le fonti **prima dell'invio**: è un'ipotesi di lavoro, non una
   funzione già implementata. Il controllo attuale dei link opera nel runner
   dopo la risposta, e non previene l'errore nell'uso ordinario della skill.
2. Haiku B12/B13: l'avviso funziona, ma tutti e sei i tentativi violano il
   vincolo sulla shell; uno omette anche la ricerca MCP. Le autorizzazioni
   bloccano i comandi estranei, ma questo non rende corretto il comportamento.
3. B01 Sonnet: box finale vietato. B20 Sonnet: sostituzione del tipo di atto
   con un alias senza la verifica richiesta. Conservare questi esiti come
   difetti distinti dalla fedeltà degli URL.

Per nuovi test con modelli, mantenere **solo l'abbonamento Claude**,
`--solo-abbonamento` e un modello esplicito; tetto predefinito di 5 USD stimati
per modello/invocazione. Le stime CLI non sono addebiti attestati. Non usare
OpenRouter, proxy API o crediti extra come sostituti. Censimento dei 32
calcolatori, fallback manuale senza shell e suite completa su altri modelli
restano non collaudati.

Controllo locale disponibile, senza chiamate a modelli o al servizio:

```bash
UV_CACHE_DIR=/private/tmp/buddalaw-uv-cache uv run --offline --no-project --with pytest --python /opt/homebrew/bin/python3.14 python -m pytest -q buddalaw/tests
```

Ultima esecuzione del 18 ottobre: **144 superati, 12 live saltati**. Non è
stata ripetuta per questo aggiornamento esclusivamente documentale.

## Prove da conservare

Sotto `buddalaw/tests/e2e/results/` (ignorato da Git):

| Cartella | Contenuto |
|---|---|
| `20261018-182214-129330` | C4, istruzioni soltanto: B12 0/3 |
| `20261018-182552-973666` | C5, primo B12 con script: 1/1 |
| `20261018-182744-292618` | C5, altre due prove: avviso presente, limite turni; non valutabili |
| `20261018-183031-596856` | C6 Haiku, usare `rivalutazione.json`: 0/6 promosse |
| `20261018-183329-097605` | C6 Sonnet, avvisi e conversazioni: 3/4 |
| `20261018-184206-338009` | C6 Sonnet, otto controlli mirati: 6/8 |

Arresto condiviso della nuova campagna:
`tests/e2e/results/20261018-c6-claude-pro/STOP`.
Al primo guasto o esaurimento della quota fermarsi senza ritenti; non
cancellare gli arresti precedenti. Non pubblicare tracce grezze né leggere
file di credenziali. Lasciare intatte le cartelle non tracciate preesistenti
`.claude/`, `logs/`, `migliora-chiarezza-testi-legali/tests/blind/` e
`migliora-chiarezza-testi-legali/tests/runs/`.

## Cronologia v9.0 conclusa — non è la lista corrente di attività

<details>
<summary>Handoff storico della v9.0, già unita a main</summary>

# BuddaLaw v9.0 — Passaggio di consegne

**Data:** 2026-10-18
**Branch corrente:** `main`, allineato a `origin/main` · **Rilascio:** beta
**PR unita:** [#1](https://github.com/avvocati-e-mac/skill-legali/pull/1), il 18 ottobre 2026 alle 15:15:36 Europe/Rome
**Commit di merge:** `82938b67a72ab48d8c420af549aae8f139effe42`
**Branch di collaudo conservato:** `feat/buddalaw-v9`
**Piano di riferimento:** il piano «BuddaLaw v9.0: skill allineata al server reale, avviso di obsolescenza, test a tre livelli» (riassunto qui sotto)


## Chiusura del 18 ottobre dopo il ripristino Pro

Il lavoro «finire test skill e passare a main» è **concluso**: la PR è stata
unita e il repository locale è già su `main`. Non restano prove da completare
per questa campagna, attese della quota o operazioni di merge da ripetere.
La versione rimane **beta**, con limiti espliciti nel README e nel rapporto.
Questa sezione e le istruzioni di ripresa qui sotto prevalgono sulla cronologia
archiviata, che conserva anche decisioni e comandi ormai superati.

- **128/128 controlli offline**, archivio coerente con i sorgenti; 12 live saltati
  nel comando ordinario. Contratto live verificato in precedenza e inventario
  esteso ai 48 tool reali; calcolatori non collaudati.
- C3: **62/62 prove previste tentate, 61 valide**. B04 r3 raggiunge il limite di
  otto turni; non viene trasformata in un successo né ripetuta per cambiare esito.
  Modello della campagna e del confronto: `claude-haiku-4-5-20251001`.
- Qualità: **16/24 casi valutabili**, critici **12/16 (75%)**. La soglia del 90%
  non è raggiunta. B12/B23 omettono l'avviso; B01/B19 hanno URL non fedeli;
  restano violazioni sui link normativi e sulla lingua. **Nessuna promozione stabile.**
- B21 ×3, B22 ×3 e B25 ×1 sono concluse dopo le 15:00 in
  `20261018-150152-757858`, **7/7 valide**: casi promossi rispettivamente 2/3,
  3/3 e 1/1. I virgolettati B22 corrispondono ai campi testuali delle fonti.
- Le sei registrazioni B21/B22 senza prova valida della vecchia tornata sono
  conservate e sostituite solo nel conteggio delle prove previste: 68 registrazioni
  grezze, 62 prove, 61 valide. Nessun tentativo comportamentale bocciato è ripetuto.
- Confronto v8.4/nessuna: **34/34 registrate, 33 valide**; qualità **11/16** e
  **5/15**. B22 senza skill è non valutabile per limite di turni. Non confrontare
  queste percentuali come garanzie statistiche o con i vecchi campioni.
- Solo **Claude Pro**, nessuna API/OpenRouter sostitutiva o attivazione di crediti
  extra. Ripristino della quota confermato dagli eventi nativi. La scelta originale
  di completare le prove prima di main è stata mantenuta, attendendo il ripristino.
- Hash C3 invariato:
  `1ce58fd6d54a617eb7bd176df5a9b304e4f89a012c2646a6d2f2f46897f0647f`.
  Le copie installate e le cartelle di lavoro preesistenti non sono state aggiornate.

Il collaudo richiesto è chiuso e documentato. Le eventuali correzioni successive
ai difetti osservati richiedono una nuova candidata e una nuova valutazione,
conservando questi risultati: non sono prove mancanti da ritentare per alzare
il punteggio. Per gli esiti per caso vale `REPORT-test-v9.0.md`, in apertura.

## Alla prossima ripresa

L'aggiornamento di questo handoff non avvia nuovi collaudi né correzioni.
Se il maintainer chiede di migliorare la beta:

1. Leggere prima l'apertura di [REPORT-test-v9.0.md](REPORT-test-v9.0.md),
   poi [tests/README.md](tests/README.md) e il
   [piano di collaudo](PIANO-collaudo-v9-red-team.md). Le parti storiche del
   piano non autorizzano OpenRouter o proxy API.
2. Partire da `main` con un nuovo branch e una nuova candidata. Priorità:
   fedeltà dei link B01/B19; avviso di aggiornamento B12/B23; link normativi
   B07/B15/B20; risposta in italiano B11. In B01 r3 restano anche chiamate
   con dominio errato e superamento del limite di letture.
3. Conservare hash, risposte ed esiti C3. Ogni modifica della skill richiede
   un nuovo hash, archivio `.skill` coerente e una nuova tornata identificata.
   Non ripetere le risposte bocciate della candidata congelata per alzare il
   punteggio. B04 resta non valutabile per il limite di otto turni.
4. Usare esclusivamente Claude in abbonamento per eventuali nuovi test con
   modelli, con le protezioni descritte sotto. Fermarsi alla quota esaurita o
   al primo guasto, preservando lo `STOP`. Non cancellare i vecchi arresti.
5. Non dichiarare collaudata l'intera suite C3 su Sonnet, Codex, Qwen o
   DeepSeek: non è stata completata su quei modelli. I 32 nuovi calcolatori
   sono censiti nell'inventario, ma non collaudati nel comportamento.

**Prove da conservare**, sotto `buddalaw/tests/e2e/results/` (ignorate da Git):

| Cartella | Contenuto |
|---|---|
| `20261018-123513-403307` | C3, B12: 0/3, tre prove valide |
| `20261018-123724-623063` | C3, altri casi prima della quota: 58 registrazioni, 51 valide |
| `20261018-150152-757858` | Ripresa delle sette prove mancanti: 7/7 valide |
| `20261018-123806-605934` | Confronto v8.4/nessuna: 34 registrazioni, 33 valide |

Per le valutazioni usare `rivalutazione.json` e i file `.esito.json` aggiornati;
non i vecchi conteggi precedenti alle correzioni del valutatore. Le rivalutazioni
non modificano risposte e tracce originali. I sei record esclusi per quota o
arresto restano nella vecchia tornata; B04 r3 è invece una prova del modello
fermata dal limite e non viene sostituita. Conservare anche
`results/20261018-c3-claude-pro/STOP`.

Le copie installate in `~/.claude/skills/`, `~/.codex/skills/` e quelle in
Downloads non sono state aggiornate. Non aggiornarle in una semplice ripresa
del collaudo. Lasciare intatte le cartelle non tracciate preesistenti `.claude/`,
`logs/`, `migliora-chiarezza-testi-legali/tests/blind/` e
`migliora-chiarezza-testi-legali/tests/runs/`. Non pubblicare tracce grezze né
leggere file di credenziali.

Ultimo controllo completo senza rete: **128 superati, 12 live saltati**:

```bash
UV_CACHE_DIR=/private/tmp/buddalaw-uv-cache uv run --offline --no-project --with pytest --python /opt/homebrew/bin/python3.14 python -m pytest -q buddalaw/tests
```

## Vincolo del maintainer: solo abbonamento Claude

Il 18 ottobre il maintainer ha precisato: «usa l'abbonamento di claude non
sprecare i miei soldi su openrouter». Questa istruzione prevale sui comandi
storici qui sotto: **non riprendere OpenRouter né i verificatori con proxy API**.
Le tornate OpenRouter incomplete restano tali e non vanno presentate come
verifica conclusa dei relativi modelli. Il passaggio a `main` è già avvenuto.

- Accesso della CLI verificato: `claude.ai`, `firstParty`, abbonamento `pro`;
  nessuna chiave API nell'ambiente. Il programma ora offre
  `--runtime claude --solo-abbonamento --modello <modello Claude esplicito>`:
  se non verifica l'abbonamento o trova variabili API, non avvia il modello.
  Il manifest conserva solo questi tre dati, senza identificativi personali.
- Controlli offline aggiornati: **128/128**, più 12 live saltati.
- I valori USD dei test Claude sono stime dei token riportate dalla CLI,
  **non addebiti attestati**. Non sommarli ai costi OpenRouter come se fossero
  fatturazione aggiuntiva. Riferimento: [Anthropic](https://code.claude.com/docs/en/costs).

## Cronologia archiviata — non è una lista di attività da eseguire

Le note seguenti documentano le tappe precedenti alla chiusura e al merge.
Le indicazioni di PR in bozza, prove mancanti, attese delle 15:00, decisioni
pendenti e comandi OpenCode/OpenRouter sono superate. Anche le frasi interne
che dichiarano una sezione prevalente si riferiscono al momento storico:
per riprendere valgono esclusivamente lo stato conclusivo e i vincoli sopra.

<details>
<summary>Mostra le note storiche del 17–18 ottobre</summary>

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
- Tornata fermata sulla quota Claude Pro del 18 ottobre (ripristino alle **15:00 Europe/Rome**): altri 25 casi v9, 59 esecuzioni
  previste (`20261018-123724-623063`): **58 registrate, 51 valide** dopo la
  rivalutazione offline; confronto v8.4/nessuna concluso: 34/34 esecuzioni, 33 valide
  (`20261018-123806-605934`). In rivalutazione finale: v8.4 **11/16** casi
  di qualità; nessuna skill **5/15**, con B22 non valutabile per limite di turni. B13 v9 passa 3/3. Arresto condiviso separato in
  `results/20261018-c3-claude-pro/STOP`, da conservare se creato.
- Valutatore corretto nei commit `a89ce62` e `a0e2859`: riconosce domini
  alterati e Markdown incompleto, e la presenza dei tool anche dopo l'avvio
  tramite riferimenti nativi ToolSearch o `check_access` riuscito. Rimuove
  soltanto il vecchio falso errore «tool BuddaLaw assenti», conservando gli
  altri errori di isolamento. Rivalutare le tracce senza nuove chiamate.
- In C3 B01 r1 il modello scrive `buddaslaw.com` e omette la parentesi finale
  del link; r3 ripete quattro volte il dominio errato `tribunario`. Sono
  difetti della risposta, da conservare. Il falso errore di isolamento r3
  viene corretto dalla prova nativa di accesso; la risposta resta bocciata.
- B04 r3 termina con `error_max_turns`: limite del canale, non prova valida.
  Non ripetere le risposte comportamentali fallite. Per completare le prove
  bloccate dalla quota restano B21 ×3, B22 ×3 e B25 ×1; usare una nuova tornata
  solo dopo il ripristino, preservando gli originali e il vecchio STOP.
- Nei primi 68 eventi d'uso C3 controllati, `isUsingOverage=false` e
  `overageDisabledReason=org_level_disabled`: nessun consumo extra attivo.
- Quota: tre tentativi B21 e due B22 sono stati rifiutati prima del modello,
  senza chiamate BuddaLaw né consumo extra. B22 r3 è fermata manualmente,
  B25 non è avviata. La vecchia tornata non riconosceva la quota nativa prima
  del caso successivo; `3a52716` corregge lo stop, con due prove offline.
  Un evento `rate_limit_event.status=rejected` ferma ora subito la tornata;
  `overageStatus=rejected` con quota ancora disponibile non la ferma.
- Bilancio C3 parziale (incluso il B12 separato): **61/62 registrate, 54 valide**.
  Qualità: **13/21** casi valutabili; B04/B21/B22 non valutabili, B25 mancante.
  Due casi v9 contengono URL non fedeli (B01 e B19): nessuna promozione stabile.
- Decisione di tempistica richiesta al maintainer: attendere il ripristino delle
  15:00 per completare, oppure portare subito la beta su main con test incompleti
  dichiarati. Nessuna risposta ricevuta al momento di questo aggiornamento;
  l'istruzione originale resta completare i test prima del passaggio a main.
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
il vecchio valutatore segnalava zero link inventati su 114 esecuzioni
(dato non ricertificato dal controllo attuale), ≈ 0,94 $ di token stimati. Non sommare questi dati alle
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

</details>

</details>

</details>
