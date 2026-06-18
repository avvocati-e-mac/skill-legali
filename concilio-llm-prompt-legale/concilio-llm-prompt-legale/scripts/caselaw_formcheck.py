#!/usr/bin/env python3
"""Deterministic FORM check for Italian case-law / authority citations.

This script never touches the network. It validates only the *form* of a
jurisprudence citation (court, section, decision number, year) and flags
citations that are malformed, use placeholder/implausible numbers, carry a
future year, or pair an incoherent court/section.

IMPORTANT (semantic contract): form-valid != exists != holding-relevant.
This script NEVER confirms that a judgment exists and NEVER confirms it
supports the candidate answer. A "plausible" form only means the citation is
shaped like a real one and still needs an external check (BuddaLaw/MCP or a
human) for existence and holding. Accordingly this script NEVER emits the
status `verified`.

It downgrades the LLM/MCP job from "verify every case-law citation" to
"verify only the few that pass the form check", and removes obvious fakes
(e.g. n. 99999/2024) from the live token budget at zero cost.

Output is the same envelope produced by `normattiva_fetch.run`, so the JSON
merges cleanly through `legal_panel.py report --sources ...`.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from legal_panel import (
    SOURCE_STATUSES,
    compact_ws,
    detect_source_citations,
    load_cases_json,
    normalize_for_match,
    now_iso,
    official_url_for_source,
    source_gate_from_records,
    source_records_from_payload,
    today_iso,
    verification_status_summary,
)

# --- Form grammar -----------------------------------------------------------

COURT_RE = (
    r"(?P<court>"
    r"Cass(?:azione)?|"
    r"C(?:orte)?\.?\s*Cost(?:ituzionale)?|"
    r"Cons(?:iglio)?\.?\s*(?:di\s+)?Stato|"
    r"TAR|"
    r"CGT|Corte\s+di\s+Giustizia\s+Tributaria|"
    r"Corte\s+d['’\s]*[Aa]ppello|"
    r"Trib(?:unale)?|"
    r"Garante"
    r")"
)
# Optional branch qualifier glued to the court (e.g. "Cass. civ.", "Cass. pen.").
BRANCH_RE = r"(?:[,\s.]*(?P<branch>civ(?:ile)?|pen(?:ale)?|trib(?:utaria)?|lavoro))?"
SECTION_RE = (
    r"(?:[,\s.]*sez(?:ione)?\.?\s*"
    r"(?P<sez>unite|U|lavoro|trib(?:utaria)?|civile|civ|penale|pen|[IVXLC]+|\d+))?"
)
NUMBER_RE = r"(?:n(?:um)?\.?\s*)(?P<num>\d{1,7})"
YEAR_RE = r"[/\s.](?P<year>\d{4})"

CASE_LAW_RE = re.compile(
    COURT_RE + BRANCH_RE + SECTION_RE + r".*?" + NUMBER_RE + YEAR_RE,
    flags=re.IGNORECASE | re.DOTALL,
)

# Repdigit / sequential placeholders frequently used as fake decision numbers.
PLACEHOLDER_NUMBERS = {"99999", "00000", "11111", "12345", "123456", "1234567"}

# Civil vs penal section coherence (used only when the court family is explicit).
CIVIL_SECTIONS = {"i", "ii", "iii", "iv", "v", "vi", "lavoro", "tributaria", "trib", "civile", "civ", "unite", "u"}
PENAL_SECTIONS = {"i", "ii", "iii", "iv", "v", "vi", "vii", "penale", "pen", "unite", "u"}


def parse_case_law(citation: str) -> dict[str, Any] | None:
    """Return {court, section, number, year} parsed from the citation, or None."""
    match = CASE_LAW_RE.search(citation)
    if not match:
        return None
    return {
        "court": compact_ws(match.group("court")),
        "branch": (match.group("branch") or "").strip().lower() or None,
        "section": (match.group("sez") or "").strip().lower() or None,
        "number": match.group("num"),
        "year": match.group("year"),
    }


def _court_family(parsed: dict[str, Any]) -> str | None:
    """Civil vs penal family, taken from the branch qualifier glued to the court."""
    branch = parsed.get("branch")
    if not branch:
        return None
    if branch.startswith("pen"):
        return "penal"
    if branch.startswith("civ") or branch.startswith("trib") or branch == "lavoro":
        return "civil"
    return None


def form_check_record(item: dict[str, Any], *, reference_year: int) -> dict[str, Any]:
    """Build a report-compatible record from a detected case-law citation.

    Status mapping (never `verified`):
      - plausible form, all checks pass -> `unsupported` (needs BuddaLaw/MCP/human)
      - placeholder/implausible number  -> `not_found`
      - future year / incoherent court+section -> `mismatch`
      - unparseable                      -> `unsupported` (malformed, needs human)
    """
    citation = str(item.get("citation") or item.get("raw_match") or "")
    parsed = parse_case_law(citation)
    flags: list[str] = []
    plausibility = "plausible"
    status = "unsupported"
    finding = (
        "Forma citazione plausibile; esistenza e massima NON verificate — "
        "richiede BuddaLaw/MCP o controllo umano."
    )

    if parsed is None:
        plausibility = "malformed"
        flags.append("unparseable_form")
        finding = (
            "Forma citazione giurisprudenziale non riconosciuta (corte/numero/anno mancanti o "
            "ambigui); verifica manuale richiesta."
        )
    else:
        number = parsed["number"]
        year = int(parsed["year"])
        section = parsed["section"]

        if number in PLACEHOLDER_NUMBERS or len(set(number)) == 1:
            plausibility = "implausible"
            status = "not_found"
            flags.append("placeholder_number")
            finding = (
                f"Numero decisione sospetto/placeholder (n. {number}); citazione probabilmente "
                "inventata, da non usare senza riscontro ufficiale."
            )
        elif year > reference_year:
            plausibility = "implausible"
            status = "mismatch"
            flags.append("future_year")
            finding = (
                f"Anno {year} successivo all'anno di riferimento {reference_year}: impossibile, "
                "citazione incoerente."
            )
        elif year < 1900:
            plausibility = "implausible"
            status = "mismatch"
            flags.append("implausible_year")
            finding = f"Anno {year} implausibile per una decisione citabile."
        else:
            family = _court_family(parsed)
            if family == "civil" and section and section in (PENAL_SECTIONS - CIVIL_SECTIONS):
                plausibility = "implausible"
                status = "mismatch"
                flags.append("court_section_incoherent")
                finding = "Sezione incoerente con la corte civile indicata."
            elif family == "penal" and section and section in (CIVIL_SECTIONS - PENAL_SECTIONS):
                plausibility = "implausible"
                status = "mismatch"
                flags.append("court_section_incoherent")
                finding = "Sezione incoerente con la corte penale indicata."

    # Self-declared invented case law in the surrounding text.
    norm = normalize_for_match(citation)
    if "sentenza inventata" in norm or "cassazione inesistente" in norm:
        plausibility = "implausible"
        status = "not_found"
        if "self_declared_invented" not in flags:
            flags.append("self_declared_invented")
        finding = "Il testo dichiara una sentenza inventata/inesistente."

    if status not in SOURCE_STATUSES:  # safety: never leak an unknown status
        status = "unsupported"

    record = {
        "candidate_id": item.get("candidate_id"),
        "citation": citation,
        "article": None,
        "act": "",
        "source_type": "case_law_or_authority",
        "preferred_tool": "buddalaw_mcp",
        "tool_used": "form_check",
        "official_url": official_url_for_source(item),
        "status": status,
        "vigente_al": None,
        "article_text_excerpt": "",
        "finding": finding,
        "score_impact": "manual_case_law_check_required",
        "raw_match": item.get("raw_match"),
        "form_check": {
            "plausibility": plausibility,
            "court": (parsed or {}).get("court"),
            "section": (parsed or {}).get("section"),
            "number": (parsed or {}).get("number"),
            "year": (parsed or {}).get("year"),
            "flags": flags,
        },
    }
    return record


def case_law_items_from_sources(sources_path: Path) -> list[dict[str, Any]]:
    data = json.loads(sources_path.read_text(encoding="utf-8"))
    records = source_records_from_payload(data)
    return [
        record
        for record in records
        if str(record.get("source_type")) == "case_law_or_authority"
    ]


def case_law_items_from_cases(cases_path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for case in load_cases_json(cases_path):
        for detected in detect_source_citations(case):
            if detected.get("source_type") != "case_law_or_authority":
                continue
            items.append({**detected, "candidate_id": case.get("candidate_id")})
    return items


def run(
    *,
    sources_path: Path | None,
    cases_path: Path | None,
    reference_year: int,
) -> dict[str, Any]:
    if sources_path is not None:
        items = case_law_items_from_sources(sources_path)
    elif cases_path is not None:
        items = case_law_items_from_cases(cases_path)
    else:  # pragma: no cover - guarded by argparse
        raise ValueError("Provide --sources or --cases.")

    records = [form_check_record(item, reference_year=reference_year) for item in items]
    status = verification_status_summary(records)
    return {
        "generated_at": now_iso(),
        "status": status,
        "source_verification": {
            "status": status,
            "notes": [
                "Form check deterministico offline delle citazioni giurisprudenziali.",
                "Forma valida != esistenza != massima pertinente: nessun record è 'verified'.",
                "Le citazioni plausibili restano da verificare con BuddaLaw/MCP o controllo umano.",
            ],
        },
        "reference_year": reference_year,
        "source_gate": source_gate_from_records(records),
        "records": records,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sources", help="source-verification JSON from legal_panel.py verify-sources.")
    group.add_argument("--cases", help="panel-input/cases JSON from extract or prepare-live.")
    parser.add_argument(
        "--reference-year",
        type=int,
        default=int(today_iso()[:4]),
        help="Upper bound for plausible decision years (default: current year).",
    )
    parser.add_argument("--output", help="Write the verification JSON here (default: stdout).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run(
        sources_path=Path(args.sources) if args.sources else None,
        cases_path=Path(args.cases) if args.cases else None,
        reference_year=args.reference_year,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(json.dumps({"output": args.output, "status": result["status"]}, ensure_ascii=False))
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
