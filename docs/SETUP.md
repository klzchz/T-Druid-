# Setup

Read `docs/SECURITY.md` before you put any real work information into a vault you connect this to — especially if you're doing this on a work laptop. It's short, read it first.

## 1. Prerequisites
- [Claude Code](https://claude.com/claude-code) installed and working (`claude --version` should print something).
- [Obsidian](https://obsidian.md) installed.
- Python 3.9+ and Node.js if you want the integration templates (job scanner, web-recon) — optional, skip if you just want the memory core.

## 2. Get an Obsidian vault ready
If you don't have a vault yet: copy `vault-template/` somewhere on disk, e.g.
```bash
cp -r vault-template "$HOME/Documents/Obsidian Vault"
```
Open Obsidian → **Open folder as vault** → pick that folder. If you already have a vault you like, copy the individual template files into it instead (don't overwrite anything of yours) — `_BOOT.md`, `_HOT.md`, `Memory Router.md`, `🧠 Brain.md`, `Last Session.md`, plus the empty `Logs/`, `Inbox/`, `Projects/` folders.

Fill in every `{{...}}` placeholder in those files with your own identity, projects, and current focus. This is the only step that's genuinely yours to do — everything else below is mechanical.

## 3. Install the Obsidian plugin that lets Claude talk to your vault

Claude Code can't read your Obsidian vault by magic — it needs a small HTTP server running inside Obsidian. That's the **Local REST API** community plugin. Click-by-click:

1. Open Obsidian, with your vault open.
2. **Settings** (gear icon, bottom left) → **Community plugins** (left sidebar).
3. If this is your first community plugin, click **Turn on community plugins** (a one-time confirmation).
4. Click **Browse**, type `Local REST API` in the search box.
5. Click the result (by Adam Coddington) → **Install** → then **Enable** (a toggle appears once installed).
6. Back in **Community plugins**, click on **Local REST API** in the left sidebar (under "Installed plugins") to open its settings.
7. Copy the **API Key** shown there — you'll need it in the next step. Leave this settings tab open, you'll come back to check the port number if anything doesn't connect.

**Obsidian must stay open** with the vault loaded for this to work — the plugin only runs while Obsidian is running. If Claude Code ever says it can't reach the vault, the first thing to check is whether Obsidian is open.

## 4. Connect Claude Code to the vault (MCP)

**The easy way — one command:**
```bash
./connect-obsidian.sh <api-key>
```
(the API key you copied in step 3). The script checks the connection and registers the MCP server for you, and tells you plainly if something's wrong instead of failing silently.

On **Windows**, use `.\connect-obsidian.ps1 <api-key>` in PowerShell instead — same behavior.

**The manual way**, if you'd rather do it yourself (or the plugin is using a non-default port — check its settings tab, step 3.6 above), on any OS:
```bash
claude mcp add --transport http obsidian http://127.0.0.1:27123 --header "Authorization: Bearer <api-key>"
```

## 5. Verify it's actually alive

```bash
claude mcp list
```
`obsidian` should show up as connected. If it doesn't:
- Is Obsidian open, with the vault loaded? (most common cause)
- Does the port in the command match the plugin's settings tab? (27123 is the default, but "HTTPS only" mode uses 27124 and `https://` instead)
- Did you paste the API key correctly? It rotates if you ever click "regenerate" in the plugin settings — a stale key looks exactly like a connection failure.

Once `claude mcp list` shows it connected, open any Claude Code session and ask it to read `_BOOT.md` from your vault. If it can quote it back to you, the brain is switched on.

## 6. Install the global boot file
```bash
cp CLAUDE.md.example ~/.claude/CLAUDE.md
```
Edit the placeholders. This file is what makes Claude Code read `_BOOT.md` at the start of every session instead of starting cold — see `docs/ARCHITECTURE.md` for why this matters.

## 7. Install the skill and the core scripts
```bash
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
mkdir -p ~/.local/bin
cp bin/* ~/.local/bin/
chmod +x ~/.local/bin/tdruid-*
```
Make sure `~/.local/bin` is on your `$PATH`.

Set the vault location in your shell profile (`~/.bashrc`, `~/.zshrc`, ...):
```bash
export TDRUID_VAULT="$HOME/Documents/Obsidian Vault"   # wherever you put it
```

Steps 6-7 (plus a check for step 5) are all done in one shot by `./install.sh` (macOS/Linux) or `.\install.ps1` (Windows) — either will tell you which manual steps are still left.

### Platform notes

- **macOS / Linux:** everything here works natively, no extra setup.
- **Windows:** `install.ps1` and `connect-obsidian.ps1` cover the setup itself. `bin/tdruid-config-sync` and `bin/tdruid-config-restore` are bash scripts (they call `git`, `rsync`, `crontab`) and need **WSL** or **Git Bash** to run — everything else in `bin/` (`tdruid-brain-check`, `tdruid-status`, `tdruid-llms`, `tdruid-nodash`) is plain Python and runs the same everywhere, including a native `python.exe`. If you're on WSL already, just follow the macOS/Linux instructions inside it — that's how this repo itself was built and tested.

## 8. Sanity check
```bash
tdruid-brain-check          # should report "clean" or a short list of warnings
tdruid-status list          # should print the example seed fact
tdruid-config-sync          # backs your local scripts up into the vault (needs the vault to be a git repo)
```

## 9. Make your memory persistent across machines/backups

Turn your vault into a git repo (a **private** one — see `docs/SECURITY.md` for why) so it survives a lost laptop and can follow you to a second machine:
```bash
cd "$TDRUID_VAULT" && git init && git add -A && git commit -m "initial vault"
# then create a private remote and:  git remote add origin <your-private-repo> && git push -u origin main
```
On a new machine, clone that private repo as the vault, run `./install.sh`, then `tdruid-config-restore` to pull your scripts/skills back down.

## 10. (Optional) integration templates and API keys

See `integrations/*/README.md` for the Discord approval-gate, job scanner, and email-report templates. Each is self-contained and documents its own env vars — and **`.env.example` at the repo root lists every one of them in a single place**, so you're not hunting through READMEs to find what to set. Copy it to `.env` (already gitignored), fill in only the sections for the features you're actually using, and load it however your shell does dotenv (or just `source .env` on macOS/Linux/WSL).

## 11. First real session
Open Claude Code anywhere, in any project. It should read `_BOOT.md` and `Last Session.md` before doing anything else, and tell you what it found (or tell you it couldn't reach the vault — never silently pretend to remember). From here, just work — the `druid-sleep` skill turns each session's conversation into durable memory.
