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
attuali serve `docling-mcp[local]` per convertire sul computer. Non modifica
automaticamente configurazioni esistenti. La [guida ai requisiti](docling-citazioni-pdf/references/installazione.md)
contiene i passaggi separati per Codex, Claude Code, Desktop e Cowork.

## Nel lavoro dello studio

Conserva i PDF nella cartella della pratica. L'assistente prepara gli estratti
con pagine e, nei lavori con più fonti, un registro che collega affermazione,
documento, passo e controllo svolto. Gli hash riconoscono la versione del file:
se il PDF cambia, i riferimenti vanno ricontrollati. Puoi riutilizzare il registro
per scrivere in Word, Markdown o LaTeX senza cambiare il tuo gestionale.

Una frase può diventare: «Il fornitore dichiara la consegna il 12 marzo
(doc. D01, lettera.pdf, p. PDF 2)». La skill deve distinguere questa dichiarazione
da una consegna effettivamente provata. Per verificare giurisprudenza o norme
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

## Origine e manutenzione

Deriva dalle skill `docling-local` di Hermes e `docling-unsloth` nel progetto
Hermes integrazione dell'autore, comprese le correzioni sui blocchi multipagina.
Riusa e collauda gli script di provenienza e di esportazione per pagina; aggiunge
diagnostica portabile e riscontro sul livello testo PDF. Non richiede quelle
skill installate, né usa percorsi o modelli personali dell'autore.

Per i manutentori:

```sh
python3 -B -m unittest discover -s docling-citazioni-pdf/tests -v
```

Esegui dalla root del repository. Le prove PDF/MCP opzionali richiedono
l'ambiente indicato nel rapporto. Non usare fascicoli riservati nei test pubblici.

Fonti per l'installazione delle skill: [Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills).
