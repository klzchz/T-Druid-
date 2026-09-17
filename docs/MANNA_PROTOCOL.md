# The Manna Protocol — facts that expire

Named after manna: it spoils if you hoard it past its day. The idea: **any note that describes a *state*** (something that can stop being true — "the project is paused," "person X works at company Y," "the campaign is running") **carries a timestamp and an expiry**, so it gets reconfirmed instead of quietly rotting into a lie.

## The convention

```
- SOME FACT: description of the state. (as-of 2026-01-15 · exp 2026-03-15)
```

- `as-of` — when this was last verified true.
- `exp` — when it should be reconfirmed. Pick an interval that matches how fast the fact actually changes (a "project is paused" fact might get a 30-day expiry; "person X's job title" might get 6 months).
- **Timeless facts/identity/rules don't need an `exp`** — only things that could stop being true.

## What happens at expiry

During your memory-consolidation pass (the `druid-sleep` skill, or whatever your own equivalent is), scan for facts within a few days of their `exp` date:
1. Check the fact against its source (the note it came from, or reality — a git log, a live API, whatever's authoritative).
2. Still true? Bump `exp` forward.
3. No longer true, or uncertain? Move it to a `## stale` block and correct the source note — **move the old value to a `## superseded (date)` block, never delete it outright.** History matters; you want to be able to see that something changed and when.

## Why this exists (the incident that motivated it)

A real deployment of this pattern had two scripts each independently assert "Project X is paused" as a hardcoded literal string — one fed a daily report, the other a one-time onboarding message. When the project actually un-paused, one script got updated and the other didn't, because **nothing outside `_HOT.md` had ever carried an expiry convention.** A teammate got told for two straight weeks that a live product was frozen, purely because the fact lived in two places and only one got fixed.

The fix was two-fold: (1) extend the expiry convention past the main "gold facts" file into any script that asserts a current-state fact (`tdruid-brain-check`'s "stale-prone script facts" check does this mechanically — it flags any state-word string in your scripts folder with no adjacent `as-of` comment), and (2) collapse duplicated facts into one source of truth that other scripts read from instead of re-asserting (`bin/tdruid-status`).

## The line not to cross

Expiry/reconfirmation is about **whether a fact is still true**, decided by evidence — never by what you'd prefer to be true, or by what's most "aligned" with some goal. If you weight what gets attention by importance/goal-alignment (a legitimate thing to do — see the Synaptic/salience idea if your Sleep skill has one), that weighting must never leak into deciding *truth itself*. A fact doesn't become true because it would be convenient.
