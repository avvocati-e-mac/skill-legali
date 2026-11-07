# PDF nativo, scansione e rischio OCR

Apri questa guida per scansioni sospette, documenti misti o origine incerta.
Il controllo preliminare trova **indizi per pagina**; non certifica la storia
del documento. Il testo selezionabile può derivare da un precedente OCR.

## Controllo prima della conversione

Usa un lettore PDF disponibile o `scripts/inspect_pdf.py`, se `pypdfium2` è già
presente. Il helper non avvia OCR, non modifica il PDF e non scarica modelli:

```sh
python3 '/percorso/SKILL/scripts/inspect_pdf.py' \
  --pdf '/pratica/documento.pdf' --output '/pratica/lavoro/ispezione.json'
```

Per impostazione predefinita campiona prima pagina, pagina centrale e ultima;
con `--pages 2 4 8` scegli pagine specifiche. Il report dichiara pagine lette e
non lette. Non trasformare il campione in una conclusione sull'intero fascicolo;
per classificarlo tutto occorre esaminare tutte le pagine. Il campionamento
riguarda qui il **formato**, non autorizza una lettura parziale del contenuto
senza l'avviso richiesto in [contesto.md](contesto.md).

| Osservazione | Conclusione prudente |
|---|---|
| Immagine dominante, testo assente o scarso | Scansione probabile; può richiedere OCR |
| Immagine dominante e testo presente | Possibile scansione già OCR o pagina digitale con immagine; controllare la resa |
| Testo presente senza immagine dominante | Livello testo disponibile, origine non certificata |
| Nessun testo né immagine dominante | Indeterminato: pagina bianca, grafica vettoriale, caratteri in tracciati o errore |
| Segnali diversi fra pagine | Possibile documento misto, da descrivere indicando la copertura |

Le soglie del helper (immagine con bounding box almeno al 75% dell'area;
meno di 40 caratteri non bianchi per testo scarso) sono **euristiche dichiarate**,
non percentuali di accuratezza. Considera solo il rettangolo dell'immagine più
grande: tasselli possono nascondere una scansione e ritagli/rotazioni possono
alterare l'area osservata. Un logo non basta per chiamare scansione una pagina;
un'immagine piena può essere stata generata digitalmente. Guarda le immagini
delle pagine dubbie e conserva l'incertezza. Un report generato non è ispezione
visiva. File protetti/corrotti non permettono di dedurre il tipo: segnala il
problema concreto e chiedi una copia leggibile nel canale consentito.

## Avviso preventivo e opzioni effettive

Se le pagine sembrano scansioni **e OCR attivo è verificato**, avvisa prima
della conversione: «Queste pagine sembrano scansioni. Docling userà il
riconoscimento ottico del testo (OCR), che può sbagliare nomi, date e importi.
Controllerò le citazioni sulle immagini originali e segnalerò i dubbi».

Se l'opzione del server non è nota: «Queste pagine possono richiedere OCR;
non ho ancora verificato che sia attivo. Il testo riconosciuto può contenere
errori e andrà confrontato con le immagini». Se è disattivo, spiega che il testo
nelle immagini potrebbe non essere estratto; non promettere OCR e non cambiarne
la configurazione senza necessità e autorizzazione. L'avviso non impone una
nuova conferma per ogni documento se l'analisi è già autorizzata.

Per scansioni già OCR avvisa del rischio del **livello testo esistente**; non
promettere che Docling rifaccia il riconoscimento. OCR attivo per default non
significa OCR nuovo su tutte le pagine. Non forzare full-page OCR per scoprire
l'origine del PDF: può sostituire testo preesistente. Anche due estrattori che
leggono lo stesso livello OCR errato possono concordare; le citazioni sensibili
richiedono confronto con l'immagine, non solo fra parser.

Fonti primarie: [pypdf, tipi di PDF ed errori del livello OCR](https://pypdf.readthedocs.io/en/stable/user/extract-text.html),
[Docling, opzioni della pipeline](https://docling-project.github.io/docling/reference/pipeline_options/),
[Docling, OCR full-page](https://docling-project.github.io/docling/_generated/examples/full_page_ocr/),
[pypdfium2, API lettura pagine e oggetti](https://pypdfium2.readthedocs.io/en/stable/python_api.html).
