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
- Solo pagine pubbliche del SITO scelto (le regole su robots.txt e blocchi sono nella sezione 3). Se una pagina mostra contenuti riservati o in abbonamento visibili perché l'utente è già collegato, fermati e chiedi (arresto a): non leggerli e non scaricarli senza il suo sì esplicito per quel sito.
- Il browser serve a LEGGERE, un provvedimento alla volta. Niente scaricamenti in massa dal browser: i PDF li scarica `scarica.py`, che non usa gli accessi del browser e rispetta sempre robots.txt.
- Niente credenziali, niente pulsanti che aprono finestre di conferma o alert, niente aggiramento di login, captcha, SPID o blocchi anti-robot (se compare un captcha lo risolve l'utente).
- Estrazione: con Chrome un subagente alla volta (verificato il 2026-11-07: i subagenti di Claude Code possono usare Claude in Chrome), oppure tu, in sequenza: il browser è uno solo, mai subagenti in parallelo sullo stesso Chrome.
- PDF: `get_page_text` di solito NON legge i PDF aperti nel visore ("No text content found"); usa pdf.js da cdnjs con `javascript_tool`, come nel browser integrato (verificato su ilcaso.it). Il codice deve iniziare con `await` e restituire una stringa (es. `JSON.stringify(...)`): una funzione asincrona senza `await` restituisce `{}` vuoto, senza errore. Su un sito nuovo il metodo è da verificare al primo uso: se non funziona, segna il provvedimento come non letto (arresto e) e annota il risultato nel profilo.
- Brave, Edge e gli altri browser basati su Chromium con l'estensione installata valgono come Chrome.

## 3. robots.txt, termini d'uso e blocchi anti-robot
Regola decisa dall'autore della skill. Distingui il tipo di sito (è scritto in testa a ogni profilo: "Tipo di sito").

**Siti pubblici e istituzionali** (giustizia amministrativa, giustizia tributaria, Corti, Garante, ANAC, AGCM, istituzioni UE): la lettura MIRATA dei provvedimenti della ricerca è sempre ammessa, anche se `robots.txt` vieta il percorso. Questi siti pubblicano atti pubblici e la skill non fa raccolta in massa: pochi provvedimenti, uno alla volta, con pause, user-agent onesto, risultato in un report e non in un database. Non serve controllare i termini d'uso. Cita sempre la fonte.

**Siti privati** (riviste, editori, banche dati commerciali, come ilcaso.it): se `robots.txt` vieta il percorso, prima di leggere controlla i termini d'uso. Se vietano l'uso automatico, è arresto (vedi `arresto.md`): chiedi all'utente.

**Scaricamento automatico** (`scarica.py`, `scarica.sh`): rispetta `robots.txt` su TUTTI i siti, anche pubblici. È la parte "meccanica". Se `robots.txt` vieta il download, il report elenca i link da aprire a mano.

**Captcha e blocchi anti-robot** (403 "Access Denied" di Akamai, sfide JavaScript, captcha Radware): non aggirarli MAI, né cambiando user-agent né risolvendo il captcha. Si può solo aprire nel browser un sito che si apre normalmente, senza verifiche. Se compare un captcha, lo risolve l'UTENTE nel browser; poi la skill prosegue un provvedimento alla volta (come per i login).

**Nel report**: dichiara nei limiti ogni volta che hai letto un percorso vietato da `robots.txt` (sito, quanti provvedimenti).

Per controllare `robots.txt`: `python3 -c "import urllib.robotparser as r;p=r.RobotFileParser('https://<dominio>/robots.txt');p.read();print(p.can_fetch('*','<url>'))"`.
Se `robots.txt` permette ma WebFetch rifiuta per sue politiche (es. `robots_disallowed` dello strumento), puoi leggere quel provvedimento nel browser, uno alla volta.

## 4. Equivalenze tra ambienti

| Nella skill | Claude (desktop, Cowork, Claude Code) | Codex / OpenAI |
|---|---|---|
| Subagenti | strumento Agent, `subagent_type` "general-purpose", `model` secondo `references/modelli.md` | subagenti di Codex se disponibili; altrimenti fai tu le fasi e dillo in una riga |
| Ricerca sul sito | WebSearch con `allowed_domains` (l'operatore `site:` viene ignorato) | ricerca web nativa limitata al dominio (con `site:` se lo strumento lo supporta); dichiara come hai filtrato |
| Lettura pagine | WebFetch | lettura web nativa o shell (`curl`), rispettando la regola robots |
| Red team (Fase 7) | subagente sonnet, obbligatorio | subagente indipendente se disponibile; altrimenti chiedi all'utente se accetta una revisione in un passaggio separato, scritta in `lavoro/red_team.md` prima di rileggere la bozza, e dichiaralo nel report. Mai un'autorevisione presentata come red team. |
| Script | `python3` da shell | uguale |

## 5. Skill Docling e pagine dei PDF (Fase 0, punto 2; Fase 5)
Serve solo ai provvedimenti scaricati come PDF. Gli HTML restano citati per punto/paragrafo ("punto 6.3"): è la forma corretta, non un difetto. Non usare mai il flusso o `SKILL.md` della skill `docling-citazioni-pdf` (carica i PDF interi nel contesto): di quella skill si usa solo lo script check_pdf_quote.py, lanciato da `pagine.py`.

**1. La skill è installata?** Prima guarda l'elenco delle skill disponibili nel contesto (anche con prefisso di plugin, es. `...:docling-citazioni-pdf`), poi le cartelle note: Claude Code `~/.claude/skills/docling-citazioni-pdf`; Codex la cartella skill di Codex. Il percorso serve per lanciarne lo script: va scoperto, non presunto, e passato a `pagine.py` con `--skill-docling "<cartella>"`. Nel dubbio chiedi all'utente; mai dichiarare "non installata" senza averlo verificato. Se non c'è: nei limiti scrivi "pagine PDF verificate solo con pdftotext: skill docling-citazioni-pdf non installata (repository avvocati-e-mac/skill-legali)". `pagine.py` funziona comunque.

**2. Il server Docling MCP** (strumenti con "docling" nel nome) serve solo per scansioni, numeri stampati e struttura, non per `pagine.py`, che è locale e verifica le citazioni sul PDF scaricato. Distingui:
- non configurato: nessuno strumento "docling" e nessuna voce nella configurazione MCP;
- configurato ma non connesso (es. ECONNREFUSED): non ritentare in ciclo e non toccare la configurazione;
- connesso.
Distingui anche server **locale** o **remoto**: remoto se l'URL MCP non è `localhost`/`127.0.0.1`. Con un server remoto (altro computer, rete privata) e rifiuto della connessione, se l'host risponde al ping il messaggio all'utente è: "il server Docling sul computer remoto non è avviato". Non provare ad avviare nulla sull'altro computer e non modificare la configurazione MCP. Per avviarlo rinvia alla guida server-remoto.md della skill docling-citazioni-pdf (non duplicarla); se il server non è connesso per altri motivi, rinvia alla sua guida di installazione. Nei limiti del report i messaggi sono diversi: skill assente / server non configurato / non connesso / remoto non avviato.

**3. Con un server remoto connesso** la VPN non condivide le cartelle: il server non vede `<cartella>/pdf/`, e i file che produce restano sul server. Per i provvedimenti PUBBLICI scaricati da un URL diretto (`url_file`) passa al server l'URL pubblico come sorgente (`convert_document_into_docling_document`, parametro `source`) al posto del percorso locale. Verificato il 2026-11-07 (Mac Studio via VPN, Cons. Stato n. 3008/2026, 13 pagine): conversione da URL in circa 30 secondi. Gli strumenti di ricerca e lettura NON restituiscono il numero di pagina: per ricavarlo esporta una pagina alla volta con `export_docling_document_to_markdown` e `page_no` (parte da 1, pagina fisica del PDF) e cerca la citazione INTERA, normalizzando spazi, apostrofi e trattini di sillabazione; un frammento breve si usa solo se la frase intera non si trova, e se compare in più pagine allunga il frammento prima di dichiararla ambigua (nella prova, i primi 6 termini di una citazione comparivano anche in un'altra pagina: falsa ambiguità). Esito della prova: 8 pagine su 8 uguali a `pagine.py`. Quando usarlo: soprattutto per PDF scansionati o senza testo, dove `pagine.py` dà `non_ritrovata_nel_pdf` o `non_verificabile`; costa una chiamata per pagina, quindi non ripeterlo sui PDF già verificati in locale. Annota nella riga di `pagine.jsonl` (campo `note`) che la pagina viene da Docling remoto. In ogni altro caso nessun trasferimento automatico: chiedi all'utente il canale (come dice la skill Docling). Le pagine di `pagine.jsonl` restano comunque quelle verificate sul PDF locale.

**4. Scrittura**: in `lavoro/ricognizione.md` la riga `Docling: skill sì/no; server non configurato/non connesso/connesso, locale/remoto; pdftotext sì/no`. Il metodo finale per citazione è in `pagine.jsonl`.
