#!/usr/bin/env python3
"""Profiler della skill: misura DOVE si spende e fa emergere gli sprechi.

A costo zero (offline, nessun modello). Stima i token con un proxy deterministico
(caratteri/4): numeri indicativi ma perfetti per confronti relativi prima/dopo
un'ottimizzazione. Niente dipendenze esterne (coerente con stdlib-only).

Metriche prodotte per un file di casi:
- citazioni totali e ripartizione per tipo (norme / UE / giurisprudenza);
- quante citazioni sono risolvibili in Python (norme via normattiva, giurisprudenza
  scartabile offline dal form-check) vs quante restano delegate all'LLM/MCP;
- dimensione (token-proxy) dei prompt giudice in modalità monolitica vs
  compatta+compressa, e round-trip live stimati con 3 vs 2 giudici.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# scripts/ su sys.path quando eseguito direttamente (fuori da pytest)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "concilio-llm-prompt-legale" / "scripts"))

import caselaw_formcheck as cf  # noqa: E402
import legal_panel as lp  # noqa: E402


def token_proxy(text: str) -> int:
    """Proxy deterministico di token: ~1 token ogni 4 caratteri."""
    return max(1, round(len(text) / 4))


def profile_citations(cases: list[dict]) -> dict:
    by_type = {"italian_statute": 0, "eu_law": 0, "case_law_or_authority": 0, "unknown": 0}
    resolvable_python = 0
    delegated_llm = 0
    caselaw_filtered_offline = 0
    for case in cases:
        for item in lp.detect_source_citations(case):
            stype = item.get("source_type", "unknown")
            by_type[stype] = by_type.get(stype, 0) + 1
            if stype == "italian_statute":
                # risolvibile deterministicamente con normattiva/verify_statutes
                resolvable_python += 1
            elif stype == "case_law_or_authority":
                record = cf.form_check_record({**item, "candidate_id": case.get("candidate_id")}, reference_year=int(lp.today_iso()[:4]))
                if record["status"] in {"not_found", "mismatch"}:
                    # scartata offline: non raggiunge l'MCP
                    caselaw_filtered_offline += 1
                    resolvable_python += 1
                else:
                    delegated_llm += 1
            else:
                delegated_llm += 1
    total = sum(by_type.values())
    return {
        "total": total,
        "by_type": by_type,
        "resolvable_in_python": resolvable_python,
        "delegated_to_llm_or_mcp": delegated_llm,
        "caselaw_filtered_offline": caselaw_filtered_offline,
        "python_resolution_ratio": round(resolvable_python / total, 3) if total else 0.0,
    }


def profile_judge_prompts(cases: list[dict], judges: int = 3) -> dict:
    profile = lp.LIVE_JUDGE_PROFILES[lp.PRIMARY_LIVE_JUDGES[0]]
    monolithic = 0
    compact = 0
    for case in cases:
        monolithic += token_proxy(lp.build_judge_prompt(case, profile))
        compact += token_proxy(lp.build_judge_prompt(case, profile, compact=True, compress=True))
    return {
        "judges_assumed": judges,
        "prompt_tokens_monolithic_per_judge": monolithic,
        "prompt_tokens_compact_compressed_per_judge": compact,
        "input_tokens_3_judges_monolithic": monolithic * 3,
        "input_tokens_2_judges_monolithic": monolithic * 2,
        "input_tokens_3_judges_compact": compact * 3,
        "savings_compact_vs_monolithic_ratio": round(1 - compact / monolithic, 3) if monolithic else 0.0,
        "savings_2_vs_3_judges_ratio": round(1 / 3, 3),
    }


def run(cases_path: Path) -> dict:
    cases = lp.load_cases_json(cases_path)
    return {
        "cases_file": str(cases_path),
        "n_candidates": len(cases),
        "citations": profile_citations(cases),
        "judge_prompts": profile_judge_prompts(cases),
        "note": "Token stimati con proxy caratteri/4: usa i valori per confronti relativi, non come fatturazione.",
    }


def to_markdown(report: dict) -> str:
    c = report["citations"]
    j = report["judge_prompts"]
    lines = [
        "# Profilo skill (proxy token, offline)",
        "",
        f"File casi: `{report['cases_file']}` — candidati: {report['n_candidates']}",
        "",
        "## Citazioni: risolte in Python vs delegate all'LLM/MCP",
        "",
        f"- Totale citazioni: {c['total']}",
        f"- Per tipo: {c['by_type']}",
        f"- Risolvibili in Python (deterministico): {c['resolvable_in_python']} ({c['python_resolution_ratio']:.0%})",
        f"- Delegate a LLM/MCP: {c['delegated_to_llm_or_mcp']}",
        f"- Giurisprudenza scartata offline dal form-check: {c['caselaw_filtered_offline']}",
        "",
        "## Prompt giudice (token-proxy per giudice)",
        "",
        f"- Monolitico: {j['prompt_tokens_monolithic_per_judge']}",
        f"- Compatto+compresso: {j['prompt_tokens_compact_compressed_per_judge']} "
        f"(risparmio {j['savings_compact_vs_monolithic_ratio']:.0%})",
        f"- Input 3 giudici monolitici: {j['input_tokens_3_judges_monolithic']}",
        f"- Input 2 giudici monolitici: {j['input_tokens_2_judges_monolithic']} "
        f"(risparmio {j['savings_2_vs_3_judges_ratio']:.0%})",
        "",
        report["note"],
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True, help="Cases JSON (extract/prepare-live output).")
    parser.add_argument("--format", choices=["json", "md"], default="md")
    parser.add_argument("--output", help="Write here instead of stdout.")
    args = parser.parse_args(argv)
    report = run(Path(args.cases))
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else to_markdown(report)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"profile written to {args.output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
