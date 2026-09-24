#!/usr/bin/env python3
"""Test statici per la skill migliora-chiarezza-testi-legali."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
import zipfile
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
SKILL_ROOT = TEST_DIR.parent
INNER_SKILL = SKILL_ROOT / "migliora-chiarezza-testi-legali"
SKILL_MD = INNER_SKILL / "SKILL.md"
CASES_JSON = TEST_DIR / "cases.json"
RUBRIC_MD = TEST_DIR / "rubric.md"
RED_TEAM_MD = TEST_DIR / "red_team.md"
ARCHIVE = SKILL_ROOT / "migliora-chiarezza-testi-legali.skill"
HOLDOUT_JSON = TEST_DIR / "holdout.json"


def distributed_files() -> list[Path]:
    return sorted(
        path for path in INNER_SKILL.rglob("*")
        if path.is_file() and path.name != ".DS_Store" and "__pycache__" not in path.parts
    )


def six_grams(text: str) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-zà-ÿ0-9]+", text.lower())
    return {tuple(words[i:i + 6]) for i in range(len(words) - 5)}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_clarity_eval():
    spec = importlib.util.spec_from_file_location("clarity_eval", TEST_DIR / "clarity_eval.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_review_app():
    spec = importlib.util.spec_from_file_location("review_app", TEST_DIR / "review_app.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules.setdefault("clarity_eval", load_clarity_eval())
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise AssertionError("SKILL.md deve iniziare con frontmatter YAML.")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise AssertionError("Frontmatter YAML non chiuso.")
    lines = text[4:end].splitlines()
    data: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if ":" not in line:
            raise AssertionError(f"Linea frontmatter non valida: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == ">":
            folded: list[str] = []
            index += 1
            while index < len(lines) and (lines[index].startswith(" ") or not lines[index].strip()):
                if lines[index].strip():
                    folded.append(lines[index].strip())
                index += 1
            data[key] = " ".join(folded)
            continue
        data[key] = value.strip('"')
        index += 1
    return data


class SkillStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.eval = load_clarity_eval()
        cls.cases = cls.eval.load_cases(CASES_JSON)
        cls.skill_text = SKILL_MD.read_text(encoding="utf-8")
        cls.rubric = RUBRIC_MD.read_text(encoding="utf-8")
        cls.red_team = RED_TEAM_MD.read_text(encoding="utf-8")

    def test_frontmatter_description_is_valid_for_cowork(self) -> None:
        meta = frontmatter(self.skill_text)
        self.assertEqual(meta["name"], "migliora-chiarezza-testi-legali")
        self.assertLessEqual(len(meta["description"]), 1024)
        self.assertIn("MANDATORY TRIGGERS", meta["description"])

    def test_skill_keeps_required_output_contract(self) -> None:
        for marker in ("PRIMA:", "DOPO:", "Motivo:", "TESTO RISCRITTO:", "Sommario:", "PROPOSTA:"):
            self.assertIn(marker, self.skill_text)
        for reference in (
            "references/atti-e-pareri.md",
            "references/contratti.md",
            "references/interpretazione-civilistica.md",
        ):
            self.assertIn(reference, self.skill_text)

    def test_skill_body_is_short_enough_for_small_models(self) -> None:
        body = self.skill_text.split("---", 2)[2]
        words = re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:'[A-Za-zÀ-ÿ0-9]+)*", body)
        self.assertLessEqual(len(words), 1000)

    def test_procedure_starts_by_asking_whether_changes_are_needed(self) -> None:
        # v2.2: Scheda e Controllo scritti dal modello sono stati tolti perche' sul set
        # DEV non miglioravano la fedelta' (vedi REPORT). Resta il primo passo contro
        # la sovra-modifica e la verifica con lo script, che e' un controllo esterno.
        procedure = self.skill_text.split("## 2. Procedura", 1)[1].split("## 3.", 1)[0]
        self.assertIn("Nessuna modifica necessaria", procedure)
        self.assertIn("scripts/controlla_invarianti.py", procedure)
        self.assertNotIn("Scheda", procedure)

    def test_distributed_files_have_no_em_dash_and_no_research(self) -> None:
        self.assertFalse((INNER_SKILL / "research").exists())
        for path in distributed_files():
            text = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name):
                self.assertNotIn("\u2014", text)
                self.assertIsNone(re.search(r"research/[\w-]+\.md", text))

    def test_references_cited_in_skill_exist(self) -> None:
        for reference in set(re.findall(r"references/[\w-]+\.md", self.skill_text)):
            with self.subTest(reference=reference):
                self.assertTrue((INNER_SKILL / reference).exists())

    def test_no_six_word_overlap_between_cases_and_skill(self) -> None:
        skill_grams: set[tuple[str, ...]] = set()
        for path in distributed_files():
            skill_grams |= six_grams(path.read_text(encoding="utf-8"))
        for case in self.eval.load_cases(CASES_JSON):
            overlap = six_grams(case["input_text"]) & skill_grams
            with self.subTest(case=case["id"]):
                self.assertFalse(overlap, f"{case['id']} ricalca la skill: {sorted(overlap)[:2]}")
        # Holdout: scritto da un altro modello senza vedere la skill. Una o due
        # sequenze comuni sono formule forensi condivise, non copia; tre o piu'
        # indicano un passo ricalcato. Il contenuto del holdout non si stampa.
        if HOLDOUT_JSON.exists():
            for case in self.eval.load_cases(HOLDOUT_JSON):
                overlap = six_grams(case["input_text"]) & skill_grams
                with self.subTest(case=case["id"]):
                    self.assertLess(len(overlap), 3, f"{case['id']}: {len(overlap)} sequenze in comune con la skill")

    def test_invariant_script_flags_added_exemption(self) -> None:
        script = load_module("controlla_invarianti", INNER_SKILL / "scripts" / "controlla_invarianti.py")
        warnings = script.controlla(
            "Il Conduttore risponde di ogni danno.",
            "Il Conduttore risponde di ogni danno, salvo caso fortuito o forza maggiore.",
        )
        self.assertTrue(any("esimente" in warning for warning in warnings))
        self.assertEqual(script.controlla("Il Venditore garantisce la conformità.", "Il Venditore garantisce la conformità."), [])

    def test_cases_schema_is_valid(self) -> None:
        errors = self.eval.validate_cases(self.cases, repo_root=SKILL_ROOT)
        self.assertEqual(errors, [])

    def test_dataset_size(self) -> None:
        self.assertGreaterEqual(len(self.cases), 12)

    def test_no_codex_only_gold_cases(self) -> None:
        for case in self.cases:
            if case["adjudication_status"] != "gold":
                continue
            annotations = case.get("annotations", {})
            reviewed = {
                name
                for name, payload in annotations.items()
                if isinstance(payload, dict) and payload.get("status") not in {"not_run", "pending", "", None}
            }
            self.assertFalse(reviewed <= {"codex"}, case["id"])

    def test_non_automatic_cases_remain_flagged(self) -> None:
        non_automatic = [
            case
            for case in self.cases
            if case["adjudication_status"] in {"ambiguous", "expert_review_only"}
        ]
        self.assertGreaterEqual(len(non_automatic), 1)
        for case in non_automatic:
            rationale = case["validation_rationale"].lower()
            self.assertTrue(
                "ambig" in rationale
                or case["annotations"]["human"]["status"] == "reviewed",
                case["id"],
            )

    def test_every_packet_has_required_annotations(self) -> None:
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["legal_invariants"])
                self.assertTrue(case["forbidden_changes"])
                self.assertTrue(case["expected_issues"])
                self.assertTrue(case["validation_rationale"])
                self.assertIn("codex", case["annotations"])
                self.assertIn("human", case["annotations"])
                self.assertIn("opus", case["annotations"])

    def test_expected_v2_references_exist(self) -> None:
        for case in self.cases:
            for reference in case["expected_references_v2"]:
                with self.subTest(case=case["id"], reference=reference):
                    self.assertTrue((INNER_SKILL / reference).exists())

    def test_rubric_uses_eight_criteria_and_0_3_scale(self) -> None:
        headings = re.findall(r"^###\s+\d+\.", self.rubric, flags=re.MULTILINE)
        self.assertEqual(len(headings), 8)
        for score in ("0:", "1:", "2:", "3:"):
            self.assertIn(score, self.rubric)
        self.assertIn("Cancelli di esclusione", self.rubric)

    def test_red_team_bias_controls_are_documented(self) -> None:
        required = (
            "position bias",
            "verbosity bias",
            "ordine invertito",
            "claude --model opus",
            "Nessun caso puo' diventare `gold`",
        )
        for text in required:
            self.assertIn(text, self.red_team)

    def test_eval_harness_format_gate(self) -> None:
        case = self.cases[0]
        bad = "Testo riscritto senza struttura."
        bad_result = self.eval.evaluate_output(case, bad)
        self.assertFalse(bad_result.passed)
        self.assertTrue(any("PRIMA" in item for item in bad_result.fatal_failures))

        rewrite = case["acceptable_rewrites"][0]["text"]
        good = f"PRIMA: {case['input_text']}\nDOPO: {rewrite}\nMotivo: riduce lo standard vago e preserva soggetti e responsabilita'."
        good_result = self.eval.evaluate_output(case, good)
        self.assertTrue(good_result.passed, good_result.as_dict())

    def test_eval_harness_scopes_do_block_with_markdown_colon_headings(self) -> None:
        case = next(case for case in self.cases if case["id"] == "C006")
        output = (
            f"**PRIMA:**\n{case['input_text']}\n\n"
            "**DOPO:**\n"
            "La controparte eccepisce la prescrizione del diritto azionato, poiche' e' decorso il termine decennale.\n\n"
            "**Motivo:**\n"
            "La forma passiva viene sostituita dalla forma attiva; la formula essendo decorso viene resa esplicita."
        )
        result = self.eval.evaluate_output(case, output)
        self.assertTrue(result.passed, result.as_dict())

    def test_eval_harness_accepts_markdown_headings_without_colon(self) -> None:
        # Da settembre 2026 il formato conta come intestazione riconosciuta, non come
        # stringa esatta: "**PRIMA**" su una riga vale quanto "PRIMA:". Le formule
        # citate nel Motivo non contano come formule rimaste nel DOPO.
        case = self.cases[0]
        output = (
            f"**PRIMA**\n{case['input_text']}\n\n"
            f"**DOPO**\n{case['acceptable_rewrites'][0]['text']}\n\n"
            "**Motivo**\n"
            "Elimina le formule massima diligenza e qualsiasi danno."
        )
        result = self.eval.evaluate_output(case, output)
        self.assertFalse(any("Formato obbligatorio mancante" in item for item in result.fatal_failures))
        self.assertFalse(any("Espressione vietata nel DOPO" in item for item in result.fatal_failures))

    def test_eval_harness_treats_no_reply_synonyms_as_same_fact(self) -> None:
        # Prova Codex 2026-09: "senza riscontro" al posto di "senza risposta alcuna"
        # non e' un fatto inventato; "invano" su un testo che non lo diceva si'.
        before = "Il secondo sollecito e' rimasto senza risposta alcuna."
        self.assertEqual(
            self.eval.delta_additions(self.eval.INTENSIFIER_PATTERNS, before, "Il secondo sollecito e' rimasto senza riscontro."),
            [],
        )
        self.assertEqual(
            self.eval.delta_additions(self.eval.INTENSIFIER_PATTERNS, "Ho inviato un sollecito.", "Ho inviato un sollecito, rimasto senza risposta."),
            ["senza riscontro"],
        )

    def test_eval_harness_catches_c004_result_obligation_regression(self) -> None:
        case = next(case for case in self.cases if case["id"] == "C004")
        output = (
            f"PRIMA: {case['input_text']}\n"
            "DOPO: Il prestatore deve rendere il sistema funzionante entro il termine concordato per iscritto tra le parti.\n"
            "Motivo: elimina lo standard vago e chiarisce l'obbligo in termini verificabili."
        )
        result = self.eval.evaluate_output(case, output)
        self.assertFalse(result.passed)
        self.assertTrue(any("scelta mezzi/risultato" in item for item in result.fatal_failures))

    def test_ab_prompt_supports_inverted_order(self) -> None:
        case = self.cases[0]
        first = "output originale"
        second = "output alternativo"
        prompt_ab = self.eval.build_ab_prompt(case, first, second, "AB")
        prompt_ba = self.eval.build_ab_prompt(case, first, second, "BA")
        self.assertIn("OUTPUT A:\noutput originale", prompt_ab)
        self.assertIn("OUTPUT A:\noutput alternativo", prompt_ba)

    def test_review_app_builds_review_payload_without_raw_outputs(self) -> None:
        review_app = load_review_app()
        payload = review_app.build_review_data(raw_dir=TEST_DIR / "missing-raw-dir")
        self.assertEqual(len(payload["cases"]), len(self.cases))
        self.assertIn("opus", payload["outputs"]["C001"])
        self.assertFalse(payload["outputs"]["C001"]["opus"]["available"])
        self.assertEqual(payload["outputs"]["C001"]["opus"]["automatic_check"]["case_id"], "C001")

    def test_review_app_save_and_load_reviews(self) -> None:
        review_app = load_review_app()
        review_path = TEST_DIR / "__tmp_human_reviews.json"
        self.addCleanup(lambda: review_path.unlink(missing_ok=True))
        saved = review_app.save_reviews(
            {
                "reviews": {
                    "C002": {
                        "final_status": "ambiguous",
                        "notes": "Da verificare con fascicolo.",
                        "models": {"opus": {"legal_meaning": "ok"}},
                    }
                }
            },
            review_path,
        )
        loaded = review_app.load_reviews(review_path)
        self.assertEqual(saved["reviews"], loaded["reviews"])
        self.assertEqual(loaded["reviews"]["C002"]["final_status"], "ambiguous")

    def test_skill_archive_matches_source(self) -> None:
        self.assertTrue(ARCHIVE.exists())
        with zipfile.ZipFile(ARCHIVE) as archive:
            names = {name for name in archive.namelist() if not name.endswith("/")}
            for path in distributed_files():
                name = "migliora-chiarezza-testi-legali/" + path.relative_to(INNER_SKILL).as_posix()
                with self.subTest(file=name):
                    self.assertIn(name, names)
                    self.assertEqual(archive.read(name), path.read_bytes())
        self.assertFalse(any("/research/" in name for name in names))


if __name__ == "__main__":
    unittest.main(verbosity=2)
