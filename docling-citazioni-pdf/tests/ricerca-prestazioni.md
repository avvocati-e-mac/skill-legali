# Docling su CPU e GPU — verifica del 28 ottobre 2026

Ricerca delegata eseguita con skill Perplexity, una query `standard`, senza Deep Research. Le conclusioni sono state confrontate con le fonti primarie originali. Nessun benchmark locale, installazione o modifica di configurazione.

## Risposta utilizzabile

Sì: negli esperimenti controllati esaminati la conversione su sola CPU richiede più tempo. Non esiste però un moltiplicatore valido per tutti i PC, tutti i PDF e tutte le versioni. Occorre distinguere elaborazione standard, OCR e modelli visuali generativi (VLM).

## Confronto controllato con versione dichiarata

Il rapporto degli autori impiega **Docling 2.5.2**, 89 PDF/4.008 pagine, EasyOCR e TableFormer fast. Lo stesso server AWS, con AMD EPYC 7R13, 8 core virtuali, 32 GB RAM e NVIDIA L4 24 GB, viene provato con GPU abilitata e poi nascosta; il caso CPU usa 8 thread. Il documento indica Ubuntu 22.04 e CUDA 12.4.

| Misura pubblicata | Solo CPU x86 | NVIDIA L4 | Rapporto calcolato CPU/GPU |
|---|---:|---:|---:|
| Media della pipeline per pagina | 3,1 s | 0,481 s | circa 6,4 volte |
| Mediana della conversione per pagina | 0,79 s | 0,114 s | circa 6,9 volte |
| OCR medio per pagina sottoposta a OCR | 13 s | 1,6 s | circa 8,1 volte |

L'ultima riga riguarda **soltanto lo stadio OCR**, non la conversione completa. Media e mediana non sono intercambiabili. Sono risultati storici della versione dichiarata, non misure della versione installata dall'utente. Fonte: [Docling Technical Report, §§ 5.1–5.4](https://arxiv.org/html/2408.09869v4).

## Confronti nella guida GPU corrente

La guida ufficiale usa un PDF di 192 pagine con 95 tabelle. Nella riga **standard inline senza OCR**, pubblica due coppie GPU/CPU sulla stessa macchina; la CPU impiega 16 thread PyTorch.

| Macchina dichiarata | GPU | Solo CPU | Tempo equivalente GPU / CPU | Rapporto calcolato |
|---|---:|---:|---:|---:|
| Linux, Ryzen 7 9800, 128 GB RAM, RTX 5090 | 7,9 pagine/s | 1,5 pagine/s | 0,127 / 0,667 s/pagina | circa 5,3 volte |
| Windows 11, Ryzen 7 9800, 64 GB RAM, RTX 5070 | 4,2 pagine/s | 1,2 pagine/s | 0,238 / 0,833 s/pagina | 3,5 volte |

I secondi/pagina e i rapporti sono **calcoli dai throughput pubblicati**, non ulteriori misure. La tabella non dichiara versione esatta del pacchetto, commit o tutti i parametri effettivamente usati: non si deve attribuirle una versione inventata o assumere che ogni esempio della guida sia la configurazione del benchmark. Non riguarda scansioni con OCR. I numeri GraniteDocling VLM nella stessa pagina usano una pipeline diversa e non vanno mescolati con queste coppie CPU/GPU. Fonte: [Docling, GPU support, Performance results](https://docling-project.github.io/docling/usage/gpu/#performance-results).

## GPU presente non significa GPU utilizzata

Docling permette di selezionare CPU, CUDA, MPS e XPU, oltre a AUTO. CUDA/XPU richiedono hardware e runtime compatibili; MPS riguarda macOS. L'esempio ufficiale seleziona esplicitamente CPU, quindi un computer dotato di GPU può comunque elaborare sulla CPU. L'accelerazione dei singoli motori OCR dipende anche dalle librerie impiegate. Fonti: [esempio ufficiale degli acceleratori](https://docling-project.github.io/docling/_generated/examples/run_with_accelerator/), [opzioni della pipeline](https://docling-project.github.io/docling/reference/pipeline_options/) e [supporto GPU/OCR](https://docling-project.github.io/docling/usage/gpu/#ocr-engines).

Nella skill, controllare l'host che esegue **il server MCP** e il dispositivo effettivo, quando osservabile. L'hardware della chat o del PC dell'utente non identifica automaticamente quello del server. La diagnostica dei soli metadati non prova l'uso della GPU. Non abilitare GPU o cambiare motore OCR senza necessità e autorizzazione.

## Avvertimento suggerito

> Docling funziona anche senza GPU, ma l'elaborazione su sola CPU può richiedere sensibilmente più tempo, soprattutto con scansioni e tabelle. I tempi dipendono dai documenti e dalla configurazione: i benchmark pubblici non permettono di promettere una durata per questo computer.

Per fascicoli lunghi su CPU confermata, avvisare **prima** dell'elaborazione estesa. Se utile al compito, misurare un piccolo campione rappresentativo nel medesimo ambiente e con gli stessi modelli, separando avvio/scaricamento da elaborazione, poi stimare un intervallo e indicare l'incertezza. Non disabilitare OCR nelle scansioni o ridurre controlli di struttura per ottenere soltanto un tempo migliore. Nessuna conferma aggiuntiva richiesta per ogni singolo PDF; l'eventuale modifica di installazione o configurazione segue le autorizzazioni già esistenti.
