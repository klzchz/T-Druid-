# Connects Claude Code to your Obsidian vault via the Local REST API plugin,
# on Windows/PowerShell. Mac/Linux users: use ./connect-obsidian.sh instead.
#
# Prerequisite: install + enable the "Local REST API" community plugin
# inside Obsidian first (Settings -> Community plugins -> Browse -> search
# "Local REST API" -> Install -> Enable). Then open its settings tab in
# Obsidian and copy the API key shown there.
#
# Usage: .\connect-obsidian.ps1 <api-key> [port]

param(
    [Parameter(Mandatory=$false)][string]$ApiKey,
    [int]$Port = 27123
)

if (-not $ApiKey) {
    Write-Host "Usage: .\connect-obsidian.ps1 <api-key> [port]"
    Write-Host ""
    Write-Host "Get the API key from Obsidian: Settings -> Community plugins ->"
    Write-Host "Local REST API -> the settings tab for that plugin shows your key."
    Write-Host "Don't have the plugin yet? Settings -> Community plugins -> Browse ->"
    Write-Host "search 'Local REST API' -> Install -> Enable, then come back here."
    exit 1
}

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Error "the 'claude' CLI isn't on your PATH - install Claude Code first."
    exit 1
}

$Url = "http://127.0.0.1:$Port"
Write-Host "-> checking the Local REST API plugin is reachable at $Url ..."
try {
    Invoke-WebRequest -Uri "$Url/" -Headers @{ Authorization = "Bearer $ApiKey" } -TimeoutSec 5 -UseBasicParsing | Out-Null
    Write-Host "   reachable."
} catch {
    Write-Warning "couldn't reach it. Make sure Obsidian is OPEN, the vault is loaded,"
    Write-Warning "and the Local REST API plugin is enabled. Continuing anyway -"
    Write-Warning "you can retry the check later; this won't stop the MCP registration."
}

Write-Host "-> registering the MCP server with Claude Code..."
claude mcp add --transport http obsidian $Url --header "Authorization: Bearer $ApiKey"

Write-Host ""
Write-Host "Done. Verify with: claude mcp list"
Write-Host "Then open a Claude Code session and ask it to read _BOOT.md from your vault."
