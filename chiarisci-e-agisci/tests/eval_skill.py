#!/usr/bin/env python3
"""Forward test riproducibili per chiarisci-e-agisci."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
OUTER_ROOT = TEST_DIR.parent
SKILL_ROOT = OUTER_ROOT / "chiarisci-e-agisci"
SKILL_MD = SKILL_ROOT / "SKILL.md"
CASES_PATH = TEST_DIR / "cases.json"
ALL_REFERENCES = {
    "organizzazione-del-lavoro.md",
    "prodromi-redazionali.md",
    "prioritizzazione.md",
    "integrazione-dei-workflow.md",
}


def load_cases(path: Path = CASES_PATH) -> list[dict]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        raise ValueError("cases.json deve contenere una lista.")
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Gli ID dei casi devono essere univoci.")
    return cases


def validate_cases(cases: list[dict]) -> list[str]:
    errors: list[str] = []
    required = {
        "id", "title", "category", "interaction", "turns",
        "expected_references", "forbidden_references", "max_questions",
        "must_not_contain",
    }
    for case in cases:
        missing = required - set(case)
        if missing:
            errors.append(f"{case.get('id', '?')}: campi mancanti {sorted(missing)}")
        if case.get("interaction") not in {"first_turn", "multi_turn"}:
            errors.append(f"{case.get('id', '?')}: interaction non valida")
        if not case.get("turns"):
            errors.append(f"{case.get('id', '?')}: almeno un turno richiesto")
        refs = set(case.get("expected_references", [])) | set(case.get("forbidden_references", []))
        unknown = refs - ALL_REFERENCES
        if unknown:
            errors.append(f"{case.get('id', '?')}: reference sconosciute {sorted(unknown)}")
    return errors


def build_prompt(case: dict) -> str:
    conversation = "\n\n".join(
        f"Turno {index + 1}:\n{turn}" for index, turn in enumerate(case["turns"])
    )
    return (
        "Usa $chiarisci-e-agisci leggendo il file "
        f"{SKILL_MD} e soltanto le reference necessarie. "
        "Se il NOT-TRIGGER è applicabile, rispondi direttamente senza usare un workflow maieutico. "
        "Non parlare del test e non simulare tool o letture che non hai eseguito.\n\n"
        f"Conversazione da continuare:\n{conversation}\n\n"
        "Rispondi soltanto all'ultimo messaggio dell'utente."
    )


def _extract_reference_paths(value: str) -> set[str]:
    return set(re.findall(r"references/([a-z0-9-]+\.md)", value))


def parse_codex(raw: str) -> tuple[str, set[str], str | None]:
    messages: list[str] = []
    refs: set[str] = set()
    error: str | None = None
    for line in raw.splitlines():
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if item.get("type") == "agent_message":
            messages.append(item.get("text", ""))
        if item.get("type") == "command_execution":
            refs |= _extract_reference_paths(item.get("command", ""))
        if event.get("type") == "error":
            error = str(event.get("message") or event)
    return (messages[-1] if messages else "", refs, error)


def parse_claude(raw: str) -> tuple[str, set[str], str | None]:
    messages: list[str] = []
    refs: set[str] = set()
    error: str | None = None
    for line in raw.splitlines():
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result":
            result = event.get("result", "")
            if result:
                messages.append(result)
            if event.get("is_error"):
                error = result or str(event.get("errors") or "errore Claude")
        message = event.get("message", {})
        for block in message.get("content", []) if isinstance(message, dict) else []:
            if block.get("type") == "text":
                messages.append(block.get("text", ""))
            if block.get("type") == "tool_use":
                refs |= _extract_reference_paths(json.dumps(block.get("input", {}), ensure_ascii=False))
    return (messages[-1] if messages else "", refs, error)


def evaluate_case(case: dict, output: str, refs: set[str], error: str | None = None) -> dict:
    lowered = output.casefold()
    expected = set(case["expected_references"])
    forbidden = set(case["forbidden_references"])
    checks = {
        "runtime_ok": error is None,
        "expected_references": expected <= refs,
        "no_forbidden_references": not (forbidden & refs),
        "question_budget": output.count("?") <= int(case["max_questions"]),
        "required_language": all(
            any(option.casefold() in lowered for option in group)
            for group in case.get("must_contain_all_any", [])
        ),
        "required_any": (
            not case.get("must_contain_any")
            or any(item.casefold() in lowered for item in case["must_contain_any"])
        ),
        "forbidden_content": not any(
            item.casefold() in lowered for item in case.get("must_not_contain", [])
        ),
    }
    return {
        "id": case["id"],
        "title": case["title"],
        "checks": checks,
        "passed": all(checks.values()),
        "references": sorted(refs),
        "question_count": output.count("?"),
        "output": output,
        "error": error,
    }


def run_command(runtime: str, prompt: str, timeout: int, model: str | None) -> tuple[str, int]:
    if runtime == "codex":
        command = [
            "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
            "--sandbox", "read-only", "--skip-git-repo-check", "--json", "-C", "/private/tmp",
        ]
        if model:
            command += ["-m", model]
        command.append(prompt)
    else:
        command = [
            "claude", "-p", "--verbose", "--output-format", "stream-json",
            "--no-session-persistence", "--permission-mode", "dontAsk",
            "--allowedTools", "Read", "--add-dir", str(SKILL_ROOT),
        ]
        if model:
            command += ["--model", model]
        command += ["--", prompt]
    completed = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
        env=os.environ.copy(),
    )
    return completed.stdout, completed.returncode


def command_run(args: argparse.Namespace) -> int:
    cases = load_cases()
    if args.case:
        wanted = set(args.case)
        cases = [case for case in cases if case["id"] in wanted]
    raw_dir = TEST_DIR / "results" / "raw" / args.label / args.runtime
    raw_dir.mkdir(parents=True, exist_ok=True)
    results = []
    parser = parse_codex if args.runtime == "codex" else parse_claude
    for case in cases:
        raw, returncode = run_command(args.runtime, build_prompt(case), args.timeout, args.model)
        (raw_dir / f"{case['id']}.jsonl").write_text(raw, encoding="utf-8")
        output, refs, error = parser(raw)
        if returncode and not error:
            error = f"exit code {returncode}"
        results.append(evaluate_case(case, output, refs, error))
        print(f"{case['id']}: {'PASS' if results[-1]['passed'] else 'FAIL'}")
    summary = {
        "runtime": args.runtime,
        "label": args.label,
        "total": len(results),
        "passed": sum(item["passed"] for item in results),
        "results": results,
    }
    destination = TEST_DIR / "results" / f"{args.label}-{args.runtime}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(destination)
    return 0 if summary["passed"] == summary["total"] else 1


def command_evaluate(args: argparse.Namespace) -> int:
    cases = {case["id"]: case for case in load_cases()}
    raw_dir = Path(args.raw_dir)
    parser = parse_codex if args.runtime == "codex" else parse_claude
    results = []
    for path in sorted(raw_dir.glob("*.jsonl")):
        case = cases[path.stem]
        output, refs, error = parser(path.read_text(encoding="utf-8"))
        results.append(evaluate_case(case, output, refs, error))
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if results and all(item["passed"] for item in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.set_defaults(func=lambda _args: _validate_command())
    run = subparsers.add_parser("run")
    run.add_argument("--runtime", choices=("codex", "claude"), required=True)
    run.add_argument("--label", required=True)
    run.add_argument("--case", action="append")
    run.add_argument("--model")
    run.add_argument("--timeout", type=int, default=180)
    run.set_defaults(func=command_run)
    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--runtime", choices=("codex", "claude"), required=True)
    evaluate.add_argument("--raw-dir", required=True)
    evaluate.set_defaults(func=command_evaluate)
    args = parser.parse_args()
    return args.func(args)


def _validate_command() -> int:
    cases = load_cases()
    errors = validate_cases(cases)
    print(f"casi={len(cases)} first_turn={sum(c['interaction'] == 'first_turn' for c in cases)} multi_turn={sum(c['interaction'] == 'multi_turn' for c in cases)}")
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
