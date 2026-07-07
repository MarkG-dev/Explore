#!/usr/bin/env node
// Scrape one or more Cosmos boards and download every visible image
// to disk. Emits a manifest.json describing what was pulled.
//
// Usage:
//   node scrape-cosmos.mjs --urls "url1,url2" --out ./moodboard [--max 30]
//
// Requires: `playwright` (or `playwright-core` with a system Chromium),
//           Node 20+, fs access.

import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { extname } from 'node:path';
import { parseArgs } from 'node:util';

const { values } = parseArgs({
  options: {
    urls: { type: 'string' },
    out:  { type: 'string' },
    max:  { type: 'string', default: '30' },
  },
});

if (!values.urls || !values.out) {
  console.error('usage: scrape-cosmos.mjs --urls "url1,url2" --out ./moodboard [--max 30]');
  process.exit(2);
}

const urls = values.urls.split(',').map(s => s.trim()).filter(Boolean);
const outDir = values.out;
const maxPerBoard = parseInt(values.max, 10);

await mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 BrandAgent/1.0',
  viewport: { width: 1440, height: 2400 },
});

const manifest = { boards: [], images: [] };

try {
  for (const boardUrl of urls) {
    if (!/^https?:\/\/(www\.)?cosmos\.so\//i.test(boardUrl)) {
      console.error(`skip: not a cosmos.so URL — ${boardUrl}`);
      continue;
    }

    const page = await context.newPage();
    console.error(`→ ${boardUrl}`);

    try {
      await page.goto(boardUrl, { waitUntil: 'networkidle', timeout: 45000 });
    } catch (e) {
      console.error(`  goto failed: ${e.message}`);
      await page.close();
      manifest.boards.push({ url: boardUrl, error: e.message, count: 0 });
      continue;
    }

    await page.waitForTimeout(1500);

    // Scroll to force lazy-load. Cosmos uses infinite-scroll.
    await page.evaluate(async (max) => {
      let lastHeight = 0;
      for (let i = 0; i < 20; i++) {
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(r => setTimeout(r, 700));
        const h = document.body.scrollHeight;
        if (h === lastHeight) break;
        lastHeight = h;
        if (document.querySelectorAll('img').length >= max * 3) break;
      }
    }, maxPerBoard);

    const imgs = await page.$$eval('img', els =>
      els
        .map(e => ({
          src: e.currentSrc || e.src || '',
          w: e.naturalWidth || 0,
          h: e.naturalHeight || 0,
        }))
        .filter(x => x.src && /^https?:\/\//.test(x.src))
    );

    const title = await page.title().catch(() => '');
    await page.close();

    // Rank: bigger images first, filter out avatar/icon-y URLs and tiny thumbs.
    const ranked = imgs
      .filter(i => !/favicon|avatar|logo|sprite|icon-/i.test(i.src))
      .filter(i => i.w === 0 || i.w >= 200)
      .sort((a, b) => (b.w * b.h) - (a.w * a.h))
      .slice(0, maxPerBoard);

    const boardEntry = { url: boardUrl, title, count: 0, images: [] };

    for (const { src } of ranked) {
      try {
        const r = await fetch(src, {
          headers: { 'user-agent': 'Mozilla/5.0 BrandAgent/1.0' },
        });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const buf = Buffer.from(await r.arrayBuffer());
        const hash = createHash('sha1').update(buf).digest('hex').slice(0, 12);
        const ext = pickExt(src, r.headers.get('content-type'));
        const fname = `${hash}${ext}`;
        await writeFile(`${outDir}/${fname}`, buf);
        boardEntry.images.push({ file: fname, src, bytes: buf.length });
        manifest.images.push({ file: fname, src, source: boardUrl });
        boardEntry.count++;
      } catch (e) {
        console.error(`  download failed: ${src.slice(0, 80)} — ${e.message}`);
      }
    }

    console.error(`  ${boardEntry.count} downloaded`);
    manifest.boards.push(boardEntry);
  }
} finally {
  await browser.close();
}

await writeFile(
  `${outDir}/manifest.json`,
  JSON.stringify(manifest, null, 2),
);

console.log(JSON.stringify({
  outDir,
  totalImages: manifest.images.length,
  boards: manifest.boards.map(b => ({ url: b.url, count: b.count })),
}, null, 2));

function pickExt(url, ct) {
  const e = extname(new URL(url).pathname).toLowerCase();
  if (['.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif'].includes(e)) return e;
  if (ct?.includes('jpeg')) return '.jpg';
  if (ct?.includes('png'))  return '.png';
  if (ct?.includes('webp')) return '.webp';
  if (ct?.includes('avif')) return '.avif';
  return '.img';
}
