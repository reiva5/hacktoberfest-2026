"""Serve the web UI with no build step.

The API address comes from the API_BASE environment variable (default http://localhost:8000)
and reaches the page as /config.js. Run: python web/serve.py  ->  http://localhost:5173
"""
import json
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

API_BASE = os.environ.get("API_BASE", "http://localhost:8000").rstrip("/")
PORT = int(os.environ.get("WEB_PORT", "5173"))


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] == "/config.js":
            body = f"window.API_BASE = {json.dumps(API_BASE)};\n".encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    handler = partial(Handler, directory=str(Path(__file__).parent))
    print(f"Web UI on http://localhost:{PORT} (API: {API_BASE})")
    ThreadingHTTPServer(("127.0.0.1", PORT), handler).serve_forever()
