# Case And Result Schema

## Evaluation Case

```json
{
  "candidate_id": "A",
  "source_file": "answer.docx",
  "quesito": "Question text",
  "risposta": "Candidate answer text",
  "ground_truth": "Reference answer or checklist",
  "data_riferimento": "2026-06-16",
  "fonti": ["art. 2385 c.c.", "GDPR art. 5"],
  "confidential": true,
  "extraction": {
    "format": "docx",
    "extracted_at": "2026-06-16T10:00:00+02:00",
    "notes": []
  }
}
```

Use `ground_truth` as a structured checklist when a single model answer would be too subjective. Keep the person who prepared the ground truth and its date in the surrounding report if available.

## Judge Verdict

```json
{
  "judge_id": "codex_gpt_5_5_xhigh",
  "model_route": "codex:gpt-5.5:xhigh",
  "mode": "live_model",
  "candidate_id": "A",
  "source_verification": {"status": "not_performed", "notes": ["..."]},
  "criteria": {
    "correttezza_normativa": {"score": 2, "weight": 3, "weighted": 6, "motivazione": "..."},
    "aggiornamento": {"score": 2, "weight": 2, "weighted": 4, "motivazione": "..."},
    "completezza": {"score": 2, "weight": 2, "weighted": 4, "motivazione": "..."},
    "assenza_allucinazioni": {"score": 3, "weight": 3, "weighted": 9, "motivazione": "..."},
    "citazione_fonti": {"score": 2, "weight": 2, "weighted": 4, "motivazione": "..."},
    "segnalazione_incertezza": {"score": 1, "weight": 1, "weighted": 1, "motivazione": "..."}
  },
  "score_ponderato": 28,
  "score_massimo": 39,
  "percentuale": 71.8,
  "kappa_discrete_score": 2,
  "flag_revisione_umana": true,
  "punti_critici_per_avvocato": ["Verify case-law citations"],
  "raw_file": "panel-results-raw/A__codex_gpt_5_5_xhigh.raw.txt"
}
```

Live judge prompts should ask for one `Judge Verdict` per candidate. If a model returns a council-style object with `judges[].verdicts[]`, the normalizer may flatten it, but separate raw files remain preferred.

## Aggregated Result

```json
{
  "ranking": [
    {"candidate_id": "A", "score_medio": 27.5, "rank": 1}
  ],
  "panel_ranking": {
    "status": "available",
    "best_candidate_id": "A",
    "ranking": []
  },
  "legal_final_assessment": {
    "status": "non_determinato",
    "reason": "Nessuna revisione umana esplicita registrata nel risultato."
  },
  "source_gate": {
    "status": "not_performed",
    "source_verification_status": "not_performed",
    "legal_final_assessment": "non_determinato",
    "counts": {}
  },
  "candidates": [],
  "source_check": {"status": "not_performed", "notes": []},
  "source_verification": {"status": "not_performed", "notes": []},
  "model_tool_availability": {},
  "raw_dir": "panel-results-raw",
  "raw_errors": [
    {"raw_file": "panel-results-raw/A__codex_gpt_5_5_xhigh.raw.txt", "error": "JSON parse failed"}
  ],
  "human_review_flags": [],
  "kappa_ready": []
}
```

## Source Verification Result

```json
{
  "generated_at": "2026-06-16T10:00:00+02:00",
  "status": "not_performed",
  "source_verification": {
    "status": "not_performed",
    "notes": ["..."]
  },
  "policy_order": [
    "Norme italiane: Normattiva skill, official text, vigency, URL, excerpt.",
    "GDPR/UE: EUR-Lex or official EU source, not Normattiva.",
    "Giurisprudenza/provvedimenti: BuddaLaw MCP, then SearXNG, then Perplexity if approved/authenticated, then base web discovery."
  ],
  "records": [
    {
      "candidate_id": "A",
      "citation": "art. 2385 c.c.",
      "article": "2385",
      "act": "c.c.",
      "source_type": "italian_statute",
      "preferred_tool": "normattiva",
      "tool_used": null,
      "official_url": "https://www.normattiva.it/...",
      "status": "unavailable",
      "vigente_al": null,
      "article_text_excerpt": "",
      "finding": "Normattiva skill missing.",
      "score_impact": "human_review_required"
    }
  ]
}
```

Allowed record statuses are `verified`, `mismatch`, `not_found`, `unavailable`, and `unsupported`. Use `verified` only when an official or approved legal source actually confirmed the text or holding.

## Normattiva Fetch Result

`scripts/normattiva_fetch.py` reads either the `Source Verification Result` above or the cases JSON
and writes a source-verification-compatible result:

```json
{
  "generated_at": "2026-06-17T10:00:00+02:00",
  "status": "verified",
  "source_verification": {
    "status": "verified",
    "notes": ["Normattiva fetch verifies official article text availability."]
  },
  "articles_dir": "normattiva-articles",
  "source_gate": {
    "status": "passed",
    "source_verification_status": "verified",
    "legal_final_assessment": "non_determinato"
  },
  "records": [
    {
      "candidate_id": "A",
      "citation": "art. 2385 c.c.",
      "article": "2385",
      "act": "c.c.",
      "source_type": "italian_statute",
      "preferred_tool": "normattiva",
      "tool_used": "normattiva_http",
      "official_url": "https://www.normattiva.it/...",
      "status": "verified",
      "vigente_al": "2026-06-17",
      "article_text_excerpt": "Art. 2385 ...",
      "finding": "Testo articolo scaricato da Normattiva; pertinenza giuridica da verificare separatamente.",
      "score_impact": "text_exists_relevance_not_checked",
      "normattiva": {
        "plain_text_file": "normattiva-articles/a__art.-2385-c.c.__2385.article.txt",
        "raw_html_file": "normattiva-articles/a__art.-2385-c.c.__2385.article.html"
      }
    }
  ]
}
```

Normattiva `verified` means article text was retrieved from the official source. It does not mean
the cited article is legally pertinent to the candidate answer.
