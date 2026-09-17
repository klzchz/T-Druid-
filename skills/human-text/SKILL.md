---
name: human-text
description: Style rule plus tool - never write the em-dash (a common AI-generated-text tell). Strip it from any text before it ships (posts, landing copy, notes, emails, commits). Triggers - posting generated text anywhere, "remove the dash", "clean the text", "no em-dash".
---

# Human Text - never the em-dash

The em-dash is a well-known fingerprint of AI-generated text. Write like a human and **never** use it, in any output: chat, social posts, landing copy, docs, commit messages.

## The rule
- Never output the em-dash (—) or en-dash (–). Use a normal hyphen with spaces " - ", a comma, parentheses, or just split the sentence.
- This is automatic, not opt-in. Self-check every message before it ships.

## The tool
`tdruid-nodash` (in `bin/`) cleans any text or file:
```bash
echo "a — b" | tdruid-nodash              # stdin -> stdout
tdruid-nodash file.txt                     # print cleaned
tdruid-nodash --write a.json b.html ...    # clean files in place (JSON stays valid)
```
Run generated copy through it before posting anywhere public-facing.
