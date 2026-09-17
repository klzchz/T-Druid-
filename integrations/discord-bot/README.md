# Discord approval-gate template

A pattern for letting a second person (co-founder, teammate) request production actions through your agent by DM, without giving their account direct execution power. See `approval-gate.py` for the full mechanics and rationale.

## Setup
1. Create a Discord bot (discord.com/developers/applications), enable the `DIRECT_MESSAGES` and `DIRECT_MESSAGE_REACTIONS` intents.
2. Open a DM channel with yourself and with your teammate via the bot at least once (send any message through the API) so you have both channel IDs.
3. Set env vars: `DISCORD_BOT_TOKEN`, `OWNER_DM_CHANNEL_ID`, `TEAMMATE_DM_CHANNEL_ID`.
4. Wire your agent to call `approval-gate.py propose "<what>" "<shell command>" "<who asked>"` whenever your teammate requests a production action in a session where you (the agent) are talking to them.
5. Run a small webhook/gateway listener (not included here — depends on your hosting) that calls `approval-gate.py approve <message_id>` / `deny <message_id>` when you react ✅/❌ on your own DM.

## Why this exists instead of just trusting the DM
Untrusted input should never directly become an executed command — see the docstring in `approval-gate.py` for the full reasoning. This is the same principle as "never let a webhook payload run arbitrary code" applied to a human-to-agent channel.
