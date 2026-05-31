# Report completo — Ottimizzazione skill ricerca-web-searXNG via confronto con Perplexity Pro

**Data**: 2026-05-30 · **Skill**: `ricerca-web-searXNG` v3 → **v4** · **Giudice**: Claude (single-rater, dichiarato)
**Comparando**: Perplexity Pro (`pwm` v0.12.1) · **Budget**: ~15 Pro Search (quota 108→96, 0 Deep Research)

> Questo report consolida: `benchmark_pplx_vs_searxng.md` (sintesi), `retrieval_eval.md` + `compute_ndcg.py`
> (ranking), `blind_pplx/evaluation.md` (qualità cieca), `token_efficiency_pplx.md`, `sensitivity_analysis.md`,
> `RED_TEAM.md` (autocritica), `references_literature.md` (fondamento). Dati grezzi: `perplexity_raw/`, `searxng_raw/`.

---

## 1. Perché questo lavoro

La skill cerca sul web via MCP SearXNG con progressive disclosure e routing legale. Perplexity Pro ha un
algoritmo di ricerca/ranking già ottimizzato: l'idea era usarlo come **specchio** per (a) estrarre euristiche
da portare nella skill, (b) capire se può fungere da gold standard, (c) confronto competitivo. Vincolo:
l'accesso a Perplexity potrebbe sparire → ogni euristica adottata dev'essere **statica nella skill**, mai una
dipendenza runtime.

## 2. Come è stato fatto (metodo)

- **12 query** = 7 storiche (continuità col benchmark a 4 modalità) + 5 nuove sui domini-skill (`test_cases_pplx.md`).
- **Two-layer** (RAGAS/Thakur): retrieval (fonti) valutato separatamente dalla generazione (risposta).
  - Retrieval: pool stile TREC, label rilevanza 0–3 con regola esplicita, **nDCG@10** (Järvelin-Kekäläinen 2002).
  - Generazione: booleani verificabili (corretto / lingua / fonte ufficiale / attuale / citation-precision / failure onesto).
- **Bias-mitigato**: cieco con chiave sigillata (`blind_pplx/_KEY.md`), ordine swap-and-average (position bias),
  **lunghezza esclusa** dalla qualità (verbosity bias → efficienza in classifica separata).
- **Perplexity NON gold standard**: deciso a priori sulla base di Liu et al. NeurIPS 2023 (solo ~51% delle frasi
  dei generative search è pienamente supportato dalle citazioni). Usato come comparando + sorgente di euristiche.

## 3. Risultati

### 3.1 Ranking delle fonti — PAREGGIO ROBUSTO
| | nDCG@10 medio | dove vince |
|---|---|---|
| SearXNG-skill | **0.732** | cucina IT (T04, N02: pplx usa social/video), news IT (T03) |
| Perplexity | **0.732** | informatica (N04: docs ufficiali > SEO-blog), dottrina (N01), fact (T01) |

**Robustezza**: perturbando le label ±1 su 300 trial, il delta resta media −0.001 (sd 0.039), pareggio nel 53%
dei casi (`sensitivity_analysis.md`). La conclusione "ranking equivalente" **non** è un artefatto delle mie label.

### 3.2 Qualità della risposta — pareggio (single-rater)
Booleani: **95% sì = 95% sì**. Difetti speculari:
- SearXNG: PDF/paywall non leggibili (N01), ranking grezzo con SEO-blog in cima (N04).
- Perplexity: citazioni social/video (N02), fonti datate (N03).
> ⚠️ Single-rater (vedi §5 RT2): indicativo, non robusto come i 3-giudici+α dello standard interno.

### 3.3 Failure (T12, N05) — sfumato
Entrambi *concludono* correttamente che la cosa non esiste. SearXNG: "0 risultati" (sobrio). Perplexity: non
confabula una risposta, **ma** cita fonti irrilevanti aggrappandosi ai frammenti (Marvel 2099, repo casuali).
SearXNG è più pulito su questo asse. (Ipotesi iniziale "pplx allucina" → corretta in "pplx è discorsivo ma onesto".)

### 3.4 Efficienza-token — vantaggio SearXNG per uso agentico
Risposte Perplexity 6–9k chars su deep/comparison; la skill mantiene il contesto ingerito ~3.2–4.9k con letture
mirate. Vantaggio *per agenti token-sensibili*, non in assoluto (vedi RT7).

### 3.5 Perplexity come gold standard? — NO
Tasso strutturale di citazioni non-supportanti (Liu et al.) + verbosità + fonti talvolta datate. **È un comparando
affidabile e una sorgente di euristiche, non un oracolo di verità.** Il gold standard resta una fact-key da fonti
indipendenti corroborate.

## 4. Cosa è cambiato nella skill (v4)

6 euristiche, tutte statiche (nessuna dipendenza da Perplexity a runtime). In `references/search_strategy.md` +
`SKILL.md` + `README.md`:

| # | Euristica | Origine empirica |
|---|---|---|
| E1 | offset `paragraphRange` quando la lettura cade nel chrome | T03, T11 (cosmonet/garante = menu) |
| E2 | istituzionali chrome-heavy → leggi da fonte secondaria | T11 (garanteprivacy inestraibile) |
| E3 | PDF/paywall non parsati → rispondi dagli snippet, max 2 tentativi | N01 (PDF LUISS binario) |
| E4 | `section` con **keyword centrale** (match parziale > esatto) | N03/T04/N02 |
| E5 | boost docs ufficiali per informatica | N04 (gap nDCG più ampio: 0.572 vs 0.799) |
| E6 | re-rank per autorevolezza prima di leggere (tabella per dominio) | N01, N04, T01 |

**E1–E4 sono fatti osservati direttamente sui tool** (riproducibili, non opinioni). E5–E6 derivano dal ranking.

## 5. Red teaming dell'attività (sintesi — dettaglio in `RED_TEAM.md`)

| ID | Difetto | Gravità | Stato |
|---|---|---|---|
| RT1 | "delta E5 +15% supera pplx" calcolato su pool diversi | 🔴 alta | **corretto** (numero rimosso) |
| RT2 | 1 giudice invece di 3 + Krippendorff α (viola standard utente) | 🔴 alta | aperto → azione A1 |
| RT3 | circolarità label di rilevanza | 🟡 media | mitigato (sensitivity analysis) |
| RT4 | "pplx non confabula" troppo netto | 🟡 media | **corretto** |
| RT5 | 12 query, 0 ripetizioni → niente varianza | 🟡 media | aperto → A3 |
| RT6 | routing legale (Normattiva/BuddaLaw), multi-dominio, URL-diretto NON testati | 🟡 media | aperto → A4 |
| RT7 | asimmetria di misura token (contesto vs output) | 🟢 bassa | dichiarato |
| RT8 | citation-precision su campione minuscolo | 🟢 bassa | dichiarato (poggia su letteratura) |

**Cosa regge**: il pareggio nDCG (sensitivity), le euristiche E1–E4 (fatti diretti), il no-gold-standard (letteratura).

## 6. Cosa resta da migliorare (oltre la skill: il METODO e la SKILL)

### Sul metodo di valutazione (per rendere i numeri difendibili)
- **A1 — Multi-giudice + α**: rieseguire i booleani contestabili con ≥2 rater aggiuntivi (anche non-Claude via
  `pwm ask -m gemini_pro`/`nemotron`) e riportare Krippendorff α. Chiude RT2, il difetto più grave.
- **A3 — Ripetizioni**: 3 run/query con media±sd (≈36 Pro Search, budget ok) per dare varianza ai confronti.
- **A5 — Secondo annotatore cieco** per le label nDCG (chiude la circolarità residua RT3).

### Sulla copertura del confronto
- **A4 — Domini non testati**: routing legale con Normattiva/BuddaLaw attivi (il pezzo più "intelligente" della
  skill, mai confrontato), query multi-dominio (S11), URL-diretto (S10), cucina EN reale, lingue terze.

### Sulla skill stessa (miglioramenti candidati emersi, NON ancora implementati)
- **M1 — Cache del re-rank di autorevolezza**: precompilare per dominio una whitelist di domini ufficiali
  (docs.python.org, developer.mozilla.org, garanteprivacy.it, gazzettaufficiale.it…) così E5/E6 sono deterministici.
- **M2 — Rilevamento automatico del chrome**: euristica per riconoscere "questo blocco è menu" (densità di link
  per riga) e saltare l'offset senza una seconda lettura → risparmio di 1 `web_url_read` su news/istituzionali.
- **M3 — Gestione PDF migliore**: valutare se il MCP `web_url_read` ha un parametro per estrazione testo PDF; se
  no, documentare il limite e suggerire fonti HTML alternative per dottrina (E3 già lo fa parzialmente).
- **M4 — `n_risultati` per news**: T03 ha mostrato che 7 fonti news IT sono abbondanti; valutare se 5 bastano
  (risparmio contesto) — richiede A3 per decidere con varianza, non a occhio.
- **M5 — Segnale di qualità della lettura**: la skill potrebbe emettere nell'header `[... · lettura: snippet-only]`
  quando ripiega sugli snippet (E3), per trasparenza all'utente su quanto è "profonda" la risposta.

### Onestà finale
Il risultato solido e difendibile è: **la skill v3 era già competitiva con un sistema commerciale ottimizzato
(Perplexity Pro) sul ranking, e v4 chiude il suo unico tallone misurato (fonti ufficiali sotto i SEO-blog).**
Tutto il resto (i punteggi di qualità) è single-rater e va consolidato con A1/A3 prima di trattarlo come definitivo.
