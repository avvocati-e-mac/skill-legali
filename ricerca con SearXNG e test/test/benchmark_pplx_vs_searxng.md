> ⚠️ **Aggiornato da V2**: questo report usava 1 solo giudice (Claude). La validazione multi-giudice (5 rater)
> in `REPORT_COMPLETO_V2.md` / `multijudge/RESULT.md` ha **corretto un risultato** (N03: Perplexity datato, 4/5
> giudici esterni lo bocciano, Claude no) e calibrato la fiducia per criterio (Q5 citation-precision α=0.323).
> Leggi `REPORT_COMPLETO_V2.md` per le conclusioni aggiornate.

# Benchmark — SearXNG-skill (v3) vs Perplexity Pro

Data: 2026-05-30 · Giudice: Claude (bias correlato dichiarato) · 12 query (7 storiche + 5 nuove)
Perplexity: Pro, `pwm` v0.12.1, ~15 Pro Search consumati (incl. 3 di ricerca letteratura).
Metodo two-layer (retrieval + generazione), cieco e bias-mitigato. Letteratura: `references_literature.md`.

Dati grezzi: `perplexity_raw/*.json`, `searxng_raw/*.md`. Calcoli: `compute_ndcg.py`, `retrieval_eval.md`,
`blind_pplx/evaluation.md`, `token_efficiency_pplx.md`.

---

## TL;DR

1. **Qualità: pareggio (95% = 95%)** su criteri booleani verificabili. Difetti speculari, non gerarchia.
2. **Ranking fonti: pari (nDCG 0.732 = 0.732)**, con profili opposti per dominio.
3. **Perplexity NON è gold standard** (Liu et al. 2023: ~51% frasi supportate dalle sue citazioni). È un
   **comparando affidabile** e una **sorgente di euristiche**.
4. **Ipotesi smentita**: Perplexity Pro **NON confabula** sui failure (T12, N05). Più robusto del WebSearch
   Claude testato nel benchmark precedente.
5. **6 euristiche azionabili** estratte, tutte **internalizzabili nella skill** senza dipendenza runtime da Perplexity.
6. **Efficienza-token**: vantaggio strutturale SearXNG-skill per uso agentico (output controllabile vs risposte pplx 6–9k chars).

---

## Risultati per layer

### Layer retrieval (nDCG@10, pool TREC) — dettaglio in `retrieval_eval.md`
| | media nDCG | vince dove |
|---|---|---|
| SearXNG-skill | **0.732** | cucina (T04 +0.14, N02 +0.12), news IT (T03 +0.19) |
| Perplexity | **0.732** | async Python (N04 +0.23: docs ufficiali > SEO-blog), dottrina (N01), fact (T01) |

### Layer generazione (% criteri booleani sì) — dettaglio in `blind_pplx/evaluation.md`
| | % sì | difetti |
|---|---|---|
| SearXNG-skill | **95%** | PDF/paywall non letti (N01), ranking grezzo con SEO-blog #1 (N04) |
| Perplexity | **95%** | citazioni social/video (N02), fonti datate (N03) |

### Citation-precision (Q5, replica ridotta Liu et al.)
Sul campione verificato, le citazioni Perplexity supportano i claim controllati. **Ma** il tasso strutturale di
non-supporto (~25–48%, Liu et al.) **impedisce** di promuoverlo a ground truth. → comparando, non oracolo.

---

## Le 6 euristiche da portare nella skill (v4)

| # | Euristica | Evidenza | Internalizzabile? |
|---|---|---|---|
| **E1** | `web_url_read paragraphRange:"1-N"` cade spesso nel **chrome/menu** su siti news/istituzionali. Partire con offset o saltare avanti se i primi paragrafi sono solo link. | T03 (cosmonet, cosimo 1-8 = chrome; 9-25 = contenuto), T11 (garante) | ✅ regola statica |
| **E2** | Siti **istituzionali a chrome pesante** (garanteprivacy) sono spesso inestraibili dal MCP → citarli come riferimento ma **leggere il contenuto da fonti secondarie strutturate** (iubenda, Altalex). | T11 | ✅ |
| **E3** | Per **legale-it/dottrina**, i PDF accademici **non sono parsati** dal MCP e le riviste sono a paywall → declassare PDF/paywall nella LETTURA, privilegiare snippet + fonti HTML aperte (Treccani, Diritto.it, Altalex). | N01 (PDF LUISS binario, rivista paywall) | ✅ |
| **E4** | `web_url_read section:` funziona meglio con **match PARZIALE** (keyword centrale dell'heading) che con la stringa completa. | N03 ("Hard reasoning" ok, "3. Hard reasoning: HLE" no), T04/N02 ("Come preparare") | ✅ |
| **E5** | Per **informatica**, **boost dei docs ufficiali** (docs.python.org, MDN, *.readthedocs.io) nel ranking di lettura, sopra blog/aggregatori, a prescindere dal relevance grezzo. | N04 (nDCG 0.572 vs 0.799: SearXNG aveva SEO-blog #1) | ✅ |
| **E6** | **Re-rank per autorevolezza di dominio** prima di scegliere l'URL da leggere, con ordine di preferenza per tipo-fonte e dominio. | N01, N04, T01 (pplx mette ufficiali in top-3) | ✅ tabella in `search_strategy.md` |

Tutte e 6 sono regole statiche → **nessuna dipendenza da Perplexity a runtime** (vincolo utente rispettato).

---

## Verdetto su "Perplexity gold standard?"

**NO come ground truth** — il tasso noto di citazioni non-supportanti (Liu et al. 2023, NeurIPS) e la verbosità
lo rendono inadatto a definire la verità. **SÌ come comparando + sorgente di euristiche** — il suo ranking
(equivalente in media) e la sua selezione fonti su informatica/dottrina hanno rivelato 6 miglioramenti concreti.

**Quando fidarsi di Perplexity come riferimento**: fact stabili, informatica (docs ufficiali), sintesi comparativa.
**Quando NON fidarsi**: cucina (social-heavy), recency critica (fonti talvolta datate), e ovunque serva verifica
puntuale delle citazioni.

## Dove ciascuno è preferibile (uso pratico)
- **SearXNG-skill**: cucina IT, news IT, privacy/air-gapped, uso agentico token-sensibile, failure dove "0 risultati" è informazione.
- **Perplexity**: sintesi comparative ricche, informatica con docs ufficiali, quando l'utente vuole un report lungo già pronto.

## Limiti residui (dichiarati)
- Giudice singolo = Claude (self-preference/bias correlato).
- Citation-precision verificata su campione, non esaustiva.
- Sessione singola, 12 query: indicativo, non potenza statistica per α inter-rater.
- Label di rilevanza retrieval assegnate dall'autore con regola esplicita (rischio circolarità mitigato dalla regola, non azzerato).
