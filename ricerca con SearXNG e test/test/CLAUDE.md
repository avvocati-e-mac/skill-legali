# CLAUDE.md — Regole per sviluppare i test in questa cartella

> Guida operativa per chiunque (Claude incluso) aggiunga o modifichi test/benchmark qui.
> Scopo: **uniformità**. L'architettura è descritta in [ARCHITETTURA_TEST.md](ARCHITETTURA_TEST.md) —
> questo file dice *come lavorare*, non *com'è fatto*. Leggi prima l'architettura se non la conosci.
>
> Progressive disclosure: **Livello 0** = le 5 regole non negoziabili. **Livello 1** = workflow per
> task tipici. **Livello 2** = dettagli e trappole note.

---

## LIVELLO 0 — Le 5 regole non negoziabili

1. **Ogni numero o è ancorato a un paper, o è coperto da un test.** Nessun punteggio "a sensazione".
   La metrica statistica vive in `metrics.py`, validata da `test_compute.py`. Non reimplementarla altrove.

2. **Mai un LLM come ground-truth di un test numerico.** (Costato caro: Perplexity ha sbagliato il valore
   canonico di α *due volte*.) Il valore atteso viene da calcolo deterministico o da una seconda
   implementazione indipendente. Vedi `test_compute.py`.

3. **Separa dati e logica.** Il codice opera su dati passati/caricati; niente risultati hard-coded nella
   logica. Le metriche stanno in `metrics.py`; gli script le importano, non le copiano.

4. **Giudizio sempre cieco e bias-mitigato.** Prompt anonimi A/B senza marker del metodo (verifica dalla
   cartella `test/` con `grep -li "searxng\|perplexity" multijudge/prompts*/*.txt` → deve dare 0 risultati),
   chiave in `blind_pplx/_KEY.md`, ordine swap-and-average, lunghezza esclusa dai criteri di qualità.

5. **Red teaming prima di concludere.** Attacca i tuoi stessi numeri, classifica i difetti 🔴🟡🟢, distingui
   *fatti osservati sui tool* (robusti) da *punteggi di giudizio* (fragili). Aggiorna `RED_TEAM_V*.md`.

---

## LIVELLO 1 — Workflow per i task tipici

### Aggiungere una nuova metrica statistica
1. Scrivila in `metrics.py` (funzione pura, docstring con la convenzione e il riferimento).
2. Aggiungi in `test_compute.py`: un **known-answer test** (valore da calcolo/paper, NON da LLM) +
   edge case (vuoto, singola unità, accordo perfetto, disaccordo totale) + una **property** (es. bounded).
3. `python3 test_compute.py` → deve restare **verde** prima di usarla in un report.

### Aggiungere query o giudici al benchmark
1. Pre-registra query + ipotesi in `test_cases_pplx.md` *prima* di guardare i dati (anti-razionalizzazione).
2. Raccogli i dati grezzi nelle cartelle `*_raw/` (mai mescolati col codice).
3. Giudici via `pwm council "<prompt>" -m gpt54,gemini_pro,kimi_k26,nemotron --no-synthesis -s none --json`.
   Costo: 1 Pro Search/modello. **Su Pro NIENTE `gpt55`/`claude_opus`** (Max-only). Controlla `pwm usage` prima.
4. Prompt generati da uno script tipo `build_prompts*.py` (mappa A/B da `_KEY.md`), mai scritti a mano.

### Produrre un nuovo report
1. Calcola con gli script (che importano da `metrics.py`).
2. Red teaming → `RED_TEAM_V{n}.md`. 3. Report → `REPORT_COMPLETO_V{n}.md` + `multijudge/RESULT_V{n}.md`.
4. **Versiona, non sovrascrivere**: i report precedenti restano (la storia dei difetti è informazione).
5. Se un risultato ribalta una conclusione precedente, **dillo apertamente** nel nuovo report.

---

## LIVELLO 2 — Dettagli, convenzioni e trappole note

### Convenzioni (le stesse di ARCHITETTURA_TEST §4, qui in forma operativa)
- **Krippendorff α**: nominale/binaria; valore canonico di verifica **0.6914**. Unità con <2 rater escluse.
- **nDCG@k**: `DCG = Σ rel_i / log₂(i+2)`; rilevanza 0–3; pool = unione top-K dei due sistemi (stile TREC).
- **Etichette di rilevanza**: regola esplicita scritta *prima* (3=ufficiale/primaria … 0=irrilevante).
- **Isolamento giudici**: `-s none` → valutano solo i testi + fact-key, non cercano. La fact-key è
  indipendente, non derivata da un lato del confronto (trappola RT12: evita la circolarità).

### Trappole già pagate (non ripeterle)
- **α hand-rolled non testata** → ora in `metrics.py` + suite. Se la tocchi, ri-valida.
- **Ground-truth da LLM** → sbagliato. Usa calcolo deterministico.
- **Metriche duplicate** negli script → DRY: importa da `metrics.py`.
- **Bug negli script di analisi** (es. indice tupla con stringa) → esegui *sempre* lo script, non fidarti
  che "sembri giusto". Un known-answer/sanity check anche per gli script di analisi.
- **Test di verifica difettoso** → anche il comando con cui *controlli* può essere sbagliato. Caso reale:
  `python3 -c "import numpy" 2>&1 | head -1 | grep -q Error` dà falso "PRESENTE" perché `head -1` legge la
  riga `Traceback (most recent call last):` (che non contiene "Error"), non il `ModuleNotFoundError` finale.
  → per testare la presenza di un modulo usa l'**exit code diretto**: `python3 -c "import numpy" && … || …`,
  e **ripeti** prima di concludere (l'ambiente può sembrare incoerente). Vale anche per il red teaming di sé stessi.
- **Campione piccolo travestito da prova**: con poche query/celle, riporta i numeri come *indicativi* e
  misura la stabilità (ripetizioni, sensitivity) prima di affermare una direzione.

### Riproducibilità (deve sempre funzionare)
```bash
cd test/
python3 test_compute.py            # metriche valide → 15/15 OK
python3 compute_ndcg.py            # retrieval → nDCG 0.732 = 0.732
python3 multijudge/compute_alpha.py   # α per criterio
python3 multijudge/analyze_a6.py      # contaminazione, varianza, outlier
```

### Manutenzione
- Niente dipendenze esterne (numpy/scipy/sklearn assenti in ambiente): implementazioni a mano **ma testate**.
- I file `* copia.md` sono duplicati spuri (Finder): non sono artefatti, vanno rimossi.
- Questo file e `ARCHITETTURA_TEST.md` sono **vivi**: aggiornali quando cambiano metriche, criteri o convenzioni.

---

*Regola d'oro, ripetuta perché conta: ogni numero o è ancorato a un paper, o è coperto da un test.*
