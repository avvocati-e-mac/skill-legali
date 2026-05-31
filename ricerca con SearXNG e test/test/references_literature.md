# Bibliografia — fondamento metodologico della valutazione

Riferimenti usati per progettare la rubrica v2 (`rubric.md`) e il report di confronto.
Ogni scelta di metodo è ancorata a uno di questi.

## Valutazione delle fonti

- **CRAAP test** — Blakeslee, S. & librarians, California State University Chico (2004).
  Currency, Relevance, Authority, Accuracy, Purpose. Include corroborazione/triangolazione.
  - https://www.scribbr.com/working-with-sources/craap-test/
  - https://library.csuchico.edu/help/source-or-information-good (origine)
  - Implicazione per noi: **Currency (attualità) e Authority (provenienza) sono assi distinti** →
    non premiare "ufficiale" come proxy di "buono"; valutare se la fonte è attuale e se supporta
    l'affermazione.

## Corroborazione tra fonti & dipendenza (la proposta dell'utente)

- **Dong, X. L., Berti-Équille, L., Srivastava, D.** — "Truth Discovery and Copying Detection
  in a Dynamic World", VLDB 2009. http://www.vldb.org/pvldb/vol2/vldb09-335.pdf
- **Dong, Berti-Équille, Srivastava** — "Integrating Conflicting Data: The Role of Source
  Dependence", PVLDB 2009. https://lunadong.com/publication/dependence_vldb.pdf
- **Li et al.** — "A Survey on Truth Discovery", arXiv:1505.02463.
  https://arxiv.org/pdf/1505.02463
  - Implicazioni per noi:
    - La corroborazione funziona **solo tra fonti indipendenti**; le fonti che si copiano
      (circular reporting) propagano il falso → N copie ≠ N conferme.
    - **Majority voting da solo → errore fino al ~30%** dei casi → la "fonte minoritaria
      corretta" è reale: la maggioranza non è prova di verità.
    - Soluzione del campo: pesare l'affidabilità/indipendenza, non contare le fonti.

## Scala di punteggio (boolean vs Likert)

- **Reference-Guided Verdict: LLMs-as-Judges in Automatic Evaluation of Free-Form QA**,
  arXiv:2408.09235. https://arxiv.org/pdf/2408.09235
- Rubric frameworks (CourseEvalAI, MDPI 2025): rubriche guidate → maggiore consistenza.
  https://www.mdpi.com/2073-431X/14/10/431
  - Implicazione: **check booleani precisi ("fatto presente? sì/no") danno inter-rater
    agreement più alto** delle scale 1–10 soggettive → la rubrica v2 usa conteggi booleani.

## Affidabilità tra giudici (statistica)

- **Krippendorff's α** — gestisce ≥3 giudici, dati ordinali/nominali, dati mancanti; si riduce
  ad altri coefficienti nei casi speciali. Soglia di accordo soddisfacente **α ≥ 0.80**.
  - https://en.wikipedia.org/wiki/Inter-rater_reliability
  - https://www.k-alpha.org/methodological-notes
  - Cohen's κ è limitato a **2** raters nominali → non adatto ai nostri 3 giudici.
  - Implicazione: riportiamo **α per metrica**, non lo scarto grezzo ad hoc.

## LLM-as-a-judge — buone pratiche e cautele

- "A Practical Guide for Evaluating LLMs and LLM-Reliant Systems", arXiv:2506.13023.
  https://arxiv.org/html/2506.13023v1
  - Cautele recepite: giudizio **cieco** (no provenienza), **ordine randomizzato**
    (position-bias), **rubrica esplicita**, più giudici + statistica di accordo. Limite noto:
    giudici dello stesso modello → errori potenzialmente **correlati**.

---

# Aggiunte per il confronto SearXNG-skill vs Perplexity (2026-05-30)

## Verifiability / citation faithfulness nei generative search (il motivo per cui Perplexity NON è gold standard)

- **Liu, N.F., Zhan, E., Liang, P.** — "Evaluating Verifiability in Generative Search Engines",
  **NeurIPS 2023 (Datasets & Benchmarks)**. https://arxiv.org/abs/2304.09848
  - Misurando *Perplexity* e New Bing: solo **~51.5%** delle frasi è pienamente supportato dalle
    citazioni; solo **~74.5%** delle citazioni supporta davvero la frase.
  - **Implicazione per noi**: trattare la risposta Perplexity come ground truth importa quel rumore
    nel metro → Perplexity resta **comparando + sorgente di euristiche**, mai gold standard. La
    verifiability va **misurata** (claim→citazione supporta sì/no), non assunta. Vedi [[blind_pplx/evaluation]] Q5.
- **Gao, T., Yen, H., Yu, J., Chen, D.** — "ALCE: Enabling LLMs to Generate Text with Citations", 2023.
  https://arxiv.org/abs/2305.14627 — benchmark per la citation faithfulness (supporting vs non-supporting).
- **AIS — "Attributable to Identified Sources"**, Rashkin et al., Google Research, 2022.
  https://arxiv.org/abs/2112.12870 — framework formale per "la fonte supporta il claim".
  - Implicazione: definiamo Q5 (citation-precision) su questa nozione di *attribuzione*.

## Metriche di ranking (layer-retrieval, two-layer eval)

- **Järvelin, K. & Kekäläinen, J.** — "Cumulated Gain-based Evaluation of IR Techniques",
  ACM TOIS 2002 — canonico per **DCG/nDCG** con rilevanza graduata. Usato in `retrieval_eval.md`/`compute_ndcg.py`.
- **Pooling stile TREC** — unione top-K dei sistemi, si valutano solo i documenti del pool quando i
  giudizi di rilevanza non sono esaustivi (Manning, Raghavan, Schütze, *Intro to IR*, 2008, cap. Evaluation).
- **RAGAS** (Es et al., 2023, https://arxiv.org/abs/2309.15217) e **Thakur et al., "Evaluating Retrieval
  Quality in RAG", 2024** — raccomandano di valutare **retrieval separato dalla generazione** (two-layer).
  - Implicazione: separiamo `retrieval_eval.md` (nDCG/recall) da `blind_pplx/evaluation.md` (qualità risposta).

## Bias del giudice LLM — mitigazioni applicate

- **Verbosity/length bias**: Dubois et al. (AlpacaFarm/length-controlled, 2024) — i giudici sovra-premiano
  risposte lunghe. **Mitigazione**: lunghezza **esclusa** dai criteri di qualità; efficienza-token in
  classifica separata (`token_efficiency_pplx.md`).
- **Position bias**: Wang et al. (2024) — calibrazione via **swap-and-average** dell'ordine. Applicato in `blind_pplx/_KEY.md`.
- **Self-preference bias**: Survey "LLM-as-a-Judge" (Li/Fu et al., 2024) — giudice e generatore stesso
  modello → bias correlato. **Dichiarato** come limite residuo; dove possibile si usa controllo booleano
  verificabile sui file (non opinione).
