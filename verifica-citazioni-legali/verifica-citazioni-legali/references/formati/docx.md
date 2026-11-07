# Atto in Word (.docx)

## Lettura
- `estrai_citazioni.py` usa `pandoc -t plain --wrap=none --track-changes=accept`. Le revisioni pendenti vengono **accettate** in lettura, cioè si verifica il testo come sarebbe dopo l'accettazione: dillo all'utente se ce ne sono.
- La posizione è espressa come **paragrafo** (par. N) o **nota** (nota N). Le note a piè di pagina, dove gli atti mettono spesso le citazioni, sono incluse.
- I numeri di paragrafo sono quelli del testo estratto e non coincidono con la numerazione di Word: per questo ogni voce ha la **stringa da cercare**, da usare con Trova (Cmd/Ctrl+F).
- Il formato `.doc` va prima salvato come `.docx`.

## Stile del «testo da incollare»
- Testo semplice, pronto da incollare in Word, con le istruzioni di formato tra parentesi quadre a fine riga, per esempio: `[corsivo: Cass. civ., sez. II, 13.11.2024, n. 29331]`, `[link su «art. 1669 c.c.»: https://…]`.
- Il diff va scritto a parole: «togli: …» / «aggiungi: …», più il blocco ```diff```.

## Applicazione selettiva (Fase 6)
- Usa la skill **`docx`** per creare `02_versione_corretta.docx` con **revisioni tracciate** (autore «Verifica citazioni») e un **commento** per ogni ID, che riporta il verdetto e la fonte. È il modo in cui un avvocato lavora in Word: accetta o rifiuta ogni modifica.
- Se la skill `docx` non è disponibile: produci `03_registro_modifiche.md` con le coppie Trova/Sostituisci, una per ID.
- Non convertire il docx via pandoc per salvarlo: perderebbe stili, intestazioni e numerazioni.
