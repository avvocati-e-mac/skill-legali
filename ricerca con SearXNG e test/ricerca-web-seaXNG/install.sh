#!/usr/bin/env bash
#
# install.sh — installa la skill "ricerca-web-searXNG" per Claude Code.
# Idempotente: rilanciarlo non duplica nulla.
#
# Cosa fa:
#   1. verifica i prerequisiti (npx, per il server mcp-searxng)
#   2. copia la skill in ~/.claude/skills/ricerca-web-searXNG/
#   3. aggiunge in modo NON distruttivo il server "searxng" a ~/.mcp.json
#   4. stampa i passi finali di verifica
#
set -euo pipefail

# --- percorsi -----------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_SKILL_DIR="$SCRIPT_DIR/ricerca-web-searXNG"  # cartella skill da copiare
DEST_SKILLS_DIR="$HOME/.claude/skills"
DEST_SKILL_DIR="$DEST_SKILLS_DIR/ricerca-web-searXNG"
MCP_FILE="$HOME/.mcp.json"
SEARXNG_URL_DEFAULT="http://localhost:8080"

# --- helper di output ---------------------------------------------------------
info()  { printf '  \033[0;34m›\033[0m %s\n' "$1"; }
ok()    { printf '  \033[0;32m✓\033[0m %s\n' "$1"; }
warn()  { printf '  \033[0;33m!\033[0m %s\n' "$1"; }
err()   { printf '  \033[0;31m✗\033[0m %s\n' "$1" >&2; }

echo
echo "Installazione skill ricerca-web-searXNG per Claude Code"
echo "==============================================="

# --- 1. prerequisiti ----------------------------------------------------------
if [ ! -f "$SRC_SKILL_DIR/SKILL.md" ]; then
  err "Non trovo $SRC_SKILL_DIR/SKILL.md. Lancia lo script dalla cartella del progetto."
  exit 1
fi

if command -v npx >/dev/null 2>&1; then
  ok "npx presente (necessario per il server mcp-searxng)"
else
  warn "npx/node NON trovato: il server SearXNG (npx -y mcp-searxng) non potrà partire."
  warn "Installa Node.js (https://nodejs.org) prima di usare la skill."
fi

# --- 2. copia skill -----------------------------------------------------------
mkdir -p "$DEST_SKILLS_DIR"
if [ -d "$DEST_SKILL_DIR" ]; then
  info "Skill già presente: aggiorno i file in $DEST_SKILL_DIR"
fi
# copia il CONTENUTO della cartella skill nella destinazione (idempotente)
cp -R "$SRC_SKILL_DIR/." "$DEST_SKILL_DIR/"
ok "Skill copiata in $DEST_SKILL_DIR"

# --- 3. merge non distruttivo del MCP -----------------------------------------
read -r -d '' SEARXNG_SNIPPET <<JSON || true
{
  "command": "npx",
  "args": ["-y", "mcp-searxng"],
  "env": { "SEARXNG_URL": "$SEARXNG_URL_DEFAULT" }
}
JSON

if command -v jq >/dev/null 2>&1; then
  if [ ! -f "$MCP_FILE" ]; then
    echo '{"mcpServers":{}}' > "$MCP_FILE"
    info "Creato $MCP_FILE"
  fi
  if jq -e '.mcpServers.searxng' "$MCP_FILE" >/dev/null 2>&1; then
    ok "Server 'searxng' già presente in ~/.mcp.json (lasciato invariato)"
  else
    tmp="$(mktemp)"
    jq --argjson s "$SEARXNG_SNIPPET" \
       '.mcpServers = (.mcpServers // {}) | .mcpServers.searxng = $s' \
       "$MCP_FILE" > "$tmp" && mv "$tmp" "$MCP_FILE"
    ok "Aggiunto server 'searxng' a ~/.mcp.json"
    warn "Imposta SEARXNG_URL sulla tua istanza (ora: $SEARXNG_URL_DEFAULT)"
  fi
else
  warn "jq non installato: non posso fare il merge automatico di ~/.mcp.json."
  warn "Aggiungi manualmente questo blocco sotto \"mcpServers\":"
  echo
  printf '  "searxng": %s\n' "$SEARXNG_SNIPPET"
  echo
fi

# --- 4. passi finali ----------------------------------------------------------
echo
echo "Fatto. Passi finali:"
info "1. Riavvia Claude Code (o esegui /mcp) per avviare il server SearXNG"
info "2. Verifica con /doctor che la skill 'ricerca-web-searXNG' sia caricata"
info "3. Assicurati che SEARXNG_URL punti alla tua istanza SearXNG"
echo
info "Disinstallazione: rm -rf $DEST_SKILL_DIR"
echo
