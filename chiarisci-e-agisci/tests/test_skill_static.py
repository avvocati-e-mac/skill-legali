#!/usr/bin/env python3
"""Test statici e di packaging per chiarisci-e-agisci."""

from __future__ import annotations

import re
import unittest
import zipfile
from pathlib import Path

from eval_skill import ALL_REFERENCES, load_cases, validate_cases


TEST_DIR = Path(__file__).resolve().parent
OUTER_ROOT = TEST_DIR.parent
INNER_SKILL = OUTER_ROOT / "chiarisci-e-agisci"
SKILL_MD = INNER_SKILL / "SKILL.md"
ARCHIVE = OUTER_ROOT / "chiarisci-e-agisci.skill"


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
        key, value = line.split(":", 1)
        if value.strip() == ">":
            folded: list[str] = []
            index += 1
            while index < len(lines) and (lines[index].startswith(" ") or not lines[index].strip()):
                if lines[index].strip():
                    folded.append(lines[index].strip())
                index += 1
            data[key.strip()] = " ".join(folded)
            continue
        data[key.strip()] = value.strip().strip('"')
        index += 1
    return data


class ChiarisciEAgisciStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL_MD.read_text(encoding="utf-8")
        cls.cases = load_cases()

    def test_frontmatter_is_portable(self) -> None:
        meta = frontmatter(self.skill_text)
        self.assertEqual(set(meta), {"name", "description"})
        self.assertEqual(meta["name"], "chiarisci-e-agisci")
        self.assertLessEqual(len(meta["description"]), 1024)
        self.assertIn("MANDATORY TRIGGERS", meta["description"])
        self.assertIn("NOT-TRIGGER", meta["description"])

    def test_dataset_has_planned_shape(self) -> None:
        self.assertEqual(validate_cases(self.cases), [])
        self.assertEqual(len(self.cases), 16)
        self.assertEqual(sum(case["interaction"] == "first_turn" for case in self.cases), 11)
        self.assertEqual(sum(case["interaction"] == "multi_turn" for case in self.cases), 5)

    def test_progressive_disclosure_structure(self) -> None:
        self.assertLessEqual(len(self.skill_text.splitlines()), 200)
        for reference in ALL_REFERENCES:
            relative = f"references/{reference}"
            self.assertIn(relative, self.skill_text)
            path = INNER_SKILL / relative
            self.assertTrue(path.exists())
            self.assertLessEqual(len(path.read_text(encoding="utf-8").splitlines()), 100)

    def test_progressive_disclosure_has_no_prefetch(self) -> None:
        self.assertRegex(self.skill_text, r"Non leggere (?:in anticipo|preventivamente) le altre reference")
        integration = (INNER_SKILL / "references/integrazione-dei-workflow.md").read_text(encoding="utf-8")
        self.assertRegex(self.skill_text + integration, r"sessione significativa")
        self.assertRegex(self.skill_text, r"Solo se.*flusso riutilizzabile")

    def test_checkpoints_are_distinct(self) -> None:
        prodromi = (INNER_SKILL / "references/prodromi-redazionali.md").read_text(encoding="utf-8")
        priorita = (INNER_SKILL / "references/prioritizzazione.md").read_text(encoding="utf-8")
        self.assertIn("due checkpoint distinti", prodromi)
        self.assertIn("non approva l'ordine", priorita)

    def test_questions_and_internal_instructions_are_guarded(self) -> None:
        priorita = (INNER_SKILL / "references/prioritizzazione.md").read_text(encoding="utf-8")
        integrazione = (INNER_SKILL / "references/integrazione-dei-workflow.md").read_text(encoding="utf-8")
        self.assertIn("Non unire i due dati nella stessa domanda", priorita)
        self.assertIn("un solo punto interrogativo complessivo", priorita)
        self.assertIn("Applicare questa checklist internamente", integrazione)
        self.assertIn("Non citare la skill, le reference", self.skill_text)

    def test_privacy_applies_to_every_mode(self) -> None:
        self.assertRegex(self.skill_text, r"Sostituire.*dati identificativi.*già ricevuti")

    def test_thread_decisions_are_preserved(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [SKILL_MD, *sorted((INNER_SKILL / "references").glob("*.md"))]
        )
        for marker in (
            "maieutica vincolata", "Organizzazione del lavoro", "Prodromi alla redazione",
            "Prioritizzazione", "valore", "rilevanza del cliente", "LEARNINGS.md",
        ):
            self.assertIn(marker.casefold(), combined.casefold())
        self.assertNotIn("Anonimator", combined)

    def test_openai_metadata_is_non_blocking(self) -> None:
        metadata = (INNER_SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Chiarisci e agisci"', metadata)
        self.assertIn("$chiarisci-e-agisci", metadata)
        self.assertNotIn("dependencies:", metadata)

    def test_no_placeholders_or_absolute_paths(self) -> None:
        for path in INNER_SKILL.rglob("*"):
            if not path.is_file() or path.name == ".DS_Store":
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"TODO|FIXME|/Users/filippostrozzi")

    def test_archive_matches_sources_and_excludes_tests(self) -> None:
        self.assertTrue(ARCHIVE.exists())
        with zipfile.ZipFile(ARCHIVE) as archive:
            names = set(archive.namelist())
            self.assertFalse(any("tests/" in name or "__MACOSX" in name or name.endswith(".DS_Store") for name in names))
            source_files = [
                path for path in INNER_SKILL.rglob("*")
                if path.is_file() and path.name != ".DS_Store" and "__pycache__" not in path.parts
            ]
            expected = {f"chiarisci-e-agisci/{path.relative_to(INNER_SKILL).as_posix()}" for path in source_files}
            archived_files = {name for name in names if not name.endswith("/")}
            self.assertEqual(archived_files, expected)
            for path in source_files:
                member = f"chiarisci-e-agisci/{path.relative_to(INNER_SKILL).as_posix()}"
                self.assertEqual(archive.read(member), path.read_bytes(), member)


if __name__ == "__main__":
    unittest.main(verbosity=2)
