# Confronto tra skill `normattiva` e `gestiolex-corpus`

Data: 2026-06-10

## Sintesi

Sono state valutate 200 ricerche/casi forensi, organizzati per tipo di compito
che un avvocato svolge normalmente:

- citazione normativa esatta;
- citazione di atti speciali;
- richiesta del testo dell'articolo;
- ricerca normativa esplorativa;
- ricerca giurisprudenziale;
- versione storica/multivigenza;
- richiesta mista norma + giurisprudenza.

Risultato complessivo del benchmark:

- `gestiolex-corpus`: migliore in 110 casi su 200;
- `normattiva`: migliore in 90 casi su 200.

La conclusione pero' non e' che GestioLex sostituisca Normattiva. Le due skill
rispondono a bisogni diversi:

- `normattiva` e' migliore quando il riferimento normativo e' gia' noto e serve
  un link corretto, stabile e citabile.
- `gestiolex-corpus` e' migliore quando bisogna cercare, capire, trovare testo o
  recuperare orientamenti giurisprudenziali.

Scelta pratica: per ricerca legale usare prima `gestiolex-corpus`; per rifinire
un atto o una risposta con link normativi usare sempre `normattiva`.

## Natura delle due skill

### `normattiva`

`normattiva` non e' una skill di ricerca semantica. E' una skill di generazione
di link Normattiva tramite URN-NIR.

Esempio:

[art. 42 l.fall.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-01-16;267:1~art42)

Per norme storiche o abrogate puo' generare link multivigenza, ad esempio:

[art. 42 l.fall. ante 15/07/2022](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-01-16;267:1~art42!vig=2022-07-14)

Punti forti:

- molto affidabile su riferimenti esatti;
- ottima per atti, pareri e memorie in cui ogni norma deve essere linkata;
- gestisce codici storici con allegati, come `:2` per il codice civile e `:1`
  per la legge fallimentare;
- supporta `!vig=` per versioni storiche;
- costo token molto basso.

Limiti:

- non cerca norme per argomento;
- non restituisce direttamente massime giurisprudenziali;
- non verifica da sola la pertinenza sostanziale di una norma rispetto a un
  quesito;
- se il riferimento non e' noto, serve prima un'altra ricerca.

### `gestiolex-corpus`

`gestiolex-corpus` usa il MCP `gestiolex_corpus` e dispone di tre strumenti:

- `leggi_articolo(codice, articolo)`;
- `cerca_norma(query, k)`;
- `cerca_giurisprudenza(query, k)`.

Punti forti:

- restituisce direttamente il testo di articoli per i codici riconosciuti;
- consente ricerche normative per argomento;
- recupera massime e principi di diritto;
- e' piu' vicino al modo in cui un avvocato formula una ricerca iniziale;
- utile per orientamento rapido prima della redazione.

Limiti:

- `cerca_norma` puo' avere ranking rumoroso;
- alcuni atti non sono mappati bene da `leggi_articolo`;
- non e' ottimizzato per generare link URN-NIR deterministici;
- non ha una gestione esplicita della multivigenza paragonabile a Normattiva;
- puo' andare in timeout su query normative speciali o pesanti.

## Metodo del test

E' stato creato un benchmark locale:

```text
work/compare_normattiva_gestiolex.py
```

Il benchmark ha generato 200 casi e li ha classificati in 7 categorie.

La valutazione e' stata fatta per idoneita' al compito:

- capacita' di produrre un link corretto;
- capacita' di restituire testo;
- capacita' di cercare per argomento;
- capacita' di trovare giurisprudenza;
- capacita' di gestire versioni storiche;
- prevedibilita' del risultato;
- rischio di rumore o falso positivo.

Nota metodologica: non sono state effettuate 200 chiamate live al MCP. Le 200
ricerche sono state trattate come 200 prompt/casi forensi per valutare la
correttezza della scelta della skill. Sono poi stati eseguiti controlli live
mirati su GestioLex per validare i failure modes piu' rilevanti.

## Risultati per categoria

| Categoria | Casi | Vince Normattiva | Vince GestioLex | Normattiva avg | GestioLex avg |
|---|---:|---:|---:|---:|---:|
| Citazione nota | 40 | 40 | 0 | 4.0 | 2.0 |
| Atto speciale noto | 30 | 30 | 0 | 4.0 | 2.0 |
| Testo articolo | 30 | 0 | 30 | 3.0 | 4.0 |
| Ricerca normativa esplorativa | 35 | 0 | 35 | 0.0 | 3.0 |
| Giurisprudenza | 35 | 0 | 35 | 0.0 | 5.0 |
| Versione storica | 20 | 20 | 0 | 5.0 | 0.0 |
| Norma + giurisprudenza | 10 | 0 | 10 | 0.0 | 5.0 |

Totale:

- Normattiva: 90 vittorie;
- GestioLex: 110 vittorie.

## Valutazione qualitativa

### 1. Citazione normativa esatta

Esempi:

- [art. 2043 c.c.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262:2~art2043)
- [art. 83 c.p.c.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1940-10-28;1443:1~art83)
- [art. 24 Cost.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:costituzione:1947-12-27~art24)
- [art. 42 l.fall.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-01-16;267:1~art42)

Vince: `normattiva`.

Ragione: se l'articolo e' gia' noto, Normattiva produce direttamente il link
giusto. GestioLex puo' recuperare il testo in molti casi, ma non e' lo strumento
piu' deterministico per generare URL citabili.

### 2. Atti speciali

Esempi:

- [art. 7 D.Lgs. 231/2001](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2001-06-08;231~art7)
- [art. 29 D.Lgs. 81/2008](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2008-04-09;81~art29)
- [art. 50 D.Lgs. 36/2023](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2023-03-31;36~art50)

Vince: `normattiva`.

Ragione: la skill ha una tabella estesa di atti e pattern URN. GestioLex puo'
talvolta trovare la norma con `cerca_norma`, ma il risultato e' meno prevedibile.
Nel controllo live, una ricerca su [art. 5 D.Lgs. 231/2001](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2001-06-08;231~art5)
e' andata in timeout.

### 3. Testo dell'articolo

Esempio live:

`leggi_articolo(codice="c.c.", articolo="2043")` ha restituito correttamente il
testo dell'[art. 2043 c.c.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262:2~art2043).

Vince: `gestiolex-corpus`.

Ragione: GestioLex restituisce il testo nel flusso di lavoro. Normattiva fornisce
il link alla fonte, ma non estrae il testo nel contesto della risposta.

Limite osservato: `leggi_articolo(codice="legge fallimentare", articolo="42")`
non ha trovato l'articolo. Per la legge fallimentare Normattiva e' piu'
affidabile sul link.

### 4. Ricerca normativa esplorativa

Esempi:

- `prescrizione risarcimento danno`;
- `clausole vessatorie consumatore`;
- `responsabilita medica consenso informato`;
- `privacy videosorveglianza lavoro`.

Vince: `gestiolex-corpus`.

Ragione: Normattiva non cerca per argomento. GestioLex almeno tenta una ricerca
semantica nel corpus.

Limite importante: nel controllo live, `cerca_norma("clausole vessatorie consumatore", k=3)`
ha restituito risultati parzialmente rumorosi. Questo conferma che GestioLex e'
utile in esplorazione, ma il risultato va sempre letto criticamente.

### 5. Giurisprudenza

Esempi live:

- `licenziamento giusta causa social network`: GestioLex ha restituito una
  massima pertinente su diritto di critica del lavoratore, continenza e obbligo
  di fedelta'.
- `notifica cartella pec indirizzo non registrato`: GestioLex ha restituito una
  massima pertinente sulla notifica PEC da indirizzo non presente nei pubblici
  registri.

Vince: `gestiolex-corpus`.

Ragione: Normattiva non contiene giurisprudenza. GestioLex e' nettamente
superiore per massime, principi e orientamenti.

### 6. Versioni storiche

Esempi:

- [art. 42 l.fall. ante 15/07/2022](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-01-16;267:1~art42!vig=2022-07-14)
- [art. 18 L. 300/1970 ante Jobs Act](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1970-05-20;300~art18!vig=2015-03-06)
- [art. 80 D.Lgs. 50/2016](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2016-04-18;50~art80!vig=2023-06-30)

Vince: `normattiva`.

Ragione: la multivigenza `!vig=` e' decisiva per il contenzioso su fatti
passati, procedure fallimentari ante Codice della crisi, appalti ante nuovo
codice e norme riformate.

### 7. Richieste miste norma + giurisprudenza

Esempio:

`Trova norme e massime utili su licenziamento giusta causa social network`.

Vince: `gestiolex-corpus`.

Ragione: e' l'unica delle due skill che puo' coprire anche la parte
giurisprudenziale. Tuttavia, in un output finale la parte normativa dovrebbe poi
essere linkata con `normattiva`.

## Pro e contro

### Normattiva - pro

- Produce link normativi precisi e citabili.
- E' deterministica su riferimenti noti.
- E' ottima per atti, pareri, contratti e memorie.
- Gestisce versioni storiche con `!vig=`.
- Ha basso consumo token.
- Riduce il rischio di citazioni nude o non verificabili.

### Normattiva - contro

- Non fa vera ricerca.
- Non trova massime.
- Non sintetizza orientamenti.
- Non risolve bene richieste come "trova la norma su...".
- Dipende dalla capacita' dell'agente di conoscere gia' tipo, data e numero
  dell'atto se la norma non e' nella lookup.

### GestioLex - pro

- Cerca norme per concetto.
- Recupera testo articolo per i codici supportati.
- Cerca giurisprudenza e massime.
- E' piu' adatta alla fase iniziale di studio della questione.
- Gestisce query formulate in linguaggio naturale meglio di Normattiva.

### GestioLex - contro

- Ranking normativo non sempre stabile.
- Alcuni mapping di atti speciali o storici non sono coperti da `leggi_articolo`.
- Non e' pensata per generare link URN-NIR perfetti.
- Non gestisce la multivigenza con la precisione di Normattiva.
- Puo' produrre risultati parziali, rumorosi o timeout.

## Qual e' la migliore?

Se devo sceglierne una sola per "fare ricerca legale", sceglierei
`gestiolex-corpus`.

Motivo: copre piu' bisogni sostanziali dell'avvocato. Sa cercare norme per
argomento, recuperare testo e trovare massime. Nel benchmark vince 110 casi su
200, soprattutto per ricerca esplorativa e giurisprudenza.

Se devo sceglierne una sola per "scrivere un atto con citazioni normative
corrette", sceglierei `normattiva`.

Motivo: e' piu' affidabile per link, multivigenza e citazioni formali. In un atto
giudiziario e' pericoloso lasciare riferimenti normativi nudi o link costruiti
male.

La soluzione migliore non e' scegliere una sola skill, ma usare un workflow a due
passaggi:

1. `gestiolex-corpus` per trovare norma, testo, massime e orientamento.
2. `normattiva` per trasformare i riferimenti normativi finali in link ufficiali
   e, quando serve, storicizzati.

## Raccomandazione operativa

Per uso professionale forense:

- ricerca iniziale: `gestiolex-corpus`;
- verifica articolo esatto su codici principali: `gestiolex-corpus` oppure
  `normattiva`, a seconda che serva testo o link;
- link finale in atto/parere: `normattiva`;
- versioni storiche: `normattiva`;
- giurisprudenza: `gestiolex-corpus`;
- atti speciali noti: `normattiva`;
- ricerche esplorative normative: `gestiolex-corpus`, ma con controllo critico
  dei risultati.

## Artefatti

- Casi completi: `outputs/normattiva_vs_gestiolex_200_cases.csv`
- Sintesi JSON: `outputs/normattiva_vs_gestiolex_200_summary.json`
- Script benchmark: `work/compare_normattiva_gestiolex.py`
