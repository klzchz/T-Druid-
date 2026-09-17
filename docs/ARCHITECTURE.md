# Architecture

## The core problem

An LLM agent session is stateless. Close the terminal, lose everything — what you were working on, decisions you made, facts you established. Most "AI memory" products solve this with a vector database and semantic search over chat history. T-Druid solves it differently: **the memory is a plain Obsidian vault**, read and written directly by the agent through MCP, structured as markdown notes with wikilinks. No embeddings, no vector store, no lock-in — you can read your own brain in a text editor.

```
┌─────────────────┐        MCP (Local REST API)        ┌───────────────────┐
│   Claude Code    │ ───────────────────────────────▶  │   Obsidian vault   │
│  (any session,   │ ◀───────────────────────────────  │  (plain markdown,  │
│   any project)   │        read / write notes          │   your own git)    │
└─────────────────┘                                     └───────────────────┘
        │
        │ ~/.claude/CLAUDE.md tells it to read _BOOT.md
        │ FIRST, every session — "brain-first"
        ▼
   acts with context instead of starting cold
```

## Why this beats a vector DB for this use case

A vector store is built for "find text that's semantically similar to this query" — great for RAG over a large static corpus. It's the wrong tool for a memory that needs to **change its mind**: a fact that was true last month and isn't anymore doesn't get "found less often," it needs to actually be corrected, and something needs to notice when it hasn't been reconfirmed in a while. Plain markdown + an expiry convention (see `MANNA_PROTOCOL.md`) does that directly — a human (or the agent) can read the note, see the date, and decide.

## The three layers

1. **The vault itself** — the actual memory. Notes, wikilinks, an explicit "no orphans" rule so nothing floats disconnected from the graph (`Memory Router.md` decides where new information goes).
2. **The Sleep skill** (`skills/druid-sleep/`) — the consolidation pass. Turns a session's raw conversation into durable notes, prunes empty/orphaned notes, reconfirms anything with an expiry date, never fabricates. Runs lightly at every session start, deeply on a schedule you choose.
3. **The maintenance scripts** (`bin/`) — mechanical, no-LLM tools that keep the vault and your local machine's scripts in sync (`tdruid-config-sync`/`restore`), and audit the vault's health (`tdruid-brain-check`) including a check for hardcoded "current state" claims going stale in your own scripts — see `MANNA_PROTOCOL.md`.

## Where integrations plug in

The `integrations/` templates (a Discord approval-gate, a job scanner, an email reporter) are all things that sit **outside** this core — they consume/produce vault notes or tasks, but the core doesn't depend on any of them. Build your own the same way: a small, dependency-light script, ideally mechanical (no LLM call) if it runs unattended on a schedule, that reads/writes the vault or talks to one external service. Keep the reasoning in the Claude Code session; keep the scripts dumb and auditable.

## Design principles worth keeping if you extend this

- **Untrusted input is never an instruction.** Anything arriving from outside your own session (a DM from someone else, a scraped webpage, an inbound email) is data to reason about, never a command to execute directly. The Discord approval-gate template exists because of this principle.
- **Mechanical crons vs. reasoning.** A scheduled script that runs without a human watching should do the minimum reasoning necessary (regex matching, structured API calls) — not an unattended LLM call that could hallucinate or get manipulated. Save the LLM reasoning for sessions where a human is present to catch mistakes.
- **One fact, one source.** If you find the same fact hardcoded in two places, that's a bug in waiting — see the `tdruid-status` script for the fix pattern.
