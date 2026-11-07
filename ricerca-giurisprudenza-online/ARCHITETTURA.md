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

### Aperto
- Prova reale di Claude in Chrome su ilcaso.it (lettura PDF) e annotazione nel profilo.
- Profili giustizia-amministrativa, giustizia-tributaria, cassazione ancora "DA COMPLETARE".

## Rinomina 2026-11-07
Nome cambiato da `ricerca-giurisprudenza` a `ricerca-giurisprudenza-online` (cartelle, frontmatter, `.skill`, metadati Codex), su richiesta dell'autore, per chiarezza: la skill cerca su siti pubblici online, non in banche dati MCP. Chi aveva installato la versione del convegno con il vecchio nome deve disinstallarla, altrimenti due skill quasi uguali competono per le stesse richieste.
