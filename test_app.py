"""Service-behaviour tests for Focus Log (lesson 94 capstone).

Starts the real app.py in a thread on an ephemeral port and exercises it
over HTTP: health, happy path, and validation errors — no mocks of the
service itself.
"""

import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import app as focus_log


def start_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), focus_log.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def call(base, method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


class TestFocusLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base = start_server()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        focus_log.TASKS.clear()

    def test_health_reports_ok(self):
        status, body = call(self.base, "GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body, {"status": "ok", "tasks": 0})

    def test_create_then_list(self):
        status, created = call(self.base, "POST", "/tasks", {"title": "Ship v1"})
        self.assertEqual(status, 201)
        self.assertEqual(created, {"id": 1, "title": "Ship v1", "done": False})

        status, listed = call(self.base, "GET", "/tasks")
        self.assertEqual(status, 200)
        self.assertEqual(listed, [created])

        status, health = call(self.base, "GET", "/health")
        self.assertEqual(health["tasks"], 1)

    def test_empty_title_is_400(self):
        for bad in ({"title": ""}, {"title": "   "}, {}):
            status, body = call(self.base, "POST", "/tasks", bad)
            self.assertEqual(status, 400, bad)
            self.assertEqual(body, {"error": "title is required"})
        status, listed = call(self.base, "GET", "/tasks")
        self.assertEqual(listed, [])  # no corrupt record was stored

    def test_unknown_route_is_404(self):
        status, body = call(self.base, "GET", "/nope")
        self.assertEqual(status, 404)
        self.assertEqual(body, {"error": "not found"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
