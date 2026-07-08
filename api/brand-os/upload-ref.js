// Brand OS — reference image upload for the Art Director.
//
// POST /api/brand-os/upload-ref?filename=<name>
//   Content-Type: image/*
//   Body: raw file bytes (≤4 MB — Vercel's serverless body ceiling)
//   → { url } — a public URL suitable for Magnific's
//              style_reference / structure_reference fields.
//
// Requires an authenticated session (client or admin) and a valid brand slug.
// Reference images are stored under brand-os/refs/<slug>/... in Vercel Blob.

import { put } from '@vercel/blob';
import { verify, readCookie } from '../../lib/brand-os-auth.js';

export const config = {
  api: { bodyParser: false },
  maxDuration: 30,
};

const MAX_BYTES = 4 * 1024 * 1024;
const OK_TYPES = /^image\/(jpeg|png|webp|gif)$/i;

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });

  const secret = process.env.AUTH_SECRET;
  if (!secret) return res.status(500).json({ error: 'AUTH_SECRET not configured' });
  if (!process.env.BLOB_READ_WRITE_TOKEN) {
    return res.status(500).json({ error: 'Vercel Blob storage not configured. Add a Blob store in Vercel → Storage.' });
  }

  const payload = await verify(readCookie(req.headers.cookie || ''), secret);
  if (!payload) return res.status(401).json({ error: 'Not signed in' });

  const url = new URL(req.url, 'http://x');
  const filename = (url.searchParams.get('filename') || 'ref').slice(0, 120);
  const slug = url.searchParams.get('slug') || payload.slug;
  if (payload.role !== 'admin' && payload.slug !== slug) {
    return res.status(403).json({ error: 'Session does not match slug' });
  }

  const contentType = (req.headers['content-type'] || '').split(';')[0].trim();
  if (!OK_TYPES.test(contentType)) {
    return res.status(400).json({ error: 'Only jpeg / png / webp / gif accepted' });
  }

  // Stream body → buffer, enforcing the size cap as we go.
  const chunks = [];
  let total = 0;
  try {
    for await (const chunk of req) {
      total += chunk.length;
      if (total > MAX_BYTES) return res.status(413).json({ error: 'Max 4 MB per reference' });
      chunks.push(chunk);
    }
  } catch (e) {
    return res.status(400).json({ error: 'Upload failed: ' + e.message });
  }
  const buf = Buffer.concat(chunks);
  if (!buf.length) return res.status(400).json({ error: 'Empty upload' });

  const safeName = filename.replace(/[^a-zA-Z0-9._-]/g, '_');
  const stamp = Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8);
  const path = `brand-os/refs/${slug}/${stamp}-${safeName}`;

  try {
    const blob = await put(path, buf, {
      access: 'public',
      contentType,
      addRandomSuffix: false,
    });
    return res.status(200).json({ url: blob.url, path });
  } catch (e) {
    return res.status(500).json({ error: 'Blob upload failed: ' + e.message });
  }
}
