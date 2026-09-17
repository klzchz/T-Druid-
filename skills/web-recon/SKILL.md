---
name: web-recon
description: Open any website headlessly (Playwright/Chromium), screenshot it, and extract its UX, features, pricing, and tech signals into a structured report. Use when asked to study/analyze a competitor's or reference site, e.g. "recon on <url>", "what does <site> do", "analyze this site's pricing/onboarding".
---

# 🔍 Web Recon — competitor/reference site analysis

Study *techniques*, not the body. **Copy ideas, features, and UX patterns (legal) — never source code, assets, brand, or protected content.** Never help build anything illegal a reference site might be doing (e.g. piracy) — flag it as a risk instead.

## Tooling
- Headless Chromium via Playwright. Install once: `npm install` in this skill's folder (installs `playwright`), then `npx playwright install chromium`.
- Recon helper: `recon.js` in this folder → screenshot + structured extract.

## Procedure
1. **Recon.** For each target URL run:
   `node recon.js "<url>" [locale]`
   Writes `out/<host>/home.png` + `out/<host>/recon.json` (title, headings, nav, CTAs, prices, script srcs = tech/CDN hints, iframes = embeds, forms). View the screenshot and share it when useful.
2. **Go deeper if needed.** Write a one-off Playwright script to walk key flows (pricing page, signup/onboarding, the core product) and screenshot each. Use a persistent context (`--user-data-dir`) only if a logged-in view is required and you have explicit permission/credentials for that account — never reuse someone else's live session without their knowledge.
3. **Analyze.** For each notable feature: what it does → how it likely works (from DOM/scripts/network) → effort to replicate in your own stack → impact for your product.
4. **Report.** Save findings to your vault (e.g. `Projects/<yours>/Competitor Intel/<site>.md`), linked back to your brain hub. Rank "what to learn from" by impact × effort.

## Guardrails (legal — do not skip)
- Functionality, UX flows, copy structure, pricing strategy, onboarding patterns = fair to learn from and reimplement in your own code.
- Do NOT copy: source code verbatim, images/fonts/assets, trademarks/logos, or any protected content.
- Do NOT build anything illegal (e.g. piracy) even if a reference site does it — note it as a legal risk and move on.
- Light recon only; don't hammer a site, respect its `robots.txt`/ToS.

## Invoke
Tell your agent "recon on `<url>`" or "web-recon `<url>` — focus on `<area>`".
