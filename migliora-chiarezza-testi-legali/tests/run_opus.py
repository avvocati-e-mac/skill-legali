#!/usr/bin/env python3
"""Esegue la skill con Opus tramite la CLI `claude`, in isolamento, come riferimento.

Isolamento (red team 2026-09): ogni caso gira in una cartella temporanea che
contiene solo la skill nella versione scelta; niente skill installate
(--disable-slash-commands), niente server MCP (--strict-mcp-config), niente
impostazioni di progetto, sessione non salvata. Il modello puo' solo leggere i
file della skill (Read). Un controllo sentinella segnala output con link a
Normattiva: vorrebbe dire che un'altra skill e' entrata nel contesto.

    python3 run_opus.py --version 8e8097f --split holdout --run-id 2026-09-25

Se la CLI non e' autenticata, in alternativa si puo' usare Opus via OpenRouter
con run_live.py (--models anthropic/claude-opus-5.5 --samples 1): stesse
condizioni dei modelli flash, costo a consumo.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

import clarity_eval  # noqa: E402
from run_live import RUNS_DIR, SPLITS, apply_variant, skill_files, user_prompt  # noqa: E402

MODEL_LABEL = "anthropic/claude-opus-cli"


def run_case(case, files, model: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="chiarezza-opus-") as tmp:
        skill_dir = Path(tmp) / "skill"
        for name, content in files.items():
            target = skill_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        system = (
            "E' attiva la skill \"migliora-chiarezza-testi-legali\". Le sue istruzioni sono in "
            "skill/SKILL.md: leggile per prime e seguile; leggi i file in skill/references/ solo "
            "quando SKILL.md lo dice. Non puoi eseguire codice."
        )
        started = time.time()
        completed = subprocess.run(
            [
                "claude", "-p", user_prompt(case),
                "--model", model,
                "--output-format", "json",
                "--append-system-prompt", system,
                "--allowedTools", "Read",
                "--disable-slash-commands",
                "--strict-mcp-config",
                "--setting-sources", "project",
                "--no-session-persistence",
            ],
            cwd=tmp, capture_output=True, text=True, timeout=900,
        )
        data = json.loads(completed.stdout or "{}")
    output = data.get("result", "") or ""
    if data.get("is_error") or "Failed to authenticate" in output:
        raise RuntimeError("La CLI claude non e' autenticata: esegui 'claude' e fai il login, poi riprova.")
    return {
        "output": output,
        "files_read": [],
        "usage": {
            "prompt_tokens": (data.get("usage") or {}).get("input_tokens", 0),
            "completion_tokens": (data.get("usage") or {}).get("output_tokens", 0),
            "cost": float(data.get("total_cost_usd", 0) or 0),
        },
        "provider": "claude-cli",
        "finish_reason": data.get("subtype"),
        "seconds": round(time.time() - started, 1),
        "sentinella_normattiva": "normattiva.it" in output,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", required=True)
    parser.add_argument("--variant", default="completa", choices=("completa", "senza-step"))
    parser.add_argument("--split", default="dev", choices=tuple(SPLITS))
    parser.add_argument("--model", default="opus")
    parser.add_argument("--cases", nargs="*")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args(argv)

    cases = clarity_eval.load_cases(SPLITS[args.split])
    if args.cases:
        cases = [case for case in cases if case["id"] in set(args.cases)]
    files = apply_variant(skill_files(args.version), args.variant)
    run_dir = RUNS_DIR / (args.run_id or date.today().isoformat()) / args.split
    out_root = run_dir / f"{args.version.replace('/', '_')}__{args.variant}" / MODEL_LABEL.replace("/", "_")
    jobs = [case for case in cases if not (out_root / f"{case['id']}__s1.json").exists()]
    print(f"{len(jobs)} casi da eseguire con Opus.", flush=True)

    def work(case):
        record = run_case(case, files, args.model)
        payload = {
            "case_id": case["id"], "split": args.split, "version": args.version, "variant": args.variant,
            "model": MODEL_LABEL, "sample": 1, "temperature": None, "genre": case.get("genre"),
            "expected_references": case.get("expected_references_v2"), **record,
            "evaluation": clarity_eval.evaluate_output(case, record["output"]).as_dict(),
        }
        out = out_root / f"{case['id']}__s1.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(work, case): case for case in jobs}
        for future in as_completed(futures):
            case = futures[future]
            try:
                payload = future.result()
            except Exception as error:  # noqa: BLE001
                print(f"ERRORE {case['id']}: {error}", flush=True)
                continue
            flag = " SENTINELLA" if payload["sentinella_normattiva"] else ""
            print(f"{'ok ' if payload['evaluation']['passed'] else 'KO '}{case['id']}{flag}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
