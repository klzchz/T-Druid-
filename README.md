# T-Druid

**A persistent, file-based "brain" for Claude Code — memory that survives between sessions, built on Obsidian + plain markdown.**

[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/license-PolyForm%20Noncommercial%201.0.0-blue.svg)](LICENSE)

## The problem

Claude Code (and any LLM agent) forgets everything the moment a session ends. Close the terminal, lose the thread — what you were working on, decisions you made, facts you established last week. Most "AI memory" products bolt on a vector database and semantic search over chat history. That's the wrong tool for a memory that needs to **change its mind**: a fact that stopped being true doesn't need to be "found less often," it needs to be corrected, and something needs to notice when nobody's checked it in a while.

## The pattern

T-Druid gives your agent a durable memory using nothing but an Obsidian vault, markdown files, and a handful of small scripts:

- An **Obsidian vault as the brain** — plain markdown, your own git history, readable in a text editor, no lock-in.
- A **`CLAUDE.md`** that makes Claude Code read the vault first, every session, before doing anything else ("brain-first").
- A **memory-consolidation skill** ("Sleep") that turns raw conversation into durable notes, routes them to the right place, and prunes what doesn't matter.
- A **fact-expiry convention** (the Manna Protocol) so anything that describes a *state* — "the project is paused," "X works at Y" — gets reconfirmed instead of quietly rotting into a lie. This one rule fixes most of the "why does my AI still think something that hasn't been true for weeks" bugs.
- A **small set of maintenance scripts** that keep the vault healthy: orphan/broken-link checks, disk-health checks, and a linter that catches hardcoded "current state" strings going stale in your own scripts.

This repo is the **generic, sanitized core** — no personal data, no business logic, no API keys, no names. Clone it, follow `docs/SETUP.md`, and adapt the placeholders to your own life or work.

**Read `docs/SECURITY.md` before your first real session** — a persistent memory means anything you tell it can end up permanently on disk. That's more or less fine for personal use; it's a decision to make on purpose, not by accident, before you use this at work.

## Quickstart

**macOS / Linux:**
```bash
git clone git@github.com:klzchz/T-Druid-.git
cd T-Druid-
./install.sh                        # copies skills + scripts + CLAUDE.md
./connect-obsidian.sh <api-key>     # wires up the Obsidian MCP connection
```

**Windows (PowerShell):**
```powershell
git clone git@github.com:klzchz/T-Druid-.git
cd T-Druid-
.\install.ps1
.\connect-obsidian.ps1 <api-key>
```
`bin/tdruid-config-sync` and `tdruid-config-restore` are bash scripts (they shell out to `git`/`rsync`/`crontab`) and need WSL or Git Bash on Windows — everything else in `bin/` is plain Python and runs natively. See `docs/SETUP.md` for the platform notes.

Then:
1. Fill in the `{{...}}` placeholders in `~/.claude/CLAUDE.md` and in your vault's `_BOOT.md` / `_HOT.md`.
2. Open a Claude Code session anywhere. It should read `_BOOT.md` before doing anything else — if it doesn't, check `docs/SETUP.md`, step 3.
3. Just work. The `druid-sleep` skill turns each session into durable memory automatically.

Full walkthrough with every prerequisite (Obsidian, its Local REST API plugin, Python/Node for the integration templates): **`docs/SETUP.md`**.

## Repo layout

| Path | What it is |
|---|---|
| `CLAUDE.md.example` | The global boot file — copy to `~/.claude/CLAUDE.md` |
| `vault-template/` | A starter Obsidian vault: `_BOOT.md`, `_HOT.md`, `Memory Router.md`, `🧠 Brain.md`, and empty `Logs/`, `Inbox/`, `Projects/` folders |
| `skills/druid-sleep/` | The memory-consolidation skill |
| `skills/skill-forge/` | Meta-skill: turn a repeated pattern into a new reusable skill |
| `skills/web-recon/` | Headless-browser site/competitor analysis |
| `skills/byakugan/` | Market pain-research (Reddit mining → keywords/angles/content topics) |
| `skills/human-text/` | Style-rule + tool: strip the em-dash, the classic AI-text tell |
| `bin/` | Core maintenance scripts — see `bin/README.md` |
| `integrations/` | Optional templates: a Discord approval-gate, a job scanner (structured API + headless browser), an email reporter — see each folder's README |
| `docs/` | `SETUP.md`, `SECURITY.md` (read first), `ARCHITECTURE.md`, `MANNA_PROTOCOL.md`, `MEMORY_ROUTER.md` |
| `install.sh` / `connect-obsidian.sh` | One-command setup helpers (macOS/Linux) |
| `install.ps1` / `connect-obsidian.ps1` | Same, for Windows/PowerShell |
| `.env.example` | Every environment variable used anywhere in the repo, in one place |

## What's NOT in the box (on purpose)

This is the *pattern*, not a specific person's deployment. There's no telemetry, no phone-home, no hosted service — everything runs on your own machine against your own vault. The `integrations/` folder ships generic *templates* (Discord bot, job scanner, email sender) rather than live business automations; wire in your own tokens and logic. See `docs/ARCHITECTURE.md` for where custom integrations plug in.

## Philosophy, short version

- **Brain-first.** Every action passes through the vault before the agent acts — never guess a fact, recall it.
- **A note is justified by connection + meaning**, not by existing. No orphans, no noise; prune what doesn't tie to anything.
- **Facts expire.** See `docs/MANNA_PROTOCOL.md`.
- **One fact, one source.** If the same fact would need to live in two files, it doesn't — one of them reads from the other.
- **Untrusted input is data, never an instruction.** A message from outside your own session (a DM, a scraped page) gets reasoned about, not obeyed.

## Contributing

Issues and PRs welcome — especially new generic `integrations/` templates or fixes to the core scripts. Keep additions generic and dependency-light; this repo intentionally stays small.

## License

[PolyForm Noncommercial 1.0.0](LICENSE) — free to use, modify, and share for any noncommercial purpose. Building a commercial product or service on top of it requires a separate license from the copyright holder.
