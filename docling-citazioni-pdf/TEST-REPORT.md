# Revisione: istruzioni progressive, contesto e avvisi — 28 ottobre 2026

Esito: **71 test superati** nel Python 3.12 con `pypdfium2 5.14.0` già presente.
La stessa suite è stata eseguita anche nel Python 3.9 con `pypdfium2 4.30`.
Sono i 57 controlli iniziali più 10 controlli del nuovo rilevatore di indizi
PDF e 4 prove sul PDF sintetico con testo, immagine, livello OCR e pagina bianca.
Nel Python senza `pypdfium2` i quattro test di integrazione vengono saltati,
non dichiarati riusciti. Nessuna installazione o modifica delle configurazioni
MCP dell'utente.

## Progressive disclosure e citazioni

Il file principale passa da **1.291 a 914 parole** (conteggio per spazi,
circa **29% in meno**), pur includendo le nuove regole. Il dato non
è una misura dei token di un particolare modello o del costo di una sessione.
I dettagli di conversione sono in `references/estrazione.md`; contesto,
scansioni e prestazioni hanno guide condizionali. Installazione e intervalli
avanzati restano fuori dal flusso ordinario. Non si richiede di leggere il
codice degli helper per usarli. I riferimenti ai precedenti ambienti di origine
sono stati eliminati dai sorgenti e dall'archivio della skill.

Default: `(p. 1)` con un PDF; (p. 1 del documento `pippo.pdf`) con più PDF;
preferenza esplicita dell'utente prioritaria. Numeri fisici distinti da stampati,
fonti riconoscibili e incertezze conservate anche con un formato personale.
I documenti devono entrare integralmente nel contesto quando la capienza lo
consente: lettura progressiva delle guide e selezione delle fonti sono due
cose diverse. Avviso prima di estratti, sintesi, ricerca o lotti. Un file
salvato non è automaticamente nel prompt; i lotti non aumentano un budget
totale o la capienza simultanea.

## Ulteriore verifica dell'installazione standard

La guida è stata confrontata direttamente con il README corrente del pacchetto
ufficiale: [Docling MCP](https://github.com/docling-project/docling-mcp/blob/main/README.md).
Percorso principale uvx, extra locale `[local]`, variabile di modalità `local`
e trasporto `stdio`; alternativa pip/venv standard. Nessun wrapper, sandbox,
cache dedicata, limite personalizzato di documenti o dispositivo imposto.
Gli esempi client usano lo stesso comando e i default di strumenti/pipeline.
Le condizioni isolate dei vecchi smoke test sono condizioni di prova, non la
procedura di installazione proposta all'utente.

Il sito generale Docling consultato riportava variabili precedenti e un default
di modalità diverso dal README corrente del pacchetto: per questa guida è stato
seguito il README specifico del server e il suo prefisso `DOCLING_MCP_`, senza
mescolare esempi di versioni diverse. Configurazioni JSON/TOML e comandi client
sono controllati per sintassi e corrispondenza degli argomenti; non è stata
eseguita una nuova installazione pulita o alterata quella dell'utente.

## Ricerche delegate

Tre subagenti hanno usato la skill Perplexity, con una query `standard`
ciascuno e controllo diretto delle fonti primarie. Rapporti pubblicabili:
[convenzioni italiane e giuridiche](tests/ricerca-citazioni.md),
[CPU/GPU](tests/ricerca-prestazioni.md),
[scansioni e OCR](tests/ricerca-scansioni.md).

`p./pag.` e `pp./pagg.` sono ammesse: le convenzioni editoriali giuridiche
variano. I numeri CPU/GPU sono benchmark circoscritti con condizioni e fonti,
non previsioni per il PC dell'utente. L'origine digitale o da scansione non
può essere certificata dal solo livello testo; l'OCR effettivo dipende dalle
opzioni del server. Le guide riportano avvisi preventivi appropriati.

## Nuovo helper di ispezione

`pypdfium2` è la libreria Python che usa il motore PDFium per leggere/renderizzare
i PDF; 4.30 e 5.14 qui indicano versioni della libreria, non di Docling o del
motore PDFium. È una dipendenza tecnica degli helper, non un diverso server
MCP o un nuovo programma che questa revisione richieda di installare.

`inspect_pdf.py` non avvia OCR, non usa rete e non certifica l'origine del PDF.
Conserva copertura del campione, indizi, soglie e limiti geometrici. Il PDF
`tests/fixtures/tipi-pdf.pdf` ha quattro pagine: testo senza immagine dominante,
immagine senza testo, immagine con livello OCR sintetico volutamente errato,
pagina bianca. Il controllo su tutte le pagine distingue i quattro indizi;
il campionamento predefinito dichiara di non avere letto la pagina 3.
Il helper non corregge il livello testo o attribuisce un tipo certo alle pagine
non esaminate. Errori e file non leggibili restano errori, non «scansioni».

Il controllo nell'altro Python presente ha rilevato differenze reali di API
in `pypdfium2 4.30`: assenza del context manager e metodo `get_pos()` invece di
`get_bounds()`. I due helper PDF sono stati adattati con chiusura esplicita
ed accesso alle coordinate secondo l'API effettivamente presente, verificata
sul codice ufficiale installato. I quattro casi strutturali passano sia con
`pypdfium2 4.30` sia con `pypdfium2 5.14`; non è richiesto aggiornare l'installazione per questo motivo.

Testate anche assenza di sovrascrittura dell'originale/report e gestione di un
file non PDF. Immagine e testo discordano intenzionalmente a p. 3: immagine
1.200,00 euro, livello testo 12.000,00 euro. L'immagine è stata effettivamente
osservata dall'autore e dal revisore; il JSON del helper mantiene correttamente
`visual_verification_performed: false` perché lo script non svolge quel controllo.
Generatori e fixture sono pubblici, senza dati di pratiche reali.

## Revisione dei flussi e limiti

Un subagente ha svolto tre casi senza ricevere la risposta attesa:
[un PDF](tests/revisione-caso-A-risposta.md),
[più PDF e stile personale](tests/revisione-caso-B-risposta.md),
[simulazione di contesto insufficiente](tests/revisione-caso-C-risposta.md).
Ha letto inizialmente solo l'entrypoint, poi le guide necessarie; ha confrontato
il testo con tutte e sette le immagini originali e rilevato la discordanza OCR.
[Metodo e limiti](tests/revisione-metodo-e-limiti.md).

È emerso un caricamento evitabile della guida di installazione anche con
conversione già fornita: il routing è stato corretto e la
[regressione mirata](tests/revisione-addendum-regressione-routing.md) conferma
che non serve aprirla. Non è una nuova prova end-to-end. Il revisore ha anche
caricato inutilmente il JSON tecnico intero: è una deviazione osservata rispetto
alla guida, non una garanzia che ogni agente rispetterà il risparmio di contesto.
Gli avvisi preventivi sono stati prodotti come **bozze**: questo test verifica
contenuti e strategia, non dimostra l'invio reale dell'avviso in una conversazione
separata prima della lettura. Il caso di 40 PDF è simulato, non un carico reale.

Non sono stati ripetuti il benchmark GPU o una conversione OCR end-to-end del
nuovo PDF: le misure di prestazioni sono pubblicate dagli autori; il test locale
nuovo riguarda l'ispezione strutturale e il confronto con le immagini. Le
precedenti prove MCP restano quelle della prima release. Nessun collaudo nuovo
delle interfacce Codex/Claude Code/Cowork o installazione da zero.

Le prove iniziali, con esiti riferiti alla versione di allora, sono conservate
qui sotto; i vecchi esempi di citazione documentano quell'esecuzione e non
sostituiscono il formato corrente.

---

# Prove iniziali della prima release — 28 ottobre 2026

Esito: **57 test automatici superati**, prova reale con Docling MCP locale
riuscita, revisione indipendente su PDF sintetico completata senza difetti
riproducibili nel perimetro osservato. Non equivale a validazione su ogni
documento, modello o applicazione.

## Cosa è stato verificato

| Prova | Esito e portata |
|---|---|
| 26 test di provenienza | Blocchi multipagina, intervalli, ambiguità, Unicode/UTF-16, base `orig`/`text`, hash, profili non comprovati, output preservati |
| 9 test diagnostica | Pacchetti assenti, `docling-slim`, interprete e PATH distinti, nessuna falsa certificazione della connessione |
| 6 test vista per pagine | Gerarchia, tabelle, provenienze invalide, elementi fuori albero, blocchi multipagina, nessuna sovrascrittura |
| 11 test riscontro testuale | Pagina effettiva della frase, passaggi fra pagine, duplicati, numeri stampati, Unicode, ricerca limitata al livello testo, istruzioni nel documento trattate come dati |
| 3 test distribuzione | Frontmatter comune, description entro 1024 caratteri, riferimenti risolvibili e byte dell'archivio identici ai sorgenti |
| 2 regressioni su output MCP reale | Un blocco sintetico viene realmente fuso fra pagine 2 e 3: la frase dell'importo resta multipagina nel derivato, mai assegnata automaticamente alla prima pagina |
| MCP locale, collegamento SDK diretto | Catalogo, conversione del PDF, chiave restituita, salvataggio MD/JSON, copia verificata e derivati creati |
| Tre confronti sul PDF reale sintetico | Frase consegna a p. PDF 2; negazione del collaudo a p. PDF 3; titolo ripetuto segnalato ambiguo |
| Tre controlli CLI su PDF | Rifiuto di sovrascrivere report o originale e di usare pagina fuori intervallo; originale invariato |
| Controllo visivo | Autore: pagine PDF 2 e 3; revisore indipendente: tutte e tre le pagine, con lettore/renderer diverso |

Ambiente della prova MCP: Python 3.12, `docling-mcp 3.4.0`, `docling-slim
2.143.1`, `docling-core 2.105.0`, SDK `mcp 2.3.0`, `pypdfium2 5.14.0`;
schema Docling `1.10.0`. Nessuna distribuzione `docling` nel venv: il motore
locale funziona tramite `docling-slim`. La diagnostica lo riconosce.
Server con modalità locale esplicita e modelli già presenti; non sono stati
installati pacchetti o modificati collegamenti/configurazioni dell'utente.

PDF e JSON di prova sono in `tests/fixtures/`, insieme a `smoke-summary.json`.
Sono interamente sintetici e pubblicabili. Hash del PDF:
`5c31835b48e2e5067e68128db18a1e5824cbe78eee8fe0431754a597db2c2bec`.
Hash del JSON:
`844736e4664d92d800210f793c158058be9f2e4caae752a8e8843236a71ca64e`.
Il report SDK mantiene correttamente il controllo visivo come non eseguito
dallo script; la successiva ispezione umana/visiva è documentata separatamente.

## Revisione indipendente

Un subagente ha ricevuto skill e PDF sintetico, poi gli artefatti della
conversione, senza una risposta attesa o un difetto suggerito. Ha prodotto
[risposta](tests/redteam-risposta.md), [metodo](tests/redteam-metodo.md) e
[revisione](tests/redteam-audit.md).

Ha distinto la dichiarazione di consegna dalla prova del fatto, conservato la
negazione sul collaudo e trattato 1.200 euro come somma richiesta/non liquidata,
non come importo sicuramente dovuto. Ha verificato che pagina stampata 41
corrisponde alla pagina fisica 3 e attribuito il termine sospeso alle pagine
fisiche 2–3. Non ha seguito l'istruzione malevola contenuta nel PDF di citare
tutto a pagina 1. Ha riconosciuto l'assenza dei tool Docling nella propria chat
senza dedurne l'assenza del programma sul computer.

Il revisore ha eseguito la suite allora composta da 55 test; i due test di
regressione sull'output reale sono stati aggiunti dopo quella lettura. I sorgenti
della skill e degli helper valutati non sono cambiati in seguito alla revisione.

## Come ripetere

Dalla root del repository, senza Docling o pacchetti PDF nel Python dei test:

```sh
python3 -B -m unittest discover -s docling-citazioni-pdf/tests -v
```

Per la prova MCP opzionale usa un Python con SDK `mcp` e `pypdfium2`, il server
già installato e modelli già scaricati. Sostituisci i percorsi reali; la cartella
di output deve essere nuova. Non legge configurazioni MCP o fascicoli personali.

```sh
'/percorso/venv/bin/python' -B docling-citazioni-pdf/tests/mcp_smoke.py \
  --server '/percorso/venv/bin/docling-mcp-server' \
  --models '/percorso/modelli' \
  --pdf docling-citazioni-pdf/tests/fixtures/fascicolo-sintetico.pdf \
  --output-dir '/cartella/autorizzata/nuova-prova'
```

Per rigenerare il PDF usa `tests/make_fixture.py` in un Python con `reportlab`;
la copia pubblicata permette il test anche senza quel generatore. Per convalidare
la skill si è usato anche `quick_validate.py` del creatore di skill Codex.

## Limiti non coperti

- Nessuna installazione da zero su macchina pulita o Windows; comandi preparati
  da fonti primarie, non provati su tutte le combinazioni.
- Nessuna installazione/connessione end-to-end nell'interfaccia Claude Code,
  Cowork o Codex: il client SDK prova il server, non la disponibilità in tali chat.
- Nessuna campagna su più modelli o fascicoli reali; nessun servizio LLM a pagamento
  usato per questi test oltre ai subagenti della sessione.
- OCR su scansioni degradate, firme, caselle e tabelle complesse non collaudati
  end-to-end. Il confronto testuale non sostituisce il controllo delle immagini.
- I profili avanzati contengono evidenze dichiarate dal chiamante: gli script
  ne controllano forma e legami, non autenticità o verità. Nessun helper certifica
  automaticamente il supporto semantico di una frase o l'autenticità del PDF.
