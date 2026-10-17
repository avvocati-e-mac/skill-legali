# Test della skill BuddaLaw

Questa cartella contiene i controlli che dicono se la skill BuddaLaw è in ordine
e se il servizio BuddaLaw si comporta ancora come la skill si aspetta. Sono
organizzati in **tre livelli**, dal più veloce e gratuito al più completo.

---

## Struttura

```
tests/
├── README.md            ← questo file
├── CHECKLIST.md         ← elenco dei casi di prova (T01…T84), con il livello che li controlla
├── conftest.py          ← impostazioni comuni dei test
├── test_struttura.py    ← Livello A: controlli sui file, senza Internet
├── test_mcp_live.py     ← Livello C: domande vere al servizio BuddaLaw
├── fixtures/
│   ├── tool_schema.json       ← elenco ufficiale degli strumenti BuddaLaw e dei loro campi
│   └── risposte_ridotte.json  ← esempi di risposte reali, accorciati e senza nomi
├── tools/
│   ├── estrai_schema.py ← legge dal servizio l'elenco aggiornato degli strumenti
│   └── chiama_mcp.py    ← fa una singola domanda a BuddaLaw e ne restituisce la risposta
└── e2e/                 ← Livello B: conversazioni complete con un modello
```

Serve Python 3 con `pytest` (`pip install pytest`). I comandi si lanciano dalla
cartella principale del repository (`skill-legali`).

---

## Livello A — controlli sui file (veloce, gratuito)

```bash
pytest buddalaw/tests/test_struttura.py
```

Dura circa un secondo e non usa Internet. È il controllo da far passare **prima
di ogni pubblicazione**. Verifica che:

- l'intestazione di `SKILL.md` sia corretta: nome `buddalaw`, versione presente,
  descrizione entro i 1024 caratteri (oltre, Cowork rifiuta l'installazione);
- ogni file citato da `SKILL.md` esista e ogni file di `references/` sia citato;
- l'archivio `buddalaw.skill` (quello che si installa in Claude Desktop e Cowork)
  contenga **esattamente** i file attuali della skill;
- `agents/openai.yaml` (per Codex) sia leggibile;
- **ogni esempio di chiamata scritto nella skill sia accettato dal servizio**:
  strumento esistente, campi esistenti, numeri scritti come numeri, valori
  ammessi. Il confronto è con `fixtures/tool_schema.json`, che viene dal
  servizio reale e non è scritto a mano: per questo il controllo non si limita
  a confermare quello che la skill già crede;
- l'elenco degli strumenti nella sezione «Controllo di aggiornamento» coincida
  con quello del servizio, e la versione citata sia quella dell'intestazione;
- non tornino regole superate dalla v9.0 (la regola «HTTP 400», il «GUID» come
  identificativo di ogni sentenza, il campo `ufficio` nella ricerca, la parola
  «MANDATORY»);
- `CHECKLIST.md` abbia ID unici e la colonna «Automatizzato in», e che ogni caso
  segnato A o C sia davvero citato nel test di quel livello.

**Un rosso atteso.** Dopo ogni modifica ai file della skill il controllo
sull'archivio è rosso finché non si rigenera `buddalaw.skill`:

```bash
cd buddalaw
rm buddalaw.skill
zip -r buddalaw.skill buddalaw/ -x '*.DS_Store' -x '*__pycache__*'
cd ..
```

---

## Livello B — conversazioni complete

Qui un modello vero risponde a domande da avvocato con la skill caricata, usando
BuddaLaw dal vivo. Il programma `e2e/run.py` controlla poi due cose: quali
ricerche il modello ha fatto (per esempio che abbia scelto la banca dati giusta)
e che cosa ha scritto (per esempio che ogni link compaia davvero nei risultati di
BuddaLaw e stia sugli estremi della sentenza). I casi sono in `e2e/casi.json` e
richiamano gli ID della checklist segnati **B**.

Si prova la skill in tre modi:

| Dove | Modello | Prima volta |
|---|---|---|
| Claude Code | Haiku (economico) o il modello predefinito | niente: usa il collegamento a BuddaLaw di claude.ai |
| opencode + OpenRouter | Qwen 3.8 Flash (Flash-Next), DeepSeek V4.1 Flash | `opencode auth login` (scegli OpenRouter), poi `bash buddalaw/tests/e2e/prepara_opencode.sh` e, se BuddaLaw non è già collegato, nella cartella `e2e/.opencode-sandbox`, `OPENCODE_DB="$PWD/.opencode-test.db" opencode mcp auth buddalaw` |

La skill installata sul computer **non** viene usata: il programma lavora in una
cartella separata con la versione del repository, così il risultato non si
confonde con una copia vecchia.

La preparazione di OpenCode disabilita nella sola cartella di prova tutti gli
altri server MCP ereditati dalle impostazioni globali. Il runner ricontrolla
questa esclusione prima di collegarsi: se trova un altro server abilitato,
chiede di ripetere la preparazione e non avvia le conversazioni.
I relativi controlli offline si eseguono con
`python3 -m pytest buddalaw/tests/test_e2e_runner.py`.

```bash
python3 buddalaw/tests/e2e/run.py --runtime claude --config v9            # tutti i casi, 1 volta
python3 buddalaw/tests/e2e/run.py --runtime claude --config v9 --solo-lampo --runs 3
python3 buddalaw/tests/e2e/run.py --runtime claude --config v8.4,nessuna --solo-lampo   # confronto
python3 buddalaw/tests/e2e/run.py --runtime opencode --config v9          # Qwen e DeepSeek
python3 buddalaw/tests/e2e/run.py --rivaluta buddalaw/tests/e2e/results/<data>   # ricontrolla senza spendere
```

**Costi.** Con Haiku un caso costa circa 1 centesimo; con Qwen e DeepSeek ancora
meno. Il programma si ferma da solo quando la spesa supera il tetto (`--budget`,
5 $ per ogni modello). Le conversazioni registrate finiscono in
`e2e/results/`, che non viene mai pubblicata su GitHub perché può contenere
nomi rimasti in chiaro nelle sentenze.

---

## Livello C — il servizio BuddaLaw reale (a pagamento, pochi centesimi)

```bash
BUDDALAW_LIVE=1 pytest buddalaw/tests/test_mcp_live.py -v
```

Senza `BUDDALAW_LIVE=1` i test vengono saltati: **non fa parte del controllo
ordinario**. Si lancia a mano, al massimo una volta a settimana o quando si
sospetta che BuddaLaw sia cambiato.

**Cosa serve:** Claude Code installato e collegato al proprio account, con il
connettore BuddaLaw attivo e l'abbonamento valido. Non serve nessuna chiave da
copiare: le domande passano da Claude Code (`claude -p`, modello Haiku), che usa
il collegamento già fatto.

**Quanto costa:** il 17 ottobre 2026 una prova completa ha fatto 13 domande a
BuddaLaw e una lettura dell'elenco degli strumenti, per circa **0,07 $** in
tutto. A fine prova il costo viene stampato. Ogni domanda ha un tetto di 0,20 $.

**Se BuddaLaw rifiuta o limita le richieste** (errore 403, 429 o messaggi di
blocco) la prova si ferma subito e non riprova da sola. La decisione di
riprovare è di chi la lancia.

### Il controllo di obsolescenza (primo test)

Il primo test (T74) rilegge dal servizio l'elenco degli strumenti BuddaLaw e lo
confronta con `fixtures/tool_schema.json`. **Diventa rosso quando BuddaLaw
aggiunge, toglie o cambia uno strumento** e mostra le differenze, per esempio:

```
BuddaLaw è cambiato: tool nuovi, spariti o con parametri cambiati.
  - tool NUOVO: search_dottrina
  - search_case_law: parametro nuovo 'sezione'
```

Cosa fare in quel caso:

1. leggere la descrizione del nuovo strumento o del campo cambiato;
2. aggiornare `SKILL.md` e i file `references/`, compreso l'elenco nella sezione
   «Dati per il controllo di aggiornamento»;
3. rigenerare la fixture: `python3 buddalaw/tests/tools/estrai_schema.py`;
4. rilanciare il livello A, rigenerare `buddalaw.skill` e pubblicare una nuova
   versione.

Lo stesso confronto si può fare da solo, senza pytest:
`python3 buddalaw/tests/tools/estrai_schema.py --check`.

### Gli altri test

Ogni test traduce in prova una regola nata dal sondaggio del 17 ottobre 2026
(`../REPORT-sondaggio-v9.md`): lettura di una Cassazione con numero e anno,
`not_found` con il suo messaggio fisso, formato delle date diverso per banca
dati, filtro per ufficio con `list_uffici`, lettura dell'art. 2043 c.c.,
articolo abrogato (art. 594 c.p.), valori non ammessi.

I test segnati **sorveglianza** controllano stranezze del servizio su cui la
skill fa affidamento (per esempio: `tributario` accettato al posto di
`tributari`). Se uno di questi diventa rosso non vuol dire che la skill sia
sbagliata: vuol dire che BuddaLaw ha cambiato comportamento e la regola della
skill va riletta.

Una sola domanda, fuori dai test:

```bash
python3 buddalaw/tests/tools/chiama_mcp.py get_law_article '{"act": "codice_civile", "article": "2043"}'
```

---

## Tornare alla versione precedente

La versione 8.4 è conservata con l'etichetta git `buddalaw-v8.4`. Per vedere o
recuperare i suoi file senza toccare il resto del repository:

```bash
git show buddalaw-v8.4:buddalaw/buddalaw/SKILL.md          # leggere la vecchia skill
git checkout buddalaw-v8.4 -- buddalaw/buddalaw buddalaw/buddalaw.skill   # ripristinarla
```

Il secondo comando sostituisce i file attuali della skill con quelli della 8.4:
poi va fatto un commit come per ogni altra modifica.

---

## Aggiornare le copie installate

I test controllano i file di questo repository, non quelli già installati sul
computer. Dopo una nuova versione le copie installate restano quelle vecchie
finché non si aggiornano. **I test non lo fanno mai da soli.**

| Dove | Come si aggiorna |
|---|---|
| Claude Code | sostituire la cartella `~/.claude/skills/buddalaw` con la cartella `buddalaw/buddalaw` del repository |
| Codex | sostituire la cartella `~/.codex/skills/buddalaw` con la cartella `buddalaw/buddalaw` del repository |
| Claude Desktop e Cowork | in Impostazioni → Skill, rimuovere BuddaLaw e installare di nuovo il file `buddalaw/buddalaw.skill` |

Prima di sostituire una cartella conviene tenerne una copia, per poter tornare
indietro.

---

## Parole tecniche usate qui

- **Fixture:** copia ridotta di una risposta reale, salvata per i test offline.
- **Schema dei tool:** l'elenco ufficiale degli strumenti BuddaLaw e dei loro campi.
- **Headless:** l'assistente lanciato da un programma, senza finestra di chat.
- **OAuth:** il login fatto una volta nel browser, che poi resta valido.
- **Proxy:** un piccolo intermediario locale che legge solo l'elenco dei tool, mai le password.
