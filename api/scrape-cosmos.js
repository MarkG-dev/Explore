// Vercel serverless function: scrape Cosmos boards for image URLs.
// Body: { urls: string[] }
//
// Strategy:
//   1. Try Playwright (headless Chromium) for JS-rendered content.
//   2. If Playwright is unavailable / times out, fall back to a plain fetch
//      and pull image URLs out of the HTML/Next.js JSON payload.

export const config = {
  maxDuration: 60,
};

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });

  const { urls } = req.body || {};
  if (!Array.isArray(urls) || urls.length === 0) {
    return res.status(400).json({ error: 'Provide urls[]' });
  }

  const results = [];
  const errors = [];

  for (const url of urls) {
    if (!/^https?:\/\/(www\.)?cosmos\.so\//i.test(url)) {
      errors.push({ url, error: 'Not a cosmos.so URL' });
      continue;
    }
    try {
      let images = await scrapeWithPlaywright(url).catch(() => null);
      if (!images || images.length === 0) {
        images = await scrapeWithFetch(url);
      }
      results.push(...images.map(u => ({ url: u, source: url })));
    } catch (e) {
      errors.push({ url, error: e.message });
    }
  }

  // Dedupe by URL
  const seen = new Set();
  const deduped = results.filter(r => {
    if (seen.has(r.url)) return false;
    seen.add(r.url);
    return true;
  });

  return res.status(200).json({ images: deduped, errors });
}

async function scrapeWithPlaywright(url) {
  let chromium, playwright;
  try {
    chromium = (await import('@sparticuz/chromium')).default;
    playwright = await import('playwright-core');
  } catch (e) {
    return null; // deps not present, fall back
  }

  const browser = await playwright.chromium.launch({
    args: chromium.args,
    executablePath: await chromium.executablePath(),
    headless: true,
  });

  try {
    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (BrandAgent) AppleWebKit/537.36',
      viewport: { width: 1280, height: 2000 },
    });
    const page = await context.newPage();
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

    // Give the grid a moment to hydrate.
    await page.waitForTimeout(1500);

    // Scroll to force lazy-loaded thumbnails.
    await page.evaluate(async () => {
      for (let y = 0; y < 4000; y += 600) {
        window.scrollTo(0, y);
        await new Promise(r => setTimeout(r, 300));
      }
    });

    const imgs = await page.$$eval('img', els =>
      els
        .map(e => e.currentSrc || e.src || '')
        .filter(u => u && /^https?:\/\//.test(u))
    );

    return normalizeUrls(imgs);
  } finally {
    await browser.close().catch(() => {});
  }
}

async function scrapeWithFetch(url) {
  const r = await fetch(url, {
    headers: {
      'user-agent': 'Mozilla/5.0 (BrandAgent) AppleWebKit/537.36',
      'accept': 'text/html,application/xhtml+xml',
    },
  });
  if (!r.ok) throw new Error(`Fetch failed: ${r.status}`);
  const html = await r.text();

  const found = new Set();

  // <meta property="og:image" ...>
  const og = html.match(/property=["']og:image["']\s+content=["']([^"']+)["']/gi) || [];
  og.forEach(m => {
    const v = m.match(/content=["']([^"']+)["']/i);
    if (v) found.add(v[1]);
  });

  // Any URL to Cosmos's image CDN or common providers used in the payload.
  const cdnRe = /https?:\/\/[^"'\s)>]+\.(?:jpg|jpeg|png|webp|avif)(?:\?[^"'\s)>]*)?/gi;
  const matches = html.match(cdnRe) || [];
  matches.forEach(u => found.add(u));

  // Strip obvious non-content assets (icons, avatars).
  return normalizeUrls([...found].filter(u =>
    !/favicon|sprite|logo|apple-touch|icon-|avatar/i.test(u)
  ));
}

function normalizeUrls(list) {
  const clean = [];
  const seen = new Set();
  for (const u of list) {
    const trimmed = u.split('#')[0];
    if (seen.has(trimmed)) continue;
    seen.add(trimmed);
    clean.push(trimmed);
  }
  return clean;
}
