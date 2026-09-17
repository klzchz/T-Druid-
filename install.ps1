# One-shot installer for T-Druid's core (skills + scripts + global CLAUDE.md)
# on Windows/PowerShell. Mac/Linux users: use ./install.sh instead.
# Does NOT touch your vault content - copy vault-template\ yourself the
# first time, or merge specific files into an existing vault. Safe to re-run.

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "== T-Druid installer (Windows) =="

$SkillsDir = Join-Path $env:USERPROFILE ".claude\skills"
$BinDir    = Join-Path $env:USERPROFILE ".claude\tdruid-bin"
$ClaudeMd  = Join-Path $env:USERPROFILE ".claude\CLAUDE.md"

New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

Write-Host "-> copying skills"
Copy-Item -Path (Join-Path $Here "skills\*") -Destination $SkillsDir -Recurse -Force

Write-Host "-> copying core scripts (Python ones only run natively on Windows;"
Write-Host "   tdruid-config-sync/restore are bash and need WSL or Git Bash - see docs/SETUP.md)"
Copy-Item -Path (Join-Path $Here "bin\*") -Destination $BinDir -Recurse -Force

if (Test-Path $ClaudeMd) {
    Write-Host "-> $ClaudeMd already exists, NOT overwriting."
    Write-Host "   Compare it with $Here\CLAUDE.md.example by hand and merge what you want."
} else {
    Copy-Item -Path (Join-Path $Here "CLAUDE.md.example") -Destination $ClaudeMd
    Write-Host "-> installed CLAUDE.md.example -> $ClaudeMd - EDIT THE {{...}} PLACEHOLDERS."
}

Write-Host ""
Write-Host "Done. Remaining manual steps:"
Write-Host "  1. Add $BinDir to your PATH (System Properties > Environment Variables),"
Write-Host "     or move its contents wherever you keep personal scripts."
Write-Host "  2. Set TDRUID_VAULT as a user environment variable, e.g.:"
Write-Host "       [Environment]::SetEnvironmentVariable('TDRUID_VAULT', `"`$env:USERPROFILE\Documents\Obsidian Vault`", 'User')"
Write-Host "  3. If you don't have a vault yet, copy vault-template\ there and open it in Obsidian."
Write-Host "  4. Install the Obsidian 'Local REST API' community plugin, then run:"
Write-Host "       .\connect-obsidian.ps1 <api-key>"
Write-Host "  5. Edit the {{...}} placeholders in $ClaudeMd and your vault's _BOOT.md / _HOT.md."
Write-Host "  6. Run: python bin\tdruid-brain-check  (or the copy under $BinDir)"
Write-Host ""
Write-Host "Full walkthrough: $Here\docs\SETUP.md"
