---
name: byakugan
description: Market pain-research for any niche or product idea - mine REAL user pain, demand, and the exact words the market uses, from Reddit (global, EN+PT), then turn it into ready-to-execute deliverables (keywords, marketing angles, content topics, distribution targets). Sibling of `sharingan` (that studies competitors; this reads the market). Use when validating a niche/product, finding pain points, mining keywords, or finding where to distribute. Triggers - "byakugan", "market research", "mine the pain", "what does the market complain about", "find the pain points", "keywords for <niche>".
---

# Byakugan - 360-degree market pain research

Premise: demand hides in complaints. Mine where people vent (Reddit worldwide, or your own local equivalent - a country-specific complaints site, a forum, whatever your market actually uses), then produce things ready to act on.

## Tooling
- **Reddit** blocks anonymous JSON/API access (HTTP 403), so `byakugan.py` renders the search UI in a real headless browser (Playwright) instead - the same approach as the `sharingan` skill.
- Deps: `pip install playwright && playwright install chromium`.
- Extending to another complaint source (e.g. a local review/complaints site for your market) means adding a similarly-scoped fetch function to `byakugan.py` - see its existing Reddit function as the template. Any site behind aggressive anti-bot (Cloudflare enterprise, etc.) may need a stealth plugin or a fallback to search-engine dorking (`site:example.com <term>`).

## Procedure
1. **Frame the hunt.** Pin down: the niche/keywords, the locale (`en`/`pt`/`both` - extend `PAIN` in `byakugan.py` for other languages).
2. **Mine.**
   ```bash
   python3 byakugan.py "<niche>" --locale both [--subs sub1,sub2] [--deep 8]
   ```
   - Pain-language operators (EN + PT baked in) are applied automatically: "is there an app", "wish there was", "alternative to", etc.
   - `--deep N` opens the top N threads for verbatim pain (post body + top comments).
   - Writes `out/<slug>/byakugan.json` and prints a digest: keywords, top subreddits, top pain posts.
3. **Read the pain.** From the JSON, cluster recurring pains (dedupe near-duplicates). Note intensity (score + comment count) and the exact language used.
4. **Turn into deliverables** (the point - "ready to execute"):
   - **Keywords** the market actually types → feed into ads/SEO.
   - **Marketing angles/hooks** - one per top pain, in the market's own words.
   - **Content topics** - the questions people keep asking.
   - **Where to distribute** - the top subreddits/threads worth a genuine, value-adding reply.
   - **Product gaps** - unmet requests → feature candidates for your own backlog.
5. **Report.** Save findings to your vault (e.g. `Projects/<yours>/Market Research/<niche>.md`), linked back to your brain hub. Rank deliverables by impact x effort.

## Guardrails
- **Read-only research.** Never post/vote/DM through any API this touches - distribution is a human decision, made by hand with what this hands you.
- Respect each platform's rate limits and self-promotion rules; don't scrape behind logins.
- Any credentials (e.g. a Reddit API app if you switch to PRAW for cheaper/more reliable access) belong in an env file, chmod 600, never in chat or the vault.

## Invoke
Tell your agent "byakugan on `<niche>`" or run `python3 byakugan.py "<niche>" --locale both`. Sibling skill: `sharingan` (competitor/site analysis).
