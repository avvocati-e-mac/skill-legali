# Prove della prima release — 28 ottobre 2026

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
