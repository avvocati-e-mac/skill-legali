#!/usr/bin/env python3
"""Minimal validator for a Codex skill folder."""

from __future__ import annotations

import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9-]{1,63}$")


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
        "references/rubric.md",
        "references/model-routing.md",
        "references/live-judging.md",
        "references/reporting.md",
        "references/source-workflow.md",
        "references/case-schema.md",
        "scripts/legal_panel.py",
    ):
        if not (path / required).exists():
            errors.append(f"Missing required support file: {required}")
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
