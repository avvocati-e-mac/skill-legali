#!/usr/bin/env python3
"""Prova la skill nel runtime reale di Codex (`codex exec`), senza installarla.

Ogni caso gira in una cartella temporanea che contiene la skill in skill/ e un
AGENTS.md che la dichiara attiva: Codex legge SKILL.md e i reference con i suoi
strumenti, come in un uso normale. Sandbox in sola lettura, sessione effimera.
Usa l'account con cui `codex` e' autenticato (nessun costo OpenRouter).

    python3 run_codex.py --version bd4cdfb --cases C005 C014 C021 C029 C036
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

import clarity_eval  # noqa: E402
from run_live import RUNS_DIR, SPLITS, apply_variant, skill_files, user_prompt  # noqa: E402

MODEL_LABEL = "openai/codex-cli"
AGENTS_MD = (
    "# Istruzioni\n\n"
    "E' attiva la skill \"migliora-chiarezza-testi-legali\". Le sue istruzioni sono in "
    "`skill/SKILL.md`: leggile per prime e seguile. Apri i file in `skill/references/` solo "
    "quando SKILL.md lo dice. Non modificare file: rispondi solo nel messaggio finale.\n"
)


def run_case(case, files, model: str | None) -> dict:
    with tempfile.TemporaryDirectory(prefix="chiarezza-codex-") as tmp:
        root = Path(tmp)
        for name, content in files.items():
            target = root / "skill" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        (root / "AGENTS.md").write_text(AGENTS_MD, encoding="utf-8")
        last = root / "risposta.md"
        command = [
            "codex", "exec", "--skip-git-repo-check", "--ephemeral", "--sandbox", "read-only",
            "-C", tmp, "-o", str(last),
        ]
        if model:
            command += ["-m", model]
        command.append(user_prompt(case))
        started = time.time()
        completed = subprocess.run(command, capture_output=True, text=True, timeout=1200)
        output = last.read_text(encoding="utf-8") if last.exists() else ""
        if not output:
            raise RuntimeError(f"codex non ha prodotto risposta: {completed.stderr[-400:]}")
        # File nominati nel log di Codex, compresi gli elenchi della cartella: indica che cosa
        # Codex ha visto, non che cosa ha aperto. Non usarlo come misura del routing.
        read = sorted({name for name in files if name != "SKILL.md" and name in completed.stdout + completed.stderr})
    return {
        "output": output,
        "files_read": read,
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0},
        "provider": "codex-cli",
        "finish_reason": "stop" if completed.returncode == 0 else f"exit {completed.returncode}",
        "seconds": round(time.time() - started, 1),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", required=True)
    parser.add_argument("--split", default="dev", choices=tuple(SPLITS))
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--model", default=None, help="modello Codex (default: quello configurato)")
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args(argv)

    cases = [case for case in clarity_eval.load_cases(SPLITS[args.split]) if case["id"] in set(args.cases)]
    files = apply_variant(skill_files(args.version), "completa")
    out_root = (RUNS_DIR / (args.run_id or f"codex-{date.today().isoformat()}") / args.split
                / f"{args.version.replace('/', '_')}__completa" / MODEL_LABEL.replace("/", "_"))
    for case in cases:
        out = out_root / f"{case['id']}__s1.json"
        if out.exists():
            continue
        try:
            record = run_case(case, files, args.model)
        except Exception as error:  # noqa: BLE001
            print(f"ERRORE {case['id']}: {error}", flush=True)
            continue
        payload = {
            "case_id": case["id"], "split": args.split, "version": args.version, "variant": "completa",
            "model": MODEL_LABEL, "sample": 1, "temperature": None, "genre": case.get("genre"),
            "expected_references": case.get("expected_references_v2"), **record,
            "evaluation": clarity_eval.evaluate_output(case, record["output"]).as_dict(),
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        verdict = "ok " if payload["evaluation"]["passed"] else "KO "
        print(f"{verdict}{case['id']} ({record['seconds']} s) {payload['evaluation']['fatal_failures'][:2]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
