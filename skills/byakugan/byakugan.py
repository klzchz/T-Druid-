#!/usr/bin/env python3
# 👁️ BYAKUGAN — market pain-miner (Python). Sees the market's real pain in 360°.
#
# Sources: Reddit (global, EN+PT) + Reclame Aqui (BR, PT). Reddit blocks anon JSON/API
# with 403, so we render the SPA in a real headless browser (Playwright) — same trick
# the Sharingan uses. Reclame Aqui sits behind Cloudflare → playwright-stealth (best effort).
#
# Usage:
#   python3 byakugan.py "<niche / keywords>" [--locale en|pt|both]
#          [--subs sub1,sub2] [--ra empresa1,empresa2] [--deep N] [--out DIR]
# Ex:
#   python3 byakugan.py "watch multiple streams at once" --locale both --deep 8
#   python3 byakugan.py "assistir varias lives" --locale pt --ra "netflix,twitch" --deep 5
#
# Writes <out>/<slug>/byakugan.json (raw + aggregates) and prints a ranked digest
# ending in a READY-TO-EXECUTE block (keywords, subreddits, pain themes).
#
# Deps: playwright (+ browsers cached in ~/.cache/ms-playwright), playwright-stealth.

import argparse, json, re, sys, time, urllib.parse
from collections import Counter
from pathlib import Path

PAIN = {
    "en": ['"i hate"', '"so frustrating"', '"wish there was"', '"is there an app"',
           '"is there a tool"', '"alternative to"', '"tired of"', '"why is there no"',
           '"looking for a way to"', '"anyone know a"'],
    "pt": ['"odeio"', '"que raiva"', '"queria um"', '"existe um app"', '"tem algum site"',
           '"alternativa para"', '"cansei de"', '"por que não existe"', '"alguém sabe como"'],
}
STOP = set(("the a an to of and or for in on is it i you my me we with that this have has do "
    "does can how why what when who be are was were will would just get got not no dont your our "
    "their so too very really any some all as at by from up out about into if then than app apps "
    "de da do dos das um uma que e ou para por com no na em nao não sem meu minha seu sua isso esse "
    "essa como quando quem pra pro mais menos muito ja já se eu voce você tem ter uns umas aos").split())

def log(*a): print(*a, file=sys.stderr, flush=True)

def niche_tokens(niche):
    """Content words of the niche — used to reject off-topic pain-operator false positives."""
    return [w for w in re.split(r"[^a-z0-9à-ú]+", niche.lower()) if len(w) >= 4 and w not in STOP]

def relevant(text, toks):
    if not toks:
        return True
    t = (text or "").lower()
    return any(tok in t for tok in toks)

def load_reddit_env():
    """client_id/secret from ~/.config/tdruid/reddit.env (read-only OAuth). Returns dict or None."""
    p = Path.home() / ".config/tdruid/reddit.env"
    if not p.exists():
        return None
    env = {}
    for line in p.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1); env[k.strip()] = v.strip().strip('"\'')
    if env.get("REDDIT_CLIENT_ID") and env.get("REDDIT_CLIENT_SECRET"):
        return env
    return None

def mine_reddit_praw(env, niche, locales, subs, deep, limit=20):
    """Preferred engine — official read-only API, no browser, gets comments cheaply."""
    import praw
    r = praw.Reddit(client_id=env["REDDIT_CLIENT_ID"], client_secret=env["REDDIT_CLIENT_SECRET"],
                    user_agent=env.get("REDDIT_USER_AGENT", "byakugan-market-research/1.0 by T-Druid"))
    r.read_only = True
    toks = niche_tokens(niche)
    hits, queries = {}, [f'{op} {niche}' for loc in locales for op in PAIN[loc]]
    scopes = ["all"] + subs
    log(f"👁️ Reddit (PRAW) — {len(queries)} queries × {len(scopes)} scope(s)")
    for scope in scopes:
        for q in queries:
            try:
                for s in r.subreddit(scope).search(q, sort="relevance", time_filter="year", limit=limit):
                    if s.permalink in hits:
                        continue
                    if scope == "all" and not relevant(f"{s.title} {s.selftext or ''}", toks):
                        continue
                    hits[s.permalink] = {"title": s.title, "sub": str(s.subreddit),
                        "score": s.score, "comments": s.num_comments,
                        "url": f"https://reddit.com{s.permalink}", "body": (s.selftext or "")[:600],
                        "top_comments": []}
            except Exception as e:
                log("  praw q err:", str(e)[:60])
            sys.stderr.write("."); sys.stderr.flush()
    sys.stderr.write("\n")
    ranked = sorted(hits.values(), key=lambda h: h["score"] + h["comments"], reverse=True)
    if deep > 0:
        for h in ranked[:deep]:
            try:
                sub = r.submission(url=h["url"]); sub.comments.replace_more(limit=0)
                h["top_comments"] = [c.body[:280] for c in sub.comments[:5] if len(c.body) > 25]
            except Exception as e:
                log("  praw deep err:", str(e)[:50])
    return ranked

def new_browser(pw, stealth=False):
    b = pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        locale="pt-BR", viewport={"width": 1366, "height": 900})
    if stealth:
        try:
            from playwright_stealth import Stealth
            Stealth().apply_stealth_sync(ctx)
        except Exception:
            try:
                from playwright_stealth import stealth_sync  # older API
                for p in ctx.pages or [ctx.new_page()]:
                    stealth_sync(p)
            except Exception as e:
                log("  (stealth unavailable:", str(e)[:60], ")")
    return b, ctx

def mine_reddit(ctx, niche, locales, subs, deep, direct=False):
    hits, page = {}, ctx.new_page()
    toks = niche_tokens(niche)
    # direct mode: search the raw term (brand/sentiment); else pain-operator mining.
    queries = [niche] if direct else [f'{op} {niche}' for loc in locales for op in PAIN[loc]]
    queries += [f'subreddit:{s} {niche}' for s in subs]
    log(f"👁️ Reddit — {len(queries)} pain queries")
    for q in queries:
        url = "https://www.reddit.com/search/?q=" + urllib.parse.quote(q) + "&sort=relevance&t=year"
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.mouse.wheel(0, 5000); page.wait_for_timeout(1200)
            rows = page.eval_on_selector_all(
                "a[href*='/comments/']",
                "els => els.map(e=>({t:e.textContent.trim(), h:e.href.split('?')[0]})).filter(x=>x.t.length>15)")
            for r in rows:
                # in direct/brand mode the search term IS the filter — don't also gate on title tokens
                if r["h"] not in hits and (direct or relevant(r["t"], toks)):
                    m = re.search(r"/r/([^/]+)/", r["h"])
                    hits[r["h"]] = {"title": r["t"], "sub": m.group(1) if m else "?", "url": r["h"], "body": "", "top_comments": []}
        except Exception as e:
            log("  q err:", str(e)[:50])
        sys.stderr.write("."); sys.stderr.flush()
    sys.stderr.write("\n")

    ranked = list(hits.values())
    if deep > 0:
        log(f"👁️ Reddit deep — opening top {min(deep,len(ranked))} threads for verbatim pain")
        for h in ranked[:deep]:
            try:
                page.goto(h["url"], wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2500)
                h["body"] = (page.eval_on_selector("div[slot='text-body'], div[data-post-click-location='text-body']",
                             "e => e.innerText") or "")[:600] if page.query_selector("div[slot='text-body']") else ""
                h["top_comments"] = page.eval_on_selector_all(
                    "div[slot='comment'] p, shreddit-comment p",
                    "els => els.map(e=>e.innerText.trim()).filter(t=>t.length>25).slice(0,5)")[:5]
            except Exception as e:
                log("  deep err:", str(e)[:50])
            sys.stderr.write("."); sys.stderr.flush()
        sys.stderr.write("\n")
    page.close()
    return ranked

def mine_reclameaqui(ctx, companies):
    out, page = [], ctx.new_page()
    for comp in companies:
        url = "https://www.reclameaqui.com.br/busca/?q=" + urllib.parse.quote(comp)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=40000)
            page.wait_for_timeout(6000)
            body = page.inner_text("body")[:200]
            if "blocked" in body.lower() or "unable to access" in body.lower():
                log(f"  RA[{comp}]: BLOCKED by Cloudflare (needs a non-headless/residential path)")
                continue
            items = page.eval_on_selector_all(
                "a[href*='/reclamacao/'], article, [class*='complain']",
                "els => els.map(e=>e.textContent.trim()).filter(t=>t.length>25).slice(0,15)")
            for t in dict.fromkeys(items):
                out.append({"company": comp, "text": t[:300]})
            log(f"  RA[{comp}]: {len(items)} items")
        except Exception as e:
            log(f"  RA[{comp}] err:", str(e)[:60])
    page.close()
    return out

def synthesize(niche, reddit_hits, ra_items):
    freq = Counter()
    for h in reddit_hits:
        for w in re.split(r"[^a-z0-9à-ú]+", h["title"].lower()):
            if len(w) >= 4 and w not in STOP:
                freq[w] += 1
    for it in ra_items:
        for w in re.split(r"[^a-z0-9à-ú]+", it["text"].lower()):
            if len(w) >= 4 and w not in STOP:
                freq[w] += 1
    keywords = [w for w, n in freq.most_common(30) if n >= 2]
    subs = Counter(h["sub"] for h in reddit_hits)
    return {"keywords": keywords, "top_subs": subs.most_common(12)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("niche")
    ap.add_argument("--locale", default="both", choices=["en", "pt", "both"])
    ap.add_argument("--subs", default="")
    ap.add_argument("--ra", default="")
    ap.add_argument("--deep", type=int, default=0)
    ap.add_argument("--direct", action="store_true", help="search raw term (brand/sentiment) instead of pain operators")
    ap.add_argument("--engine", default="auto", choices=["auto", "praw", "playwright"])
    ap.add_argument("--out", default=str(Path(__file__).parent / "out"))
    A = ap.parse_args()
    locales = ["en", "pt"] if A.locale == "both" else [A.locale]
    subs = [s.strip() for s in A.subs.split(",") if s.strip()]
    companies = [c.strip() for c in A.ra.split(",") if c.strip()]

    env = load_reddit_env()
    use_praw = A.engine == "praw" or (A.engine == "auto" and env)
    reddit_hits, ra_items = [], []

    if use_praw and env:
        log("engine: PRAW (official read-only API)")
        reddit_hits = mine_reddit_praw(env, A.niche, locales, subs, A.deep)
    else:
        log("engine: Playwright (no Reddit key — browser render). Add ~/.config/tdruid/reddit.env for PRAW.")

    # Playwright still needed for Reclame Aqui, and for Reddit when there's no key.
    if (not use_praw) or companies:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b, ctx = new_browser(pw, stealth=bool(companies))
            if not use_praw:
                reddit_hits = mine_reddit(ctx, A.niche, locales, subs, A.deep, direct=A.direct)
            ra_items = mine_reclameaqui(ctx, companies) if companies else []
            b.close()

    agg = synthesize(A.niche, reddit_hits, ra_items)
    slug = re.sub(r"[^a-z0-9]+", "-", A.niche.lower()).strip("-")[:40]
    d = Path(A.out) / slug; d.mkdir(parents=True, exist_ok=True)
    payload = {"niche": A.niche, "locale": A.locale, "reddit_count": len(reddit_hits),
               "ra_count": len(ra_items), "reddit": reddit_hits, "reclame_aqui": ra_items, **agg}
    (d / "byakugan.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    print(f"\n===== 👁️ BYAKUGAN — niche=\"{A.niche}\" · reddit={len(reddit_hits)} · reclameaqui={len(ra_items)} =====")
    print("\n## KEYWORDS the market actually uses")
    print("  " + "  ".join(agg["keywords"]) if agg["keywords"] else "  (none)")
    print("\n## TOP SUBREDDITS (where the pain lives — go post/answer here)")
    for s, n in agg["top_subs"]: print(f"  r/{s} ({n})")
    print("\n## TOP PAIN POSTS")
    for i, h in enumerate(reddit_hits[:20], 1):
        print(f"{i:2}. r/{h['sub']} :: {h['title'][:90]}")
        if h.get("body"): print(f'     body: "{h["body"][:160]}"')
        for c in h.get("top_comments", [])[:2]: print(f'     ↳ "{c[:150]}"')
        print(f"     {h['url']}")
    if ra_items:
        print("\n## RECLAME AQUI (BR complaints = paying-customer pain)")
        for it in ra_items[:15]: print(f"  [{it['company']}] {it['text'][:140]}")
    print(f"\n(raw → skills/byakugan/out/{slug}/byakugan.json)")

if __name__ == "__main__":
    main()
