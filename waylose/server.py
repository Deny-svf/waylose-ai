"""Tiny stdlib HTTP demo endpoint for waylose.ai (no auth, no keys).

  GET /                      — agent info
  GET /health                — {"ok": true}
  GET /status                — verified agent stats (on-chain results)
  GET /audit?address=0x...   — live read-only audit triage as JSON

Run:  python3 -m waylose.server   (PORT env var, default 8080)
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from .audit import audit

AGENT = {
    "name": "waylose.ai",
    "agent_id": "waylose.ai",
    "chains": ["BNB Chain (56)", "Robinhood Chain (4663)"],
    "wallet": "0xcD5676cEEA5E5acF8518CAd820A1B2e9818e5255",
    "mode": "free-first mint hunter: audit -> mint -> verify -> list",
}

STATUS = {
    "agent": "waylose.ai",
    "wojak_claimed": "12,500,000 $WOJAK (free Agent ID mint, 2026-11-11)",
    "agc_pool_b": "596,381 / 927,500 AGC claimed (claim #9, 2026-11-14)",
    "free_mints_listed": ["Hopkin Genesis #2251", "Eclipse Court Genesis #48",
                          "RIGAI Badge #331"],
    "rules": ["free first", "paid only with explicit approval",
              "preview before money moves", "verify on-chain after every tx"],
}


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802 - http.server naming
        p = urlparse(self.path)
        if p.path == "/":
            self._json(AGENT)
        elif p.path == "/health":
            self._json({"ok": True})
        elif p.path == "/status":
            self._json(STATUS)
        elif p.path == "/audit":
            addr = parse_qs(p.query).get("address", [None])[0]
            if not addr or not addr.startswith("0x") or len(addr) != 42:
                self._json({"error": "pass ?address=0x... (42 chars)"}, 400)
                return
            try:
                self._json(audit(addr))
            except Exception as e:  # noqa: BLE001 - surface as JSON
                self._json({"error": str(e)}, 502)
        else:
            self._json({"error": "not found"}, 404)

    def log_message(self, *args):  # keep stdout clean
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
