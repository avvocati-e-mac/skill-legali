#!/usr/bin/env python3
"""
Analisi A6 (contaminazione self-preference V1) + A3 (varianza tra run) + RT10 (Nemotron/verbosity).
Importa alpha da metrics.py (validato). Riproducibile.
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import metrics
from collections import Counter, defaultdict

HERE = os.path.dirname(__file__)
RAW_A6 = os.path.join(HERE, "raw_a6")
RAW_P = os.path.join(HERE, "..", "perplexity_raw")
MODELS = ["GPT-5.4", "Gemini 3.1 Pro", "Kimi K2.6", "Nemotron 3 Super"]
QIDS = ["T01", "T03", "T04", "T06", "T07"]
RUNS = [1, 2]

# Claude V1 su query non contestabili: tutto True (vedi blind_pplx/evaluation.md).
def claude_v1(qid, side, crit):
    return True

# Lunghezza risposta per (qid, sistema) — per verbosity bias. Mappa A/B da _KEY.md.
KEY = {"T01": ("Perplexity", "SearXNG"), "T03": ("SearXNG", "Perplexity"),
       "T04": ("Perplexity", "SearXNG"), "T06": ("SearXNG", "Perplexity"),
       "T07": ("Perplexity", "SearXNG")}
# chars risposta: Perplexity dal raw; SearXNG sintesi breve (~250-400) → uso valori misurati.
PPLX_LEN = {q: len(json.load(open(os.path.join(RAW_P, q + ".json")))["answer"]) for q in QIDS}
SX_LEN = {"T01": 70, "T03": 330, "T04": 250, "T06": 280, "T07": 90}  # sintesi concise


def side_len(qid, side):
    sysname = KEY[qid][0 if side == "A" else 1]
    return PPLX_LEN[qid] if sysname == "Perplexity" else SX_LEN[qid]


def parse_judge(ans):
    m = re.search(r'\{.*"A".*"B".*\}', ans or "", re.DOTALL)
    if not m:
        return None
    txt = m.group(0)
    depth = 0; end = None
    for i, ch in enumerate(txt):
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: end = i + 1; break
    try:
        return json.loads(txt[:end])
    except Exception:
        try:
            return json.loads(txt[:end].replace("True", "true").replace("False", "false"))
        except Exception:
            return None


# Carica: ratings[(qid,run,side,crit)][rater] = bool
ratings = defaultdict(dict)
parse_fail = []
for run in RUNS:
    for qid in QIDS:
        path = os.path.join(RAW_A6, f"{qid}_r{run}.json")
        if not os.path.exists(path):
            continue
        d = json.load(open(path))
        for r in d["individual_results"]:
            model = r["model"]; j = parse_judge(r.get("answer"))
            if j is None:
                parse_fail.append((qid, run, model)); continue
            for side in ("A", "B"):
                for crit, val in j.get(side, {}).items():
                    ratings[(qid, run, side, crit)][model] = bool(val)

# ---- A6: contaminazione self-preference. Confronto maggioranza-esterni vs Claude(=True) ----
print("=== A6: celle dove la MAGGIORANZA dei 4 esterni DISSENTE da Claude (che aveva detto True) ===")
contaminated = 0; total_cells = 0
for (qid, run, side, crit), d in sorted(ratings.items()):
    if run != 1:  # conta contaminazione sul run 1 (V1-equivalente)
        continue
    ext = [d[m] for m in MODELS if m in d]
    if not ext:
        continue
    total_cells += 1
    maj = metrics.majority(ext)
    if maj is False:  # esterni dicono False, Claude diceva True
        contaminated += 1
        sysname = KEY[qid][0 if side == "A" else 1]
        print(f"  {qid} {side}({sysname}) {crit}: esterni={d}  Claude=True -> CONTAMINATA")
print(f"  Celle contaminate: {contaminated}/{total_cells} "
      f"({100*contaminated/total_cells:.0f}%) sulle query non contestabili")

# ---- A3: stabilità tra run (varianza) ----
print("\n=== A3: stabilità tra i 2 run (stesso prompt, stessi modelli) ===")
flips = 0; comparable = 0
for qid in QIDS:
    for side in ("A", "B"):
        for crit_set in [set(k[3] for k in ratings if k[0] == qid)]:
            for crit in crit_set:
                for m in MODELS:
                    v1 = ratings.get((qid, 1, side, crit), {}).get(m)
                    v2 = ratings.get((qid, 2, side, crit), {}).get(m)
                    if v1 is not None and v2 is not None:
                        comparable += 1
                        if v1 != v2: flips += 1
print(f"  Voti che cambiano tra run 1 e run 2: {flips}/{comparable} "
      f"({100*flips/comparable:.0f}% instabilità)" if comparable else "  n/d")

# ---- RT10: outlier rate + verbosity bias per giudice ----
print("\n=== RT10: tasso di minoranza (outlier) e verbosity bias per giudice ===")
minority = Counter(); appearances = Counter()
# verbosity: per ogni giudice, frazione di voti True dati alla risposta PIU' LUNGA vs PIU' CORTA
longer_true = Counter(); longer_tot = Counter()
for (qid, run, side, crit), d in ratings.items():
    votes = [d[m] for m in MODELS if m in d]
    if len(votes) < 2:
        continue
    maj = metrics.majority(votes)
    for m in MODELS:
        if m in d:
            appearances[m] += 1
            if maj is not None and d[m] != maj:
                minority[m] += 1
    # verbosity: confronta A vs B per lunghezza
    la, lb = side_len(qid, "A"), side_len(qid, "B")
    longer = "A" if la > lb else "B"
    if side == longer:
        for m in MODELS:
            if m in d:
                longer_tot[m] += 1
                if d[m]: longer_true[m] += 1
print(f"  {'giudice':18} {'%minoranza':>11} {'%True_su_lungo':>15}")
for m in MODELS:
    mr = 100*minority[m]/appearances[m] if appearances[m] else 0
    vr = 100*longer_true[m]/longer_tot[m] if longer_tot[m] else 0
    print(f"  {m:18} {mr:10.0f}% {vr:14.0f}%")

if parse_fail:
    print("\nPARSE FAIL:", parse_fail)
else:
    print("\n0 parse-fail.")
