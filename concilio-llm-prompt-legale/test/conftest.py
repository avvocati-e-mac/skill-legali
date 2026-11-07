"""Pytest bootstrap: make the skill's scripts/ importable with a flat import.

`normattiva_fetch.py`, `caselaw_formcheck.py` and `verify_statutes.py` do a flat
`import legal_panel` / `import normattiva_fetch`. Putting scripts/ first on
sys.path reproduces production exactly (no packaging, stdlib-only). `importlib`
would load a second copy of `legal_panel` under a private name and break those
flat imports, so we deliberately use sys.path here.
"""

from __future__ import annotations

import sys

from _paths import SCRIPTS_DIR

scripts_dir = str(SCRIPTS_DIR)
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
