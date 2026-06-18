"""Single source of truth for skill paths used by the test harness.

The harness lives in the OUTER folder `concilio-llm-prompt-legale/test/`, outside
the installable inner skill folder. Only this file hard-codes the inner folder
name so nothing else has to.
"""

from __future__ import annotations

from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
SKILL_ROOT = TEST_DIR.parent / "concilio-llm-prompt-legale"
SCRIPTS_DIR = SKILL_ROOT / "scripts"
REFERENCES_DIR = SKILL_ROOT / "references"
LEGAL_PANEL = SCRIPTS_DIR / "legal_panel.py"
FIXTURES = TEST_DIR / "fixtures"
