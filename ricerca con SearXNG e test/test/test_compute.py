#!/usr/bin/env python3
"""
test_compute.py — known-answer + edge-case + property tests per metrics.py.
Eseguire: python3 test_compute.py  (usa unittest, niente dipendenze esterne).

IMPORTANTE: i valori attesi NON provengono da un LLM (inaffidabile su aritmetica) ma da:
- calcolo deterministico esplicito (Krippendorff caso canonico → 0.6914),
- una SECONDA implementazione indipendente come oracolo differenziale,
- valori banali per i casi degeneri.
"""
import itertools
import math
import unittest
from collections import Counter

import metrics


# --- Oracolo differenziale: seconda implementazione indipendente di alpha ---
def alpha_independent(units):
    """Implementazione separata (stile pairwise/coincidence) per cross-check differenziale."""
    o = Counter()
    for u in units:
        rs = list(u.values())
        m = len(rs)
        if m < 2:
            continue
        for a, b in itertools.permutations(rs, 2):
            o[(a, b)] += 1.0 / (m - 1)
    if not o:
        return None
    cats = sorted({k[0] for k in o} | {k[1] for k in o})
    n_c = {v: sum(o.get((v, w), 0) for w in cats) for v in cats}
    n = sum(n_c.values())
    if n < 2:
        return None
    Do_frac = sum(o.get((a, b), 0) for a in cats for b in cats if a != b) / n
    De_frac = (n * n - sum(v * v for v in n_c.values())) / (n * (n - 1))
    return 1 - Do_frac / De_frac if De_frac else 1.0


# Caso canonico Wikipedia (3 coder, unità pairabili). Valore deterministico atteso = 0.69136.
CANONICAL = [
    {'B': 1, 'C': 1}, {'A': 1, 'C': 1}, {'A': 1, 'C': 1}, {'A': 1, 'B': 3},
    {'B': 2, 'C': 2}, {'A': 2, 'C': 2}, {'B': 3, 'C': 3}, {'A': 3, 'B': 3, 'C': 4},
    {'A': 3, 'C': 3}, {'A': 3, 'C': 3}, {'A': 4, 'B': 4, 'C': 4}, {'A': 3, 'C': 4},
]


class TestKrippendorff(unittest.TestCase):
    def test_canonical_known_answer(self):
        # Coincidence matrix canonica: off-diag=6, n=26, Σn_c²=190 → Do/De → 0.69136
        self.assertAlmostEqual(metrics.krippendorff_alpha_nominal(CANONICAL), 0.69136, places=4)

    def test_matches_independent_impl(self):
        # Oracolo differenziale su casi vari
        import random
        random.seed(42)
        for _ in range(100):
            units = [{'a': random.randint(0, 1), 'b': random.randint(0, 1),
                      'c': random.randint(0, 1)} for _ in range(8)]
            a = metrics.krippendorff_alpha_nominal(units)
            b = alpha_independent(units)
            if a is None:
                self.assertIsNone(b)
            else:
                self.assertAlmostEqual(a, b, places=6)

    def test_perfect_agreement(self):
        self.assertAlmostEqual(metrics.krippendorff_alpha_nominal(
            [{'a': 1, 'b': 1}, {'a': 0, 'b': 0}]), 1.0, places=6)

    def test_total_disagreement_negative(self):
        # 2 unità, 2 rater, sempre discordi → alpha < 0
        self.assertLess(metrics.krippendorff_alpha_nominal(
            [{'a': 1, 'b': 0}, {'a': 0, 'b': 1}]), 0)

    def test_single_category_returns_one(self):
        # tutti lo stesso valore → nessun disaccordo atteso → 1.0
        self.assertEqual(metrics.krippendorff_alpha_nominal(
            [{'a': 1, 'b': 1}, {'a': 1, 'b': 1}]), 1.0)

    def test_no_pairable_units_returns_none(self):
        self.assertIsNone(metrics.krippendorff_alpha_nominal([{'a': 1}, {'b': 0}]))

    def test_empty_returns_none(self):
        self.assertIsNone(metrics.krippendorff_alpha_nominal([]))

    def test_bounded(self):
        # property: alpha <= 1 sempre
        import random
        random.seed(1)
        for _ in range(200):
            units = [{'a': random.randint(0, 1), 'b': random.randint(0, 1)} for _ in range(6)]
            a = metrics.krippendorff_alpha_nominal(units)
            if a is not None:
                self.assertLessEqual(a, 1.0 + 1e-9)


class TestNDCG(unittest.TestCase):
    def test_ideal_ranking_is_one(self):
        # ranking già ideale → nDCG = 1
        self.assertAlmostEqual(metrics.ndcg([3, 2, 1], [3, 2, 1]), 1.0, places=6)

    def test_known_value(self):
        # rels=[1,0,1], pool ideale=[1,1,0]. DCG=1/log2(2)+0+1/log2(4)=1+0.5=1.5
        # IDCG=1/log2(2)+1/log2(3)=1+0.6309=1.6309 → nDCG=0.9197
        self.assertAlmostEqual(metrics.ndcg([1, 0, 1], [1, 1, 0]), 1.5 / (1 + 1 / math.log2(3)), places=6)

    def test_worst_ranking_lower_than_best(self):
        best = metrics.ndcg([3, 0], [3, 0])
        worst = metrics.ndcg([0, 3], [3, 0])
        self.assertGreater(best, worst)

    def test_empty_pool(self):
        self.assertEqual(metrics.ndcg([], []), 0.0)


class TestMajority(unittest.TestCase):
    def test_clear_majority(self):
        self.assertEqual(metrics.majority([True, True, False]), True)

    def test_tie_returns_default(self):
        self.assertIsNone(metrics.majority([True, False]))

    def test_unanimous(self):
        self.assertEqual(metrics.majority([False, False, False]), False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
