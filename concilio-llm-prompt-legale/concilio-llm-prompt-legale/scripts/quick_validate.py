#!/usr/bin/env python3
"""Minimal validator for a Codex skill folder."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9-]{1,63}$")

ARCHITECTURE_ANCHORS = (
    "arXiv:2306.05685",
    "arXiv:2412.05579",
    "arXiv:2505.12864",
    "arXiv:2504.21202",
    "arXiv:2505.17267",
    "PMC3900052",
)

EXPECTED_PRIMARY_LIVE_JUDGES = (
    "codex_gpt_5_5_xhigh",
    "perplexity_gemini_pro",
    "perplexity_kimi_k26",
)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter.")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not closed.")
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def literal_assignment(text: str, name: str) -> object | None:
    module = ast.parse(text)
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    return None


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    skill_file = path / "SKILL.md"
    if not skill_file.exists():
        return [f"Missing {skill_file}"]
    try:
        frontmatter = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return [str(exc)]

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not NAME_RE.fullmatch(name):
        errors.append("Frontmatter name must be lowercase letters, digits, and hyphens only, max 63 chars.")
    if name and path.name != name:
        errors.append(f"Folder name {path.name!r} must match frontmatter name {name!r}.")
    if not description:
        errors.append("Frontmatter description is required.")
    if any(key not in {"name", "description"} for key in frontmatter):
        errors.append("Frontmatter should contain only name and description.")
    for required in (
        "ARCHITETTURA.md",
        "CLAUDE.md",
        "AGENTS.md",
        "references/rubric.md",
        "references/model-routing.md",
        "references/live-judging.md",
        "references/reporting.md",
        "references/source-workflow.md",
        "references/case-schema.md",
        "scripts/legal_panel.py",
        "scripts/normattiva_fetch.py",
        "scripts/verify_statutes.py",
        "scripts/caselaw_formcheck.py",
    ):
        if not (path / required).exists():
            errors.append(f"Missing required support file: {required}")

    claude_file = path / "CLAUDE.md"
    agents_file = path / "AGENTS.md"
    if claude_file.exists() and agents_file.exists():
        if claude_file.read_bytes() != agents_file.read_bytes():
            errors.append("CLAUDE.md and AGENTS.md must be byte-for-byte identical.")

    architecture_file = path / "ARCHITETTURA.md"
    if architecture_file.exists():
        architecture_text = architecture_file.read_text(encoding="utf-8")
        for anchor in ARCHITECTURE_ANCHORS:
            if anchor not in architecture_text:
                errors.append(f"ARCHITETTURA.md missing scientific anchor: {anchor}")
    legal_panel_file = path / "scripts/legal_panel.py"
    if legal_panel_file.exists():
        legal_panel_text = legal_panel_file.read_text(encoding="utf-8")
        try:
            primary_judges = literal_assignment(legal_panel_text, "PRIMARY_LIVE_JUDGES")
        except Exception as exc:
            errors.append(f"Unable to parse PRIMARY_LIVE_JUDGES: {exc}")
        else:
            if tuple(primary_judges or ()) != EXPECTED_PRIMARY_LIVE_JUDGES:
                errors.append(
                    "PRIMARY_LIVE_JUDGES must be "
                    f"{list(EXPECTED_PRIMARY_LIVE_JUDGES)!r} to avoid duplicate GPT-family primaries."
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("Usage: quick_validate.py <skill-folder>", file=sys.stderr)
        return 2
    errors = validate(Path(args[0]))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
