// Brand OS — public brand name lookup.
//
// GET /api/brand-os/brand-name?slug=<x>
//   → { slug, name }
//
// Public — no auth required. Only returns the display name so a
// pre-login page (e.g. spacecadet.studio/loopx) can render the brand
// title before the user enters their password.

import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'GET only' });

  const url = new URL(req.url, 'http://x');
  const slug = url.searchParams.get('slug');
  if (!slug) return res.status(400).json({ error: 'slug required' });
  if (!/^[a-z][a-z0-9-]{1,40}$/.test(slug)) {
    return res.status(400).json({ error: 'invalid slug' });
  }

  try {
    const raw = await readFile(join(process.cwd(), 'brands', `${slug}.json`), 'utf8');
    const brand = JSON.parse(raw);
    return res.status(200).json({ slug: brand.slug || slug, name: brand.name || slug });
  } catch {
    return res.status(404).json({ error: 'Brand not found' });
  }
}
