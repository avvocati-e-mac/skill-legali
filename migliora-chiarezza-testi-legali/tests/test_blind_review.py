#!/usr/bin/env python3
"""Test per blind_review.py (revisione umana cieca A/B).

Tutti i test lavorano in cartelle temporanee: non scrivono mai dentro
tests/blind/ ne' altrove nel repository.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

import blind_review  # noqa: E402


CASES_JSON = TEST_DIR / "cases.json"
FAKE_MODEL = "faux-model-glm52"
ARM_A = "chiarezza-vTEST__completa"
ARM_B = "working-vTEST__completa"
TEST_CASE_IDS = ("C001", "C002", "C003")


# Uno "stile" fittizio per braccio: un vero output di modello non conosce ne'
# scrive mai il nome del braccio o della versione della skill che lo ha
# prodotto, quindi qui differenziamo il testo dei due bracci senza incorporare
# le stringhe ARM_A/ARM_B (la pulizia di blind_review non e' pensata per
# scovare stringhe arbitrarie: verifichiamo solo che i campi strutturati -
# arm/model - non compaiano, non un'euristica sul testo libero).
ARM_STYLES = {"stile-diretto": ARM_A, "stile-articolato": ARM_B}


def make_output(case_id: str, style: str) -> str:
    """Testo di output plausibile, con sezioni Scheda:/Controllo: e un
    riferimento a un file della skill dentro il Motivo, cosi' i test possono
    verificare che entrambi i meccanismi di pulizia funzionino."""
    return (
        f"PRIMA: testo originale del caso {case_id}.\n"
        f"DOPO: versione riscritta in {style} del caso {case_id}, piu' chiara.\n"
        "Motivo: frase spezzata e resa attiva, come indicato in "
        "references/principi-garner.md.\n\n"
        "Scheda: dati interni di elaborazione, punteggio 9/10, non per l'avvocato.\n\n"
        "Controllo: verificato secondo le istruzioni di SKILL.md, ho aperto "
        "references/interpretazione-civilistica.md e concludo che il controllo e' superato.\n\n"
        "Sommario: eliminata la subordinata annidata e reso esplicito il soggetto."
    )


def build_fake_run_dir(root: Path) -> Path:
    """Crea root/run/dev/<arm>/<model>/<CASE>__s1.json per due bracci e tre casi."""
    run_dir = root / "run" / "dev"
    for style, arm in ARM_STYLES.items():
        model_dir = run_dir / arm / FAKE_MODEL
        model_dir.mkdir(parents=True, exist_ok=True)
        for case_id in TEST_CASE_IDS:
            payload = {
                "case_id": case_id,
                "output": make_output(case_id, style),
            }
            (model_dir / f"{case_id}__s1.json").write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
    return run_dir


class CleanOutputTests(unittest.TestCase):
    def test_strips_scheda_and_controllo_sections_and_file_names(self) -> None:
        raw = make_output("C001", ARM_A)
        cleaned = blind_review.clean_output(raw)

        self.assertNotIn("Scheda:", cleaned)
        self.assertNotIn("Controllo:", cleaned)
        self.assertNotIn("references/", cleaned)
        self.assertNotIn("SKILL.md", cleaned)
        self.assertNotIn("9/10", cleaned)
        self.assertNotIn("punteggio", cleaned.lower())

        # Il resto del contenuto deve restare.
        self.assertIn("PRIMA:", cleaned)
        self.assertIn("DOPO:", cleaned)
        self.assertIn("Motivo:", cleaned)
        self.assertIn("Sommario:", cleaned)
        self.assertIn("eliminata la subordinata annidata", cleaned)

    def test_case_insensitive_and_bold_headers(self) -> None:
        raw = (
            "**DOPO:** testo pulito.\n\n"
            "**controllo:** nota interna da nascondere.\n\n"
            "**Sommario:** fine."
        )
        cleaned = blind_review.clean_output(raw)
        self.assertIn("testo pulito", cleaned)
        self.assertNotIn("nota interna", cleaned)
        self.assertIn("fine", cleaned)


class BuildBlindPairsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.run_dir = build_fake_run_dir(self.root)

    def test_pairs_never_leak_arm_model_or_internal_sections(self) -> None:
        pairs, secret = blind_review.build_blind_pairs(
            run_dirs=[self.run_dir],
            arm_a=ARM_A,
            arm_b=ARM_B,
            n_pairs=2,
            seed=123,
            cases_paths=[CASES_JSON],
        )
        self.assertEqual(len(pairs), 2)
        self.assertEqual(len(secret), 2)

        blob = json.dumps(pairs, ensure_ascii=False)
        for forbidden in (ARM_A, ARM_B, FAKE_MODEL, "Scheda:", "Controllo:", "references/", "SKILL.md"):
            self.assertNotIn(forbidden, blob, f"'{forbidden}' non deve comparire nelle coppie anonime")

        for pair in pairs:
            self.assertEqual(
                set(pair.keys()),
                {"pair_id", "input_text", "context", "testo_1", "testo_2"},
            )
            self.assertTrue(pair["pair_id"].startswith("P"))
            self.assertTrue(pair["testo_1"])
            self.assertTrue(pair["testo_2"])
            self.assertIn("DOPO:", pair["testo_1"])
            self.assertIn("DOPO:", pair["testo_2"])

        # La mappa segreta e' l'unico posto dove compaiono bracci e modello.
        for pair_id, meta in secret.items():
            self.assertEqual(set(meta.keys()), {"arm_testo_1", "arm_testo_2", "model", "case_id", "sample"})
            self.assertEqual({meta["arm_testo_1"], meta["arm_testo_2"]}, {ARM_A, ARM_B})
            self.assertEqual(meta["model"], FAKE_MODEL)
            self.assertIn(meta["case_id"], TEST_CASE_IDS)

    def test_stratifies_one_pair_per_case_when_possible(self) -> None:
        pairs, secret = blind_review.build_blind_pairs(
            run_dirs=[self.run_dir],
            arm_a=ARM_A,
            arm_b=ARM_B,
            n_pairs=3,
            seed=7,
            cases_paths=[CASES_JSON],
        )
        self.assertEqual(len(pairs), 3)
        case_ids = [meta["case_id"] for meta in secret.values()]
        self.assertEqual(sorted(case_ids), sorted(TEST_CASE_IDS))

    def test_caps_at_available_candidates(self) -> None:
        pairs, secret = blind_review.build_blind_pairs(
            run_dirs=[self.run_dir],
            arm_a=ARM_A,
            arm_b=ARM_B,
            n_pairs=10,
            seed=1,
            cases_paths=[CASES_JSON],
        )
        # Un solo modello/campione per caso: al massimo 3 coppie possibili.
        self.assertEqual(len(pairs), 3)

    def test_seeded_randomization_is_reproducible(self) -> None:
        args = dict(
            run_dirs=[self.run_dir],
            arm_a=ARM_A,
            arm_b=ARM_B,
            n_pairs=3,
            seed=999,
            cases_paths=[CASES_JSON],
        )
        pairs_1, secret_1 = blind_review.build_blind_pairs(**args)
        pairs_2, secret_2 = blind_review.build_blind_pairs(**args)
        self.assertEqual(pairs_1, pairs_2)
        self.assertEqual(secret_1, secret_2)

    def test_different_seed_can_change_assignment_or_selection(self) -> None:
        common = dict(
            run_dirs=[self.run_dir],
            arm_a=ARM_A,
            arm_b=ARM_B,
            n_pairs=3,
            cases_paths=[CASES_JSON],
        )
        results = {
            seed: blind_review.build_blind_pairs(seed=seed, **common) for seed in range(10)
        }
        serialized = {seed: json.dumps(secret, sort_keys=True) for seed, (_, secret) in results.items()}
        self.assertGreater(len(set(serialized.values())), 1, "semi diversi dovrebbero poter dare esiti diversi")


class UnblindTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.session_dir = Path(self._tmp.name) / "sessione-test"
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def _write_secret(self, secret: dict) -> None:
        blind_review._write_json(self.session_dir / "mappa_segreta.json", secret)

    def _write_answers(self, answers: dict) -> None:
        blind_review.save_answers({"answers": answers}, self.session_dir)

    def test_computes_per_arm_averages_preferences_and_sign_test(self) -> None:
        secret = {
            "P01": {"arm_testo_1": "armA", "arm_testo_2": "armB", "model": "m", "case_id": "C001", "sample": 1},
            "P02": {"arm_testo_1": "armB", "arm_testo_2": "armA", "model": "m", "case_id": "C002", "sample": 1},
            "P03": {"arm_testo_1": "armA", "arm_testo_2": "armB", "model": "m", "case_id": "C003", "sample": 1},
        }
        self._write_secret(secret)

        def score(fedelta, chiarezza, fluidita, naturalezza, fatti):
            return {
                "fedelta_giuridica": fedelta,
                "chiarezza": chiarezza,
                "fluidita": fluidita,
                "naturalezza": naturalezza,
                "fatti_aggiunti_persi": fatti,
                "fatti_nota": "",
            }

        answers = {
            "P01": {
                "testo_1": score(3, 3, 3, 3, False),  # armA
                "testo_2": score(2, 2, 2, 2, False),  # armB
                "preferenza": "testo_1",  # armA vince
                "nota": "",
            },
            "P02": {
                "testo_1": score(1, 1, 1, 1, True),  # armB
                "testo_2": score(3, 3, 2, 3, False),  # armA
                "preferenza": "testo_2",  # armA vince
                "nota": "",
            },
            "P03": {
                "testo_1": score(2, 3, 3, 2, False),  # armA
                "testo_2": score(1, 2, 2, 1, True),  # armB
                "preferenza": "testo_2",  # armB vince
                "nota": "",
            },
        }
        self._write_answers(answers)

        result = blind_review.unblind(self.session_dir)

        self.assertEqual(result["n_pairs_totali"], 3)
        self.assertEqual(result["n_pairs_con_risposta"], 3)
        self.assertEqual(result["pareggi"], 0)

        arm_a = result["per_arm"]["armA"]
        arm_b = result["per_arm"]["armB"]

        self.assertEqual(arm_a["medie"]["fedelta_giuridica"], round(8 / 3, 2))
        self.assertEqual(arm_a["medie"]["chiarezza"], 3.0)
        self.assertEqual(arm_a["medie"]["fluidita"], round(8 / 3, 2))
        self.assertEqual(arm_a["medie"]["naturalezza"], round(8 / 3, 2))
        self.assertEqual(arm_a["n_valutazioni"], 3)
        self.assertEqual(arm_a["preferenze"], 2)
        self.assertEqual(arm_a["fatti_aggiunti_persi_segnalati"], 0)

        self.assertEqual(arm_b["medie"]["fedelta_giuridica"], round(4 / 3, 2))
        self.assertEqual(arm_b["medie"]["chiarezza"], round(5 / 3, 2))
        self.assertEqual(arm_b["medie"]["fluidita"], round(5 / 3, 2))
        self.assertEqual(arm_b["medie"]["naturalezza"], round(4 / 3, 2))
        self.assertEqual(arm_b["n_valutazioni"], 3)
        self.assertEqual(arm_b["preferenze"], 1)
        self.assertEqual(arm_b["fatti_aggiunti_persi_segnalati"], 2)

        sign_test = result["sign_test"]
        self.assertEqual(sign_test["arm_a"], "armA")
        self.assertEqual(sign_test["arm_b"], "armB")
        self.assertEqual(sign_test["wins_a"], 2)
        self.assertEqual(sign_test["wins_b"], 1)
        self.assertEqual(sign_test["pareggi"], 0)
        self.assertEqual(sign_test["p_value"], 1.0)

    def test_ties_are_excluded_from_sign_test_but_counted(self) -> None:
        secret = {
            "P01": {"arm_testo_1": "armA", "arm_testo_2": "armB", "model": "m", "case_id": "C001", "sample": 1},
        }
        self._write_secret(secret)
        self._write_answers(
            {
                "P01": {
                    "testo_1": {"fedelta_giuridica": 2, "chiarezza": 2, "fluidita": 2, "naturalezza": 2,
                                "fatti_aggiunti_persi": "", "fatti_nota": ""},
                    "testo_2": {"fedelta_giuridica": 2, "chiarezza": 2, "fluidita": 2, "naturalezza": 2,
                                "fatti_aggiunti_persi": "", "fatti_nota": ""},
                    "preferenza": "equivalenti",
                    "nota": "",
                }
            }
        )
        result = blind_review.unblind(self.session_dir)
        self.assertEqual(result["pareggi"], 1)
        self.assertEqual(result["sign_test"]["wins_a"], 0)
        self.assertEqual(result["sign_test"]["wins_b"], 0)
        self.assertEqual(result["sign_test"]["p_value"], 1.0)

    def test_unanswered_pairs_are_ignored(self) -> None:
        secret = {
            "P01": {"arm_testo_1": "armA", "arm_testo_2": "armB", "model": "m", "case_id": "C001", "sample": 1},
            "P02": {"arm_testo_1": "armA", "arm_testo_2": "armB", "model": "m", "case_id": "C002", "sample": 1},
        }
        self._write_secret(secret)
        self._write_answers({})
        result = blind_review.unblind(self.session_dir)
        self.assertEqual(result["n_pairs_totali"], 2)
        self.assertEqual(result["n_pairs_con_risposta"], 0)
        self.assertEqual(result["per_arm"], {})

    def test_markdown_report_mentions_both_arms(self) -> None:
        secret = {
            "P01": {"arm_testo_1": "armA", "arm_testo_2": "armB", "model": "m", "case_id": "C001", "sample": 1},
        }
        self._write_secret(secret)
        self._write_answers(
            {
                "P01": {
                    "testo_1": {"fedelta_giuridica": 3, "chiarezza": 3, "fluidita": 3, "naturalezza": 3,
                                "fatti_aggiunti_persi": False, "fatti_nota": ""},
                    "testo_2": {"fedelta_giuridica": 1, "chiarezza": 1, "fluidita": 1, "naturalezza": 1,
                                "fatti_aggiunti_persi": False, "fatti_nota": ""},
                    "preferenza": "testo_1",
                    "nota": "",
                }
            }
        )
        result = blind_review.unblind(self.session_dir)
        markdown = blind_review.format_markdown(result)
        self.assertIn("armA", markdown)
        self.assertIn("armB", markdown)
        self.assertIn("Test dei segni", markdown)


class ExactSignTestTests(unittest.TestCase):
    def test_no_data_returns_one(self) -> None:
        self.assertEqual(blind_review.exact_sign_test(0, 0), 1.0)

    def test_known_value_for_five_zero_split(self) -> None:
        self.assertAlmostEqual(blind_review.exact_sign_test(5, 0), 0.0625)

    def test_even_split_is_not_significant(self) -> None:
        self.assertEqual(blind_review.exact_sign_test(4, 4), 1.0)


class SessionPathTests(unittest.TestCase):
    def test_rejects_path_traversal_names(self) -> None:
        with self.assertRaises(SystemExit):
            blind_review.session_path("../../etc")
        with self.assertRaises(SystemExit):
            blind_review.session_path("a/b")

    def test_accepts_simple_names(self) -> None:
        path = blind_review.session_path("prova-01")
        self.assertEqual(path, blind_review.BLIND_DIR / "prova-01")


if __name__ == "__main__":
    unittest.main(verbosity=2)
