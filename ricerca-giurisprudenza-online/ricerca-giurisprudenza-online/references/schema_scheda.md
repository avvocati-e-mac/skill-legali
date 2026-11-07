# Schema della scheda e regole di estrazione

Una scheda per provvedimento: `lavoro/schede/<id>.json`. Lo script `scripts/controlli.py` la valida: i campi sono tutti obbligatori, non se ne possono aggiungere altri e i valori a elenco devono essere esattamente quelli indicati. Dato assente = `"non indicato"` (per le liste: `[]`).

## Schema

```json
{
  "id": "12345",
  "estremi": {
    "ufficio": "TAR Lazio - Roma",
    "sezione": "Sezione Terza",
    "grado": "primo grado",
    "tipo": "sentenza",
    "data_decisione": "2025-03-14",
    "data_deposito": "2025-03-20",
    "numero": "1234/2025",
    "rg": "5678/2024",
    "giudice": "Presidente X, estensore Y"
  },
  "url_scheda": "https://...",
  "url_file": "https://...",
  "fonte_testo": "provvedimento",
  "testo_letto": "integrale",
  "chi": "avvocato",
  "come_emerge": "...",
  "fatti": "...",
  "parte_rilevante": "...",
  "norme_applicate": ["art. 96 c.p.c."],
  "esito": "rigetta",
  "definitivo": "non indicato",
  "motivo_reale_dell_esito": "...",
  "tema_causa_dell_esito": "no",
  "ruolo_del_tema": "concorrente",
  "conseguenze_legate_al_tema": ["condanna art. 96 co. 3", "spese"],
  "importi": ["euro 2.000"],
  "citazioni": [{"testo": "...", "pagina": "4"}],
  "precedenti_citati": ["Cass. n. ..."],
  "dubbi": []
}
```

## Definizioni e valori ammessi

| Campo | Valori / contenuto |
|---|---|
| `id` | uguale al nome del file; solo lettere, cifre e `-` (niente `_`) |
| `estremi.*` | tutti e nove i campi presenti; le date in formato `AAAA-MM-GG` (o `non indicato`); `giudice` = giudice monocratico o collegio |
| `url_scheda`, `url_file` | URL come in `elenco.csv` (o `non indicato`) |
| `fonte_testo` | `provvedimento` (testo del provvedimento) \| `massima_sito` (solo la massima o il sommario del sito) |
| `testo_letto` | `integrale` \| `parziale` \| `no` (PDF scansione senza testo: niente OCR, scheda compilata dai dati del sito, segnalalo in `dubbi`) |
| `chi` | chi ha usato / sollevato il tema: `avvocato` \| `parte` \| `giudice` \| `ctu` \| `altro` |
| `come_emerge` | in che modo il tema entra nella causa (una frase) |
| `fatti` | max 60 parole |
| `parte_rilevante` | max 150 parole; ciò che il testo dice sul tema |
| `norme_applicate` | lista di norme citate nella parte rilevante |
| `esito` | esito sul merito o sul rito: `accoglie` \| `rigetta` \| `inammissibile` \| `improcedibile` \| `altro` (cassa, rinvia, ecc.: `altro`) |
| `definitivo` | `si` \| `no` \| `non indicato` |
| `motivo_reale_dell_esito` | max 30 parole; perché il giudice ha deciso così, a prescindere dal tema |
| `tema_causa_dell_esito` | `si` \| `no` \| `non chiaro`: riferito all'esito principale (merito o rito) |
| `ruolo_del_tema` | `decisivo` = senza il tema l'esito di almeno un capo cambierebbe \| `concorrente` = pesa insieme ad altri motivi autonomi \| `obiter` = detto ma non necessario alla decisione \| `marginale`. Va valutato su TUTTI i capi della decisione: merito o rito, ma anche art. 96, spese, trasmissione atti |
| `conseguenze_legate_al_tema` | lista, uno o più valori: `condanna art. 96 co. 3` \| `condanna art. 96 co. 4` \| `trasmissione atti all'Ordine` \| `spese` \| `nessuna` \| `altro` (`nessuna` esclude gli altri; se `altro`, spiega in `dubbi`). Indica solo le conseguenze che il provvedimento collega al tema |
| `importi` | lista di importi come scritti nel testo |
| `citazioni` | lista di `{"testo": ..., "pagina": ...}`; ogni testo max 25 parole, copiato dal file `testi/<id>.txt`, senza omissioni `[...]`; `pagina` come nel testo |
| `precedenti_citati` | lista di precedenti richiamati sul tema |
| `dubbi` | lista di incertezze, lacune, scansioni, incoerenze |

Coerenza: se `ruolo_del_tema` è `obiter` o `marginale`, il tema non può essere la causa dell'esito né di una condanna ex art. 96. Lo script segnala come avviso le incoerenze evidenti.

## Regole di estrazione (per il subagente)

1. Apri il provvedimento una sola volta. Verifica subito la pertinenza: se non affronta il TEMA nella motivazione, non compilare la scheda, aggiungi una riga a `lavoro/scartati.csv` (`id,titolo,motivo`) e passa oltre.
2. Leggi il testo INTEGRALE, a blocchi se è lungo. Se nel browser il PDF appare vuoto, estrai il testo con pdf.js caricato da cdnjs tramite `javascript_tool` (verifica prima che la versione scelta esista). Con Claude in Chrome prova prima `get_page_text`; il metodo pdf.js in Chrome è da verificare al primo uso (`references/ambienti.md`). Se è una scansione senza testo: niente OCR, `testo_letto = "no"`.
3. Salva in `lavoro/testi/<id>.txt` SOLO: intestazione (prime 1.500 battute), i passaggi sul TEMA con 300 battute prima e dopo e il numero di pagina (riga `[pag. N]`), il dispositivo (ultime 2.000 battute). Non ricopiare tutto il testo. Togli gli spazi spuri dentro le parole prodotti dall'estrazione.
4. Copia le citazioni dal file `testi/<id>.txt` appena salvato (rileggilo), non dalla memoria.
5. Compila `lavoro/schede/<id>.json` secondo lo schema. Tieni separato ciò che il testo dice da ciò che deduci.
6. Con il browser integrato: una scheda (tab) per subagente, da chiudere alla fine. Con Claude in Chrome o un browser di Codex: estrae solo l'orchestratore, in schede nuove create apposta e chiuse alla fine, mai quelle dell'utente. Non digitare credenziali, non aggirare login, captcha o robots.
7. Restituisci max 150 parole: id elaborati, id scartati, problemi.
