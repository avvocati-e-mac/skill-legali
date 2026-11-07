# Atto in LibreOffice/OpenDocument (.odt)

## Lettura
- `estrai_citazioni.py` usa `pandoc -t plain --wrap=none`. La posizione è il **paragrafo** o la **nota** del testo estratto, e ogni voce ha la **stringa da cercare** per Trova e sostituisci (Cmd/Ctrl+H).
- Le modifiche registrate non accettate possono non comparire come nel documento: se l'utente usa «Registra modifiche», chiedigli di accettarle o rifiutarle prima.

## Stile del «testo da incollare»
Come per docx: testo semplice con le istruzioni di formato tra parentesi quadre, più il diff.

## Applicazione selettiva (Fase 6)
Non c'è una skill dedicata per l'ODT. In ordine di preferenza:
1. **Istruzioni Trova/Sostituisci** in `03_registro_modifiche.md`, una per ID. L'utente le applica in LibreOffice e vede ogni modifica: è la via più sicura.
2. **Modifica di `content.xml`** in una copia, con Python `zipfile`: estrai, sostituisci, ricomprimi mantenendo `mimetype` come primo file non compresso. Funziona solo se la stringa da cercare sta **tutta in un unico nodo di testo**: verificalo prima, perché una citazione con corsivo è spezzata in più `<text:span>`. Se non è così, torna al punto 1.
3. **Conversione via pandoc** (`pandoc 02_versione_corretta.md -o 02_versione_corretta.odt`) solo se l'utente accetta di perdere la formattazione originale: dichiaralo.
