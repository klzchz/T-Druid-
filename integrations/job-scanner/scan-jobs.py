#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generic template: scan a few real, structured job sources for postings
matching your own keywords, and print them (or wire them into your own task
tracker / notification channel — see the bottom of `main()`).

Deliberately uses STRUCTURED APIs/feeds instead of scraping HTML or trusting
search-engine snippets: RemoteOK's own JSON API, an RSS feed, and any
Greenhouse-hosted company's public jobs API. Search snippets and single
scraped job-posting URLs rot fast (closed postings, wrong region, dead
links) — structured, official endpoints don't.

Edit KEYWORDS and GREENHOUSE_BOARDS for your own search. A Greenhouse
board's token is the last segment of its public URL, e.g.
`job-boards.greenhouse.io/<token>`.
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

UA = "Mozilla/5.0 (job-scanner template)"

# Replace with your own keywords.
KEYWORDS = re.compile(r"backend|full[- ]?stack|python|typescript|node\.?js", re.I)

# Add any Greenhouse-hosted company you want to track.
GREENHOUSE_BOARDS = []


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def remoteok():
    found = []
    try:
        jobs = json.loads(fetch("https://remoteok.com/api"))
    except Exception as e:
        print(f"RemoteOK failed: {e}", file=sys.stderr)
        return found
    for j in jobs:
        if not isinstance(j, dict) or "position" not in j:
            continue
        if not KEYWORDS.search(j.get("position", "")):
            continue
        found.append({
            "title": f"{j['position']} @ {j.get('company', '?')}",
            "url": j.get("url") or j.get("apply_url") or "",
            "source": "RemoteOK",
        })
    return found


def weworkremotely():
    found = []
    try:
        root = ET.fromstring(fetch("https://weworkremotely.com/categories/remote-programming-jobs.rss"))
    except Exception as e:
        print(f"WeWorkRemotely failed: {e}", file=sys.stderr)
        return found
    for item in root.iter("item"):
        title_el, link_el = item.find("title"), item.find("link")
        if title_el is None or not title_el.text or not KEYWORDS.search(title_el.text):
            continue
        found.append({"title": title_el.text.strip(),
                      "url": link_el.text if link_el is not None else "",
                      "source": "WeWorkRemotely"})
    return found


def greenhouse():
    """Public API, always-current, real absolute URLs (no link rot)."""
    found = []
    for token in GREENHOUSE_BOARDS:
        try:
            jobs = json.loads(fetch(
                f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true")).get("jobs", [])
        except Exception as e:
            print(f"Greenhouse/{token} failed: {e}", file=sys.stderr)
            continue
        for j in jobs:
            title = j.get("title", "")
            if not KEYWORDS.search(title):
                continue
            loc = (j.get("location") or {}).get("name", "N/A")
            found.append({"title": f"{title} @ {token} ({loc})",
                          "url": j.get("absolute_url", ""),
                          "source": "Greenhouse"})
    return found


def main():
    jobs = remoteok() + weworkremotely() + greenhouse()
    for j in jobs:
        print(f"[{j['source']}] {j['title']}\n  {j['url']}")
    print(f"\n{len(jobs)} matching posting(s).", file=sys.stderr)

    # Wire this into your own system instead of just printing, e.g.:
    #   - create a task in your tracker
    #   - append to a markdown note in your vault
    #   - post to a Discord/Slack webhook
    # Keep it mechanical (no LLM call) so it's cheap to run on a cron.


if __name__ == "__main__":
    main()
