# Validazione multi-giudice (5 rater) — risultato

**Domanda dell'utente**: usare GPT/Gemini/Kimi/Nemotron come giudici migliora i risultati/il report?
**Risposta breve: SÌ, in modo sostanziale.** Ha (a) chiuso RT2, (b) **smascherato un self-preference bias di
Claude** che aveva alterato una conclusione, (c) quantificato quali criteri sono affidabili e quali no.

Setup: 5 query contestabili (T11, N01, N02, N03, N04) × 4 giudici esterni via `pwm council --no-synthesis
-s none` + Claude = **5 rater**. 20 Pro Search. 0 parse-fail. Cieco (prompt senza marker del metodo). Dati:
`raw/*.json`, calcolo: `compute_alpha.py`.

## 1. Inter-rater agreement (Krippendorff α, binario)

| Criterio | α | % accordo pieno | Lettura |
|---|---|---|---|
| Q2 lingua adeguata | **1.000** | 100% | oggettivo — accordo perfetto, soglia 0.80 superata |
| Q4 attuale (recency) | **1.000** | 100% | oggettivo |
| Q1 corretto | 0.564 | 80% | moderato — sotto 0.80, c'è soggettività residua |
| Q3 fonte autorevole | 0.562 | 60% | moderato — "cosa è autorevole" divide i giudici |
| Q5 citation-precision | **0.323** | 75% | **basso** — giudicare se una citazione *supporta* il claim è intrinsecamente difficile |

**Interpretazione α**: i criteri *verificabili sui file* (lingua, recency) hanno α=1.0 → robusti, la valutazione
single-rater di Claude su questi era già affidabile. I criteri *di giudizio* (Q1, Q3, soprattutto **Q5**) hanno
α basso → **NON erano affidabili a giudice singolo**. Q5 a 0.323 conferma empiricamente l'avvertimento di Liu
et al. 2023: la citation-precision è il criterio meno consensuale e va trattato con cautela, **non** come misura
secca. Questo è un guadagno netto di consapevolezza che il report v1 (single-rater) non poteva avere.

> Nota statistica: 5 query → poche unità per criterio (8–10). α è **indicativo**, non potenza forte (RT5 resta).

## 2. Il reperto chiave: self-preference di Claude smascherato (N03)

Su **N03 (Opus vs GPT reasoning), risposta Perplexity, Q1_corretto**:
- **Claude (io)**: corretto ✅
- **GPT-5.4, Gemini 3.1 Pro, Kimi K2.6, Nemotron**: **NON corretto ❌ (4 su 4 esterni concordi)**

Perché i 4 esterni hanno ragione: la risposta Perplexity afferma "GPT-5.x ha vantaggio netto sul reasoning" e si
ferma al confronto **Opus 4.7 vs GPT-5.5** con fonti **2025** (llmbase, braintrust, spectrumailab). La fact-key
(dati System Card maggio 2026) dice che **Opus 4.8 guida su HLE** — la risposta Perplexity dà un quadro **datato
e con la conclusione invertita** rispetto allo stato attuale. I 4 modelli esterni l'hanno colto; io ero stato
indulgente, plausibilmente per una narrazione interna "GPT forte su math / Claude su dialogo" non più vera nel 2026.

**Conseguenza sul punteggio**: con la regola di maggioranza (5 rater), N03-Perplexity-Q1 passa da ✅ a ❌. Questo
**rompe il pareggio "95%=95%"** del report v1 a sfavore di Perplexity su questa cella → vedi §4.

## 3. Outlier sistematico: Nemotron

Nemotron 3 Super è in minoranza in **5 degli 8 disaccordi** (T11-B-Q1, N01-A-Q5, N02-A-Q3, N03-A-Q3, e concorda
con la minoranza in N03-B-Q5). Tende a essere più severo/idiosincratico. Per la regola dell'utente ("dove il
booleano è verificabile, scarta l'outlier"): sui criteri oggettivi il suo voto discorde va scartato; sui criteri
di giudizio va riportato ma pesato. Non lo elimino dai dati — lo segnalo, come impone l'onestà metodologica.

## 4. Il pareggio regge? — ricalcolo a maggioranza 5-rater

Applicando la **maggioranza dei 5 rater** (con scarto outlier sui criteri verificabili):
- **T11**: entrambi tutto vero tranne Nemotron su B-Q1 (minoranza 1/5 → B resta corretto). **Pari.**
- **N01**: A (SearXNG) Q3 fonte-autorevole = maggioranza **false** (3/5: Claude, GPT, Nemotron) → SearXNG perde
  qui (fonte ufficiale non letta, PDF/paywall — coerente con E3). B (Perplexity) Q3 = **true** (4/5). **Punto a Perplexity.**
- **N02**: A (Perplexity) Q3 = **false** (4/5, social-heavy); B (SearXNG) Q3 = **true** (unanime). **Punto a SearXNG.**
- **N03**: B (Perplexity) Q1 = **false** (4/5) → **Perplexity perde** sul contenuto datato. A (SearXNG) tutto vero. **Punto a SearXNG.**
- **N04**: entrambi tutto vero (unanime). **Pari.**

**Esito**: il pareggio globale **si incrina leggermente a favore di SearXNG** sulle query contestabili:
SearXNG vince nettamente N02 e N03, perde N01 (fonte ufficiale non letta — difetto noto, correggibile con E3).
Non è più "95%=95%" secco: con 5 giudici, **su questi 5 casi soggettivi SearXNG è leggermente avanti**, soprattutto
perché Perplexity paga le fonti social (N02) e datate (N03), che un giudice singolo-Claude aveva sottovalutato.

## 5. Verdetto: il multi-giudice migliora il report?

**SÌ, nettamente:**
1. **Chiude RT2** (il difetto più grave): i punteggi non sono più single-rater; abbiamo α per criterio.
2. **Corregge un errore reale** (N03): il self-preference di Claude aveva mascherato che Perplexity dà una
   risposta datata sul confronto AI. Senza i 4 esterni non l'avrei colto. Questo da solo giustifica l'attività.
3. **Calibra la fiducia**: ora sappiamo che Q5 (citation-precision) è poco affidabile (α 0.323) e Q1/Q3 moderati,
   mentre lingua/recency sono oggettivi (α 1.0). Il report v2 può pesare i criteri di conseguenza.
4. **Decorrelazione**: i 4 giudici sono di famiglie diverse (OpenAI, Google, Moonshot, NVIDIA) → bias non correlato
   con Claude. La convergenza 4/4 contro Claude su N03 è un segnale forte, non rumore.

**Limiti residui** (onesti): 5 query = α indicativo (RT5 aperto); i giudici restano LLM (bias comuni possibili, ma
decorrelati); Nemotron outlier; `-s none` significa che i giudici non verificano fatti nuovi (mitigato da fact-key).
