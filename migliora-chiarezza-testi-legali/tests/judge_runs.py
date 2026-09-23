#!/usr/bin/env python3
"""Giudice LLM esplorativo (non-Claude) sugli output di run_live.py.

Scelte contro i bias noti (red_team.md, REPORT 2026-09):
- giudice di un'altra famiglia (default Gemini via OpenRouter): niente self-preference
  verso testi scritti con una skill redatta da Claude;
- giudizio ASSOLUTO su un output per volta, non preferenza A/B: niente position bias;
- sezioni "Scheda" e "Controllo" rimosse prima del giudizio: il giudice non capisce
  quale versione della skill ha prodotto l'output;
- domande chiuse per invariante (si'/no) e punteggi 0-3.
Il risultato e' solo esplorativo: si riporta nel report solo se l'accordo con la
revisione cieca dell'avvocato (kappa) e' almeno 0,4.

Esempio:
    python3 judge_runs.py --run-dir runs/2026-09-23/dev --arms chiarezza-v1.0__completa working__completa
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean
from typing import Any

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

import clarity_eval  # noqa: E402
import openrouter_client  # noqa: E402

DEFAULT_JUDGE = "google/gemini-3.1-pro-preview"
HIDDEN_SECTIONS = {"scheda", "controllo"}

PROMPT = """Sei un avvocato italiano esperto di tecnica redazionale. Valuta UNA riscrittura di un testo legale.
La riscrittura deve rendere il testo piu' chiaro SENZA cambiarne il significato giuridico e mantenendo il
registro forense. Non premiare la lunghezza, l'eleganza o la formattazione se la fedelta' peggiora.

CONTESTO: {context}

TESTO ORIGINALE:
{input_text}

INVARIANTI GIURIDICHE (devono restare vere nella riscrittura):
{invariants}

MODIFICHE VIETATE:
{forbidden}

RISCRITTURA DA VALUTARE (blocchi DOPO, eventuale TESTO RISCRITTO, motivazioni):
{output}

Rispondi SOLO con un oggetto JSON:
{{"invarianti": [{{"n": 1, "rispettata": true}}, ...],
  "modifiche_vietate_presenti": [numeri delle modifiche vietate compiute, lista vuota se nessuna],
  "fatti_aggiunti": true/false (fatti, date, importi, termini, esimenti o fonti non presenti nell'originale, esclusi i segnaposto tra parentesi quadre e le proposte marcate come PROPOSTA),
  "fedelta": 0-3, "chiarezza": 0-3, "fluidita": 0-3 (si legge bene, senza frasi a singhiozzo), "naturalezza": 0-3 (non sembra scritto da un'IA), "registro_forense": 0-3,
  "nota": "una frase"}}"""


def clean_output(output: str) -> str:
    sections = list(clarity_eval.SECTION_HEADER_RE.finditer(output))
    if not sections:
        return output
    kept = [output[: sections[0].start()]] if sections[0].start() > 0 else []
    for index, section in enumerate(sections):
        end = sections[index + 1].start() if index + 1 < len(sections) else len(output)
        if section.group(1).lower() in HIDDEN_SECTIONS:
            continue
        kept.append(output[section.start():end])
    text = "".join(kept)
    return re.sub(r"references/[\w.-]+|SKILL\.md", "[file]", text)


def load_cases() -> dict[str, dict[str, Any]]:
    cases = {}
    for path in (TEST_DIR / "cases.json", TEST_DIR / "holdout.json"):
        if path.exists():
            for case in clarity_eval.load_cases(path):
                cases[case["id"]] = case
    return cases


def judge_one(record: dict[str, Any], case: dict[str, Any], model: str) -> dict[str, Any]:
    prompt = PROMPT.format(
        context=json.dumps(case.get("context", {}), ensure_ascii=False),
        input_text=case["input_text"],
        invariants="\n".join(f"{i}. {text}" for i, text in enumerate(case["legal_invariants"], start=1)),
        forbidden="\n".join(f"{i}. {text}" for i, text in enumerate(case["forbidden_changes"], start=1)),
        output=clean_output(record["output"]) or "(output vuoto)",
    )
    response = openrouter_client.chat(
        model, [{"role": "user", "content": prompt}], temperature=0.0, max_tokens=4000,
        response_format={"type": "json_object"},
    )
    content = response["choices"][0]["message"]["content"] or "{}"
    content = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE)
    verdict = json.loads(content)
    verdict["_cost"] = float((response.get("usage") or {}).get("cost", 0) or 0)
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--arms", nargs="+", required=True)
    parser.add_argument("--judge", default=DEFAULT_JUDGE)
    parser.add_argument("--samples", type=int, nargs="*", default=[1], help="campioni da giudicare (default: solo il primo)")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args(argv)

    cases = load_cases()
    judge_dir = args.run_dir / "_giudice"
    jobs = []
    for path in sorted(args.run_dir.rglob("*.json")):
        if "_giudice" in path.parts:
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        arm = f"{record.get('version')}__{record.get('variant')}"
        if arm not in args.arms or record.get("sample") not in args.samples:
            continue
        out = judge_dir / path.relative_to(args.run_dir)
        if out.exists():
            continue
        jobs.append((record, arm, out))
    print(f"{len(jobs)} giudizi da eseguire con {args.judge}.", flush=True)

    cost = 0.0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(judge_one, record, cases[record["case_id"]], args.judge): (record, arm, out) for record, arm, out in jobs}
        for future in as_completed(futures):
            record, arm, out = futures[future]
            try:
                verdict = future.result()
            except Exception as error:  # noqa: BLE001
                print(f"ERRORE {record['case_id']} {arm}: {error}", flush=True)
                continue
            cost += verdict.get("_cost", 0)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps({"arm": arm, "model": record["model"], "case_id": record["case_id"],
                                       "sample": record["sample"], "harness_passed": record["evaluation"]["passed"],
                                       "verdict": verdict}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Costo giudice: ${cost:.3f}")

    rows: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for path in sorted(judge_dir.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows[(data["arm"], data["model"])].append(data)
    print("\n| Braccio | Modello | n | Fedelta | Chiarezza | Fluidita | Naturalezza | Registro | Fatti aggiunti | Accordo con harness |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for (arm, model), items in sorted(rows.items()):
        verdicts = [item["verdict"] for item in items]
        def avg(key: str) -> str:
            values = [v.get(key) for v in verdicts if isinstance(v.get(key), (int, float))]
            return f"{mean(values):.2f}" if values else "-"
        added = sum(1 for v in verdicts if v.get("fatti_aggiunti"))
        judge_ok = [not v.get("fatti_aggiunti") and not v.get("modifiche_vietate_presenti") and all(i.get("rispettata") for i in v.get("invarianti", [])) for v in verdicts]
        agreement = mean(1.0 if ok == item["harness_passed"] else 0.0 for ok, item in zip(judge_ok, items))
        print(f"| {arm} | {model.split('/')[-1]} | {len(items)} | {avg('fedelta')} | {avg('chiarezza')} | {avg('fluidita')} | {avg('naturalezza')} | {avg('registro_forense')} | {added} | {agreement:.0%} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
