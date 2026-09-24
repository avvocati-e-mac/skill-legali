#!/usr/bin/env python3
"""Aggrega i run di run_live.py e confronta due versioni della skill.

- tasso di superamento dei cancelli per versione/variante e modello;
- categorie di errore piu' frequenti;
- confronto appaiato (stesso modello, caso e campione): McNemar esatto e
  bootstrap raggruppato per caso della differenza nei fallimenti;
- test A/A: campione 1 contro campione 2 della stessa versione (rumore di fondo);
- routing dei reference (v2) e metriche descrittive (lunghezza, Gulpease, cadenza);
- "onesta' del Controllo": quante volte l'output dichiara il controllo superato
  mentre il harness trova un errore.

Esempio:
    python3 analyze_runs.py --run-dir runs/2026-09-23/dev \
        --compare chiarezza-v1.0__completa working__completa
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any

FAILURE_KINDS = (
    ("Formato", "formato"),
    ("Blocco DOPO", "formato"),
    ("Sovra-modifica", "sovra-modifica"),
    ("Sotto-modifica", "sotto-modifica"),
    ("Elemento da preservare", "elemento perso"),
    ("Espressione vietata", "formula non eliminata"),
    ("Manca almeno uno", "scelta non segnalata"),
    ("Persona", "persona"),
    ("Numeri", "numeri/date inventati"),
    ("Intensificatori", "intensificatori"),
    ("Esimenti", "esimenti aggiunte"),
    ("Operatore giuridico", "operatore eliminato"),
    ("Verbo dispositivo", "verbo dispositivo"),
    ("Tic da IA", "tic IA"),
    ("Fonti nuove", "fonti nuove"),
)


def kind_of(failure: str) -> str:
    for prefix, label in FAILURE_KINDS:
        if failure.startswith(prefix):
            return label
    return "altro"


def load_records(run_dir: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted(run_dir.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if "evaluation" in data:
            data["arm"] = f"{data['version']}__{data['variant']}"
            records.append(data)
    return records


def binom_two_sided(k: int, n: int) -> float:
    """p-value esatto di McNemar: binomiale(n, 0.5) sulle coppie discordanti."""
    if n == 0:
        return 1.0
    k = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired(records_a, records_b):
    index_b = {(r["model"], r["case_id"], r["sample"]): r for r in records_b}
    pairs = []
    for record in records_a:
        other = index_b.get((record["model"], record["case_id"], record["sample"]))
        if other:
            pairs.append((record, other))
    return pairs


def compare(pairs, seed: int = 7, iterations: int = 2000) -> dict[str, Any]:
    fail_a = [not a["evaluation"]["passed"] for a, _ in pairs]
    fail_b = [not b["evaluation"]["passed"] for _, b in pairs]
    only_a = sum(1 for x, y in zip(fail_a, fail_b) if x and not y)
    only_b = sum(1 for x, y in zip(fail_a, fail_b) if y and not x)
    by_case: dict[str, list[tuple[bool, bool]]] = defaultdict(list)
    for (a, _), fa, fb in zip(pairs, fail_a, fail_b):
        by_case[a["case_id"]].append((fa, fb))
    cases = list(by_case)
    rng = random.Random(seed)
    diffs = []
    for _ in range(iterations):
        sample = [rng.choice(cases) for _ in cases]
        rows = [row for case in sample for row in by_case[case]]
        if rows:
            diffs.append(mean(fb for _, fb in rows) - mean(fa for fa, _ in rows))
    diffs.sort()
    low = diffs[int(0.025 * len(diffs))] if diffs else float("nan")
    high = diffs[int(0.975 * len(diffs)) - 1] if diffs else float("nan")
    return {
        "coppie": len(pairs),
        "casi": len(cases),
        "fallimenti_A": sum(fail_a),
        "fallimenti_B": sum(fail_b),
        "solo_A_fallisce": only_a,
        "solo_B_fallisce": only_b,
        "p_mcnemar_esatto": round(binom_two_sided(only_a, only_a + only_b), 4),
        "diff_tasso_fallimento_B_meno_A": round(mean(fail_b) - mean(fail_a), 3) if pairs else None,
        "ic95_bootstrap_per_caso": (round(low, 3), round(high, 3)),
    }


CONTROL_OK_RE = re.compile(r"Controllo:?[^\n]*(?:\n[^\n]*){0,12}", re.IGNORECASE)


def control_claims_ok(output: str) -> bool | None:
    match = CONTROL_OK_RE.search(output)
    if not match:
        return None
    block = match.group(0).lower()
    if re.search(r"\b(no|violat|problema|da correggere|non superat)\b", block) and not re.search(r"\bnessun", block):
        return False
    return True


def summarize(records: list[dict[str, Any]]) -> str:
    lines = ["| Braccio | Modello | Output | Superati | Tasso | Tasso senza errori di formato | Token medi | Costo | Rapporto lunghezza (mediana) | Gulpease dopo (mediana) |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(record["arm"], record["model"])].append(record)
    for (arm, model), rows in sorted(groups.items()):
        passed = sum(r["evaluation"]["passed"] for r in rows)
        substance = sum(
            all(kind_of(f) == "formato" for f in r["evaluation"]["fatal_failures"]) for r in rows
        )
        tokens = mean(r["usage"]["prompt_tokens"] + r["usage"]["completion_tokens"] for r in rows)
        cost = sum(r["usage"]["cost"] for r in rows)
        ratios = [r["evaluation"]["metrics"].get("length_ratio") for r in rows if r["evaluation"]["metrics"].get("length_ratio")]
        gulp = [r["evaluation"]["metrics"].get("after", {}).get("gulpease") for r in rows]
        gulp = [g for g in gulp if g is not None]
        lines.append(
            f"| {arm} | {model.split('/')[-1]} | {len(rows)} | {passed} | {passed / len(rows):.0%} | {substance / len(rows):.0%} | {tokens:,.0f} | ${cost:.3f} | "
            f"{median(ratios):.2f} | {round(median(gulp), 1) if gulp else '-'} |"
        )
    return "\n".join(lines)


def failure_table(records: list[dict[str, Any]]) -> str:
    counts: dict[str, Counter] = defaultdict(Counter)
    for record in records:
        for failure in record["evaluation"]["fatal_failures"]:
            counts[record["arm"]][kind_of(failure)] += 1
    kinds = sorted({kind for counter in counts.values() for kind in counter})
    arms = sorted(counts)
    lines = ["| Tipo di errore | " + " | ".join(arms) + " |", "|---|" + "---:|" * len(arms)]
    for kind in kinds:
        lines.append(f"| {kind} | " + " | ".join(str(counts[arm][kind]) for arm in arms) + " |")
    return "\n".join(lines)


def routing_table(records: list[dict[str, Any]]) -> str:
    lines = ["| Braccio | Modello | Reference attesi aperti | Nessun reference | Media file letti |", "|---|---|---:|---:|---:|"]
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(record["arm"], record["model"])].append(record)
    for (arm, model), rows in sorted(groups.items()):
        expected_ok = sum(1 for r in rows if r.get("expected_references") and set(r["expected_references"]) <= set(r["files_read"]))
        none = sum(1 for r in rows if not r["files_read"])
        lines.append(
            f"| {arm} | {model.split('/')[-1]} | {expected_ok}/{len(rows)} | {none} | {mean(len(r['files_read']) for r in rows):.1f} |"
        )
    return "\n".join(lines)


def control_honesty(records: list[dict[str, Any]]) -> str:
    lines = ["| Braccio | Modello | Output con Controllo | Controllo 'ok' ma harness KO |", "|---|---|---:|---:|"]
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(record["arm"], record["model"])].append(record)
    for (arm, model), rows in sorted(groups.items()):
        claims = [(control_claims_ok(r["output"]), r["evaluation"]["passed"]) for r in rows]
        with_control = [c for c in claims if c[0] is not None]
        false_ok = sum(1 for claim, passed in with_control if claim and not passed)
        lines.append(f"| {arm} | {model.split('/')[-1]} | {len(with_control)} | {false_ok} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-dir", type=Path, required=True, action="append")
    parser.add_argument("--compare", nargs=2, metavar=("A", "B"), action="append", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    records = [record for run_dir in args.run_dir for record in load_records(run_dir)]
    print(f"## Riepilogo ({len(records)} output)\n")
    print(summarize(records))
    print("\n## Errori per tipo\n")
    print(failure_table(records))
    print("\n## Routing dei reference\n")
    print(routing_table(records))
    print("\n## Onesta' del Controllo\n")
    print(control_honesty(records))

    by_arm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_arm[record["arm"]].append(record)

    print("\n## Test A/A (campione 1 contro campione 2, stessa versione)\n")
    for arm, rows in sorted(by_arm.items()):
        s1 = [dict(r, sample=0) for r in rows if r["sample"] == 1]
        s2 = [dict(r, sample=0) for r in rows if r["sample"] == 2]
        if s1 and s2:
            print(f"- {arm}: {json.dumps(compare(paired(s1, s2)), ensure_ascii=False)}")

    for arm_a, arm_b in args.compare:
        print(f"\n## Confronto appaiato: A = {arm_a}, B = {arm_b}\n")
        models = sorted({r["model"] for r in by_arm.get(arm_a, [])} & {r["model"] for r in by_arm.get(arm_b, [])})
        overall = paired(by_arm.get(arm_a, []), by_arm.get(arm_b, []))
        for model in models:
            subset = [(a, b) for a, b in overall if a["model"] == model]
            print(f"- {model}: {json.dumps(compare(subset), ensure_ascii=False)}")
        print(f"- aggregato: {json.dumps(compare(overall), ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
