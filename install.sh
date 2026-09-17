#!/usr/bin/env bash
# One-shot installer for T-Druid's core (skills + scripts + global CLAUDE.md).
# Does NOT touch your vault content — copy vault-template/ yourself the first
# time, or merge specific files into an existing vault. Safe to re-run.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== T-Druid installer =="

mkdir -p "$HOME/.claude/skills" "$HOME/.local/bin"

echo "-> copying skills"
cp -r "$HERE/skills/"* "$HOME/.claude/skills/"

echo "-> copying core scripts"
cp "$HERE/bin/"* "$HOME/.local/bin/"
chmod +x "$HOME/.local/bin/tdruid-"*

if [ -f "$HOME/.claude/CLAUDE.md" ]; then
  echo "-> ~/.claude/CLAUDE.md already exists, NOT overwriting."
  echo "   Compare it with $HERE/CLAUDE.md.example by hand and merge what you want."
else
  cp "$HERE/CLAUDE.md.example" "$HOME/.claude/CLAUDE.md"
  echo "-> installed CLAUDE.md.example -> ~/.claude/CLAUDE.md — EDIT THE {{...}} PLACEHOLDERS."
fi

echo
echo "Done. Remaining manual steps:"
echo "  1. Set TDRUID_VAULT in your shell profile, e.g.:"
echo "       export TDRUID_VAULT=\"\$HOME/Documents/Obsidian Vault\""
echo "  2. If you don't have a vault yet, copy vault-template/ there and open it in Obsidian."
echo "  3. Install the Obsidian 'Local REST API' community plugin and register it as an MCP server."
echo "  4. Edit the {{...}} placeholders in ~/.claude/CLAUDE.md and your vault's _BOOT.md / _HOT.md."
echo "  5. Run: tdruid-brain-check"
echo
echo "Full walkthrough: $HERE/docs/SETUP.md"
