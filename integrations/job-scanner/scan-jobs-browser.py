#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generic template: scan job boards that only render their listings via
JavaScript (a plain HTTP fetch just gets the empty page shell) using a real,
clean, headless Chromium via Playwright.

Deliberately does NOT reuse your personal logged-in browser session. It's
tempting to want to "just use my Chrome session" for sites like LinkedIn,
but automating on top of a real logged-in account is exactly what gets
accounts flagged/restricted for bot-like behavior. A fresh, anonymous
browser profile gets you the same public listings (these boards don't
require login to browse) without that risk.

Install once:
    pip install playwright
    playwright install chromium

Usage: scan-jobs-browser.py
"""
import re
import sys

from playwright.sync_api import sync_playwright

UA = "Mozilla/5.0 (job-scanner template)"
KEYWORDS = re.compile(r"backend|full[- ]?stack|python|typescript|node\.?js", re.I)


def yc_jobs(page):
    """Y Combinator's jobs board is a client-rendered React app."""
    found = []
    try:
        page.goto("https://www.ycombinator.com/jobs/role/software-engineer",
                  wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        for card in page.locator("a[href*='/companies/'][href*='/jobs/']").all():
            try:
                text, href = card.inner_text(timeout=2000).strip(), card.get_attribute("href")
            except Exception:
                continue
            if not text or not href or not KEYWORDS.search(text):
                continue
            title = text.splitlines()[0][:120]
            found.append({"title": title, "source": "YC",
                          "url": "https://www.ycombinator.com" + href if href.startswith("/") else href})
    except Exception as e:
        print(f"YC failed: {e}", file=sys.stderr)
    return found


def linkedin_public_search(page, keywords="Node.js", location="Brazil", remote_only=True):
    """LinkedIn's public job search — no login needed to browse."""
    found = []
    try:
        wt = "&f_WT=2" if remote_only else ""
        page.goto(f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}{wt}",
                  wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        for card in page.locator("li div.base-card").all()[:25]:
            try:
                title = card.locator("h3").first.inner_text(timeout=1500).strip()
                company = card.locator("h4").first.inner_text(timeout=1500).strip()
                href = card.locator("a.base-card__full-link").first.get_attribute("href")
            except Exception:
                continue
            if not title or not KEYWORDS.search(title):
                continue
            found.append({"title": f"{title} @ {company}", "source": "LinkedIn",
                          "url": (href or "").split("?")[0]})
    except Exception as e:
        print(f"LinkedIn failed: {e}", file=sys.stderr)
    return found


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=UA)
        page = ctx.new_page()
        jobs = yc_jobs(page) + linkedin_public_search(page)
        browser.close()

    for j in jobs:
        print(f"[{j['source']}] {j['title']}\n  {j['url']}")
    print(f"\n{len(jobs)} matching posting(s).", file=sys.stderr)


if __name__ == "__main__":
    main()
