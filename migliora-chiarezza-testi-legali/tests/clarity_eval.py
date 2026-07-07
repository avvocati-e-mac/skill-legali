#!/usr/bin/env python3
"""Harness standard library per i golden packet della skill di chiarezza legale."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CASES = BASE_DIR / "cases.json"
DEFAULT_RUBRIC = BASE_DIR / "rubric.md"

REQUIRED_FIELDS = (
    "id",
    "title",
    "document_type",
    "input_text",
    "expected_issues",
    "legal_invariants",
    "acceptable_rewrites",
    "forbidden_changes",
    "required_reference",
    "human_notes",
    "adjudication_status",
    "validation_rationale",
)

VALID_STATUSES = {
    "draft_codex",
    "opus_reviewed",
    "human_reviewed",
    "gold",
    "ambiguous",
    "expert_review_only",
}

REQUIRED_GOLD_ANNOTATORS = {"opus", "human"}
LEGAL_REFERENCE_PATTERNS = (
    re.compile(
        r"\b(?:Cass\.|Cassazione|Corte di Cassazione)\s+[^;\n]*?(?:n\.\s*)?\d{2,}(?:/\d{4}| del \d{4})?",
        re.IGNORECASE,
    ),
    re.compile(r"\bartt?\.\s*[^.;:\n]*", re.IGNORECASE),
    re.compile(r"\bD\.M\.\s*[^.;:\n]*", re.IGNORECASE),
    re.compile(r"\bD\.Lgs\.\s*[^.;:\n]*", re.IGNORECASE),
    re.compile(r"\b(?:legge|l\.)\s+n\.?\s*[^.;:\n]*", re.IGNORECASE),
    re.compile(r"\bCost\.\s*[^.;:\n]*", re.IGNORECASE),
)
LEGAL_REF_NUMBER_RE = re.compile(r"\d+")
SECTION_HEADER_RE = re.compile(
    r"^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*)?"
    r"(PRIMA|DOPO|Motivo)"
    r"(?:\s*\([^:\n]*\))?"
    r"(?:(:)(?:\*\*)?|(?:\*\*)|[ \t]*$)[ \t]*",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class EvalResult:
    case_id: str
    fatal_failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.fatal_failures

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "fatal_failures": self.fatal_failures,
            "warnings": self.warnings,
            "notes": self.notes,
        }


def load_cases(path: Path = DEFAULT_CASES) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("cases.json deve contenere una lista di casi.")
    return data


def validate_cases(cases: list[dict[str, Any]], repo_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    root = repo_root or BASE_DIR.parent

    for index, case in enumerate(cases, start=1):
        prefix = f"case #{index}"
        case_id = case.get("id", prefix)
        if case_id in seen:
            errors.append(f"{case_id}: id duplicato.")
        seen.add(case_id)

        for field_name in REQUIRED_FIELDS:
            if field_name not in case:
                errors.append(f"{case_id}: campo obbligatorio mancante: {field_name}.")

        status = case.get("adjudication_status")
        if status not in VALID_STATUSES:
            errors.append(f"{case_id}: adjudication_status non ammesso: {status!r}.")

        for list_field in (
            "expected_issues",
            "legal_invariants",
            "acceptable_rewrites",
            "forbidden_changes",
            "required_reference",
        ):
            value = case.get(list_field)
            if not isinstance(value, list) or not value:
                errors.append(f"{case_id}: {list_field} deve essere una lista non vuota.")

        for issue in case.get("expected_issues", []):
            if not isinstance(issue, dict) or not {"code", "severity", "description"} <= set(issue):
                errors.append(f"{case_id}: ogni expected_issue richiede code, severity, description.")

        for rewrite in case.get("acceptable_rewrites", []):
            if not isinstance(rewrite, dict) or not rewrite.get("label") or not rewrite.get("text"):
                errors.append(f"{case_id}: ogni acceptable_rewrite richiede label e text.")

        for reference in case.get("required_reference", []):
            reference_path = root / "migliora-chiarezza-testi-legali" / reference
            if not reference_path.exists():
                errors.append(f"{case_id}: reference inesistente: {reference}.")

        annotations = case.get("annotations", {})
        if not isinstance(annotations, dict):
            errors.append(f"{case_id}: annotations deve essere un oggetto.")
        elif status == "gold":
            reviewed = {
                name
                for name, payload in annotations.items()
                if isinstance(payload, dict) and payload.get("status") not in {None, "", "not_run", "pending"}
            }
            if not REQUIRED_GOLD_ANNOTATORS <= reviewed:
                errors.append(f"{case_id}: un caso gold richiede almeno review Opus e umana.")
            if annotations.get("codex", {}).get("status") and reviewed <= {"codex"}:
                errors.append(f"{case_id}: un caso con sola annotazione Codex non puo' essere gold.")
            if not case.get("validation_rationale"):
                errors.append(f"{case_id}: un caso gold richiede validation_rationale.")

        automation = case.get("automation", {})
        if not isinstance(automation, dict):
            errors.append(f"{case_id}: automation deve essere un oggetto.")
        else:
            markers = automation.get("required_output_markers", [])
            if markers and set(markers) != {"PRIMA:", "DOPO:", "Motivo:"}:
                errors.append(f"{case_id}: required_output_markers deve contenere PRIMA, DOPO e Motivo.")

    return errors


def find_case(cases: list[dict[str, Any]], case_id: str) -> dict[str, Any]:
    for case in cases:
        if case.get("id") == case_id:
            return case
    raise KeyError(f"Caso non trovato: {case_id}")


def extract_do_text(output: str) -> str:
    sections = list(SECTION_HEADER_RE.finditer(output))
    if sections:
        blocks: list[str] = []
        for index, section in enumerate(sections):
            if section.group(1).lower() != "dopo":
                continue
            start = section.end()
            end = sections[index + 1].start() if index + 1 < len(sections) else len(output)
            blocks.append(output[start:end].strip())
        if blocks:
            return "\n".join(blocks)

    matches = re.findall(r"DOPO:\s*(.*?)(?=\n\s*(?:PRIMA:|Motivo:)|\Z)", output, flags=re.DOTALL | re.IGNORECASE)
    return "\n".join(match.strip() for match in matches)


def sentence_word_counts(text: str) -> list[int]:
    counts: list[int] = []
    for sentence in re.split(r"[.!?]\s+", text):
        words = re.findall(r"\b\w+\b", sentence)
        if words:
            counts.append(len(words))
    return counts


def extract_legal_references(text: str) -> set[str]:
    refs: set[str] = set()
    for pattern in LEGAL_REFERENCE_PATTERNS:
        refs.update(match.group(0).strip().lower() for match in pattern.finditer(text))
    return refs


def normalize_reference(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip()


def same_reference(candidate: str, known: str) -> bool:
    candidate_norm = normalize_reference(candidate)
    known_norm = normalize_reference(known)
    if candidate_norm == known_norm:
        return True
    if candidate_norm in known_norm or known_norm in candidate_norm:
        return True

    candidate_numbers = set(LEGAL_REF_NUMBER_RE.findall(candidate_norm))
    known_numbers = set(LEGAL_REF_NUMBER_RE.findall(known_norm))
    if candidate_numbers and not candidate_numbers <= known_numbers:
        return False

    candidate_has_cass = "cass" in candidate_norm or "cassazione" in candidate_norm
    known_has_cass = "cass" in known_norm or "cassazione" in known_norm
    return candidate_has_cass and known_has_cass and bool(candidate_numbers & known_numbers)


def is_known_reference(candidate: str, known_refs: set[str]) -> bool:
    return any(same_reference(candidate, known) for known in known_refs)


def evaluate_output(case: dict[str, Any], output: str) -> EvalResult:
    result = EvalResult(case_id=case["id"])
    automation = case.get("automation", {})
    markers = automation.get("required_output_markers", ["PRIMA:", "DOPO:", "Motivo:"])

    for marker in markers:
        if marker not in output:
            result.fatal_failures.append(f"Formato obbligatorio mancante: {marker}")

    do_text = extract_do_text(output)
    if not do_text:
        result.fatal_failures.append("Blocco DOPO non trovato o vuoto.")
        do_text = output

    for literal in automation.get("must_preserve_literals", []):
        if literal.lower() not in output.lower():
            result.fatal_failures.append(f"Elemento da preservare assente: {literal}")

    for forbidden in automation.get("fatal_forbidden_after", []):
        if forbidden.lower() in do_text.lower():
            result.fatal_failures.append(f"Espressione vietata nel DOPO: {forbidden}")

    for group in automation.get("must_include_one_of", []):
        label = group.get("label", "gruppo obbligatorio")
        terms = group.get("terms", [])
        if terms and not any(term.lower() in output.lower() for term in terms):
            result.fatal_failures.append(
                f"Manca almeno uno dei termini richiesti per {label}: {', '.join(terms)}"
            )

    allowed_refs = {ref.lower() for ref in automation.get("allowed_legal_references", [])}
    input_refs = extract_legal_references(case.get("input_text", ""))
    known_refs = input_refs | allowed_refs
    output_refs = extract_legal_references(do_text)
    unknown_refs = sorted(ref for ref in output_refs if not is_known_reference(ref, known_refs))
    if unknown_refs:
        result.warnings.append(
            "Possibili fonti nuove da verificare: " + "; ".join(unknown_refs)
        )

    long_sentences = [count for count in sentence_word_counts(do_text) if count > 45]
    if long_sentences:
        result.warnings.append(f"Frasi ancora lunghe nel DOPO: {long_sentences}")

    if case.get("adjudication_status") in {"ambiguous", "expert_review_only"}:
        result.notes.append(
            "Caso non adatto a fallimento automatico rigido senza revisione esperta."
        )

    return result


def build_ab_prompt(case: dict[str, Any], output_a: str, output_b: str, order: str = "AB") -> str:
    if order not in {"AB", "BA"}:
        raise ValueError("order deve essere AB o BA.")
    first, second = (output_a, output_b) if order == "AB" else (output_b, output_a)
    rubric = DEFAULT_RUBRIC.read_text(encoding="utf-8")
    payload = {
        "case_id": case["id"],
        "document_type": case["document_type"],
        "input_text": case["input_text"],
        "legal_invariants": case["legal_invariants"],
        "forbidden_changes": case["forbidden_changes"],
        "required_reference": case["required_reference"],
    }
    return (
        "Valuta i due output anonimi per la skill di chiarezza legale.\n"
        "Non premiare lunghezza, tono elegante o formattazione se la fedelta' giuridica peggiora.\n"
        "Restituisci JSON con score 0-3 per criterio, fatal_failures e preferenza motivata.\n\n"
        f"RUBRICA:\n{rubric}\n\n"
        f"PACKET:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        f"OUTPUT A:\n{first}\n\n"
        f"OUTPUT B:\n{second}\n"
    )


def cmd_validate(args: argparse.Namespace) -> int:
    cases = load_cases(args.cases)
    errors = validate_cases(cases)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(cases)} casi validi.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    for case in load_cases(args.cases):
        print(f"{case['id']}\t{case['adjudication_status']}\t{case['document_type']}\t{case['title']}")
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    cases = load_cases(args.cases)
    case = find_case(cases, args.case)
    output = Path(args.output).read_text(encoding="utf-8")
    result = evaluate_output(case, output)
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0 if result.passed else 1


def cmd_ab_prompt(args: argparse.Namespace) -> int:
    cases = load_cases(args.cases)
    case = find_case(cases, args.case)
    output_a = Path(args.output_a).read_text(encoding="utf-8")
    output_b = Path(args.output_b).read_text(encoding="utf-8")
    print(build_ab_prompt(case, output_a, output_b, args.order))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="valida cases.json")
    validate_parser.set_defaults(func=cmd_validate)

    list_parser = subparsers.add_parser("list", help="elenca i casi")
    list_parser.set_defaults(func=cmd_list)

    eval_parser = subparsers.add_parser("evaluate", help="valuta un output per un caso")
    eval_parser.add_argument("--case", required=True)
    eval_parser.add_argument("--output", required=True)
    eval_parser.set_defaults(func=cmd_evaluate)

    ab_parser = subparsers.add_parser("ab-prompt", help="genera prompt A/B con ordine invertibile")
    ab_parser.add_argument("--case", required=True)
    ab_parser.add_argument("--output-a", required=True)
    ab_parser.add_argument("--output-b", required=True)
    ab_parser.add_argument("--order", choices=("AB", "BA"), default="AB")
    ab_parser.set_defaults(func=cmd_ab_prompt)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        args = parser.parse_args(["validate"])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
