# Rilevare scansioni e avvertire sull’OCR

Verifica del 28 ottobre 2026: una query Perplexity standard, dopo controllo
accesso, seguita da lettura diretta delle fonti ufficiali. Nessun PDF reale,
installazione o configurazione modificati. Le proposte euristiche seguenti
non sono un classificatore di provenienza certificato da Docling.

## Esito operativo

È possibile rilevare **indizi della struttura di ogni pagina**, non garantire
l’origine storica del PDF. Un testo selezionabile può essere nativo oppure un
livello OCR sovrapposto a una scansione; il documento può contenere pagine di
tipi diversi. pypdf distingue espressamente PDF nativi, scansioni e scansioni
con OCR e avverte che gli errori del livello OCR possono sommarsi a quelli di
estrazione. Evitare quindi «testo selezionabile = nativo» o «zero caratteri =
scansione certa». [pypdf: estrazione e tipi di PDF](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)

Criteri proposti, da conservare come osservazioni e confermare sulle immagini:

| Segnali per pagina | Esito prudente |
|---|---|
| Immagine dominante, testo utile assente | Pagina compatibile con scansione senza livello testo; possibile OCR necessario |
| Immagine dominante e testo presente | Pagina con immagine e livello testo; possibile scansione già OCR |
| Testo leggibile, nessuna immagine dominante | Pagina prevalentemente testuale; possibile nativo digitale |
| Nessun testo, nessuna immagine dominante, errori o segnali contrastanti | Tipo indeterminato: può essere bianca, grafica vettoriale, testo convertito in tracciati o estrazione fallita |
| Pagine di categorie diverse | Documento misto, con pagine e limiti indicati |

Un logo non trasforma una pagina testuale in scansione. Una pagina rasterizzata
può anche essere stata generata digitalmente. Un’immagine dominante non prova
che vi sia testo leggibile. Sono necessarie ispezione visiva e descrizione della
copertura controllata. Le soglie di area o caratteri sono convenzioni del
rilevatore, non certezze o percentuali di accuratezza.

## Procedura leggera per la skill

1. Prima della conversione controllare le pagine pertinenti; per fascicoli lunghi
   campionare e dichiarare quali pagine sono state viste e quali no. Non
   attribuire il tipo dell’intero PDF dalla copertina. Se occorre classificare
   tutto il documento, ispezionare tutte le pagine o conservare l’incertezza.
2. Leggere quantità e qualità del testo e presenza/dimensione delle immagini
   con lettore PDF o libreria già disponibile, senza avviare OCR in questa fase.
3. Guardare la resa delle pagine dubbie. Solo una resa prodotta su disco, senza
   ispezione, non è controllo visivo. Per una scansione già OCR confrontare il
   livello testo con l’immagine: l’accordo di due estrattori non valida l’OCR.
4. Mostrare l’avvertimento **prima** della conversione che potrebbe eseguire
   OCR. Non serve imporre una nuova conferma per ogni documento se l’analisi è
   già autorizzata; serve comunicare tipo probabile, rischio e controllo previsto.
5. Su input protetti o corrotti riportare il problema concreto, senza dedurne
   il tipo; chiedere una copia leggibile/password attraverso il canale ammesso,
   senza inserirla in log, rapporti o comandi pubblici. Nessun tentativo di
   aggirare protezioni.

## Che cosa può fare davvero Docling

Nella CLI ufficiale corrente `--ocr` è abilitato per impostazione predefinita;
`--force-ocr` è falso e deprecato in favore di `--ocr-mode full_page`.
L’OCR abilitato non equivale a rifare ogni pagina: modalità e pipeline decidono
quali regioni elaborare. L’OCR full-page sostituisce il testo preesistente;
non forzarlo soltanto per scoprire il tipo del PDF. La guida API specifica che
`do_ocr=True` abilita OCR per immagini/scansioni e che può sostituire o integrare
il testo. Verificare le opzioni **effettive del server**, non solo i default.
[Docling CLI](https://docling-project.github.io/docling/reference/cli/),
[opzioni pipeline](https://docling-project.github.io/docling/reference/pipeline_options/),
[esempio OCR full-page](https://docling-project.github.io/docling/_generated/examples/full_page_ocr/)

Docling documenta inoltre che persino il rilevamento di un livello testo rotto
non scopre tutte le parole errate ma alfabeticamente plausibili. La funzione
`replace_broken_text_layer` è disattivata di default nella documentazione
corrente. Non promettere pertanto che la selezionabilità o la conversione
riuscita attestino la correttezza del testo.
[Docling: livello testo corrotto](https://docling-project.github.io/docling/concepts/OCR/#replace-a-broken-pdf-text-layer)

Il codice locale installato di `docling-mcp 3.4.0` è stato letto senza eseguirne
la conversione: `LocalDocumentConverter` copia `settings.do_ocr` in
`PdfPipelineOptions.do_ocr`; nelle impostazioni server il valore predefinito
è `True`. Non è stata letta o pubblicata configurazione privata: questo dato
non certifica l’opzione effettiva di qualunque sessione.

## Avvertimenti suggeriti

Con scansione probabile e OCR attivo verificato:

> Queste pagine sembrano scansioni. Docling userà il riconoscimento ottico del
> testo (OCR), che può sbagliare nomi, date, importi e altri passaggi. Verificherò
> le citazioni sulle immagini originali e segnalerò le letture incerte.

Se l’opzione effettiva non è nota:

> Queste pagine sembrano scansioni e possono richiedere OCR. Non posso ancora
> verificare se il server lo abbia attivo; il testo riconosciuto può contenere
> errori e andrà confrontato con le immagini originali.

Se OCR è disattivo, dire che le immagini potrebbero non fornire testo e
predisporre l’opzione adeguata entro il mandato; non dichiarare «Docling farà
OCR». Per scansione già OCR parlare di **livello testo potenzialmente
inesatto**, senza promettere un nuovo riconoscimento.

## API verificata, se si aggiunge un helper

Verificata in sola lettura nell’installazione `pypdfium2 5.14.0` e sulla
[documentazione ufficiale](https://pypdfium2.readthedocs.io/en/stable/python_api.html):
`PdfPage.get_textpage()`, `PdfTextPage.count_chars()`, `get_text_bounded()`;
`PdfPage.get_objects(filter=[raw.FPDF_PAGEOBJ_IMAGE], max_depth=15)`;
`PdfObject.get_bounds()` restituisce left/bottom/right/top;
`PdfPage.get_size()` e `render()` sono disponibili. **`get_pos()` non esiste**
in questa versione. Chiudere textpage e page; elaborare PDFium in sequenza,
non in thread paralleli. Non serve renderizzare per ottenere i contatori.

Un helper dovrebbe restituire pagine esaminate, conteggi e indizi, non un
verdetto «nativo/scansione» certo. L’area dei bounding box è un’approssimazione:
ritagli, trasformazioni, form annidati e immagini sovrapposte richiedono cautela.
Per scansioni composte da più tasselli, la sola immagine più grande può non
essere dominante; una semplice somma può invece contare due volte le
sovrapposizioni. Non occorre sviluppare geometria complessa per questo avviso:
conservare «indeterminato» e ricorrere alla resa visiva è più corretto.
