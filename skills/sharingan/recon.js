// Sharingan (Itachi) — competitor recon via Playwright (headless Chromium).
// Usage: node recon.js <url> [locale]
// Opens the page, full-page screenshot, and extracts UX/feature/pricing/tech
// signals into recon.json. Copy IDEAS & FUNCTIONALITY — never source/assets/content.
const { chromium } = require('playwright')
const fs = require('fs')
const path = require('path')

;(async () => {
  const url = process.argv[2]
  const locale = process.argv[3] || 'en-US'
  if (!url) {
    console.error('usage: node recon.js <url> [locale]')
    process.exit(1)
  }
  const host = new URL(url).hostname.replace(/^www\./, '')
  const outdir = path.join(__dirname, 'out', host)
  fs.mkdirSync(outdir, { recursive: true })

  const browser = await chromium.launch({ headless: true })
  const ctx = await browser.newContext({ locale, viewport: { width: 1366, height: 2200 } })
  const page = await ctx.newPage()
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {})
  await page.waitForTimeout(2000)

  const shot = path.join(outdir, 'home.png')
  await page.screenshot({ path: shot, fullPage: true }).catch(() => {})

  const data = await page.evaluate(() => {
    const txt = (el) => (el?.textContent || '').trim().replace(/\s+/g, ' ')
    const pick = (sel, n = 40) => [...document.querySelectorAll(sel)].slice(0, n).map(txt).filter(Boolean)
    const attrs = (sel, a, n = 60) => [...document.querySelectorAll(sel)].slice(0, n).map((e) => e.getAttribute(a)).filter(Boolean)
    const currencyRe = /(?:R\$|US?\$|€|£|¥|₩|฿|₹)\s?\d[\d.,]*/g
    const body = document.body?.innerText || ''
    const html = document.documentElement.outerHTML
    return {
      title: document.title,
      metaDesc: document.querySelector('meta[name=description]')?.content || '',
      generator: document.querySelector('meta[name=generator]')?.content || '',
      og: {
        title: document.querySelector('meta[property="og:title"]')?.content || '',
        desc: document.querySelector('meta[property="og:description"]')?.content || '',
      },
      headings: { h1: pick('h1', 10), h2: pick('h2', 25) },
      nav: [...new Set(pick('nav a, header a', 40))],
      ctas: [...new Set(pick('button, a.btn, [class*=btn], [class*=cta]', 40))],
      pricesSeen: [...new Set(body.match(currencyRe) || [])].slice(0, 25),
      scripts: [...new Set(attrs('script[src]', 'src', 80))],
      iframes: [...new Set(attrs('iframe', 'src', 25))],
      videoSrcs: [...new Set(attrs('video, video source', 'src', 25))],
      hlsHints: [...new Set(html.match(/[^"'\s]+\.m3u8[^"'\s]*/g) || [])].slice(0, 10),
      forms: pick('form button[type=submit], form [type=submit], form button', 12),
    }
  }).catch((e) => ({ error: String(e) }))

  fs.writeFileSync(path.join(outdir, 'recon.json'), JSON.stringify(data, null, 2))
  console.log('HOST:', host)
  console.log('SCREENSHOT:', shot)
  console.log('JSON:', path.join(outdir, 'recon.json'))
  console.log('----- EXTRACT -----')
  console.log(JSON.stringify(data, null, 2))
  await browser.close()
})()
