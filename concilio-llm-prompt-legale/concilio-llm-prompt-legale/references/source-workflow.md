# Source Workflow

Source verification is separate from LLM judging. A judge can assess plausibility, but official or paid legal sources must verify existence, currency, and holdings. In reports, explain `source_verification: not_performed` as: "le citazioni non sono state controllate su fonti ufficiali".

## Esegui la verifica con un SUBAGENTE (non nel thread principale)

`verify-sources` **instrada e classifica** le citazioni come entità (norma italiana, norma UE/GDPR,
sentenza, provvedimento del Garante) e prepara il registro con `preferred_tool` e gli URL ufficiali,
ma **non scarica i testi** (lo stato resta `not_performed`/`unsupported`). La verifica vera va svolta
da un **subagente dedicato**, non leggendo le pagine nel thread principale: ogni lookup web/Normattiva
restituisce pagine lunghe e brucerebbe un'infinità di token nel contesto principale.

Protocollo per il subagente di verifica fonti:

1. Ricevi il registro prodotto da `verify-sources` (lista di citazioni con `source_type`,
   `preferred_tool`, `official_url`).
2. Per ciascuna citazione, recupera la fonte **reale**:
   - norma italiana → skill Normattiva (se installata) o `official_url` Normattiva;
   - norma UE/GDPR → EUR-Lex;
   - sentenza/provvedimento → BuddaLaw o GestioLex Corpus se presenti, altrimenti ricerca web.
3. Valuta **esistenza E pertinenza**: non basta che la fonte esista, deve sostenere l'uso che la
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
   - Use the local Normattiva skill from `avvocati-e-mac/skill-legali` when installed.
   - Read the article text, verify vigency, record the official URL, relevant excerpt, `vigente_al`, finding, and score impact.
   - If the Normattiva skill is missing, stop the official Normattiva check, mark the record `unavailable`, and ask the user before installing it.
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
```

Each record must include `citation`, `source_type`, `preferred_tool`, `tool_used`, `official_url`, `status`, `vigente_al`, `article_text_excerpt`, `finding`, and `score_impact`.

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
