// Vercel serverless function: Magnific API proxy.
// Submits an upscale/restyle job and polls to completion.
//
// Body: {
//   apiKey, image, prompt, engine, scale,
//   creativity, hdr, resemblance, fractality
// }
//
// image may be an https:// URL or a data URL (data:image/...;base64,...)
//
// Magnific reference:
//   POST https://api.magnific.ai/v1/upscale  → { id }
//   GET  https://api.magnific.ai/v1/status/:id → { status, url|image_url }
// (If these change, adjust the constants below.)

export const config = {
  maxDuration: 60,
};

const MAG_BASE = 'https://api.magnific.ai/v1';
const POLL_INTERVAL_MS = 2000;
const POLL_TIMEOUT_MS = 55000;

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });

  const {
    apiKey, image, prompt = '',
    engine = 'magnific_sparkle',
    scale = 2,
    creativity = 4,
    hdr = 3,
    resemblance = 6,
    fractality = 2,
  } = req.body || {};

  if (!apiKey) return res.status(400).json({ error: 'Missing apiKey' });
  if (!image)  return res.status(400).json({ error: 'Missing image' });

  try {
    // 1. Submit the job.
    const submitRes = await fetch(`${MAG_BASE}/upscale`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        image,                     // Magnific accepts URL or base64 data URL
        prompt,
        engine,
        scale_factor: scale,
        creativity,
        hdr,
        resemblance,
        fractality,
      }),
    });

    const submitData = await submitRes.json();
    if (!submitRes.ok) {
      return res.status(submitRes.status).json({
        error: submitData.error || submitData.message || 'Magnific submit failed',
        raw: submitData,
      });
    }

    const jobId = submitData.id || submitData.job_id;
    if (!jobId) return res.status(500).json({ error: 'No job id returned', raw: submitData });

    // 2. Poll to completion.
    const start = Date.now();
    while (Date.now() - start < POLL_TIMEOUT_MS) {
      await new Promise(r => setTimeout(r, POLL_INTERVAL_MS));
      const statusRes = await fetch(`${MAG_BASE}/status/${jobId}`, {
        headers: { 'authorization': `Bearer ${apiKey}` },
      });
      const statusData = await statusRes.json();
      if (!statusRes.ok) {
        return res.status(statusRes.status).json({
          error: statusData.error || 'Magnific status failed',
          raw: statusData,
        });
      }
      const state = (statusData.status || '').toLowerCase();
      if (state === 'completed' || state === 'succeeded' || state === 'done') {
        const imageUrl = statusData.url || statusData.image_url || statusData.output;
        return res.status(200).json({ imageUrl, jobId, raw: statusData });
      }
      if (state === 'failed' || state === 'error') {
        return res.status(500).json({ error: 'Magnific job failed', raw: statusData });
      }
    }

    return res.status(504).json({ error: 'Magnific job timed out; try again or check dashboard', jobId });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
