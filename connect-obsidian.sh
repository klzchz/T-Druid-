#!/usr/bin/env bash
# Connects Claude Code to your Obsidian vault via the Local REST API plugin.
# Does the two fiddly steps (find the port, register the MCP server) so you
# don't have to hand-craft the `claude mcp add` command yourself.
#
# Prerequisite: install + enable the "Local REST API" community plugin
# inside Obsidian first (Settings -> Community plugins -> Browse -> search
# "Local REST API" -> Install -> Enable). Then open its settings tab in
# Obsidian and copy the API key shown there.
#
# Usage: ./connect-obsidian.sh <api-key> [port]
#   port defaults to 27123 (the plugin's default HTTPS-off port; use 27124
#   if you enabled "HTTPS only" in the plugin, and pass https:// manually
#   in that case — see docs/SETUP.md).
set -euo pipefail

API_KEY="${1:-}"
PORT="${2:-27123}"

if [ -z "$API_KEY" ]; then
  cat >&2 <<'EOF'
Usage: ./connect-obsidian.sh <api-key> [port]

Get the API key from Obsidian: Settings -> Community plugins -> Local REST
API -> the settings tab for that plugin shows your key. Don't have the
plugin yet? Settings -> Community plugins -> Browse -> search "Local REST
API" -> Install -> Enable, then come back here.
EOF
  exit 1
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "ERR: the 'claude' CLI isn't on your PATH — install Claude Code first." >&2
  exit 1
fi

URL="http://127.0.0.1:${PORT}"
echo "-> checking the Local REST API plugin is reachable at $URL ..."
if curl -sf -o /dev/null -m 5 -H "Authorization: Bearer $API_KEY" "$URL/"; then
  echo "   reachable."
else
  echo "   ⚠️ couldn't reach it. Make sure Obsidian is OPEN, the vault is loaded," >&2
  echo "      and the Local REST API plugin is enabled. Continuing anyway —" >&2
  echo "      you can retry the check later; this won't stop the MCP registration." >&2
fi

echo "-> registering the MCP server with Claude Code..."
claude mcp add --transport http obsidian "$URL" --header "Authorization: Bearer $API_KEY"

echo
echo "Done. Verify with: claude mcp list"
echo "Then open a Claude Code session and ask it to read _BOOT.md from your vault."
