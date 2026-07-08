// Brand OS — client-facing brand hub data.
//
// GET /api/brand-os/hub?slug=<x>
//   Returns the public subset of the brand config the hub UI needs:
//     name, slug, tagline, assets, palette (for accent colors), key strategy lines.
//   Does NOT return voice guidelines, examples, do-not-use, prompt templates,
//   passwordHash, or model choices — those are admin-only via /brands.
//
// Access: any authenticated session whose slug matches, OR any admin.

import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { verify, readCookie } from '../../lib/brand-os-auth.js';

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'GET only' });

  const secret = process.env.AUTH_SECRET;
  if (!secret) return res.status(500).json({ error: 'AUTH_SECRET not configured' });

  const payload = await verify(readCookie(req.headers.cookie || ''), secret);
  if (!payload) return res.status(401).json({ error: 'Not signed in' });

  const url = new URL(req.url, 'http://x');
  const slug = url.searchParams.get('slug');
  if (!slug) return res.status(400).json({ error: 'slug required' });

  if (payload.role !== 'admin' && payload.slug !== slug) {
    return res.status(403).json({ error: 'Session does not match slug' });
  }

  try {
    const brand = JSON.parse(await readFile(join(process.cwd(), 'brands', `${slug}.json`), 'utf8'));
    return res.status(200).json({
      name: brand.name,
      slug: brand.slug,
      tagline: brand.strategy?.belief || brand.strategy?.positioning?.split(/\.|—/)[0] || '',
      strategy: {
        positioning: brand.strategy?.positioning || '',
        belief: brand.strategy?.belief || '',
      },
      palette: brand.art?.palette || [],
      assets: brand.assets || {},
    });
  } catch {
    return res.status(404).json({ error: `Brand ${slug} not found` });
  }
}
