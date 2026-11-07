# Architettura e decisioni — ricerca-giurisprudenza-online

## Origine
Skill del convegno CC Ravenna (9 ottobre 2026), importata nel repository il 2026-11-07 senza modifiche (commit "importa la skill originale"), poi adattata.

## Adattamento 2026-11-07: ambienti e browser

### Problema
La versione del convegno presupponeva il **browser integrato** (`Claude_Browser`), che esiste solo nell'app desktop di Claude. In Claude Code da terminale/IDE esiste solo **Claude in Chrome** (`claude-in-chrome`): su siti come ilcaso.it, dove WebFetch rifiuta le schede, la skill andava sempre in arresto (b). In Codex mancavano equivalenze per Agent, WebSearch `allowed_domains` e red team.

### Decisioni
- Scelta del browser in Fase 0 **sugli strumenti presenti**, riconosciuti per sottostringa (prefissi diversi in desktop e sessioni remote): browser integrato > Claude in Chrome > browser di Codex > nessuno. Dettagli in `references/ambienti.md`, letto solo in Fase 0 (progressive disclosure).
- Ramo desktop **invariato** nel comportamento, per non far regredire chi la usa nell'app.
- Chrome è il browser personale dell'utente: schede nuove, solo pagine pubbliche, stop su contenuti riservati visibili grazie ai suoi accessi, nessun download in massa dal browser (scarica `scarica.py`, che non usa i cookie del browser), estrazione solo dall'orchestratore in sequenza.
- **Regola robots unica:** decide il `robots.txt` del sito, non il messaggio dello strumento. ilcaso.it (controllato il 2026-11-07): `User-agent: *` + `Disallow:` vuoto, quindi il rifiuto di WebFetch è una politica dello strumento e la lettura nel browser è ammessa.
- Codex: subagenti se disponibili; red team indipendente o, in mancanza, passaggio separato solo con il sì dell'utente e dichiarato nel report.
- Script non modificati.

### Red teaming del piano (subagente, 2026-11-07)
Rilievi accolti: contraddizione sulla regola robots (alta); pdf.js in Chrome non dimostrato (alta: segnato "da verificare al primo uso", prima `get_page_text`); siti in abbonamento con login già attivi nel Chrome dell'utente (alta); nomi strumenti con prefisso `remote-devices`, `enable__*`, più Chrome collegati, estensione non connessa (media); subagenti senza accesso a Chrome (media: estrae l'orchestratore); ramo Codex e red team (media); regressione desktop e reinstallazione del `.skill` (media); `ARCHITETTURA.md` (bassa); test fragili su stringhe (bassa); commit separati (media).
Rilievi respinti: `__pycache__` nello zip (falso: era un artefatto della verifica locale, lo zip originale non lo contiene).
Rilievo rimesso all'autore: user-agent da browser in `scarica.py`/`scarica.sh`. Deciso il 2026-11-07: user-agent onesto `ricerca-giurisprudenza-online/1.0 (+URL del repository)`; se un sito rifiuta, nessun camuffamento né ritento: link da aprire a mano nel report. Effetto collaterale: le regole robots.txt dedicate a questo nome ora si applicano davvero (`can_fetch` usa il nome).

### Prova reale con Claude in Chrome (2026-11-07, Claude Code da terminale, estensione in Brave)
- Scelta dell'ambiente: nessuno strumento `Claude_Browser`, strumenti `claude-in-chrome` presenti, un solo browser collegato → Claude in Chrome. Corretto.
- ilcaso.it, provvedimento 32960: `get_page_text` sul PDF fallisce; pdf.js 3.11.174 da cdnjs via `javascript_tool` legge 13 pagine e 29.535 caratteri. Trappola: senza `await` iniziale lo strumento restituisce `{}`. Annotato in `ambienti.md`.
- Scheda HTML leggibile; il menu "PREMIUM" presente su ogni pagina dava un falso segnale di contenuto riservato: annotato nel profilo.
- `scarica.py` e `scarica.sh` con user-agent onesto: PDF scaricato (`%PDF-1.7`, 380 kB), uscita 0.
- Scheda del browser creata e chiusa; nessuna scheda dell'utente toccata.

### Aperto
- Profili giustizia-amministrativa, giustizia-tributaria, cassazione ancora "DA COMPLETARE".

## Rinomina 2026-11-07
Nome cambiato da `ricerca-giurisprudenza` a `ricerca-giurisprudenza-online` (cartelle, frontmatter, `.skill`, metadati Codex), su richiesta dell'autore, per chiarezza: la skill cerca su siti pubblici online, non in banche dati MCP. Chi aveva installato la versione del convegno con il vecchio nome deve disinstallarla, altrimenti due skill quasi uguali competono per le stesse richieste.

## Schede e report generali (2026-11-07)
Su indicazione dell'autore ("i report devono essere generali, non specifici come l'esempio originale"): la ricerca di prova sugli appalti (costi della manodopera, art. 108 c. 9 d.lgs. 36/2023) aveva messo "altro" in tutte le 8 schede, perché `conseguenze_legate_al_tema` ammetteva solo voci del tema del convegno (art. 96 c.p.c., trasmissione all'Ordine, spese). Ora è una lista di frasi libere (max 12 parole, `["nessuna"]` esclusiva); `conteggi.py` le conta come scritte; `controlli.py` non ha più elenchi fissi e generalizza l'avviso di coerenza (obiter/marginale). Regole di bozza e red team con formule generali.
Scartata la proposta del valutatore di "campi specifici per tema": contraria alla scelta di schede generali.

## Ottimizzazione dei modelli (2026-11-07)
Obiettivo dell'autore: per ogni compito, il modello meno costoso che lo risolve. Misure su una ricerca reale (appalti, 8+1 provvedimenti, giustizia-amministrativa.it, lettura da terminale):

| Fase | Modello | Token / chiamate | Esito |
|---|---|---|---|
| Estrazione schede (4 provv.) | haiku | 162k / 21 e 148k / 20 | meccanico perfetto (31/31 citazioni, estremi corretti); sovrastima "decisivo" 7/8 (reali 5), un obiter come ratio, un'indicazione parziale come omissione |
| Estrazione (1 provv., PDF già scaricato) | haiku | 95k / 11 | idem |
| Bozza | sonnet | 74k / 6 | buona, ma eredita le sovrastime |
| Red team | sonnet | 106k / 13 | 10 rilievi di calibratura reali, nessun falso positivo |
| Valutazione contro banca dati esterna | sonnet | 85k / 12 | trova lacune (contrasto d'appello) |
| Ricognizione sito nuovo | sonnet | 57k / 9 | si ferma davanti al blocco anti-robot |
| Censimento 9 fonti | sonnet | 75k / 15 | ok |
| Controlli e conteggi | script Python | 0 | già così |
| Interrogazioni | orchestratore (il più costoso) | - | da delegare |

Scelte: haiku per il meccanico; qualificazioni fini verificate da sonnet solo sulle schede "decisivo"/`tema_causa=si` (alternativa scartata: sonnet su tutte, più caro); interrogazioni delegabili a subagente economico con elenco deciso dall'orchestratore; risalita di un livello solo su segnali precisi; modelli usati annotati nel report. Dettaglio operativo in `references/modelli.md`.

## Metodo di ricerca dopo la valutazione con BuddaLaw (2026-11-07)
La ricerca di prova (appalti) valutata contro BuddaLaw: copertura 2/5, correttezza 3/5, prudenza 4/5, utilità 3/5. Mancava un contrasto d'appello (pronuncia del giudice d'appello che ammette il soccorso istruttorio contro TAR rigidi) perché nessuna interrogazione era mirata all'organo di vertice. Correzioni: interrogazioni distinte per grado/organo con almeno una per il vertice e una "di contrasto"; giro sui precedenti citati da più schede; sezione **Contrasti** obbligatoria nella bozza; con meno di 10 schede "in N pronunce lette"; red team con controllo di copertura per grado.
Red team della bozza: 10 rilievi di calibratura (ruolo "decisivo" sovrastimato 7/8 → 5/8; obiter preso per ratio; indicazione parziale descritta come omissione), nessuna citazione o estremo errato (31/31).

## Regola robots / termini d'uso e nuove fonti (2026-11-07)
Decisa dall'autore: siti pubblici e istituzionali → lettura mirata ammessa anche contro robots.txt (atti pubblici, nessuna raccolta in massa, report e non database); siti privati → prima i termini d'uso. Scaricamento automatico sempre conforme a robots.txt. Captcha e blocchi anti-robot mai aggirati (captcha risolto dall'utente). Censimento fonti (da terminale): Garante, ANAC, AGCM leggibili; Corte di giustizia UE solo browser; Corte costituzionale (captcha) ed EUR-Lex (sfida anti-robot) bloccati. Giustizia tributaria: 403 Akamai da terminale; nel browser si apre senza verifiche; testo in riquadro Adobe non leggibile → lettura tramite "Scarica provvedimento" con consenso dell'utente. Verificato anche che i subagenti possono usare Claude in Chrome.
