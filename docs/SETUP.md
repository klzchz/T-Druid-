# Setup

## 1. Prerequisites
- [Claude Code](https://claude.com/claude-code) installed and working.
- [Obsidian](https://obsidian.md) installed, with a vault (new or existing).
- The **Local REST API** community plugin for Obsidian (Settings → Community plugins → Browse → search "Local REST API" → install and enable). This is what lets Claude Code read/write your vault via MCP.
- Python 3.9+ and Node.js if you want the integration templates (job scanner, web-recon).

## 2. Get an Obsidian vault ready
If you don't have one yet, copy `vault-template/` somewhere on disk (e.g. `~/Documents/Obsidian Vault`) and open that folder as a vault in Obsidian. If you already have a vault, copy the template files into it instead (don't overwrite anything of yours).

Fill in the `{{...}}` placeholders in `_BOOT.md`, `_HOT.md`, `🧠 Brain.md`, and `Last Session.md` with your own identity, projects, and current focus.

## 3. Connect Claude Code to the vault (MCP)
In Obsidian's Local REST API plugin settings, copy the API key and port. Then register it as an MCP server for Claude Code — the exact command depends on your Claude Code version, but it looks like:

```bash
claude mcp add obsidian --transport http http://127.0.0.1:<port> --header "Authorization: Bearer <api-key>"
```

Check `claude mcp list` afterward to confirm it's connected. (If your Claude Code version uses a different MCP registration flow, check `claude mcp --help` — the plugin's own docs also cover this.)

## 4. Install the global boot file
```bash
cp CLAUDE.md.example ~/.claude/CLAUDE.md
```
Edit the placeholders. This file is what makes Claude Code read `_BOOT.md` at the start of every session instead of starting cold — see `docs/ARCHITECTURE.md` for why this matters.

## 5. Install the skill and the core scripts
```bash
mkdir -p ~/.claude/skills
cp -r skills/druid-sleep skills/skill-forge skills/web-recon ~/.claude/skills/
mkdir -p ~/.local/bin
cp bin/* ~/.local/bin/
chmod +x ~/.local/bin/tdruid-*
```
Make sure `~/.local/bin` is on your `$PATH`.

Set the vault location in your shell profile (`~/.bashrc`, `~/.zshrc`, ...):
```bash
export TDRUID_VAULT="$HOME/Documents/Obsidian Vault"   # wherever you put it
```

## 6. Sanity check
```bash
tdruid-brain-check          # should report "clean" or a short list of warnings
tdruid-status list          # should print the example seed fact
tdruid-config-sync          # backs your local scripts up into the vault (needs the vault to be a git repo)
```

## 7. (Optional) integration templates
See `integrations/*/README.md` for the Discord approval-gate, job scanner, and email-report templates. Each is self-contained and documents its own env vars.

## 8. First real session
Open Claude Code anywhere, in any project. It should read `_BOOT.md` and `Last Session.md` before doing anything else, and tell you what it found (or tell you it couldn't reach the vault — never silently pretend to remember). From here, just work — the `druid-sleep` skill turns each session's conversation into durable memory.

For the one-shot version of steps 4-6, see `install.sh` in the repo root.
