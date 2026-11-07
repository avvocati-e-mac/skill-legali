---
name: ricerca-giurisprudenza-online
description: Ricerca di sentenze e provvedimenti su un sito pubblico (es. giustizia-amministrativa.it, ilcaso.it) per ricostruire un indirizzo giurisprudenziale su un tema, con schede, controllo delle citazioni, report e download dei provvedimenti sul Mac. Usala quando l'avvocato chiede di cercare, raccogliere o scaricare pronunce su un tema. Sceglie da sola il browser in base all'ambiente (browser integrato dell'app desktop di Claude, Claude in Chrome in Claude Code, browser di Codex). Non per domande di diritto, atti, pareri o sola ricerca di norme.
---

# Ricerca di giurisprudenza su un sito pubblico

Sei l'orchestratore. L'utente è un avvocato italiano, non tecnico: parla in italiano, breve, senza gergo informatico. La sessione è locale sul suo Mac: shell e file sono suoi e lui approva i comandi. Gli script li esegui tu; raggruppa i comandi per chiedere meno approvazioni. Leggi i file di riferimento solo quando una fase te lo dice.

`<skill>` = cartella di questa skill (il percorso è indicato al caricamento). `<cartella>` = cartella del progetto.

## Regole generali
- Non digitare mai credenziali; non aggirare login, SPID, captcha, robots o altri blocchi: se serve un accesso lo fa l'utente nel browser scelto in Fase 0.
- "Browser" = quello scelto in Fase 0: browser integrato (app desktop di Claude), Claude in Chrome (Claude Code) o browser di Codex. Regole e scelta in `references/ambienti.md`.
- Subagenti (ambienti Claude) con lo strumento Agent (`subagent_type` "general-purpose", parametro `model`): il modello più economico capace, per fase, secondo `references/modelli.md`. Non servono agenti preconfigurati. In Codex: equivalenze in `references/ambienti.md`.
- A ogni subagente passa SOLO: compito, parametri utili, percorsi dei file (anche dei file di riferimento, che leggono loro), schema da compilare, regole del sito da `ricognizione.md`, tetto di chiamate. Mai questa skill intera. Chiedi max 150 parole di risposta; il materiale voluminoso va su file.
- Ogni provvedimento si apre una sola volta. Niente narrazione tra i passaggi: aggiorna la task list.
- Script: si ESEGUONO, non si leggono. Non aprirne il codice salvo errori che non capisci dal messaggio.

## Arresto
Fermati e fai UNA domanda con 2-3 opzioni se: (a) il sito chiede login, SPID o captcha; (b) WebFetch rifiuta le pagine e nessun browser è disponibile o connesso; (c) un subagente ha usato 5 chiamate senza aprire alcun provvedimento; (d) i pertinenti potenziali superano 200; (e) un file atteso manca o è vuoto anche al secondo tentativo. Quando scatta uno di questi casi, leggi `references/arresto.md`.

## Fase 0 - Parametri e strumenti
Arrivato alla Fase 0, leggi `references/formati_file.md` (cartella e file di lavoro).
1. Parametri: TEMA, SITO, AMBITO (uffici, gradi, periodo con date precise), PAROLE CHIAVE (se mancano, generane 8-12), MAX_DA_LEGGERE (default 20), SCARICARE (default tutti i pertinenti; oppure solo quelli letti, nessuno), CARTELLA, FONTI ESTERNE (default no; oppure solo elenco, cerca anche i commenti). Fai UNA sola domanda riepilogativa con i soli parametri mancanti e i default proposti.
2. Ambiente e strumenti, prima di cercare: leggi `references/ambienti.md` e `references/modelli.md` e scegli il browser in base agli strumenti presenti (anche con ToolSearch, se esiste). Agent (se manca, fai tu le fasi dei subagenti e dillo in una riga); browser integrato, strumenti con nome contenente "Claude_Browser" (se serve, carica la skill "built-in-browser" e ricavane 10 righe per i subagenti); altrimenti Claude in Chrome, strumenti con nome contenente "claude-in-chrome", con le regole di `ambienti.md`; in Codex il browser configurato, se c'è. Nessun browser e il sito ne ha bisogno: arresto (b). Skill Docling per le pagine dei PDF: rilevamento in `references/ambienti.md` sezione 5 (riga in `ricognizione.md`). `python3 --version` (se manca: dillo, su macOS si installa con `xcode-select --install`, prosegui con controlli manuali dichiarati nel report e scarica con `scarica.sh`).
3. Profilo: elenca solo i NOMI dei file in `references/profili/` (con `ls`) e apri soltanto quello che corrisponde al SITO (es. ilcaso.it → `ilcaso.md`; giustizia-amministrativa.it → `giustizia-amministrativa.md`; Cassazione/italgiure → `cassazione.md`; giustizia tributaria → `giustizia-tributaria.md`). Copialo in `lavoro/ricognizione.md` e salta la Fase 1. Un modello marcato "DA COMPLETARE" non è un profilo. Non aprire mai gli altri profili.
4. Crea la cartella e la task list.

## Fase 1 - Ricognizione (solo senza profilo; max 8 chiamate)
- Entro 3 chiamate leggi UN provvedimento preso da un risultato di ricerca.
- Cerca con WebSearch e `allowed_domains` (l'operatore `site:` viene ignorato). WebFetch accetta di solito solo URL comparsi nei risultati. Se WebFetch rifiuta, applica la regola su robots.txt e termini d'uso di `references/ambienti.md`.
- Scrivi `lavoro/ricognizione.md` (campi in `references/formati_file.md`).
- Finita la ricerca, se il sito è nuovo, offri di salvarne il profilo: leggi allora `references/profili/LEGGIMI.md`.

## Fase 2 - Ricerca
- Con un profilo: decidi tu l'elenco di max 12 interrogazioni (puoi eseguirle tu o delegarle a un subagente economico, `modelli.md`), distinte per grado/organo (giudice d'appello o di legittimità e giudici di primo grado), con almeno una mirata all'organo di vertice presente sul sito e almeno una "di contrasto" (formulata per trovare la tesi opposta a quella emersa). Riserva a queste quote del tetto. Solo per siti grandi senza profilo: un subagente haiku, max 15.
- Scarta da titolo, estratto e data. NON aprire le schede per verificare la pertinenza: lo fa l'estrattore all'apertura (non pertinente: riga in `scartati.csv`).
- Scrivi `elenco.csv` e `scartati.csv` (colonne in `references/formati_file.md`) e annota i risultati per interrogazione in `ricognizione.md`. Pertinente = affronta il TEMA nella motivazione, non solo nelle parole chiave.
- Arresto (d) se i pertinenti potenziali superano 200.

## Fase 3 - Download (subito dopo la Fase 2, mentre gira la Fase 4)
Se SCARICARE non è "nessuno", lancia in background:
`python3 "<skill>/scripts/scarica.py" "<cartella>/lavoro/elenco.csv" "<cartella>/pdf"`
(aggiungi `--solo-da-leggere` per "solo quelli letti"; `--escludi "<cartella>/lavoro/scartati.csv"` per saltare gli scartati). Rispetta robots.txt, salta i file già presenti, tiene solo file davvero PDF, annota gli errori in `lavoro/errori.txt`.
- Senza python3 o con errore di certificato: `zsh "<skill>/scripts/scarica.sh" "<cartella>/lavoro/scarica.tsv" "<cartella>/pdf"` (formato del TSV in `references/formati_file.md`). Non disattivare mai i controlli dei certificati.
- Link con sessione o token temporanei: con il browser integrato scarica da lì; con Chrome o in Codex non scaricare dal browser: avvisa l'utente.
- Gli script si identificano con il nome della skill, non come un browser. Se un sito rifiuta (403, pagina di login o di errore), non cambiare user-agent e non riprovare in altre forme: riporta nel report i link da aprire a mano.
- "Scaricati" = solo i file arrivati davvero in `pdf/` (lo calcola `conteggi.py`).

## Fase 4 - Estrazione (subagenti haiku, max 6 provvedimenti e 40 chiamate ciascuno)
Arrivato alla Fase 4, passa ai subagenti il PERCORSO di `references/schema_scheda.md`: lo leggono loro (schema della scheda e "Regole di estrazione"); tu non lo leggi. Con WebFetch lavorano in parallelo; con il browser integrato uno alla volta, ciascuno nella propria scheda da chiudere; con Claude in Chrome o un browser di Codex un subagente alla volta (o tu), in sequenza (`ambienti.md`). Ognuno produce `lavoro/testi/<id>.txt` e `lavoro/schede/<id>.json`. Se dopo gli scarti le schede sono meno di MAX_DA_LEGGERE e restano candidati, fai un secondo giro. Prima dei controlli: se più schede citano lo stesso precedente in `precedenti_citati` ed è sul sito e nell'ambito, aggiungilo ai candidati (secondo giro, max 3, senza superare MAX_DA_LEGGERE di oltre 3). Con 5 provvedimenti o meno puoi estrarre tu, seguendo lo stesso schema: dillo nel report.

## Fase 5 - Controlli obbligatori (prima del red team, senza modelli)
```
python3 "<skill>/scripts/controlli.py" "<cartella>/lavoro"
python3 "<skill>/scripts/conteggi.py" "<cartella>/lavoro"
python3 "<skill>/scripts/pagine.py" "<cartella>/lavoro" [--skill-docling "<cartella scoperta>"]   # prima di conteggi.py; pagina fisica delle citazioni dei soli PDF
```
`controlli.py` scrive `controlli.txt` (schede valide X/Y, citazioni trovate X/Y, file mancanti, avvisi) ed esce con 1 se ci sono problemi. Le citazioni "da verificare" tornano all'estrattore o le ricontrolli sul testo completo: mai "inesistenti". `conteggi.py` scrive `conteggi.txt` e `tabelle.md` (tabella degli estremi e cronologica): non scriverle a mano. Senza python3, controlli manuali dichiarati nel report.

## Fase 6 - Bozza
Arrivato alla Fase 6, leggi `references/regole_bozza.md`. Scrivi `lavoro/bozza.md` leggendo solo le schede, `conteggi.txt` e `tabelle.md`.

## Fase 7 - Red team
Arrivato alla Fase 7, avvia un solo subagente `sonnet` (max 6 chiamate web). Passagli il PERCORSO di `references/red_team.md` (lo legge lui), la bozza, i conteggi e le schede con i relativi `testi/`: tutte se sono 8 o meno, altrimenti 5 a campione. Applica le correzioni. Il red team è OBBLIGATORIO e deve essere un subagente, non un tuo controllo: se non riesci ad avviarlo, fermati e dillo all'utente prima di scrivere il report (in Codex senza subagenti: alternativa in `ambienti.md`, solo con il sì dell'utente).

## Fase 8 - Report
Per i link alle norme leggi ora `references/normattiva.md` (o usa la skill "normattiva", se installata). Crea `report.md` nella radice di `<cartella>` con le regole di `regole_bozza.md` già lette (sezione "Esito del red teaming" in fondo). Conversione in .docx solo se l'utente la chiede e `pandoc` è installato. Messaggio finale: tre righe, con il percorso di `report.md` e della cartella `pdf/`.
