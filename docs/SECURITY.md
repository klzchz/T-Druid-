# Security & Privacy — read this before you use this at work

T-Druid's whole value is that it remembers everything you tell it, forever, across sessions. That's also exactly why it's dangerous to set up carelessly. Read this before your first real session, especially if you plan to use it for anything work-related.

## The core tradeoff

Every prompt you send in a Claude Code session connected to this vault can end up written to disk, in plain markdown, in a folder that:
- persists indefinitely (that's the whole point),
- may get committed to a git remote if you set one up (step 9 in `SETUP.md`),
- is readable by anything else running on your machine with file-system access,
- and if the Local REST API plugin's port is ever reachable from outside your machine (a misconfigured firewall, a shared/cloud dev box), is readable by anyone who can reach that port with the API key.

None of that is a bug — it's the mechanism. A memory that isn't durable and locally inspectable isn't a memory, it's a cache. But it means **you are the one deciding what's safe to say to it.**

## If you're using this for work

This is **each engineer's own call to make**, not something this project can decide for you. Concretely, before you start:

- **Check your employer's data handling / AI usage policy first.** Some companies explicitly prohibit pasting proprietary code, credentials, customer data, or internal strategy into any third-party or locally-stored AI tool. Find out before you find out the hard way.
- **Never let credentials, API keys, or tokens land in a note.** If you need Claude to know a secret exists, tell it where the secret is stored (a `.env` file, a secrets manager) — never paste the value itself into a prompt or a vault note. The scripts in `bin/` and `integrations/` follow this rule themselves (env vars only, nothing hardcoded); keep your own additions to the same standard.
- **If your vault syncs to a git remote, make sure that remote is private and yours.** A vault full of work context pushed to a public repo, or a third-party's cloud service, is an information leak with your name on the commit.
- **Be deliberate about what you let it remember from work sessions.** The `Memory Router.md` convention (route-or-Inbox, never guess) exists partly for this reason: an explicit routing decision is a moment where you can notice "wait, should this actually be written down."
- **A local vault is not an audited, access-controlled system.** If your employer requires SOC2/audit trails/access logs for where work data lives, a personal Obsidian vault almost certainly doesn't satisfy that — this is a personal productivity tool, not enterprise infrastructure.

None of this means don't do it — plenty of engineers run exactly this kind of personal system successfully. It means: **decide on purpose, not by accident.** The failure mode isn't "the tool is unsafe," it's "I didn't think about where this was going before I typed it."

## Other things worth locking down

- **The Local REST API plugin binds to localhost by default** — keep it that way unless you specifically know you need remote access, and if you do, put it behind your own auth/VPN, not just the plugin's API key.
- **The Discord approval-gate template** (`integrations/discord-bot/`) is designed so a compromised or socially-engineered teammate DM can't directly execute commands — see its own docstring. Don't weaken that gate for convenience; it exists because the failure mode (someone's account gets used to run an arbitrary shell command against your infrastructure) is a real one.
- **The job-scanner browser template** deliberately uses a clean, anonymous browser profile instead of your real logged-in session — see `integrations/job-scanner/README.md`. Don't "upgrade" it to reuse your real session; that's how accounts get flagged for bot-like behavior.
- **Rotate the Local REST API key** if you ever suspect it leaked (accidentally committed, shared in a screenshot, etc.) — regenerate it from the plugin's settings tab and re-run `./connect-obsidian.sh` with the new one.
