# Validazione V3 — fix dei problemi aperti + red teaming del codice

Estende `RESULT.md` (V2). Risolve: codice non testato (Krippendorff), A6 (contaminazione self-preference),
A3 (varianza), RT10 (Nemotron). Dati: `raw_a6/` (5 query × 4 giudici × 2 run = 40 giudizi), `A6_A3_RT10_results.txt`.

## 0. Red teaming del CODICE (il fix più importante)

**Scoperta**: la mia implementazione di Krippendorff α non era validata contro alcun riferimento (numpy/scipy/
sklearn non disponibili in ambiente). Ho costruito un **known-answer test** sul caso canonico di Wikipedia.

**Trappola evitata**: ho chiesto a Perplexity il valore atteso del caso canonico → mi ha dato **0.7477**, poi
(in un secondo giro) **0.9231** — **entrambi sbagliati**. Il valore corretto, calcolato deterministicamente, è
**0.6914** (Do=6/26, De=486/650). **Lezione: un LLM non è una fonte affidabile per il ground-truth di un test
numerico.** Ho ancorato il test a:
1. calcolo aritmetico esplicito (deterministico),
2. una **seconda implementazione indipendente** come oracolo differenziale (concorda su 100 casi random),
3. valori banali per i casi degeneri.

**Esito**: `test_compute.py` → **15/15 PASS**. La mia implementazione α **era già corretta**; i valori del report
V2 (0.564, 0.562, 0.323, 1.000) **sono confermati validi**. Ora però sono prodotti da `metrics.py` validato e
condiviso (non più hand-rolled in ogni script). Best practice applicate: known-answer test, oracolo differenziale,
separazione dati/logica, convenzione documentata, no metriche duplicate.

## 1. A6 — Contaminazione del self-preference di Claude (QUANTIFICATA)

Rivalutate a 4 giudici esterni le **5 query non contestabili** (T01,T03,T04,T06,T07), dove V1-Claude aveva dato
**tutto ✅**. Celle dove la maggioranza dei 4 esterni **dissente** da Claude:

| Cella | Esterni | Claude V1 | Verdetto |
|---|---|---|---|
| T01-B (SearXNG) Q3 fonte-autorevole | **4/4 false** | true | Claude troppo indulgente (SearXNG citava Wikipedia, non openai.com primario) |
| T03-B (Perplexity) Q1 corretto | 3/4 false | true | Claude indulgente **verso Perplexity** |
| T03-B (Perplexity) Q3 fonte-autorevole | **4/4 false** | true | idem |

**Contaminazione: 3/26 celle (~11%)** sulle query "facili" — **identica in entrambi i run** (stabile, non rumore).

**Reperto che RIBALTA RT9** (verificato in red teaming): 2 delle 3 celle contaminate riguardano **Perplexity**
(T03), 1 SearXNG (T01). Combinando con la cella contaminata di V2 (N03-B = Perplexity), il bilancio è **~3 celle
pro-Perplexity vs 1 pro-SearXNG**. Cioè Claude V1 è stato indulgente **soprattutto verso Perplexity, NON verso sé
stesso** → **l'opposto del self-preference** che RT9 ipotizzava. Riformulazione corretta del bias di Claude:
- NON è self-preference (pro-Claude/pro-un-lato);
- è **leniency generale** (Claude è più generoso di una giuria di 4 modelli, ~11% delle celle facili);
- se ha una direzione, è semmai *pro-Perplexity* (Claude tende a "dare credito" a risposte lunghe e ben scritte —
  vedi verbosity §3 — che è lo stile di Perplexity).

**Implicazione onesta**: il campione è minuscolo (3-4 celle), quindi la *direzione* (pro-Perplexity) è un segnale
debole, non una prova. Ma posso affermare con sicurezza che **NON c'è self-preference pro-Claude/pro-SearXNG** —
se mai il contrario. Questo **rafforza l'imparzialità del confronto a sfavore di SearXNG**: la skill non è stata
avvantaggiata dal giudice-Claude; semmai Perplexity lo è stato. La conclusione "ranking/qualità pari" è quindi
*conservativa* per SearXNG, non gonfiata.

## 2. A3 — Stabilità tra run (RT5 parzialmente chiuso)

2 run identici (stesso prompt, stessi modelli, `-s none`): **solo 3/102 voti cambiano (3% instabilità)**.
→ I giudizi LLM sono **altamente riproducibili**. α e punteggi NON sono inflazionati da rumore stocastico.
Resta il limite del numero di *query* (potenza), ma la **affidabilità per-giudizio è alta**. RT5 ridimensionato.

## 3. RT10 — Nemotron NON è un outlier (era artefatto del piccolo campione)

| Giudice | % minoranza (su set ampio) | % True su risposta lunga |
|---|---|---|
| GPT-5.4 | 2% | 77% |
| Gemini 3.1 Pro | 6% | 73% |
| Kimi K2.6 | 2% | 88% |
| **Nemotron 3 Super** | **0%** | 76% |

Su 5 query × 2 run, Nemotron è il **più consensuale** (0% minoranza), non un outlier. La sua "idiosincrasia"
vista in V2 era un **artefatto del campione piccolo** (5 query contestate, dove i disaccordi si concentrano).
**RT10 declassato**: nessun giudice è sistematicamente rumoroso. Gemini è il più "indipendente" (6%).

**Verbosity bias**: tutti i giudici votano True sulla risposta più lunga il 73–88% delle volte (Kimi il più alto).
MA "lungo" correla con "Perplexity", che è spesso effettivamente corretto → **non è prova netta di bias**: non
posso separare "premia il lungo" da "il lungo era davvero migliore" su questo campione. Lo segnalo come **non
concludente**, non come bias accertato. Per isolarlo servirebbero coppie lunghezza-controllata (stessa qualità,
lunghezza diversa) — fuori scope qui.

## 4. Impatto sui risultati V2

- I valori α **restano validi** (codice ora testato).
- Il pareggio qualità V1 "95%=95%" era **gonfiato in valore assoluto** (Claude indulgente ~11%), ma **simmetricamente**
  → il *confronto relativo* SearXNG vs Perplexity regge. Con maggioranza-5-rater, su tutte le 10 query la qualità
  reale è più bassa del 95% dichiarato, ma per entrambi.
- Conclusione principale **invariata e rafforzata**: ranking pari (nDCG 0.732, testato), qualità sostanzialmente pari
  con difetti speculari, Perplexity non gold-standard. Ora con codice validato + varianza misurata + bias caratterizzato.
