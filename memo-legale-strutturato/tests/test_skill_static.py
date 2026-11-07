#!/usr/bin/env python3
"""Test statici per la skill memo-legale-strutturato."""

from __future__ import annotations

import re
import unittest
import zipfile
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
SKILL_ROOT = TEST_DIR.parent
INNER_SKILL = SKILL_ROOT / "memo-legale-strutturato"
SKILL_MD = INNER_SKILL / "SKILL.md"
ARCHIVE = SKILL_ROOT / "memo-legale-strutturato.skill"


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


class MemoLegaleSkillStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL_MD.read_text(encoding="utf-8")

    def test_frontmatter_description_is_valid(self) -> None:
        meta = frontmatter(self.skill_text)
        self.assertEqual(meta["name"], "memo-legale-strutturato")
        self.assertLessEqual(len(meta["description"]), 1024)
        self.assertIn("MANDATORY TRIGGERS", meta["description"])
        for trigger in ("memo legale", "parere interno", "case assessment"):
            self.assertIn(trigger, meta["description"])

    def test_progressive_disclosure_is_explicit(self) -> None:
        self.assertIn("Progressive disclosure", self.skill_text)
        for reference in (
            "references/modelli-memo.md",
            "references/adattamento-diritto-italiano.md",
            "references/tooling-installazione.md",
        ):
            self.assertIn(reference, self.skill_text)
            self.assertTrue((INNER_SKILL / reference).exists())
        self.assertRegex(self.skill_text, r"Non caricare reference di routine")

    def test_tooling_rules_cover_buddalaw_and_perplexity(self) -> None:
        required = (
            "BuddaLaw",
            "Perplexity",
            "pplx_*",
            "pwm",
            "check_access",
            "Solo al primo lancio",
        )
        for marker in required:
            self.assertIn(marker, self.skill_text)

    def test_output_contract_is_present(self) -> None:
        for marker in (
            "risposta breve",
            "fatti rilevanti",
            "istituti",
            "rischi",
            "raccomandazione operativa",
        ):
            self.assertIn(marker, self.skill_text.lower())

    def test_references_keep_expected_installation_hints(self) -> None:
        tooling = (INNER_SKILL / "references/tooling-installazione.md").read_text(encoding="utf-8")
        for marker in (
            "https://github.com/avvocati-e-mac/skill-legali",
            "buddalaw/buddalaw.skill",
            "pwm --ai",
            "claude mcp add perplexity pwm-mcp",
        ):
            self.assertIn(marker, tooling)

    def test_no_placeholders(self) -> None:
        for path in INNER_SKILL.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"TODO|FIXME|\{\{")

    def test_archive_contains_installable_skill_files(self) -> None:
        self.assertTrue(ARCHIVE.exists())
        with zipfile.ZipFile(ARCHIVE) as archive:
            names = set(archive.namelist())
        self.assertIn("memo-legale-strutturato/SKILL.md", names)
        self.assertIn("memo-legale-strutturato/agents/openai.yaml", names)
        self.assertIn("memo-legale-strutturato/references/modelli-memo.md", names)
        self.assertFalse(any("__MACOSX" in name or name.endswith(".DS_Store") for name in names))


if __name__ == "__main__":
    unittest.main()
