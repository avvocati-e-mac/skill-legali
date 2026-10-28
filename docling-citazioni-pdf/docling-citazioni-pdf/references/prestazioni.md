# Tempi di conversione su CPU e GPU

Apri questa guida per conversioni senza accelerazione, fascicoli lunghi,
domande sui tempi o scelta del dispositivo. Non caricarla per ogni citazione.

Docling funziona su CPU. Nei benchmark controllati esaminati una GPU compatibile
riduce sensibilmente i tempi, ma non esiste un fattore valido per ogni macchina,
PDF o pipeline. Presenza della GPU e utilizzo effettivo sono condizioni diverse:
verifica il dispositivo del **server MCP**, se osservabile, non quello della
shell o del computer da cui si apre la chat. La diagnostica dei metadati dei
pacchetti non prova quale dispositivo stia lavorando.

Quando è confermata l'esecuzione su sola CPU, avvisa prima della conversione:
«Docling lavorerà sulla CPU: l'elaborazione può richiedere più tempo, soprattutto
con scansioni e tabelle. La durata dipende dal fascicolo e dalla configurazione».
Un avviso per il lotto basta, senza ripeterlo a ogni file o chiedere nuovi
permessi per una conversione già autorizzata. Se il dispositivo è ignoto non
presentare come misurata una lentezza di quel computer.

## Quanto può cambiare: esempi pubblicati

| Prova | CPU | GPU | Rapporto dei tempi CPU/GPU |
|---|---:|---:|---:|
| Guida corrente, PDF 192 pagine/95 tabelle, standard inline senza OCR, Ryzen 7 9800, Linux, RTX 5090, CPU 16 thread | 1,5 pagine/s | 7,9 pagine/s | circa 5,3 volte |
| Stesso PDF e tipo di pipeline, Ryzen 7 9800, Windows 11, RTX 5070, CPU 16 thread | 1,2 pagine/s | 4,2 pagine/s | 3,5 volte |

Sono rapporti calcolati dai throughput pubblicati, non misure del computer
dell'utente. La guida non dichiara la versione esatta del pacchetto e questi
confronti non includono OCR. Non mescolarli con i risultati di pipeline VLM.
[Docling: GPU support, Performance results](https://docling-project.github.io/docling/usage/gpu/#performance-results).

Il rapporto tecnico storico con Docling **2.5.2**, 89 PDF/4.008 pagine, confronta
lo stesso server AMD EPYC 7R13 (8 vCPU) con e senza NVIDIA L4: media della
pipeline 3,1 contro 0,481 secondi/pagina, circa **6,4 volte**; mediana 0,79
contro 0,114, circa **6,9 volte**. La media e la mediana sono misure diverse.
Il circa 8 volte riportato per lo stadio OCR non va applicato alla durata
complessiva. [Rapporto tecnico Docling, §§ 5.1–5.4](https://arxiv.org/html/2408.09869v4).

Questi esempi non fissano un intervallo garantito «3,5–6,9 volte» per le
installazioni future. Incidono modelli, risoluzione, OCR, tabelle, thread,
memoria, dispositivi e versioni.

## Stima pratica e configurazione

Se utile prima di un lotto lungo, misura un piccolo campione rappresentativo
con la stessa pipeline e sullo stesso host. Separa avvio/download iniziale
dall'elaborazione, includi tipi di pagina diversi e restituisci una stima con
incertezza. Non disattivare OCR necessario o controlli di struttura per ridurre
soltanto il tempo.

Docling supporta selezione CPU/CUDA/MPS/XPU/AUTO secondo hardware e librerie;
un sistema con GPU può essere configurato per CPU. Non cambiare dispositivo o
installare driver come conseguenza automatica di una richiesta di analisi.
[Acceleratori Docling](https://docling-project.github.io/docling/_generated/examples/run_with_accelerator/).
