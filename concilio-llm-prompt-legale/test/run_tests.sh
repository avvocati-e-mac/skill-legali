#!/usr/bin/env bash
# Harness di test per la skill concilio-llm-prompt-legale.
# Gira offline, gratis, senza chiamare modelli. Tier-2 (live) è opt-in via env var.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"

# Tier-1 (unit) + Livello 2 (invarianti) + Livello 3 (pipeline su raw finti)
python3 -m pytest "$DIR" -v "$@"

# Tier-2 live (opzionale):
#   RUN_LIVE_E2E=1 ANTHROPIC_API_KEY=... ./run_tests.sh
