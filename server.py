#!/usr/bin/env python3
"""HTTP wrapper for readme-doctor. POST /score with README text as body -> JSON score.
Run: python server.py [port]. x402 paywall to be added; payTo = creator EVM wallet."""
import json, re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from readme_doctor import CHECKS

PAY_TO = "0xdee5d17120fe5b415858c977555fd0c4ed6d3fda"

def score(text):
    s, fixes = 0, []
    for name, pat, fix, pts in CHECKS:
        if re.search(pat, text, re.M): s += pts
        else: fixes.append({"check": name, "fix": fix, "points": pts})
    return {"score": s, "max": 100, "fixes": fixes}

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(min(n, 200000)).decode("utf-8", "replace")
        out = json.dumps(score(body)).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(out)
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"readme-doctor: POST README text to /score")

if __name__ == "__main__":
    HTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8080), H).serve_forever()
