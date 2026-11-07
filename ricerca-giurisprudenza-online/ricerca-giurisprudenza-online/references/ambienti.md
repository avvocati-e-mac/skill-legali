# Ambiente e browser (Fase 0, punto 2)

Da leggere in Fase 0. Scegli il browser guardando gli strumenti DAVVERO disponibili (nomi, anche con ToolSearch se esiste); non indovinare e non inventare strumenti. Riconosci i nomi per sottostringa: possono avere prefissi diversi (`mcp__...`, `mcp__remote-devices__...`).

## 1. Quale ambiente e quale browser (in quest'ordine)

| Se trovi... | Ambiente probabile | Browser da usare |
|---|---|---|
| strumenti con `Claude_Browser` (o solo `enable__...Claude_Browser`: attivalo) | app desktop di Claude (Cowork, Claude Code nell'app) | **browser integrato** (preferito: separato dagli accessi personali dell'utente). Comportamento invariato rispetto al resto della skill. |
| strumenti con `claude-in-chrome` (o solo `enable__mcp__claude-in-chrome`: attivalo) | Claude Code da terminale o IDE | **Claude in Chrome**, con le regole della sezione 2 |
| nessuno dei due, ma sei in Codex/ambiente OpenAI con uno strumento browser già configurato (integrato o MCP) | Codex | quel browser, con le stesse regole della sezione 2 |
| nessun browser | qualsiasi | nessuno: solo pagine raggiungibili senza browser; se il sito ne ha bisogno, arresto (b) |

Se ci sono sia il browser integrato sia Chrome, usa il browser integrato. Se trovi più Chrome collegati (`list_connected_browsers`), chiedi all'utente quale usare. Se gli strumenti di Chrome esistono ma l'estensione non risponde o non è connessa, è arresto (b): non ritentare in ciclo.

Scrivi in `lavoro/ricognizione.md` la riga `Ambiente e browser: ...` e riportala nei limiti del report.

## 2. Regole per Claude in Chrome (e per un browser di Codex)
Chrome è il browser VERO dell'utente, con i suoi accessi già aperti.
- Prima di usarlo: se esiste la skill di Claude in Chrome, caricala; carica tutti gli strumenti Chrome con UNA sola ToolSearch; chiama `tabs_context_mcp`. Avvisa l'utente in una riga: "Userò il tuo Chrome in una scheda nuova, solo per leggere pagine pubbliche di <sito>; non tocco le altre schede".
- Lavora solo in schede nuove create da te (`tabs_create_mcp`) e chiudile alla fine. Mai riusare schede dell'utente.
- Solo pagine pubbliche del SITO scelto. Se una pagina mostra contenuti riservati o in abbonamento visibili perché l'utente è già collegato, fermati e chiedi (arresto a): non leggerli e non scaricarli senza il suo sì esplicito per quel sito.
- Il browser serve a LEGGERE, un provvedimento alla volta. Niente scaricamenti in massa dal browser: i PDF li scarica `scarica.py`, che non usa gli accessi del browser e rispetta robots.txt.
- Niente credenziali, niente pulsanti che aprono finestre di conferma o alert, niente aggiramento di login, captcha o SPID.
- Estrazione: con Chrome la fai TU (orchestratore), in sequenza; non affidarla a subagenti, che potrebbero non avere accesso a Chrome.
- PDF: `get_page_text` di solito NON legge i PDF aperti nel visore ("No text content found"); usa pdf.js da cdnjs con `javascript_tool`, come nel browser integrato (verificato su ilcaso.it). Il codice deve iniziare con `await` e restituire una stringa (es. `JSON.stringify(...)`): una funzione asincrona senza `await` restituisce `{}` vuoto, senza errore. Su un sito nuovo il metodo è da verificare al primo uso: se non funziona, segna il provvedimento come non letto (arresto e) e annota il risultato nel profilo.
- Brave, Edge e gli altri browser basati su Chromium con l'estensione installata valgono come Chrome.

## 3. robots.txt: regola unica
Decide il file `robots.txt` del sito, non il messaggio di uno strumento.
- Se `robots.txt` vieta il percorso: non ottenerlo con NESSUNO strumento (né WebFetch, né browser, né script).
- Se `robots.txt` lo permette ma WebFetch rifiuta per sue politiche (es. `robots_disallowed` dello strumento): puoi leggere quel provvedimento nel browser, uno alla volta.
- Per controllare: `python3 -c "import urllib.robotparser as r;p=r.RobotFileParser('https://<dominio>/robots.txt');p.read();print(p.can_fetch('*','<url>'))"`.

## 4. Equivalenze tra ambienti

| Nella skill | Claude (desktop, Cowork, Claude Code) | Codex / OpenAI |
|---|---|---|
| Subagenti | strumento Agent, `subagent_type` "general-purpose", `model` haiku (ricerca, estrazione) e sonnet (red team) | subagenti di Codex se disponibili; altrimenti fai tu le fasi e dillo in una riga |
| Ricerca sul sito | WebSearch con `allowed_domains` (l'operatore `site:` viene ignorato) | ricerca web nativa limitata al dominio (con `site:` se lo strumento lo supporta); dichiara come hai filtrato |
| Lettura pagine | WebFetch | lettura web nativa o shell (`curl`), rispettando la regola robots |
| Red team (Fase 7) | subagente sonnet, obbligatorio | subagente indipendente se disponibile; altrimenti chiedi all'utente se accetta una revisione in un passaggio separato, scritta in `lavoro/red_team.md` prima di rileggere la bozza, e dichiaralo nel report. Mai un'autorevisione presentata come red team. |
| Script | `python3` da shell | uguale |
