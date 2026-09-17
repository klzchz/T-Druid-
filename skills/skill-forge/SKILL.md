---
name: skill-forge
description: Crystallize a repeatable pattern your agent just executed into a reusable Claude Code skill — the self-improving skill loop. Use after solving something non-trivial that will recur, or when told "turn this into a skill" / "save this flow".
---

# 🛠️ Skill Forge — turn experience into a reusable skill

The agent should get more capable the more it runs, by **creating skills from experience** and **improving them during use** — instead of solving the same non-trivial problem from scratch every time.

## When to forge
- A multi-step task that will recur (a recon flow, a deploy/check, a data pull, a report).
- After hitting and solving friction worth not repeating.
- NOT for trivial one-liners (SRP — one skill, one responsibility; don't bloat).

## Procedure
1. **Name** the pattern (kebab-case) + a one-line description with trigger phrases.
2. **Write** `~/.claude/skills/<name>/SKILL.md` (frontmatter `name` + `description`, then a tight procedure). Add a helper script (e.g. `<name>.js`/`.py`) when there's reusable code — keep it self-contained.
3. **Register in the brain:** a note (or memory entry) describing the capability, linked to your brain hub note; add it to the relevant index (`tdruid-llms`, if you're using that generator, regenerates `_llms.txt` automatically).
4. **Self-improve:** when the skill is reused and something is clunky or wrong, EDIT the SKILL.md / helper — don't work around it. Note what changed.

## Examples already forged (in this repo)
- `sharingan` — generic competitor/site recon via Playwright.
- `tdruid-llms` (`bin/tdruid-llms`) — vault → llms.txt index.

## Guardrail
Forge capabilities/automation, never anything that violates your own safety boundaries (no piracy, no irreversible/outward action without confirmation). Keep skills generic + reusable, not one-off.
