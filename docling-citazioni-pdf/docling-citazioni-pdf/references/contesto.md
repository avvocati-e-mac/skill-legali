# Documenti nel prompt e limiti di contesto

Apri questa guida per documenti lunghi, capienza incerta, troncamento, recupero
selettivo o lavoro a lotti. La lettura condizionale delle guide della skill
risparmia istruzioni; non deve diventare una riduzione silenziosa delle fonti.

## Quando il contenuto entra

Inserisci tutto il contenuto estratto dei PDF nel prompt/contesto di lavoro del
modello, mantenendo confini tra documenti, nomi e riferimenti alle pagine.
In una chat questo avviene tramite allegati o risultati degli strumenti
effettivamente letti: la skill non riscrive i messaggi dell'utente né può
forzare l'host a inserire un file binario nel prompt. Un semplice percorso,
un indice vettoriale, una chiave di cache o un file su disco non bastano.

Se gli allegati sono già disponibili per intero, non duplicarli. Se Docling
ha prodotto l'estrazione richiesta, rendila disponibile integralmente senza
dedurre l'avvenuta lettura dal salvataggio. Con uno strumento che tronca la
risposta leggi il file salvato in porzioni adeguate, senza confondere `max_size`
con un offset. La lettura a porzioni rende integrale il contesto solo se tutte
le parti restano effettivamente disponibili al modello contemporaneamente.

Non caricare il JSON tecnico completo oltre al testo se basta usarlo per le
provenienze: sarebbe una duplicazione inutile. Conserva però tabelle, note,
didascalie e passaggi contrari. Quando immagini o layout sono essenziali, usa
la visione se supportata e includine il costo nel budget; l'OCR non sostituisce
le informazioni grafiche. Un'immagine non leggibile o un errore di estrazione
restano lacune da dichiarare anche quando tutto il testo estratto entra.

Il vincolo riguarda il contesto di analisi, non la risposta finale: non serve
restituire all'utente l'intero fascicolo. Non inviare contenuti a servizi o
modelli vietati dalla pratica per soddisfare il requisito; segnala il conflitto.

## Valutare lo spazio senza inventarlo

Usa il budget residuo esposto dall'ambiente e un tokenizer compatibile, se
disponibili. Considera richiesta, cronologia, istruzioni/guide, risultati dei
tool, testi/immagini e spazio per ragionamento e risposta. Non assumere una
finestra fissa dal nome del modello e non equiparare byte, parole e token.
Una stima prudenziale va chiamata stima. Se capienza o caricamento integrale
non sono accertabili, dichiaralo prima della lettura selettiva.

## Avvisare prima di ridurre la copertura

Prima di usare estratti, riassunti, ricerca selettiva o lotti spiega brevemente:

- quali documenti o parti non entreranno insieme nel contesto;
- quale metodo userai e il suo limite rispetto alla lettura integrale;
- quali alternative sono praticabili, ad esempio restringere il quesito,
  lavorare per gruppi o usare un ambiente con maggiore capienza.

Esempio, senza inventare conteggi: «I documenti non entrano tutti insieme nel
contesto disponibile. Li leggerò per gruppi e conserverò un registro delle
fonti; per confronti trasversali recupererò i passaggi originali. La lettura
dei gruppi precedenti non resterà integralmente nel contesto».

L'avviso è preventivo: non va nascosto nella risposta finale dopo aver già
ridotto le fonti. Non impone una nuova autorizzazione se il metodo rientra nel
mandato. Se l'utente ha richiesto esclusivamente una lettura integrale simultanea
o vietato selezioni, il limite richiede una sua scelta prima di proseguire con
un metodo incompatibile.

I lotti non aumentano la finestra di contesto né un budget totale residuo:
se manca spazio anche per un gruppo utile e la risposta, occorre un contesto
nuovo o maggiore capienza prima dell'analisi, non una promessa di lettura a lotti.

Nei lotti conserva registro di parti lette, documenti/pagine, citazioni,
negazioni, questioni aperte e parti escluse. Per un confronto recupera di nuovo
le fonti originali necessarie; il riepilogo di un lotto è una memoria di lavoro,
non il suo testo integrale. Dopo compattazione automatica o perdita di contenuto
non continuare a dichiarare l'intero fascicolo presente: informa l'utente prima
di affidarti a quel riepilogo o passa a una strategia già dichiarata.
