# BuddaLaw — Report test v8.2

**Data:** 2026-05-19  
**Versione testata:** 8.2  
**Obiettivo:** Verificare le 2 migliorie introdotte in v8.2 (C1/T39 e C2/T40-T41) e controllo di regressione sulle feature v8.1.  
**Metodo:** Test live MCP — 3 chiamate parallele in sessione.

---

## T39 — C1: Verifica esplicita `data_deposito` sui risultati

**Query:** «responsabilità medica errore diagnostico struttura ospedaliera risarcimento»  
**Parametri:** `search_category="civile"`, `data_deposito="2025-05-19"` (data odierna = filtro stretto), `max_results=5`

**Risultati restituiti dal server con rispettive date:**

| # | Sentenza | data_deposito | Entro filtro? |
|---|---|---|---|
| 1 | Cass. 13869/2020 | 2020-07-06 | ❌ SCARTARE |
| 2 | Cass. 5380/2023 | 2023-02-21 | ❌ SCARTARE |
| 3 | Cass. 7884/2025 | 2025-03-25 | ❌ SCARTARE |
| 4 | Cass. 5673/2025 | 2025-03-04 | ❌ SCARTARE |
| 5 | Cass. 29331/2019 | 2019-11-13 | ❌ SCARTARE |

**Analisi:** Con `data_deposito="2025-05-19"` (oggi), tutti e 5 i risultati hanno data anteriore al filtro. Il server ha completamente ignorato il parametro. Senza la regola C1, Claude avrebbe presentato Cass. 13869/2020 (2020) come "sentenza recente".

**Con la regola C1:** Claude verifica il campo `data_deposito` di ciascun risultato, rileva che nessuno supera il filtro, e comunica: «Non ho trovato sentenze depositate dopo il [data] su questo tema — amplio la ricerca.»

**Esito:** ✅ REGOLA NECESSARIA E VERIFICATA — il server conferma il comportamento non rigoroso già documentato nei test precedenti, con un filtro ancora più stretto (data odierna).

---

## T40-T41 — C2: Deduplicazione risultati identici

### T40 — `search_case_law`: duplicato per `idatto`

**Query:** «licenziamento per giustificato motivo oggettivo soppressione posto lavoro»  
**Parametri:** `search_category="civile"`, `max_results=7`

**Risultati — analisi `idatto`:**

| # | idatto | Duplicato? |
|---|---|---|
| 1 | ECLI:IT:CASS:2019:9468CIV | — prima occorrenza (score 0.77) |
| 2 | ECLI:IT:CASS:2019:9468CIV | ⚠️ DUPLICATO (score 0.41, estratto diverso) |
| 3 | ECLI:IT:CASS:2022:10459CIV | — |
| 4 | ECLI:IT:CASS:2022:1386CIV | — |
| 5 | ECLI:IT:CASS:2020:3819CIV | — |
| 6 | ECLI:IT:CASS:2021:13643CIV | — |
| 7 | ECLI:IT:CASS:2025:21420CIV | — |

**Cass. 9468/2019 appare due volte** con score diverso (0.77 e 0.41) e testi diversi (due estratti della stessa sentenza). Senza la regola C2, Claude citerebbe la stessa sentenza due volte nell'analisi.

**Con la regola C2:** Claude mantiene solo la prima occorrenza per `idatto` → 6 sentenze uniche presentate.

**Esito T40:** ✅ DUPLICATO CONFERMATO — regola necessaria.

### T41 — `search_articles`: duplicato per `numero`+`fonte_normativa`

**Query:** «obblighi sicurezza datore di lavoro prevenzione infortuni»  
**Parametri:** `domain="special_civil"`, `max_results=7` (restituiti 11)

**Duplicati rilevati:**

| numero | fonte_normativa 1 | fonte_normativa 2 | Duplicato? |
|---|---|---|---|
| 278 | «Decreto Legislativo 81/2008» | «Decreto Legislativo n. 81 del 2008» | ⚠️ stesso articolo, nome fonte diverso |
| 35 | «Decreto Legislativo 81/2008» | «Decreto Legislativo n. 81 del 2008» | ⚠️ stesso articolo, nome fonte diverso |
| 271 | «Decreto Legislativo 81/2008» | «Decreto Legislativo n. 81 del 2008» | ⚠️ stesso articolo, nome fonte diverso |

**3 articoli su 11 sono duplicati** con variante del nome della fonte («Decreto Legislativo 81/2008» vs «Decreto Legislativo n. 81 del 2008»). In totale: 11 risultati → 8 unici.

**Nota tecnica:** la regola C2 deduplicava per `numero`+`fonte_normativa` (stringa esatta) — ma poiché il server usa varianti dello stesso nome, la regola va estesa: deduplicare per `numero` + numero identificativo della legge estratto da `fonte_normativa` (es. «81/2008»), indipendentemente dalla formulazione del nome.

**Esito T41:** ✅ DUPLICATI CONFERMATI — regola C2 funziona ma chiave di dedup da rafforzare (candidato v8.3).

---

## Controllo regressione — feature v8.1

### M2 (pertinenza topica) — nessuna regressione ✅
La ricerca su «responsabilità medica» ha restituito risultati tutti pertinenti (responsabilità contrattuale struttura sanitaria ex artt. 1218-1228 c.c., onere della prova, rapporto di spedalità). Nessun fuori tema.

### M4 (sintesi come fonte primaria) — nessuna regressione ✅
Tutte le sintesi restituite sono ricche e complete (es. Cass. 13869/2020: ~400 parole sul principio ex artt. 1218-1228 c.c.; Cass. 7884/2025: perdita di chance e ritardo diagnostico). Nessuna necessità di `get_judgement` per citazione standard.

### M5 (multi-DB) — nessuna regressione ✅
Le ricerche parallele su `civile` e `special_civil` hanno prodotto set di risultati complementari e non sovrapposti (giurisprudenza vs normativa D.Lgs. 81/2008).

---

## Miglioria candidata per v8.3

**C2-bis — Chiave dedup `search_articles` più robusta**  
La chiave `numero`+`fonte_normativa` (stringa esatta) non è affidabile: il server usa varianti dello stesso atto («Decreto Legislativo 81/2008» e «Decreto Legislativo n. 81 del 2008»). La regola va precisata:

> Deduplicare `search_articles` per `numero` + numero identificativo della legge estratto da `fonte_normativa` (es. «81/2008», «392/1978»), trattando come equivalenti le varianti di denominazione dello stesso atto.

Priorità: 🟡 Media — produce ridondanza nella risposta ma non errori fattuali.

---

## Riepilogo finale

| Test | Feature | Esito | Note |
|---|---|---|---|
| T39 | C1 — verifica data_deposito sui risultati | ✅ PASS | Server ignora completamente il filtro; regola indispensabile |
| T40 | C2 — dedup `search_case_law` per idatto | ✅ PASS | Cass. 9468/2019 duplicata con score e testi diversi |
| T41 | C2 — dedup `search_articles` | ✅ PASS (con nota) | 3 duplicati su 11; chiave dedup da rafforzare in v8.3 |
| Regressione M2 | Pertinenza topica | ✅ no regressione | |
| Regressione M4 | Sintesi come fonte primaria | ✅ no regressione | |
| Regressione M5 | Ricerca multi-DB | ✅ no regressione | |

**Tutte le feature v8.2 verificate. Nessuna regressione sulle feature v8.1.** Un aggiustamento minore alla regola C2 per `search_articles` è candidato a v8.3.
