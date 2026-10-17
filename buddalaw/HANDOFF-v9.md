# BuddaLaw v9.0 — Passaggio di consegne

**Data:** 2026-10-17
**Branch:** `feat/buddalaw-v9` · **PR in bozza:** https://github.com/avvocati-e-mac/skill-legali/pull/1 (non unire a `main` senza l'ok del maintainer)
**Piano di riferimento:** il piano «BuddaLaw v9.0: skill allineata al server reale, avviso di obsolescenza, test a tre livelli» (riassunto qui sotto)

## Dove siamo

| Fatto | Commit |
|---|---|
| Sondaggio del server MCP 1.30.0 (16 tool, enum, formati, 37 comportamenti) | `f4c48ea` |
| Skill v9.0: 187 righe, procedura in 7 passi, tabella di instradamento, inventario dei tool per l'avviso di aggiornamento | `6dca99e` |
| Suite di test a tre livelli (A offline, B end-to-end, C live) e `tests/CHECKLIST.md` (T01–T84) | `83a33c9` |
| Report di collaudo con Haiku | `9659b35` |
| README e CLAUDE.md/AGENTS.md allineati | `a0c39ee`, `aa6e9ca` |

Livello A: 52/52 verde. Haiku v9: 24/26 casi, ⚡ 17/18, zero link inventati su 114 esecuzioni, ≈ 0,94 $. Dettagli in `REPORT-test-v9.0.md`.

## Aggiornamento dopo la ripresa del 17 ottobre

- Il maintainer ha autorizzato la ripresa e chiesto un confronto mirato sullo
  stesso quesito con **subagenti GPT Astra e Luna**, più **DeepSeek V4.1 Flash e
  Qwen 3.8 Flash-Next tramite OpenCode/OpenRouter**. Quattro risposte concluse,
  conservate integralmente in `tests/e2e/results/20261017-caso-chirurgo/` (ignorata
  da git) e copiate in Downloads con il confronto e gli audit.
- BuddaLaw è autenticato in OpenCode; non occorre presumere un nuovo login.
  Qwen Flash-Next usa l'ID `openrouter/qwen/qwen3.8-flash`. Versione CLI: 1.18.19.
- Esiti mirati: Astra 4 ricerche e 1 integrale ottenuto su 2 richieste; Luna
  3 ricerche e 2 integrali dichiarati nell'audit; DeepSeek **10 ricerche** e
  nessun integrale ottenuto; Qwen **7 ricerche**, nessun integrale ottenuto,
  **4 chiamate non conformi e 1 URL giurisprudenziale alterato**. Dati completi
  nel report; questo singolo caso non sostituisce la suite né prova soglie
  percentuali di affidabilità.
- Costo OpenCode delle due risposte concluse: **0,05780 $**, esclusi
  preparazione e tentativo incompleto. Costi GPT non disponibili.
- La suite generale è stata interrotta per il quesito richiesto: Qwen aveva
  passato B00–B02. Le prove preparatorie con isolamento errato sono escluse.
- Il runner ora esclude tutti gli MCP estranei ereditati, non avvia il modello
  se la skill viene caricata dalla posizione sbagliata e ferma anche HTTP 500.
  La sandbox nega `task` e `question`: una delega interna `explore` aveva lasciato
  aperto il primo tentativo DeepSeek. Il tentativo è conservato separatamente.
  Per il quesito mirato sono stati usati 16 passi; il runner ordinario resta a 8.
- Offline: **61/61** (52 strutturali più 9 sul runner). La skill e il `.skill`
  non sono cambiati. Non sono state aggiornate copie installate.
- Il canale C via Claude ha rifiutato `claude-haiku-5-5` come modello non
  riconosciuto, senza chiamare BuddaLaw: risolvere questo ID prima di rilanciarlo.

La lista qui sotto descrive il lavoro generale ancora aperto, con le
precisazioni dell'aggiornamento sopra. Non unire la PR senza l'ok del maintainer.

## Cosa resta da fare

Nella prima tornata il server era andato fuori servizio a metà collaudo
(«Circuit breaker aperto — backend temporaneamente non disponibile», HTTP 500).
Il maintainer ha poi autorizzato la ripresa e `check_access` è riuscito, come
registrato sopra. Per completare il lavoro generale rimangono questi passi;
resta lo stop senza ritenti automatici al primo nuovo blocco o guasto:

1. **Livello C:** `BUDDALAW_LIVE=1 python3.14 -m pytest buddalaw/tests/test_mcp_live.py`
2. **Livello B, Haiku:**
   - `python3 buddalaw/tests/e2e/run.py --runtime claude --config v9 --solo-lampo --runs 3`, guardando soprattutto B12 e B23 (avviso di aggiornamento: la correzione non è ancora provata dal vivo), B13 e B24;
   - `--config v8.4,nessuna --solo-lampo` per il confronto (oggi non conclusivo: 3 casi validi, pari);
   - `--modello default --solo-lampo`.
3. **opencode (Qwen 3.8 Flash-Next, DeepSeek V4.1 Flash):** eseguire `bash buddalaw/tests/e2e/prepara_opencode.sh` per applicare le esclusioni aggiornate. OpenRouter e BuddaLaw risultano autenticati: fare `opencode mcp auth buddalaw` soltanto se viene richiesto. Completare `--runtime opencode --config v9 --runs 1` e `--solo-lampo --runs 3`.
4. Aggiornare `REPORT-test-v9.0.md` con i nuovi esiti, poi commit e push.
5. Facoltativo: verificare con `normattiva/normattiva/scripts/verifica.py` le due discrepanze URN di `get_law_article` (S1: allegato `;262` invece di `;262:2` per i codici; S2: URN diverso per il D.M. 55/2014).
6. Togliere la bozza dalla PR e unire solo dopo l'ok.

## Avvertenze per chi riprende

- **pytest:** nella ripresa anche `python3.14` era privo di pytest; i 61 controlli sono stati eseguiti con `uv run --no-project --with pytest --python /opt/homebrew/bin/python3.14 python -m pytest buddalaw/tests/test_struttura.py buddalaw/tests/test_e2e_runner.py`, usando una cache temporanea, senza modificare Python installato.
- **Isolamento:** in `~/.claude/skills/buddalaw` (e probabilmente `~/.codex/skills/buddalaw`) c'è una vecchia v8.3 con lo stesso nome. I runner la escludono (`--disable-slash-commands`; in opencode `OPENCODE_DISABLE_EXTERNAL_SKILLS=1`, `OPENCODE_DISABLE_CLAUDE_CODE=1`). Non aggiornare quelle copie senza consenso.
- **Spesa:** tetto del runner 5 $ per modello (`--budget`); finora ≈ 0,94 $.
- **Server:** fermarsi al primo 403/429, circuit breaker o HTTP 500, senza ritentare (`tools/chiama_mcp.py` lo fa già).
- **Riservatezza:** non leggere file di credenziali (es. `auth.json` di opencode); nessuna chiave nel repo; fixture pseudonimizzate.
- **Schema:** se il livello C segnala un cambio di schema, rigenerare la fixture con `python3 buddalaw/tests/tools/estrai_schema.py` e aggiornare l'inventario in fondo a `SKILL.md`, poi rigenerare `buddalaw.skill`.
- **GPT / Codex:** Astra e Luna collaudati come subagenti con MCP nativi in questa sessione. Non equivale a un collaudo della CLI Codex né a un aggiornamento della sua configurazione locale.
