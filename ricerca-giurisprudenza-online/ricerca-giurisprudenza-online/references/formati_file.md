# Cartella del progetto e formati dei file di lavoro

Da leggere all'inizio della Fase 0 (creazione della cartella) e della Fase 2 (scrittura di `elenco.csv`).

## Cartella
Su macOS la cartella che il Finder in italiano mostra come "Documenti" è `~/Documents` sul disco: se l'utente indica "Documenti/...", usa `~/Documents/...`. Default: `~/Documents/Ricerche/<tema-breve>`. Crea con `mkdir -p`. Al primo accesso macOS può chiedere all'utente il permesso di accedere a Documenti: è normale.

```
<cartella>/lavoro/   elenco.csv, scartati.csv, ricognizione.md, testi/, schede/,
                     controlli.txt, pagine.jsonl, conteggi.txt, tabelle.md, bozza.md, errori.txt (se ci sono errori)
<cartella>/pdf/      provvedimenti scaricati
<cartella>/report.md
```

## elenco.csv
Colonne: `id,ufficio,sezione,grado,tipo,data,numero,rg,url_scheda,url_file,pertinenza,motivo,da_leggere,formato`
- `id`: breve, solo lettere, cifre e trattino (niente sottolineatura); di solito il numero della scheda sul sito
- `data`: AAAA-MM-GG
- `pertinenza`: alta | media | bassa; `motivo`: max 15 parole
- `da_leggere`: si | no (si fino a MAX_DA_LEGGERE, per pertinenza e recenza)
- `formato`: pdf | html (default pdf)
- separatore virgola, testo tra virgolette se contiene virgole

## scartati.csv
Colonne: `id,titolo,motivo`. Scrivi sempre almeno l'intestazione. Ci finiscono i candidati scartati dalla ricerca (titolo, estratto, data) e quelli che l'estrattore trova non pertinenti all'apertura.

## ricognizione.md
Pagina d'ingresso; come si cerca; schema dell'URL della scheda e del file; formato; strumento che funziona; provvedimento di prova; quanti risultati dà il sito per ogni interrogazione. Con un profilo del sito è la copia del profilo più il registro delle interrogazioni.

## scarica.tsv (solo per scarica.sh)
Quattro colonne separate da tabulazione, nessuna vuota (se manca un dato scrivi `-`):
`url_file <TAB> url_scheda <TAB> nome_file <TAB> formato`
`nome_file` ASCII: `AAAA-MM-GG_ufficio_numero_<id>.pdf`. Se python3 c'è, `scarica.py --piano lavoro/scarica.tsv` lo genera.

## pagine.jsonl (scritto da pagine.py)
Una riga JSON per citazione dei soli provvedimenti scaricati come PDF; il file è riscritto per intero a ogni esecuzione, chiave (`id`, `i`). Le schede non cambiano.
Campi: `id`; `i` (indice in `citazioni` della scheda); `file_pdf`; `sha256_pdf`; `metodo` (`check_pdf_quote` | `pdftotext` | `nessuno`); `stato` (`trovata` | `ambigua` | `non_ritrovata_nel_pdf` | `non_verificabile`); `pagina_fisica` (numero o null); `note`.
La ricerca usa `citazioni[].testo`, non il campo `pagina`. `non_ritrovata_nel_pdf` non vuol dire citazione falsa: il testo estratto dal PDF non la contiene così com'è. La pagina è fisica (n-esima del PDF), non il numero stampato.
