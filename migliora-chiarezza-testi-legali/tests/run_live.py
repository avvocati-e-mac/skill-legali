#!/usr/bin/env python3
"""Esegue la skill su modelli reali (OpenRouter) e valuta gli output con clarity_eval.

Simula il caricamento reale di una skill: nel prompt di sistema c'e' solo SKILL.md;
i file references/ si leggono con lo strumento `leggi_file`, cosi' si misura anche
se il modello apre i reference giusti (progressive disclosure).

Esempi:
    python3 run_live.py --version chiarezza-v1.0 --split dev --samples 3
    python3 run_live.py --version working --variant senza-step --split dev
    python3 run_live.py --version working --split holdout --samples 3   # una sola volta
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from typing import Any

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

import clarity_eval  # noqa: E402
import openrouter_client  # noqa: E402

SKILL_ROOT = TEST_DIR.parent
REPO_ROOT = SKILL_ROOT.parent
INNER_REL = "migliora-chiarezza-testi-legali/migliora-chiarezza-testi-legali"
INNER_DIR = REPO_ROOT / INNER_REL
RUNS_DIR = TEST_DIR / "runs"
SPLITS = {"dev": TEST_DIR / "cases.json", "holdout": TEST_DIR / "holdout.json"}
DEFAULT_MODELS = ("deepseek/deepseek-v4.1-flash", "qwen/qwen3.8-flash")
STEP_BLOCK_RE = re.compile(r"<!-- step:inizio -->.*?<!-- step:fine -->", re.DOTALL)
MAX_TOOL_TURNS = 6


def skill_files(version: str) -> dict[str, str]:
    """File distribuiti della skill in una versione: 'working' o un riferimento git."""
    if version == "working":
        return {
            path.relative_to(INNER_DIR).as_posix(): path.read_text(encoding="utf-8")
            for path in sorted(INNER_DIR.rglob("*"))
            if path.is_file() and path.suffix in {".md", ".py", ".yaml"} and ".DS_Store" not in path.name
        }
    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", version, INNER_REL],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True,
    ).stdout.split()
    files: dict[str, str] = {}
    for full_path in listing:
        content = subprocess.run(
            ["git", "show", f"{version}:{full_path}"],
            cwd=REPO_ROOT, check=True, capture_output=True, text=True,
        ).stdout
        files[full_path[len(INNER_REL) + 1:]] = content
    return files


def apply_variant(files: dict[str, str], variant: str) -> dict[str, str]:
    if variant == "completa":
        return files
    if variant == "senza-step":
        patched = dict(files)
        patched["SKILL.md"] = STEP_BLOCK_RE.sub("", files["SKILL.md"])
        if patched["SKILL.md"] == files["SKILL.md"]:
            raise SystemExit("Variante senza-step: SKILL.md non contiene i marcatori <!-- step:inizio/fine -->.")
        return patched
    raise SystemExit(f"Variante sconosciuta: {variant}")


def system_prompt(files: dict[str, str]) -> str:
    others = sorted(name for name in files if name != "SKILL.md")
    return (
        "Sei un assistente che lavora per un avvocato italiano. E' attiva la skill "
        "\"migliora-chiarezza-testi-legali\": seguine le istruzioni.\n\n"
        f"<skill_md>\n{files['SKILL.md']}\n</skill_md>\n\n"
        "I file della skill citati in SKILL.md non sono nel contesto: se la skill ti dice "
        "di aprirne uno, leggilo con lo strumento leggi_file. Non puoi eseguire codice.\n"
        f"File disponibili: {', '.join(others)}"
    )


def user_prompt(case: dict[str, Any]) -> str:
    context = case.get("context") or {}
    lines = []
    if context:
        described = "; ".join(f"{key}: {value}" for key, value in context.items())
        lines.append(f"Contesto: {described}.")
    lines.append(
        "Migliora la chiarezza di questo testo. Procedi fino alla fine senza fermarti a chiedere conferma."
    )
    lines.append(f"\n{case['input_text']}")
    return "\n".join(lines)


def tool_spec(files: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "leggi_file",
                "description": "Legge un file della skill (per esempio references/contratti.md).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "percorso": {
                            "type": "string",
                            "enum": sorted(name for name in files if name != "SKILL.md"),
                        }
                    },
                    "required": ["percorso"],
                },
            },
        }
    ]


def run_one(case: dict[str, Any], files: dict[str, str], model: str, temperature: float) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt(files)},
        {"role": "user", "content": user_prompt(case)},
    ]
    tools = tool_spec(files)
    files_read: list[str] = []
    usage_total = {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0}
    provider = None
    started = time.time()
    output = ""
    finish = None
    for _ in range(MAX_TOOL_TURNS + 1):
        response = openrouter_client.chat(model, messages, tools=tools, temperature=temperature)
        provider = response.get("provider", provider)
        usage = response.get("usage") or {}
        usage_total["prompt_tokens"] += usage.get("prompt_tokens", 0) or 0
        usage_total["completion_tokens"] += usage.get("completion_tokens", 0) or 0
        usage_total["cost"] += float(usage.get("cost", 0) or 0)
        choice = response["choices"][0]
        message = choice["message"]
        finish = choice.get("finish_reason")
        calls = message.get("tool_calls") or []
        if not calls:
            output = message.get("content") or ""
            break
        messages.append({"role": "assistant", "content": message.get("content") or "", "tool_calls": calls})
        for call in calls:
            try:
                path = json.loads(call["function"].get("arguments") or "{}").get("percorso", "")
            except json.JSONDecodeError:
                path = ""
            files_read.append(path)
            content = files.get(path, f"File inesistente: {path}")
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": content})
    return {
        "output": output,
        "files_read": files_read,
        "usage": usage_total,
        "provider": provider,
        "finish_reason": finish,
        "seconds": round(time.time() - started, 1),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", required=True, help="'working' oppure un tag/commit git (es. chiarezza-v1.0)")
    parser.add_argument("--variant", default="completa", choices=("completa", "senza-step"))
    parser.add_argument("--split", default="dev", choices=tuple(SPLITS))
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--cases", nargs="*", help="limita a questi id")
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--run-id", default=None, help="cartella in tests/runs/ (default: data odierna)")
    args = parser.parse_args(argv)

    cases = clarity_eval.load_cases(SPLITS[args.split])
    if args.cases:
        cases = [case for case in cases if case["id"] in set(args.cases)]
    files = apply_variant(skill_files(args.version), args.variant)
    version_label = args.version.replace("/", "_")
    run_dir = RUNS_DIR / (args.run_id or date.today().isoformat()) / args.split
    jobs = []
    for model in args.models:
        for case in cases:
            for sample in range(1, args.samples + 1):
                out_path = run_dir / f"{version_label}__{args.variant}" / model.replace("/", "_") / f"{case['id']}__s{sample}.json"
                if out_path.exists():
                    continue
                jobs.append((model, case, sample, out_path))
    print(f"{len(jobs)} chiamate da eseguire ({args.split}, {version_label}, {args.variant}).", flush=True)

    def work(job):
        model, case, sample, out_path = job
        record = run_one(case, files, model, args.temperature)
        evaluation = clarity_eval.evaluate_output(case, record["output"]).as_dict()
        payload = {
            "case_id": case["id"],
            "split": args.split,
            "version": args.version,
            "variant": args.variant,
            "model": model,
            "sample": sample,
            "temperature": args.temperature,
            "genre": case.get("genre"),
            "expected_references": case.get("expected_references_v2"),
            **record,
            "evaluation": evaluation,
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    done = failed = 0
    cost = 0.0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(work, job): job for job in jobs}
        for future in as_completed(futures):
            model, case, sample, _ = futures[future]
            try:
                payload = future.result()
            except Exception as error:  # noqa: BLE001 - si registra e si prosegue
                failed += 1
                print(f"ERRORE {model} {case['id']} s{sample}: {error}", flush=True)
                continue
            done += 1
            cost += payload["usage"]["cost"]
            status = "ok " if payload["evaluation"]["passed"] else "KO "
            print(f"{status}{model.split('/')[-1]:<22} {case['id']} s{sample}  ${cost:.3f}", flush=True)
    print(f"Completate {done}, errori {failed}, costo ${cost:.3f}. Output in {run_dir}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
