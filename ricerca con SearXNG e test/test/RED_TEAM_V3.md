# Red teaming V3 — del codice, dei test e dei nuovi risultati

Estende `RED_TEAM_V2.md`. Focus richiesto: red teaming dei test + miglior programmazione + red teaming dei risultati.

## A. Red teaming del CODICE/TEST (nuovo, il più importante)

### RT-CODE-1 — Krippendorff α non era validata 🔴 → ✅ CHIUSO
La metrica chiave del report (α) era hand-rolled senza alcun test. Rischio: tutti gli α inventati.
- **Fix**: `metrics.py` (logica pura) + `test_compute.py` (15 test: known-answer canonico 0.6914, oracolo
  differenziale su 100 casi, edge case, property bounded). **15/15 PASS.** α confermata corretta.

### RT-CODE-2 — Ground-truth preso da un LLM era SBAGLIATO 🔴 → documentato
Perplexity ha fornito il valore atteso del caso canonico come 0.7477 e poi 0.9231: **entrambi errati** (vero
0.6914). Se mi fossi fidato, avrei "corretto" un'implementazione giusta verso una sbagliata.
- **Lezione/regola**: il valore atteso di un known-answer test deve venire da calcolo deterministico o seconda
  implementazione, **mai** da un LLM. Applicato.

### RT-CODE-3 — Metriche duplicate in più script (DRY) 🟡 → ✅ CHIUSO
`dcg`/`ndcg`/α erano copiate in `compute_ndcg.py` e `compute_alpha.py`. Refactor → import da `metrics.py` unico.
Verificato: nDCG 0.732 invariato, α invariati.

### RT-CODE-4 — Il mio script di analisi aveva un bug 🟡 → corretto
`analyze_a6.py` usava `KEY[qid][0 if side=="A" else "B"]` (stringa come indice di tupla) → TypeError. Corretto a
indice intero. **Conferma che anche gli script di analisi vanno eseguiti/verificati, non solo scritti.**

### Best practice ANCORA non applicate (onestà)
- Nessun `requirements.txt`/ambiente bloccato (ma: zero dipendenze esterne per scelta → mitigato).
- Test non in CI (eseguiti a mano). Per un repo serio andrebbero in un hook/CI.
- I dict di label/giudizio Claude sono dati-in-codice; idealmente in JSON/CSV separati. Parzialmente fatto (metrics
  separato; i dati di valutazione restano inline per tracciabilità nel medesimo file versionato).

## B. Red teaming dei RISULTATI V3

### RT-V3-1 — "Claude V1 = tutto True" era un'assunzione 🟡 → verificato
Controllato: le celle V1 sulle query non contestabili erano davvero tutte ✅ (0 ⚠️). Assunzione valida.

### RT-V3-2 — Contaminazione misurata solo su 1 run? 🟡 → verificato
Ricalcolata su entrambi i run: **3/26 in run 1 E run 2** (identica). Stabile, non artefatto.

### RT-V3-3 — "Bias simmetrico" era impreciso 🟡 → corretto
Il campione è 3-4 celle: non posso affermare simmetria. **Corretto in RESULT_V3**: posso solo dire che NON c'è
self-preference pro-SearXNG; la direzione (semmai pro-Perplexity) è un segnale debole.

### RT-V3-4 — RT9 ribaltato 🟢 → reperto netto
Combinando A6+V2: ~3 celle contaminate pro-Perplexity, 1 pro-SearXNG → Claude NON favoriva sé/SearXNG. Il confronto
è conservativo per SearXNG. (Buona notizia per la difendibilità: il giudice-Claude non ha "tifato" per la skill.)

### RT-V3-5 — Verbosity bias non isolato 🟡 → dichiarato non concludente
Tutti i giudici votano True sul testo lungo 73–88%, ma "lungo"≈"Perplexity"≈"spesso corretto". Non posso separare
"premia la lunghezza" da "il lungo era migliore". Serve un test lunghezza-controllata (stessa qualità, lunghezze
diverse) → non fatto, segnalato come limite.

### RT-V3-6 — Potenza statistica ancora limitata 🟡 → aperto
10 query totali, 2 run. α su 8–26 unità: indicativo. La *stabilità* è alta (A3), ma il numero di *query* resta il
limite. Per pubblicabilità servirebbero ~30+ query. Onestà: questo è un benchmark *robusto come metodo*, non
*potente come campione*.

## C. Cosa regge dopo tutto il red teaming
- α validata (15/15), nDCG validato → i numeri sono corretti.
- Conclusione "pari + Perplexity non gold-standard" sopravvive a: sensitivity (label), multi-giudice (5 vendor),
  varianza (run), e ora codice testato.
- Il bias del giudice-Claude è caratterizzato e **non avvantaggia SearXNG** → confronto difendibile.

## D. Azioni residue (oneste, non fatte)
- A4/RT6: routing legale Normattiva/BuddaLaw mai confrontato (il pezzo più "skill-specifico").
- Più query per potenza statistica (RT-V3-6).
- Test lunghezza-controllata per isolare il verbosity bias (RT-V3-5).
- Test in CI invece che a mano.
