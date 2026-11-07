# BuddaLaw — collaudo della candidata v9.1

**Data:** 18 ottobre 2026. **Stato:** revisione beta conclusa; non promossa a stabile.
La campagna C3 della v9.0 è conclusa e resta documentata in
[REPORT-test-v9.0.md](REPORT-test-v9.0.md). I suoi risultati non vengono
riscritti né sommati a quelli della candidata successiva.

**Esito:** 144 controlli offline superati. C6: Haiku **0/6** prove promosse;
Sonnet **9/12**, tutte le 18 prove valide. Il confronto automatico risolve
l'omissione dell'avviso nei campioni osservati, ma restano violazioni nell'uso
degli strumenti e un URL alterato. Nessuna attestazione di affidabilità
generale o di completamento della suite C3 sulla nuova candidata.

## Modifiche rispetto alla v9.0

- Scoperta del catalogo prima delle ricerche, con un solo avviso immediato
  quando compaiono nomi nuovi.
- Confronto locale degli elenchi con `scripts/verifica_catalogo.py` dove shell
  e Python sono disponibili. Lo script legge l'inventario della propria copia
  della skill, non usa rete o credenziali e rifiuta conteggi incoerenti e
  duplicati. Negli altri ambienti resta il confronto manuale dell'assistente.
- Copia del collegamento dalla singola fonte, con controllo dell'intero URL;
  nessuna ricostruzione da numero, anno o identificativo.
- Separazione fra lettura del testo normativo e generazione dei collegamenti;
  una richiesta di solo link passa a `normattiva`, se disponibile.
- Ricerca e risposta in italiano fin dal primo messaggio, filtro per anno
  per le pronunce recenti e conservazione del tipo di atto chiesto dall'utente
  fino alla verifica sulla risposta del server.

## Metodo e limiti

Solo **Claude Pro**, modelli `claude-haiku-4-5-20251001` e
`claude-sonnet-4-6`, con
`--solo-abbonamento`. Nessuna nuova chiamata OpenRouter o proxy API. Le stime
USD della CLI misurano i token e non attestano addebiti aggiuntivi.
Copie installate e vecchi arresti restano invariati. Il nuovo arresto condiviso
è `tests/e2e/results/20261018-c5-claude-pro/STOP`: al primo guasto o esaurimento
della quota si ferma la campagna, senza ritenti automatici.

L'etichetta `v9` del runner indica i sorgenti correnti congelati nel manifest,
qui la candidata **9.1**. `v9-ridotta` rimuove dall'inventario soltanto
`search_similar_cases`, lasciandolo visibile nel catalogo del server e nel
resto delle istruzioni. Non equivale a cambiare il servizio.

Il runner conserva le fonti ammesse. Per la nuova skill consente anche Bash,
limitando l'autorizzazione automatica alla chiamata
`python3 <copia-temporanea>/scripts/verifica_catalogo.py ...`. Nessuna shell
viene aggiunta alle configurazioni prive dello script. L'output dello script
non è una fonte giuridica. Questo ambiente differisce dalla vecchia C3 e ne
documenta la nuova funzionalità, senza pretendere un confronto statistico.

Lo schema del server non è stato rigenerato: i 48 nomi scoperti nella nuova
prova coincidono con la fixture; le chiamate vengono confrontate con lo schema
conservato. Non è una nuova certificazione live di tutti i parametri o dei
32 calcolatori. Nessun collaudo completo dichiarato per altri modelli o per
Claude Desktop senza shell.

## Diagnostica C4, conclusa

La sola riscrittura delle istruzioni non ha risolto l'avviso: B12 **0/3**,
tre prove valide. I 48 nomi erano disponibili, ma il modello non ha segnalato
`search_similar_cases` assente dall'inventario ridotto. Le risposte restano
conservate in `tests/e2e/results/20261018-182214-129330/`.

Hash C4 di `SKILL.md`:
`11b33aa33d5c288fd8285e9c5cc475acaf17258387f7e10332cd55222894fea0`.
Stima CLI: 0,495 USD di token. La prima verifica dell'abbonamento aveva
raggiunto il timeout senza avviare alcun modello; il successivo controllo
della CLI ha confermato Pro.

## Candidata C5

Hash di `SKILL.md`:
`d0a3471922985b132ce3148b424a365bffa5631be045069240284c058c538138`.

**140 controlli offline superati**, 12 live saltati. Archivio `.skill`
coerente con i sorgenti. Le nuove prove offline coprono i tre prefissi MCP,
un nome nuovo a parità di totale, tool non visibili senza falso avviso,
cataloghi incompleti, duplicati, server estranei e lettura della copia locale
dell'inventario.

Prima prova B12: **1/1**, in `20261018-182552-973666/`. Controllo aggiuntivo
della traccia: i 48 nomi passati allo script coincidono esattamente con i
48 riferimenti restituiti da `ToolSearch`. L'avviso precede la ricerca e i
collegamenti della risposta superano il valutatore. Stima CLI: 0,158 USD.
Le altre due ripetizioni, in `20261018-182744-292618/`, emettono l'avviso ma
raggiungono entrambe il limite di otto turni senza ricerche MCP. Il modello
tenta anche comandi shell estranei alla verifica, rifiutati dalle autorizzazioni.
**Bilancio C5: 3/3 registrate, una sola prova valida e promossa**. Non si
presenta come un successo complessivo di B12. Stima CLI delle due prove
interrotte: 0,322 USD.

## Candidata C6

Hash di `SKILL.md`:
`f55712536f17d3c809c6b1632bdaa6c7a59db1ed331e344468e39814e794fed5`.

La skill precisa il comando diretto, il percorso assoluto e il ruolo distinto
dei tool MCP per accesso e ricerca. Non autorizza comandi shell alternativi
in caso di errore. Il runner porta il limite a **16 turni per tutti i profili**,
registrandolo nel manifest: il vecchio limite risultava insufficiente già in
B04 della C3 e ha interrotto due prove C5. La modifica non altera le attese
su fonti, avvisi, lingua o numero di ricerche. Non si riclassificano le vecchie
prove né si sommano i loro successi a C6.

Tornate:

- Haiku, B12 e B13, tre prove per caso:
  `tests/e2e/results/20261018-183031-596856/`.
- Sonnet `claude-sonnet-4-6`, B12/B13/B23/B24, una prova per caso, stessa
  candidata e arresto condiviso, sandbox separata:
  `tests/e2e/results/20261018-183329-097605/`.

### Esiti del controllo del catalogo

| Caso | Haiku C6 | Sonnet C6 |
|---|---|---|
| B12, avviso vero | **0/3**: avviso presente 3/3, ma comandi shell estranei | **1/1** |
| B13, nessun falso avviso | **0/3**: nessun falso avviso, ma comandi shell estranei; una prova omette anche la ricerca MCP | **1/1** |
| B23, avviso una volta su tre turni | non eseguito | **0/1**: avviso corretto, URL alterato |
| B24, accesso una volta su tre turni | non eseguito | **1/1** |

Haiku: **6/6 prove valide, nessuna promossa**, 0/2 casi. Gli iniziali «OK»
non controllavano i comandi shell estranei: la rivalutazione offline li
boccia, preservando gli originali. Sonnet: **4/4 valide, 3/4 promosse**.
Non sono campioni statisticamente comparabili né un collaudo completo della
suite. I risultati sconsigliano la promozione stabile anche su Sonnet.

Il difetto di B23 è confermato nella traccia: la fonte restituisce l'URL con
identificativo finale `66194858`; la risposta scrive `66194758`. Non è un
falso errore del valutatore né un collegamento mancante nel corpus. La risposta
non viene corretta dopo il test. Non si ripete il caso per sostituire l'errore.

Stime CLI: Haiku **1,102 USD**, Sonnet **2,368 USD**, incluse nell'uso
dell'abbonamento secondo gli eventi osservati: `isUsingOverage=false`,
`overageDisabledReason=org_level_disabled`. Non sono addebiti attestati.

### Controlli mirati sulle altre modifiche

Sonnet: B01/B07/B11/B15/B19/B20/B21/B22, una prova per caso, stessa candidata,
limite complessivo di 5 USD stimati e massimo 2 per esecuzione, in
`tests/e2e/results/20261018-184206-338009/`. **8/8 valide, 6/8 promosse**,
3,155 USD di token stimati. Sono controlli su link, norme, lingua, `not_found` e virgolettati;
non sostituiscono le tre ripetizioni dei casi critici previste dalla vecchia C3.

| Caso | Esito | Osservazione |
|---|---|---|
| B01, tributario | bocciato | Collegamenti fedeli e dominio corretto; compare un box finale di avvertenze vietato dalla skill |
| B07, testo normativo storico | promosso | Versione alla data richiesta, senza link normativo improprio |
| B11, domanda inglese | promosso | Ricerca e risposta in italiano; manca solo l'indicazione esplicita «in italiano», controllo non bloccante |
| B15, solo link normativo | promosso | Segnala l'assenza della skill dedicata, senza inventare il collegamento né chiamare BuddaLaw |
| B19, pronunce recenti | promosso | Filtro per anno e collegamenti fedeli |
| B20, tipo di atto errato | bocciato | Usa l'alias `testo_unico_sicurezza_lavoro` invece degli estremi richiesti: legge il decreto ma non verifica il tipo «legge» indicato dall'utente come prescritto |
| B21, sentenza non disponibile | promosso | Riferisce `not_found` senza creare un collegamento |
| B22, virgolettato | promosso | Il passo supera il confronto letterale con il testo della fonte |

La campagna mirata è **conclusa**. Sonnet totalizza 9/12 prove promosse
nei due gruppi; Haiku 0/6 dopo la rivalutazione che considera anche i
comandi shell rifiutati. I conteggi non si sommano tra modelli e non sono
una stima statistica di affidabilità. Nessuna risposta fallita è stata
riscritta o ripetuta per cambiare l'esito. Non sono stati aggiornati modelli,
copie installate o configurazioni MCP dell'utente.

Il valutatore aggiunge un controllo sulle chiamate Bash, anche rifiutate:
ammette solo il comando diretto dello script nella copia temporanea, con
numero e nomi identici al catalogo osservato. Comandi estranei e nomi non
osservati fanno fallire la prova. Le tracce originali vengono rivalutate
senza nuove chiamate al modello; gli «OK» del vecchio valutatore non sono
l'esito definitivo di C6. **144 controlli offline superati**, 12 live saltati.

Il validatore generico di `skill-creator` rifiuta i campi `version` e
`changelog`, già presenti nella v9.0. Sono mantenuti secondo le convenzioni
di questo repository; intestazione, versione, descrizione e archivio sono
verificati dai test strutturali del progetto.
