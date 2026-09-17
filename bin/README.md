# Core scripts

- `tdruid-config-sync` — publishes your local `~/.local/bin/tdruid-*` scripts and Claude Code config into your vault (so they ride your vault's own git backup).
- `tdruid-config-restore` — the inverse: installs whatever the vault has onto a fresh machine. Run this on boot on any new machine.
- `tdruid-brain-check` — read-only vault health check: orphans, broken links, empty notes, disk space, and stale/unstamped "current state" claims hardcoded in your scripts (see `../docs/MANNA_PROTOCOL.md`).
- `tdruid-status` — single source of truth for "current state" facts, so you never have the same fact hardcoded in two scripts that can drift apart.
- `tdruid-llms` — generates an `llms.txt`-style index of your vault (path + one-line description per note) so any agent/tool can ingest the brain quickly.
- `tdruid-nodash` — strips the em-dash from text/files (see `../skills/human-text/`).

All of them are dependency-light (stdlib Python / plain bash) and read `$TDRUID_VAULT` for the vault location.
