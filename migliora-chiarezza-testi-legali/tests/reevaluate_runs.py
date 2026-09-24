#!/usr/bin/env python3
"""Ricalcola la valutazione di tutti gli output salvati con il harness attuale.

Serve quando si corregge clarity_eval.py o la specifica di un caso: gli output
dei modelli non cambiano, cambia solo il giudizio, uguale per tutte le versioni.

    python3 reevaluate_runs.py runs/2026-09-23
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

import clarity_eval  # noqa: E402

SPLITS = {"dev": TEST_DIR / "cases.json", "holdout": TEST_DIR / "holdout.json"}


def main(argv: list[str]) -> int:
    root = Path(argv[0]) if argv else TEST_DIR / "runs"
    cases = {}
    for split, path in SPLITS.items():
        if path.exists():
            cases[split] = {case["id"]: case for case in clarity_eval.load_cases(path)}
    changed = total = 0
    for path in sorted(root.rglob("*.json")):
        if "_giudice" in path.parts:
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        case = cases.get(record.get("split"), {}).get(record.get("case_id"))
        if not case or "evaluation" not in record:
            continue
        total += 1
        new = clarity_eval.evaluate_output(case, record["output"]).as_dict()
        if new["passed"] != record["evaluation"]["passed"]:
            changed += 1
        record["evaluation"] = new
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rivalutati {total} output; esito cambiato in {changed}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
