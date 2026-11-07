# Deleghe a subagenti

## Quando conviene
- Più di 6-8 pronunce da leggere per intero: dividi per **gruppo tematico** (es. «direzione lavori e vizi progettuali», «solidarietà e decadenza»), così ogni subagente legge pronunce collegate e coglie i passi contrari.
- Non delegare compiti da una sola chiamata, la verifica delle norme (poche consultazioni e quote strette), né gli strumenti con **browser o sessione condivisi**: vanno usati da un solo agente alla volta, di solito la sessione principale.
- Scegli il modello più economico capace del compito:
  - estrazione o esistenza di estremi: modello piccolo;
  - lettura e sintesi giuridica di una pronuncia: modello medio;
  - verdetti finali e report: sessione principale.

## Prompt-modello (da adattare)

```
Sei un assistente di verifica giurisprudenziale. Strumenti: <strumento e come caricarlo>.

VINCOLI
- Lavora solo in <cartella scratchpad>; non scrivere altrove.
- Nelle query non inserire nomi di parti o persone; non caricare testi del fascicolo.
- Cita ogni fonte con gli estremi: sezione, tipo, numero, data di deposito, ECLI/Rv, URL.
- Riassunti automatici e "sintesi" non valgono come prova: conta solo il testo.
- Se non trovi qualcosa scrivi "non trovato nel testo letto" o "non verificato", mai "non esiste".

METODO
1. Recupera il testo integrale di ogni pronuncia e salvalo in <scratchpad>/<numero>_<anno>.txt.
2. Per ogni frase: python3 <skill>/scripts/confronta_verbatim.py --fonte <file> --citazione "<frase>".
3. Leggi il contesto: ratio, inciso, motivazione riferita, esito del motivo, dispositivo.

PRONUNCE E FRASI
<ID> — <estremi come nell'atto> — frasi: «…» — principio per cui è citata: …

FORMATO DI RITORNO, per ogni ID
- Estremi verificati
- Per ogni frase: esito dello script + 2-3 righe di contesto letterale
- Natura del passo ed esito del motivo
- Passi CONTRARI alla tesi per cui è citata (letterali)
- Testo integrale letto: sì/no
```

## Controllo
Il rapporto del subagente è una **fonte secondaria**. Prima di scrivere il report:
- rileggi di persona ogni verbatim che entrerà nel report (decisivo, contrario o proposto in sostituzione);
- riesegui `confronta_verbatim.py` sui file salvati;
- nel registro annota `"letto_da": "subagente"` oppure `"io"`.
