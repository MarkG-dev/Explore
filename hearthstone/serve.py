#!/usr/bin/env python3
"""Local server that matches production routing exactly.

Use this rather than `python3 -m http.server`, and rather than opening index.html
directly. Two reasons:

1. `file://` does not work. Browsers block fetch() from an opaque origin, so every
   dataset silently comes back empty. The paths are correct; the browser refuses
   the read. You need HTTP.

2. Plain `http.server` does NOT reproduce production. Vercel's rewrite serves the
   page AT /hearthstone with no redirect, while http.server 301s /hearthstone to
   /hearthstone/. That difference hid a real bug: relative data paths resolved
   against / in production and 404'd. This server applies the same rewrites from
   vercel.json without redirecting, so what you see locally is what deploys.

Usage:
    python3 hearthstone/serve.py            # http://127.0.0.1:8000/hearthstone
    python3 hearthstone/serve.py --port 9000
"""
import argparse
import functools
import http.server
import json
import os
import socketserver
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_rewrites():
    """Read vercel.json so local routing cannot drift from production."""
    path = os.path.join(REPO, "vercel.json")
    table = {}
    if not os.path.exists(path):
        return {"/hearthstone": "/hearthstone/index.html"}
    try:
        cfg = json.load(open(path))
    except Exception as e:
        print(f"[warn] could not parse vercel.json ({e}); using default route", file=sys.stderr)
        return {"/hearthstone": "/hearthstone/index.html"}
    for r in cfg.get("rewrites", []):
        src, dst = r.get("source", ""), r.get("destination", "")
        # skip the parameterised catch-all; it is not useful locally
        if ":" in src or ":" in dst:
            continue
        table[src] = dst
    return table


class Handler(http.server.SimpleHTTPRequestHandler):
    rewrites = {}

    def translate_path(self, path):
        clean = path.split("?", 1)[0].split("#", 1)[0].rstrip("/") or "/"
        if clean in self.rewrites:
            path = self.rewrites[clean]
        return super().translate_path(path)

    def end_headers(self):
        # never cache during development; stale JSON is a confusing bug to chase
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        msg = fmt % args
        if " 404 " in msg or " 500 " in msg:
            print("  MISS:", msg, file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args()

    Handler.rewrites = load_rewrites()
    handler = functools.partial(Handler, directory=REPO)
    socketserver.TCPServer.allow_reuse_address = True

    missing = [f for f in ("hearthstone/data/cards_lite.json",
                           "hearthstone/data/manifest.json")
               if not os.path.exists(os.path.join(REPO, f))]
    if missing:
        print("[warn] missing data files -- the site will render empty:", file=sys.stderr)
        for m in missing:
            print(f"         {m}", file=sys.stderr)
        print("       run scripts/build_history.py then scripts/extract_cards.py,\n"
              "       or restore them from git.", file=sys.stderr)

    with socketserver.TCPServer((a.host, a.port), handler) as srv:
        print(f"serving {REPO}")
        print(f"  study     http://{a.host}:{a.port}/hearthstone")
        print(f"  prototype http://{a.host}:{a.port}/hearthstone/prototype/  (once built)")
        print(f"  routing   {len(Handler.rewrites)} rewrites from vercel.json, no redirects")
        print("Ctrl-C to stop.")
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


if __name__ == "__main__":
    main()
