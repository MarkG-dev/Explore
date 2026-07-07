// Vercel serverless function: proxy to Anthropic Messages API.
// Body: { apiKey, system, messages, max_tokens, model? }

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'POST only' });
  }
  try {
    const { apiKey, system, messages, max_tokens = 2000, model } = req.body || {};
    if (!apiKey) return res.status(400).json({ error: 'Missing apiKey' });
    if (!messages || !Array.isArray(messages)) return res.status(400).json({ error: 'Missing messages' });

    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: model || 'claude-opus-4-8',
        max_tokens,
        system,
        messages,
      }),
    });

    const data = await r.json();
    if (!r.ok) {
      return res.status(r.status).json({ error: data.error?.message || 'Anthropic error', raw: data });
    }
    const text = (data.content || [])
      .filter(b => b.type === 'text')
      .map(b => b.text)
      .join('\n');
    return res.status(200).json({ text, stop_reason: data.stop_reason });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
