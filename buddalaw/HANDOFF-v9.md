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

## Cosa resta da fare

Il server BuddaLaw è andato fuori servizio a metà collaudo («Circuit breaker aperto — backend temporaneamente non disponibile», HTTP 500). Nessun ritento automatico. **Prima di ripartire serve il via del maintainer**; poi una sola chiamata di prova (`check_access`) e, se risponde:

1. **Livello C:** `BUDDALAW_LIVE=1 python3.14 -m pytest buddalaw/tests/test_mcp_live.py`
2. **Livello B, Haiku:**
   - `python3 buddalaw/tests/e2e/run.py --runtime claude --config v9 --solo-lampo --runs 3`, guardando soprattutto B12 e B23 (avviso di aggiornamento: la correzione non è ancora provata dal vivo), B13 e B24;
   - `--config v8.4,nessuna --solo-lampo` per il confronto (oggi non conclusivo: 3 casi validi, pari);
   - `--modello default --solo-lampo`.
3. **opencode (Qwen 3.8 Flash, DeepSeek V4.1 Flash):** il maintainer deve prima eseguire `bash buddalaw/tests/e2e/prepara_opencode.sh` e poi, dentro `buddalaw/tests/e2e/.opencode-sandbox`, `OPENCODE_DB="$PWD/.opencode-test.db" opencode mcp auth buddalaw`. OpenRouter è già autenticato. Poi `--runtime opencode --config v9 --runs 1` e `--solo-lampo --runs 3`.
4. Aggiornare `REPORT-test-v9.0.md` con i nuovi esiti, poi commit e push.
5. Facoltativo: verificare con `normattiva/normattiva/scripts/verifica.py` le due discrepanze URN di `get_law_article` (S1: allegato `;262` invece di `;262:2` per i codici; S2: URN diverso per il D.M. 55/2014).
6. Togliere la bozza dalla PR e unire solo dopo l'ok.

## Avvertenze per chi riprende

- **pytest:** Homebrew ha portato `python3` alla 3.15 senza pytest; usare `python3.14 -m pytest`.
- **Isolamento:** in `~/.claude/skills/buddalaw` (e probabilmente `~/.codex/skills/buddalaw`) c'è una vecchia v8.3 con lo stesso nome. I runner la escludono (`--disable-slash-commands`; in opencode `OPENCODE_DISABLE_EXTERNAL_SKILLS=1`, `OPENCODE_DISABLE_CLAUDE_CODE=1`). Non aggiornare quelle copie senza consenso.
- **Spesa:** tetto del runner 5 $ per modello (`--budget`); finora ≈ 0,94 $.
- **Server:** fermarsi al primo 403/429, circuit breaker o HTTP 500, senza ritentare (`tools/chiama_mcp.py` lo fa già).
- **Riservatezza:** non leggere file di credenziali (es. `auth.json` di opencode); nessuna chiave nel repo; fixture pseudonimizzate.
- **Schema:** se il livello C segnala un cambio di schema, rigenerare la fixture con `python3 buddalaw/tests/tools/estrai_schema.py` e aggiornare l'inventario in fondo a `SKILL.md`, poi rigenerare `buddalaw.skill`.
- **Codex:** ramo non collaudato (in `~/.codex/config.toml` non c'è BuddaLaw).
