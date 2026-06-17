# Source Workflow

Source verification is separate from LLM judging. A judge can assess plausibility, but official or paid legal sources must verify existence, currency, and holdings. In reports, explain `source_verification: not_performed` as: "le citazioni non sono state controllate su fonti ufficiali".

## Esegui la verifica con un SUBAGENTE (non nel thread principale)

`verify-sources` **instrada e classifica** le citazioni come entità (norma italiana, norma UE/GDPR,
sentenza, provvedimento del Garante) e prepara il registro con `preferred_tool` e gli URL ufficiali.
Per le norme italiane, il passaggio successivo è `scripts/normattiva_fetch.py`, che scarica HTML e
TXT degli articoli da Normattiva. Per giurisprudenza e provvedimenti, la verifica vera va svolta da
un **subagente dedicato**, non leggendo le pagine nel thread principale: ogni lookup web o banca dati
restituisce pagine lunghe e brucerebbe molti token nel contesto principale.

Protocollo per il subagente di verifica fonti:

1. Ricevi il registro prodotto da `verify-sources` (lista di citazioni con `source_type`,
   `preferred_tool`, `official_url`).
2. Per ciascuna citazione, recupera la fonte **reale**:
   - norma italiana → `scripts/normattiva_fetch.py` su `source-verification.json` o `panel-input.json`;
   - norma UE/GDPR → EUR-Lex;
   - sentenza/provvedimento → BuddaLaw o GestioLex Corpus se presenti, altrimenti ricerca web.
3. Valuta **esistenza/testo E pertinenza**: lo scarico Normattiva conferma che l'articolo esiste e
   recupera il testo ufficiale, ma non decide da solo se la norma sostiene l'uso che la
   risposta ne fa. Esempi reali: `Cass. 5318/2025` esiste ma è sezione tributaria → se usata per altro,
   `status = mismatch`; un numero di sentenza inesistente → `not_found`.
4. **Ritorna SOLO il registro JSON compilato** (un record per citazione con `status`
   `verified`/`mismatch`/`not_found`/`unavailable`, `official_url`, breve `finding`). Nessun dump di
   pagine web nel contesto principale.

Vale sia in Claude (lancia un subagente/Agent) sia in Codex (subagente/processo separato). Il report
deve riportare l'esito **verificato dal subagente**, non lo stato grezzo `not_performed` del wrapper.

## Route And Confidentiality Gate

Before live search or cloud upload:

1. Leggi `confidential_reason` del caso: se il flag è scattato solo per il tema (o non è scattato) e non risultano dati personali reali (email non placeholder, codici fiscali, parti nominate), **non** trattare il materiale come riservato. Un parere anonimizzato con sole email-esempio non attiva il gate.
2. If the user has not already specified the route, ask whether they want only local/offline processing or also online/live processing.
3. Disclose the intended provider/tool before any cloud/live route.
4. Do not choose local/offline or online/live silently based only on the confidentiality label.

## Verification Order

1. Italian legislation:
   - Run `legal_panel.py verify-sources` first, then `scripts/normattiva_fetch.py` after the user has approved the source-verification route.
   - Normattiva fetch is an official web call. It writes `normattiva-verification.json`, `normattiva-verification.md`, and `normattiva-articles/` with HTML/TXT article files.
   - Record official URL, article text excerpt, `vigente_al`, finding, and score impact.
   - Treat `verified` as existence/text verification only. Still review legal relevance manually.
2. GDPR and EU law:
   - Use EUR-Lex or another official EU source.
   - Do not use Normattiva as the authority for GDPR text or EU-law currency.
3. Case law and measures:
   - Use BuddaLaw MCP or another approved legal database first for Cassation, ordinary courts, TAR/CGT, Garante, and similar citations.
   - GestioLex Corpus MCP (also from `avvocati-e-mac/skill-legali`) is an acceptable approved database for Italian statutes and case-law maxims; use it when installed/approved, instead of or alongside BuddaLaw.
   - If no approved legal database is available, use SearXNG when installed/configured.
   - If SearXNG is unavailable, use Perplexity only when authenticated and explicitly approved.
   - If Perplexity is unavailable/expired/not approved, use base web search only as discovery and confirm against official or authorized sources.
4. Fallback:
   - If no live/official source is available, leave `source_verification` as `not_performed` and state this clearly in the report.

Use the script entrypoint for repeatable citation routing:

```bash
python3 concilio-llm-prompt-legale/scripts/legal_panel.py verify-sources --cases panel-input.json --output source-verification.json
python3 concilio-llm-prompt-legale/scripts/normattiva_fetch.py --sources source-verification.json --output-json normattiva-verification.json --output-md normattiva-verification.md --articles-dir normattiva-articles
```

Each record must include `citation`, `source_type`, `preferred_tool`, `tool_used`, `official_url`, `status`, `vigente_al`, `article_text_excerpt`, `finding`, and `score_impact`.

Then merge one or more source registers into the final report:

```bash
python3 concilio-llm-prompt-legale/scripts/legal_panel.py report --input panel-results-normalized.json --sources source-verification.json --sources normattiva-verification.json --output panel-results-report.md
```

`report --sources` is repeatable. Use it to combine Normattiva outcomes with BuddaLaw/GestioLex
case-law outcomes. If the gate is not clean, the Markdown report is still generated but marked as a
technical provisional report.

## Overrides

Apply these flags even if LLM judges score highly:

- Cited statute not found or cited in an obsolete version: set or recommend `aggiornamento = 0` and human review.
- Case-law citation not verifiable: set or recommend `assenza_allucinazioni = 0-1` and human review.
- Privacy or employment-law advice lacks proportionality, minimization, employee-monitoring, or notice analysis: flag human review.
- The answer recommends automatic forwarding of employee or role mailbox content without minimization or notice analysis: flag high GDPR/employment-law risk.

## Reporting

State whether source checks were:

- `not_performed`: no official-source or live-source check was performed; citations remain unchecked.
- `partial`: web search but no official or paid legal database confirmation.
- `verified`: official source or approved legal database confirmed core citations.

Never present an unverified citation as verified.

Keep these concepts separate:

- `panel_ranking`: LLM panel ranking and scores.
- `source_gate`: source-verification gate from Normattiva/BuddaLaw/GestioLex records.
- `legal_final_assessment`: remains `non_determinato` unless a human lawyer explicitly records a final legal assessment.
