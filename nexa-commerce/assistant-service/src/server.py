"""Nexa Commerce shopping assistant - HTTP front end (stdlib only)."""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.shop_assistant import ShopAssistant  # noqa: E402

PORT = int(os.environ.get("NEXA_ASSISTANT_PORT", "8083"))
ASSISTANT = ShopAssistant()


class Handler(BaseHTTPRequestHandler):
    server_version = "NexaAssistant/1.0"

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            return self._json(200, {"status": "ok", "service": "assistant"})
        if parsed.path == "/api/assistant/ask":
            params = parse_qs(parsed.query)
            session = (params.get("session") or ["anon"])[0]
            message = (params.get("q") or [""])[0]
            return self._json(200, ASSISTANT.reply(session, message))
        return self._json(404, {"error": "not found"})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[assistant] " + (fmt % args) + "\n")


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    sys.stderr.write("[assistant] listening on %d\n" % PORT)
    server.serve_forever()


if __name__ == "__main__":
    main()
