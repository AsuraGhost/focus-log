# app.py — Tiny capstone product: Focus Log (Python standard library only)
# Run: python app.py
# Check: curl http://127.0.0.1:8000/health
# Create: curl -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d '{"title": "Ship v1"}'
# List:  curl http://127.0.0.1:8000/tasks
import json
import os
import signal
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TASKS = []  # One in-memory table: the whole data model for v1.

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if not length:
            return {}
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        # Health check: deployers and tests use this to prove the app is alive.
        if self.path == "/health":
            return self._send(200, {"status": "ok", "tasks": len(TASKS)})
        if self.path == "/tasks":
            return self._send(200, TASKS)
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/tasks":
            return self._send(404, {"error": "not found"})
        data = self._read_json()
        title = str(data.get("title", "")).strip()
        # Validate at the boundary: a clear 400 beats a corrupt record.
        if not title:
            return self._send(400, {"error": "title is required"})
        task = {"id": len(TASKS) + 1, "title": title, "done": False}
        TASKS.append(task)
        return self._send(201, task)

    def log_message(self, *args):
        pass  # Keep output clean; a real app would use structured logging.

if __name__ == "__main__":
    # Hosted platforms inject $PORT and need a public bind; local runs keep
    # the same defaults (0.0.0.0:8000). Binding 127.0.0.1 would be
    # unreachable behind any platform router.
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)

    # Graceful stop: platforms send SIGTERM before killing the container;
    # without a handler the process waits out the full grace period.
    def _stop(signum, frame):
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    print(f"Focus Log running at http://0.0.0.0:{port} — try GET /health")
    server.serve_forever()
