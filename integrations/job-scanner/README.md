# Job scanner templates

Two scripts, two problems:

- **`scan-jobs.py`** — structured-API scanner (RemoteOK's JSON API, WeWorkRemotely's RSS, any Greenhouse-hosted company's public jobs API). No browser needed. Reliable and fast; the tradeoff is it only covers sources with a real API/feed.
- **`scan-jobs-browser.py`** — for boards that only render via JavaScript (Y Combinator's jobs page, LinkedIn's public search). Uses a real headless Chromium (Playwright) with a **clean, anonymous profile** — deliberately not your own logged-in session (see the docstring for why).

## A note on "auto-apply" bots

It's tempting to go one step further and have the agent submit applications automatically. As of 2026, that's a bad idea: ATS platforms increasingly detect and spam-flag mass-submitted applications, and doing it under a real identity risks getting that identity blacklisted across recruiting databases. The "cyborg" model — the agent sources and prepares, a human does the final, personalized submission — is what actually works. These scripts stop at "here's a curated, verified list"; wire the final send-off yourself.

## Combining with the email-report template

Pipe either script's output into `../email-report/send-report.py` to get a periodic curated shortlist emailed to yourself with your resume attached.
