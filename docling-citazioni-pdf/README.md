# Docling: citazioni puntuali dai PDF

Una skill per collegare le affermazioni di un riassunto, una cronologia o un memo
alle pagine dei documenti della pratica. Pensata per Codex, Claude Code e
Cowork/Claude Desktop con un server Docling MCP accessibile.

Esempio di richiesta:

> Esamina contratto, lettere e perizia. Prepara una cronologia, cita per ogni
> fatto il documento e la pagina del PDF e segnala ciò che non puoi verificare.

La skill controlla i requisiti, usa Docling per estrarre testo e struttura,
conserva il JSON con le provenienze e confronta i passaggi con l'originale.
Distingue sempre **pagina fisica del PDF** e numerazione stampata, oltre a
**pagina candidata**, **riscontro sul livello testo** e **controllo visivo**.
Non promette citazioni infallibili: la verifica del contenuto resta necessaria,
soprattutto per scansioni, tabelle e frasi distribuite su più pagine.

## Installazione della skill

- **Codex:** copia la cartella interna `docling-citazioni-pdf/` in
  `~/.agents/skills/` oppure in `.agents/skills/` del progetto. È quella che
  contiene `SKILL.md`, non la cartella esterna che include test e archivio.
- **Claude Code:** copia la stessa cartella in `~/.claude/skills/` oppure in
  `.claude/skills/` del progetto. Puoi richiamarla come `/docling-citazioni-pdf`.
- **Cowork/Claude Desktop:** carica [docling-citazioni-pdf.skill](docling-citazioni-pdf.skill)
  tramite la gestione delle skill disponibile nella tua versione.

Il file `.skill` è un archivio ZIP della cartella interna; contiene anche gli
script e le guide. I test rimangono fuori dall'archivio installabile.

**Installare la skill non installa Docling.** Se il server manca o non è
collegato, la skill guida la diagnosi e prepara i comandi adatti. Nelle versioni
attuali la guida usa l'avvio standard ufficiale con `uvx`, pacchetto
`docling-mcp[local]` e modalità locale esplicita; pip/venv è l'alternativa.
Non richiede launcher o configurazioni personali e non modifica automaticamente
configurazioni esistenti. La [guida ai requisiti](docling-citazioni-pdf/references/installazione.md)
contiene i passaggi separati per Codex, Claude Code, Desktop e Cowork.

## Nel lavoro dello studio

Conserva i PDF nella cartella della pratica. L'assistente prepara gli estratti
con pagine e, nei lavori con più fonti, un registro che collega affermazione,
documento, passo e controllo svolto. Gli hash riconoscono la versione del file:
se il PDF cambia, i riferimenti vanno ricontrollati. Puoi riutilizzare il registro
per scrivere in Word, Markdown o LaTeX senza cambiare il tuo gestionale.

Con un solo PDF scrive, ad esempio: «Il fornitore dichiara la consegna il
12 marzo (p. 2)». Con più PDF aggiunge la fonte: (p. 2 del documento
`lettera.pdf`). Puoi indicare il tuo stile, ad esempio «usa pag. e il numero
dell'allegato»: la skill lo mantiene. La numerazione predefinita conta le pagine
fisiche del PDF; eventuali numeri stampati vengono distinti. La skill deve
distinguere una dichiarazione da un fatto effettivamente provato. Per verificare giurisprudenza o norme
aggiornate serve il successivo lavoro sulle banche dati, con le skill pertinenti.

## Limiti e riservatezza

La conversione locale non rende automaticamente locale il modello, la chat o
Cowork. Il primo avvio può scaricare modelli; i testi estratti possono arrivare
al modello che stai usando. La skill non sceglie un servizio remoto come
ripiego e non amplia i permessi per superare gli errori. In Cowork servono
connettori effettivamente disponibili e accesso ai file fra gli ambienti:
un percorso del computer non è necessariamente quello della shell isolata.

Compatibilità delle istruzioni e pacchetto verificata; disponibilità degli
strumenti soggetta al client. Consulta [TEST-REPORT.md](TEST-REPORT.md) per le
prove effettivamente eseguite e quelle non coperte.

## Istruzioni progressive e documenti completi

Il file principale contiene il flusso essenziale. Le guide su installazione,
estrazione, contesto, scansioni, prestazioni e intervalli si aprono solo quando
servono: non vengono caricate tutte per una risposta semplice.

Questo risparmio sulle istruzioni non riduce le fonti: **i documenti entrano
integralmente nel prompt/contesto di analisi quando c'è spazio**. Prima di usare
estratti, riassunti, ricerca o lotti, la skill informa l'utente di cosa non
entrerà e del metodo previsto. Un file salvato non equivale a un file presente
nel contesto. I documenti già inclusi per intero non vengono duplicati.

## Scansioni, OCR e tempi

La skill controlla gli indizi delle pagine prima della conversione. Distingue
scansioni probabili, testo presente e pagine miste, dichiarando la copertura
controllata. Una scansione può già avere testo da OCR: la selezionabilità non
ne prova l'origine digitale. Per scansioni e OCR attivo avvisa prima che nomi,
date, importi e altri passaggi potrebbero essere riconosciuti male e richiedere
controllo sulle immagini. Se le opzioni del server non sono note, lo dice.

Docling funziona anche senza GPU; su sola CPU può richiedere più tempo. Nei
confronti ufficiali consultati il vantaggio delle GPU è consistente ma dipende
da macchina, pipeline e documento: nessun moltiplicatore fisso per il tuo PC.
La [guida alle prestazioni](docling-citazioni-pdf/references/prestazioni.md)
riporta numeri, condizioni e fonti. Il dispositivo va verificato sul server
MCP: avere una GPU sul computer non significa usarla per la conversione.

## Manutenzione

Per i manutentori:

```sh
python3 -B -m unittest discover -s docling-citazioni-pdf/tests -v
```

Esegui dalla root del repository. Le prove PDF/MCP opzionali richiedono
l'ambiente indicato nel rapporto. Non usare fascicoli riservati nei test pubblici.

Fonti per l'installazione delle skill: [Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills).
