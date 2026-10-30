"""End-to-end tests for x402_server.py against a local mock facilitator (127.0.0.1 only, no network)."""
import base64, json, os, sys, threading, unittest, urllib.request, urllib.error, importlib
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CREATOR = "0xdee5d17120fe5b415858c977555fd0c4ed6d3fda"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
PAYMENT = base64.b64encode(json.dumps({"x402Version": 1, "scheme": "exact", "network": "base",
                                       "payload": {"signature": "0xsig", "authorization": {}}}).encode()).decode()
README = "# Demo\n\nA tool.\n\n## Install\n\npip install demo\n\n## Usage\n\ndemo run\n\n## License\n\nMIT\n"


class MockFac(BaseHTTPRequestHandler):
    mode = {"verify": True, "settle": True}
    calls = []

    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        MockFac.calls.append((self.path, body))
        if self.path == "/verify":
            out = {"isValid": True, "payer": "0xabc"} if MockFac.mode["verify"] else {"isValid": False, "invalidReason": "insufficient_funds"}
        elif self.path == "/settle":
            out = {"success": True, "transaction": "0xtx", "network": "base"} if MockFac.mode["settle"] else {"success": False, "errorReason": "settle_failed"}
        else:
            self.send_response(404); self.end_headers(); return
        b = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


def serve(handler):
    srv = HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class X402EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fac = serve(MockFac)
        os.environ["FACILITATOR_URL"] = "http://127.0.0.1:%d" % cls.fac.server_port
        os.environ.pop("PRICE_ATOMIC", None); os.environ.pop("NETWORK", None)
        import x402_server
        cls.mod = importlib.reload(x402_server)
        cls.app = serve(cls.mod.H)
        cls.base = "http://127.0.0.1:%d" % cls.app.server_port

    @classmethod
    def tearDownClass(cls):
        cls.app.shutdown(); cls.fac.shutdown()

    def setUp(self):
        MockFac.calls.clear()
        MockFac.mode.update(verify=True, settle=True)

    def post(self, body, payment=None):
        req = urllib.request.Request(self.base + "/score", data=body.encode(), method="POST")
        if payment is not None:
            req.add_header("X-PAYMENT", payment)
        try:
            r = urllib.request.urlopen(req, timeout=15)
            return r.status, json.loads(r.read()), r.headers
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read()), e.headers

    def test_payto_hardcoded_to_creator(self):
        self.assertEqual(self.mod.PAY_TO.lower(), CREATOR)

    def test_get_info(self):
        d = json.loads(urllib.request.urlopen(self.base + "/", timeout=10).read())
        self.assertEqual(d["payTo"].lower(), CREATOR)
        self.assertEqual(d["network"], "base")
        self.assertAlmostEqual(d["price_usdc"], 0.01)

    def test_no_payment_returns_402_challenge(self):
        code, d, _ = self.post(README)
        self.assertEqual(code, 402)
        req = d["accepts"][0]
        self.assertEqual(req["payTo"].lower(), CREATOR)
        self.assertEqual(req["network"], "base")
        self.assertEqual(req["asset"], USDC_BASE)
        self.assertEqual(req["maxAmountRequired"], "10000")
        self.assertEqual(MockFac.calls, [])

    def test_valid_payment_verifies_settles_and_scores(self):
        code, d, h = self.post(README, PAYMENT)
        self.assertEqual(code, 200, d)
        self.assertIsInstance(d, dict)
        self.assertEqual([c[0] for c in MockFac.calls], ["/verify", "/settle"])
        for _, body in MockFac.calls:
            self.assertEqual(body["paymentRequirements"]["payTo"].lower(), CREATOR)
        settle = json.loads(base64.b64decode(h["X-PAYMENT-RESPONSE"]))
        self.assertTrue(settle["success"])

    def test_invalid_payment_rejected_without_settle(self):
        MockFac.mode["verify"] = False
        code, d, _ = self.post(README, PAYMENT)
        self.assertEqual(code, 402)
        self.assertEqual(d["error"], "insufficient_funds")
        self.assertEqual([c[0] for c in MockFac.calls], ["/verify"])

    def test_settle_failure_rejected(self):
        MockFac.mode["settle"] = False
        code, d, _ = self.post(README, PAYMENT)
        self.assertEqual(code, 402)
        self.assertEqual(d["error"], "settle_failed")

    def test_garbage_payment_header_rejected(self):
        code, d, _ = self.post(README, "not-base64-json!!")
        self.assertEqual(code, 402)
        self.assertEqual(MockFac.calls, [])

    def test_facilitator_down_fails_closed(self):
        old = self.mod.FAC
        self.mod.FAC = "http://127.0.0.1:1"
        try:
            code, d, _ = self.post(README, PAYMENT)
        finally:
            self.mod.FAC = old
        self.assertEqual(code, 402)
        self.assertIn("payment check failed", d["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
