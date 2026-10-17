# Atto in Markdown (.md)

## Lettura
- `estrai_citazioni.py` indica la posizione come **riga**.
- I link `[testo](url)` vengono letti: verifica anche l'URL.

## Stile del «testo da incollare»
- Estremi in corsivo: `*Cass. civ., sez. II, 13.11.2024, n. 29331, Rv. 673088-02*`.
- Norme con link: `[art. 1669 c.c.](https://www.normattiva.it/uri-res/N2Ls?urn:...~art1669)`.
- Virgolette basse «…».
- Il diff va in un blocco ```diff```.

## Applicazione selettiva (Fase 6)
- Copia in `02_versione_corretta.md` e sostituisci le stringhe esatte, dopo aver controllato che siano univoche.
- Se l'atto finale si genera da questo .md (pandoc → docx/pdf), segnala che i derivati vanno rigenerati.
