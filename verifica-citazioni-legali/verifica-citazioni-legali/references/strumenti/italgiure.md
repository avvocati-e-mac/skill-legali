# ItalgiureWeb (Cassazione): CLI `igw` e MCP `italgiure`

Archivio ufficiale della Corte di cassazione. Per i dettagli operativi carica la skill `italgiureweb`.

## Che cosa dà
- **Massime ufficiali** con Rv: esatte, ma sono il testo del Massimario, non la motivazione.
- **Testo integrale (PDF)**:
  - testo digitale per il civile dal 2022, citabile alla lettera;
  - OCR dal 2011 circa: va riscontrato sull'immagine;
  - fino al 2010 circa, scansioni senza testo: serve un OCR locale (es. `ocrmypdf -l ita --sidecar out.txt in.pdf out.pdf`).
- Massime conformi e difformi, quando la massima le indica: utili per la validità nel tempo.

## Limiti
- **Contiene solo le pronunce massimate.** Uno zero per numero e anno vuol dire «non massimata o in altro archivio», non «inesistente». L'esistenza si verifica su un'altra fonte (es. BuddaLaw con ECLI).
- Una sola sessione browser e un limite di richieste: **non usarlo in parallelo**, e non da più agenti.
- Le query non accettano `non`/`NOT` (errore del sito).
- Il download del PDF richiede un **consenso esplicito** per ogni file (opzione `--download` della CLI, oppure `prepare_pdf` seguito da `download_pdf` nell'MCP).
- Nei PDF ogni pagina ha un'intestazione di firma che spezza le frasi a cavallo di pagina. `confronta_verbatim.py` la rimuove automaticamente (righe ripetute).

## Uso tipico
- Ricerca per numero: `igw --visible search --decision-number N --year AAAA` (aggiungi `--read K` per leggere la massima K).
- Per Rv: `--massima-number NNNNNN` (le sei cifre senza il suffisso).
- Se l'utente vuole vedere il browser, usa `--visible`. Fuori dal sandbox, se il sandbox blocca il browser.
- Copia i PDF scaricati in `<output>/fonti/` ed estrai il testo con `pdftotext`.
