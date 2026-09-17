#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generic template: a Discord-based approval gate for letting a second person
(a co-founder, a teammate) trigger production actions through your agent —
WITHOUT letting their DM directly execute commands.

The design, and why it looks like this
---------------------------------------
A teammate can ask for anything over DM. If the bot executed it directly,
then whoever controls that DM controls production — their account gets
compromised, or they get socially engineered into pasting a malicious
command, and now your site is down or your data is gone. Nobody approved it.

So: a request becomes a PROPOSAL with the exact shell command shown in full,
you react ✅ or ❌ on your own DM, and only then does it run. Your teammate
gets to operate real infrastructure; you keep the key. The difference
between the two designs is a two-second reaction.

Configure via environment variables (put them in a .env file, never commit
them):
    DISCORD_BOT_TOKEN     bot token
    OWNER_DM_CHANNEL_ID   DM channel id where YOU approve/deny
    TEAMMATE_DM_CHANNEL_ID DM channel id to notify the requester

Usage:
    approval-gate.py propose "<description>" "<shell command>" "<requested by>"
    approval-gate.py approve <id>      # call this from your reaction-webhook handler
    approval-gate.py deny <id>
    approval-gate.py list
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

STATE_DIR = os.path.expanduser("~/.config/tdruid-approval-gate")
PENDING_FILE = os.path.join(STATE_DIR, "pending.json")
TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
OWNER_DM = os.environ.get("OWNER_DM_CHANNEL_ID", "")
TEAMMATE_DM = os.environ.get("TEAMMATE_DM_CHANNEL_ID", "")
EXPIRY_MINUTES = 60  # an old, un-reacted proposal shouldn't silently execute later


def api(method, path, body=None):
    req = urllib.request.Request(
        "https://discord.com/api/v10" + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            t = r.read().decode()
            return json.loads(t) if t.strip() else {}
    except Exception as e:
        print(f"discord API error: {e}", file=sys.stderr)
        return {}


def send(channel_id, content):
    return api("POST", f"/channels/{channel_id}/messages", {"content": content})


def load():
    if not os.path.exists(PENDING_FILE):
        return {}
    try:
        return json.load(open(PENDING_FILE, encoding="utf-8"))
    except Exception:
        return {}


def save(d):
    os.makedirs(STATE_DIR, exist_ok=True)
    json.dump(d, open(PENDING_FILE, "w", encoding="utf-8"), indent=2)


def cmd_propose(args):
    description, command, requester = args
    msg = send(OWNER_DM,
               f"Approval needed: **{description}**\nRequested by: {requester}\n"
               f"```\n{command}\n```\nReact ✅ to approve or ❌ to deny.")
    if not msg.get("id"):
        sys.exit("failed to post the approval request")
    d = load()
    d[msg["id"]] = {"description": description, "command": command,
                     "requester": requester,
                     "created": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    save(d)
    send(TEAMMATE_DM, f"Asked the owner to approve: {description}. "
                      f"I'll run it and let you know as soon as they do.")
    print("proposed", msg["id"])


def cmd_approve(args):
    mid = args[0]
    d = load()
    if mid not in d:
        return  # a reaction on some other message
    p = d.pop(mid)
    save(d)

    age_min = (datetime.now(timezone.utc)
               - datetime.fromisoformat(p["created"])).total_seconds() / 60
    if age_min > EXPIRY_MINUTES:
        send(OWNER_DM, f"⏱️ proposal expired ({age_min:.0f} min old), NOT executed: "
                       f"{p['description']}. Ask again if you still want it.")
        return

    result = subprocess.run(["bash", "-lc", p["command"]],
                            capture_output=True, text=True, timeout=900)
    ok = result.returncode == 0
    output = (result.stdout or result.stderr or "").strip()[-1200:]
    tag = "✅ done" if ok else f"❌ FAILED (exit {result.returncode})"

    send(OWNER_DM, f"{tag}: {p['description']}\n```\n{output[:1500]}\n```")
    send(TEAMMATE_DM, f"{tag}: **{p['description']}**\nApproved.\n```\n{output[:900]}\n```")
    print(tag)


def cmd_deny(args):
    mid = args[0]
    d = load()
    if mid not in d:
        return
    p = d.pop(mid)
    save(d)
    send(TEAMMATE_DM, f"Not approved: **{p['description']}**. Ask the owner why if you want to understand.")
    print("denied")


def cmd_list(args):
    d = load()
    if not d:
        print("no pending proposals.")
    for mid, p in d.items():
        print(f"{mid} · {p['created']} · {p['requester']}: {p['description']}\n   $ {p['command']}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    {"propose": cmd_propose, "approve": cmd_approve,
     "deny": cmd_deny, "list": cmd_list}.get(
        cmd, lambda a: sys.exit("unknown command"))(args)


if __name__ == "__main__":
    main()
