# Dal JSON alla citazione controllabile

## Dossier e metodo ordinario

Nella cartella di lavoro della pratica conserva gli originali o il riferimento
alla loro posizione, le copie esatte di JSON/Markdown salvati da MCP, i derivati
per pagine e il registro. Registra gli SHA-256 del PDF e del JSON al momento
della conversione e controllali prima di riusare i risultati. Gli hash legano
una verifica a quei byte, ma non provano da soli che il server abbia convertito
quel PDF: conserva anche ricevuta/chiamata di conversione e chiave restituita.

Esempi shell: sostituisci i percorsi con quelli effettivi, citandoli in modo
sicuro. `SKILL` qui rappresenta la cartella che contiene `SKILL.md`, non una
variabile già impostata. Gli script Python standard funzionano senza Docling
nel Python della chat; il confronto sul PDF richiede invece `pypdfium2`.

```sh
python3 '/percorso/SKILL/scripts/export_page_references.py' \
  --json '/pratica/lavoro/D01.docling.json' \
  --output-prefix '/pratica/lavoro/D01'
```

Produce `D01.pagine.md` e `D01.riferimenti.json` e rifiuta di sovrascrivere file.
L'ordine segue l'albero Docling, raggruppato per pagina, senza dedurre un ordine
visivo dalle coordinate. Conserva interi i blocchi multipagina, elenca celle e
coordinate delle tabelle e segnala immagini, elementi senza provenienza e
blocchi non raggiunti dall'albero. Non riproduce il layout. Pagine senza blocchi
non sono necessariamente vuote. Non taglia `charspan` con semantica sconosciuta.

Se un blocco ha pagine candidate 4 e 5, cerca la frase su entrambe nell'originale.
Puoi attribuirla alla sola p. PDF 5 dopo il riscontro diretto su quella pagina,
anche senza un profilo degli indici Docling. Se non puoi controllarla resta
«pp. candidate 4–5, non verificate»; non scegliere la pagina più comoda.

```sh
python3 '/percorso/SKILL/scripts/check_pdf_quote.py' \
  --pdf '/pratica/originali/contratto.pdf' --pages 4 5 \
  --quote 'passaggio realmente estratto' \
  --output '/pratica/lavoro/C01.riscontro-testo.json'
```

Lo script legge il **livello testo del PDF originale** con PDFium e cerca tutte
le occorrenze nelle pagine fisiche indicate (contigue, 1-based). Conserva le
pagine effettivamente intersecate dal match, con una mappa ai caratteri estratti;
non usa gli offset Docling. Normalizza NFD, spazi e alcune virgolette/apostrofi,
mantenendo accenti, maiuscole e numeri. Non riunisce parole sillabate né corregge
OCR. Il report contiene hash e versione del lettore. `text_match_found` attesta
solo corrispondenza nel livello testo: **non** riscontro visivo o supporto logico
all'affermazione. `ambiguous_text_match` conserva tutte le occorrenze.
`text_not_found` riguarda solo quel livello testo e quelle pagine; una scansione
può essere leggibile nell'immagine anche senza testo. Non cercare un virgolettato
usando la parafrasi dell'assistente. Per tabelle controlla intestazioni, unità,
righe/colonne e note nella resa visiva.

Per la verifica visiva apri le pagine nel lettore PDF della piattaforma oppure
rendile con un programma disponibile (PDFium/Poppler), poi **guardale**. Registra
pagina, file immagine o riferimento al lettore, passaggio osservato ed eventuali
difformità. Una resa grafica presente su disco ma non ispezionata resta non
verificata. Le etichette PDF del visualizzatore non sono automaticamente i numeri
stampati: registra questi ultimi solo dopo averli letti nella pagina.

## Registro delle affermazioni

Per risposte brevi il registro può restare una tabella nella risposta; per dossier
salvalo come Markdown e/o JSON accanto ai derivati. Non imporre nuove cartelle
se lo studio ha già una struttura. Modello di riga (valori d'esempio sintetici):

| ID | Affermazione e natura | Fonte e passo | Pagine e controllo | Esito |
|---|---|---|---|---|
| C01 | Il fornitore dichiara la consegna il 12 marzo; parafrasi | D01, lettera.pdf; «La consegna è avvenuta il 12 marzo»; anchor letto dal JSON | p. PDF 2; confronto sul livello testo, visivo non eseguito | supporta una dichiarazione del fornitore; non prova da sola la consegna |

Il registro effettivo deve contenere anche SHA-256, percorso/riferimento della
fonte, pagine candidate rispetto a confermate, estratto di contesto, evidenza
del controllo ed eventuali passi contrari. Per più fonti associa alla stessa
affermazione più record documento/passo/pagine/metodo, senza riusare hash o
numerazioni fra documenti. Nel testo finale scrivi, ad esempio:

> Il fornitore dichiara che la consegna è avvenuta il 12 marzo (doc. D01,
> lettera.pdf, p. PDF 2; riscontro sul livello testo).

Non convertire la frase in «La consegna è provata». Un'inferenza va etichettata
e deve citare tutti i suoi presupposti. Per una scadenza calcolata distingui
data documentata, regola giuridica verificata altrove e calcolo dell'assistente.
Se due fonti si contraddicono, cita entrambe senza risolvere il conflitto per
ordine di acquisizione. Non riportare interi fascicoli nella chat se bastano
gli estratti pertinenti.

## Metodo avanzato: intervalli Docling

Solo se serve automatizzare citazioni attraverso blocchi multipagina o più
anchor, leggi [intervalli.md](intervalli.md) e usa `citation_provenance.py`.
Senza profilo comprovato lo script cerca il passo ma non propone pagine; il
metodo ordinario di confronto diretto sul PDF resta disponibile. Non inventare
profili pur di ottenere un numero. Anche con profilo valido lo script mantiene
`citation_verified: false`: non controlla il PDF e non certifica le dichiarazioni
inserite nel profilo.
