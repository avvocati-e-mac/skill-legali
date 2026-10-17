---
name: verifica-citazioni-legali
description: "Verifica le citazioni di un atto, parere, memoria o contratto già scritto, specie se generato o rivisto con IA. Per ogni sentenza, massima, norma, virgolettato o documento di causa controlla che esista, che gli estremi siano esatti, che la frase tra virgolette sia letterale e che il principio sia davvero quello della fonte, anche cercando passi contrari. Produce un report chiaro con tabella delle azioni e testo da incollare e, a richiesta, applica solo le correzioni scelte. Formati: LaTeX, Markdown, DOCX, ODT (PDF in lettura). Chiede all'utente quali banche dati usare. USARE SEMPRE quando l'utente chiede di verificare o revisionare citazioni, sentenze, massime, norme o verbatim, chiede «esiste questa sentenza?», «controlla l'atto prima del deposito», o vuole sapere se un testo scritto con IA contiene allucinazioni. NON usarla per redigere un atto né per una ricerca giurisprudenziale libera."
---

# Verifica delle citazioni legali

Un atto scritto o rivisto con IA può contenere citazioni che *sembrano* giuste:
- sentenze inesistenti;
- numeri veri con un contenuto diverso;
- frasi tra virgolette ritoccate;
- principi rovesciati;
- norme con commi che non esistono.

Il giudice e la controparte leggono la fonte, quindi un solo errore mina la credibilità di tutto l'atto. Questa skill controlla ogni citazione **sulla fonte letta**, mai a memoria o per plausibilità. Consegna poi un report che si capisce al primo colpo e su cui si può intervenire in modo puntuale.

La skill verifica e propone. Non decide la strategia difensiva: quando una correzione cambia un argomento, lo segnala «per decisione dell'avvocato».

## Mappa: cosa leggere e quando

Carica i file solo quando servono.

| Momento | Leggi |
|---|---|
| Dopo la Fase 0, per il formato scelto | `references/formati/<latex|markdown|docx|odt>.md` |
| Dopo la Fase 0, per ogni strumento scelto | `references/strumenti/<nome>.md`. Se lo strumento non è elencato: `strumenti/generico.md` |
| Fase 3, sempre | `references/allucinazioni-ia.md` (verdetti, gravità, tre chiavi) |
| Fase 3, giurisprudenza | `references/verifica-giurisprudenza.md` |
| Fase 3, norme | `references/verifica-norme.md` |
| Fase 3, esito dubbio | `references/trappole.md` |
| Se deleghi a subagenti | `references/deleghe.md` |
| Se l'utente autorizza il web | `references/ricerca-integrativa.md` |
| Fase 4 | `references/scrittura-report.md`, `assets/modello_report.md` |

## Fase 0: Avvio, con una sola tornata di domande

Prima di tutto leggi l'eventuale `CLAUDE.md` o `AGENTS.md` del progetto. Le sue regole su fonti, perimetro, riservatezza e scadenze prevalgono su questa skill: dichiaralo all'utente.

Poi chiedi, in un'unica tornata, solo quello che il contesto non dice già. Se le risposte sono già nella richiesta, non chiedere di nuovo.
- **Claude (Desktop, Cowork, Code):** usa `AskUserQuestion` se disponibile, altrimenti un elenco numerato in chat.
- **Codex/OpenAI:** usa lo strumento di domanda all'utente se presente, altrimenti un elenco numerato in chat.

Domande:
1. **Documento**: percorso e formato (tex, md, docx, odt; il pdf solo in lettura).
2. **Modalità**:
   - *rapida*: esistenza, estremi e verbatim;
   - *completa*: in più natura del passo, pertinenza, passi contrari, validità nel tempo.
3. **Strumenti per categoria.** Spiega che cosa serve e lascia scegliere lo strumento (contratto di capacità):
   - legittimità: esistenza ed estremi più testo o massima (es. Italgiure, BuddaLaw, DeJure, OneLegale, altro);
   - merito: esistenza più testo (es. BDM, BuddaLaw, altro);
   - Corte costituzionale e UE: testo ufficiale (sito della Corte, EUR-Lex/CURIA);
   - norme: testo vigente e storico (Normattiva, EUR-Lex, altro);
   - documenti di causa: cartella in cui si trovano.
4. **Web e ricerca approfondita** (skill `perplexity-web-mcp`): sì o no. Se sì, vale solo come fonte secondaria.
5. **Subagenti**: sì o no.
6. **Riservatezza**: i nomi da tenere fuori da query e report; il divieto di caricare all'esterno il testo dell'atto (default: vietato).
7. **Cartella di output**. Default: una nuova cartella `Revisione citazioni/` accanto all'atto.

## Fase 1: Collaudo degli strumenti

Per ogni strumento scelto, fai una chiamata di stato o una ricerca di prova su una citazione dell'atto. La prova può essere la prima verifica vera: registrala due volte, nel collaudo e nella voce. Riporta una tabella *strumento · esito · conseguenza*.

Perché: in pratica sessioni scadute, quote esaurite e lacune d'archivio sono la prima causa di falsi «non trovato».

Regole:
- **niente retry** su 403, 429, quote o blocchi: fermati e riferisci;
- login e identità digitale li gestisce l'utente: suggerisci il comando (`! <comando>`);
- uno strumento che manca è un **limite da dichiarare**, non da aggirare.

## Fase 2: Inventario

1. Copia l'atto, senza modifiche, in `<output>/00_originale.<ext>`.
2. Esegui l'estrazione:
   `python3 <skill>/scripts/estrai_citazioni.py <atto> --out <output>`
   Ottieni `inventario.md` e `inventario.json`, con ID (C01…), posizione e stringa da cercare.
3. **Seconda lettura integrale** dell'atto. Aggiungi quello che le regex non vedono: «conf.», «ivi», «v. anche», dottrina, rinvii impliciti, affermazioni del tipo «la giurisprudenza è pacifica». Riconcilia: «lo script trova X voci, la lettura Y; differenza spiegata».
4. Crea `stato_verifica.json` (modello in `assets/`) e `registro_verifica.jsonl`, così il lavoro può riprendere dopo una pausa o una compattazione.
5. Se l'atto è lungo o le quote sono strette:
   - stima le richieste necessarie per strumento;
   - metti in testa le citazioni **decisive**, quelle su cui regge un motivo o un'eccezione;
   - dillo all'utente.

## Fase 3: Verifica

Per ogni voce, nell'ordine di priorità, applica i livelli di `verifica-giurisprudenza.md` o `verifica-norme.md` e assegna **un verdetto e una gravità** secondo `allucinazioni-ia.md`.

Regole che non si saltano:
- **Tre chiavi.** Numero e anno, sezione o data, materia coerente con il principio citato. Se una chiave non torna, è una «chimera» finché non si prova il contrario.
- **Verbatim solo sul testo.** Confronta ogni virgolettato con `scripts/confronta_verbatim.py`, mai a occhio. Il riassunto automatico di una banca dati e la risposta di un motore IA non sono la fonte.
- **Zero risultati ≠ inesistente.** «Inesistente» richiede una prova positiva (vedi `allucinazioni-ia.md`). Altrimenti il verdetto è «non reperita» e si indica il limite dello strumento.
- **Massima ≠ motivazione; OCR ≠ testo.** Dichiara quale delle due hai letto. Un passo OCR va riscontrato sull'immagine prima di citarlo alla lettera.
- **Leggi il contesto.** Se la frase è la motivazione del giudice inferiore riferita dalla Corte, un inciso con rinvii o un obiter, il principio non è quello. Cerca anche i passi **contrari** nella stessa pronuncia.
- **I verbatim decisivi li rileggi tu**, anche se li ha trovati un subagente.
- Annota ogni accertamento nel registro: strumento, query, data, identificativo, passo e chi l'ha letto.

## Fase 4: Report

Scrivi `<output>/01_verifica_citazioni.md` seguendo `assets/modello_report.md` e `scrittura-report.md`:
1. **Esito in breve**, al massimo 8 righe, comprensibile da solo.
2. **Tabella delle azioni**, ordinata per gravità: ID · stringa da cercare · problema · azione con un solo verbo · intervento (`prima → dopo` se breve, altrimenti rinvio alla scheda). Chi legge la tabella deve poter correggere senza aprire altro.
3. **Schede** per ID: in una frase · cosa dice davvero la fonte · cosa fare · testo da incollare nel formato sorgente · diff.
4. **Appendici**: norme, rilievi non di citazione, registro, limiti.

Per ogni passo usato nel report salva in `fonti/estratti_verificati.md` il passo letterale e il riferimento. Copia in `fonti/` i PDF scaricati, solo con il consenso dell'utente.

**Prima di consegnare**, controlla che le correzioni non introducano errori nuovi:
- ogni virgolettato del *testo da incollare* deve stare negli estratti e risultare IDENTICA a `confronta_verbatim.py`;
- ogni estremo proposto deve essere quello verificato.

## Fase 5: Consegna

- Controllo di riservatezza: cerca nel report i nomi da escludere.
- Aggiorna l'eventuale mappa o indice di progetto.
- L'atto originale **non si modifica mai**.
- Nel messaggio finale: l'esito in breve, le azioni bloccanti e i limiti. Il resto sta nel report.

## Fase 6: Applicazione selettiva, su richiesta

L'utente risponde per esempio «applica C01, C03, C07; C05 no».
1. Controlla che ogni stringa da cercare sia ancora presente e univoca nell'atto: il testo può essere cambiato nel frattempo.
2. Applica **solo** quelle modifiche a una copia `02_versione_corretta.<ext>`, come spiega `formati/<formato>.md`. Per docx usa le revisioni tracciate, con un commento per ID.
3. Scrivi `03_registro_modifiche.md` con ID, testo prima e testo dopo.
4. Per le azioni «decide l'avvocato» non applicare nulla senza una scelta esplicita.

## Collaudo della skill (facoltativo)

`assets/test/atto_test.md` contiene citazioni seminate: vere, inventate, chimere, alterate. `assets/test/atteso.json` contiene i verdetti attesi. Usalo:
- quando cambi strumenti, come canarino: verifica in modalità rapida e confronta con l'atteso;
- come eval della skill.
