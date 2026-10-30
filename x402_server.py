#!/usr/bin/env python3
"""Paid readme-doctor API (x402). POST /score with README text.
No/invalid payment -> HTTP 402 with payment requirements. Valid -> verify+settle via facilitator, then score.
Env: FACILITATOR_URL (default https://x402.org/facilitator), PRICE_ATOMIC (default 10000 = 0.01 USDC), NETWORK (default base).
payTo is hard-coded to the creator's Base wallet."""
import json, os, sys, base64, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from server import score

PAY_TO = "0xdee5d17120fe5b415858c977555fd0c4ed6d3fda"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
FAC = os.environ.get("FACILITATOR_URL", "https://x402.org/facilitator")
PRICE = os.environ.get("PRICE_ATOMIC", "10000")
NETWORK = os.environ.get("NETWORK", "base")

def requirements(resource):
    return {"scheme": "exact", "network": NETWORK, "maxAmountRequired": PRICE, "resource": resource,
            "description": "Score a README.md (0-100) with concrete fixes", "mimeType": "application/json",
            "payTo": PAY_TO, "maxTimeoutSeconds": 60, "asset": USDC_BASE,
            "extra": {"name": "USD Coin", "version": "2"}}

def fac(path, payload):
    req = urllib.request.Request(FAC + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))

class H(BaseHTTPRequestHandler):
    def _send(self, code, obj, extra=None):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        for k, v in (extra or {}).items(): self.send_header(k, v)
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        self._send(200, {"service": "readme-doctor", "usage": "POST README text to /score", "price_usdc": int(PRICE)/1e6, "payTo": PAY_TO, "network": NETWORK})
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(min(n, 200000)).decode("utf-8", "replace")
        host = self.headers.get("Host", "localhost")
        reqs = requirements(f"https://{host}/score")
        xp = self.headers.get("X-PAYMENT")
        if not xp:
            return self._send(402, {"x402Version": 1, "error": "X-PAYMENT header required", "accepts": [reqs]})
        try:
            payment = json.loads(base64.b64decode(xp))
            v = fac("/verify", {"x402Version": 1, "paymentPayload": payment, "paymentRequirements": reqs})
            if not v.get("isValid"):
                return self._send(402, {"x402Version": 1, "error": v.get("invalidReason", "invalid payment"), "accepts": [reqs]})
            s = fac("/settle", {"x402Version": 1, "paymentPayload": payment, "paymentRequirements": reqs})
            if not s.get("success"):
                return self._send(402, {"x402Version": 1, "error": s.get("errorReason", "settlement failed"), "accepts": [reqs]})
        except Exception as e:
            return self._send(402, {"x402Version": 1, "error": f"payment check failed: {e}", "accepts": [reqs]})
        self._send(200, score(body), {"X-PAYMENT-RESPONSE": base64.b64encode(json.dumps(s).encode()).decode()})

if __name__ == "__main__":
    HTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8402), H).serve_forever()
