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


def load_clarity_eval():
    spec = importlib.util.spec_from_file_location("clarity_eval", TEST_DIR / "clarity_eval.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
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
        for marker in ("PRIMA/DOPO", "Motivo"):
            self.assertIn(marker, self.skill_text)
        self.assertRegex(self.skill_text, r"sommario\s+sintetico")
        for reference in (
            "references/principi-garner.md",
            "references/esempi-atti-giudiziari.md",
            "references/interpretazione-civilistica.md",
        ):
            self.assertIn(reference, self.skill_text)

    def test_cases_schema_is_valid(self) -> None:
        errors = self.eval.validate_cases(self.cases, repo_root=SKILL_ROOT)
        self.assertEqual(errors, [])

    def test_initial_dataset_size(self) -> None:
        self.assertGreaterEqual(len(self.cases), 10)
        self.assertLessEqual(len(self.cases), 12)

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

    def test_ambiguous_cases_remain_flagged(self) -> None:
        ambiguous = [case for case in self.cases if case["adjudication_status"] == "ambiguous"]
        self.assertGreaterEqual(len(ambiguous), 1)
        for case in ambiguous:
            self.assertIn("ambig", case["validation_rationale"].lower())

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

    def test_required_references_exist(self) -> None:
        for case in self.cases:
            for reference in case["required_reference"]:
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

    def test_eval_harness_keeps_format_fail_separate_from_do_content(self) -> None:
        case = self.cases[0]
        output = (
            f"**PRIMA**\n{case['input_text']}\n\n"
            f"**DOPO**\n{case['acceptable_rewrites'][0]['text']}\n\n"
            "**Motivo**\n"
            "Elimina le formule massima diligenza e qualsiasi danno."
        )
        result = self.eval.evaluate_output(case, output)
        self.assertFalse(result.passed)
        self.assertTrue(any("Formato obbligatorio mancante" in item for item in result.fatal_failures))
        self.assertFalse(any("Espressione vietata nel DOPO" in item for item in result.fatal_failures))

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

    def test_skill_archive_contains_installable_skill_files(self) -> None:
        self.assertTrue(ARCHIVE.exists())
        with zipfile.ZipFile(ARCHIVE) as archive:
            names = set(archive.namelist())
        required = {
            "migliora-chiarezza-testi-legali/SKILL.md",
            "migliora-chiarezza-testi-legali/agents/openai.yaml",
            "migliora-chiarezza-testi-legali/references/principi-garner.md",
            "migliora-chiarezza-testi-legali/references/esempi-atti-giudiziari.md",
            "migliora-chiarezza-testi-legali/references/interpretazione-civilistica.md",
        }
        self.assertTrue(required <= names)


if __name__ == "__main__":
    unittest.main(verbosity=2)
