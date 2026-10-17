#!/usr/bin/env bash
# Prepara la cartella di prova stabile per i test end-to-end di BuddaLaw con opencode.
#
#   bash buddalaw/tests/e2e/prepara_opencode.sh
#
# Crea buddalaw/tests/e2e/.opencode-sandbox/ (esclusa da git) con:
#   - opencode.json: BuddaLaw come server MCP remoto (OAuth), gli altri server
#     della configurazione globale spenti, skill diverse da buddalaw negate,
#     bash/modifica/webfetch negati;
#   - un repository git vuoto, perche' opencode cerca AGENTS.md, .opencode/ e
#     .claude/ risalendo fino alla radice git: cosi' si ferma qui e non legge
#     il CLAUDE.md/AGENTS.md del repository skill-legali.
# La skill vera e propria (.opencode/skills/buddalaw/) la copia run.py prima di
# ogni esecuzione, secondo la configurazione scelta (v9, v8.4, nessuna...).
#
# Dopo questo script, UNA VOLTA SOLA:
#   cd buddalaw/tests/e2e/.opencode-sandbox && \
#     OPENCODE_DB="$PWD/.opencode-test.db" opencode mcp auth buddalaw
# Il token resta nei dati di opencode dell'utente, mai nel repository.
# OPENCODE_DB separato: le sessioni di prova non finiscono nella cronologia
# dell'utente (e un database creato da un'altra versione di opencode non blocca
# i test con «no such column»). run.py usa lo stesso file.
set -euo pipefail
QUI="$(cd "$(dirname "$0")" && pwd)"
SANDBOX="$QUI/.opencode-sandbox"
mkdir -p "$SANDBOX/.opencode/skills"
cd "$SANDBOX"
[ -d .git ] || git init -q .
cat > opencode.json <<'JSON'
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "buddalaw": {
      "type": "remote",
      "url": "https://mcp.buddalaw.com/mcp",
      "enabled": true
    },
    "searxng": {
      "type": "local",
      "command": ["true"],
      "enabled": false
    }
  },
  "agent": {
    "build": { "steps": 8 }
  },
  "permission": {
    "skill": { "*": "deny", "buddalaw": "allow" },
    "bash": "deny",
    "edit": "deny",
    "webfetch": "deny",
    "websearch": "deny",
    "read": "allow"
  }
}
JSON
echo "Cartella di prova pronta: $SANDBOX"
OC="$(command -v opencode || ls /usr/local/Cellar/opencode/*/bin/opencode 2>/dev/null | tail -1 || true)"
if [ -z "$OC" ]; then
  echo "opencode non trovato nel PATH: installalo (brew install opencode) o imposta OPENCODE_BIN."
  exit 0
fi
OPENCODE_DB="$SANDBOX/.opencode-test.db" OPENCODE_DISABLE_EXTERNAL_SKILLS=1 \
  OPENCODE_DISABLE_CLAUDE_CODE=1 python3 - "$OC" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

# Legge solo i nomi MCP dalla configurazione risolta, senza stampare chiavi o token.
proc = subprocess.run([sys.argv[1], "debug", "config"], capture_output=True,
                      text=True, check=True, timeout=60)
resolved = json.loads(proc.stdout)
path = Path("opencode.json")
config = json.loads(path.read_text())
for name in resolved.get("mcp", {}):
    if name != "buddalaw":
        config["mcp"][name] = {"enabled": False}
path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
print("Server MCP estranei esclusi dalla sandbox.")
PY
echo "Ora esegui una volta:"
echo "  cd \"$SANDBOX\" && OPENCODE_DB=\"$SANDBOX/.opencode-test.db\" $OC mcp auth buddalaw"
echo "e controlla con:"
echo "  cd \"$SANDBOX\" && OPENCODE_DB=\"$SANDBOX/.opencode-test.db\" OPENCODE_DISABLE_EXTERNAL_SKILLS=1 $OC mcp list"
