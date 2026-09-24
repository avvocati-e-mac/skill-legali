# Handoff: migliora-chiarezza-testi-legali v2

Documento di passaggio per riprendere il lavoro in una nuova sessione.
Branch: `feat/chiarezza-v2` (pubblicato). Baseline: tag `chiarezza-v1.0`.
Piano approvato: `~/.claude/plans/esamina-la-il-repository-noble-twilight.md`
(copia dei punti essenziali qui sotto).

## Perché esiste la v2 (in una riga per punto)

- Gli esempi della v1 insegnano gli errori che la rubrica vieta: fatti
  inventati, persona invertita (C005), garanzia eliminata, esimenti aggiunte.
- 10 casi di test su 12 ricalcavano gli esempi della skill: il vecchio
  benchmark misurava la copia, non la capacità.
- Richieste di Filippo: percorsi separati atti/pareri e contratti (Garner),
  cadenza chiara ma fluente (Manzoni), niente frasi da IA, progressive
  disclosure efficiente, revisione a step, funzionamento su DeepSeek V4.1
  Flash e Qwen 3.8 Flash, test veri v1 contro v2.

## Fatto

1. Push dei 5 commit normattiva su `main`; tag `chiarezza-v1.0`; branch creato.
2. **Harness** `tests/clarity_eval.py`: cancelli "delta" sul testo prodotto
   (numeri e date nuovi, intensificatori, esimenti, persona, operatori
   giuridici, "si obbliga a", tic da IA, fonti nuove), divisore di frasi con
   abbreviazioni giuridiche, Gulpease e cadenza (solo descrittive),
   "Nessuna modifica necessaria".
3. **Strumenti**: `openrouter_client.py` (DeepSeek fissato su DeepInfra fp8,
   perché il provider DeepSeek risponde 404; Qwen su Alibaba), `run_live.py`
   (simula il caricamento della skill con lo strumento `leggi_file`),
   `analyze_runs.py` (McNemar esatto, bootstrap per caso, A/A, routing,
   onestà del Controllo), `judge_runs.py` (giudice Gemini 3.1 Pro,
   punteggi assoluti), `generate_holdout.py` (holdout scritto da GPT-5.6
   Terra e congelato con SHA-256).
4. **Casi 12 corretti** (commit su branch): gold ripuliti, campi `genre`,
   `context`, `persona`, `expected_references_v2`, `must_preserve_in_dopo`.
   Nessun gold passa più con la semplice copia del PRIMA.
5. **Holdout congelato e committato** (20 casi GPT, SHA-256 in
   `tests/holdout.sha256`). Non leggerlo.
6. **Prima versione v2 committata** (`f1430e8`): SKILL.md, reference
   `atti-e-pareri.md`, `contratti.md`, `frasi-da-ia.md`, `lezione-manzoni.md`,
   script `controlla_invarianti.py`, `research/` fuori dal pacchetto, test
   statici v2 (24 verdi), `.skill` rigenerato.
7. **Primo confronto DEV (12 casi, 3 campioni, harness corretto)**: v1 3-14%
   di output senza errori, v2 86% su entrambi i modelli flash (McNemar
   p<0,001). Scheda e Controllo: nessuna differenza netta (p=0,21); il
   Controllo dichiara "ok" su output con errori in circa un caso su tre.
8. **v2.1** (`b28b615`, poi `8e8097f`): niente diagnosi separata, date e
   numeri conservati, "come sopra rappresentato e difeso" tra le formule.
9. **DEV a 38 casi** (C013-C038, tre lunghi). **Verifica fonti** fatta
   (`tests/verifica-fonti-2026-09.md`): tolta Cass. 3704/2018, citata a
   torto dalla v1. CLAUDE.md e AGENTS.md aggiornati.
10. **Opus**: la CLI `claude` in sottoprocesso non è autenticata (OAuth
    scaduto); si usa `anthropic/claude-opus-5.5` via OpenRouter con
    `run_live.py --samples 1`.

Run in `tests/runs/2026-09-23/dev` (v1) e `tests/runs/2026-09-24/dev`
(v2.1 = `8e8097f`); rilanciare lo stesso comando completa i casi mancanti.
Dopo ogni modifica del harness: `python3 tests/reevaluate_runs.py tests/runs`.

## Ancora da fare

| Lavoro | Comando |
|---|---|
| v1 e v2.1 sui casi C027-C038 | `run_live.py --version chiarezza-v1.0 ...` e `--version 8e8097f ...` (salta ciò che esiste) |
| Analisi DEV | `analyze_runs.py --run-dir tests/runs/2026-09-23/dev --run-dir tests/runs/2026-09-24/dev --compare chiarezza-v1.0__completa 8e8097f__completa` |
| Holdout finale (una volta) | v1 e v2 finale, 2 flash × 3 campioni, Opus via OpenRouter × 1 |
| Giudice e revisione cieca | `judge_runs.py`, `blind_review.py serve ...` |
| Report e README | `tests/REPORT-2026-09-XX.md`, riga del README e cronologia |

**Regola anti-contaminazione:** chi scrive la v2 NON deve leggere
`holdout.json` fino alla valutazione finale. Verifica integrità:
`python3 tests/generate_holdout.py --verify`.

## Prossimi passi, in ordine

1. Unire `cases_dev_new.json` a `cases.json` dopo un controllo a campione;
   togliere il vincolo "≤12 casi" in `test_skill_static.py`; `validate`.
2. Commit "dataset DEV esteso e holdout congelato" (holdout incluso, senza
   leggerlo) e push.
3. **Baseline v1** su DEV (prima di committare la v2):
   `python3 tests/run_live.py --version chiarezza-v1.0 --split dev --samples 3 --run-id <data>`
   poi `python3 tests/analyze_runs.py --run-dir tests/runs/<data>/dev` (A/A incluso).
4. Scrivere i reference v2 (contenuti nel piano, Passo 4):
   `references/atti-e-pareri.md`, `references/contratti.md`,
   `references/frasi-da-ia.md`, `references/lezione-manzoni.md`; correggere
   `interpretazione-civilistica.md`; aggiornare `bibliografia.md` e
   `tradizione-italiana.md` (senza rimandi a `research/`); eliminare
   `principi-garner.md` ed `esempi-atti-giudiziari.md`; spostare `research/`
   fuori dalla cartella interna. Usare solo fonti "VERIFICATO" dal file di
   verifica. Esempi nuovi, senza la lineetta lunga "—".
5. Aggiornare `test_skill_static.py` alla v2 (description ≤1024, corpo
   SKILL.md ≤1000 parole, niente "—" e niente `research/` nei file
   distribuiti, anti-leakage 6-gram tra casi e skill, reference esistenti,
   archivio allineato). Rigenerare `migliora-chiarezza-testi-legali.skill`.
6. Iterare su DEV: `--version working` (varianti `completa` e `senza-step`),
   confronto con `--compare chiarezza-v1.0__completa working__completa`.
   Iterare solo su SKILL.md e reference, mai guardando il holdout.
7. Commit v2 (skill + reference + script + test + .skill), push.
8. **Holdout, una sola volta**: v1 e v2, 2 modelli flash, 3 campioni;
   Opus v2 come riferimento (`claude --bare`, cartella vuota). Giudice:
   `judge_runs.py`. Revisione cieca di Filippo su circa 15 coppie.
9. Report `tests/REPORT-2026-09-XX.md`: endpoint primario (fallimenti di
   fedeltà sul holdout, McNemar + IC bootstrap), secondario (giudizio cieco
   di Filippo), A/A, ablazione degli step, routing, costi, limiti.
10. README, CLAUDE.md e AGENTS.md (skill mancante nell'elenco), correzione
    dei percorsi nel REPORT di luglio; merge su `main` solo se la v2 non
    peggiora la fedeltà.

## Decisioni già prese (non rimettere in discussione)

- Una skill, due percorsi; Manzoni come regole nel nucleo più un reference a
  parte, mai imitazione dello stile ottocentesco.
- Testi lunghi: la skill lavora la prima parte e chiede se continuare; chiude
  sempre con `TESTO RISCRITTO:` e `Sommario:`.
- Holdout solo sintetico, scritto da un modello non-Claude.
- Formula esemplificativa: si abbrevia ("tra cui, a titolo esemplificativo,"),
  non si elimina (art. 1365 c.c. non opera in automatico: Cass. 9560/2017 e
  successive, da confermare nel file di verifica).
- Le soglie di cadenza tratte da Manzoni restano metriche descrittive, non
  cancelli.

## Costi finora

Smoke test OpenRouter: circa 0,01 $. Holdout con GPT-5.6 Terra: da leggere
nel log di OpenRouter. Stima completa del piano: meno di 10 $.
