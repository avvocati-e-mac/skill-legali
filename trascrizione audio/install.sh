#!/usr/bin/env bash
#
# install.sh — installa la skill "audio-transcription" per Claude Code.
# Idempotente: rilanciarlo non duplica nulla.
#
# Cosa fa:
#   1. copia la skill in ~/.claude/skills/audio-transcription/
#   2. stampa i passi finali
#
# Nota: questa skill NON usa un server MCP. Il tool di trascrizione vero e proprio
# (parakeet-mlx / whisper.cpp / faster-whisper) viene installato al primo uso,
# seguendo le istruzioni della skill in base al tuo computer.
#
set -euo pipefail

# --- percorsi -----------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_SKILL_DIR="$SCRIPT_DIR/audio-transcription"   # cartella skill da copiare
DEST_SKILLS_DIR="$HOME/.claude/skills"
DEST_SKILL_DIR="$DEST_SKILLS_DIR/audio-transcription"

# --- helper di output ---------------------------------------------------------
info()  { printf '  \033[0;34m›\033[0m %s\n' "$1"; }
ok()    { printf '  \033[0;32m✓\033[0m %s\n' "$1"; }
warn()  { printf '  \033[0;33m!\033[0m %s\n' "$1"; }
err()   { printf '  \033[0;31m✗\033[0m %s\n' "$1" >&2; }

echo
echo "Installazione skill audio-transcription per Claude Code"
echo "======================================================"

# --- 1. prerequisiti ----------------------------------------------------------
if [ ! -f "$SRC_SKILL_DIR/SKILL.md" ]; then
  err "Non trovo $SRC_SKILL_DIR/SKILL.md. Lancia lo script dalla cartella del progetto."
  exit 1
fi

# --- 2. copia skill -----------------------------------------------------------
mkdir -p "$DEST_SKILLS_DIR"
if [ -d "$DEST_SKILL_DIR" ]; then
  info "Skill già presente: aggiorno i file in $DEST_SKILL_DIR"
fi
cp -R "$SRC_SKILL_DIR/." "$DEST_SKILL_DIR/"
ok "Skill copiata in $DEST_SKILL_DIR"

# --- 3. passi finali ----------------------------------------------------------
echo
echo "Fatto. Passi finali:"
info "1. Riavvia Claude Code"
info "2. Verifica con /doctor che la skill 'audio-transcription' sia caricata"
info "3. Chiedi a Claude di trascrivere un file (es. «trascrivi udienza.mp3»):"
info "   al primo uso installerà da solo il tool adatto al tuo computer."
echo
info "Disinstallazione: rm -rf $DEST_SKILL_DIR"
echo
