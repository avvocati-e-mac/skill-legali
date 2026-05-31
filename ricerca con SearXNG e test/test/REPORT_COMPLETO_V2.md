# Report completo V2 — SearXNG-skill (v4) vs Perplexity Pro, con validazione multi-giudice

**Data**: 2026-05-30 · **Skill**: v4 · **Comparando**: Perplexity Pro (`pwm` v0.12.1)
**Giudici**: 5 rater (Claude + GPT-5.4 + Gemini 3.1 Pro + Kimi K2.6 + Nemotron 3 Super) · **Budget**: ~35 Pro Search

> **Cosa cambia rispetto a V1**: V1 aveva un solo giudice (Claude) → il red teaming l'aveva marcato come difetto
> più grave (RT2). V2 aggiunge **4 giudici esterni di famiglie diverse** sulle 5 query contestabili, con Krippendorff
> α per criterio. Risultato: **RT2 chiuso**, **un errore di V1 corretto** (N03), fiducia sui criteri **calibrata**.
> Fonti: `multijudge/RESULT.md`, `multijudge/compute_alpha.py`, `multijudge/raw/`, + tutti gli artefatti V1.

---

## 1. Perché (invariato da V1)
Ottimizzare la skill usando Perplexity Pro come specchio: estrarre euristiche, capire se è gold standard, confronto
competitivo. Vincolo: nessuna dipendenza runtime da Perplexity → euristiche statiche nella skill.

## 2. Metodo (V2 = V1 + multi-giudice)
- Two-layer: retrieval (nDCG@10, pool TREC) + generazione (booleani Q1–Q6), bias-mitigato (cieco, swap, no-verbosity).
- **Novità V2**: generazione rivalutata da **5 rater**. I 4 esterni via `pwm council --no-synthesis -s none` (isolati
  dalla ricerca web → giudicano solo i testi + fact-key forniti). Prompt anonimi A/B (cecità verificata via grep).
- Perplexity NON gold standard (Liu et al. NeurIPS 2023, ~51% claim supportati) — confermato e ora **misurato**: il
  criterio "le citazioni supportano il claim" (Q5) ha α=0.323 tra 5 giudici → è davvero il punto debole strutturale.

## 3. Risultati

### 3.1 Ranking fonti — PAREGGIO ROBUSTO (invariato)
nDCG@10 medio **0.732 (SearXNG) = 0.732 (Perplexity)**, robusto a perturbazione label ±1 (sensitivity analysis:
delta −0.001, sd 0.039). SearXNG vince cucina/news IT; Perplexity vince informatica (docs ufficiali) → euristica E5.

### 3.2 Qualità della risposta — RIVISTO da 5 giudici
**V1 diceva 95%=95% (single-rater Claude). V2 lo corregge:**

Krippendorff α per criterio (5 rater):
| Criterio | α | Affidabilità |
|---|---|---|
| Q2 lingua, Q4 recency | 1.000 | oggettivi — la valutazione regge |
| Q1 corretto | 0.564 | moderata |
| Q3 fonte autorevole | 0.562 | moderata |
| Q5 citation-precision | 0.323 | **bassa — trattare con cautela** |

Ricalcolo a **maggioranza 5-rater** sulle 5 query contestabili (`RESULT.md §4`):
- **N02** (carbonara): SearXNG vince — Perplexity Q3 fonte-autorevole = false (4/5: social/video, non procedura ufficiale).
- **N03** (Opus vs GPT): **SearXNG vince — Perplexity Q1 = false (4/5)**: dà un quadro **datato** (Opus 4.7 vs GPT-5.5,
  fonti 2025) con conclusione invertita rispetto ai dati 2026 (Opus 4.8 in testa su HLE). **V1 (Claude) l'aveva dato corretto.**
- **N01** (dottrina): Perplexity vince — SearXNG Q3 = false (3/5): fonte ufficiale non letta (PDF/paywall → difetto noto, E3).
- **T11, N04**: pari (accordo unanime).

**Esito V2**: sulle query *soggettive* il pareggio si **incrina leggermente a favore di SearXNG** (vince N02, N03;
perde N01), perché Perplexity paga fonti social (N02) e datate (N03) che il giudice singolo-Claude aveva sottovalutato.

### 3.3 Il reperto che giustifica l'intera attività: self-preference di Claude (N03)
4 giudici esterni su 4 (OpenAI, Google, Moonshot, NVIDIA — famiglie decorrelate) concordano che la risposta
Perplexity su N03 è **errata** (datata); io (Claude) l'avevo giudicata corretta. È un **self-preference/leniency
bias** misurabile, esattamente ciò che RT2 prevedeva in astratto e che ora è documentato su un caso concreto.
**Senza i 4 giudici esterni non l'avrei colto.**

### 3.4 Failure, efficienza-token, gold-standard (invariati da V1, vedi REPORT_COMPLETO.md)
Failure: entrambi onesti, SearXNG più sobrio. Efficienza: vantaggio SearXNG per uso agentico. Gold-standard: NO.

## 4. Skill v4 — 6 euristiche (invariate, vedi `references/search_strategy.md`)
E1 offset chrome · E2 istituzionali→fonte secondaria · E3 PDF/paywall→snippet · E4 section keyword-parziale ·
E5 boost docs ufficiali · E6 re-rank autorevolezza. La validazione N01 a 5 giudici **conferma E3** (la fonte
ufficiale non letta è penalizzata da 3/5 giudici → leggere meglio le fonti istituzionali ha valore reale).

## 5. Stato red teaming (dettaglio in RED_TEAM_V2.md)
| ID | Difetto | V1 | V2 |
|---|---|---|---|
| RT1 | delta E5 su pool diversi | 🔴 | corretto |
| **RT2** | **1 giudice solo** | 🔴 aperto | ✅ **CHIUSO** (5 rater + α) |
| RT3 | circolarità label | 🟡 | mitigato (sensitivity) |
| RT4 | "pplx non confabula" netto | 🟡 | corretto |
| RT5 | 12 query, 0 ripetizioni | 🟡 | aperto (α indicativo su poche unità) |
| RT6 | routing legale non testato | 🟡 | aperto |
| **RT9 (nuovo)** | **self-preference di Claude** | — | **scoperto e documentato** (N03) |
| **RT10 (nuovo)** | **Nemotron outlier sistematico** | — | segnalato (minoranza in 5/8 disaccordi) |

## 6. Verdetto finale
- **Il multi-giudice MIGLIORA il report**: chiude il difetto più grave, corregge un errore concreto, calibra la
  fiducia per criterio. Risposta diretta alla domanda dell'utente: **sì, e in modo non banale**.
- **La conclusione principale tiene e si rafforza**: la skill SearXNG v4 è **competitiva con Perplexity Pro**; sulle
  query soggettive, con 5 giudici, è **leggermente avanti** (penalizza meno le fonti social/datate). Il suo unico
  difetto residuo misurato (fonte ufficiale non letta, N01) è già indirizzato da E3.
- **Onestà**: 5 query = potenza statistica limitata (RT5); i giudici restano LLM; Nemotron è idiosincratico. I numeri
  di qualità V2 sono *più difendibili* di V1, non *definitivi*. Per chiudere RT5 servirebbero ripetizioni (A3).
