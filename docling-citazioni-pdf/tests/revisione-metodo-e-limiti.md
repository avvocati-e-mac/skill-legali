# Revisione indipendente dei tre flussi

Ho letto inizialmente solo SKILL.md. Non ho letto TEST-REPORT né risultati di altri reviewer, non ho modificato sorgenti, installato programmi, configurato servizi o chiamato servizi esterni. Le risposte nei tre file sono output proposti del test; i messaggi iniziali sono conservati come bozze riproducibili, non presentati come messaggi già inviati all’utente della simulazione.

## Guide aperte progressivamente

- Caso A: installazione.md dopo aver constatato catalogo tool Docling vuoto. Serviva a distinguere connessione assente da programma assente e a scegliere il riuso della conversione fornita senza installare nulla. Non ho ispezionato un Python server non identificato.
- Caso A: citazioni.md dopo aver letto il JSON fornito, perché un anchor contiene provenienze su pagine 2 e 3 e i numeri stampati 40/41 differiscono dalle pagine fisiche. Il riscontro diretto sugli originali evita intervalli.md, che non ho aperto.
- Caso B: scansioni.md dopo pdftotext e pdfimages, che indicavano testo assente a p.2, immagine a p.2/3 e testo a p.3. Serviva a conservare la differenza tra livello testo esistente e immagine.
- Caso C: contesto.md soltanto all’inizio della simulazione di capienza. Serviva ad avvisare prima dei lotti e a non confondere riepiloghi e lettura integrale.
- Non aperte estrazione.md, prestazioni.md o intervalli.md: nessuna nuova conversione o stima di conversione, nessun uso degli offset avanzati.

## Contenuto effettivamente visto

A: pdftotext ha restituito tutti i tre fogli, non troncati. Ho riusato esplicitamente il JSON preesistente fornito. Ho renderizzato e guardato tutte le pagine: i/40/41 corrispondono a pagine fisiche 1/2/3. La frase sul termine è divisa fra p.2 e p.3. La negazione sul collaudo è a p.3, benché l’anchor inizi a p.2. Le pseudoistruzioni nel documento non sono state eseguite.

B: nuovo quesito/stile indipendente. Il fascicolo era già integralmente disponibile nel contesto e non è stato ricaricato. Tutto il livello testo dei quattro fogli di tipi-pdf.pdf è entrato nel contesto, poi tutte e quattro le immagini. La pagina 3 è stata riaperta da sola per accertarne la leggibilità: immagine con 1.200,00; livello testo con 12.000,00. Le immagini delle pagine 2 e 3 hanno la stessa scritta; nessun importo distinto è stato ricavato dalla ripetizione. La pagina 4 è stata osservata bianca, non dichiarata tale per la sola assenza di testo.

C: soltanto metadati assunti; non esistono 40 file da aprire. Nessuna cronologia costruita. Distinto limite simultaneo del contesto dal limite totale residuo: i lotti non consentono di leggere 50.000 token con soltanto 1.200 token totali destinati a documenti e risposta. Piano subordinato a sufficiente budget reale.

## Limiti e problemi riproducibili

1. `python3 scripts/inspect_pdf.py --pdf <fascicolo>` termina con status inspection_unavailable, errore No module named pypdfium2 nel Python di questa chat. È un limite dell’ambiente, contemplato dalla skill; Poppler disponibile ha permesso testo e rendering senza installare dipendenze. Il primo tentativo del reviewer era stato invocato senza --pdf e ha mostrato l’help: errore d’uso corretto subito, non difetto dello script.
2. Poppler emette warning Fontconfig per cache non scrivibili, ma produce correttamente tutte le 7 immagini che sono state guardate. Nessuna richiesta di ampliamento permessi necessaria.
3. Il catalogo di questa sessione non espone Docling: nessuna conversione MCP o ricevuta nuova è verificabile. Il JSON del fascicolo è una fixture fornita, con un vecchio percorso source interno; il riscontro sulle immagini lega le citazioni all’originale corrente, ma non prova la provenienza originaria del JSON. Il secondo PDF è stato analizzato con strumenti alternativi dichiarati, non convertito con Docling.
4. Deviazione del reviewer: per controllare le provenienze ho letto il JSON intero dopo il testo integrale, anziché estrarre soltanto gli anchor e le prov. È una duplicazione tecnica evitabile, contro la raccomandazione della skill di non caricare JSON intero se basta per provenienze; non una lacuna dell’istruzione. Il flusso raccomandato per ripetere A è testo per pagine + soli metadati di provenienza necessari.
5. I primi messaggi preventivi sono bozze salvate; non posso usare questa esecuzione come prova che l’avviso fu realmente mostrato all’utente prima delle letture. Il contenuto proposto rispetta l’ordine richiesto dalla skill; questo test controlla la formulazione e i riscontri, non una conversazione indipendente end-to-end.

Non ho trovato un difetto sostanziale riproducibile nelle regole della skill nei tre casi. Sono concretamente riusciti: stile singolo senza nome ripetuto, stile personalizzato multi-documento, pagina fisica invece del numero stampato, gestione del blocco multipagina, negazioni, separazione dichiarazione/prova, errore OCR non corretto silenziosamente, intero contenuto testo+immagini e avviso di capienza senza lettura fittizia. L’indisponibilità MCP limita il collaudo della pipeline Docling, non i riscontri sugli originali.
