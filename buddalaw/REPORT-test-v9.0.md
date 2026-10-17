# BuddaLaw — Report di collaudo v9.0

**Data:** 2026-10-17
**Versione collaudata:** 9.0 (branch `feat/buddalaw-v9`)
**Confronto previsto:** v8.4 (tag `buddalaw-v8.4`) e nessuna skill
**Metodo:** tre livelli. A = controlli sui file, senza rete. B = conversazioni vere con BuddaLaw. C = chiamate dirette al server.

> **In una riga.** Nella prima tornata completa, con il server funzionante, la v9.0 con Haiku supera 24 casi su 26, e 17 su 18 fra quelli critici ⚡ (94%), senza nessun link inventato. Poi il server BuddaLaw ha smesso di rispondere («Circuit breaker aperto — backend temporaneamente non disponibile»). Le ripetizioni, il confronto con la v8.4 e il livello C sono quindi da rifare. Il collaudo ha trovato un difetto vero, l'avviso di aggiornamento che non compariva mai: è corretto nella skill, ma la correzione non è ancora stata provata dal vivo.

## Ambiente e isolamento

| Voce | Valore |
|---|---|
| Runtime | Claude Code headless (`claude -p`), connettore claude.ai BuddaLaw |
| Modello | `claude-haiku-5-5`. Il modello predefinito non è stato provato (server fuori servizio) |
| Isolamento | `--disable-slash-commands`: nessuna skill installata è attiva, nemmeno la v8.3 in `~/.claude/skills`. Skill iniettata con `--append-system-prompt-file`. Tool ridotti a Read e ToolSearch, altri server MCP vietati. `system/init` controllato a ogni esecuzione |
| opencode (Qwen 3.8 Flash, DeepSeek V4.1 Flash) | Saltato: OpenRouter è autenticato, ma BuddaLaw nella sandbox non ancora (`buddalaw needs authentication`) |
| Codex / OpenAI | **Non collaudato**: in `~/.codex/config.toml` non c'è il server BuddaLaw |

## Cronologia

| # | Comando | `results/` | Esito |
|---|---|---|---|
| 1 | `run.py --config v9 --runs 1` (26 casi) | 20261017-155125 | valido |
| 2 | `--config v9 --solo-lampo --runs 3` | 20261017-161258 | guasto del server da B03 run 3: colpite 38 esecuzioni su 54 |
| 3 | `--config v8.4,nessuna --solo-lampo --runs 1` | 20261017-163716 | guasto: colpite 28 esecuzioni su 34 |
| — | una chiamata di prova | — | `RetryError`: stop, nessun nuovo tentativo |
| 4 | `--modello default --solo-lampo` | — | non eseguito |
| C | `BUDDALAW_LIVE=1 pytest test_mcp_live.py` | — | non eseguito in questa tornata. Era verde (12/12) poco prima, nel collaudo di S3 |

Un'esecuzione è «colpita» se almeno una risposta di BuddaLaw diceva «Circuit breaker aperto», «backend temporaneamente non disponibile» o «HTTP 500». Le esecuzioni colpite sono escluse dal conteggio. Durante il guasto la skill si è comportata bene: nessuna sentenza a memoria, nessun link inventato, il guasto riferito con le parole del server, nessun ciclo di nuovi tentativi.

## Livello A

52 test passati su 52, con l'archivio `.skill` rigenerato dopo le correzioni. Description: 941 caratteri (limite 1024). `SKILL.md`: 187 righe.

## Livello B — esiti v9.0 con Haiku

Formato: esecuzioni promosse / esecuzioni valide. «—» = nessuna esecuzione valida.

| Caso | ⚡ | Tema | v9 | v8.4 | nessuna |
|---|---|---|---|---|---|
| B00 | ⚡ | isolamento | 4/4 | 1/1 | 1/1 |
| B01 | ⚡ | IVA: tributari/tributario | 4/4 | — | — |
| B02 | ⚡ | Cassazione per numero | 4/4 | — | — |
| B03 | ⚡ | Corte costituzionale | 3/3 | — | — |
| B04 | ⚡ | CGUE con numero di causa | 1/1 | — | 0/1 |
| B05 | ⚡ | casi simili di merito | 1/1 | — | — |
| B06 | ⚡ | list_uffici → codiceufficio | 1/1 | — | — |
| B07 | ⚡ | get_law_article al 2022 | 3/3 | 1/1 | — |
| B08 | | articolo abrogato | 1/1 | | |
| B09 | ⚡ | SU 577/2008 non disponibile | 1/1 | — | — |
| B10 | | Sezioni Unite e contrasto | 1/1 | | |
| B11 | | domanda in inglese | 1/1 | | |
| B12 | ⚡ | avviso di aggiornamento vero | **0/1** | n.a. | n.a. |
| B13 | ⚡ | nessun falso avviso | 1/1 | — | — |
| B14 | ⚡ | passa la mano a verifica-citazioni | 1/1 | — | — |
| B15 | | solo link a una norma | 1/1 | | |
| B16 | ⚡ | check_access prima di tutto | 1/1 | — | — |
| B17 | ⚡ | niente sentenze a memoria | 4/4 | 1/1 | 1/1 |
| B18 | ⚡ | numero e anno interi | 2/2 | — | — |
| B19 | ⚡ | «più recenti» con anno | 1/1 | — | — |
| B20 | | warning di get_law_article | 1/1 | | |
| B21 | ⚡ | not_found penale | 1/1 | — | — |
| B22 | ⚡ | virgolettati letterali | 1/1 | — | — |
| B23 | | avviso su tre turni | **0/1** | n.a. | n.a. |
| B24 | | check_access una sola volta | 1/1 | | |
| B25 | | contratto, ID interi | 1/1 | | |

**Confronto prima/dopo: non conclusivo.** Sui 3 casi validi in comune (B00, B07, B17) v9 e v8.4 sono pari. Le esecuzioni colpite dal guasto mostrano comunque, a titolo indicativo, gli errori che la v9 corregge: senza le sue istruzioni Haiku usa `dominio="tributari"` (B01), non chiama `list_uffici` (B06), non usa `anno` (B19) e, senza skill, non cerca in `eu-case-law` (B04).

## Chiamate e costo

| Tornata | Esecuzioni | Chiamate BuddaLaw | $ |
|---|---|---|---|
| 1 | 26 | 82 | 0,46 |
| 2 | 54 | 154 | 0,33 |
| 3 | 34 | 87 | 0,15 |
| Totale | 114 | ≈ 324 | **≈ 0,94** (tetto 5 $) |

## Criteri di successo del piano

| Criterio | Esito |
|---|---|
| Livello A verde | sì |
| Livello C verde o fermo dichiarato | verde poco prima del guasto (S3, 12/12); da rifare dopo le correzioni |
| ≥ 90% dei casi ⚡ con Haiku (2 su 3) | sì sui dati validi (94%); le 3 ripetizioni complete non sono state possibili |
| ≥ 80% con Qwen e DeepSeek | non verificato: BuddaLaw non ancora autenticato in opencode |
| Zero link inventati | sì: 114 esecuzioni su 114 |
| Costo dichiarato | sì, ≈ 0,94 $ |
| v9 ≥ v8.4, migliore sui divari G1–G8 | non verificato (guasto); pari sui 3 casi validi |
| Avviso presente quando serve, assente quando non serve | assente quando non serve: sì (B13, B24). Presente quando serve: **no** (B12, B23) → corretto, da riprovare |
| Description ≤ 1024; SKILL.md < 500 righe | sì |

## Fallimenti, classificati

Classi: (a) difetto della skill · (b) limite del modello · (c) falso errore del controllo · (g) guasto del server

| Caso | Classe | Causa | Rimedio |
|---|---|---|---|
| B12, B23 | (a) | Nessun passo della procedura richiamava il controllo di aggiornamento | Applicato: richiamo al passo 2 e voce 6 della checklist riscritta |
| B14 | (b)/(a) lieve | Non nominava `verifica-citazioni-legali` | Applicato: regola di precedenza esplicita |
| B15 | (c) | «it» di normattiva.it contato come parola inglese | Runner corretto |
| B07 | (c) | «non ha segnalato avvertenze» letto come box finale; «novanta» in lettere | Runner e caso corretti |
| B22 (prima tornata) | (c) | Apostrofo tipografico ’ contro apostrofo dritto ' | Runner corretto |
| B00 v8.4 | (c) | Connettore `pending` all'avvio | Runner corretto |
| B04 nessuna | (b) | Senza skill non cerca in `eu-case-law` | Atteso (G2) |
| tornate 2–3 | (g) | Circuit breaker, HTTP 500, RetryError | Esclusi, da rifare |

## Correzioni applicate dopo il collaudo e la revisione indipendente

Applicate alla skill dopo questi dati. Sono controllate dal livello A, ma non ancora dal vivo:

- avviso di aggiornamento richiamato al passo 2 della procedura; il secondo motivo di avviso vale solo per un valore della tabella che il server non accetta più;
- link alle norme fatti solo dalla skill normattiva: il `normattiva_url` di BuddaLaw per i codici e i d.m. può aprire un altro articolo;
- tetto delle chiamate definito con precisione (contano le `search_*`);
- `not_found` nella Cassazione: una nuova lettura con il solo `dominio`; se l'utente non dice civile o penale, prima civile e poi penale;
- di nuovo la tabella materia → `domain` di `search_articles`, che era nella v8.4;
- segnaposto al posto di estremi ed esempi presi da casi veri;
- `chiama_mcp.py` si ferma anche sul «circuit breaker».

## Da fare quando il server risponde di nuovo (con il via dell'utente)

1. Livello C.
2. `--config v9 --solo-lampo --runs 3` (in particolare B12, B13, B23, B24), poi `--config v8.4,nessuna --solo-lampo` e `--modello default --solo-lampo`.
3. Autenticare BuddaLaw in opencode e lanciare `--runtime opencode --config v9 --runs 1`, poi `--solo-lampo --runs 3`.
4. Aggiornare questo report.
