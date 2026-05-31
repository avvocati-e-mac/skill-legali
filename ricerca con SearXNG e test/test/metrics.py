#!/usr/bin/env python3
"""
metrics.py — funzioni statistiche pure per il benchmark (logica separata dai dati).

Niente dipendenze esterne (numpy/scipy/sklearn NON disponibili in questo ambiente → implementazioni
a mano, ma VALIDATE con known-answer test in test_compute.py).

Convenzioni dichiarate (best practice: documentare quando esistono più definizioni):
- Krippendorff's alpha: variante NOMINALE (binaria), metrica di disaccordo δ²=0 se uguale, 1 se diverso.
  Do = (Σ_{c≠k} o_ck) / n ;  De = (n² − Σ_c n_c²) / (n(n−1)) ;  alpha = 1 − Do/De.
  Coincidence matrix o costruita con peso 1/(m−1) per coppia ordinata entro un'unità con m valutatori
  (Krippendorff 2011). Unità con <2 valutatori escluse. Ref: Krippendorff "Computing Krippendorff's
  Alpha-Reliability" (2011); en.wikipedia.org/wiki/Krippendorff%27s_alpha.
  NOTA: validata indipendentemente con DUE implementazioni che concordano (vedi test_compute.py).
  Il valore atteso del caso canonico è 0.6914 (calcolato deterministicamente, NON da LLM).
- nDCG@k: Järvelin & Kekäläinen (2002). DCG = Σ rel_i / log2(i+2); nDCG = DCG / IDCG, IDCG = DCG
  dell'ordinamento ideale del pool. rel graduata 0..3.
"""
import itertools
import math
from collections import Counter


def _coincidence(units):
    """Costruisce la coincidence matrix (Counter su coppie ordinate) da unità {rater: value}."""
    o = Counter()
    for u in units:
        rs = list(u.values())
        m = len(rs)
        if m < 2:
            continue
        for a, b in itertools.permutations(rs, 2):
            o[(a, b)] += 1.0 / (m - 1)
    return o


def krippendorff_alpha_nominal(units):
    """
    Krippendorff's alpha nominale per dati con valutatori mancanti.
    units: lista di dict {rater_id: categoria}. Ritorna float, o None se non calcolabile.
    """
    o = _coincidence(units)
    if not o:
        return None
    cats = sorted({k[0] for k in o} | {k[1] for k in o})
    n_c = {v: sum(o.get((v, w), 0) for w in cats) for v in cats}
    n = sum(n_c.values())
    if n < 2:
        return None
    Do = sum(o.get((a, b), 0) for a in cats for b in cats if a != b)  # = Σ off-diagonal (numeratore, /n implicito)
    sum_nc2 = sum(n_c[v] ** 2 for v in cats)
    De = (n * n - sum_nc2) / (n - 1)  # nota: Do qui è "conteggio" non /n; il /n di Do e l'1/n di De si elidono
    if De == 0:
        return 1.0  # nessun disaccordo atteso (una sola categoria) → accordo perfetto per convenzione
    return 1.0 - Do / De


def dcg(rels):
    """Discounted Cumulative Gain (Järvelin & Kekäläinen 2002)."""
    return sum(r / math.log2(i + 2) for i, r in enumerate(rels))


def ndcg(ranked_rels, pool_rels, k=10):
    """nDCG@k: ranking osservato vs ordinamento ideale del pool."""
    d = dcg(ranked_rels[:k])
    ideal = dcg(sorted(pool_rels, reverse=True)[:k])
    return d / ideal if ideal else 0.0


def majority(values, tie=None):
    """Voto di maggioranza su una lista di booleani. tie = valore se parità (default None)."""
    c = Counter(values)
    if not c:
        return None
    top = c.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return tie
    return top[0][0]
