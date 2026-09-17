# T-Druid

**A persistent, file-based "brain" for Claude Code — memory that survives between sessions, built on Obsidian + plain markdown.**

Claude Code (and any LLM agent) forgets everything when the session ends. T-Druid is a pattern — not a product — for giving your agent a durable memory: an Obsidian vault as the brain, a global `CLAUDE.md` that tells Claude to read it first ("brain-first"), and a small set of scripts/skills that keep that memory honest over time (facts expire, get reconfirmed, get pruned — never silently trusted forever).

This repo is the **generic, sanitized core**. It ships with no personal data, no business logic, no API keys, no names. Clone it, follow `docs/SETUP.md`, and adapt the placeholders to your own life/work.

## What's in the box

- **`CLAUDE.md.example`** — the global boot file. Copy to `~/.claude/CLAUDE.md`, fill in the placeholders (your name, your projects, your language). This is what makes Claude Code load your vault on every session instead of starting cold.
- **`vault-template/`** — a starter Obsidian vault: `_BOOT.md` (fast digest), `_HOT.md` (always-loaded gold facts with expiry dates), `Memory Router.md` (where new information goes), and empty `Conversas/`, `Inbox/`, `Projects/` folders.
- **`skills/druid-sleep/`** — the memory-consolidation skill ("sleep"): reads recent session logs, routes facts to the right notes, prunes dead/empty notes, reconfirms anything with an expiry date, never fabricates.
- **`bin/`** — a handful of small, dependency-light scripts that keep the vault and your local machine in sync (`tdruid-config-sync`, `tdruid-config-restore`, `tdruid-brain-check`, `tdruid-status`). No secrets, no third-party service coupling.
- **`docs/`** — setup, the MCP connection to Obsidian, the two core conventions (Memory Router, Manna Protocol/fact-expiry), and the overall architecture.

## What's NOT in the box (on purpose)

This is the *pattern*, not a specific person's deployment. It does **not** include: Discord bots, email senders, job scrapers, CRM/analytics integrations, or any business-specific automation. Those are things you build on top once the brain itself is working — see `docs/ARCHITECTURE.md` for where they'd plug in.

## Quickstart

```bash
./install.sh                        # copies skills + scripts + CLAUDE.md
./connect-obsidian.sh <api-key>     # wires up the Obsidian MCP connection
```
Then fill in the `{{...}}` placeholders in `~/.claude/CLAUDE.md` and in your vault's `_BOOT.md`/`_HOT.md`, and open a Claude Code session anywhere. It should read `_BOOT.md` before doing anything else. Full walkthrough with every prerequisite: `docs/SETUP.md`.

## Philosophy (short version)

- **Brain-first.** Every action passes through the vault before Claude acts — never guess a fact, recall it.
- **A note is justified by connection + meaning**, not by existing. No orphans, no noise, prune what doesn't tie to anything.
- **Facts expire.** Anything that describes a *state* ("the project is paused", "X works at Y") carries a `(as-of DATE · exp DATE)` stamp so it gets reconfirmed instead of quietly going stale forever — see `docs/MANNA_PROTOCOL.md`. This one rule fixes most of the "why does my AI think something that hasn't been true for weeks" bugs.
- **One fact, one source.** If the same fact would need to live in two files, it doesn't — one of them reads from the other.

## License

MIT — see `LICENSE`. Use it, fork it, rip out what you don't need.
